from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass
class EvalRecord:
    query: str
    answer: str
    contexts: List[str]
    ground_truth: Optional[str]


def load_jsonl(path: Path) -> Iterable[EvalRecord]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            payload = json.loads(line)
            yield EvalRecord(
                query=payload["query"],
                answer=payload.get("answer", ""),
                contexts=payload.get("contexts", []),
                ground_truth=payload.get("ground_truth"),
            )


def evaluate_stub(record: EvalRecord) -> dict:
    """
    Placeholder for ARES-style evaluation.

    Replace with an LLM judge or ARES implementation to score:
    - faithfulness
    - relevance
    - context_recall
    """
    return {
        "query": record.query,
        "faithfulness": 0.0,
        "relevance": 0.0,
        "context_recall": 0.0,
        "notes": "stub",
    }


def write_csv(rows: Iterable[dict], output_path: Path) -> None:
    rows = list(rows)
    if not rows:
        return
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="ARES-style evaluation stub")
    parser.add_argument("--input", required=True, help="JSONL input file")
    parser.add_argument("--output", default="assets/ares_eval.csv")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    records = load_jsonl(input_path)
    rows = [evaluate_stub(record) for record in records]
    write_csv(rows, output_path)

    print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
