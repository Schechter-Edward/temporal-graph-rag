from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from temporal_graph_rag import TemporalGraphRAG
from temporal_graph_rag.api.ui import UI_HTML

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = TemporalGraphRAG()
    app.state.engine = engine
    try:
        yield
    finally:
        engine.close()


app = FastAPI(title="Temporal Graph RAG", version="0.1.0", lifespan=lifespan)


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3)
    reference_time: datetime | None = None


class SourceItem(BaseModel):
    doc_id: str
    content: str
    sources: list[str]
    fused_score: float
    source_scores: dict[str, float]
    valid_from: datetime | None
    valid_to: datetime | None


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
    temporal_context: dict


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    return HTMLResponse(UI_HTML)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    engine = app.state.engine
    res = engine.query(req.query, req.reference_time)
    sources = [
        SourceItem(
            doc_id=s.doc_id,
            content=s.content,
            sources=s.sources,
            fused_score=s.fused_score,
            source_scores=s.source_scores,
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
