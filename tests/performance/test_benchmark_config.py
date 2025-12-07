"""
Configuration impact performance benchmarks.

Tests how different configurations affect processing performance.
"""

import statistics
from pathlib import Path

import pytest

from markdown_chunker_v2 import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig

from .corpus_selector import CorpusSelector
from .results_manager import ResultsManager
from .utils import run_benchmark


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


class TestConfigBenchmarks:
    """Configuration impact benchmarks."""

    def test_config_profiles_performance(self, corpus_selector, results_manager):
        """
        Benchmark different configuration profiles.

        Compares:
        - Default configuration
        - Code-heavy configuration
        - Structured configuration
        - Minimal configuration
        - No-overlap configuration
        """
        # Select representative documents
        documents = corpus_selector.get_all_documents()
        # Get medium-sized documents for consistent comparison
        medium_docs = [d for d in documents if 5000 <= d["size_bytes"] <= 20000]
        test_docs = medium_docs[:10] if len(medium_docs) >= 10 else medium_docs

        print(f"\nBenchmarking configuration profiles on {len(test_docs)} documents...")

        configs = {
            "default": ChunkConfig(),
            "code_heavy": ChunkConfig.for_code_heavy(),
            "structured": ChunkConfig.for_structured(),
            "minimal": ChunkConfig.minimal(),
            "no_overlap": ChunkConfig(overlap_size=0),
        }

        config_results = {}

        for config_name, config in configs.items():
            print(f"\n  Testing {config_name} config...")
            chunker = MarkdownChunker(config)

            times = []
            memories = []
            chunk_counts = []

            for doc in test_docs:
                content = corpus_selector.load_document(doc)

                def chunk_doc():
                    return chunker.chunk(content)

                result = run_benchmark(chunk_doc, warmup_runs=1, measurement_runs=3)

                times.append(result["time"]["mean"])
                memories.append(result["memory"]["mean"])
                chunk_counts.append(len(result["result"]))

            config_results[config_name] = {
                "time": {
                    "mean": statistics.mean(times),
                    "min": min(times),
                    "max": max(times),
                    "stddev": statistics.stdev(times) if len(times) > 1 else 0,
                },
                "memory": {
                    "mean": statistics.mean(memories),
                    "min": min(memories),
                    "max": max(memories),
                },
                "output": {
                    "avg_chunk_count": statistics.mean(chunk_counts),
                },
                "document_count": len(test_docs),
            }

            print(
                f"    Avg time: {config_results[config_name]['time']['mean']*1000:.2f}ms"
            )
            print(
                f"    Avg chunks: {config_results[config_name]['output']['avg_chunk_count']:.1f}"
            )

        # Save results
        for config_name, data in config_results.items():
            results_manager.add_benchmark_result("config", config_name, data)

        # Validate no-overlap is faster than with-overlap
        if "no_overlap" in config_results and "default" in config_results:
            no_overlap_time = config_results["no_overlap"]["time"]["mean"]
            default_time = config_results["default"]["time"]["mean"]

            # No-overlap should be at most equal or slightly faster
            # (overlap processing has some overhead)
            assert no_overlap_time <= default_time * 1.1, (
                f"No-overlap config unexpectedly slow: {no_overlap_time*1000:.2f}ms "
                f"vs default {default_time*1000:.2f}ms"
            )

    def test_overlap_size_impact(self, corpus_selector, results_manager):
        """
        Test impact of different overlap sizes on performance.

        Measures overhead from overlap processing.
        """
        # Select a few medium documents
        documents = corpus_selector.get_all_documents()
        medium_docs = [d for d in documents if 5000 <= d["size_bytes"] <= 15000]
        test_docs = medium_docs[:5] if len(medium_docs) >= 5 else medium_docs

        overlap_sizes = [0, 50, 100, 200, 400]
        overlap_results = {}

        print("\nTesting overlap size impact...")

        for overlap_size in overlap_sizes:
            config = ChunkConfig(overlap_size=overlap_size)
            chunker = MarkdownChunker(config)

            times = []

            for doc in test_docs:
                content = corpus_selector.load_document(doc)

                def chunk_doc():
                    return chunker.chunk(content)

                result = run_benchmark(chunk_doc, warmup_runs=1, measurement_runs=3)
                times.append(result["time"]["mean"])

            avg_time = statistics.mean(times)
            overlap_results[overlap_size] = avg_time

            print(f"  Overlap {overlap_size}: {avg_time*1000:.2f}ms")

        # Overlap should have minimal impact on performance
        # (since it's metadata-only in v2)
        baseline_time = overlap_results[0]
        for overlap_size, time in overlap_results.items():
            if overlap_size == 0:
                continue

            overhead = (
                (time - baseline_time) / baseline_time if baseline_time > 0 else 0
            )
            # Overhead should be less than 40%
            assert overhead < 0.40, (
                f"Overlap size {overlap_size} adds {overhead*100:.1f}% overhead "
                f"(expected < 40%)"
            )

    def test_chunk_size_impact(self, corpus_selector):
        """
        Test impact of different max_chunk_size settings.

        Validates that larger chunk sizes don't degrade performance.
        """
        # Select medium documents
        documents = corpus_selector.get_all_documents()
        medium_docs = [d for d in documents if 8000 <= d["size_bytes"] <= 15000]
        test_docs = medium_docs[:5] if len(medium_docs) >= 5 else medium_docs

        chunk_sizes = [1024, 2048, 4096, 8192]
        size_times = {}

        print("\nTesting chunk size impact...")

        for chunk_size in chunk_sizes:
            config = ChunkConfig(
                max_chunk_size=chunk_size, min_chunk_size=chunk_size // 4
            )
            chunker = MarkdownChunker(config)

            times = []

            for doc in test_docs:
                content = corpus_selector.load_document(doc)

                def chunk_doc():
                    return chunker.chunk(content)

                result = run_benchmark(chunk_doc, warmup_runs=1, measurement_runs=3)
                times.append(result["time"]["mean"])

            avg_time = statistics.mean(times)
            size_times[chunk_size] = avg_time

            print(f"  Chunk size {chunk_size}: {avg_time*1000:.2f}ms")

        # Performance should be relatively stable across chunk sizes
        times_list = list(size_times.values())
        if len(times_list) > 1:
            time_variance = statistics.stdev(times_list) / statistics.mean(times_list)
            # Coefficient of variation should be reasonable
            assert (
                time_variance < 0.5
            ), f"Chunk size impact too large: CV={time_variance:.2f}"
