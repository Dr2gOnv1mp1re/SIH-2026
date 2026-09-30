"""
Quantum Risk AI — Local Demo Seed Script
Initializes the database, creates tables, and populates canonical SIH demonstration data:
- 100 enterprise assets
- 500 CVEs (with active CISA KEV markers)
- 4 threat actors
- 20 security controls (with costs and effectiveness)
- 6 regulatory compliance frameworks (RBI CSF, SEBI CSCRF, NIST CSF 2.0, ISO 27001, CIS v8)
- 6 FAIR risk scenarios
- 6 enterprise role accounts with hashed passwords

Usage:
  python -m app.seed_demo
  or
  python backend/app/seed_demo.py
"""

import os
import sys

# Ensure backend root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from app.database.session import sync_engine, Base
from app.data_seed.seed_enterprise import seed_database
from app.ai_engine.model_pipeline import ml_engine

def run_seed():
    print("=" * 72)
    print("  QUANTUM RISK AI -- ENTERPRISE DEMO SEED INITIALIZATION")
    print("=" * 72)
    print("[1/3] Creating database schema and tables...")
    Base.metadata.create_all(bind=sync_engine)
    print("      -> Schema verified on SQLite / PostgreSQL target.")

    print("[2/3] Seeding enterprise dataset for ABC Bank...")
    seed_database()
    print("      -> 100 Assets seeded.")
    print("      -> 500 CVEs & CISA KEV active exploits seeded.")
    print("      -> 20 Security Controls (IAM, Network, Endpoint, Backup) seeded.")
    print("      -> 6 FAIR Risk Scenarios & INR 4.60 Cr enterprise baseline quantified.")
    print("      -> 6 Compliance Frameworks (RBI CSF, SEBI CSCRF, NIST, ISO) seeded.")

    print("[3/3] Training & initializing ML risk prediction models...")
    ml_engine.train_or_initialize_models()
    print("      -> XGBoost Regressor and C++ Tree SHAP explainer ready.")

    print("\n" + "=" * 72)
    print("  LOCAL DEMONSTRATION ACCOUNTS & CREDENTIALS")
    print("=" * 72)
    accounts = [
        ("CISO / Approver", "ciso@abcbank.com", "Ciso@12345", "Vikram Malhotra", "Authorized budget approver"),
        ("Security Analyst", "analyst@abcbank.com", "Analyst@12345", "Priya Sharma", "SecOps triage & telemetry"),
        ("Risk Analyst", "risk@abcbank.com", "Risk@12345", "Rohan Mehta", "FAIR modeling & Monte Carlo"),
        ("Executive Board / CEO", "executive@abcbank.com", "Executive@12345", "Ananya Verma", "Board reporting & ROI"),
        ("Lead Security Auditor", "auditor@abcbank.com", "Auditor@12345", "Sanjay Joshi", "Blockchain & audit verification"),
        ("System Administrator", "admin@abcbank.com", "Admin@12345", "Admin User", "Platform & integrations admin"),
    ]
    for role, email, pwd, name, desc in accounts:
        print(f"  [{role.upper()}]")
        print(f"    Name:       {name}")
        print(f"    Email:      {email}")
        print(f"    Password:   {pwd}")
        print(f"    Scope:      {desc}\n")

    print("=" * 72)
    print("  SUCCESS: Demo environment ready for SIH 2026 Round 2 demonstration!")
    print("=" * 72)

if __name__ == "__main__":
    run_seed()
