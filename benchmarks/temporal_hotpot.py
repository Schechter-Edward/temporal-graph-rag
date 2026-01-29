import argparse
import random
import time
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt

from temporal_graph_rag import TemporalGraphRAG


@dataclass
class QueryCase:
    text: str
    ref_time: datetime
    ground_truth: str


def synthetic_dataset(n: int = 50) -> list[QueryCase]:
    data: list[QueryCase] = []
    for _ in range(n):
        year = random.choice([2023, 2024])
        query = f"Who led Project Orion before the March {year} reorg?"
        data.append(QueryCase(query, datetime(year, 6, 1), "Alice"))
    return data


def evaluate_temporal_accuracy(answer: str, ground_truth: str) -> float:
    return 1.0 if ground_truth.lower() in answer.lower() else 0.0


def run_benchmark(n: int, visualize: bool) -> None:
    engine = TemporalGraphRAG()
    data = synthetic_dataset(n)

    latencies = []
    accuracies = []

    for case in data:
        start = time.time()
        res = engine.query(case.text, case.ref_time)
        latencies.append((time.time() - start) * 1000)
        accuracies.append(evaluate_temporal_accuracy(res.answer, case.ground_truth))

    mean_acc = float(np.mean(accuracies))
    p99 = float(np.percentile(latencies, 99))

    print("Temporal Graph RAG - Synthetic Benchmark")
    print("=" * 50)
    print(f"Samples: {n}")
    print(f"Accuracy: {mean_acc:.2%}")
    print(f"P99 Latency: {p99:.1f} ms")

    if visualize:
        plt.figure(figsize=(6, 4))
        plt.hist(latencies, bins=12, color="#4ecdc4")
        plt.title("Latency Distribution (ms)")
        plt.xlabel("Milliseconds")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig("assets/benchmark_results.png", dpi=150)
        print("Saved assets/benchmark_results.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=50)
    parser.add_argument("--visualize", action="store_true")
    args = parser.parse_args()

    run_benchmark(args.samples, args.visualize)
