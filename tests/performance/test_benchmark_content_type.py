"""
Content type performance benchmarks.

Tests processing performance across different document content types.
"""

import statistics
from pathlib import Path

import pytest

from markdown_chunker_v2 import MarkdownChunker

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


@pytest.fixture(scope="module")
def chunker():
    """Create chunker instance."""
    return MarkdownChunker()


class TestContentTypeBenchmarks:
    """Content type performance benchmarks."""

    @pytest.mark.slow
    def test_benchmark_by_content_type(self, corpus_selector, results_manager, chunker):
        """
        Benchmark processing performance across content types.

        Measures:
        - Processing time per content category
        - Strategy selection patterns
        - Chunk quality metrics
        """
        # Select documents by category (reduced for faster testing)
        content_selection = corpus_selector.select_by_category(samples_per_category=3)

        content_results = {}

        for content_type, documents in content_selection.items():
            if not documents:
                continue

            print(f"\nBenchmarking {content_type} content ({len(documents)} files)...")

            category_times = []
            category_memories = []
            category_strategies = []
            category_chunks = []
            category_chunk_sizes = []

            for doc in documents:
                content = corpus_selector.load_document(doc)
                _ = len(content.encode("utf-8"))

                # Run benchmark with strategy analysis
                def chunk_with_analysis():
                    chunks, strategy, analysis = chunker.chunk_with_analysis(content)
                    return {
                        "chunks": chunks,
                        "strategy": strategy,
                        "analysis": analysis,
                    }

                result = run_benchmark(
                    chunk_with_analysis, warmup_runs=1, measurement_runs=3
                )

                # Extract result details
                output = result["result"]
                chunks = output["chunks"]
                strategy = output["strategy"]

                category_times.append(result["time"]["mean"])
                category_memories.append(result["memory"]["mean"])
                category_strategies.append(strategy)
                category_chunks.append(len(chunks))

                if chunks:
                    avg_chunk_size = statistics.mean([len(c.content) for c in chunks])
                    category_chunk_sizes.append(avg_chunk_size)

            # Aggregate results
            # Determine dominant strategy
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
                    "stddev": (
                        statistics.stdev(category_times)
                        if len(category_times) > 1
                        else 0
                    ),
                },
                "memory": {
                    "mean": statistics.mean(category_memories),
                    "min": min(category_memories),
                    "max": max(category_memories),
                },
                "strategy": dominant_strategy,
                "strategy_distribution": strategy_counts,
                "output": {
                    "avg_chunk_count": statistics.mean(category_chunks),
                    "avg_chunk_size": (
                        statistics.mean(category_chunk_sizes)
                        if category_chunk_sizes
                        else 0
                    ),
                },
                "document_count": len(documents),
            }

            avg_time = content_results[content_type]["time"]["mean"] * 1000
            print(f"  Avg time: {avg_time:.2f}ms")
            print(f"  Dominant strategy: {dominant_strategy}")
            avg_chunks = content_results[content_type]["output"]["avg_chunk_count"]
            print(f"  Avg chunks: {avg_chunks:.1f}")

        # Save results
        for content_type, data in content_results.items():
            results_manager.add_benchmark_result("content_type", content_type, data)

    @pytest.mark.slow
    def test_strategy_selection_appropriateness(self, corpus_selector, chunker):
        """
        Validate that strategies are selected appropriately for content types.

        Expected patterns:
        - debug_logs should trigger code_aware
        - changelogs should trigger structural or fallback
        - technical_docs should often trigger code_aware or structural
        """
        # Test a few samples from specific categories
        categories_to_test = {
            "debug_logs": "code_aware",
            "technical_docs": ["code_aware", "structural"],
        }

        for category, expected_strategies in categories_to_test.items():
            selection = corpus_selector.select_by_category(
                categories=[category], samples_per_category=5
            )

            if category not in selection or not selection[category]:
                continue

            strategies_seen = []
            for doc in selection[category]:
                content = corpus_selector.load_document(doc)
                chunks, strategy, analysis = chunker.chunk_with_analysis(content)
                strategies_seen.append(strategy)

            # Validate expected strategies are used
            if isinstance(expected_strategies, str):
                expected_strategies = [expected_strategies]

            matches = sum(1 for s in strategies_seen if s in expected_strategies)
            match_rate = matches / len(strategies_seen) if strategies_seen else 0

            # At least 50% should match expected pattern
            assert match_rate >= 0.5, (
                f"Category {category} expected strategies {expected_strategies}, "
                f"but only {match_rate*100:.1f}% matched. Seen: {set(strategies_seen)}"
            )
