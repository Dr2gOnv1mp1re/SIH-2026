import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

# Async Engine (for FastAPI async request handlers)
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Sync Engine (for initial seed data and background calculations)
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.SYNC_DATABASE_URL else {}
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

def ensure_sqlite_schema():
    """Ensures dataset_id column exists on existing SQLite tables without losing data."""
    if "sqlite" not in settings.SYNC_DATABASE_URL:
        return
    import sqlite3
    db_path = settings.SYNC_DATABASE_URL.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        return
    try:
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        tables_to_check = [
            "assets", "vulnerabilities", "threat_indicators", "risk_assessments",
            "optimization_runs", "ciso_decisions", "audit_logs", "risk_scenarios",
            "security_incidents"
        ]
        for tbl in tables_to_check:
            table_exists = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tbl}'").fetchone()
            if table_exists:
                cols = [c[1] for c in cur.execute(f"PRAGMA table_info({tbl})").fetchall()]
                if "dataset_id" not in cols:
                    cur.execute(f"ALTER TABLE {tbl} ADD COLUMN dataset_id VARCHAR(100) DEFAULT 'sih_ps26105'")
                if tbl == "optimization_runs" and "timestamp" not in cols:
                    cur.execute(f"ALTER TABLE {tbl} ADD COLUMN timestamp DATETIME DEFAULT NULL")
                    cur.execute(f"UPDATE {tbl} SET timestamp = created_at WHERE timestamp IS NULL")

        # Specific columns for Phase 7-9 governance & scenario engine
        extra_columns = {
            "ciso_decisions": [
                ("recommendation_id", "VARCHAR(100)"),
                ("version", "INTEGER DEFAULT 1"),
                ("scenario_id", "VARCHAR(100)"),
                ("status", "VARCHAR(50) DEFAULT 'COMMITTED'"),
                ("comments", "TEXT"),
                ("approved_controls", "JSON"),
                ("approved_budget", "FLOAT"),
                ("risk_before", "FLOAT"),
                ("projected_risk_after", "FLOAT"),
                ("financial_exposure_before", "FLOAT"),
                ("projected_financial_exposure_after", "FLOAT")
            ],
            "scenarios": [
                ("base_dataset_id", "VARCHAR(100) DEFAULT 'sih_ps26105'"),
                ("created_by", "VARCHAR(255) DEFAULT 'CISO / Security Architect'"),
                ("changes", "JSON"),
                ("status", "VARCHAR(50) DEFAULT 'SAVED'"),
                ("investment_cost", "FLOAT DEFAULT 0.0"),
                ("financial_exposure_before", "FLOAT"),
                ("financial_exposure_after", "FLOAT"),
                ("attack_paths_affected", "JSON"),
                ("affected_assets", "JSON")
            ],
            "audit_logs": [
                ("event_id", "VARCHAR(100)"),
                ("event_type", "VARCHAR(100)"),
                ("integrity_hash", "VARCHAR(64)"),
                ("description", "TEXT")
            ]
        }
        for tbl, cols_list in extra_columns.items():
            tbl_exists = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tbl}'").fetchone()
            if tbl_exists:
                existing = [c[1] for c in cur.execute(f"PRAGMA table_info({tbl})").fetchall()]
                for col_name, col_def in cols_list:
                    if col_name not in existing:
                        cur.execute(f"ALTER TABLE {tbl} ADD COLUMN {col_name} {col_def}")

        # Create performance and integrity indexes (Section 11 & 12)
        indexes = [
            ("idx_assets_org", "assets", "organization_id"),
            ("idx_vulns_org", "vulnerabilities", "organization_id"),
            ("idx_vulns_asset", "vulnerabilities", "affected_asset_id"),
            ("idx_vulns_cve", "vulnerabilities", "cve_id"),
            ("idx_assessments_org_time", "risk_assessments", "organization_id, timestamp"),
            ("idx_opt_runs_org", "optimization_runs", "organization_id"),
            ("idx_ciso_dec_org", "ciso_decisions", "organization_id"),
            ("idx_ciso_dec_rec", "ciso_decisions", "recommendation_id"),
            ("idx_audit_logs_org_time", "audit_logs", "organization_id, timestamp"),
            ("idx_audit_logs_evt", "audit_logs", "event_type"),
            ("idx_datasets_active", "datasets", "is_active")
        ]
        for idx_name, tbl, cols in indexes:
            tbl_exists = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tbl}'").fetchone()
            if tbl_exists:
                cur.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {tbl} ({cols})")

        con.commit()
        con.close()
    except Exception as e:
        print(f"[SCHEMA MIGRATION WARNING]: {e}")


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()
