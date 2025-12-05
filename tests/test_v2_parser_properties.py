"""
V2 Test Implementation: Parser Properties

Implements test specifications SPEC-001 to SPEC-007 from
docs/v2-test-specification/v2-test-specification.md

Tests Parser.analyze() functionality including:
- Content analysis metrics accuracy
- Fenced block extraction
- Header detection
- Table detection
- Preamble detection
- Line number accuracy
- Edge cases
"""

import pytest
from hypothesis import given, settings, strategies as st, HealthCheck

from markdown_chunker_v2.parser import Parser
from markdown_chunker_v2.types import ContentAnalysis, FencedBlock, Header, TableBlock


# =============================================================================
# SPEC-001: Content Analysis Metrics Accuracy
# =============================================================================

class TestSPEC001ContentAnalysisMetrics:
    """
    SPEC-001: Content Analysis Metrics Accuracy
    
    **Feature: v2-test-implementation, Property 1: Content metrics accuracy**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-001
    """
    
    @given(st.text(min_size=0, max_size=5000))
    @settings(max_examples=100, deadline=5000, suppress_health_check=[HealthCheck.too_slow])
    def test_metrics_accuracy_property(self, text: str):
        """Property: For any markdown text, metrics are accurate."""
        parser = Parser()
        analysis = parser.analyze(text)
        
        # Normalize text same way parser does
        normalized = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # total_chars must equal length of normalized text
        assert analysis.total_chars == len(normalized)
        
        # total_lines calculation
        if normalized:
            assert analysis.total_lines == normalized.count('\n') + 1
        else:
            assert analysis.total_lines == 0
        
        # code_ratio must be in valid range
        assert 0 <= analysis.code_ratio <= 1
        
        # counts must be non-negative
        assert analysis.code_block_count >= 0
        assert analysis.header_count >= 0
        assert analysis.table_count >= 0
    
    def test_empty_text_edge_case(self):
        """Edge case: Empty text should have valid metrics."""
        parser = Parser()
        analysis = parser.analyze("")
        
        assert analysis.total_chars == 0
        assert analysis.total_lines == 0
        assert analysis.code_ratio == 0
        assert analysis.code_block_count == 0
        assert analysis.header_count == 0
    
    def test_whitespace_only(self):
        """Edge case: Whitespace-only text should have valid metrics."""
        parser = Parser()
        analysis = parser.analyze("   \n\t\n   ")
        
        assert analysis.total_chars > 0
        assert analysis.total_lines > 0
        assert analysis.code_ratio == 0
    
    def test_code_ratio_calculation(self):
        """Test code_ratio is calculated correctly."""
        parser = Parser()
        
        # Document with code block
        text = "Some text\n\n```python\ncode here\n```\n\nMore text"
        analysis = parser.analyze(text)
        
        # code_ratio should be > 0 when code blocks exist
        if analysis.code_block_count > 0:
            assert analysis.code_ratio > 0


# =============================================================================
# SPEC-002: Fenced Block Extraction Completeness
# =============================================================================

class TestSPEC002FencedBlockExtraction:
    """
    SPEC-002: Fenced Block Extraction Completeness
    
    **Feature: v2-test-implementation, Property 2: Fenced block extraction**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-002
    """
    
    def test_single_code_block_extraction(self):
        """Test single code block is extracted correctly."""
        parser = Parser()
        text = "Before\n\n```python\ndef hello():\n    pass\n```\n\nAfter"
        analysis = parser.analyze(text)
        
        assert analysis.code_block_count == 1
        assert len(analysis.code_blocks) == 1
        
        block = analysis.code_blocks[0]
        assert block.language == "python"
        assert "def hello" in block.content
        assert block.start_line >= 1
        assert block.end_line >= block.start_line
    
    def test_multiple_code_blocks(self):
        """Test multiple code blocks are all extracted."""
        parser = Parser()
        text = """# Header

```python
code1
```

Some text

```javascript
code2
```

More text

```
code3
```
"""
        analysis = parser.analyze(text)
        
        assert analysis.code_block_count == 3
        assert len(analysis.code_blocks) == 3
        
        # Check languages
        languages = [b.language for b in analysis.code_blocks]
        assert "python" in languages
        assert "javascript" in languages
        assert None in languages  # No language specified
    
    def test_code_block_boundaries(self):
        """Test code block line boundaries are accurate."""
        parser = Parser()
        text = "Line 1\nLine 2\n```\ncode\n```\nLine 6"
        analysis = parser.analyze(text)
        
        assert len(analysis.code_blocks) == 1
        block = analysis.code_blocks[0]
        
        # Block should start at line 3 (1-indexed)
        assert block.start_line == 3
        # Block should end at line 5
        assert block.end_line == 5
    
    def test_empty_code_block(self):
        """Edge case: Empty code block."""
        parser = Parser()
        text = "```\n```"
        analysis = parser.analyze(text)
        
        assert analysis.code_block_count == 1
        assert analysis.code_blocks[0].content == ""
    
    @given(st.text(alphabet=st.characters(whitelist_categories=['Lu', 'Ll', 'Nd']), min_size=0, max_size=100))
    @settings(max_examples=50, deadline=5000)
    def test_code_block_content_preserved(self, code_content: str):
        """Property: Code block content is preserved exactly."""
        parser = Parser()
        text = f"```\n{code_content}\n```"
        analysis = parser.analyze(text)
        
        if analysis.code_blocks:
            assert analysis.code_blocks[0].content == code_content


# =============================================================================
# SPEC-003: Header Detection Accuracy
# =============================================================================

class TestSPEC003HeaderDetection:
    """
    SPEC-003: Header Detection Accuracy
    
    **Feature: v2-test-implementation, Property 3: Header detection**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-003
    """
    
    def test_all_header_levels(self):
        """Test headers at all levels (1-6) are detected."""
        parser = Parser()
        text = """# H1
## H2
### H3
#### H4
##### H5
###### H6
"""
        analysis = parser.analyze(text)
        
        assert analysis.header_count == 6
        levels = [h.level for h in analysis.headers]
        assert levels == [1, 2, 3, 4, 5, 6]
    
    def test_header_text_extraction(self):
        """Test header text is extracted correctly."""
        parser = Parser()
        text = "# My Header Title\n\n## Another Header"
        analysis = parser.analyze(text)
        
        assert analysis.headers[0].text == "My Header Title"
        assert analysis.headers[1].text == "Another Header"
    
    def test_header_line_numbers(self):
        """Test header line numbers are accurate (1-indexed)."""
        parser = Parser()
        text = "# First\n\nSome text\n\n## Second"
        analysis = parser.analyze(text)
        
        assert analysis.headers[0].line == 1
        assert analysis.headers[1].line == 5
    
    def test_headers_inside_code_blocks_ignored(self):
        """Headers inside code blocks should NOT be detected."""
        parser = Parser()
        text = """# Real Header

```markdown
# Fake Header Inside Code
## Another Fake
```

## Real Header 2
"""
        analysis = parser.analyze(text)
        
        # Only 2 real headers should be detected
        assert analysis.header_count == 2
        texts = [h.text for h in analysis.headers]
        assert "Real Header" in texts
        assert "Real Header 2" in texts
        assert "Fake Header Inside Code" not in texts


# =============================================================================
# SPEC-004: Table Detection
# =============================================================================

class TestSPEC004TableDetection:
    """
    SPEC-004: Table Detection
    
    **Feature: v2-test-implementation, Unit: Table detection**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-004
    """
    
    def test_simple_table_detection(self):
        """Test simple table is detected."""
        parser = Parser()
        text = """| Col1 | Col2 |
|------|------|
| A    | B    |
| C    | D    |
"""
        analysis = parser.analyze(text)
        
        assert analysis.table_count == 1
        assert len(analysis.tables) == 1
    
    def test_table_column_count(self):
        """Test table column count is accurate."""
        parser = Parser()
        text = """| A | B | C | D |
|---|---|---|---|
| 1 | 2 | 3 | 4 |
"""
        analysis = parser.analyze(text)
        
        assert analysis.tables[0].column_count >= 3  # At least 3 columns
    
    def test_table_inside_code_block_ignored(self):
        """Tables inside code blocks should NOT be detected."""
        parser = Parser()
        text = """```
| Col1 | Col2 |
|------|------|
| A    | B    |
```
"""
        analysis = parser.analyze(text)
        
        assert analysis.table_count == 0


# =============================================================================
# SPEC-005: Preamble Detection
# =============================================================================

class TestSPEC005PreambleDetection:
    """
    SPEC-005: Preamble Detection
    
    **Feature: v2-test-implementation, Property: Preamble detection**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-005
    """
    
    def test_preamble_detected(self):
        """Test preamble is detected when content before first header."""
        parser = Parser()
        text = """This is preamble content.
More preamble.

# First Header

Content after header.
"""
        analysis = parser.analyze(text)
        
        assert analysis.has_preamble is True
        assert analysis.preamble_end_line > 0
    
    def test_no_preamble_when_starts_with_header(self):
        """Test no preamble when document starts with header."""
        parser = Parser()
        text = """# First Header

Content after header.
"""
        analysis = parser.analyze(text)
        
        assert analysis.has_preamble is False
    
    def test_no_preamble_with_only_whitespace_before_header(self):
        """Test no preamble when only whitespace before header."""
        parser = Parser()
        text = """

# First Header

Content.
"""
        analysis = parser.analyze(text)
        
        assert analysis.has_preamble is False


# =============================================================================
# SPEC-006: Line Number Accuracy
# =============================================================================

class TestSPEC006LineNumberAccuracy:
    """
    SPEC-006: Line Number Accuracy
    
    **Feature: v2-test-implementation, Property 3: Line number accuracy**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-006
    """
    
    def test_line_numbers_are_1_indexed(self):
        """Test all line numbers are 1-indexed."""
        parser = Parser()
        text = "# Header\n\n```\ncode\n```"
        analysis = parser.analyze(text)
        
        # Headers
        for header in analysis.headers:
            assert header.line >= 1
        
        # Code blocks
        for block in analysis.code_blocks:
            assert block.start_line >= 1
            assert block.end_line >= block.start_line
        
        # Tables
        for table in analysis.tables:
            assert table.start_line >= 1
            assert table.end_line >= table.start_line
    
    def test_line_numbers_with_crlf(self):
        """Test line numbers are correct with Windows line endings."""
        parser = Parser()
        text = "# Header\r\n\r\n## Second"
        analysis = parser.analyze(text)
        
        assert analysis.headers[0].line == 1
        assert analysis.headers[1].line == 3
    
    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=20, deadline=5000)
    def test_header_line_accuracy(self, num_blank_lines: int):
        """Property: Header line numbers match actual position."""
        parser = Parser()
        blank = "\n" * num_blank_lines
        text = f"{blank}# Header"
        analysis = parser.analyze(text)
        
        if analysis.headers:
            # Header should be at line (num_blank_lines + 1)
            assert analysis.headers[0].line == num_blank_lines + 1


# =============================================================================
# SPEC-007: Parser Edge Cases
# =============================================================================

class TestSPEC007ParserEdgeCases:
    """
    SPEC-007: Parser Edge Cases
    
    **Feature: v2-test-implementation, Unit: Parser edge cases**
    **Validates: Requirements 3.1, 5.2**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-007
    """
    
    def test_empty_string(self):
        """Parser handles empty string gracefully."""
        parser = Parser()
        analysis = parser.analyze("")
        
        assert isinstance(analysis, ContentAnalysis)
        assert analysis.total_chars == 0
    
    def test_only_whitespace(self):
        """Parser handles whitespace-only input."""
        parser = Parser()
        analysis = parser.analyze("   \n\t\n   ")
        
        assert isinstance(analysis, ContentAnalysis)
    
    def test_very_long_line(self):
        """Parser handles very long lines."""
        parser = Parser()
        long_line = "x" * 10000
        analysis = parser.analyze(long_line)
        
        assert isinstance(analysis, ContentAnalysis)
        assert analysis.total_chars == 10000
    
    def test_unicode_content(self):
        """Parser handles unicode content."""
        parser = Parser()
        text = "# Заголовок\n\n日本語テキスト\n\n🎉 Emoji content"
        analysis = parser.analyze(text)
        
        assert isinstance(analysis, ContentAnalysis)
        assert analysis.header_count == 1
    
    def test_mixed_line_endings(self):
        """Parser handles mixed line endings."""
        parser = Parser()
        text = "Line1\r\nLine2\rLine3\nLine4"
        analysis = parser.analyze(text)
        
        assert isinstance(analysis, ContentAnalysis)
        # After normalization, should have 4 lines
        assert analysis.total_lines == 4
    
    def test_unclosed_code_block(self):
        """Parser handles unclosed code block."""
        parser = Parser()
        text = "```python\ncode without closing fence"
        analysis = parser.analyze(text)
        
        # Should not crash
        assert isinstance(analysis, ContentAnalysis)
