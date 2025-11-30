"""
Tests for fallback metadata preservation in ChunkingResult.

This module tests that fallback metadata from FallbackManager is properly
preserved in the final ChunkingResult instead of being overwritten by
error-based logic.
"""

from unittest.mock import Mock, patch

import pytest

from markdown_chunker.chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig, ChunkingResult


class TestFallbackMetadataPreservation:
    """Test fallback metadata preservation functionality."""

    def test_no_fallback_metadata_when_primary_succeeds(self):
        """Test that fallback metadata is correct when primary strategy succeeds."""
        chunker = MarkdownChunker()
        md = "# Header\n\nSimple paragraph content."

        result = chunker.chunk_with_analysis(md)

        # Should not use fallback when primary strategy succeeds
        assert result.fallback_used is False
        assert result.fallback_level == 0
        assert len(result.warnings) == 0
        assert len(result.errors) == 0

        # Chunks should have execution metadata
        for chunk in result.chunks:
            assert chunk.metadata["execution_fallback_used"] is False
            assert chunk.metadata["execution_fallback_level"] == 0
            assert chunk.metadata["execution_strategy_used"] == result.strategy_used

    def test_fallback_metadata_preserved_from_fallback_manager(self):
        """Test that fallback metadata from FallbackManager is preserved."""
        chunker = MarkdownChunker()

        # Mock FallbackManager to return specific fallback metadata
        mock_result = ChunkingResult(
            chunks=[Mock()],  # Mock chunk
            strategy_used="sentences",
            processing_time=0.1,
            fallback_used=True,
            fallback_level=3,
            errors=["Primary strategy failed", "Structural strategy failed"],
            warnings=["Primary strategy returned no chunks"],
        )

        with patch.object(
            chunker._fallback_manager, "execute_with_fallback", return_value=mock_result
        ):
            result = chunker.chunk_with_analysis("# Test\n\nContent")

        # Fallback metadata should be preserved from FallbackManager
        assert result.fallback_used is True
        assert result.fallback_level == 3
        assert result.strategy_used == "sentences"
        assert "Primary strategy failed" in result.errors
        assert "Structural strategy failed" in result.errors
        assert "Primary strategy returned no chunks" in result.warnings

    def test_fallback_metadata_not_overwritten_by_error_logic(self):
        """Test that fallback metadata is not overwritten by error-based logic."""
        chunker = MarkdownChunker()

        # Create a result that has errors but fallback_used=False (edge case)
        mock_result = ChunkingResult(
            chunks=[Mock()],
            strategy_used="mixed",
            processing_time=0.1,
            fallback_used=False,  # Primary succeeded but had warnings
            fallback_level=0,
            errors=[],  # No errors
            warnings=["Some non-critical warning"],
        )

        with patch.object(
            chunker._fallback_manager, "execute_with_fallback", return_value=mock_result
        ):
            result = chunker.chunk_with_analysis("# Test\n\nContent")

        # Should preserve FallbackManager metadata, not use error-based logic
        assert (
            result.fallback_used is False
        )  # From FallbackManager, not len(errors) > 0
        assert (
            result.fallback_level == 0
        )  # From FallbackManager, not 1 if errors else 0
        assert len(result.warnings) == 1
        assert "Some non-critical warning" in result.warnings

    def test_emergency_fallback_metadata(self):
        """Test metadata when emergency fallback is used."""
        chunker = MarkdownChunker()

        # Mock FallbackManager to raise exception, triggering emergency fallback
        with patch.object(
            chunker._fallback_manager,
            "execute_with_fallback",
            side_effect=Exception("All strategies failed"),
        ):
            result = chunker.chunk_with_analysis("# Test\n\nContent")

        # When all strategies fail, should return error result
        assert result.fallback_used is True
        assert result.fallback_level == 4  # Emergency level
        assert result.strategy_used == "none"  # No strategy succeeded
        assert len(result.errors) > 0
        assert any("failed" in str(err).lower() for err in result.errors)

    def test_fallback_metadata_in_chunk_metadata(self):
        """Test that fallback metadata is included in individual chunk metadata."""
        chunker = MarkdownChunker()

        # Mock a fallback scenario
        mock_chunk = Mock()
        mock_chunk.metadata = {"strategy": "sentences", "content_type": "text"}
        mock_chunk.content = "Test content"
        mock_chunk.start_line = 1
        mock_chunk.end_line = 1

        mock_result = ChunkingResult(
            chunks=[mock_chunk],
            strategy_used="sentences",
            processing_time=0.1,
            fallback_used=True,
            fallback_level=3,
            errors=["Primary failed"],
            warnings=["Warning message"],
        )

        with patch.object(
            chunker._fallback_manager, "execute_with_fallback", return_value=mock_result
        ):
            # Mock metadata enricher to avoid complex setup
            with patch.object(
                chunker._metadata_enricher, "enrich_chunks"
            ) as mock_enrich:
                mock_enrich.return_value = [mock_chunk]

                chunker.chunk_with_analysis("# Test\n\nContent")

                # Check that fallback_info was passed to metadata enricher
                mock_enrich.assert_called_once()
                call_args = mock_enrich.call_args
                assert "fallback_info" in call_args.kwargs

                fallback_info = call_args.kwargs["fallback_info"]
                assert fallback_info["fallback_used"] is True
                assert fallback_info["fallback_level"] == 3
                assert fallback_info["strategy_used"] == "sentences"

    def test_warnings_preserved_from_fallback_manager(self):
        """Test that warnings from FallbackManager are preserved in final result."""
        chunker = MarkdownChunker()

        mock_result = ChunkingResult(
            chunks=[Mock()],
            strategy_used="structural",
            processing_time=0.1,
            fallback_used=True,
            fallback_level=2,
            errors=["Primary strategy failed"],
            warnings=["Primary strategy returned no chunks", "Another warning"],
        )

        with patch.object(
            chunker._fallback_manager, "execute_with_fallback", return_value=mock_result
        ):
            result = chunker.chunk_with_analysis("# Test\n\nContent")

        # All warnings should be preserved
        assert len(result.warnings) == 2
        assert "Primary strategy returned no chunks" in result.warnings
        assert "Another warning" in result.warnings

    def test_manual_strategy_no_fallback_metadata(self):
        """Test that manual strategy selection doesn't use fallback metadata."""
        chunker = MarkdownChunker()

        # Use manual strategy selection (bypasses FallbackManager)
        result = chunker.chunk_with_analysis("# Test\n\nContent", strategy="sentences")

        # Should not use fallback when manually selecting strategy
        assert result.fallback_used is False
        assert result.fallback_level == 0
        assert result.strategy_used == "sentences"

        # Note: May have validation warnings if data completeness check
        # detects minor discrepancies (e.g., whitespace normalization)
        # This is expected behavior from the validator
        assert len(result.warnings) <= 1  # Allow validation warnings

    def test_stage1_failure_fallback_metadata(self):
        """Test fallback metadata when Stage 1 processing fails."""
        chunker = MarkdownChunker()

        # Mock Stage 1 to fail
        with patch.object(
            chunker.stage1, "process_document", side_effect=Exception("Stage 1 failed")
        ):
            result = chunker.chunk_with_analysis("# Test\n\nContent")

        # Should return empty result with fallback metadata
        assert len(result.chunks) == 0
        assert result.strategy_used == "none"
        assert result.fallback_used is True
        assert result.fallback_level == 4  # Highest fallback level
        assert "Stage 1 processing failed" in str(result.errors)


class TestFallbackMetadataIntegration:
    """Integration tests for fallback metadata preservation."""

    def test_complete_pipeline_with_fallback(self):
        """Test complete pipeline preserves fallback metadata correctly."""
        config = ChunkConfig(
            max_chunk_size=100,  # Small size to potentially trigger fallbacks
            min_chunk_size=10,
        )
        chunker = MarkdownChunker(config)

        # Use content that might trigger fallback
        md = "# Very Long Header That Exceeds Chunk Size Limits\n\n" + "Content. " * 50

        result = chunker.chunk_with_analysis(md)

        # Verify result structure
        assert isinstance(result, ChunkingResult)
        assert len(result.chunks) > 0

        # Verify fallback metadata is consistent
        assert isinstance(result.fallback_used, bool)
        assert isinstance(result.fallback_level, int)
        assert result.fallback_level >= 0

        # If fallback was used, verify metadata consistency
        if result.fallback_used:
            assert result.fallback_level > 0
            # Chunks should have execution metadata
            for chunk in result.chunks:
                assert "execution_fallback_used" in chunk.metadata
                assert chunk.metadata["execution_fallback_used"] is True
                assert (
                    chunk.metadata["execution_fallback_level"] == result.fallback_level
                )

    def test_metadata_enricher_receives_fallback_info(self):
        """Test that MetadataEnricher receives and uses fallback information."""
        chunker = MarkdownChunker()

        # Create a scenario where fallback is used
        mock_chunk = Mock()
        mock_chunk.metadata = {"strategy": "emergency", "content_type": "text"}
        mock_chunk.content = "Emergency content"
        mock_chunk.start_line = 1
        mock_chunk.end_line = 1

        mock_result = ChunkingResult(
            chunks=[mock_chunk],
            strategy_used="emergency",
            processing_time=0.1,
            fallback_used=True,
            fallback_level=4,
            errors=["All strategies failed"],
            warnings=[],
        )

        with patch.object(
            chunker._fallback_manager, "execute_with_fallback", return_value=mock_result
        ):
            # Spy on metadata enricher
            original_enrich = chunker._metadata_enricher.enrich_chunks

            def spy_enrich(*args, **kwargs):
                # Verify fallback_info is passed
                assert "fallback_info" in kwargs
                fallback_info = kwargs["fallback_info"]
                assert fallback_info["fallback_used"] is True
                assert fallback_info["fallback_level"] == 4
                assert fallback_info["strategy_used"] == "emergency"

                # Call original method
                return original_enrich(*args, **kwargs)

            with patch.object(
                chunker._metadata_enricher, "enrich_chunks", side_effect=spy_enrich
            ):
                result = chunker.chunk_with_analysis("# Test\n\nContent")

                # Verify the result
                assert result.fallback_used is True
                assert result.fallback_level == 4
                assert result.strategy_used == "emergency"


if __name__ == "__main__":
    pytest.main([__file__])
