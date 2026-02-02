from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional
import calendar
import re
import math

from temporal_graph_rag.retrievers import BM25Retriever, InMemoryDenseRetriever, InMemoryGraphRetriever, Retriever
from temporal_graph_rag.types import FusedRetrievalResult, QueryResponse, RetrievalResult, TemporalContext


class TemporalGraphRAG:
    """Minimal, runnable temporal RAG skeleton with hybrid fusion.

    Replace in-memory stores with Neo4j/Qdrant/Elasticsearch in production.
    """

    def __init__(
        self,
        docs: Optional[List[dict]] = None,
        retrievers: Optional[List[Retriever]] = None,
    ) -> None:
        self._docs = docs or [
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
        self._retrievers = retrievers or [
            InMemoryGraphRetriever(self._docs),
            InMemoryDenseRetriever(self._docs),
            BM25Retriever(self._docs),
        ]

    def query(self, query: str, reference_time: Optional[datetime] = None) -> QueryResponse:
        ref_time = reference_time or datetime.utcnow()
        ctx = self._parse_temporal_context(query, ref_time)

        results_lists = [retriever.retrieve(query, ctx) for retriever in self._retrievers]
        fused = self._temporal_rrf(results_lists, ctx)
        top = fused[:5]

        answer = self._synthesize(query, top, ctx)
        return QueryResponse(answer=answer, sources=top, temporal_context=ctx)

    def close(self) -> None:
        for retriever in self._retrievers:
            close = getattr(retriever, "close", None)
            if callable(close):
                close()

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

        month_match = re.search(
            r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+((19|20)\d{2})",
            lower,
        )
        if month_match:
            month_map = {
                "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
            }
            month = month_map[month_match.group(1)[:3]]
            year = int(month_match.group(2))
            month_end = calendar.monthrange(year, month)[1]
            time_start = datetime(year, month, 1)
            time_end = datetime(year, month, month_end)
            granularity = "month"

        return TemporalContext(
            reference_time=ref_time,
            operators=operators,
            time_start=time_start,
            time_end=time_end,
            granularity=granularity,
        )

    def _temporal_rrf(
        self,
        results_lists: Iterable[List[RetrievalResult]],
        ctx: TemporalContext,
        k: int = 60,
    ) -> List[FusedRetrievalResult]:
        scores: dict[str, float] = {}
        source_scores: dict[str, dict[str, float]] = {}
        doc_map: dict[str, RetrievalResult] = {}

        for results in results_lists:
            for rank, result in enumerate(results):
                rrf = 1.0 / (k + rank + 1)
                temporal_boost = self._temporal_boost(result, ctx)
                source_weight = 1.2 if result.source == "graph" else 1.0
                final = rrf * temporal_boost * source_weight

                scores[result.doc_id] = scores.get(result.doc_id, 0.0) + final
                if result.doc_id not in source_scores:
                    source_scores[result.doc_id] = {}
                source_scores[result.doc_id][result.source] = (
                    source_scores[result.doc_id].get(result.source, 0.0) + final
                )
                doc_map[result.doc_id] = result

        sorted_ids = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        fused_results: List[FusedRetrievalResult] = []
        for doc_id, fused_score in sorted_ids:
            base = doc_map[doc_id]
            per_source = source_scores.get(doc_id, {})
            fused_results.append(
                FusedRetrievalResult(
                    doc_id=base.doc_id,
                    content=base.content,
                    sources=sorted(per_source.keys()),
                    fused_score=fused_score,
                    source_scores=per_source,
                    valid_from=base.valid_from,
                    valid_to=base.valid_to,
                )
            )
        return fused_results

    def _temporal_boost(self, result: RetrievalResult, ctx: TemporalContext) -> float:
        """Soft filter: penalize out-of-window results without dropping them."""
        if result.valid_from is None:
            return 1.0
        ref = ctx.reference_time
        days = abs((ref - result.valid_from).days)
        recency_boost = 0.5 + math.exp(-days / 365.0)

        window_factor = 1.0
        if ctx.time_start and ctx.time_end:
            valid_to = result.valid_to or datetime.max
            overlaps = result.valid_from <= ctx.time_end and valid_to >= ctx.time_start
            window_factor = 1.2 if overlaps else 0.35

        return recency_boost * window_factor

    def _synthesize(
        self, query: str, results: List[FusedRetrievalResult], ctx: TemporalContext
    ) -> str:
        if not results:
            return "No relevant temporal facts found."

        lines = [
            f"Query: {query}",
            f"Temporal bounds: {ctx.time_start} -> {ctx.time_end}",
        ]
        for res in results[:3]:
            lines.append(
                f"- {res.content} (sources={','.join(res.sources)}, valid={res.valid_from}..{res.valid_to})"
            )
        return "\n".join(lines)
