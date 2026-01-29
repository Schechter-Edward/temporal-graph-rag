from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional
import re
import math


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
class QueryResponse:
    answer: str
    sources: List[RetrievalResult]
    temporal_context: TemporalContext


class TemporalGraphRAG:
    """Minimal, runnable temporal RAG skeleton with hybrid fusion.

    Replace in-memory stores with Neo4j/Qdrant/Elasticsearch in production.
    """

    def __init__(self) -> None:
        self._docs = [
            {
                "id": "doc-1",
                "content": "Alice led Project Orion from 2023-01 to 2024-02.",
                "valid_from": datetime(2023, 1, 1),
                "valid_to": datetime(2024, 2, 28),
            },
            {
                "id": "doc-2",
                "content": "Bob took over infrastructure in 2024-03 after the reorg.",
                "valid_from": datetime(2024, 3, 1),
                "valid_to": None,
            },
            {
                "id": "doc-3",
                "content": "The March 2024 reorg shifted ownership to Platform Ops.",
                "valid_from": datetime(2024, 3, 1),
                "valid_to": datetime(2024, 3, 31),
            },
        ]

    def query(self, query: str, reference_time: Optional[datetime] = None) -> QueryResponse:
        ref_time = reference_time or datetime.utcnow()
        ctx = self._parse_temporal_context(query, ref_time)

        graph_results = self._graph_retrieve(query, ctx)
        dense_results = self._dense_retrieve(query, ctx)
        sparse_results = self._sparse_retrieve(query, ctx)

        fused = self._temporal_rrf([graph_results, dense_results, sparse_results], ctx)
        top = fused[:5]

        answer = self._synthesize(query, top, ctx)
        return QueryResponse(answer=answer, sources=top, temporal_context=ctx)

    def _parse_temporal_context(self, query: str, ref_time: datetime) -> TemporalContext:
        operators: List[str] = []
        time_start: Optional[datetime] = None
        time_end: Optional[datetime] = None
        granularity = "day"

        lower = query.lower()
        if "before" in lower:
            operators.append("BEFORE")
        if "after" in lower:
            operators.append("AFTER")
        if "during" in lower:
            operators.append("DURING")
        if "between" in lower:
            operators.append("BETWEEN")

        year_match = re.search(r"(19|20)\d{2}", lower)
        if year_match:
            year = int(year_match.group(0))
            time_start = datetime(year, 1, 1)
            time_end = datetime(year, 12, 31)
            granularity = "year"

        month_match = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(19|20)\d{2}", lower)
        if month_match:
            month_map = {
                "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
            }
            month = month_map[month_match.group(1)[:3]]
            year = int(month_match.group(2))
            time_start = datetime(year, month, 1)
            time_end = datetime(year, month, 28)
            granularity = "month"

        return TemporalContext(
            reference_time=ref_time,
            operators=operators,
            time_start=time_start,
            time_end=time_end,
            granularity=granularity,
        )

    def _graph_retrieve(self, query: str, ctx: TemporalContext) -> List[RetrievalResult]:
        # Placeholder: treat any doc mentioning query tokens as graph hits.
        tokens = set(query.lower().split())
        results: List[RetrievalResult] = []
        for doc in self._docs:
            if tokens & set(doc["content"].lower().split()):
                score = 0.9
                results.append(self._wrap(doc, "graph", score))
        return results

    def _dense_retrieve(self, query: str, ctx: TemporalContext) -> List[RetrievalResult]:
        # Placeholder for vector retrieval.
        results: List[RetrievalResult] = []
        for i, doc in enumerate(self._docs):
            score = 0.6 - (i * 0.05)
            results.append(self._wrap(doc, "dense", score))
        return results

    def _sparse_retrieve(self, query: str, ctx: TemporalContext) -> List[RetrievalResult]:
        # Placeholder for BM25.
        results: List[RetrievalResult] = []
        for i, doc in enumerate(self._docs[::-1]):
            score = 0.5 - (i * 0.05)
            results.append(self._wrap(doc, "sparse", score))
        return results

    def _wrap(self, doc: dict, source: str, score: float) -> RetrievalResult:
        return RetrievalResult(
            doc_id=doc["id"],
            content=doc["content"],
            source=source,
            score=score,
            valid_from=doc["valid_from"],
            valid_to=doc["valid_to"],
        )

    def _temporal_rrf(
        self,
        results_lists: Iterable[List[RetrievalResult]],
        ctx: TemporalContext,
        k: int = 60,
    ) -> List[RetrievalResult]:
        scores: dict[str, float] = {}
        doc_map: dict[str, RetrievalResult] = {}

        for results in results_lists:
            for rank, result in enumerate(results):
                rrf = 1.0 / (k + rank + 1)
                temporal_boost = self._temporal_boost(result, ctx)
                source_weight = 1.2 if result.source == "graph" else 1.0
                final = rrf * temporal_boost * source_weight

                scores[result.doc_id] = scores.get(result.doc_id, 0.0) + final
                doc_map[result.doc_id] = result

        sorted_ids = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return [doc_map[doc_id] for doc_id, _ in sorted_ids]

    def _temporal_boost(self, result: RetrievalResult, ctx: TemporalContext) -> float:
        if result.valid_from is None:
            return 1.0
        ref = ctx.reference_time
        days = abs((ref - result.valid_from).days)
        return 0.5 + math.exp(-days / 365.0)

    def _synthesize(
        self, query: str, results: List[RetrievalResult], ctx: TemporalContext
    ) -> str:
        if not results:
            return "No relevant temporal facts found."

        lines = [
            f"Query: {query}",
            f"Temporal bounds: {ctx.time_start} -> {ctx.time_end}",
        ]
        for res in results[:3]:
            lines.append(
                f"- {res.content} (source={res.source}, valid={res.valid_from}..{res.valid_to})"
            )
        return "\n".join(lines)
