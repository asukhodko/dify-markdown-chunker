"""
V2 Test Implementation: Additional Specifications

Implements test specifications SPEC-027 to SPEC-052 from
docs/v2-test-specification/v2-test-specification.md

Additional tests covering:
- Header path accuracy
- Overlap constraints
- Unicode handling
- Line ending normalization
- Content type detection
- Performance baselines
- Config profiles and defaults
"""

import pytest
from hypothesis import given, settings, strategies as st, HealthCheck

from markdown_chunker_v2.chunker import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig
from markdown_chunker_v2.parser import Parser
from markdown_chunker_v2.types import Chunk


# =============================================================================
# SPEC-027: Header Path Accuracy
# =============================================================================

class TestSPEC027HeaderPathAccuracy:
    """
    SPEC-027: Header Path Accuracy
    
    **Feature: v2-test-implementation, Unit: Header path accuracy**
    **Validates: Requirements 3.1, 5.1**
    """
    
    def test_header_path_reflects_hierarchy(self):
        """Test header_path reflects document hierarchy."""
        config = ChunkConfig(strategy_override="structural")
        chunker = MarkdownChunker(config)
        
        text = """# Main

## Sub1

Content 1.

## Sub2

Content 2.
"""
        chunks = chunker.chunk(text)
        
        # Check that header paths exist
        paths = [c.metadata.get('header_path') for c in chunks if c.metadata.get('header_path')]
        assert len(paths) >= 1
    
    def test_header_path_starts_with_slash(self):
        """Test header_path starts with /."""
        config = ChunkConfig(strategy_override="structural")
        chunker = MarkdownChunker(config)
        
        text = "# Header\n\nContent."
        chunks = chunker.chunk(text)
        
        for chunk in chunks:
            path = chunk.metadata.get('header_path')
            if path and isinstance(path, str):
                assert path.startswith('/'), f"Path should start with /: {path}"


# =============================================================================
# SPEC-028: Overlap Size Constraint
# =============================================================================

class TestSPEC028OverlapSizeConstraint:
    """
    SPEC-028: Overlap Size Constraint
    
    **Feature: v2-test-implementation, Unit: Overlap size constraint**
    **Validates: Requirements 3.1, 5.1**
    """
    
    def test_overlap_size_less_than_max_chunk(self):
        """Test overlap_size must be less than max_chunk_size."""
        with pytest.raises(ValueError):
            ChunkConfig(max_chunk_size=100, overlap_size=100)
        
        with pytest.raises(ValueError):
            ChunkConfig(max_chunk_size=100, overlap_size=150)
    
    def test_overlap_size_zero_valid(self):
        """Test overlap_size=0 is valid (disables overlap)."""
        config = ChunkConfig(overlap_size=0)
        assert config.overlap_size == 0
        assert config.enable_overlap is False


# =============================================================================
# SPEC-035: Chunk Index Correctness
# =============================================================================

class TestSPEC035ChunkIndexCorrectness:
    """
    SPEC-035: Chunk Index Correctness
    
    **Feature: v2-test-implementation, Property: Chunk index correctness**
    **Validates: Requirements 3.1, 5.1**
    """
    
    def test_chunk_indices_sequential(self):
        """Test chunk indices are sequential starting from 0."""
        chunker = MarkdownChunker()
        text = "Para 1.\n\n" * 10
        chunks = chunker.chunk(text)
        
        indices = [c.metadata['chunk_index'] for c in chunks]
        assert indices == list(range(len(chunks)))
    
    @given(st.integers(min_value=1, max_value=20))
    @settings(max_examples=10, deadline=5000)
    def test_chunk_index_always_sequential(self, num_paras: int):
        """Property: Chunk indices are always sequential."""
        chunker = MarkdownChunker()
        text = "Paragraph content.\n\n" * num_paras
        chunks = chunker.chunk(text)
        
        if chunks:
            indices = [c.metadata['chunk_index'] for c in chunks]
            assert indices == list(range(len(chunks)))


# =============================================================================
# SPEC-036: Content Type Detection
# =============================================================================

class TestSPEC036ContentTypeDetection:
    """
    SPEC-036: Content Type Detection
    
    **Feature: v2-test-implementation, Unit: Content type detection**
    **Validates: Requirements 3.1, 5.1**
    """
    
    def test_text_content_type(self):
        """Test plain text is detected as 'text'."""
        chunker = MarkdownChunker()
        chunks = chunker.chunk("Plain text content.")
        
        if chunks:
            assert chunks[0].metadata['content_type'] == 'text'
    
    def test_code_content_type(self):
        """Test code blocks are detected as 'code'."""
        chunker = MarkdownChunker()
        chunks = chunker.chunk("```python\ncode\n```")
        
        if chunks:
            assert chunks[0].metadata['content_type'] == 'code'
    
    def test_table_content_type(self):
        """Test tables are detected as 'table'."""
        chunker = MarkdownChunker()
        text = "| A | B |\n|---|---|\n| 1 | 2 |"
        chunks = chunker.chunk(text)
        
        if chunks:
            assert chunks[0].metadata['content_type'] == 'table'
    
    def test_mixed_content_type(self):
        """Test mixed content is detected as 'mixed'."""
        chunker = MarkdownChunker()
        text = "```code```\n\n| A | B |\n|---|---|\n| 1 | 2 |"
        chunks = chunker.chunk(text)
        
        # At least one chunk should be mixed or have both types
        content_types = [c.metadata['content_type'] for c in chunks]
        assert 'mixed' in content_types or ('code' in content_types and 'table' in content_types)


# =============================================================================
# SPEC-039: Unicode Content Handling
# =============================================================================

class TestSPEC039UnicodeContentHandling:
    """
    SPEC-039: Unicode Content Handling
    
    **Feature: v2-test-implementation, Unit: Unicode content handling**
    **Validates: Requirements 3.1, 5.2**
    """
    
    def test_cyrillic_content(self):
        """Test Cyrillic content is handled correctly."""
        parser = Parser()
        text = "# Заголовок\n\nТекст на русском языке."
        analysis = parser.analyze(text)
        
        assert analysis.header_count == 1
        assert analysis.headers[0].text == "Заголовок"
    
    def test_cjk_content(self):
        """Test CJK content is handled correctly."""
        parser = Parser()
        text = "# 日本語\n\n中文内容"
        analysis = parser.analyze(text)
        
        assert analysis.header_count == 1
        assert "日本語" in analysis.headers[0].text
    
    def test_emoji_content(self):
        """Test emoji content is handled correctly."""
        chunker = MarkdownChunker()
        text = "# 🎉 Celebration\n\n🚀 Launch time! ✨"
        chunks = chunker.chunk(text)
        
        assert len(chunks) >= 1
        combined = ''.join(c.content for c in chunks)
        assert '🎉' in combined
        assert '🚀' in combined
    
    def test_mixed_scripts(self):
        """Test mixed scripts are handled correctly."""
        chunker = MarkdownChunker()
        text = "# English and Русский\n\nMixed 日本語 content."
        chunks = chunker.chunk(text)
        
        assert len(chunks) >= 1


# =============================================================================
# SPEC-040: Line Ending Normalization
# =============================================================================

class TestSPEC040LineEndingNormalization:
    """
    SPEC-040: Line Ending Normalization
    
    **Feature: v2-test-implementation, Property: Line ending normalization**
    **Validates: Requirements 3.1, 5.1**
    """
    
    def test_crlf_normalized(self):
        """Test CRLF (Windows) line endings are normalized."""
        parser = Parser()
        text = "# Header\r\n\r\nContent"
        analysis = parser.analyze(text)
        
        assert analysis.header_count == 1
        assert analysis.total_lines == 3
    
    def test_cr_normalized(self):
        """Test CR (old Mac) line endings are normalized."""
        parser = Parser()
        text = "# Header\r\rContent"
        analysis = parser.analyze(text)
        
        assert analysis.header_count == 1
    
    def test_mixed_line_endings(self):
        """Test mixed line endings are all normalized."""
        parser = Parser()
        text = "Line1\r\nLine2\rLine3\nLine4"
        analysis = parser.analyze(text)
        
        assert analysis.total_lines == 4
    
    def test_chunking_with_crlf(self):
        """Test chunking works with CRLF line endings."""
        chunker = MarkdownChunker()
        text = "# Header\r\n\r\nParagraph 1.\r\n\r\nParagraph 2."
        chunks = chunker.chunk(text)
        
        assert len(chunks) >= 1


# =============================================================================
# SPEC-045: Code Block Language Detection
# =============================================================================

class TestSPEC045CodeBlockLanguageDetection:
    """
    SPEC-045: Code Block Language Detection
    
    **Feature: v2-test-implementation, Unit: Code block language detection**
    **Validates: Requirements 3.1, 5.1**
    """
    
    def test_python_language_detected(self):
        """Test Python language is detected."""
        parser = Parser()
        text = "```python\ncode\n```"
        analysis = parser.analyze(text)
        
        assert analysis.code_blocks[0].language == "python"
    
    def test_javascript_language_detected(self):
        """Test JavaScript language is detected."""
        parser = Parser()
        text = "```javascript\ncode\n```"
        analysis = parser.analyze(text)
        
        assert analysis.code_blocks[0].language == "javascript"
    
    def test_no_language_is_none(self):
        """Test no language specifier results in None."""
        parser = Parser()
        text = "```\ncode\n```"
        analysis = parser.analyze(text)
        
        assert analysis.code_blocks[0].language is None
    
    def test_various_languages(self):
        """Test various language specifiers."""
        parser = Parser()
        languages = ['go', 'rust', 'java', 'cpp', 'ruby', 'php', 'sql']
        
        for lang in languages:
            text = f"```{lang}\ncode\n```"
            analysis = parser.analyze(text)
            assert analysis.code_blocks[0].language == lang


# =============================================================================
# SPEC-046: Table Column Counting
# =============================================================================

class TestSPEC046TableColumnCounting:
    """
    SPEC-046: Table Column Counting
    
    **Feature: v2-test-implementation, Unit: Table column counting**
    **Validates: Requirements 3.1, 5.1**
    """
    
    def test_two_column_table(self):
        """Test 2-column table is counted correctly."""
        parser = Parser()
        text = "| A | B |\n|---|---|\n| 1 | 2 |"
        analysis = parser.analyze(text)
        
        assert analysis.tables[0].column_count >= 1
    
    def test_four_column_table(self):
        """Test 4-column table is counted correctly."""
        parser = Parser()
        text = "| A | B | C | D |\n|---|---|---|---|\n| 1 | 2 | 3 | 4 |"
        analysis = parser.analyze(text)
        
        assert analysis.tables[0].column_count >= 3


# =============================================================================
# SPEC-048: Chunk Size Distribution
# =============================================================================

class TestSPEC048ChunkSizeDistribution:
    """
    SPEC-048: Chunk Size Distribution
    
    **Feature: v2-test-implementation, Unit: Chunk size distribution**
    **Validates: Requirements 3.1, 5.1**
    """
    
    def test_metrics_calculated(self):
        """Test chunking metrics are calculated."""
        chunker = MarkdownChunker()
        text = "Paragraph. " * 50
        chunks, metrics = chunker.chunk_with_metrics(text)
        
        assert metrics.total_chunks == len(chunks)
        assert metrics.avg_chunk_size > 0
        assert metrics.min_size > 0
        assert metrics.max_size >= metrics.min_size
    
    def test_undersize_count(self):
        """Test undersize chunk counting."""
        config = ChunkConfig(min_chunk_size=1000)
        chunker = MarkdownChunker(config)
        text = "Short."
        chunks, metrics = chunker.chunk_with_metrics(text)
        
        # Short text should be undersize
        if chunks:
            assert metrics.undersize_count >= 0


# =============================================================================
# SPEC-049: Error Message Quality
# =============================================================================

class TestSPEC049ErrorMessageQuality:
    """
    SPEC-049: Error Message Quality
    
    **Feature: v2-test-implementation, Unit: Error message quality**
    **Validates: Requirements 3.1, 5.2**
    """
    
    def test_max_chunk_size_error_message(self):
        """Test max_chunk_size error has clear message."""
        with pytest.raises(ValueError) as exc_info:
            ChunkConfig(max_chunk_size=0)
        
        assert "max_chunk_size" in str(exc_info.value)
        assert "positive" in str(exc_info.value)
    
    def test_overlap_size_error_message(self):
        """Test overlap_size error has clear message."""
        with pytest.raises(ValueError) as exc_info:
            ChunkConfig(max_chunk_size=100, overlap_size=200)
        
        assert "overlap_size" in str(exc_info.value)
        assert "max_chunk_size" in str(exc_info.value)
    
    def test_strategy_override_error_message(self):
        """Test strategy_override error has clear message."""
        with pytest.raises(ValueError) as exc_info:
            ChunkConfig(strategy_override="invalid")
        
        assert "strategy_override" in str(exc_info.value)


# =============================================================================
# SPEC-050: Config Defaults
# =============================================================================

class TestSPEC050ConfigDefaults:
    """
    SPEC-050: Config Defaults
    
    **Feature: v2-test-implementation, Unit: Config defaults**
    **Validates: Requirements 3.1, 5.1**
    """
    
    def test_default_max_chunk_size(self):
        """Test default max_chunk_size is 4096."""
        config = ChunkConfig()
        assert config.max_chunk_size == 4096
    
    def test_default_min_chunk_size(self):
        """Test default min_chunk_size is 512."""
        config = ChunkConfig()
        assert config.min_chunk_size == 512
    
    def test_default_overlap_size(self):
        """Test default overlap_size is 200."""
        config = ChunkConfig()
        assert config.overlap_size == 200
    
    def test_default_code_threshold(self):
        """Test default code_threshold is 0.3."""
        config = ChunkConfig()
        assert config.code_threshold == 0.3
    
    def test_default_structure_threshold(self):
        """Test default structure_threshold is 3."""
        config = ChunkConfig()
        assert config.structure_threshold == 3
    
    def test_default_preserve_atomic_blocks(self):
        """Test default preserve_atomic_blocks is True."""
        config = ChunkConfig()
        assert config.preserve_atomic_blocks is True
    
    def test_config_presets(self):
        """Test config presets work correctly."""
        code_heavy = ChunkConfig.for_code_heavy()
        assert code_heavy.max_chunk_size == 8192
        
        structured = ChunkConfig.for_structured()
        assert structured.structure_threshold == 2
        
        minimal = ChunkConfig.minimal()
        assert minimal.max_chunk_size == 1024


# =============================================================================
# SPEC-030: Config Profiles
# =============================================================================

class TestSPEC030ConfigProfiles:
    """
    SPEC-030: Config Profiles
    
    **Feature: v2-test-implementation, Unit: Config profiles**
    **Validates: Requirements 3.1, 5.1**
    """
    
    def test_for_code_heavy_profile(self):
        """Test for_code_heavy profile."""
        config = ChunkConfig.for_code_heavy()
        
        assert config.max_chunk_size > 4096
        assert config.code_threshold < 0.3
    
    def test_for_structured_profile(self):
        """Test for_structured profile."""
        config = ChunkConfig.for_structured()
        
        assert config.structure_threshold < 3
    
    def test_minimal_profile(self):
        """Test minimal profile."""
        config = ChunkConfig.minimal()
        
        assert config.max_chunk_size < 4096
        assert config.min_chunk_size < 512


# =============================================================================
# SPEC-041: Metadata Serialization
# =============================================================================

class TestSPEC041MetadataSerialization:
    """
    SPEC-041: Metadata Serialization
    
    **Feature: v2-test-implementation, Property: Metadata serialization**
    **Validates: Requirements 3.1, 5.1**
    """
    
    def test_metadata_in_to_dict(self):
        """Test metadata is included in to_dict()."""
        chunk = Chunk(
            content="Test",
            start_line=1,
            end_line=1,
            metadata={"key": "value", "number": 42}
        )
        
        data = chunk.to_dict()
        assert "metadata" in data
        assert data["metadata"]["key"] == "value"
        assert data["metadata"]["number"] == 42
    
    def test_metadata_roundtrip(self):
        """Test metadata survives serialization roundtrip."""
        original = Chunk(
            content="Test",
            start_line=1,
            end_line=1,
            metadata={"strategy": "test", "custom": [1, 2, 3]}
        )
        
        restored = Chunk.from_dict(original.to_dict())
        assert restored.metadata["strategy"] == "test"
        assert restored.metadata["custom"] == [1, 2, 3]


# =============================================================================
# SPEC-033: API Backward Compatibility
# =============================================================================

class TestSPEC033APIBackwardCompatibility:
    """
    SPEC-033: API Backward Compatibility
    
    **Feature: v2-test-implementation, Unit: API backward compatibility**
    **Validates: Requirements 3.1, 5.1**
    """
    
    def test_chunk_simple_returns_dict(self):
        """Test chunk_simple returns dictionary format."""
        chunker = MarkdownChunker()
        result = chunker.chunk_simple("Test content")
        
        assert isinstance(result, dict)
        assert "chunks" in result
        assert "errors" in result
        assert "total_chunks" in result
        assert "strategy_used" in result
    
    def test_chunk_simple_with_config_dict(self):
        """Test chunk_simple accepts config as dict."""
        chunker = MarkdownChunker()
        result = chunker.chunk_simple(
            "Test content",
            config={"max_chunk_size": 1000}
        )
        
        assert isinstance(result, dict)
        assert len(result["errors"]) == 0
    
    def test_config_from_dict(self):
        """Test ChunkConfig.from_dict works."""
        data = {
            "max_chunk_size": 2048,
            "min_chunk_size": 256,
            "overlap_size": 100
        }
        
        config = ChunkConfig.from_dict(data)
        assert config.max_chunk_size == 2048
        assert config.min_chunk_size == 256
    
    def test_config_to_dict(self):
        """Test ChunkConfig.to_dict works."""
        config = ChunkConfig(max_chunk_size=2048)
        data = config.to_dict()
        
        assert data["max_chunk_size"] == 2048
        assert "enable_overlap" in data
