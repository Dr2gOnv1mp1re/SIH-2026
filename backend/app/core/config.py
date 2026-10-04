import json
import os
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Vercel's function filesystem is read-only except /tmp, so the default SQLite file lives there.
# (Ephemeral: re-created and re-seeded on cold start. Set DATABASE_URL to a hosted Postgres for persistence.)
IS_VERCEL = bool(os.getenv("VERCEL"))
_DB_DIR = "/tmp" if IS_VERCEL else BASE_BACKEND_DIR
DEFAULT_DB_FILE = os.path.join(_DB_DIR, "cyber_risk_enterprise.db").replace("\\", "/")


def _absolutize_sqlite(url: str) -> str:
    prefixes = ("sqlite+aiosqlite:///", "sqlite:///")
    for prefix in prefixes:
        if url.startswith(prefix):
            path = url[len(prefix):]
            if path.startswith(":memory:"):
                return url
            if path.startswith("/") or (len(path) > 1 and path[1] == ":"):
                return url
            abs_path = os.path.abspath(os.path.join(BASE_BACKEND_DIR, path)).replace("\\", "/")
            return prefix + abs_path
    return url


def to_async_db_url(url: str) -> str:
    url = (url or "").strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("sqlite:///") and "+aiosqlite" not in url:
        url = url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return _absolutize_sqlite(url)


def to_sync_db_url(url: str) -> str:
    url = (url or "").strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("sqlite+aiosqlite://"):
        url = url.replace("sqlite+aiosqlite:", "sqlite:", 1)
    return _absolutize_sqlite(url)


def parse_cors_origins(raw: str) -> List[str]:
    value = (raw or "").strip()
    if not value or value == "*":
        return []
    if value.startswith("["):
        try:
            parsed = json.loads(value)
            return [str(item).strip() for item in parsed if str(item).strip() and str(item).strip() != "*"]
        except json.JSONDecodeError:
            pass
    return [part.strip() for part in value.split(",") if part.strip() and part.strip() != "*"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_BACKEND_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    PROJECT_NAME: str = "AI-Powered Cyber Risk Quantification & Investment Optimization Platform"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = os.getenv("JWT_SECRET", "super-secret-enterprise-cyber-risk-key-2026-sih-quantum-safe")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    DATABASE_URL: str = f"sqlite+aiosqlite:///{DEFAULT_DB_FILE}"
    SYNC_DATABASE_URL: str = ""

    CORS_ORIGINS: str = "*"
    FRONTEND_URL: str = ""

    DEFAULT_ORG_NAME: str = "ABC Bank"
    DEFAULT_ORG_INDUSTRY: str = "Banking & Financial Services"
    DEFAULT_ORG_REVENUE: float = 5000000000.0
    DEFAULT_ORG_BUDGET: float = 10000000.0
    DEFAULT_ORG_EMPLOYEES: int = 2500

    DEFAULT_RISK_APPETITE_MAX_ENTERPRISE: float = 10000000.0
    DEFAULT_RISK_APPETITE_CRITICAL_ASSET: float = 1000000.0

    ENABLE_HYPERLEDGER_FABRIC: bool = False
    BLOCKCHAIN_NETWORK_NAME: str = "Enterprise-Audit-Fabric-Channel"

    def cors_origin_list(self) -> List[str]:
        origins = parse_cors_origins(self.CORS_ORIGINS)
        frontend = (self.FRONTEND_URL or "").strip().rstrip("/")
        if frontend and frontend not in origins:
            origins.append(frontend)
        return origins


_settings = Settings()
_settings.DATABASE_URL = to_async_db_url(_settings.DATABASE_URL)
if _settings.SYNC_DATABASE_URL:
    _settings.SYNC_DATABASE_URL = to_sync_db_url(_settings.SYNC_DATABASE_URL)
else:
    _settings.SYNC_DATABASE_URL = to_sync_db_url(_settings.DATABASE_URL)

settings = _settings
