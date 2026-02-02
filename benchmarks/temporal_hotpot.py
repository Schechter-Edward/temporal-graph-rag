import argparse
import calendar
import random
import time
from dataclasses import dataclass
from datetime import datetime

from temporal_graph_rag import TemporalGraphRAG


@dataclass
class QueryCase:
    text: str
    ref_time: datetime
    ground_truth: str


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


def synthetic_dataset(docs: list[dict], n: int = 50) -> list[QueryCase]:
    data: list[QueryCase] = []
    for _ in range(n):
        doc = random.choice(docs)
        person = doc["content"].split()[0]
        project = doc["content"].split()[3]
        month = doc["valid_from"].strftime("%B")
        year = doc["valid_from"].year
        query = f"Who led Project {project} during {month} {year}?"
        data.append(QueryCase(query, doc["valid_from"], person))
    return data


def evaluate_temporal_accuracy(answer: str, ground_truth: str) -> float:
    return 1.0 if ground_truth.lower() in answer.lower() else 0.0


def _percentile(sorted_values: list[int], percentile: float) -> float:
    idx = int(percentile * (len(sorted_values) - 1))
    return float(sorted_values[idx])


def run_benchmark(n: int, doc_count: int, seed: int, visualize: bool) -> None:
    docs = build_docs(doc_count, seed)
    data = synthetic_dataset(docs, n)
    engine = TemporalGraphRAG(docs=docs)

    latencies_ns: list[int] = []
    accuracies: list[float] = []

    for case in data:
        start = time.perf_counter_ns()
        res = engine.query(case.text, case.ref_time)
        latencies_ns.append(time.perf_counter_ns() - start)
        accuracies.append(evaluate_temporal_accuracy(res.answer, case.ground_truth))

    sorted_ns = sorted(latencies_ns)
    mean_ns = sum(sorted_ns) / len(sorted_ns)
    p50_ns = _percentile(sorted_ns, 0.50)
    p90_ns = _percentile(sorted_ns, 0.90)
    p99_ns = _percentile(sorted_ns, 0.99)

    mean_acc = sum(accuracies) / len(accuracies)

    print("Temporal Graph RAG - Synthetic Benchmark")
    print("=" * 50)
    print(f"Samples: {n}")
    print(f"Docs: {doc_count}")
    print(f"Accuracy: {mean_acc:.2%}")
    print(f"Latency mean: {mean_ns / 1e6:.3f} ms ({mean_ns / 1e3:.1f} µs)")
    print(f"P50: {p50_ns / 1e6:.3f} ms ({p50_ns / 1e3:.1f} µs)")
    print(f"P90: {p90_ns / 1e6:.3f} ms ({p90_ns / 1e3:.1f} µs)")
    print(f"P99: {p99_ns / 1e6:.3f} ms ({p99_ns / 1e3:.1f} µs)")

    if visualize:
        try:
            import matplotlib.pyplot as plt
        except Exception:
            print("matplotlib not available; skipping chart.")
            return
        plt.figure(figsize=(6, 4))
        plt.hist([value / 1e6 for value in latencies_ns], bins=18, color="#4ecdc4")
        plt.title("Latency Distribution (ms)")
        plt.xlabel("Milliseconds")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig("assets/benchmark_results.png", dpi=150)
        print("Saved assets/benchmark_results.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=200)
    parser.add_argument("--doc-count", type=int, default=500)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--visualize", action="store_true")
    args = parser.parse_args()

    run_benchmark(args.samples, args.doc_count, args.seed, args.visualize)
