import random
from datetime import datetime, timedelta
from app.database.session import sync_engine, SyncSessionLocal, Base
from app.database.models import (
    Organization, User, BusinessService, Asset, AssetDependency,
    Vulnerability, Threat, SecurityControl, RiskAssessment,
    RiskHistory, FinancialModel, MLModelRegistry, OptimizationRun,
    ComplianceFinding, BlockchainTransaction, AuditLog,
    ThreatIndicator, RiskScenario, ComplianceFramework, ComplianceControl,
    SecurityIncident
)
from app.core.security import get_password_hash
from app.risk_engine.calculator import calculate_asset_criticality, calculate_risk_score
from app.financial_engine.eal import calculate_eal
from app.blockchain.ledger import generate_canonical_hash, audit_ledger

def seed_database():
    Base.metadata.create_all(bind=sync_engine)
    db = SyncSessionLocal()

    try:
        # Check if already seeded
        existing_org = db.query(Organization).filter(Organization.name == "ABC Bank").first()
        if existing_org:
            existing_scenarios = db.query(RiskScenario).filter(RiskScenario.organization_id == existing_org.id).count()
            if existing_scenarios == 0:
                print("Seeding missing RiskScenario entries for ABC Bank...")
                assets = db.query(Asset).filter(Asset.organization_id == existing_org.id).all()
                scenarios_data = [
                    ("Core Payment Database Ransomware & Extortion", assets[0].id if len(assets) > 0 else None, 1.2, 0.7, 0.52, 8728000.0, 4538560.0, 6500000.0, 11500000.0, 85.0, True, {"cve": "CVE-2021-44228", "attack_vector": "Public Web -> Payment API -> Lateral -> DB"}),
                    ("Internet Banking Portal RCE / Session Hijacking", assets[1].id if len(assets) > 1 else None, 2.5, 0.8, 1.40, 5200000.0, 7280000.0, 4000000.0, 7000000.0, 88.0, False, {"cve": "CVE-2022-22965", "attack_vector": "Public Facing Web Server"}),
                    ("Payment API Gateway Credential Stuffing & Bypass", assets[2].id if len(assets) > 2 else None, 1.8, 0.6, 0.85, 6500000.0, 5525000.0, 5000000.0, 8500000.0, 82.0, False, {"cve": "CVE-2024-21762", "attack_vector": "API Endpoint SSL Portal"}),
                    ("Active Directory Kerberoasting & Domain Takeover", assets[3].id if len(assets) > 3 else None, 1.0, 0.6, 0.60, 7500000.0, 4500000.0, 6000000.0, 10000000.0, 80.0, False, {"cve": "VULN-IAM-09", "attack_vector": "Unsegmented Workstation -> Domain Admin"}),
                    ("Cloud Storage Customer KYC Data Exposure", assets[4].id if len(assets) > 4 else None, 1.4, 0.5, 0.70, 4000000.0, 2800000.0, 3000000.0, 5500000.0, 78.0, False, {"cve": "VULN-S3-01", "attack_vector": "Misconfigured S3 Bucket Permissions"}),
                    ("Remaining Distributed Host Exposures (95 Assets Aggregate)", None, 3.2, 0.6, 1.92, 11123146.0, 21356440.0, 15000000.0, 28000000.0, 84.0, False, {"notes": "Aggregate of 95 non-crown-jewel enterprise assets and background threat events"})
                ]
                for s_name, s_aid, s_tef, s_vul, s_aro, s_sle, s_eal, s_min, s_max, s_conf, s_crown, s_det in scenarios_data:
                    rs = RiskScenario(
                        organization_id=existing_org.id,
                        asset_id=s_aid,
                        name=s_name,
                        threat_event_frequency=s_tef,
                        vulnerability_exploitability=s_vul,
                        loss_event_frequency=s_aro,
                        single_loss_expectancy=s_sle,
                        expected_annual_loss=s_eal,
                        loss_magnitude_min=s_min,
                        loss_magnitude_max=s_max,
                        confidence_level=s_conf,
                        is_primary_crown_jewel=s_crown,
                        scenario_details=s_det
                    )
                    db.add(rs)
                db.commit()
                print("Seeded 6 RiskScenario records successfully.")
            
            # Check if security incidents are seeded
            existing_incidents = db.query(SecurityIncident).filter(SecurityIncident.organization_id == existing_org.id).all()
            if not existing_incidents:
                print("Seeding historical SecurityIncident records for ABC Bank...")
                assets = db.query(Asset).filter(Asset.organization_id == existing_org.id).all()
                _seed_security_incidents(db, existing_org.id, assets)
                print("Seeded historical SecurityIncident records successfully.")
            else:
                existing_record_ids = {b.get("record_id") for b in audit_ledger.get_all_blocks()}
                for inc in existing_incidents:
                    if inc.incident_id not in existing_record_ids:
                        payload = {
                            "incident_id": inc.incident_id,
                            "incident_type": inc.incident_type,
                            "incident_date": inc.incident_date.isoformat(),
                            "total_observed_loss": inc.total_observed_loss,
                            "revenue_loss": inc.revenue_loss,
                            "recovery_cost": inc.recovery_cost,
                            "response_cost": inc.response_cost,
                            "regulatory_cost": inc.regulatory_cost,
                            "other_loss": inc.other_loss,
                            "incident_status": inc.incident_status
                        }
                        audit_ledger.record_transaction(
                            record_type="SECURITY_INCIDENT_RECORDED",
                            record_id=inc.incident_id,
                            payload_data=payload
                        )

            print("Database already contains seed data for ABC Bank.")
            return

        print("Seeding realistic enterprise cybersecurity dataset for ABC Bank...")

        # 1. Organization
        org = Organization(
            name="ABC Bank",
            industry="Banking & Financial Services",
            country="India",
            employee_count=2500,
            annual_revenue=5000000000.0,       # ₹500 Crore
            cybersecurity_budget=10000000.0,    # ₹1 Crore
            risk_appetite_enterprise=10000000.0,# ₹1 Crore max
            risk_appetite_critical_asset=1000000.0, # ₹10 Lakh max
            financial_assumptions={
                "hourly_downtime_cost": 300000.0,
                "incident_response_hourly_rate": 25000.0,
                "data_recovery_base_cost": 1500000.0,
                "legal_regulatory_base_cost": 2000000.0,
                "customer_impact_multiplier": 1.5,
                "business_interruption_multiplier": 1.2
            }
        )
        db.add(org)
        db.flush()

        # 2. Roles & Users
        users = [
            ("admin@abcbank.com", "Admin User", "ADMIN", "Admin@12345"),
            ("ciso@abcbank.com", "Vikram Malhotra (CISO)", "CISO", "Ciso@12345"),
            ("analyst@abcbank.com", "Priya Sharma (Security Analyst)", "SECURITY_ANALYST", "Analyst@12345"),
            ("risk@abcbank.com", "Rohan Mehta (Risk Analyst)", "RISK_ANALYST", "Risk@12345"),
            ("executive@abcbank.com", "Ananya Verma (CEO/Board)", "EXECUTIVE", "Executive@12345"),
            ("auditor@abcbank.com", "Sanjay Joshi (Lead Auditor)", "AUDITOR", "Auditor@12345")
        ]
        for email, name, role, pwd in users:
            user = User(
                organization_id=org.id,
                email=email,
                full_name=name,
                role=role,
                hashed_password=get_password_hash(pwd),
                is_active=True
            )
            db.add(user)
        db.flush()

        # 3. Business Services
        services_data = [
            ("Online Retail Banking", "Direct customer internet banking and account portals", 96.0, 400000.0),
            ("UPI & IMPS Payment Switch", "Real-time payment clearance and settlement switch", 99.0, 600000.0),
            ("Corporate Treasury & Trade", "High-value enterprise transactions and forex trade", 94.0, 350000.0),
            ("ATM & POS Switching Network", "Branch ATM network routing and debit transactions", 90.0, 250000.0),
            ("Loan Origination & Credit Scoring", "Underwriting and credit bureau verification pipeline", 84.0, 150000.0),
            ("Enterprise Employee Portal", "Internal HR, payroll, and corporate intranet", 65.0, 50000.0)
        ]
        created_services = []
        for name, desc, crit, hourly in services_data:
            bs = BusinessService(
                organization_id=org.id,
                name=name,
                description=desc,
                criticality=crit,
                hourly_revenue_impact=hourly
            )
            db.add(bs)
            created_services.append(bs)
        db.flush()

        # 4. 100 Assets (25 Servers, 10 Databases, 20 Applications, 45 Endpoints)
        random.seed(42)
        created_assets = []

        # 10 Databases (Crown Jewels)
        db_names = [
            ("DB-PAY-01", "Core Payment Database Cluster (Oracle RAC)", 98.0, 95.0, 95.0, 0.2, 98.0, False, created_services[1].id),
            ("DB-CUST-01", "Customer PII & Account Master (PostgreSQL HA)", 95.0, 98.0, 90.0, 0.5, 95.0, False, created_services[0].id),
            ("DB-TREASURY-01", "Treasury & FX Transaction DB (MS SQL)", 92.0, 90.0, 92.0, 0.5, 90.0, False, created_services[2].id),
            ("DB-CARD-01", "Credit Card Vault & Tokenization DB", 96.0, 99.0, 90.0, 0.2, 98.0, False, created_services[1].id),
            ("DB-LOAN-01", "Loan Management & KYC Store", 82.0, 85.0, 80.0, 2.0, 85.0, False, created_services[4].id),
            ("DB-AUDIT-01", "Immutable Regulatory Compliance DB", 88.0, 80.0, 70.0, 4.0, 98.0, False, created_services[5].id),
            ("DB-FRAUD-01", "Real-Time ML Fraud Feature Store (Redis/Clickhouse)", 86.0, 75.0, 85.0, 1.0, 80.0, False, created_services[1].id),
            ("DB-BACKUP-01", "Disaster Recovery Storage Vault (Ceph)", 92.0, 90.0, 85.0, 0.5, 92.0, False, created_services[0].id),
            ("DB-ATM-01", "ATM Transaction Journaling DB", 84.0, 80.0, 80.0, 1.0, 85.0, False, created_services[3].id),
            ("DB-DWH-01", "Enterprise Analytics Data Warehouse", 70.0, 75.0, 60.0, 8.0, 70.0, False, created_services[5].id)
        ]
        for name, full_name, bi, ds, rd, dt, reg, exp, bs_id in db_names:
            crit = calculate_asset_criticality(bi, ds, rd, reg, exp, dt)
            asset = Asset(
                organization_id=org.id,
                name=full_name,
                asset_type="database",
                ip_address=f"10.0.4.{len(created_assets) + 10}",
                hostname=f"{name.lower()}.internal.bank.net",
                owner="Database Operations",
                department="Core Banking Infrastructure",
                operating_system="Oracle Linux / RHEL 8",
                business_service_id=bs_id,
                business_importance=bi,
                data_sensitivity=ds,
                revenue_dependency=rd,
                downtime_tolerance_hours=dt,
                regulatory_importance=reg,
                internet_exposed=exp,
                criticality_score=crit,
                current_risk_score=94.0 if name == "DB-PAY-01" else round(crit * 0.85, 1),
                expected_annual_loss=7200000.0 if name == "DB-PAY-01" else round(crit * 35000.0, 2),
                tags=["crown_jewel", "pci_dss", "rbi_regulated"]
            )
            db.add(asset)
            created_assets.append(asset)

        # 25 Servers
        for i in range(1, 26):
            is_web = (i <= 5)
            is_api = (6 <= i <= 12)
            is_iam = (i in (13, 14))
            name = f"srv-web-prod-0{i}" if is_web else (f"srv-api-gateway-0{i}" if is_api else (f"srv-iam-dc-0{i}" if is_iam else f"srv-microservice-node-{i}"))
            bi = 85.0 if is_api else (78.0 if is_web else 70.0)
            ds = 80.0 if is_api else (65.0 if is_web else 60.0)
            rd = 85.0 if (is_api or is_web) else 65.0
            reg = 90.0 if is_iam else 75.0
            exp = True if (is_web or i in (6, 7)) else False
            dt = 0.5 if is_api else (1.0 if is_web else 4.0)
            crit = calculate_asset_criticality(bi, ds, rd, reg, exp, dt)
            
            asset = Asset(
                organization_id=org.id,
                name=name,
                asset_type="server",
                ip_address=f"10.0.1.{i+10}" if not exp else f"198.51.100.{i+2}",
                hostname=f"{name}.bank.net",
                owner="DevOps & Infrastructure",
                department="IT Operations",
                operating_system="Red Hat Enterprise Linux 8.8",
                business_service_id=created_services[0 if is_web else 1].id,
                business_importance=bi,
                data_sensitivity=ds,
                revenue_dependency=rd,
                downtime_tolerance_hours=dt,
                regulatory_importance=reg,
                internet_exposed=exp,
                criticality_score=crit,
                current_risk_score=88.0 if is_web else round(crit * 0.75, 1),
                expected_annual_loss=4500000.0 if is_web else round(crit * 25000.0, 2),
                tags=["dmz" if exp else "internal_network", "production"]
            )
            db.add(asset)
            created_assets.append(asset)

        # 20 Applications
        app_titles = [
            "Retail Banking Web Portal", "Mobile Banking Backend API", "Corporate FX Portal",
            "Payment Gateway Router", "Unified Payments Interface (UPI) Switch", "Card Authorization Engine",
            "Fraud Monitoring Daemon", "KYC Automated Verifier", "Loan Disbursement Pipeline",
            "Customer Support Helpdesk", "Swift Interbank Messaging Node", "ATM Terminal Manager",
            "Branch Ops Core System", "Internal HRIS", "Enterprise Email Exchange",
            "Treasury Accounting System", "Direct Tax Settlement Portal", "Mutual Fund Distribution App",
            "Credit Card Statement Generator", "Security Information & Event Hub"
        ]
        for i, title in enumerate(app_titles):
            exp = (i in (0, 1, 3, 4))
            bi = 92.0 if i < 6 else 75.0
            crit = calculate_asset_criticality(bi, 85.0, 85.0, 90.0, exp, 0.5 if i < 6 else 2.0)
            asset = Asset(
                organization_id=org.id,
                name=title,
                asset_type="application",
                ip_address=f"10.0.2.{i+15}",
                hostname=f"app-{i+1}.internal.bank.net",
                owner="Application Security Team",
                department="Digital Banking",
                operating_system="Container / Kubernetes K8s",
                business_service_id=created_services[0 if i in (0, 1) else (1 if i in (3, 4, 5) else 2)].id,
                business_importance=bi,
                data_sensitivity=85.0,
                revenue_dependency=85.0,
                downtime_tolerance_hours=0.5 if i < 6 else 2.0,
                regulatory_importance=90.0,
                internet_exposed=exp,
                criticality_score=crit,
                current_risk_score=84.0 if exp else 65.0,
                expected_annual_loss=3800000.0 if exp else 1500000.0,
                tags=["app_tier", "cloud_native"]
            )
            db.add(asset)
            created_assets.append(asset)

        # 45 Endpoints (Laptops & Desks)
        for i in range(1, 46):
            is_exec = (i <= 5)
            is_admin = (6 <= i <= 12)
            name = f"Exec-Laptop-{i}" if is_exec else (f"Admin-Workstation-{i}" if is_admin else f"Branch-Desk-{i}")
            bi = 80.0 if is_admin else (70.0 if is_exec else 45.0)
            crit = calculate_asset_criticality(bi, 75.0 if is_exec else 50.0, 50.0, 60.0, False, 8.0)
            asset = Asset(
                organization_id=org.id,
                name=name,
                asset_type="endpoint",
                ip_address=f"192.168.10.{i+10}",
                hostname=f"{name.lower()}.corp.bank.net",
                owner="End User Compute",
                department="Corporate Staff",
                operating_system="Windows 11 Enterprise",
                business_service_id=created_services[5].id,
                business_importance=bi,
                data_sensitivity=65.0 if is_exec else 45.0,
                revenue_dependency=40.0,
                downtime_tolerance_hours=8.0,
                regulatory_importance=55.0,
                internet_exposed=False,
                criticality_score=crit,
                current_risk_score=52.0,
                expected_annual_loss=450000.0,
                tags=["fleet", "edr_enrolled"]
            )
            db.add(asset)
            created_assets.append(asset)

        db.flush()

        # 5. Security Controls (20 Enterprise Controls)
        controls_data = [
            ("CTRL-PATCH", "Automated Critical Vulnerability Patching", "VULN_MGMT", 70.0, 80.0, 3, 1800000.0, 400000.0, 7500000.0, [], 0.90),
            ("CTRL-MFA", "Privileged Identity Multi-Factor Authentication", "IAM", 72.0, 85.0, 3, 1200000.0, 300000.0, 4500000.0, [], 0.95),
            ("CTRL-EDR", "Next-Gen EDR / XDR Autonomous Response", "ENDPOINT", 85.0, 88.0, 4, 2500000.0, 600000.0, 8000000.0, [], 0.90),
            ("CTRL-SEG", "Network Micro-segmentation & Zero Trust Isolation", "NETWORK", 60.0, 78.0, 2, 2000000.0, 450000.0, 6000000.0, [], 0.85),
            ("CTRL-BACKUP", "Immutable WORM Air-Gapped Backup Vault", "BACKUP", 75.0, 92.0, 3, 1000000.0, 200000.0, 3500000.0, [], 0.90),
            ("CTRL-WAF", "Next-Gen Cloud Web Application Firewall (WAF)", "NETWORK", 80.0, 82.0, 3, 1500000.0, 350000.0, 4000000.0, [], 0.85),
            ("CTRL-PAM", "Privileged Access Management & Session Vault", "IAM", 65.0, 80.0, 3, 1400000.0, 300000.0, 4200000.0, ["CTRL-MFA"], 0.88),
            ("CTRL-DLP", "Endpoint & Cloud Data Loss Prevention (DLP)", "ENCRYPTION", 58.0, 70.0, 2, 1100000.0, 250000.0, 2800000.0, [], 0.80),
            ("CTRL-SOC", "24/7 Managed Detection & SOC Monitoring", "MONITORING", 85.0, 85.0, 4, 1600000.0, 400000.0, 4800000.0, ["CTRL-EDR"], 0.90),
            ("CTRL-TRAIN", "Security Awareness Anti-Phishing Simulation", "TRAINING", 65.0, 60.0, 2, 800000.0, 150000.0, 2000000.0, [], 0.75),
            ("CTRL-APISEC", "API Security Gateway & Schema Validator", "NETWORK", 62.0, 75.0, 2, 1200000.0, 280000.0, 3600000.0, [], 0.85),
            ("CTRL-CSPM", "Cloud Security Posture Management (CSPM)", "MONITORING", 70.0, 80.0, 3, 1500000.0, 350000.0, 3800000.0, [], 0.85),
            ("CTRL-DAM", "Database Activity Monitoring (DAM) & Masking", "ENCRYPTION", 68.0, 82.0, 3, 1400000.0, 300000.0, 3900000.0, [], 0.88),
            ("CTRL-SCAN", "Continuous Dynamic App Security Testing (DAST)", "VULN_MGMT", 75.0, 72.0, 3, 900000.0, 200000.0, 2200000.0, [], 0.80),
            ("CTRL-HSM", "Hardware Security Module (HSM) Key Protection", "ENCRYPTION", 90.0, 95.0, 4, 2200000.0, 500000.0, 5000000.0, [], 0.95),
            ("CTRL-IGA", "Identity Governance & Lifecycle Access Review", "IAM", 65.0, 75.0, 3, 1600000.0, 350000.0, 3800000.0, [], 0.85),
            ("CTRL-EMAIL", "AI-Powered Email Phishing Defense", "ENDPOINT", 82.0, 80.0, 3, 1000000.0, 220000.0, 2500000.0, [], 0.80),
            ("CTRL-ENCR", "Full-Disk & Database Column-Level Encryption", "ENCRYPTION", 85.0, 90.0, 4, 700000.0, 150000.0, 1800000.0, [], 0.90),
            ("CTRL-HUNT", "Autonomous Cyber Threat Hunting Engine", "MONITORING", 55.0, 78.0, 2, 1300000.0, 300000.0, 3200000.0, ["CTRL-SOC"], 0.82),
            ("CTRL-MICROSEG", "Zero-Trust Microsegmentation Gateway", "NETWORK", 50.0, 85.0, 2, 1800000.0, 400000.0, 4500000.0, ["CTRL-SEG"], 0.90)
        ]
        created_controls = []
        for code, name, cat, cov, eff, mat, icost, acost, red, prereq, dim in controls_data:
            ctrl = SecurityControl(
                organization_id=org.id,
                code=code,
                name=name,
                category=cat,
                coverage_percentage=cov,
                effectiveness_percentage=eff,
                maturity_level=mat,
                implementation_cost=icost,
                annual_cost=acost,
                modeled_risk_reduction=red,
                prerequisites=prereq,
                diminishing_return_factor=dim,
                status="DEPLOYED" if cov >= 80 else "PARTIALLY_DEPLOYED"
            )
            db.add(ctrl)
            created_controls.append(ctrl)
        db.flush()

        # 6. 500 Vulnerabilities (50 Critical, 180 High, 200 Medium, 70 Low)
        cve_templates = [
            ("CVE-2021-44228", "Apache Log4j2 JNDI Remote Code Execution", 10.0, "CRITICAL", True, True),
            ("CVE-2022-22965", "Spring Framework RCE (Spring4Shell)", 9.8, "CRITICAL", True, True),
            ("CVE-2024-21762", "FortiOS Out-of-bounds Write in SSL VPN", 9.6, "CRITICAL", True, True),
            ("CVE-2023-36884", "Office and Windows HTML RCE Vulnerability", 8.8, "HIGH", True, True),
            ("CVE-2023-4863", "Heap Buffer Overflow in libwebp", 8.8, "HIGH", True, False),
            ("CVE-2023-38606", "Kernel Privilege Escalation in Unix Subsystem", 7.8, "HIGH", True, False),
            ("CVE-2022-3786", "OpenSSL X.509 Buffer Overflows", 7.5, "HIGH", False, False),
            ("CVE-2023-22515", "Broken Access Control in Web Admin Interface", 9.8, "CRITICAL", True, True),
            ("CVE-2024-1709", "Authentication Bypass in ScreenConnect", 10.0, "CRITICAL", True, True),
            ("CVE-2023-44487", "HTTP/2 Rapid Reset DDoS Vulnerability", 7.5, "HIGH", True, False),
            ("CVE-2023-29357", "Privilege Escalation via JWT Spoofing", 8.8, "HIGH", True, False),
            ("CVE-2022-41040", "Exchange Server Server-Side Request Forgery", 8.8, "HIGH", True, True),
            ("CVE-2023-27997", "Heap-based buffer overflow in VPN SSL portal", 9.8, "CRITICAL", True, True),
            ("CVE-2022-26134", "OGNL Injection in Web Framework", 9.8, "CRITICAL", True, True),
            ("CVE-2021-34527", "PrintSpooler Remote Code Execution (PrintNightmare)", 8.8, "HIGH", True, True)
        ]

        # First 50 Critical CVEs attached to critical servers and apps
        for i in range(50):
            template = cve_templates[i % len(cve_templates)]
            target_asset = created_assets[i % 35]  # target DBs, servers, apps
            vuln = Vulnerability(
                organization_id=org.id,
                affected_asset_id=target_asset.id,
                cve_id=f"{template[0]}-{i+1:02d}" if i >= len(cve_templates) else template[0],
                title=template[1],
                description=f"Critical vulnerability identified in {target_asset.name}. Allows remote unauthenticated execution.",
                cvss_score=template[2],
                severity="CRITICAL",
                exploit_available=template[4],
                active_exploitation=template[5],
                patch_available=True,
                remediation_status="OPEN",
                source="Wazuh EDR & OpenVAS Scanner",
                evidence={"cve": template[0], "cisa_kev": template[5], "cvss_v3": template[2]}
            )
            db.add(vuln)

        # 180 High Severity CVEs
        for i in range(50, 230):
            target_asset = created_assets[i % len(created_assets)]
            vuln = Vulnerability(
                organization_id=org.id,
                affected_asset_id=target_asset.id,
                cve_id=f"CVE-2023-{10000 + i}",
                title=f"High Severity Privilege Escalation in {target_asset.asset_type}",
                cvss_score=round(random.uniform(7.0, 8.9), 1),
                severity="HIGH",
                exploit_available=random.choice([True, False]),
                active_exploitation=False,
                patch_available=True,
                remediation_status="OPEN",
                source="OpenVAS Scanner",
                evidence={"scan_id": f"NVT-{i}", "solution": "Vendor Patch Available"}
            )
            db.add(vuln)

        # 200 Medium Severity CVEs
        for i in range(230, 430):
            target_asset = created_assets[i % len(created_assets)]
            vuln = Vulnerability(
                organization_id=org.id,
                affected_asset_id=target_asset.id,
                cve_id=f"CVE-2022-{20000 + i}",
                title=f"Medium Configuration Weakness / TLS Cipher on {target_asset.hostname}",
                cvss_score=round(random.uniform(4.0, 6.9), 1),
                severity="MEDIUM",
                exploit_available=False,
                active_exploitation=False,
                patch_available=True,
                remediation_status="OPEN",
                source="Automated Vulnerability Feed",
                evidence={"scan_id": f"NVT-{i}"}
            )
            db.add(vuln)

        # 70 Low Severity CVEs
        for i in range(430, 500):
            target_asset = created_assets[i % len(created_assets)]
            vuln = Vulnerability(
                organization_id=org.id,
                affected_asset_id=target_asset.id,
                cve_id=f"CVE-2021-{30000 + i}",
                title=f"Low Information Disclosure Banner on {target_asset.hostname}",
                cvss_score=round(random.uniform(1.0, 3.9), 1),
                severity="LOW",
                exploit_available=False,
                active_exploitation=False,
                patch_available=True,
                remediation_status="OPEN",
                source="OpenVAS Scanner",
                evidence={"banner_leak": True}
            )
            db.add(vuln)

        db.flush()

        # 7. Threat Intelligence Feeds
        threats_data = [
            ("FIN7 (Carbanak Financial Syndicate)", "Ransomware & Extortion", "T1190 - Exploit Public-Facing App", "CRITICAL", True, ["CVE-2021-44228", "CVE-2022-22965"]),
            ("LockBit 3.0 Ransomware Group", "Ransomware & Double Extortion", "T1486 - Data Encrypted for Impact", "CRITICAL", True, ["CVE-2023-36884"]),
            ("Lazarus Group (APT38)", "Financial Wire & Swift Fraud", "T1078 - Valid Accounts Lateral Movement", "CRITICAL", True, ["CVE-2024-21762"]),
            ("Anonymous Sudan / Killnet", "Distributed Denial of Service (DDoS)", "T1498 - Network Denial of Service", "HIGH", False, ["CVE-2023-44487"])
        ]
        for actor, ttype, tech, sev, active, cves in threats_data:
            threat = Threat(
                organization_id=org.id,
                threat_actor=actor,
                threat_type=ttype,
                attack_technique=tech,
                threat_severity=sev,
                active_campaign=active,
                exploit_cves=cves,
                target_asset_types=["server", "database", "application"],
                relevance_score=95.0 if active else 70.0
            )
            db.add(threat)
        db.flush()

        # 8. Risk History Timeline (Matching Section 79 demonstration)
        now = datetime.utcnow()
        history_events = [
            (now - timedelta(hours=6), 72.0, 28000000.0, "Normal Modeled Enterprise Baseline Risk (09:00)"),
            (now - timedelta(hours=4), 78.5, 35000000.0, "Critical Vulnerability Discovered: Log4j2 RCE (10:15)"),
            (now - timedelta(hours=2), 82.0, 46000000.0, "Active CISA In-The-Wild Exploitation Detected (10:32)"),
            (now, 82.0, 46000000.0, "Current Modeled Exposure (Pre-Investment Decision)")
        ]
        for ts, score, eal_v, trigger in history_events:
            rh = RiskHistory(
                organization_id=org.id,
                timestamp=ts,
                risk_score=score,
                expected_annual_loss=eal_v,
                trigger_event=trigger,
                details={"modeled_label": "MODELED ESTIMATE"}
            )
            db.add(rh)

        # 9. Initial Risk Assessment Record
        current_assessment = RiskAssessment(
            organization_id=org.id,
            assessment_name="Continuous Enterprise Cyber Risk Assessment",
            enterprise_risk_score=82.0,
            risk_level="CRITICAL",
            expected_annual_loss=46000000.0,  # ₹4.6 Crore
            modeled_loss_min=35000000.0,
            modeled_loss_max=62000000.0,
            confidence_percentage=85.0,
            assessment_trigger="Active CISA Exploitation Event",
            risk_contributors={
                "critical_vulnerability_pct": 25.0,
                "active_exploitation_pct": 20.0,
                "asset_criticality_pct": 20.0,
                "internet_exposure_pct": 15.0,
                "weak_control_segmentation_pct": 11.0,
                "other_environmental_factors_pct": 9.0
            },
            canonical_hash=generate_canonical_hash({"risk_score": 82.0, "eal": 46000000.0, "assets": 100}),
            blockchain_tx_id="TX-FABRIC-2026-ASSESS-001"
        )
        db.add(current_assessment)
        db.flush()

        # 10. Initial Optimization Run Recommendation
        opt_run = OptimizationRun(
            organization_id=org.id,
            budget_amount=10000000.0,         # ₹1 Crore
            current_modeled_risk=46000000.0,  # ₹4.6 Crore
            projected_modeled_risk=20000000.0,# ₹2.0 Crore
            modeled_risk_reduction=26000000.0,# ₹2.6 Crore
            total_investment=8500000.0,       # ₹85 Lakh
            efficiency_metric=3.06,           # 2.6Cr / 85L = 3.06x
            selected_controls=[
                {"code": "CTRL-PATCH", "name": "Automated Critical Vulnerability Patching", "cost": 1800000.0, "reduction": 7500000.0},
                {"code": "CTRL-MFA", "name": "Privileged Identity Multi-Factor Authentication", "cost": 1200000.0, "reduction": 4500000.0},
                {"code": "CTRL-EDR", "name": "Next-Gen EDR / XDR Autonomous Response", "cost": 2500000.0, "reduction": 8000000.0},
                {"code": "CTRL-SEG", "name": "Network Micro-segmentation & Zero Trust Isolation", "cost": 2000000.0, "reduction": 6000000.0},
                {"code": "CTRL-BACKUP", "name": "Immutable WORM Air-Gapped Backup Vault", "cost": 1000000.0, "reduction": 3500000.0}
            ],
            status="RECOMMENDED",
            canonical_hash=generate_canonical_hash({"budget": 10000000.0, "invested": 8500000.0, "reduction": 26000000.0}),
            blockchain_tx_id="TX-FABRIC-2026-OPT-001"
        )
        db.add(opt_run)
        db.flush()

        # 11. Compliance Findings (NIST CSF, ISO 27001, CIS Controls)
        compliance_items = [
            ("NIST CSF 2.0", "PR.AC-1", "Identity & Access Management Policy", "GAP", "28% of administrative lateral paths lack MFA enforcement.", "Enforce CTRL-MFA across all RDP/SSH jump hosts.", "Identity Sec Team"),
            ("NIST CSF 2.0", "PR.IP-12", "Vulnerability Management & Patch SLA", "GAP", "50 Critical CVEs exceed the 14-day remediation SLA.", "Deploy CTRL-PATCH automated orchestration.", "SecOps Team"),
            ("ISO/IEC 27001:2022", "A.13.1.3", "Segregation in Networks", "GAP", "Direct SQL traffic permitted between Web Tier and Core Payment DB.", "Deploy CTRL-SEG microsegmentation rule.", "Network Security"),
            ("ISO/IEC 27001:2022", "A.12.1.2", "Protection Against Malware", "COMPLIANT", "EDR deployed on 85% of fleet with real-time behavioral heuristic prevention.", "Maintain coverage.", "Endpoint Ops"),
            ("CIS Controls v8", "CIS-10", "Data Recovery Capabilities", "PARTIAL", "Backups are replicated daily but lack immutable WORM air-gapping.", "Deploy CTRL-BACKUP immutable vault.", "Infrastructure Ops")
        ]
        for fw, code, title, status, gap, rem, owner in compliance_items:
            cf = ComplianceFinding(
                organization_id=org.id,
                framework=fw,
                control_code=code,
                requirement_title=title,
                status=status,
                gap_description=gap,
                evidence_summary=f"Automated audit verification against active network and host telemetry on {now.strftime('%Y-%m-%d')}.",
                evidence_hash=generate_canonical_hash({"code": code, "status": status}),
                recommended_remediation=rem,
                owner=owner,
                due_date=now + timedelta(days=30)
            )
            db.add(cf)

        # 11b. Compliance Frameworks (including Indian Banking & Regulatory Frameworks)
        frameworks_data = [
            ("NIST_CSF_2_0", "NIST Cybersecurity Framework 2.0", "2.0", "NIST standard for identifying, protecting, detecting, responding, and recovering from cyber incidents.", "National Institute of Standards and Technology", 106, 81, 76.4),
            ("ISO_27001_2022", "ISO/IEC 27001:2022 Information Security Management", "2022", "International benchmark for establishing, implementing, maintaining, and continually improving an ISMS.", "ISO / IEC", 93, 73, 78.5),
            ("CIS_V8", "CIS Critical Security Controls v8", "8.0", "Prioritized set of 18 critical cyber defense actions providing high-impact risk mitigation.", "Center for Internet Security", 153, 111, 72.5),
            ("RBI_CSF", "RBI Cyber Security Framework for Banks", "Annex 1-4", "Reserve Bank of India baseline cyber resilience controls mandated for scheduled commercial banks.", "Reserve Bank of India (RBI)", 65, 53, 81.5),
            ("SEBI_CSCRF", "SEBI Cyber Security and Cyber Resilience Framework", "2024", "Securities and Exchange Board of India framework covering critical market infrastructure and financial intermediaries.", "SEBI", 74, 59, 79.7)
        ]
        for f_code, f_name, f_ver, f_desc, f_reg, f_tot, f_map, f_cov in frameworks_data:
            fw = ComplianceFramework(
                code=f_code,
                name=f_name,
                version=f_ver,
                description=f_desc,
                regulatory_body=f_reg,
                total_controls=f_tot,
                mapped_controls=f_map,
                coverage_percentage=f_cov
            )
            db.add(fw)

        # 11c. Threat Indicators (IOCs & CVE mappings)
        indicators_data = [
            ("CVE", "CVE-2021-44228", 100.0, "CISA KEV / NVD", "CRITICAL"),
            ("CVE", "CVE-2022-22965", 98.0, "CISA KEV / VMware", "CRITICAL"),
            ("CVE", "CVE-2024-21762", 96.0, "CISA KEV / Fortinet", "CRITICAL"),
            ("IP", "185.220.101.45", 90.0, "AlienVault OTX (FIN7 C2 Ingress)", "HIGH"),
            ("DOMAIN", "auth-sync-gateway-check.net", 92.0, "Mandiant Threat Intel (Active Exfil Domain)", "CRITICAL"),
            ("HASH", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 85.0, "Wazuh Agent Host IOC", "HIGH"),
            ("TECHNIQUE", "T1190 - Exploit Public-Facing Application", 95.0, "MITRE ATT&CK Matrix", "CRITICAL"),
            ("TECHNIQUE", "T1078 - Valid Accounts (Lateral Movement)", 88.0, "MITRE ATT&CK Matrix", "HIGH")
        ]
        for i_type, i_val, i_conf, i_src, i_sev in indicators_data:
            ti = ThreatIndicator(
                organization_id=org.id,
                threat_id=created_threats[0].id if created_threats else None,
                indicator_type=i_type,
                value=i_val,
                confidence=i_conf,
                source=i_src,
                severity=i_sev
            )
            db.add(ti)

        # 11d. Modeled Risk Scenarios (Detailed scenario-level breakdown aggregating to Enterprise EAL)
        # Explicitly satisfying EAL = SLE * ARO consistency at the scenario level!
        scenarios_data = [
            ("Core Payment Database Ransomware & Extortion", created_assets[0].id if created_assets else None, 1.2, 0.7, 0.52, 8728000.0, 4538560.0, 6500000.0, 11500000.0, 85.0, True, {"cve": "CVE-2021-44228", "attack_vector": "Public Web -> Payment API -> Lateral -> DB"}),
            ("Internet Banking Portal RCE / Session Hijacking", created_assets[1].id if len(created_assets) > 1 else None, 2.5, 0.8, 1.40, 5200000.0, 7280000.0, 4000000.0, 7000000.0, 88.0, False, {"cve": "CVE-2022-22965", "attack_vector": "Public Facing Web Server"}),
            ("Payment API Gateway Credential Stuffing & Bypass", created_assets[2].id if len(created_assets) > 2 else None, 1.8, 0.6, 0.85, 6500000.0, 5525000.0, 5000000.0, 8500000.0, 82.0, False, {"cve": "CVE-2024-21762", "attack_vector": "API Endpoint SSL Portal"}),
            ("Active Directory Kerberoasting & Domain Takeover", created_assets[3].id if len(created_assets) > 3 else None, 1.0, 0.6, 0.60, 7500000.0, 4500000.0, 6000000.0, 10000000.0, 80.0, False, {"cve": "VULN-IAM-09", "attack_vector": "Unsegmented Workstation -> Domain Admin"}),
            ("Cloud Storage Customer KYC Data Exposure", created_assets[4].id if len(created_assets) > 4 else None, 1.4, 0.5, 0.70, 4000000.0, 2800000.0, 3000000.0, 5500000.0, 78.0, False, {"cve": "VULN-S3-01", "attack_vector": "Misconfigured S3 Bucket Permissions"}),
            ("Remaining Distributed Host Exposures (95 Assets Aggregate)", None, 3.2, 0.6, 1.92, 11123146.0, 21356440.0, 15000000.0, 28000000.0, 84.0, False, {"notes": "Aggregate of 95 non-crown-jewel enterprise assets and background threat events"})
        ]
        for s_name, s_aid, s_tef, s_vul, s_aro, s_sle, s_eal, s_min, s_max, s_conf, s_crown, s_det in scenarios_data:
            rs = RiskScenario(
                organization_id=org.id,
                asset_id=s_aid,
                name=s_name,
                threat_event_frequency=s_tef,
                vulnerability_exploitability=s_vul,
                loss_event_frequency=s_aro,
                single_loss_expectancy=s_sle,
                expected_annual_loss=s_eal,
                loss_magnitude_min=s_min,
                loss_magnitude_max=s_max,
                confidence_level=s_conf,
                is_primary_crown_jewel=s_crown,
                scenario_details=s_det
            )
            db.add(rs)

        # 12. Blockchain Transactions (Initial blocks for demonstration)
        audit_ledger.record_transaction(
            record_type="RISK_ASSESSMENT",
            record_id=current_assessment.id,
            payload_data={
                "assessment_id": current_assessment.id,
                "risk_score": 82.0,
                "expected_annual_loss": 46000000.0,
                "timestamp": now.isoformat()
            }
        )
        audit_ledger.record_transaction(
            record_type="OPTIMIZATION_RECOMMENDATION",
            record_id=opt_run.id,
            payload_data={
                "optimization_id": opt_run.id,
                "budget": 10000000.0,
                "recommended_investment": 8500000.0,
                "modeled_risk_reduction": 26000000.0
            }
        )

        _seed_security_incidents(db, org.id, created_assets)

        db.commit()
        print("Successfully seeded ABC Bank enterprise dataset (100 assets, 500 vulns, 20 controls, attack paths, security incidents, blockchain ledger)!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()

def _seed_security_incidents(db, org_id: str, assets: list):
    """
    Seeds realistic historical cybersecurity incident evidence for ABC Bank.
    Total historical observed loss across these 5 real incidents = ₹46.0 Lakh (₹0.46 Crore),
    clearly demonstrating distinction from modeled EAL (₹4.60 Crore).
    """
    asset_0 = assets[0].id if len(assets) > 0 else None
    asset_1 = assets[1].id if len(assets) > 1 else None
    asset_2 = assets[2].id if len(assets) > 2 else None
    asset_3 = assets[3].id if len(assets) > 3 else None
    asset_4 = assets[4].id if len(assets) > 4 else None

    incidents_data = [
        {
            "incident_id": "INC-2024-001",
            "incident_type": "Phishing / Credential Compromise",
            "incident_date": datetime(2024, 11, 18, 10, 15, 0),
            "affected_asset_id": asset_1,
            "asset_criticality": "High",
            "attack_vector": "Spear-Phishing -> Employee Session Hijacking",
            "cve_id": None,
            "cvss_score": None,
            "kev_status": False,
            "downtime_hours": 0.0,
            "revenue_loss": 0.0,
            "recovery_cost": 150000.0,
            "response_cost": 250000.0,
            "regulatory_cost": 0.0,
            "other_loss": 50000.0,
            "incident_status": "RESOLVED",
            "notes": "Targeted phishing campaign against customer support desk. Credentials isolated and revoked within 45 minutes."
        },
        {
            "incident_id": "INC-2025-002",
            "incident_type": "DDoS",
            "incident_date": datetime(2025, 3, 10, 14, 20, 0),
            "affected_asset_id": asset_2,
            "asset_criticality": "Critical",
            "attack_vector": "Volumetric UDP Reflection & Layer 7 HTTP Flood",
            "cve_id": None,
            "cvss_score": None,
            "kev_status": False,
            "downtime_hours": 2.5,
            "revenue_loss": 625000.0,
            "recovery_cost": 180000.0,
            "response_cost": 320000.0,
            "regulatory_cost": 0.0,
            "other_loss": 75000.0,
            "incident_status": "CLOSED",
            "notes": "Upstream ISP traffic scrubbers activated. Routed to Cloudflare Magic Transit."
        },
        {
            "incident_id": "INC-2025-003",
            "incident_type": "Vulnerability Exploitation",
            "incident_date": datetime(2025, 6, 22, 2, 45, 0),
            "affected_asset_id": asset_0,
            "asset_criticality": "Critical",
            "attack_vector": "Exploit Public Facing Application (Log4j JNDI lookup attempt)",
            "cve_id": "CVE-2021-44228",
            "cvss_score": 9.8,
            "kev_status": True,
            "downtime_hours": 1.0,
            "revenue_loss": 250000.0,
            "recovery_cost": 450000.0,
            "response_cost": 500000.0,
            "regulatory_cost": 200000.0,
            "other_loss": 100000.0,
            "incident_status": "RESOLVED",
            "notes": "Edge probe detected by WAF and blocked; egress firewall prevented lateral callback."
        },
        {
            "incident_id": "INC-2025-004",
            "incident_type": "Supply Chain Attack",
            "incident_date": datetime(2025, 9, 5, 9, 10, 0),
            "affected_asset_id": asset_4,
            "asset_criticality": "High",
            "attack_vector": "Third-Party SDK Dependency Compromise",
            "cve_id": "VULN-S3-01",
            "cvss_score": 7.5,
            "kev_status": False,
            "downtime_hours": 0.0,
            "revenue_loss": 0.0,
            "recovery_cost": 220000.0,
            "response_cost": 380000.0,
            "regulatory_cost": 150000.0,
            "other_loss": 50000.0,
            "incident_status": "RESOLVED",
            "notes": "Compromised third-party javascript package detected by SAST/SCA scanner."
        },
        {
            "incident_id": "INC-2025-005",
            "incident_type": "Ransomware (Attempted)",
            "incident_date": datetime(2025, 12, 14, 23, 10, 0),
            "affected_asset_id": asset_3,
            "asset_criticality": "Critical",
            "attack_vector": "Lateral Movement via Kerberoasting Attempt",
            "cve_id": "VULN-IAM-09",
            "cvss_score": 8.8,
            "kev_status": False,
            "downtime_hours": 0.5,
            "revenue_loss": 125000.0,
            "recovery_cost": 200000.0,
            "response_cost": 300000.0,
            "regulatory_cost": 0.0,
            "other_loss": 25000.0,
            "incident_status": "RESOLVED",
            "notes": "Kerberoasting attempt detected on domain service accounts. EDR instantly quarantined source workstation."
        }
    ]

    for d in incidents_data:
        total_loss = round(
            d["revenue_loss"] + d["recovery_cost"] + d["response_cost"] +
            d["regulatory_cost"] + d["other_loss"],
            2
        )
        inc = SecurityIncident(
            organization_id=org_id,
            incident_id=d["incident_id"],
            incident_type=d["incident_type"],
            incident_date=d["incident_date"],
            affected_asset_id=d["affected_asset_id"],
            asset_criticality=d["asset_criticality"],
            attack_vector=d["attack_vector"],
            cve_id=d["cve_id"],
            cvss_score=d["cvss_score"],
            kev_status=d["kev_status"],
            downtime_hours=d["downtime_hours"],
            revenue_loss=d["revenue_loss"],
            recovery_cost=d["recovery_cost"],
            response_cost=d["response_cost"],
            regulatory_cost=d["regulatory_cost"],
            other_loss=d["other_loss"],
            total_observed_loss=total_loss,
            incident_status=d["incident_status"],
            data_source="ACTUAL_ORGANIZATIONAL_DATA",
            notes=d["notes"],
            created_by="SecOps IR Team"
        )
        payload = {
            "incident_id": inc.incident_id,
            "incident_type": inc.incident_type,
            "incident_date": inc.incident_date.isoformat(),
            "total_observed_loss": inc.total_observed_loss,
            "revenue_loss": inc.revenue_loss,
            "recovery_cost": inc.recovery_cost,
            "response_cost": inc.response_cost,
            "regulatory_cost": inc.regulatory_cost,
            "other_loss": inc.other_loss,
            "incident_status": inc.incident_status
        }
        inc.canonical_hash = generate_canonical_hash(payload)
        try:
            blk = audit_ledger.record_transaction(
                record_type="SECURITY_INCIDENT_RECORDED",
                record_id=inc.incident_id,
                payload_data=payload
            )
            inc.blockchain_tx_id = blk.get("transaction_id")
        except Exception:
            pass

        db.add(inc)

    db.commit()

if __name__ == "__main__":
    seed_database()
