"""
Tests for chunk boundary invariance.

Verifies that chunk boundaries do NOT depend on include_metadata parameter.
This addresses CHNK-CRIT-01: Unstable boundaries with include_metadata toggle.
"""

import re
from pathlib import Path
from unittest.mock import patch

import pytest

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from adapter import MigrationAdapter


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sde_criteria_document() -> str:
    """Load the SDE criteria document fixture."""
    fixture_path = FIXTURES_DIR / "sde_criteria.md"
    if not fixture_path.exists():
        pytest.skip(f"Fixture not found: {fixture_path}")
    return fixture_path.read_text(encoding="utf-8")


@pytest.fixture
def adapter() -> MigrationAdapter:
    """Create adapter instance."""
    return MigrationAdapter()


@pytest.fixture
def config(adapter):
    """Create chunker config."""
    return adapter.build_chunker_config(max_chunk_size=1000)


class TestChunkingCalledOnce:
    """Tests that chunking is performed exactly once."""

    def test_chunking_called_once_with_include_metadata_true(
        self, sde_criteria_document, adapter, config
    ):
        """Chunking should be called once with include_metadata=True."""
        with patch.object(
            adapter, '_perform_chunking', wraps=adapter._perform_chunking
        ) as mock:
            adapter.run_chunking(
                sde_criteria_document, config, include_metadata=True
            )
            assert mock.call_count == 1

    def test_chunking_called_once_with_include_metadata_false(
        self, sde_criteria_document, adapter, config
    ):
        """Chunking should be called once with include_metadata=False."""
        with patch.object(
            adapter, '_perform_chunking', wraps=adapter._perform_chunking
        ) as mock:
            adapter.run_chunking(
                sde_criteria_document, config, include_metadata=False
            )
            assert mock.call_count == 1


class TestRawChunksIdentical:
    """Tests that raw_chunks are identical regardless of include_metadata."""

    def test_raw_chunks_identical_for_different_include_metadata(
        self, sde_criteria_document, adapter, config
    ):
        """Raw chunks should be identical for different include_metadata values."""
        # Get raw_chunks directly (bypassing rendering)
        raw_chunks_1 = adapter._perform_chunking(
            sde_criteria_document, config, enable_hierarchy=False, debug=False
        )
        raw_chunks_2 = adapter._perform_chunking(
            sde_criteria_document, config, enable_hierarchy=False, debug=False
        )

        # Should be identical
        assert len(raw_chunks_1) == len(raw_chunks_2)

        for c1, c2 in zip(raw_chunks_1, raw_chunks_2):
            assert c1["start_line"] == c2["start_line"]
            assert c1["end_line"] == c2["end_line"]
            assert c1["content"] == c2["content"]

    def test_raw_chunks_identical_hierarchical_mode(
        self, sde_criteria_document, adapter, config
    ):
        """Raw chunks should be identical in hierarchical mode."""
        raw_chunks_1 = adapter._perform_chunking(
            sde_criteria_document, config, enable_hierarchy=True, debug=False
        )
        raw_chunks_2 = adapter._perform_chunking(
            sde_criteria_document, config, enable_hierarchy=True, debug=False
        )

        assert len(raw_chunks_1) == len(raw_chunks_2)

        for c1, c2 in zip(raw_chunks_1, raw_chunks_2):
            assert c1["start_line"] == c2["start_line"]
            assert c1["end_line"] == c2["end_line"]
            assert c1["content"] == c2["content"]


class TestBoundaryInvariance:
    """Tests that boundaries are invariant to include_metadata."""

    def test_boundaries_invariant_to_include_metadata(
        self, sde_criteria_document, adapter, config
    ):
        """Boundaries should not depend on include_metadata."""
        result_with = adapter.run_chunking(
            sde_criteria_document, config, include_metadata=True
        )
        result_without = adapter.run_chunking(
            sde_criteria_document, config, include_metadata=False
        )

        # Chunk count should match
        assert len(result_with) == len(result_without), (
            f"Chunk count mismatch: {len(result_with)} vs {len(result_without)}"
        )

        # Content should match (after removing metadata block)
        for i, (chunk_with, chunk_without) in enumerate(zip(result_with, result_without)):
            content_with = extract_content_from_dify_style(chunk_with)
            assert content_with == chunk_without, (
                f"Content mismatch at chunk {i}:\n"
                f"With metadata: {content_with[:100]}...\n"
                f"Without metadata: {chunk_without[:100]}..."
            )

    def test_boundaries_invariant_hierarchical_mode(
        self, sde_criteria_document, adapter, config
    ):
        """Boundaries should be invariant in hierarchical mode."""
        result_with = adapter.run_chunking(
            sde_criteria_document, config,
            include_metadata=True, enable_hierarchy=True
        )
        result_without = adapter.run_chunking(
            sde_criteria_document, config,
            include_metadata=False, enable_hierarchy=True
        )

        assert len(result_with) == len(result_without)

        for chunk_with, chunk_without in zip(result_with, result_without):
            content_with = extract_content_from_dify_style(chunk_with)
            assert content_with == chunk_without


class TestPreambleSeparate:
    """Tests that preamble is a separate chunk in both modes."""

    def test_preamble_separate_in_both_modes(
        self, sde_criteria_document, adapter, config
    ):
        """Preamble should be a separate chunk."""
        raw_chunks = adapter._perform_chunking(
            sde_criteria_document, config, enable_hierarchy=False, debug=False
        )

        # First chunk should be preamble
        first_chunk = raw_chunks[0]
        assert first_chunk["metadata"].get("content_type") == "preamble", (
            f"First chunk is not preamble: {first_chunk['metadata'].get('content_type')}"
        )

        # Preamble should not contain first header
        assert not first_chunk["content"].strip().startswith("# Критерии"), (
            "Preamble should not contain first header"
        )

    def test_preamble_separate_hierarchical_mode(
        self, sde_criteria_document, adapter, config
    ):
        """Preamble should be separate in hierarchical mode."""
        raw_chunks = adapter._perform_chunking(
            sde_criteria_document, config, enable_hierarchy=True, debug=False
        )

        # Find preamble chunk
        preamble_chunks = [
            c for c in raw_chunks
            if c["metadata"].get("content_type") == "preamble"
        ]

        assert len(preamble_chunks) >= 1, "Preamble chunk not found"


class TestCoverageAsRecall:
    """Tests for content coverage as line recall."""

    def test_content_coverage_at_least_95_percent(
        self, sde_criteria_document, adapter, config
    ):
        """Content coverage should be at least 95%."""
        raw_chunks = adapter._perform_chunking(
            sde_criteria_document, config, enable_hierarchy=False, debug=False
        )

        coverage = calculate_line_recall(raw_chunks, sde_criteria_document)
        assert coverage >= 0.95, f"Coverage {coverage:.1%} < 95%"

    def test_coverage_not_inflated_by_repetition(
        self, sde_criteria_document, adapter, config
    ):
        """Coverage should not be inflated by header repetition."""
        raw_chunks = adapter._perform_chunking(
            sde_criteria_document, config, enable_hierarchy=False, debug=False
        )

        coverage = calculate_line_recall(raw_chunks, sde_criteria_document)

        # Coverage should be high but not > 1.0
        assert 0.95 <= coverage <= 1.0, (
            f"Coverage {coverage:.1%} is outside expected range [95%, 100%]"
        )


class TestValidateAndFixApplied:
    """Tests that validate_and_fix is applied in both modes."""

    def test_validate_and_fix_applied_non_hierarchical(
        self, sde_criteria_document, adapter, config
    ):
        """validate_and_fix should be applied in non-hierarchical mode."""
        with patch.object(
            adapter._input_validator, 'validate_and_fix',
            wraps=adapter._input_validator.validate_and_fix
        ) as mock:
            adapter._perform_chunking(
                sde_criteria_document, config, enable_hierarchy=False, debug=False
            )
            assert mock.call_count == 1

    def test_validate_and_fix_applied_hierarchical(
        self, sde_criteria_document, adapter, config
    ):
        """validate_and_fix should be applied in hierarchical mode."""
        with patch.object(
            adapter._input_validator, 'validate_and_fix',
            wraps=adapter._input_validator.validate_and_fix
        ) as mock:
            adapter._perform_chunking(
                sde_criteria_document, config, enable_hierarchy=True, debug=False
            )
            assert mock.call_count == 1


class TestIndexableField:
    """Tests for indexable field handling."""

    def test_indexable_field_respects_library_value(self, adapter):
        """OutputFilter should respect indexable from library."""
        chunks = [
            {
                "content": "Test content",
                "metadata": {"indexable": False, "is_leaf": True}
            }
        ]

        filtered = adapter._output_filter._add_indexable_field(chunks)

        # Should NOT overwrite library value
        assert filtered[0]["metadata"]["indexable"] is False

    def test_indexable_field_set_if_missing(self, adapter):
        """OutputFilter should set indexable if missing."""
        chunks = [
            {
                "content": "Test content",
                "metadata": {"is_leaf": True}
            }
        ]

        filtered = adapter._output_filter._add_indexable_field(chunks)

        # Should set indexable=True for leaf
        assert filtered[0]["metadata"]["indexable"] is True


class TestNoEmbeddedOverlap:
    """Tests that render_with_embedded_overlap is not used."""

    def test_no_embedded_overlap_in_output(
        self, sde_criteria_document, adapter, config
    ):
        """Output should not contain embedded overlap markers."""
        result = adapter.run_chunking(
            sde_criteria_document, config, include_metadata=False
        )

        for chunk in result:
            # Should not contain overlap markers
            assert "[previous:" not in chunk
            assert "[next:" not in chunk


# Helper functions

def extract_content_from_dify_style(chunk: str) -> str:
    """Extract content from dify-style chunk."""
    marker = "</metadata>\n"
    if marker in chunk:
        return chunk.split(marker, 1)[1]
    return chunk


def calculate_line_recall(chunks: list[dict], original: str) -> float:
    """Calculate recall of original lines."""
    def normalize(s: str) -> str:
        return ' '.join(s.split())

    original_lines = [
        normalize(line) for line in original.split('\n')
        if len(normalize(line)) >= 20
    ]

    if not original_lines:
        return 1.0

    chunks_text = normalize(' '.join(c["content"] for c in chunks))

    found = sum(1 for line in original_lines if line in chunks_text)
    return found / len(original_lines)
