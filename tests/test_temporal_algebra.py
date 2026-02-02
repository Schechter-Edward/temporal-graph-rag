from datetime import datetime
from temporal_graph_rag.temporal.algebra import Interval, relate


def dt(y, m, d):
    return datetime(y, m, d)


def test_before():
    a = Interval(dt(2024, 1, 1), dt(2024, 1, 2))
    b = Interval(dt(2024, 1, 3), dt(2024, 1, 4))
    assert relate(a, b) == "before"


def test_meets():
    a = Interval(dt(2024, 1, 1), dt(2024, 1, 2))
    b = Interval(dt(2024, 1, 2), dt(2024, 1, 3))
    assert relate(a, b) == "meets"


def test_met_by():
    a = Interval(dt(2024, 1, 2), dt(2024, 1, 3))
    b = Interval(dt(2024, 1, 1), dt(2024, 1, 2))
    assert relate(a, b) == "met_by"


def test_overlaps():
    a = Interval(dt(2024, 1, 1), dt(2024, 1, 5))
    b = Interval(dt(2024, 1, 4), dt(2024, 1, 10))
    assert relate(a, b) == "overlaps"


def test_during():
    a = Interval(dt(2024, 1, 2), dt(2024, 1, 3))
    b = Interval(dt(2024, 1, 1), dt(2024, 1, 5))
    assert relate(a, b) == "during"
