from datetime import datetime

from temporal_graph_rag.engine import TemporalGraphRAG


def dt(y, m, d):
    return datetime(y, m, d)


def test_parse_temporal_context_year():
    engine = TemporalGraphRAG()
    ctx = engine._parse_temporal_context("Who led Orion before 2024?", dt(2025, 1, 1))
    assert ctx.operators == ["BEFORE"]
    assert ctx.time_start == dt(2024, 1, 1)
    assert ctx.time_end == dt(2024, 12, 31)
    assert ctx.granularity == "year"


def test_parse_temporal_context_month_end():
    engine = TemporalGraphRAG()
    ctx = engine._parse_temporal_context("What changed during Feb 2024?", dt(2024, 3, 1))
    assert ctx.operators == ["DURING"]
    assert ctx.time_start == dt(2024, 2, 1)
    assert ctx.time_end == dt(2024, 2, 29)
    assert ctx.granularity == "month"
