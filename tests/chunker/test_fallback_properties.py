"""
Property-based tests for FallbackManager behavior.

Tests verify that fallback chain works correctly across all scenarios:
- Fallback produces valid chunks when primary fails
- Fallback metadata is correct
- Errors propagate correctly when all fallbacks fail
- Fallback is deterministic and reliable

**Feature: markdown-chunker-quality-audit, Property 12: Fallback Behavior**
**Validates: Requirements 1.3, 2.2**
"""

from unittest.mock import MagicMock, Mock

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from markdown_chunker.chunker.components.fallback_manager import (
    FallbackLevel,
    FallbackManager,
)
from markdown_chunker.chunker.strategies.base import BaseStrategy
from markdown_chunker.chunker.strategies.sentences_strategy import SentencesStrategy
from markdown_chunker.chunker.types import ChunkConfig, ChunkingResult
from markdown_chunker.parser.types import ContentAnalysis, Stage1Results


# Test data generators
@st.composite
def markdown_content(draw):
    """Generate random markdown content."""
    # Generate paragraphs
    num_paragraphs = draw(st.integers(min_value=1, max_value=5))
    paragraphs = []

    for _ in range(num_paragraphs):
        # Generate sentences
        num_sentences = draw(st.integers(min_value=1, max_value=5))
        sentences = []

        for _ in range(num_sentences):
            # Generate words
            num_words = draw(st.integers(min_value=3, max_value=15))
            words = [
                draw(
                    st.text(
                        alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
                        min_size=3,
                        max_size=10,
                    )
                )
                for _ in range(num_words)
            ]

            sentence = " ".join(words) + "."
            sentences.append(sentence)

        paragraph = " ".join(sentences)
        paragraphs.append(paragraph)

    return "\n\n".join(paragraphs)


@st.composite
def mock_stage1_results(draw):
    """Generate mock Stage1Results."""
    from markdown_chunker.parser.types import ElementCollection

    mock = Mock(spec=Stage1Results)

    # Create analysis mock with all required attributes
    mock.analysis = Mock(spec=ContentAnalysis)
    mock.analysis.content_type = draw(
        st.sampled_from(["text_heavy", "code_heavy", "mixed"])
    )
    mock.analysis.line_count = draw(st.integers(min_value=1, max_value=100))
    mock.analysis.char_count = draw(st.integers(min_value=10, max_value=10000))

    # Required basic metrics
    mock.analysis.total_chars = mock.analysis.char_count
    mock.analysis.total_lines = mock.analysis.line_count
    mock.analysis.total_words = mock.analysis.char_count // 5  # Rough estimate

    # Required ratios
    mock.analysis.code_ratio = 0.0
    mock.analysis.text_ratio = 1.0
    mock.analysis.list_ratio = 0.0
    mock.analysis.table_ratio = 0.0

    # Required counts
    mock.analysis.header_count = {}
    mock.analysis.code_block_count = 0
    mock.analysis.list_count = 0
    mock.analysis.table_count = 0
    mock.analysis.link_count = 0
    mock.analysis.image_count = 0
    mock.analysis.inline_code_count = 0

    # Languages
    mock.analysis.languages = {}

    # Complexity metrics
    mock.analysis.complexity_score = 0.0
    mock.analysis.max_header_depth = 0
    mock.analysis.has_mixed_content = False
    mock.analysis.nested_list_depth = 0
    mock.analysis.has_tables = False
    mock.analysis.has_nested_lists = False

    # ContentMetrics fields
    mock.analysis.average_line_length = 0.0
    mock.analysis.max_line_length = 0
    mock.analysis.empty_lines = 0
    mock.analysis.indented_lines = 0
    mock.analysis.punctuation_ratio = 0.0
    mock.analysis.special_chars = {}

    # Block elements
    mock.analysis.block_elements = []
    mock.analysis.preamble = None

    # Helper method
    mock.analysis.get_total_header_count = Mock(return_value=0)

    # Add required Stage1Results attributes
    mock.ast = Mock()  # AST object
    mock.fenced_blocks = []  # List of fenced code blocks

    # Create ElementCollection mock
    mock.elements = Mock(spec=ElementCollection)
    mock.elements.headers = []
    mock.elements.code_blocks = []
    mock.elements.lists = []
    mock.elements.tables = []
    mock.elements.get_element_count = Mock(return_value=0)

    mock.parser_name = "test_parser"
    mock.processing_time = 0.0
    mock.metadata = {}

    return mock


class FailingStrategy(BaseStrategy):
    """Strategy that always fails for testing."""

    name = "failing"
    priority = 1

    def can_handle(self, analysis, config):
        return True

    def apply(self, content, stage1_results, config):
        raise ValueError("Intentional failure for testing")

    def calculate_quality(self, analysis):
        return 0.5


class EmptyStrategy(BaseStrategy):
    """Strategy that returns empty chunks for testing."""

    name = "empty"
    priority = 1

    def can_handle(self, analysis, config):
        return True

    def apply(self, content, stage1_results, config):
        return []  # Empty chunks

    def calculate_quality(self, analysis):
        return 0.5


# Property Tests


@given(
    content=markdown_content(),
    stage1=mock_stage1_results(),
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_fallback_produces_valid_chunks_on_failure(content, stage1):
    """
    Property: When primary strategy fails, fallback produces valid chunks.

    **Feature: markdown-chunker-quality-audit, Property 12a: Fallback Produces Valid Chunks**
    **Validates: Requirements 1.3, 2.2**
    """
    config = ChunkConfig(max_chunk_size=2000)
    manager = FallbackManager(config)

    # Use failing strategy as primary
    failing_strategy = FailingStrategy()

    # Execute with fallback
    result = manager.execute_with_fallback(content, stage1, failing_strategy)

    # Verify fallback produced valid chunks
    assert isinstance(result, ChunkingResult)
    assert len(result.chunks) > 0, "Fallback should produce chunks"
    assert result.fallback_used is True, "Fallback should be marked as used"
    assert result.fallback_level in [
        1,
        2,
    ], "Should use fallback level 1 (structural) or 2 (sentences)"
    assert result.strategy_used in [
        "structural",
        "sentences",
    ], "Should use structural or sentences strategy"

    # Verify chunks are valid
    for chunk in result.chunks:
        assert chunk.content, "Chunk should have content"
        assert len(chunk.content) > 0, "Chunk content should not be empty"


@given(
    content=markdown_content(),
    stage1=mock_stage1_results(),
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_fallback_metadata_correct(content, stage1):
    """
    Property: Fallback chunks have correct metadata.

    **Feature: markdown-chunker-quality-audit, Property 12b: Fallback Metadata Correctness**
    **Validates: Requirements 1.3, 2.2**
    """
    config = ChunkConfig(max_chunk_size=2000)
    manager = FallbackManager(config)

    # Use failing strategy as primary
    failing_strategy = FailingStrategy()

    # Execute with fallback
    result = manager.execute_with_fallback(content, stage1, failing_strategy)

    # Verify fallback metadata in chunks
    for chunk in result.chunks:
        assert "fallback_level" in chunk.metadata, "Chunk should have fallback_level"
        assert chunk.metadata["fallback_level"] in [
            1,
            2,
        ], "Fallback level should be 1 or 2"
        assert "fallback_reason" in chunk.metadata, "Chunk should have fallback_reason"
        # Reason should mention the fallback strategy used
        assert any(
            s in chunk.metadata["fallback_reason"] for s in ["structural", "sentences"]
        ), "Reason should mention fallback strategy"


@given(
    content=markdown_content(),
    stage1=mock_stage1_results(),
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_empty_chunks_trigger_fallback(content, stage1):
    """
    Property: When primary strategy returns empty chunks, fallback is triggered.

    **Feature: markdown-chunker-quality-audit, Property 12c: Empty Chunks Trigger Fallback**
    **Validates: Requirements 1.3, 6.1**
    """
    config = ChunkConfig(max_chunk_size=2000)
    manager = FallbackManager(config)

    # Use empty strategy as primary
    empty_strategy = EmptyStrategy()

    # Execute with fallback
    result = manager.execute_with_fallback(content, stage1, empty_strategy)

    # Verify fallback was triggered
    assert (
        result.fallback_used is True
    ), "Fallback should be used when primary returns empty"
    assert len(result.chunks) > 0, "Fallback should produce chunks"
    assert result.strategy_used == "sentences", "Should use sentences strategy"


@given(
    content=markdown_content(),
    stage1=mock_stage1_results(),
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_fallback_preserves_content(content, stage1):
    """
    Property: Fallback preserves content (minimal data loss).

    **Feature: markdown-chunker-quality-audit, Property 12d: Fallback Preserves Content**
    **Validates: Requirements 1.5, 10.2**

    Note: Fallback uses sentences strategy which may lose some formatting,
    but should preserve most textual content.
    """
    config = ChunkConfig(max_chunk_size=2000)
    manager = FallbackManager(config)

    # Use failing strategy as primary
    failing_strategy = FailingStrategy()

    # Execute with fallback
    result = manager.execute_with_fallback(content, stage1, failing_strategy)

    # Verify content preservation
    combined_content = "".join(chunk.content for chunk in result.chunks)

    # Filter control characters from both for comparison
    import re

    content_filtered = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", content)
    combined_filtered = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", combined_content)

    # Allow for whitespace normalization
    content_words = set(content_filtered.split())
    combined_words = set(combined_filtered.split())

    # Check that most words are preserved
    # Fallback may lose some content due to sentence splitting, so we allow 50% threshold
    if content_words:
        preserved_ratio = len(content_words & combined_words) / len(content_words)
        assert (
            preserved_ratio >= 0.5
        ), f"Should preserve at least 50% of content, got {preserved_ratio:.2%}"


@given(
    content=markdown_content(),
    stage1=mock_stage1_results(),
)
@settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_fallback_is_deterministic(content, stage1):
    """
    Property: Fallback behavior is deterministic (same input → same output).

    **Feature: markdown-chunker-quality-audit, Property 12e: Fallback Determinism**
    **Validates: Requirements 10.2, 10.5**
    """
    config = ChunkConfig(max_chunk_size=2000)
    manager = FallbackManager(config)

    # Use failing strategy as primary
    failing_strategy = FailingStrategy()

    # Execute twice
    result1 = manager.execute_with_fallback(content, stage1, failing_strategy)
    result2 = manager.execute_with_fallback(content, stage1, failing_strategy)

    # Verify determinism
    assert len(result1.chunks) == len(
        result2.chunks
    ), "Should produce same number of chunks"
    assert result1.strategy_used == result2.strategy_used, "Should use same strategy"
    assert (
        result1.fallback_level == result2.fallback_level
    ), "Should use same fallback level"

    # Verify chunk content is identical
    for chunk1, chunk2 in zip(result1.chunks, result2.chunks):
        assert chunk1.content == chunk2.content, "Chunk content should be identical"


@given(
    content=markdown_content(),
    stage1=mock_stage1_results(),
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_sentences_strategy_never_fails(content, stage1):
    """
    Property: Sentences strategy (fallback) never fails.

    **Feature: markdown-chunker-quality-audit, Property 12f: Sentences Strategy Reliability**
    **Validates: Requirements 1.3, 2.2**
    """
    config = ChunkConfig(max_chunk_size=2000)

    # Use sentences strategy directly
    sentences_strategy = SentencesStrategy()

    # Execute (should never raise exception)
    try:
        chunks = sentences_strategy.apply(content, stage1, config)

        # Verify it produced chunks
        assert len(chunks) > 0, "Sentences strategy should always produce chunks"

        # Verify chunks are valid
        for chunk in chunks:
            assert chunk.content, "Chunk should have content"
            assert len(chunk.content) > 0, "Chunk content should not be empty"

    except Exception as e:
        pytest.fail(f"Sentences strategy should never fail, but got: {e}")


@given(
    content=markdown_content(),
    stage1=mock_stage1_results(),
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_fallback_errors_accumulated(content, stage1):
    """
    Property: Fallback accumulates errors from failed strategies.

    **Feature: markdown-chunker-quality-audit, Property 12g: Error Accumulation**
    **Validates: Requirements 1.3, 7.1**
    """
    config = ChunkConfig(max_chunk_size=2000)
    manager = FallbackManager(config)

    # Use failing strategy as primary
    failing_strategy = FailingStrategy()

    # Execute with fallback
    result = manager.execute_with_fallback(content, stage1, failing_strategy)

    # Verify errors are accumulated
    # Note: If fallback succeeds, errors list contains primary failure
    # If fallback also fails, errors list contains both failures
    if result.fallback_used and len(result.chunks) > 0:
        # Fallback succeeded - should have primary error
        assert (
            len(result.errors) > 0 or len(result.warnings) > 0
        ), "Should accumulate errors/warnings from primary failure"


# Unit tests for edge cases


def test_fallback_skipped_when_primary_is_sentences():
    """Test that fallback is skipped when primary is already sentences strategy."""
    config = ChunkConfig(max_chunk_size=2000)
    manager = FallbackManager(config)

    # Use sentences strategy as primary
    sentences_strategy = SentencesStrategy()

    # Mock stage1 results
    stage1 = Mock(spec=Stage1Results)
    stage1.analysis = Mock(spec=ContentAnalysis)
    stage1.analysis.content_type = "text"

    content = "This is a test. This is only a test."

    # Execute
    result = manager.execute_with_fallback(content, stage1, sentences_strategy)

    # Verify no fallback was used (primary succeeded)
    assert (
        result.fallback_used is False
    ), "Should not use fallback when primary is sentences"
    assert result.strategy_used == "sentences", "Should use sentences strategy"
    assert len(result.chunks) > 0, "Should produce chunks"


def test_fallback_validation():
    """Test fallback chain validation."""
    config = ChunkConfig(max_chunk_size=2000, enable_fallback=True)
    manager = FallbackManager(config)

    # Validate
    issues = manager.validate_fallback_chain()

    # Should have no issues
    assert len(issues) == 0, f"Should have no validation issues, got: {issues}"


def test_fallback_validation_disabled():
    """Test fallback chain validation when disabled."""
    config = ChunkConfig(max_chunk_size=2000, enable_fallback=False)
    manager = FallbackManager(config)

    # Validate
    issues = manager.validate_fallback_chain()

    # Should have issue about disabled fallback
    assert len(issues) > 0, "Should have validation issue when fallback disabled"
    assert any(
        "disabled" in issue.lower() for issue in issues
    ), "Should mention that fallback is disabled"


def test_fallback_statistics():
    """Test fallback statistics."""
    config = ChunkConfig(max_chunk_size=2000, enable_fallback=True)
    manager = FallbackManager(config)

    # Get statistics
    stats = manager.get_fallback_statistics()

    # Verify statistics
    assert "fallback_enabled" in stats
    assert stats["fallback_enabled"] is True
    assert "max_fallback_level" in stats
    assert stats["max_fallback_level"] == 2  # 3-level chain (0, 1, 2)
    assert "sentences_strategy" in stats
    assert stats["sentences_strategy"] == "sentences"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
