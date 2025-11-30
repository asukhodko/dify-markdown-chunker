"""
Benchmark the main chunking pipeline.

Measures performance across different document sizes and content types.

Usage:
    python -m benchmarks.benchmark_chunker
"""

import json
import sys
from datetime import datetime
from typing import Dict, List

from markdown_chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig

from .utils import (
    calculate_throughput,
    format_size,
    format_time,
    generate_markdown_document,
    measure_all,
)


def benchmark_by_size() -> List[Dict]:
    """
    Benchmark chunking performance by document size.

    Tests documents of various sizes: 1KB, 10KB, 50KB, 100KB, 500KB

    Returns:
        List of benchmark results
    """
    sizes=[
        (1, "small"),
        (10, "medium"),
        (50, "large"),
        (100, "very_large"),
        (500, "huge"),
    ]

    results=[]
    chunker=MarkdownChunker()

    print("\n" + "=" * 80)
    print("BENCHMARK: Document Size")
    print("=" * 80)
    print(f"{'Size':<15} {'Time':<15} {'Throughput':<20} {'Chunks':<10} {'Memory':<15}")
    print("-" * 80)

    for size_kb, label in sizes:
        # Generate test document
        content=generate_markdown_document(size_kb, "mixed")
        actual_size=len(content.encode('utf-8'))

        # Measure performance
        metrics=measure_all(chunker.chunk, content)
        chunks=metrics["result"]
        time_taken=metrics["time"]
        memory_mb=metrics["memory_mb"]

        # Calculate metrics
        throughput=calculate_throughput(actual_size, time_taken)

        # Store results
        result={
            "label": label,
            "size_kb": size_kb,
            "actual_size_bytes": actual_size,
            "time_seconds": time_taken,
            "throughput_kbps": throughput,
            "chunks_count": len(chunks),
            "memory_mb": memory_mb,
        }
        results.append(result)

        # Print results
        print(
            f"{label:<15} "
            f"{format_time(time_taken):<15} "
            f"{throughput:.2f} KB/s{'':<10} "
            f"{len(chunks):<10} "
            f"{memory_mb:.2f} MB"
        )

    print("=" * 80)
    return results


def benchmark_by_content_type() -> List[Dict]:
    """
    Benchmark chunking performance by content type.

    Tests different content types: text, code, mixed, list, table

    Returns:
        List of benchmark results
    """
    content_types=["text", "code", "mixed", "list", "table"]
    size_kb=50  # Use consistent size for comparison

    results=[]
    chunker=MarkdownChunker()

    print("\n" + "=" * 80)
    print("BENCHMARK: Content Type")
    print("=" * 80)
    print(f"{'Type':<15} {'Time':<15} {'Strategy':<20} {'Chunks':<10} {'Avg Size':<15}")
    print("-" * 80)

    for content_type in content_types:
        # Generate test document
        content=generate_markdown_document(size_kb, content_type)

        # Measure performance
        metrics=measure_all(chunker.chunk, content, include_analysis=True)
        result_obj=metrics["result"]
        time_taken=metrics["time"]

        # Extract metrics
        chunks=result_obj.chunks
        strategy=result_obj.strategy_used
        avg_size=sum(len(c.content) for c in chunks) / len(chunks) if chunks else 0

        # Store results
        result={
            "content_type": content_type,
            "time_seconds": time_taken,
            "strategy_used": strategy,
            "chunks_count": len(chunks),
            "avg_chunk_size": avg_size,
        }
        results.append(result)

        # Print results
        print(
            f"{content_type:<15} "
            f"{format_time(time_taken):<15} "
            f"{strategy:<20} "
            f"{len(chunks):<10} "
            f"{avg_size:.0f} chars"
        )

    print("=" * 80)
    return results


def save_results(results: Dict, filename: str="benchmark_results.json"):
    """
    Save benchmark results to JSON file.

    Args:
        results: Benchmark results dictionary
        filename: Output filename
    """
    results["timestamp"] = datetime.now().isoformat()
    results["version"] = "1.4.0"

    with open(filename, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {filename}")


def main():
    """Run all benchmarks."""
    print("\n" + "=" * 80)
    print("MARKDOWN CHUNKER BENCHMARKS")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Version: 1.4.0")

    # Run benchmarks
    size_results=benchmark_by_size()
    content_results=benchmark_by_content_type()

    # Combine results
    all_results={
        "by_size": size_results,
        "by_content_type": content_results,
    }

    # Save results
    save_results(all_results)

    print("\n" + "=" * 80)
    print("BENCHMARKS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
