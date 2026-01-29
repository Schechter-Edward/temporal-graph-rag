from __future__ import annotations

import argparse
from datetime import datetime

from temporal_graph_rag import TemporalGraphRAG


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI demo for Temporal Graph RAG")
    parser.add_argument("query", help="Natural language query")
    parser.add_argument(
        "--reference-time",
        help="ISO timestamp (e.g. 2024-06-01T00:00:00)",
        default=None,
    )
    args = parser.parse_args()

    reference_time = None
    if args.reference_time:
        reference_time = datetime.fromisoformat(args.reference_time)

    engine = TemporalGraphRAG()
    result = engine.query(args.query, reference_time=reference_time)

    print("Answer:\n")
    print(result.answer)
    print("\nSources:")
    for source in result.sources:
        print(
            f"- {source.content} | source={source.source} "
            f"valid={source.valid_from}..{source.valid_to} score={source.score:.3f}"
        )


if __name__ == "__main__":
    main()
