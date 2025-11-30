"""
Benchmark individual chunking strategies.

Measures performance of each strategy independently.

Usage:
    python -m benchmarks.benchmark_strategies
"""

from datetime import datetime
from typing import Dict, List

from markdown_chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig

from .utils import format_time, generate_markdown_document, measure_all


def benchmark_strategies() -> List[Dict]:
    """
    Benchmark each strategy independently.

    Returns:
        List of benchmark results for each strategy
    """
    strategies=[
        ("code", "code"),
        ("structural", "text"),
        ("mixed", "mixed"),
        ("list", "list"),
        ("table", "table"),
        ("sentences", "text"),
    ]

    size_kb=50
    results=[]

    print("\n" + "=" * 80)
    print("BENCHMARK: Strategies")
    print("=" * 80)
    print(f"{'Strategy':<20} {'Time':<15} {'Chunks':<10} {'Avg Size':<15}")
    print("-" * 80)

    for strategy_name, content_type in strategies:
        # Generate appropriate content
        content=generate_markdown_document(size_kb, content_type)

        # Create chunker and force strategy
        chunker=MarkdownChunker()

        # Measure performance
        try:
            metrics=measure_all(chunker.chunk, content, strategy=strategy_name)
            chunks=metrics["result"]
            time_taken=metrics["time"]

            avg_size=sum(len(c.content) for c in chunks) / len(chunks) if chunks else 0

            result={
                "strategy": strategy_name,
                "time_seconds": time_taken,
                "chunks_count": len(chunks),
                "avg_chunk_size": avg_size,
            }
            results.append(result)

            print(
                f"{strategy_name:<20} "
                f"{format_time(time_taken):<15} "
                f"{len(chunks):<10} "
                f"{avg_size:.0f} chars"
            )
        except Exception as e:
            print(f"{strategy_name:<20} ERROR: {str(e)}")

    print("=" * 80)
    return results


def main():
    """Run strategy benchmarks."""
    print("\n" + "=" * 80)
    print("STRATEGY BENCHMARKS")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results=benchmark_strategies()

    print("\n" + "=" * 80)
    print("BENCHMARKS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
