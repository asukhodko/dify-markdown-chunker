"""
Strategy-specific performance benchmarks.

Tests individual strategy performance and overhead analysis.
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


class TestStrategyBenchmarks:
    """Strategy-specific performance benchmarks."""

    def test_code_aware_strategy_performance(self, corpus_selector, results_manager):
        """Benchmark CodeAware strategy on appropriate documents."""
        # Select code-heavy documents
        selection = corpus_selector.select_by_category(
            categories=["debug_logs", "technical_docs"],
            samples_per_category=10
        )

        all_docs = []
        for docs in selection.values():
            all_docs.extend(docs)

        # Force CodeAware strategy
        config = ChunkConfig(strategy_override="code_aware")
        chunker = MarkdownChunker(config)

        times = []
        memories = []
        chunk_counts = []

        print("\nBenchmarking code_aware strategy...")

        for doc in all_docs[:15]:  # Limit to 15 for speed
            content = corpus_selector.load_document(doc)

            def chunk_doc():
                return chunker.chunk(content)

            result = run_benchmark(chunk_doc, warmup_runs=1, measurement_runs=3)

            times.append(result["time"]["mean"])
            memories.append(result["memory"]["mean"])
            chunk_counts.append(len(result["result"]))

        strategy_results = {
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
            "document_count": len(all_docs[:15]),
        }

        print(f"  Avg time: {strategy_results['time']['mean']*1000:.2f}ms")
        print(f"  Documents tested: {strategy_results['document_count']}")

        results_manager.add_benchmark_result("strategy", "code_aware", strategy_results)

    def test_structural_strategy_performance(self, corpus_selector, results_manager):
        """Benchmark Structural strategy on appropriate documents."""
        # Select structured documents
        selection = corpus_selector.select_by_category(
            categories=["changelogs", "github_readmes"],
            samples_per_category=10
        )

        all_docs = []
        for docs in selection.values():
            all_docs.extend(docs)

        # Force Structural strategy
        config = ChunkConfig(strategy_override="structural")
        chunker = MarkdownChunker(config)

        times = []
        memories = []
        chunk_counts = []

        print("\nBenchmarking structural strategy...")

        for doc in all_docs[:15]:  # Limit to 15 for speed
            content = corpus_selector.load_document(doc)

            def chunk_doc():
                return chunker.chunk(content)

            result = run_benchmark(chunk_doc, warmup_runs=1, measurement_runs=3)

            times.append(result["time"]["mean"])
            memories.append(result["memory"]["mean"])
            chunk_counts.append(len(result["result"]))

        strategy_results = {
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
            "document_count": len(all_docs[:15]),
        }

        print(f"  Avg time: {strategy_results['time']['mean']*1000:.2f}ms")
        print(f"  Documents tested: {strategy_results['document_count']}")

        results_manager.add_benchmark_result("strategy", "structural", strategy_results)

    def test_fallback_strategy_performance(self, corpus_selector, results_manager):
        """Benchmark Fallback strategy on simple documents."""
        # Select simple documents
        selection = corpus_selector.select_by_category(
            categories=["personal_notes"],
            samples_per_category=10
        )

        all_docs = []
        for docs in selection.values():
            all_docs.extend(docs)

        # Force Fallback strategy
        config = ChunkConfig(strategy_override="fallback")
        chunker = MarkdownChunker(config)

        times = []
        memories = []
        chunk_counts = []

        print("\nBenchmarking fallback strategy...")

        for doc in all_docs[:10]:  # Limit to 10 for speed
            content = corpus_selector.load_document(doc)

            def chunk_doc():
                return chunker.chunk(content)

            result = run_benchmark(chunk_doc, warmup_runs=1, measurement_runs=3)

            times.append(result["time"]["mean"])
            memories.append(result["memory"]["mean"])
            chunk_counts.append(len(result["result"]))

        strategy_results = {
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
            "document_count": len(all_docs[:10]),
        }

        print(f"  Avg time: {strategy_results['time']['mean']*1000:.2f}ms")
        print(f"  Documents tested: {strategy_results['document_count']}")

        results_manager.add_benchmark_result("strategy", "fallback", strategy_results)

    def test_strategy_comparison(self, corpus_selector):
        """
        Compare strategies on the same document to measure overhead differences.

        Tests that different strategies have reasonable performance characteristics.
        """
        # Pick a medium-sized mixed content document
        selection = corpus_selector.select_by_category(
            categories=["mixed_content"],
            samples_per_category=3
        )

        if not selection.get("mixed_content"):
            pytest.skip("No mixed_content documents available")

        doc = selection["mixed_content"][0]
        content = corpus_selector.load_document(doc)

        strategies = ["code_aware", "structural", "fallback"]
        strategy_times = {}

        for strategy_name in strategies:
            config = ChunkConfig(strategy_override=strategy_name)
            chunker = MarkdownChunker(config)

            def chunk_doc():
                return chunker.chunk(content)

            result = run_benchmark(chunk_doc, warmup_runs=1, measurement_runs=5)
            strategy_times[strategy_name] = result["time"]["mean"]

        # All strategies should complete in reasonable time
        # No strategy should be more than 3x slower than the fastest
        min_time = min(strategy_times.values())
        max_time = max(strategy_times.values())

        ratio = max_time / min_time if min_time > 0 else 1.0

        assert ratio < 3.0, \
            f"Strategy performance too variable: {ratio:.2f}x difference. " \
            f"Times: {strategy_times}"
