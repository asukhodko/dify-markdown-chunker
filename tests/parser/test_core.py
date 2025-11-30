"""Tests for parser.core module (skeleton tests)."""

from markdown_chunker.parser import core


class TestFencedBlockExtractor:
    """Test FencedBlockExtractor class (skeleton)."""

    def test_can_instantiate(self):
        """Test that FencedBlockExtractor can be instantiated."""
        extractor = core.FencedBlockExtractor()
        assert extractor is not None


class TestParserInterface:
    """Test ParserInterface class (skeleton)."""

    def test_can_instantiate(self):
        """Test that ParserInterface can be instantiated."""
        parser = core.ParserInterface()
        assert parser is not None


class TestConvenienceFunctions:
    """Test convenience functions (skeleton)."""

    def test_extract_fenced_blocks_exists(self):
        """Test that extract_fenced_blocks function exists."""
        assert hasattr(core, "extract_fenced_blocks")
        assert callable(core.extract_fenced_blocks)
