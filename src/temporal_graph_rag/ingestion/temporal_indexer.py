from datetime import datetime
from typing import Optional


class TemporalIndexer:
    """Stub indexer for temporal payloads."""

    def index_document(
        self,
        content: str,
        valid_from: datetime,
        valid_to: Optional[datetime],
        entities: list[str],
    ) -> dict:
        return {
            "content": content,
            "valid_from": valid_from.isoformat(),
            "valid_to": valid_to.isoformat() if valid_to else None,
            "entities": entities,
            "ingestion_time": datetime.utcnow().isoformat(),
        }
