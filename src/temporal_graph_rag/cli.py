from __future__ import annotations

import argparse
import json
from datetime import datetime

from temporal_graph_rag import TemporalGraphRAG


def _parse_reference_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Temporal Graph RAG CLI")
    parser.add_argument("query", help="Natural language query")
    parser.add_argument(
        "--reference-time",
        help="ISO timestamp (e.g. 2024-06-01T00:00:00)",
        default=None,
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full JSON response",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of sources to show",
    )
    args = parser.parse_args()

    engine = TemporalGraphRAG()
    result = engine.query(args.query, reference_time=_parse_reference_time(args.reference_time))

    if args.json:
        payload = {
            "answer": result.answer,
            "sources": [
                {
                    "doc_id": s.doc_id,
                    "content": s.content,
                    "sources": s.sources,
                    "fused_score": s.fused_score,
                    "source_scores": s.source_scores,
                    "valid_from": s.valid_from.isoformat() if s.valid_from else None,
                    "valid_to": s.valid_to.isoformat() if s.valid_to else None,
                }
                for s in result.sources
            ],
            "temporal_context": {
                "reference_time": result.temporal_context.reference_time.isoformat(),
                "operators": result.temporal_context.operators,
                "time_start": result.temporal_context.time_start.isoformat()
                if result.temporal_context.time_start
                else None,
                "time_end": result.temporal_context.time_end.isoformat()
                if result.temporal_context.time_end
                else None,
                "granularity": result.temporal_context.granularity,
            },
        }
        print(json.dumps(payload, indent=2))
        return

    print("Answer:\n")
    print(result.answer)
    print("\nSources:")
    for source in result.sources[: args.limit]:
        print(
            f"- {source.content} | sources={','.join(source.sources)} "
            f"valid={source.valid_from}..{source.valid_to} fused_score={source.fused_score:.3f}"
        )


if __name__ == "__main__":
    main()
