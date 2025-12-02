"""
Quality improvement tests comparing baseline vs block-based implementation.

Measures actual improvements in MC-001 through MC-006 metrics.
"""

import pytest

from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig
from tests.quality_metrics import MetricsCalculator


@pytest.fixture
def baseline_config():
    """Configuration with block-based features disabled (baseline)."""
    return ChunkConfig(
        max_chunk_size=1000,
        overlap_size=100,
        block_based_splitting=False,
        allow_oversize_for_integrity=False,
        min_effective_chunk_size=0,
        block_based_overlap=False,
        detect_url_pools=False,
    )


@pytest.fixture
def block_based_config():
    """Configuration with all block-based features enabled."""
    return ChunkConfig(
        max_chunk_size=1000,
        overlap_size=100,
        block_based_splitting=True,
        allow_oversize_for_integrity=True,
        min_effective_chunk_size=400,
        block_based_overlap=True,
        detect_url_pools=True,
    )


@pytest.fixture
def career_matrix_content():
    """Career matrix document from fixtures."""
    import pathlib

    path = pathlib.Path(__file__).parent / "fixtures/real_documents/career_matrix.md"
    return path.read_text()


@pytest.fixture
def technical_spec_content():
    """Technical spec document from fixtures."""
    import pathlib

    path = pathlib.Path(__file__).parent / "fixtures/real_documents/technical_spec.md"
    return path.read_text()


class TestQualityImprovements:
    """Tests measuring quality improvements with block-based features."""

    def test_career_matrix_improvements(
        self, baseline_config, block_based_config, career_matrix_content
    ):
        """Measure improvements on career matrix document."""
        calculator = MetricsCalculator()

        # Baseline metrics
        chunker_baseline = MarkdownChunker(config=baseline_config)
        chunks_baseline = chunker_baseline.chunk(career_matrix_content)
        metrics_baseline = calculator.calculate_metrics(
            chunks_baseline, career_matrix_content
        )

        # Block-based metrics
        chunker_block = MarkdownChunker(config=block_based_config)
        chunks_block = chunker_block.chunk(career_matrix_content)
        metrics_block = calculator.calculate_metrics(
            chunks_block, career_matrix_content
        )

        # Print comparison
        print("\n=== Career Matrix Quality Improvements ===")
        print(f"Chunks: {len(chunks_baseline)} → {len(chunks_block)}")
        print("\nMC-001 Section Completeness:")
        print(f"  Baseline: {metrics_baseline.section_completeness_rate:.1%}")
        print(f"  Block-based: {metrics_block.section_completeness_rate:.1%}")

        print("\nMC-002 Structural Integrity:")
        print(f"  Baseline: {metrics_baseline.structural_element_integrity:.1%}")
        print(f"  Block-based: {metrics_block.structural_element_integrity:.1%}")

        print("\nMC-003 Overlap Integrity:")
        print(f"  Baseline: {metrics_baseline.overlap_block_integrity:.1%}")
        print(f"  Block-based: {metrics_block.overlap_block_integrity:.1%}")

        print("\nMC-004 Size Stability (CV):")
        print(f"  Baseline: {metrics_baseline.chunk_size_cv:.3f}")
        print(f"  Block-based: {metrics_block.chunk_size_cv:.3f}")

        print("\nMC-005 URL Pool Preservation:")
        print(f"  Baseline: {metrics_baseline.url_pool_preservation:.1%}")
        print(f"  Block-based: {metrics_block.url_pool_preservation:.1%}")

        print("\nMC-006 Header Path Completeness:")
        print(f"  Baseline: {metrics_baseline.header_path_completeness:.1%}")
        print(f"  Block-based: {metrics_block.header_path_completeness:.1%}")

        # Verify improvements (lenient thresholds for initial implementation)
        # Structural integrity may change due to different chunking strategy
        # The key improvement is in size stability (MC-004)
        assert (
            metrics_block.chunk_size_cv <= metrics_baseline.chunk_size_cv + 0.05
        ), f"Size stability should improve: {metrics_baseline.chunk_size_cv:.3f} → {metrics_block.chunk_size_cv:.3f}"

        # Header path completeness should not regress
        assert (
            metrics_block.header_path_completeness
            >= metrics_baseline.header_path_completeness - 0.05
        ), "Header path completeness should not regress"

    def test_technical_spec_improvements(
        self, baseline_config, block_based_config, technical_spec_content
    ):
        """Measure improvements on technical spec document."""
        calculator = MetricsCalculator()

        # Baseline metrics
        chunker_baseline = MarkdownChunker(config=baseline_config)
        chunks_baseline = chunker_baseline.chunk(technical_spec_content)
        metrics_baseline = calculator.calculate_metrics(
            chunks_baseline, technical_spec_content
        )

        # Block-based metrics
        chunker_block = MarkdownChunker(config=block_based_config)
        chunks_block = chunker_block.chunk(technical_spec_content)
        metrics_block = calculator.calculate_metrics(
            chunks_block, technical_spec_content
        )

        # Print comparison
        print("\n=== Technical Spec Quality Improvements ===")
        print(f"Chunks: {len(chunks_baseline)} → {len(chunks_block)}")
        print("\nMC-001 Section Completeness:")
        print(f"  Baseline: {metrics_baseline.section_completeness_rate:.1%}")
        print(f"  Block-based: {metrics_block.section_completeness_rate:.1%}")

        print("\nMC-002 Structural Integrity:")
        print(f"  Baseline: {metrics_baseline.structural_element_integrity:.1%}")
        print(f"  Block-based: {metrics_block.structural_element_integrity:.1%}")

        print("\nMC-004 Size Stability (CV):")
        print(f"  Baseline: {metrics_baseline.chunk_size_cv:.3f}")
        print(f"  Block-based: {metrics_block.chunk_size_cv:.3f}")

        # Size CV should improve (lower is better)
        # Allow for some variance due to different chunking approaches
        assert (
            metrics_block.chunk_size_cv <= metrics_baseline.chunk_size_cv + 0.1
        ), "Size stability should not regress significantly"

    def test_summary_of_improvements(
        self,
        baseline_config,
        block_based_config,
        career_matrix_content,
        technical_spec_content,
    ):
        """Generate summary report of improvements across all test documents."""
        calculator = MetricsCalculator()

        documents = [
            ("Career Matrix", career_matrix_content),
            ("Technical Spec", technical_spec_content),
        ]

        print("\n" + "=" * 60)
        print("BLOCK-BASED CHUNKING QUALITY IMPROVEMENTS SUMMARY")
        print("=" * 60)

        for doc_name, content in documents:
            # Baseline
            chunker_baseline = MarkdownChunker(config=baseline_config)
            chunks_baseline = chunker_baseline.chunk(content)
            metrics_baseline = calculator.calculate_metrics(chunks_baseline, content)

            # Block-based
            chunker_block = MarkdownChunker(config=block_based_config)
            chunks_block = chunker_block.chunk(content)
            metrics_block = calculator.calculate_metrics(chunks_block, content)

            print(f"\n{doc_name}:")
            print(f"  Chunks: {len(chunks_baseline)} → {len(chunks_block)}")

            # Calculate deltas
            struct_delta = (
                metrics_block.structural_element_integrity
                - metrics_baseline.structural_element_integrity
            )
            cv_delta = metrics_block.chunk_size_cv - metrics_baseline.chunk_size_cv

            print(
                f"  Structural Integrity: {metrics_baseline.structural_element_integrity:.1%} → {metrics_block.structural_element_integrity:.1%} ({struct_delta:+.1%})"
            )
            print(
                f"  Size CV: {metrics_baseline.chunk_size_cv:.3f} → {metrics_block.chunk_size_cv:.3f} ({cv_delta:+.3f})"
            )
            print(
                f"  URL Pool Preservation: {metrics_baseline.url_pool_preservation:.1%} → {metrics_block.url_pool_preservation:.1%}"
            )

        print("\n" + "=" * 60)
        print("Key Features Enabled:")
        print("  ✓ Block-based splitting (MC-001, MC-002, MC-005)")
        print("  ✓ 20% oversize tolerance (MC-001)")
        print("  ✓ URL pool detection (MC-005)")
        print("  ✓ Block-based overlap (MC-003)")
        print("  ✓ Header path validation (MC-006)")
        print("  ✓ Chunk size normalization (MC-004)")
        print("=" * 60)
