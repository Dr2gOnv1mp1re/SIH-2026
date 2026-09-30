import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON, Table
from sqlalchemy.orm import relationship
from app.database.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, unique=True)
    industry = Column(String(100), default="Banking")
    country = Column(String(100), default="India")
    employee_count = Column(Integer, default=2500)
    annual_revenue = Column(Float, default=5000000000.0)  # ₹500 Crore
    cybersecurity_budget = Column(Float, default=10000000.0)  # ₹1 Crore
    risk_appetite_enterprise = Column(Float, default=10000000.0)  # ₹1 Crore Max Acceptable Risk
    risk_appetite_critical_asset = Column(Float, default=1000000.0)  # ₹10 Lakh per Critical Asset
    financial_assumptions = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="organization", cascade="all, delete-orphan")
    business_services = relationship("BusinessService", back_populates="organization", cascade="all, delete-orphan")
    vulnerabilities = relationship("Vulnerability", back_populates="organization", cascade="all, delete-orphan")
    threats = relationship("Threat", back_populates="organization", cascade="all, delete-orphan")
    security_controls = relationship("SecurityControl", back_populates="organization", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="organization", cascade="all, delete-orphan")
    optimization_runs = relationship("OptimizationRun", back_populates="organization", cascade="all, delete-orphan")
    ciso_decisions = relationship("CISODecision", back_populates="organization", cascade="all, delete-orphan")
    threat_indicators = relationship("ThreatIndicator", back_populates="organization", cascade="all, delete-orphan")
    risk_scenarios = relationship("RiskScenario", back_populates="organization", cascade="all, delete-orphan")
    blockchain_transactions = relationship("BlockchainTransaction", back_populates="organization", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="organization", cascade="all, delete-orphan")
    security_incidents = relationship("SecurityIncident", back_populates="organization", cascade="all, delete-orphan")
    incident_calibrations = relationship("SecurityIncidentCalibration", back_populates="organization", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="organization", cascade="all, delete-orphan")

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(String(100), primary_key=True)  # dataset_id
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    name = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), default="CSV")  # CSV, XLSX, ZIP
    source = Column(String(255), default="User Upload")
    is_active = Column(Boolean, default=False)
    total_records = Column(Integer, default=0)
    valid_records = Column(Integer, default=0)
    rejected_records = Column(Integer, default=0)
    mapped_fields = Column(Integer, default=0)
    missing_fields = Column(Integer, default=0)
    warnings = Column(JSON, default=list)
    rejected_reasons = Column(JSON, default=list)
    field_mappings = Column(JSON, default=dict)
    summary = Column(JSON, default=dict)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="datasets")

    @property
    def dataset_id(self) -> str:
        return self.id

    @property
    def dataset_name(self) -> str:
        return self.name

    @property
    def original_filename(self) -> str:
        return self.filename

    @property
    def upload_timestamp(self) -> Optional[str]:
        return self.uploaded_at.isoformat() if self.uploaded_at else None

    @property
    def record_count(self) -> int:
        return self.total_records or 0

    @property
    def status(self) -> str:
        if self.is_active:
            return "Active"
        elif self.valid_records > 0:
            return "Validated"
        return "Uploaded"

    @property
    def schema_information(self) -> Dict[str, Any]:
        return self.field_mappings or {
            "mapped_fields": self.mapped_fields,
            "missing_fields": self.missing_fields
        }

    @property
    def source_type(self) -> str:
        return self.source or "Uploaded"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_id": self.id,
            "dataset_name": self.name,
            "original_filename": self.filename,
            "file_type": self.file_type,
            "source_type": self.source_type,
            "upload_timestamp": self.upload_timestamp,
            "record_count": self.total_records,
            "valid_records": self.valid_records,
            "rejected_records": self.rejected_records,
            "status": self.status,
            "is_active": self.is_active,
            "schema_information": self.schema_information,
            "warnings": self.warnings or []
        }

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="SECURITY_ANALYST")  # ADMIN, CISO, SECURITY_ANALYST, RISK_ANALYST, EXECUTIVE, AUDITOR
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="users")

class BusinessService(Base):
    __tablename__ = "business_services"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    criticality = Column(Float, default=90.0)  # 0-100
    hourly_revenue_impact = Column(Float, default=250000.0)  # ₹2.5 Lakh per hour downtime
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="business_services")
    assets = relationship("Asset", back_populates="business_service")

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(100), nullable=False)  # server, database, application, endpoint, laptop, api, cloud_resource, network_device, identity_system, storage
    ip_address = Column(String(100), nullable=True)
    hostname = Column(String(255), nullable=True)
    owner = Column(String(255), default="IT Operations")
    department = Column(String(255), default="Core Banking")
    operating_system = Column(String(100), default="Linux RHEL")
    business_service_id = Column(String(36), ForeignKey("business_services.id"), nullable=True)
    dataset_id = Column(String(100), default="sih_ps26105", index=True)
    
    # Criticality Components (0-100)
    business_importance = Column(Float, default=80.0)
    data_sensitivity = Column(Float, default=85.0)
    revenue_dependency = Column(Float, default=80.0)
    downtime_tolerance_hours = Column(Float, default=1.0)
    regulatory_importance = Column(Float, default=90.0)
    internet_exposed = Column(Boolean, default=False)
    criticality_score = Column(Float, default=85.0)  # Normalized 0-100
    
    # Calculated Risk & Financial Metrics
    current_risk_score = Column(Float, default=75.0)  # 0-100
    expected_annual_loss = Column(Float, default=1500000.0)  # EAL in Rupees
    status = Column(String(50), default="ACTIVE")
    tags = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="assets")
    business_service = relationship("BusinessService", back_populates="assets")
    vulnerabilities = relationship("Vulnerability", back_populates="asset", cascade="all, delete-orphan")
    security_incidents = relationship("SecurityIncident", back_populates="asset")

class AssetDependency(Base):
    __tablename__ = "asset_dependencies"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    source_asset_id = Column(String(36), ForeignKey("assets.id"), nullable=False)
    target_asset_id = Column(String(36), ForeignKey("assets.id"), nullable=False)
    dependency_type = Column(String(100), default="NETWORK_FLOW")  # NETWORK_FLOW, API_CALL, DB_CONNECTION, AUTH_TRUST
    impact_weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    affected_asset_id = Column(String(36), ForeignKey("assets.id"), nullable=False)
    cve_id = Column(String(50), nullable=False, index=True)
    dataset_id = Column(String(100), default="sih_ps26105", index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cvss_score = Column(Float, default=7.5)
    severity = Column(String(50), default="HIGH")  # LOW, MEDIUM, HIGH, CRITICAL
    exploit_available = Column(Boolean, default=False)
    active_exploitation = Column(Boolean, default=False)  # CISA KEV Known Exploited
    patch_available = Column(Boolean, default=True)
    remediation_status = Column(String(50), default="OPEN")  # OPEN, IN_PROGRESS, REMEDIATED
    discovery_date = Column(DateTime, default=datetime.utcnow)
    source = Column(String(100), default="Wazuh / OpenVAS")
    evidence = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="vulnerabilities")
    asset = relationship("Asset", back_populates="vulnerabilities")

class Threat(Base):
    __tablename__ = "threats"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    threat_actor = Column(String(255), default="FIN7 / Ransomware Syndicate")
    threat_type = Column(String(100), default="Ransomware & Extortion")
    attack_technique = Column(String(100), default="T1190 - Exploit Public-Facing App")  # MITRE ATT&CK
    threat_severity = Column(String(50), default="CRITICAL")
    active_campaign = Column(Boolean, default=True)
    exploit_cves = Column(JSON, default=list)  # List of targeted CVEs
    target_asset_types = Column(JSON, default=list)
    relevance_score = Column(Float, default=90.0)  # 0-100
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="threats")

class SecurityControl(Base):
    __tablename__ = "security_controls"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    code = Column(String(50), nullable=False)  # e.g., CTRL-MFA, CTRL-EDR, CTRL-SEG
    name = Column(String(255), nullable=False)
    category = Column(String(100), default="IAM")  # IAM, ENDPOINT, NETWORK, BACKUP, VULN_MGMT, SOC, TRAINING, ENCRYPTION
    description = Column(Text, nullable=True)
    coverage_percentage = Column(Float, default=70.0)
    effectiveness_percentage = Column(Float, default=75.0)
    maturity_level = Column(Integer, default=3)  # 1 to 5
    implementation_cost = Column(Float, default=1200000.0)  # e.g. ₹12 Lakh
    annual_cost = Column(Float, default=300000.0)
    modeled_risk_reduction = Column(Float, default=4500000.0)  # e.g. ₹45 Lakh reduction
    status = Column(String(50), default="PARTIALLY_DEPLOYED")
    prerequisites = Column(JSON, default=list)  # list of prerequisite control codes
    diminishing_return_factor = Column(Float, default=0.85)
    mitigated_vulnerabilities = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="security_controls")

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    assessment_name = Column(String(255), default="Continuous Enterprise Assessment")
    dataset_id = Column(String(100), default="sih_ps26105", index=True)
    enterprise_risk_score = Column(Float, default=82.0)  # 0-100
    risk_level = Column(String(50), default="CRITICAL")  # LOW, MEDIUM, HIGH, VERY HIGH, CRITICAL
    expected_annual_loss = Column(Float, default=46000000.0)  # ₹4.6 Crore
    modeled_loss_min = Column(Float, default=35000000.0)
    modeled_loss_max = Column(Float, default=62000000.0)
    confidence_percentage = Column(Float, default=85.0)
    assessment_trigger = Column(String(255), default="Scheduled Continuous Evaluation")
    risk_contributors = Column(JSON, default=dict)
    canonical_hash = Column(String(64), nullable=True)  # SHA-256
    blockchain_tx_id = Column(String(100), nullable=True)
    is_tampered = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="risk_assessments")

class RiskHistory(Base):
    __tablename__ = "risk_history"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(Float, nullable=False)
    expected_annual_loss = Column(Float, nullable=False)
    trigger_event = Column(String(255), nullable=False)
    details = Column(JSON, default=dict)

class FinancialModel(Base):
    __tablename__ = "financial_models"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), default="Standard FAIR-Aligned Financial Model")
    hourly_downtime_cost = Column(Float, default=300000.0)  # ₹3 Lakh / hour
    incident_response_hourly_rate = Column(Float, default=25000.0)  # ₹25,000 / hour
    data_recovery_base_cost = Column(Float, default=1500000.0)  # ₹15 Lakh
    legal_regulatory_base_cost = Column(Float, default=2000000.0)  # ₹20 Lakh
    customer_impact_multiplier = Column(Float, default=1.5)
    business_interruption_multiplier = Column(Float, default=1.2)
    probability_multiplier = Column(Float, default=1.0)
    version = Column(String(50), default="1.0.0")
    updated_at = Column(DateTime, default=datetime.utcnow)

class MLModelRegistry(Base):
    __tablename__ = "ml_models"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_name = Column(String(100), default="XGBoost Cyber Risk Regressor")
    model_type = Column(String(50), default="XGBoost")  # XGBoost, RandomForest
    version = Column(String(50), default="v2.4.1")
    rmse = Column(Float, default=2.14)
    mae = Column(Float, default=1.65)
    r2_score = Column(Float, default=0.94)
    feature_names = Column(JSON, default=list)
    hyperparameters = Column(JSON, default=dict)
    dataset_size = Column(Integer, default=5000)
    trained_at = Column(DateTime, default=datetime.utcnow)

class MLPredictionRecord(Base):
    __tablename__ = "ml_predictions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    predicted_30d_risk = Column(Float, default=95.0)
    predicted_30d_eal = Column(Float, default=9500000.0)  # ₹95 Lakh
    predicted_60d_eal = Column(Float, default=12000000.0)
    predicted_90d_eal = Column(Float, default=15500000.0)
    trend = Column(String(50), default="INCREASING")
    confidence_percentage = Column(Float, default=82.0)
    shap_explanation = Column(JSON, default=dict)  # Local feature impacts
    created_at = Column(DateTime, default=datetime.utcnow)

class OptimizationRun(Base):
    __tablename__ = "optimization_runs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    dataset_id = Column(String(100), default="sih_ps26105", index=True)
    budget_amount = Column(Float, default=10000000.0)  # ₹1 Crore
    current_modeled_risk = Column(Float, default=46000000.0)  # ₹4.6 Crore
    projected_modeled_risk = Column(Float, default=20000000.0)  # ₹2.0 Crore
    modeled_risk_reduction = Column(Float, default=26000000.0)  # ₹2.6 Crore
    total_investment = Column(Float, default=8500000.0)  # ₹85 Lakh
    efficiency_metric = Column(Float, default=3.06)  # 2.6Cr / 85L = 3.06x
    selected_controls = Column(JSON, default=list)
    status = Column(String(50), default="RECOMMENDED")  # RECOMMENDED, CISO_APPROVED, IMPLEMENTED, REJECTED
    approved_by = Column(String(255), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)
    canonical_hash = Column(String(64), nullable=True)
    blockchain_tx_id = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="optimization_runs")

class ScenarioRecord(Base):
    __tablename__ = "scenarios"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    parameters = Column(JSON, default=dict)
    baseline_risk = Column(Float, default=46000000.0)
    simulated_risk = Column(Float, default=20000000.0)
    modeled_risk_reduction = Column(Float, default=26000000.0)
    base_dataset_id = Column(String(100), default="sih_ps26105")
    created_by = Column(String(255), default="CISO / Security Architect")
    changes = Column(JSON, default=list)
    status = Column(String(50), default="SAVED")  # SAVED, RUNNING, COMPARISON, RESET
    investment_cost = Column(Float, default=0.0)
    financial_exposure_before = Column(Float, nullable=True)
    financial_exposure_after = Column(Float, nullable=True)
    attack_paths_affected = Column(JSON, default=list)
    affected_assets = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

class AttackPathRecord(Base):
    __tablename__ = "attack_paths"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), default="External Exploit -> Payment DB")
    target_asset_name = Column(String(255), default="Payment Database Cluster")
    path_length = Column(Integer, default=5)
    path_risk_score = Column(Float, default=94.0)
    nodes_chain = Column(JSON, default=list)
    vulnerabilities = Column(JSON, default=list)
    missing_controls = Column(JSON, default=list)
    affected_services = Column(JSON, default=list)
    potential_financial_impact = Column(Float, default=7200000.0)  # ₹72 Lakh EAL
    recommended_mitigations = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

class ComplianceFinding(Base):
    __tablename__ = "compliance_findings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    framework = Column(String(50), default="NIST CSF")  # NIST CSF, ISO 27001, CIS Controls
    control_code = Column(String(50), nullable=False)
    requirement_title = Column(String(255), nullable=False)
    status = Column(String(50), default="GAP")  # COMPLIANT, GAP, PARTIAL
    gap_description = Column(Text, nullable=True)
    evidence_summary = Column(Text, nullable=True)
    evidence_hash = Column(String(64), nullable=True)
    recommended_remediation = Column(Text, nullable=True)
    owner = Column(String(255), default="Security Engineering")
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class BlockchainTransaction(Base):
    __tablename__ = "blockchain_transactions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    record_type = Column(String(50), nullable=False)  # ASSESSMENT, RECOMMENDATION, CISO_APPROVAL, COMPLIANCE_EVIDENCE
    record_id = Column(String(36), nullable=False)
    canonical_sha256_hash = Column(String(64), nullable=False)
    previous_block_hash = Column(String(64), nullable=False)
    block_number = Column(Integer, nullable=False)
    payload_snapshot = Column(JSON, nullable=False)
    transaction_id = Column(String(100), nullable=False, unique=True)
    status = Column(String(50), default="VERIFIED")  # VERIFIED, TAMPERED, PENDING
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="blockchain_transactions")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String(36), nullable=True)
    user_email = Column(String(255), nullable=True)
    dataset_id = Column(String(100), default="sih_ps26105", index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(100), default="127.0.0.1")
    event_id = Column(String(100), nullable=True)
    event_type = Column(String(100), nullable=True)
    integrity_hash = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="audit_logs")

class CISODecision(Base):
    __tablename__ = "ciso_decisions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    user_name = Column(String(255), nullable=False)
    user_role = Column(String(50), nullable=False, default="CISO")
    dataset_id = Column(String(100), default="sih_ps26105", index=True)
    recommendation_id = Column(String(100), nullable=True)
    version = Column(Integer, default=1)
    scenario_id = Column(String(100), nullable=True)
    decision = Column(String(50), nullable=False)  # APPROVE, REJECT, MODIFY, REQUEST_REVIEW
    status = Column(String(50), default="COMMITTED")  # COMMITTED, PENDING, REJECTED, MODIFIED
    decision_notes = Column(Text, nullable=True)
    comments = Column(Text, nullable=True)
    portfolio_snapshot = Column(JSON, default=list)
    approved_controls = Column(JSON, default=list)
    current_eal = Column(Float, default=46000000.0)
    projected_eal = Column(Float, default=20000000.0)
    modeled_risk_reduction = Column(Float, default=26000000.0)
    risk_before = Column(Float, nullable=True)
    projected_risk_after = Column(Float, nullable=True)
    financial_exposure_before = Column(Float, nullable=True)
    projected_financial_exposure_after = Column(Float, nullable=True)
    budget_allocated = Column(Float, default=10000000.0)
    approved_budget = Column(Float, nullable=True)
    investment_approved = Column(Float, default=8500000.0)
    confidence_percentage = Column(Float, default=85.0)
    canonical_hash = Column(String(64), nullable=True)
    blockchain_tx_id = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="ciso_decisions")

class ThreatIndicator(Base):
    __tablename__ = "threat_indicators"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    threat_id = Column(String(36), ForeignKey("threats.id"), nullable=True)
    indicator_type = Column(String(50), nullable=False)  # IP, DOMAIN, HASH, CVE, TECHNIQUE
    dataset_id = Column(String(100), default="sih_ps26105", index=True)
    value = Column(String(255), nullable=False)
    confidence = Column(Float, default=85.0)
    source = Column(String(100), default="CISA KEV / MITRE ATT&CK")
    severity = Column(String(50), default="HIGH")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="threat_indicators")

class RiskScenario(Base):
    __tablename__ = "risk_scenarios"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    asset_id = Column(String(36), ForeignKey("assets.id"), nullable=True)
    name = Column(String(255), nullable=False)
    dataset_id = Column(String(100), default="sih_ps26105", index=True)
    threat_event_frequency = Column(Float, default=1.2)
    vulnerability_exploitability = Column(Float, default=0.7)
    loss_event_frequency = Column(Float, default=0.52)  # ARO
    single_loss_expectancy = Column(Float, default=8728000.0)  # SLE in INR
    expected_annual_loss = Column(Float, default=4538560.0)  # EAL = SLE * ARO
    loss_magnitude_min = Column(Float, default=6500000.0)
    loss_magnitude_max = Column(Float, default=11500000.0)
    confidence_level = Column(Float, default=85.0)
    is_primary_crown_jewel = Column(Boolean, default=False)
    scenario_details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="risk_scenarios")

class ComplianceFramework(Base):
    __tablename__ = "compliance_frameworks"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    code = Column(String(50), nullable=False, unique=True)  # NIST_CSF, ISO_27001, CIS_V8, RBI_CSF, SEBI_CSCRF
    name = Column(String(255), nullable=False)
    version = Column(String(50), default="2.0")
    description = Column(Text, nullable=True)
    regulatory_body = Column(String(100), default="RBI / SEBI / NIST")
    total_controls = Column(Integer, default=50)
    mapped_controls = Column(Integer, default=42)
    coverage_percentage = Column(Float, default=84.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class ComplianceControl(Base):
    __tablename__ = "compliance_controls"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    framework_code = Column(String(50), nullable=False)
    control_code = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(100), default="IDENTIFY")
    requirement = Column(Text, nullable=True)
    status = Column(String(50), default="COMPLIANT")  # COMPLIANT, PARTIAL, GAP
    mapped_security_control_code = Column(String(50), nullable=True)
    evidence_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class SecurityIncident(Base):
    __tablename__ = "security_incidents"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    incident_id = Column(String(100), nullable=False, index=True)
    dataset_id = Column(String(100), default="sih_ps26105", index=True)
    incident_type = Column(String(100), nullable=False)  # Ransomware, Data Breach, DDoS, Phishing, API Abuse, Supply Chain, Insider Threat
    incident_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    affected_asset_id = Column(String(36), ForeignKey("assets.id"), nullable=True)
    asset_criticality = Column(String(50), default="High")  # Critical, High, Medium, Low
    attack_vector = Column(String(255), default="Phishing")
    cve_id = Column(String(100), nullable=True)
    cvss_score = Column(Float, nullable=True)
    kev_status = Column(Boolean, default=False)
    downtime_hours = Column(Float, default=0.0)
    
    # Financial Component Losses (INR, >= 0.0)
    revenue_loss = Column(Float, default=0.0)
    recovery_cost = Column(Float, default=0.0)
    response_cost = Column(Float, default=0.0)
    regulatory_cost = Column(Float, default=0.0)
    other_loss = Column(Float, default=0.0)
    total_observed_loss = Column(Float, default=0.0)  # Calculated server-side as sum of components
    
    incident_status = Column(String(50), default="RESOLVED")  # OPEN, CONTAINED, RESOLVED, CLOSED
    data_source = Column(String(50), default="ACTUAL_ORGANIZATIONAL_DATA")  # ACTUAL_ORGANIZATIONAL_DATA, SIMULATED_DEMO_DATA
    notes = Column(Text, nullable=True)
    created_by = Column(String(255), default="System")
    canonical_hash = Column(String(64), nullable=True)
    blockchain_tx_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="security_incidents")
    asset = relationship("Asset", back_populates="security_incidents")

class SecurityIncidentCalibration(Base):
    __tablename__ = "security_incident_calibrations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    calibrated_by = Column(String(255), nullable=False)
    calibration_status = Column(String(50), default="APPROVED")  # PROPOSED, APPROVED, REJECTED
    data_sufficiency = Column(String(50), default="SUFFICIENT")  # SUFFICIENT, INSUFFICIENT, MARGINAL
    incident_count = Column(Integer, default=0)
    previous_assumptions = Column(JSON, default=dict)
    calibrated_assumptions = Column(JSON, default=dict)
    observed_loss_mean = Column(Float, default=0.0)
    observed_annual_frequency = Column(Float, default=0.0)
    canonical_hash = Column(String(64), nullable=True)
    blockchain_tx_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="incident_calibrations")

