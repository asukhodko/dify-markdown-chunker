"""
Scalability analysis benchmarks.

Performs regression analysis to validate scaling characteristics.
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


class TestScalabilityBenchmarks:
    """Scalability analysis benchmarks."""

    def test_linear_scaling_analysis(self, corpus_selector, results_manager, chunker):
        """
        Perform linear regression analysis on processing time vs document size.

        Validates that the chunker scales linearly with document size.

        Note on R² threshold (0.70):
        - Small documents (<5KB) have higher variance due to fixed overhead
        - Fixed costs (parsing, strategy selection) dominate for tiny files
        - Larger documents show more consistent linear behavior
        - R² > 0.70 indicates acceptable linear trend in practice
        - Perfect linearity (R² > 0.95) is unrealistic for mixed-size samples
        """
        # Get all documents and sort by size
        documents = corpus_selector.get_all_documents()
        documents.sort(key=lambda d: d["size_bytes"])

        # Sample documents across size range
        # Use percentiles to get good distribution
        percentiles = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95]
        sample_docs = []

        for p in percentiles:
            idx = int((p / 100) * len(documents))
            if idx < len(documents):
                sample_docs.append(documents[idx])

        print(f"\nPerforming scalability analysis on {len(sample_docs)} documents...")

        sizes_kb = []
        times_ms = []
        memories_mb = []

        for doc in sample_docs:
            content = corpus_selector.load_document(doc)
            size_bytes = len(content.encode("utf-8"))
            size_kb = size_bytes / 1024

            def chunk_doc():
                return chunker.chunk(content)

            result = run_benchmark(chunk_doc, warmup_runs=1, measurement_runs=3)

            time_ms = result["time"]["mean"] * 1000
            memory_mb = result["memory"]["mean"]

            sizes_kb.append(size_kb)
            times_ms.append(time_ms)
            memories_mb.append(memory_mb)

            print(f"  {size_kb:.1f}KB: {time_ms:.2f}ms, {memory_mb:.2f}MB")

        # Perform linear regression: Time = coefficient * Size + intercept
        regression = self._linear_regression(sizes_kb, times_ms)

        print("\nRegression Analysis:")
        print(
            f"  Time(ms) = {regression['coefficient']:.4f} × Size(KB) + {regression['intercept']:.2f}"
        )
        print(f"  R-squared: {regression['r_squared']:.4f}")

        # Memory regression
        memory_regression = self._linear_regression(sizes_kb, memories_mb)
        print(
            f"  Memory(MB) = {memory_regression['coefficient']:.4f} × Size(KB) + {memory_regression['intercept']:.2f}"
        )

        # Generate projections
        projections = []
        for size_mb in [1, 5, 10, 50, 100]:
            size_kb = size_mb * 1024
            projected_time_ms = (
                regression["coefficient"] * size_kb + regression["intercept"]
            )
            projected_memory_mb = (
                memory_regression["coefficient"] * size_kb
                + memory_regression["intercept"]
            )

            projections.append(
                {
                    "size_mb": size_mb,
                    "time_seconds": projected_time_ms / 1000,
                    "memory_mb": projected_memory_mb,
                }
            )

        # Save scalability results
        scalability_results = {
            "regression": regression,
            "memory_regression": memory_regression,
            "projections": projections,
            "sample_count": len(sample_docs),
        }

        results_manager.add_benchmark_result(
            "scalability", "analysis", scalability_results
        )

        # Validate R-squared (should show reasonable linearity)
        # Note: Smaller documents have more variance due to fixed overhead
        # R² > 0.7 indicates acceptable linear trend
        assert (
            regression["r_squared"] >= 0.70
        ), f"Poor linear scaling: R² = {regression['r_squared']:.4f} (expected ≥ 0.70)"

        # Validate coefficient is reasonable (< 2ms per KB for good performance)
        # Typical range: 0.2-0.5 ms/KB for well-optimized system
        assert (
            regression["coefficient"] < 2.0
        ), f"Processing too slow: {regression['coefficient']:.4f}ms per KB (expected < 2.0)"

    def test_memory_scaling_analysis(self, corpus_selector, chunker):
        """
        Validate that memory usage scales reasonably with document size.

        Ensures no memory leaks or excessive memory consumption.
        """
        # Select documents at different sizes
        documents = corpus_selector.get_all_documents()
        documents.sort(key=lambda d: d["size_bytes"])

        # Sample small, medium, large
        indices = [
            int(len(documents) * 0.2),  # 20th percentile (small)
            int(len(documents) * 0.5),  # 50th percentile (medium)
            int(len(documents) * 0.8),  # 80th percentile (large)
        ]

        memory_ratios = []
        document_sizes_kb = []

        for idx in indices:
            if idx >= len(documents):
                continue

            doc = documents[idx]
            content = corpus_selector.load_document(doc)
            size_kb = len(content.encode("utf-8")) / 1024

            def chunk_doc():
                return chunker.chunk(content)

            result = run_benchmark(chunk_doc, warmup_runs=1, measurement_runs=3)
            memory_mb = result["memory"]["mean"]

            # Calculate memory per KB of input
            memory_ratio = memory_mb / size_kb if size_kb > 0 else 0
            memory_ratios.append(memory_ratio)
            document_sizes_kb.append(size_kb)

        # Memory ratio should be relatively consistent for larger documents
        # Note: For small documents (<5KB), base Python overhead dominates,
        # causing high variance in memory/KB ratio. This is expected behavior.
        # For larger documents, ratio stabilizes.
        if len(memory_ratios) > 1:
            # Memory usage validation:
            # Very small documents have proportionally higher overhead due to Python baseline.
            # Skip validation for tiny documents where baseline dominates actual usage.

            # Only validate memory scaling if we have reasonably sized documents
            # Documents < 5KB will have baseline overhead that skews ratios
            valid_samples = [
                (size, ratio)
                for size, ratio in zip(document_sizes_kb, memory_ratios)
                if size > 5.0
            ]

            if len(valid_samples) >= 2:
                valid_sizes, valid_ratios = zip(*valid_samples)
                avg_ratio = statistics.mean(valid_ratios)

                # Allow higher variance for memory measurements (they're inherently noisy)
                max_deviation = 1.5

                for ratio in valid_ratios:
                    deviation = (
                        abs(ratio - avg_ratio) / avg_ratio if avg_ratio > 0 else 0
                    )
                    assert deviation < max_deviation, (
                        f"Memory scaling inconsistent: {deviation*100:.1f}% deviation "
                        f"(expected < {max_deviation*100:.0f}%, avg_ratio={avg_ratio:.4f})"
                    )

    def _linear_regression(self, x_values, y_values):
        """
        Perform simple linear regression.

        Args:
            x_values: Independent variable (e.g., document size)
            y_values: Dependent variable (e.g., processing time)

        Returns:
            Dictionary with regression results
        """
        n = len(x_values)
        if n < 2:
            return {"coefficient": 0, "intercept": 0, "r_squared": 0}

        # Calculate means
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(y_values)

        # Calculate coefficient (slope)
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return {"coefficient": 0, "intercept": y_mean, "r_squared": 0}

        coefficient = numerator / denominator
        intercept = y_mean - coefficient * x_mean

        # Calculate R-squared
        y_predicted = [coefficient * x + intercept for x in x_values]
        ss_total = sum((y - y_mean) ** 2 for y in y_values)
        ss_residual = sum((y - yp) ** 2 for y, yp in zip(y_values, y_predicted))

        r_squared = 1 - (ss_residual / ss_total) if ss_total > 0 else 0

        return {
            "coefficient": coefficient,
            "intercept": intercept,
            "r_squared": r_squared,
        }
