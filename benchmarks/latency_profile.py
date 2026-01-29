from __future__ import annotations

import argparse
import statistics
import time
from typing import List

import matplotlib.pyplot as plt

from temporal_graph_rag import TemporalGraphRAG


DEFAULT_QUERIES = [
    "Who led Project Orion before 2024?",
    "What happened during the March 2024 reorg?",
    "Who managed infrastructure after the reorg?",
    "What changed between 2023 and 2024?",
    "Was Alice leading Orion during February 2024?",
]


def run_queries(engine: TemporalGraphRAG, queries: List[str], samples: int) -> List[float]:
    latencies_ms: List[float] = []
    for i in range(samples):
        query = queries[i % len(queries)]
        start = time.perf_counter()
        engine.query(query)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        latencies_ms.append(elapsed_ms)
    return latencies_ms


def summarize(latencies_ms: List[float]) -> dict:
    sorted_ms = sorted(latencies_ms)
    p50 = sorted_ms[int(0.50 * (len(sorted_ms) - 1))]
    p90 = sorted_ms[int(0.90 * (len(sorted_ms) - 1))]
    p99 = sorted_ms[int(0.99 * (len(sorted_ms) - 1))]
    return {
        "count": len(sorted_ms),
        "mean_ms": statistics.mean(sorted_ms),
        "p50_ms": p50,
        "p90_ms": p90,
        "p99_ms": p99,
        "min_ms": sorted_ms[0],
        "max_ms": sorted_ms[-1],
    }


def plot(latencies_ms: List[float], output_path: str) -> None:
    plt.figure(figsize=(8, 4.5))
    plt.hist(latencies_ms, bins=20, color="#3A6EA5", edgecolor="black")
    plt.title("Temporal Graph RAG Latency Profile")
    plt.xlabel("Latency (ms)")
    plt.ylabel("Requests")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)


def main() -> None:
    parser = argparse.ArgumentParser(description="Latency profile for Temporal Graph RAG")
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--out", default="assets/latency_profile.png")
    args = parser.parse_args()

    engine = TemporalGraphRAG()
    latencies_ms = run_queries(engine, DEFAULT_QUERIES, args.samples)
    stats = summarize(latencies_ms)

    print("Latency summary (ms):")
    for key in ["count", "mean_ms", "p50_ms", "p90_ms", "p99_ms", "min_ms", "max_ms"]:
        value = stats[key]
        if key == "count":
            print(f"  {key}: {value}")
        else:
            print(f"  {key}: {value:.2f}")

    plot(latencies_ms, args.out)
    print(f"Chart saved to {args.out}")


if __name__ == "__main__":
    main()
