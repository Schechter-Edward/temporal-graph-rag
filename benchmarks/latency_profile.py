from __future__ import annotations

import argparse
import calendar
import random
import time
from datetime import datetime
from typing import List

from temporal_graph_rag import TemporalGraphRAG


DEFAULT_QUERIES = [
    "Who led Project Orion before 2024?",
    "What happened during the March 2024 reorg?",
    "Who managed infrastructure after the reorg?",
    "What changed between 2023 and 2024?",
    "Was Alice leading Orion during February 2024?",
]


PEOPLE = ["Alice", "Bob", "Chloe", "Dev", "Ethan", "Fatima", "Grace", "Hiro"]
PROJECTS = ["Orion", "Helios", "Nova", "Atlas", "Aurora", "Zephyr"]


def _random_valid_window(year: int, start_month: int) -> tuple[datetime, datetime]:
    duration = random.randint(1, 6)
    end_month = min(12, start_month + duration)
    end_day = calendar.monthrange(year, end_month)[1]
    return datetime(year, start_month, 1), datetime(year, end_month, end_day)


def build_docs(count: int, seed: int) -> list[dict]:
    random.seed(seed)
    docs: list[dict] = []
    for i in range(count):
        person = random.choice(PEOPLE)
        project = random.choice(PROJECTS)
        year = random.choice([2022, 2023, 2024, 2025])
        start_month = random.randint(1, 12)
        valid_from, valid_to = _random_valid_window(year, start_month)
        docs.append(
            {
                "id": f"doc-{i}",
                "content": f"{person} led Project {project} from {valid_from:%Y-%m} to {valid_to:%Y-%m}.",
                "valid_from": valid_from,
                "valid_to": valid_to,
            }
        )
    return docs


def run_queries(engine: TemporalGraphRAG, queries: List[str], samples: int) -> List[float]:
    latencies_ns: List[int] = []
    for i in range(samples):
        query = queries[i % len(queries)]
        start = time.perf_counter_ns()
        engine.query(query)
        elapsed_ns = time.perf_counter_ns() - start
        latencies_ns.append(elapsed_ns)
    return latencies_ns


def summarize(latencies_ns: List[int]) -> dict:
    sorted_ns = sorted(latencies_ns)
    p50 = sorted_ns[int(0.50 * (len(sorted_ns) - 1))]
    p90 = sorted_ns[int(0.90 * (len(sorted_ns) - 1))]
    p99 = sorted_ns[int(0.99 * (len(sorted_ns) - 1))]
    return {
        "count": len(sorted_ns),
        "mean_ns": sum(sorted_ns) / len(sorted_ns),
        "p50_ns": p50,
        "p90_ns": p90,
        "p99_ns": p99,
        "min_ns": sorted_ns[0],
        "max_ns": sorted_ns[-1],
    }


def plot(latencies_ns: List[int], output_path: str) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print("matplotlib not available; skipping chart.")
        return
    plt.figure(figsize=(8, 4.5))
    plt.hist([value / 1e6 for value in latencies_ns], bins=20, color="#3A6EA5", edgecolor="black")
    plt.title("Temporal Graph RAG Latency Profile")
    plt.xlabel("Latency (ms)")
    plt.ylabel("Requests")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)


def main() -> None:
    parser = argparse.ArgumentParser(description="Latency profile for Temporal Graph RAG")
    parser.add_argument("--samples", type=int, default=200)
    parser.add_argument("--doc-count", type=int, default=500)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out", default="assets/latency_profile.png")
    args = parser.parse_args()

    docs = build_docs(args.doc_count, args.seed)
    engine = TemporalGraphRAG(docs=docs)
    latencies_ns = run_queries(engine, DEFAULT_QUERIES, args.samples)
    stats = summarize(latencies_ns)

    print("Latency summary:")
    print(f"  count: {stats['count']}")
    print(f"  mean: {stats['mean_ns'] / 1e6:.3f} ms ({stats['mean_ns'] / 1e3:.1f} µs)")
    print(f"  p50: {stats['p50_ns'] / 1e6:.3f} ms ({stats['p50_ns'] / 1e3:.1f} µs)")
    print(f"  p90: {stats['p90_ns'] / 1e6:.3f} ms ({stats['p90_ns'] / 1e3:.1f} µs)")
    print(f"  p99: {stats['p99_ns'] / 1e6:.3f} ms ({stats['p99_ns'] / 1e3:.1f} µs)")
    print(f"  min: {stats['min_ns'] / 1e6:.3f} ms ({stats['min_ns'] / 1e3:.1f} µs)")
    print(f"  max: {stats['max_ns'] / 1e6:.3f} ms ({stats['max_ns'] / 1e3:.1f} µs)")

    plot(latencies_ns, args.out)
    print(f"Chart saved to {args.out}")


if __name__ == "__main__":
    main()
