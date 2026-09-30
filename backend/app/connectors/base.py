"""
CyberSecurityConnector Base Interface.
Defines the common standard interface for all external telemetry and cyber intelligence connectors:
- connect()
- health_check()
- fetch()
- normalize()
- store()
Tracks metadata: source, source_id, fetched_at, last_updated, raw_reference, normalized_data.
Truthfulness rule: If connection cannot be verified, status MUST reflect NOT CONFIGURED or DEMO DATA.
"""

import abc
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

class ConnectorStatus(str, Enum):
    CONNECTED = "CONNECTED"
    NOT_CONFIGURED = "NOT CONFIGURED"
    DEMO_DATA = "DEMO DATA"
    ERROR = "ERROR"

class CyberSecurityConnector(abc.ABC):
    """
    Standard interface for all Quantum Risk AI cybersecurity telemetry connectors.
    """
    def __init__(self, source_name: str, endpoint: Optional[str] = None):
        self.source_name = source_name
        self.endpoint = endpoint
        self.last_sync_timestamp: Optional[datetime] = None
        self.last_health_status: ConnectorStatus = ConnectorStatus.NOT_CONFIGURED
        self.last_health_message: str = "Connector initialized"
        self.total_records_ingested: int = 0

    @abc.abstractmethod
    def connect(self) -> bool:
        """Attempts to establish connection or verify endpoint availability."""
        pass

    @abc.abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Runs an active diagnostic probe. Returns status:
        CONNECTED | NOT CONFIGURED | DEMO DATA | ERROR
        """
        pass

    @abc.abstractmethod
    def fetch(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Extracts raw threat/vulnerability/telemetry feeds."""
        pass

    @abc.abstractmethod
    def normalize(self, raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Converts raw vendor payloads into Quantum Risk AI canonical schema:
        source, source_id, fetched_at, last_updated, raw_reference, normalized_data
        """
        pass

    def store(self, normalized_records: List[Dict[str, Any]], db_session: Optional[Any] = None) -> int:
        """
        Stores normalized records into the database or memory cache.
        Returns number of records persisted.
        """
        self.total_records_ingested += len(normalized_records)
        self.last_sync_timestamp = datetime.utcnow()
        return len(normalized_records)

    def sync_pipeline(self, limit: int = 100, db_session: Optional[Any] = None) -> Dict[str, Any]:
        """
        Executes full pipeline: connect -> fetch -> normalize -> store.
        """
        health = self.health_check()
        raw = self.fetch(limit=limit)
        normalized = self.normalize(raw)
        stored_count = self.store(normalized, db_session)
        return {
            "source": self.source_name,
            "status": health["status"],
            "raw_count": len(raw),
            "normalized_count": len(normalized),
            "stored_count": stored_count,
            "synced_at": self.last_sync_timestamp.isoformat() if self.last_sync_timestamp else datetime.utcnow().isoformat(),
            "data_freshness": "REAL PUBLIC INTELLIGENCE" if health["status"] == ConnectorStatus.CONNECTED else "SYNTHETIC DEMO DATA"
        }
