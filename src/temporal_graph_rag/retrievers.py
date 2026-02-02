from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import time
from typing import Callable, Iterable, List, Optional, Protocol

from temporal_graph_rag.types import RetrievalResult, TemporalContext


class Retriever(Protocol):
    name: str

    def retrieve(self, query: str, ctx: TemporalContext) -> List[RetrievalResult]:
        ...


def _wrap(doc: dict, source: str, score: float) -> RetrievalResult:
    return RetrievalResult(
        doc_id=doc["id"],
        content=doc["content"],
        source=source,
        score=score,
        valid_from=doc["valid_from"],
        valid_to=doc["valid_to"],
    )


@dataclass
class InMemoryGraphRetriever:
    docs: List[dict]
    name: str = "graph"

    def retrieve(self, query: str, ctx: TemporalContext) -> List[RetrievalResult]:
        tokens = set(query.lower().split())
        results: List[RetrievalResult] = []
        for doc in self.docs:
            if tokens & set(doc["content"].lower().split()):
                results.append(_wrap(doc, self.name, 0.9))
        return results


@dataclass
class InMemoryDenseRetriever:
    docs: List[dict]
    name: str = "dense"

    def retrieve(self, query: str, ctx: TemporalContext) -> List[RetrievalResult]:
        results: List[RetrievalResult] = []
        for i, doc in enumerate(self.docs):
            score = 0.6 - (i * 0.05)
            results.append(_wrap(doc, self.name, score))
        return results


@dataclass
class BM25Retriever:
    docs: List[dict]
    name: str = "sparse"

    def __post_init__(self) -> None:
        from rank_bm25 import BM25Okapi
        self._tokenized = [doc["content"].lower().split() for doc in self.docs]
        self._bm25 = BM25Okapi(self._tokenized)

    def retrieve(self, query: str, ctx: TemporalContext) -> List[RetrievalResult]:
        tokens = query.lower().split()
        scores = self._bm25.get_scores(tokens)
        results: List[RetrievalResult] = []
        for doc, score in zip(self.docs, scores):
            results.append(_wrap(doc, self.name, float(score)))
        results.sort(key=lambda item: item.score, reverse=True)
        return results


@dataclass
class Neo4jGraphRetriever:
    uri: str
    user: str
    password: str
    database: Optional[str] = None
    name: str = "graph"
    limit: int = 50
    query_timeout_s: float = 5.0
    max_retries: int = 2
    retry_backoff_s: float = 0.2
    _driver: Optional[object] = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        from neo4j import GraphDatabase
        self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def retrieve(self, query: str, ctx: TemporalContext) -> List[RetrievalResult]:
        cypher = (
            "MATCH (d:Document) "
            "WHERE toLower(d.content) CONTAINS toLower($term) "
            "RETURN d.id AS id, d.content AS content, d.valid_from AS valid_from, "
            "d.valid_to AS valid_to "
            "LIMIT $limit"
        )
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                results: List[RetrievalResult] = []
                with self._driver.session(database=self.database) as session:
                    rows = session.run(
                        cypher,
                        term=query,
                        limit=self.limit,
                        timeout=self.query_timeout_s,
                    )
                    for row in rows:
                        valid_from = _parse_dt(row.get("valid_from"))
                        valid_to = _parse_dt(row.get("valid_to"))
                        results.append(
                            RetrievalResult(
                                doc_id=row["id"],
                                content=row["content"],
                                source=self.name,
                                score=0.9,
                                valid_from=valid_from,
                                valid_to=valid_to,
                            )
                        )
                return results
            except Exception as exc:  # pragma: no cover - network dependent
                last_exc = exc
                if attempt >= self.max_retries:
                    break
                time.sleep(self.retry_backoff_s * (attempt + 1))
        raise RuntimeError("Neo4j query failed after retries") from last_exc

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()


@dataclass
class QdrantDenseRetriever:
    url: str
    collection: str
    embedding_fn: Callable[[str], Iterable[float]]
    api_key: Optional[str] = None
    name: str = "dense"
    limit: int = 50
    timeout_s: float = 5.0
    max_retries: int = 2
    retry_backoff_s: float = 0.2
    _client: Optional[object] = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        from qdrant_client import QdrantClient
        self._client = QdrantClient(url=self.url, api_key=self.api_key, timeout=self.timeout_s)

    def retrieve(self, query: str, ctx: TemporalContext) -> List[RetrievalResult]:
        query_vector = list(self.embedding_fn(query))
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                hits = self._client.search(
                    collection_name=self.collection,
                    query_vector=query_vector,
                    limit=self.limit,
                )
                results: List[RetrievalResult] = []
                for hit in hits:
                    payload = hit.payload or {}
                    results.append(
                        RetrievalResult(
                            doc_id=str(hit.id),
                            content=str(payload.get("content", "")),
                            source=self.name,
                            score=float(hit.score),
                            valid_from=_parse_dt(payload.get("valid_from")),
                            valid_to=_parse_dt(payload.get("valid_to")),
                        )
                    )
                return results
            except Exception as exc:  # pragma: no cover - network dependent
                last_exc = exc
                if attempt >= self.max_retries:
                    break
                time.sleep(self.retry_backoff_s * (attempt + 1))
        raise RuntimeError("Qdrant search failed after retries") from last_exc


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text)
