"""Unit tests for configuration."""

import pytest

from markdown_chunker.config import ChunkConfig
from markdown_chunker.types import ConfigurationError


class TestChunkConfig:
    """Test ChunkConfig dataclass."""

    def test_default_config(self):
        """Test default configuration factory."""
        config = ChunkConfig.default()
        assert config.max_chunk_size == 4096
        assert config.min_chunk_size == 512
        assert config.overlap_size == 200
        assert config.preserve_atomic_blocks is True
        assert config.code_threshold == 0.3
        assert config.structure_threshold == 3

    def test_for_code_docs_config(self):
        """Test code docs configuration factory."""
        config = ChunkConfig.for_code_docs()
        assert config.max_chunk_size == 6144
        assert config.code_threshold == 0.2
        assert config.overlap_size == 300

    def test_for_rag_config(self):
        """Test RAG configuration factory."""
        config = ChunkConfig.for_rag()
        assert config.max_chunk_size == 2048
        assert config.overlap_size == 150

    def test_derived_target_chunk_size(self):
        """Test derived target_chunk_size property."""
        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=200)
        assert config.target_chunk_size == 600

    def test_derived_min_effective_chunk_size(self):
        """Test derived min_effective_chunk_size property."""
        config = ChunkConfig(max_chunk_size=1000)
        assert config.min_effective_chunk_size == 400

    def test_overlap_enabled_property(self):
        """Test overlap_enabled property."""
        config1 = ChunkConfig(overlap_size=200)
        assert config1.overlap_enabled is True

        config2 = ChunkConfig(overlap_size=0)
        assert config2.overlap_enabled is False

    def test_validation_max_less_than_min(self):
        """Test that max_chunk_size < min_chunk_size raises error."""
        with pytest.raises(ConfigurationError, match="max_chunk_size"):
            ChunkConfig(max_chunk_size=100, min_chunk_size=200)

    def test_validation_min_too_small(self):
        """Test that min_chunk_size < 1 raises error."""
        with pytest.raises(ConfigurationError, match="min_chunk_size"):
            ChunkConfig(min_chunk_size=0)

    def test_validation_overlap_negative(self):
        """Test that negative overlap_size raises error."""
        with pytest.raises(ConfigurationError, match="overlap_size"):
            ChunkConfig(overlap_size=-10)

    def test_validation_overlap_too_large(self):
        """Test that overlap_size >= max_chunk_size raises error."""
        with pytest.raises(ConfigurationError, match="overlap_size"):
            ChunkConfig(max_chunk_size=1000, overlap_size=1000)

    def test_validation_code_threshold_out_of_range(self):
        """Test that code_threshold outside [0, 1] raises error."""
        with pytest.raises(ConfigurationError, match="code_threshold"):
            ChunkConfig(code_threshold=1.5)

        with pytest.raises(ConfigurationError, match="code_threshold"):
            ChunkConfig(code_threshold=-0.1)

    def test_validation_structure_threshold_too_small(self):
        """Test that structure_threshold < 1 raises error."""
        with pytest.raises(ConfigurationError, match="structure_threshold"):
            ChunkConfig(structure_threshold=0)

    def test_config_repr(self):
        """Test string representation."""
        config = ChunkConfig()
        repr_str = repr(config)
        assert "ChunkConfig" in repr_str
        assert "max=4096" in repr_str
