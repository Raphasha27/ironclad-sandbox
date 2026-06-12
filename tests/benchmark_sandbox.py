"""Run simple execution benchmarks for Ironclad Sandbox.

This script is intentionally runnable outside pytest:

    python tests/benchmark_sandbox.py
"""
from __future__ import annotations

import argparse
import sys
import timeit
import tracemalloc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sandbox.executor import MontySandbox


BENCHMARKS = {
    "arithmetic": "output = sum(range(100))",
    "collections": "output = sorted([5, 3, 8, 1, 9, 2])",
    "dict_summary": """
values = [10, 20, 30, 40, 50]
output = {"count": len(values), "average": sum(values) / len(values)}
""",
}


def run_benchmark(name: str, code: str, iterations: int) -> dict[str, float | int | str]:
    sandbox = MontySandbox()

    def execute_once() -> None:
        result = sandbox.execute(code)
        if not result.success:
            raise RuntimeError(f"{name} benchmark failed: {result.error}")

    tracemalloc.start()
    memory_before = tracemalloc.get_traced_memory()[0]
    total_seconds = timeit.timeit(execute_once, number=iterations)
    memory_after, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "name": name,
        "iterations": iterations,
        "total_ms": round(total_seconds * 1000, 3),
        "avg_ms": round((total_seconds / iterations) * 1000, 6),
        "memory_delta_bytes": memory_after - memory_before,
        "peak_memory_bytes": peak_memory,
    }


def format_markdown_table(results: list[dict[str, float | int | str]]) -> str:
    lines = [
        "| Benchmark | Iterations | Total ms | Avg ms/run | Memory delta bytes | Peak memory bytes |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in results:
        lines.append(
            "| {name} | {iterations} | {total_ms} | {avg_ms} | "
            "{memory_delta_bytes} | {peak_memory_bytes} |".format(**row)
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark repeated Ironclad Sandbox executions."
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=1000,
        help="Number of executions per benchmark case.",
    )
    args = parser.parse_args()

    if args.iterations < 1:
        parser.error("--iterations must be at least 1")

    results = [
        run_benchmark(name, code, args.iterations)
        for name, code in BENCHMARKS.items()
    ]
    print(format_markdown_table(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
