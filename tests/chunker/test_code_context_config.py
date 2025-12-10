"""
Unit tests for code-context binding configuration.

Tests validation of new configuration parameters for enhanced
code-context binding feature.
"""

import pytest

from markdown_chunker_v2.config import ChunkConfig


class TestCodeContextConfigValidation:
    """Test validation of code-context binding parameters."""

    def test_default_config_valid(self):
        """Default configuration is valid."""
        config = ChunkConfig()

        # Verify defaults
        assert config.enable_code_context_binding is True
        assert config.max_context_chars_before == 500
        assert config.max_context_chars_after == 300
        assert config.related_block_max_gap == 5
        assert config.bind_output_blocks is True
        assert config.preserve_before_after_pairs is True

    def test_custom_config_valid(self):
        """Custom configuration values are accepted."""
        config = ChunkConfig(
            enable_code_context_binding=False,
            max_context_chars_before=1000,
            max_context_chars_after=500,
            related_block_max_gap=10,
            bind_output_blocks=False,
            preserve_before_after_pairs=False,
        )

        assert config.enable_code_context_binding is False
        assert config.max_context_chars_before == 1000
        assert config.max_context_chars_after == 500
        assert config.related_block_max_gap == 10
        assert config.bind_output_blocks is False
        assert config.preserve_before_after_pairs is False

    def test_negative_max_context_chars_before_invalid(self):
        """Negative max_context_chars_before raises error."""
        with pytest.raises(
            ValueError, match="max_context_chars_before must be non-negative"
        ):
            ChunkConfig(max_context_chars_before=-1)

    def test_negative_max_context_chars_after_invalid(self):
        """Negative max_context_chars_after raises error."""
        with pytest.raises(
            ValueError, match="max_context_chars_after must be non-negative"
        ):
            ChunkConfig(max_context_chars_after=-1)

    def test_zero_max_context_chars_valid(self):
        """Zero max_context_chars is valid (disables extraction)."""
        config = ChunkConfig(
            max_context_chars_before=0,
            max_context_chars_after=0,
        )

        assert config.max_context_chars_before == 0
        assert config.max_context_chars_after == 0

    def test_zero_related_block_max_gap_invalid(self):
        """Zero related_block_max_gap raises error."""
        with pytest.raises(ValueError, match="related_block_max_gap must be >= 1"):
            ChunkConfig(related_block_max_gap=0)

    def test_negative_related_block_max_gap_invalid(self):
        """Negative related_block_max_gap raises error."""
        with pytest.raises(ValueError, match="related_block_max_gap must be >= 1"):
            ChunkConfig(related_block_max_gap=-5)


class TestCodeContextConfigSerialization:
    """Test serialization of code-context binding configuration."""

    def test_to_dict_includes_new_params(self):
        """to_dict() includes code-context binding parameters."""
        config = ChunkConfig()
        data = config.to_dict()

        assert "enable_code_context_binding" in data
        assert "max_context_chars_before" in data
        assert "max_context_chars_after" in data
        assert "related_block_max_gap" in data
        assert "bind_output_blocks" in data
        assert "preserve_before_after_pairs" in data

        assert data["enable_code_context_binding"] is True
        assert data["max_context_chars_before"] == 500
        assert data["max_context_chars_after"] == 300
        assert data["related_block_max_gap"] == 5
        assert data["bind_output_blocks"] is True
        assert data["preserve_before_after_pairs"] is True

    def test_from_dict_with_new_params(self):
        """from_dict() handles code-context binding parameters."""
        data = {
            "max_chunk_size": 2048,
            "enable_code_context_binding": False,
            "max_context_chars_before": 800,
            "max_context_chars_after": 400,
            "related_block_max_gap": 3,
            "bind_output_blocks": False,
            "preserve_before_after_pairs": False,
        }

        config = ChunkConfig.from_dict(data)

        assert config.max_chunk_size == 2048
        assert config.enable_code_context_binding is False
        assert config.max_context_chars_before == 800
        assert config.max_context_chars_after == 400
        assert config.related_block_max_gap == 3
        assert config.bind_output_blocks is False
        assert config.preserve_before_after_pairs is False

    def test_from_dict_without_new_params_uses_defaults(self):
        """from_dict() uses defaults when new params missing."""
        data = {
            "max_chunk_size": 2048,
        }

        config = ChunkConfig.from_dict(data)

        # Should use defaults for code-context binding params
        assert config.enable_code_context_binding is True
        assert config.max_context_chars_before == 500
        assert config.max_context_chars_after == 300
        assert config.related_block_max_gap == 5
        assert config.bind_output_blocks is True
        assert config.preserve_before_after_pairs is True

    def test_roundtrip_serialization(self):
        """Configuration survives roundtrip serialization."""
        original = ChunkConfig(
            max_chunk_size=3000,
            enable_code_context_binding=False,
            max_context_chars_before=700,
            related_block_max_gap=8,
        )

        data = original.to_dict()
        restored = ChunkConfig.from_dict(data)

        assert restored.max_chunk_size == original.max_chunk_size
        assert (
            restored.enable_code_context_binding == original.enable_code_context_binding
        )
        assert restored.max_context_chars_before == original.max_context_chars_before
        assert restored.related_block_max_gap == original.related_block_max_gap


class TestBackwardCompatibility:
    """Test backward compatibility of configuration."""

    def test_existing_code_works_without_new_params(self):
        """Existing code creating ChunkConfig still works."""
        # This is how existing code creates configs
        config = ChunkConfig(
            max_chunk_size=2048,
            min_chunk_size=256,
            overlap_size=100,
        )

        # Should work without specifying new params
        assert config.max_chunk_size == 2048
        assert config.min_chunk_size == 256
        assert config.overlap_size == 100

        # New params should have defaults
        assert config.enable_code_context_binding is True
        assert config.max_context_chars_before == 500

    def test_for_code_heavy_profile_works(self):
        """Existing profile methods still work."""
        config = ChunkConfig.for_code_heavy()

        # Should have code-heavy settings
        assert config.max_chunk_size == 8192
        assert config.code_threshold == 0.2

        # Should have default code-context settings
        assert config.enable_code_context_binding is True

    def test_all_profiles_work(self):
        """All configuration profiles work with new params."""
        profiles = [
            ChunkConfig.default(),
            ChunkConfig.for_code_heavy(),
            ChunkConfig.for_structured(),
            ChunkConfig.minimal(),
            ChunkConfig.for_changelogs(),
        ]

        for config in profiles:
            # All should have valid code-context binding params
            assert isinstance(config.enable_code_context_binding, bool)
            assert config.max_context_chars_before >= 0
            assert config.max_context_chars_after >= 0
            assert config.related_block_max_gap >= 1


class TestFeatureFlagBehavior:
    """Test enable_code_context_binding flag behavior."""

    def test_feature_enabled_by_default(self):
        """Feature is enabled by default."""
        config = ChunkConfig()
        assert config.enable_code_context_binding is True

    def test_feature_can_be_disabled(self):
        """Feature can be explicitly disabled."""
        config = ChunkConfig(enable_code_context_binding=False)
        assert config.enable_code_context_binding is False

    def test_disabled_feature_still_validates_params(self):
        """Parameters validated even when feature disabled."""
        # Should still validate even when disabled
        with pytest.raises(ValueError):
            ChunkConfig(
                enable_code_context_binding=False,
                max_context_chars_before=-1,  # Invalid
            )
