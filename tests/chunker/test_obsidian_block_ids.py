"""Tests for Obsidian block ID stripping functionality.

Tests the strip_obsidian_block_ids configuration option and preprocessing.
"""

from markdown_chunker_v2.chunker import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig


class TestObsidianBlockIDStripping:
    """Test Obsidian block ID removal feature."""

    def test_strip_enabled_single_id(self):
        """Strip single Obsidian block ID when enabled."""
        text = "This is content with block reference. ^abc123"
        config = ChunkConfig(strip_obsidian_block_ids=True)
        chunker = MarkdownChunker(config)

        result = chunker._preprocess_text(text)

        assert "^abc123" not in result
        assert result.strip() == "This is content with block reference."

    def test_strip_enabled_multiple_ids(self):
        """Strip multiple Obsidian block IDs when enabled."""
        text = """Line one with ID. ^id001
Line two with ID. ^id002
Line three with ID. ^id003"""

        config = ChunkConfig(strip_obsidian_block_ids=True)
        chunker = MarkdownChunker(config)

        result = chunker._preprocess_text(text)

        assert "^id001" not in result
        assert "^id002" not in result
        assert "^id003" not in result
        assert "Line one with ID." in result
        assert "Line two with ID." in result
        assert "Line three with ID." in result

    def test_strip_disabled_preserves_ids(self):
        """Preserve Obsidian block IDs when disabled (default)."""
        text = "Content with block reference. ^abc123"
        config = ChunkConfig(strip_obsidian_block_ids=False)
        chunker = MarkdownChunker(config)

        result = chunker._preprocess_text(text)

        assert "^abc123" in result
        assert result == text

    def test_default_config_preserves_ids(self):
        """Default config preserves Obsidian block IDs."""
        text = "Content with block reference. ^xyz789"
        config = ChunkConfig()  # Default strip_obsidian_block_ids=False
        chunker = MarkdownChunker(config)

        result = chunker._preprocess_text(text)

        assert "^xyz789" in result

    def test_strip_alphanumeric_ids(self):
        """Strip block IDs with alphanumeric characters."""
        text = """Content A. ^abc
Content B. ^123
Content C. ^a1b2c3"""

        config = ChunkConfig(strip_obsidian_block_ids=True)
        chunker = MarkdownChunker(config)

        result = chunker._preprocess_text(text)

        assert "^abc" not in result
        assert "^123" not in result
        assert "^a1b2c3" not in result

    def test_strip_with_trailing_spaces(self):
        """Strip block IDs with trailing spaces."""
        text = "Content with spaces.  ^id123  "
        config = ChunkConfig(strip_obsidian_block_ids=True)
        chunker = MarkdownChunker(config)

        result = chunker._preprocess_text(text)

        assert "^id123" not in result
        assert result.strip() == "Content with spaces."

    def test_dont_strip_mid_line_caret(self):
        """Don't strip ^text that appears mid-line (not a block ID)."""
        text = "Use ^C to cancel or run ^command in shell"
        config = ChunkConfig(strip_obsidian_block_ids=True)
        chunker = MarkdownChunker(config)

        result = chunker._preprocess_text(text)

        # Mid-line carets should be preserved
        assert "^C" in result
        assert "^command" in result

    def test_chunk_method_applies_preprocessing(self):
        """Chunk method applies preprocessing when enabled."""
        text = """# Header

Content with block ID. ^blockref

More content."""

        config = ChunkConfig(strip_obsidian_block_ids=True, max_chunk_size=500)
        chunker = MarkdownChunker(config)

        chunks = chunker.chunk(text)

        # Check that ^blockref is not in any chunk content
        for chunk in chunks:
            assert "^blockref" not in chunk.content

    def test_hierarchical_chunk_applies_preprocessing(self):
        """Hierarchical chunking applies preprocessing when enabled."""
        text = """# Main Header

Section content with ID. ^section1

## Subsection

Subsection content with ID. ^section2"""

        config = ChunkConfig(strip_obsidian_block_ids=True, max_chunk_size=500)
        chunker = MarkdownChunker(config)

        result = chunker.chunk_hierarchical(text)

        # Check all chunks
        for chunk in result.chunks:
            assert "^section1" not in chunk.content
            assert "^section2" not in chunk.content

    def test_real_world_russian_example(self):
        """Test with real-world Russian content example."""
        text = """Помогает команде принимать архитектурные решения. ^be59e1

Результаты работы влияют на производительность продукта. ^8b067e"""

        config = ChunkConfig(strip_obsidian_block_ids=True)
        chunker = MarkdownChunker(config)

        result = chunker._preprocess_text(text)

        assert "^be59e1" not in result
        assert "^8b067e" not in result
        assert "Помогает команде принимать архитектурные решения." in result
        assert "Результаты работы влияют на производительность продукта." in result

    def test_empty_text(self):
        """Handle empty text gracefully."""
        config = ChunkConfig(strip_obsidian_block_ids=True)
        chunker = MarkdownChunker(config)

        result = chunker._preprocess_text("")
        assert result == ""

    def test_no_block_ids_text_unchanged(self):
        """Text without block IDs remains unchanged."""
        text = """# Regular Markdown

This is just regular content
without any Obsidian block references."""

        config = ChunkConfig(strip_obsidian_block_ids=True)
        chunker = MarkdownChunker(config)

        result = chunker._preprocess_text(text)

        assert result == text
