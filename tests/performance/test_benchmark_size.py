"""
Size-based performance benchmarks.

Tests processing performance across different document size categories.
"""

import statistics
from pathlib import Path

import pytest

from markdown_chunker_v2 import MarkdownChunker
from .corpus_selector import CorpusSelector
from .results_manager import ResultsManager
from .utils import calculate_throughput, run_benchmark


@pytest.fixture(scope="module")
def corpus_selector():
    """Create corpus selector."""
    corpus_path = Path(__file__).parent.parent / "corpus"
    return CorpusSelector(corpus_path)


@pytest.fixture(scope="module")
def results_manager():
    """Create results manager."""
    results_path = Path(__file__).parent / "results"
    return ResultsManager(results_path)


@pytest.fixture(scope="module")
def chunker():
    """Create chunker instance."""
    return MarkdownChunker()


class TestSizeBenchmarks:
    """Size-based performance benchmarks."""

    def test_benchmark_by_size(self, corpus_selector, results_manager, chunker):
        """
        Benchmark processing performance across size categories.

        Measures:
        - Processing time per size category
        - Throughput (KB/s)
        - Memory usage
        - Chunk statistics
        """
        # Select documents by size
        size_selection = corpus_selector.select_by_size()

        size_results = {}

        for size_category, documents in size_selection.items():
            if not documents:
                continue

            print(f"\nBenchmarking {size_category} documents ({len(documents)} files)...")

            category_times = []
            category_memories = []
            category_throughputs = []
            category_chunks = []
            category_sizes = []

            for doc in documents:
                content = corpus_selector.load_document(doc)
                size_bytes = len(content.encode('utf-8'))

                # Run benchmark
                def chunk_doc():
                    return chunker.chunk(content)

                result = run_benchmark(
                    chunk_doc,
                    warmup_runs=1,
                    measurement_runs=3
                )

                # Calculate throughput
                throughput = calculate_throughput(
                    size_bytes,
                    result["time"]["mean"]
                )

                # Collect output statistics
                chunks = result["result"]
                chunk_count = len(chunks)
                avg_chunk_size = statistics.mean([len(c.content) for c in chunks]) if chunks else 0

                category_times.append(result["time"]["mean"])
                category_memories.append(result["memory"]["mean"])
                category_throughputs.append(throughput["kb_per_sec"])
                category_chunks.append(chunk_count)
                category_sizes.append(size_bytes)

            # Aggregate results for this size category
            size_results[size_category] = {
                "time": {
                    "mean": statistics.mean(category_times),
                    "min": min(category_times),
                    "max": max(category_times),
                    "stddev": statistics.stdev(category_times) if len(category_times) > 1 else 0,
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

            print(f"  Avg time: {size_results[size_category]['time']['mean']*1000:.2f}ms")
            print(f"  Throughput: {size_results[size_category]['throughput']['kb_per_sec']:.1f} KB/s")

        # Save results
        for size_cat, data in size_results.items():
            results_manager.add_benchmark_result("size", size_cat, data)

        # Validate performance meets thresholds for medium documents
        if "medium" in size_results:
            medium_time_ms = size_results["medium"]["time"]["mean"] * 1000
            # For ~10KB documents, should process in reasonable time
            avg_size_kb = size_results["medium"]["output"]["avg_size_bytes"] / 1024
            # Threshold: ~10ms per KB or better
            expected_max_ms = avg_size_kb * 10
            assert medium_time_ms < expected_max_ms, \
                f"Medium document processing too slow: {medium_time_ms:.2f}ms " \
                f"(expected < {expected_max_ms:.2f}ms for {avg_size_kb:.1f}KB)"

    def test_throughput_scaling(self, corpus_selector, results_manager, chunker):
        """
        Test that throughput scales reasonably with document size.

        Validates that larger documents don't show severe performance degradation.
        """
        documents = corpus_selector.get_all_documents()
        # Sort by size
        documents.sort(key=lambda d: d["size_bytes"])

        # Sample documents at different sizes
        sample_indices = [
            int(len(documents) * 0.1),   # 10th percentile
            int(len(documents) * 0.3),   # 30th
            int(len(documents) * 0.5),   # 50th (median)
            int(len(documents) * 0.7),   # 70th
            int(len(documents) * 0.9),   # 90th
        ]

        throughputs = []
        sizes = []

        for idx in sample_indices:
            if idx >= len(documents):
                continue

            doc = documents[idx]
            content = corpus_selector.load_document(doc)
            size_bytes = len(content.encode('utf-8'))

            def chunk_doc():
                return chunker.chunk(content)

            result = run_benchmark(chunk_doc, warmup_runs=1, measurement_runs=3)
            throughput = calculate_throughput(size_bytes, result["time"]["mean"])

            throughputs.append(throughput["kb_per_sec"])
            sizes.append(size_bytes / 1024)

        # Throughput should remain relatively stable (not degrade severely)
        if len(throughputs) > 1:
            throughput_variance = statistics.stdev(throughputs) / statistics.mean(throughputs)
            # Coefficient of variation should be reasonable (< 1.0 for good scaling)
            assert throughput_variance < 1.0, \
                f"Throughput too inconsistent across sizes: CV={throughput_variance:.2f}"
