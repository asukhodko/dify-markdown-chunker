#!/usr/bin/env python3
"""
Standalone benchmark runner (no pytest required).

Executes key performance benchmarks and generates report.
"""

import statistics
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from markdown_chunker_v2 import MarkdownChunker  # noqa: E402
from tests.performance.corpus_selector import CorpusSelector  # noqa: E402
from tests.performance.results_manager import ResultsManager  # noqa: E402
from tests.performance.utils import calculate_throughput, run_benchmark  # noqa: E402


def benchmark_by_size(corpus_selector, results_manager, chunker):
    """Run size-based benchmarks."""
    print("\n" + "=" * 70)
    print("SIZE-BASED BENCHMARKS")
    print("=" * 70)

    size_selection = corpus_selector.select_by_size()
    size_results = {}

    for size_category, documents in size_selection.items():
        if not documents:
            continue

        print(f"\n{size_category.upper()} documents ({len(documents)} files)...")

        category_times = []
        category_memories = []
        category_throughputs = []
        category_chunks = []
        category_sizes = []

        for doc in documents:
            content = corpus_selector.load_document(doc)
            size_bytes = len(content.encode("utf-8"))

            def chunk_doc():
                return chunker.chunk(content)

            result = run_benchmark(chunk_doc, warmup_runs=1, measurement_runs=3)
            throughput = calculate_throughput(size_bytes, result["time"]["mean"])

            chunks = result["result"]
            chunk_count = len(chunks)
            _ = statistics.mean([len(c.content) for c in chunks]) if chunks else 0

            category_times.append(result["time"]["mean"])
            category_memories.append(result["memory"]["mean"])
            category_throughputs.append(throughput["kb_per_sec"])
            category_chunks.append(chunk_count)
            category_sizes.append(size_bytes)

        size_results[size_category] = {
            "time": {
                "mean": statistics.mean(category_times),
                "min": min(category_times),
                "max": max(category_times),
                "stddev": (
                    statistics.stdev(category_times) if len(category_times) > 1 else 0
                ),
            },
            "memory": {
                "mean": statistics.mean(category_memories),
                "min": min(category_memories),
                "max": max(category_memories),
            },
            "throughput": {
                "kb_per_sec": statistics.mean(category_throughputs),
                "min": min(category_throughputs),
                "max": max(category_throughputs),
            },
            "output": {
                "avg_chunk_count": statistics.mean(category_chunks),
                "avg_size_bytes": statistics.mean(category_sizes),
            },
            "document_count": len(documents),
        }

        print(f"  ✓ Avg time: {size_results[size_category]['time']['mean']*1000:.2f}ms")
        print(
            f"  ✓ Throughput: {size_results[size_category]['throughput']['kb_per_sec']:.1f} KB/s"
        )
        print(f"  ✓ Memory: {size_results[size_category]['memory']['mean']:.2f} MB")

    for size_cat, data in size_results.items():
        results_manager.add_benchmark_result("size", size_cat, data)

    return size_results


def benchmark_by_content_type(corpus_selector, results_manager, chunker):
    """Run content-type benchmarks."""
    print("\n" + "=" * 70)
    print("CONTENT-TYPE BENCHMARKS")
    print("=" * 70)

    content_selection = corpus_selector.select_by_category(samples_per_category=8)
    content_results = {}

    for content_type, documents in content_selection.items():
        if not documents:
            continue

        print(f"\n{content_type.upper()} ({len(documents)} files)...")

        category_times = []
        category_strategies = []
        category_chunks = []

        for doc in documents:
            content = corpus_selector.load_document(doc)

            def chunk_with_analysis():
                chunks, strategy, analysis = chunker.chunk_with_analysis(content)
                return {"chunks": chunks, "strategy": strategy}

            result = run_benchmark(
                chunk_with_analysis, warmup_runs=1, measurement_runs=2
            )
            output = result["result"]

            category_times.append(result["time"]["mean"])
            category_strategies.append(output["strategy"])
            category_chunks.append(len(output["chunks"]))

        strategy_counts = {}
        for s in category_strategies:
            strategy_counts[s] = strategy_counts.get(s, 0) + 1
        dominant_strategy = (
            max(strategy_counts, key=strategy_counts.get)
            if strategy_counts
            else "unknown"
        )

        content_results[content_type] = {
            "time": {
                "mean": statistics.mean(category_times),
                "min": min(category_times),
                "max": max(category_times),
            },
            "strategy": dominant_strategy,
            "output": {
                "avg_chunk_count": statistics.mean(category_chunks),
            },
            "document_count": len(documents),
        }

        print(
            f"  ✓ Avg time: {content_results[content_type]['time']['mean']*1000:.2f}ms"
        )
        print(f"  ✓ Strategy: {dominant_strategy}")

    for content_type, data in content_results.items():
        results_manager.add_benchmark_result("content_type", content_type, data)

    return content_results


def benchmark_scalability(corpus_selector, results_manager, chunker):
    """Run scalability analysis."""
    print("\n" + "=" * 70)
    print("SCALABILITY ANALYSIS")
    print("=" * 70)

    documents = corpus_selector.get_all_documents()
    documents.sort(key=lambda d: d["size_bytes"])

    percentiles = [10, 30, 50, 70, 90]
    sample_docs = []

    for p in percentiles:
        idx = int((p / 100) * len(documents))
        if idx < len(documents):
            sample_docs.append(documents[idx])

    print(f"\nAnalyzing {len(sample_docs)} documents...")

    sizes_kb = []
    times_ms = []

    for doc in sample_docs:
        content = corpus_selector.load_document(doc)
        size_bytes = len(content.encode("utf-8"))
        size_kb = size_bytes / 1024

        def chunk_doc():
            return chunker.chunk(content)

        result = run_benchmark(chunk_doc, warmup_runs=1, measurement_runs=3)
        time_ms = result["time"]["mean"] * 1000

        sizes_kb.append(size_kb)
        times_ms.append(time_ms)

        print(f"  {size_kb:6.1f} KB -> {time_ms:6.2f} ms")

    # Linear regression
    x_mean = statistics.mean(sizes_kb)
    y_mean = statistics.mean(times_ms)

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(sizes_kb, times_ms))
    denominator = sum((x - x_mean) ** 2 for x in sizes_kb)

    coefficient = numerator / denominator if denominator > 0 else 0
    intercept = y_mean - coefficient * x_mean

    y_predicted = [coefficient * x + intercept for x in sizes_kb]
    ss_total = sum((y - y_mean) ** 2 for y in times_ms)
    ss_residual = sum((y - yp) ** 2 for y, yp in zip(times_ms, y_predicted))
    r_squared = 1 - (ss_residual / ss_total) if ss_total > 0 else 0

    print("\nRegression Model:")
    print(f"  Time(ms) = {coefficient:.4f} × Size(KB) + {intercept:.2f}")
    print(f"  R² = {r_squared:.4f}")

    regression = {
        "coefficient": coefficient,
        "intercept": intercept,
        "r_squared": r_squared,
    }

    results_manager.add_benchmark_result(
        "scalability", "analysis", {"regression": regression}
    )

    return regression


def main():
    """Run comprehensive benchmarks."""
    print("=" * 70)
    print("MARKDOWN CHUNKER V2 - PERFORMANCE BENCHMARKS")
    print("=" * 70)

    # Initialize components
    corpus_path = Path(__file__).parent.parent / "corpus"
    results_path = Path(__file__).parent / "results"

    corpus_selector = CorpusSelector(corpus_path)
    results_manager = ResultsManager(results_path)
    chunker = MarkdownChunker()

    # Run benchmarks
    try:
        size_results = benchmark_by_size(corpus_selector, results_manager, chunker)
        _ = benchmark_by_content_type(corpus_selector, results_manager, chunker)
        regression = benchmark_scalability(corpus_selector, results_manager, chunker)

        # Save results
        results_manager.save_latest_run()
        results_manager.save_report()
        results_manager.export_csv()

        print("\n" + "=" * 70)
        print("BENCHMARKS COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"\nResults saved to: {results_path}/")
        print("  - latest_run.json")
        print("  - performance_report.md")
        print("  - results_all.csv")

        # Summary
        print("\n" + "=" * 70)
        print("PERFORMANCE SUMMARY")
        print("=" * 70)

        print("\nSize-Based Performance:")
        for size_cat in ["tiny", "small", "medium", "large"]:
            if size_cat in size_results:
                data = size_results[size_cat]
                print(
                    f"  {size_cat.title():10s}: {data['time']['mean']*1000:6.2f}ms  "
                    f"{data['throughput']['kb_per_sec']:7.1f} KB/s  "
                    f"{data['memory']['mean']:5.2f} MB"
                )

        print(
            f"\nScaling: {regression['coefficient']:.4f} ms/KB  (R² = {regression['r_squared']:.4f})"
        )

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
