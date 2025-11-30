"""
Tests for ChunkConfig validation and auto-adjustment functionality.

This module tests the validation logic in ChunkConfig.__post_init__ to ensure
that small chunk sizes are handled correctly and auto-adjustment works as expected.
"""

import pytest

from markdown_chunker.chunker.types import ChunkConfig


class TestChunkConfigValidation:
    """Test ChunkConfig validation and auto-adjustment."""

    def test_default_config_valid(self):
        """Test that default configuration is valid."""
        config = ChunkConfig()
        assert config.max_chunk_size > 0
        assert config.min_chunk_size > 0
        assert (
            config.min_chunk_size <= config.target_chunk_size <= config.max_chunk_size
        )

    def test_small_max_chunk_size_auto_adjustment(self):
        """Test auto-adjustment when max_chunk_size is smaller than default min_chunk_size."""
        # Default min_chunk_size is 512, so max_chunk_size=500 should trigger adjustment
        config = ChunkConfig(max_chunk_size=500)

        assert config.max_chunk_size == 500
        assert config.min_chunk_size == 250  # max(1, 500 // 2)
        assert config.target_chunk_size == 500  # Adjusted to max_chunk_size
        assert (
            config.min_chunk_size <= config.target_chunk_size <= config.max_chunk_size
        )

    def test_very_small_max_chunk_size(self):
        """Test auto-adjustment with very small max_chunk_size."""
        config = ChunkConfig(max_chunk_size=200)

        assert config.max_chunk_size == 200
        assert config.min_chunk_size == 100  # max(1, 200 // 2)
        assert config.target_chunk_size == 200
        assert (
            config.min_chunk_size <= config.target_chunk_size <= config.max_chunk_size
        )

    def test_tiny_max_chunk_size(self):
        """Test auto-adjustment with tiny max_chunk_size."""
        config = ChunkConfig(max_chunk_size=10)

        assert config.max_chunk_size == 10
        assert config.min_chunk_size == 5  # max(1, 10 // 2)
        assert config.target_chunk_size == 10
        assert (
            config.min_chunk_size <= config.target_chunk_size <= config.max_chunk_size
        )

    def test_min_chunk_size_one(self):
        """Test that min_chunk_size never goes below 1."""
        config = ChunkConfig(max_chunk_size=1)

        assert config.max_chunk_size == 1
        assert config.min_chunk_size == 1  # max(1, 1 // 2) = max(1, 0) = 1
        assert config.target_chunk_size == 1

    def test_target_chunk_size_adjustment_too_large(self):
        """Test target_chunk_size adjustment when it's larger than max_chunk_size."""
        config = ChunkConfig(max_chunk_size=1000, target_chunk_size=1500)  # Too large

        assert config.max_chunk_size == 1000
        assert config.target_chunk_size == 1000  # Adjusted down
        assert (
            config.min_chunk_size <= config.target_chunk_size <= config.max_chunk_size
        )

    def test_target_chunk_size_adjustment_too_small(self):
        """Test target_chunk_size adjustment when it's smaller than min_chunk_size."""
        config = ChunkConfig(
            max_chunk_size=1000, min_chunk_size=300, target_chunk_size=200  # Too small
        )

        assert config.max_chunk_size == 1000
        assert config.min_chunk_size == 300
        assert config.target_chunk_size == 300  # Adjusted up
        assert (
            config.min_chunk_size <= config.target_chunk_size <= config.max_chunk_size
        )

    def test_equal_sizes_allowed(self):
        """Test that equal min, target, and max sizes are allowed."""
        config = ChunkConfig(
            max_chunk_size=1000, min_chunk_size=1000, target_chunk_size=1000
        )

        assert config.max_chunk_size == 1000
        assert config.min_chunk_size == 1000
        assert config.target_chunk_size == 1000

    def test_size_invariants_maintained(self):
        """Test that size invariants are always maintained after adjustment."""
        test_cases = [
            {"max_chunk_size": 100},
            {"max_chunk_size": 500},
            {"max_chunk_size": 1000, "target_chunk_size": 1500},
            {"max_chunk_size": 1000, "min_chunk_size": 300, "target_chunk_size": 200},
            {"max_chunk_size": 50, "min_chunk_size": 100},  # min > max
        ]

        for kwargs in test_cases:
            config = ChunkConfig(**kwargs)
            assert (
                config.min_chunk_size
                <= config.target_chunk_size
                <= config.max_chunk_size
            ), f"Size invariant violated for {kwargs}: min={config.min_chunk_size}, target={config.target_chunk_size}, max={config.max_chunk_size}"

    def test_percentage_validation(self):
        """Test that percentage values are validated correctly."""
        # Valid percentages
        config = ChunkConfig(
            overlap_percentage=0.5,
            code_ratio_threshold=0.7,
            list_ratio_threshold=0.6,
            table_ratio_threshold=0.4,
        )
        assert config.overlap_percentage == 0.5

        # Invalid overlap_percentage
        with pytest.raises(
            ValueError, match="overlap_percentage must be between 0.0 and 1.0"
        ):
            ChunkConfig(overlap_percentage=1.5)

        with pytest.raises(
            ValueError, match="overlap_percentage must be between 0.0 and 1.0"
        ):
            ChunkConfig(overlap_percentage=-0.1)

        # Invalid code_ratio_threshold
        with pytest.raises(
            ValueError, match="code_ratio_threshold must be between 0.0 and 1.0"
        ):
            ChunkConfig(code_ratio_threshold=1.5)

        # Invalid list_ratio_threshold
        with pytest.raises(
            ValueError, match="list_ratio_threshold must be between 0.0 and 1.0"
        ):
            ChunkConfig(list_ratio_threshold=-0.1)

        # Invalid table_ratio_threshold
        with pytest.raises(
            ValueError, match="table_ratio_threshold must be between 0.0 and 1.0"
        ):
            ChunkConfig(table_ratio_threshold=1.5)

    def test_positive_size_validation(self):
        """Test that size values must be positive."""
        with pytest.raises(ValueError, match="max_chunk_size must be positive"):
            ChunkConfig(max_chunk_size=0)

        with pytest.raises(ValueError, match="max_chunk_size must be positive"):
            ChunkConfig(max_chunk_size=-100)

        with pytest.raises(ValueError, match="min_chunk_size must be positive"):
            ChunkConfig(min_chunk_size=0)

        with pytest.raises(ValueError, match="min_chunk_size must be positive"):
            ChunkConfig(min_chunk_size=-50)

    def test_integration_test_scenarios(self):
        """Test scenarios that were failing in integration tests."""
        # This was failing before the fix
        config = ChunkConfig(max_chunk_size=500)
        assert config.max_chunk_size == 500
        assert config.min_chunk_size == 250
        assert config.target_chunk_size == 500

        # Test with chunker creation (integration scenario)
        from markdown_chunker.chunker import MarkdownChunker

        chunker = MarkdownChunker(config)
        assert chunker.config.max_chunk_size == 500
        assert chunker.config.min_chunk_size == 250

    def test_factory_methods_still_work(self):
        """Test that factory methods still work after validation changes."""
        # Test all factory methods
        configs = [
            ChunkConfig.default(),
            ChunkConfig.for_code_heavy(),
            ChunkConfig.for_structured_docs(),
            ChunkConfig.for_large_documents(),
            ChunkConfig.compact(),
        ]

        for config in configs:
            # All should maintain size invariants
            assert (
                config.min_chunk_size
                <= config.target_chunk_size
                <= config.max_chunk_size
            )
            assert config.max_chunk_size > 0
            assert config.min_chunk_size > 0
