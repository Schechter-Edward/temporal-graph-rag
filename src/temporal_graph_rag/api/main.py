from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel, Field

from temporal_graph_rag import TemporalGraphRAG

app = FastAPI(title="Temporal Graph RAG", version="0.1.0")
engine = TemporalGraphRAG()


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3)
    reference_time: datetime | None = None


class SourceItem(BaseModel):
    doc_id: str
    content: str
    source: str
    score: float
    valid_from: datetime | None
    valid_to: datetime | None


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
    temporal_context: dict


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    res = engine.query(req.query, req.reference_time)
    sources = [
        SourceItem(
            doc_id=s.doc_id,
            content=s.content,
            source=s.source,
            score=s.score,
            valid_from=s.valid_from,
            valid_to=s.valid_to,
        )
        for s in res.sources
    ]
    return QueryResponse(
        answer=res.answer,
        sources=sources,
        temporal_context={
            "reference_time": res.temporal_context.reference_time,
            "operators": res.temporal_context.operators,
            "time_start": res.temporal_context.time_start,
            "time_end": res.temporal_context.time_end,
            "granularity": res.temporal_context.granularity,
        },
    )
