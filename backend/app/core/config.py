import os
from pydantic_settings import BaseSettings
from typing import List

BASE_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_FILE = os.path.join(BASE_BACKEND_DIR, "cyber_risk_enterprise.db").replace("\\", "/")

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI-Powered Cyber Risk Quantification & Investment Optimization Platform"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security & Auth
    SECRET_KEY: str = os.getenv("JWT_SECRET", "super-secret-enterprise-cyber-risk-key-2026-sih-quantum-safe")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DEFAULT_DB_FILE}")
    SYNC_DATABASE_URL: str = os.getenv("SYNC_DATABASE_URL", f"sqlite:///{DEFAULT_DB_FILE}")
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Default Organization Seeds
    DEFAULT_ORG_NAME: str = "ABC Bank"
    DEFAULT_ORG_INDUSTRY: str = "Banking & Financial Services"
    DEFAULT_ORG_REVENUE: float = 5000000000.0  # ₹500 Crore (5,000,000,000)
    DEFAULT_ORG_BUDGET: float = 10000000.0     # ₹1 Crore (10,000,000)
    DEFAULT_ORG_EMPLOYEES: int = 2500
    
    # Risk Appetite Defaults (in Rupees)
    DEFAULT_RISK_APPETITE_MAX_ENTERPRISE: float = 10000000.0  # ₹1 Crore
    DEFAULT_RISK_APPETITE_CRITICAL_ASSET: float = 1000000.0   # ₹10 Lakh
    
    # Blockchain Audit Configuration
    ENABLE_HYPERLEDGER_FABRIC: bool = False  # If True uses Fabric Gateway SDK; fallback uses cryptographic SHA-256 block ledger
    BLOCKCHAIN_NETWORK_NAME: str = "Enterprise-Audit-Fabric-Channel"
    
    class Config:
        case_sensitive = True

settings = Settings()
