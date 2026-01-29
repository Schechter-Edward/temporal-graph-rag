from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


AllenRelation = Literal[
    "before",
    "after",
    "meets",
    "overlaps",
    "during",
    "starts",
    "finishes",
    "equals",
]


@dataclass(frozen=True)
class Interval:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError("Interval end must be >= start")


def relate(a: Interval, b: Interval) -> AllenRelation:
    if a.start == b.start and a.end == b.end:
        return "equals"
    if a.end < b.start:
        return "before"
    if a.start > b.end:
        return "after"
    if a.end == b.start:
        return "meets"
    if a.start < b.start < a.end < b.end:
        return "overlaps"
    if b.start <= a.start and a.end <= b.end:
        if a.start == b.start:
            return "starts"
        if a.end == b.end:
            return "finishes"
        return "during"
    return "overlaps"
