from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class TemporalContext:
    reference_time: datetime
    operators: List[str]
    time_start: Optional[datetime]
    time_end: Optional[datetime]
    granularity: str


@dataclass
class RetrievalResult:
    doc_id: str
    content: str
    source: str
    score: float
    valid_from: Optional[datetime]
    valid_to: Optional[datetime]


@dataclass
class FusedRetrievalResult:
    doc_id: str
    content: str
    sources: List[str]
    fused_score: float
    source_scores: dict[str, float]
    valid_from: Optional[datetime]
    valid_to: Optional[datetime]


@dataclass
class QueryResponse:
    answer: str
    sources: List[FusedRetrievalResult]
    temporal_context: TemporalContext
