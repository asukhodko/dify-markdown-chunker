"""
Tests for preamble configuration in ChunkConfig.
"""

import pytest

from markdown_chunker.chunker.types import ChunkConfig


class TestPreambleConfig:
    """Tests for preamble configuration fields."""

    def test_default_preamble_settings(self):
        """Test default preamble settings."""
        config = ChunkConfig()

        assert config.extract_preamble is True
        assert config.separate_preamble_chunk is False
        assert config.preamble_min_size == 10

    def test_custom_preamble_settings(self):
        """Test custom preamble settings."""
        config = ChunkConfig(
            extract_preamble=False,
            separate_preamble_chunk=True,
            preamble_min_size=50,
        )

        assert config.extract_preamble is False
        assert config.separate_preamble_chunk is True
        assert config.preamble_min_size == 50

    def test_negative_preamble_min_size_raises_error(self):
        """Test that negative preamble_min_size raises ValueError."""
        with pytest.raises(ValueError, match="preamble_min_size must be non-negative"):
            ChunkConfig(preamble_min_size=-1)

    def test_preamble_disabled(self):
        """Test disabling preamble extraction."""
        config = ChunkConfig(extract_preamble=False)

        assert config.extract_preamble is False

    def test_separate_preamble_chunk_enabled(self):
        """Test enabling separate preamble chunk."""
        config = ChunkConfig(extract_preamble=True, separate_preamble_chunk=True)

        assert config.extract_preamble is True
        assert config.separate_preamble_chunk is True

    def test_factory_methods_preserve_preamble_defaults(self):
        """Test that factory methods preserve preamble defaults."""
        configs = [
            ChunkConfig.default(),
            ChunkConfig.for_code_heavy(),
            ChunkConfig.for_dify_rag(),
        ]

        for config in configs:
            assert config.extract_preamble is True
            assert config.preamble_min_size == 10


class TestPreambleChunking:
    """Tests for preamble integration in chunking process."""

    def test_preamble_added_to_first_chunk_metadata(self):
        """Test that preamble is added to first chunk metadata."""
        from markdown_chunker import ChunkConfig, MarkdownChunker

        config = ChunkConfig(extract_preamble=True, separate_preamble_chunk=False)
        chunker = MarkdownChunker(config)

        text = """This is an introduction to the document.

# First Header
Content here.

# Second Header
More content."""

        result = chunker.chunk(text, include_analysis=True)

        assert len(result.chunks) >= 1
        first_chunk = result.chunks[0]
        assert "preamble" in first_chunk.metadata
        assert first_chunk.metadata["has_preamble"] is True
        assert first_chunk.metadata["preamble_type"] == "introduction"

    def test_separate_preamble_chunk(self):
        """Test creating separate preamble chunk."""
        from markdown_chunker import ChunkConfig, MarkdownChunker

        config = ChunkConfig(extract_preamble=True, separate_preamble_chunk=True)
        chunker = MarkdownChunker(config)

        text = """Author: John Doe
Date: 2025-11-10

# First Header
Content here."""

        result = chunker.chunk(text, include_analysis=True)

        # Should have preamble chunk + content chunks
        assert len(result.chunks) >= 2

        # First chunk should be preamble
        preamble_chunk = result.chunks[0]
        assert preamble_chunk.metadata.get("is_preamble_chunk") is True
        assert preamble_chunk.metadata["preamble_type"] == "metadata"
        assert "Author" in preamble_chunk.content

    def test_no_preamble_no_metadata(self):
        """Test that no preamble means no preamble metadata."""
        from markdown_chunker import ChunkConfig, MarkdownChunker

        config = ChunkConfig(extract_preamble=True)
        chunker = MarkdownChunker(config)

        text = """# First Header
Content here."""

        result = chunker.chunk(text, include_analysis=True)

        assert len(result.chunks) >= 1
        first_chunk = result.chunks[0]
        assert "preamble" not in first_chunk.metadata

    def test_preamble_extraction_disabled(self):
        """Test that disabling preamble extraction works."""
        from markdown_chunker import ChunkConfig, MarkdownChunker

        config = ChunkConfig(extract_preamble=False)
        chunker = MarkdownChunker(config)

        text = """This is an introduction.

# Header
Content."""

        result = chunker.chunk(text, include_analysis=True)

        # Preamble should not be in metadata
        first_chunk = result.chunks[0]
        assert "preamble" not in first_chunk.metadata

    def test_preamble_with_metadata_fields(self):
        """Test preamble with metadata fields."""
        from markdown_chunker import ChunkConfig, MarkdownChunker

        config = ChunkConfig(extract_preamble=True, separate_preamble_chunk=True)
        chunker = MarkdownChunker(config)

        text = """Title: Test Document
Author: Jane Smith
Version: 1.0

# Introduction
Content here."""

        result = chunker.chunk(text, include_analysis=True)

        preamble_chunk = result.chunks[0]
        assert preamble_chunk.metadata["has_metadata"] is True
        assert "title" in preamble_chunk.metadata["metadata_fields"]
        assert preamble_chunk.metadata["metadata_fields"]["author"] == "Jane Smith"
