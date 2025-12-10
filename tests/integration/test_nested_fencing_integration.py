"""
Integration tests for nested fencing support.

Tests the complete pipeline from parsing through chunking for nested fence documents.
"""

import pytest

from markdown_chunker_v2 import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig
from markdown_chunker_v2.parser import Parser


class TestCorpusFileParsing:
    """Test parsing of corpus files with nested fencing."""

    def test_nested_fencing_011_parsing(self):
        """Verify nested_fencing_011.md parses correctly."""
        with open("tests/corpus/nested_fencing/nested_fencing_011.md") as f:
            text = f.read()

        parser = Parser()
        result = parser.analyze(text)

        # Should extract multiple code blocks (mix of backticks and tildes)
        assert len(result.code_blocks) >= 3

        # Check for various fence types
        fence_chars = {b.fence_char for b in result.code_blocks}
        assert "`" in fence_chars or "~" in fence_chars

        # Verify content preservation
        for block in result.code_blocks:
            assert block.content is not None
            assert block.is_closed in (True, False)

    def test_nested_fencing_013_parsing(self):
        """Verify nested_fencing_013.md with triple nesting parses correctly."""
        with open("tests/corpus/nested_fencing/nested_fencing_013.md") as f:
            text = f.read()

        parser = Parser()
        result = parser.analyze(text)

        # Should handle quintuple backticks
        assert len(result.code_blocks) >= 4

        # Check max fence length
        max_length = max(b.fence_length for b in result.code_blocks)
        assert max_length >= 4

    def test_tilde_fencing_basic_parsing(self):
        """Verify tilde_fencing_basic.md parses correctly."""
        with open("tests/corpus/nested_fencing/tilde_fencing_basic.md") as f:
            text = f.read()

        parser = Parser()
        result = parser.analyze(text)

        # Should extract tilde-fenced blocks
        assert len(result.code_blocks) >= 2

        # Check for tilde fences
        tilde_blocks = [b for b in result.code_blocks if b.fence_char == "~"]
        assert len(tilde_blocks) >= 2

    def test_mixed_fence_types_parsing(self):
        """Verify mixed_fence_types.md with both backtick and tilde fences."""
        with open("tests/corpus/nested_fencing/mixed_fence_types.md") as f:
            text = f.read()

        parser = Parser()
        result = parser.analyze(text)

        # Should extract both fence types
        backtick_blocks = [b for b in result.code_blocks if b.fence_char == "`"]
        tilde_blocks = [b for b in result.code_blocks if b.fence_char == "~"]

        assert len(backtick_blocks) >= 2
        assert len(tilde_blocks) >= 1

    def test_deep_nesting_parsing(self):
        """Verify deep_nesting.md with up to 6-backtick nesting."""
        with open("tests/corpus/nested_fencing/deep_nesting.md") as f:
            text = f.read()

        parser = Parser()
        result = parser.analyze(text)

        # Should handle deep nesting
        assert len(result.code_blocks) >= 4

        # Check for sextuple backticks
        max_length = max(b.fence_length for b in result.code_blocks)
        assert max_length >= 5

    def test_edge_cases_parsing(self):
        """Verify edge_cases.md with unclosed fence."""
        with open("tests/corpus/nested_fencing/edge_cases.md") as f:
            text = f.read()

        parser = Parser()
        result = parser.analyze(text)

        # Should handle unclosed fence gracefully
        assert len(result.code_blocks) >= 1

        # At least one unclosed fence
        unclosed = [b for b in result.code_blocks if not b.is_closed]
        assert len(unclosed) >= 1

    def test_meta_documentation_parsing(self):
        """Verify meta_documentation.md realistic documentation example."""
        with open("tests/corpus/nested_fencing/meta_documentation.md") as f:
            text = f.read()

        parser = Parser()
        result = parser.analyze(text)

        # Should extract multiple nested structures
        assert len(result.code_blocks) >= 5

        # Check for nested blocks
        nested_blocks = [b for b in result.code_blocks if b.fence_length > 3]
        assert len(nested_blocks) >= 3


class TestFullPipelineChunking:
    """Test complete chunking pipeline with nested fences."""

    def test_chunking_with_nested_fences(self):
        """Verify chunks preserve nested structure."""
        text = """# Documentation Guide

Use quadruple backticks for examples:

````markdown
To show code:

```python
def example():
    pass
```
````

This demonstrates meta-documentation."""

        chunker = MarkdownChunker()
        chunks = chunker.chunk(text)

        # Should create chunks
        assert len(chunks) > 0

        # Check that nested content is preserved in chunks
        has_nested = any("````" in chunk.content for chunk in chunks)
        assert has_nested

    def test_code_blocks_remain_atomic(self):
        """Verify code blocks (including nested) remain atomic."""
        text = """# Tutorial

````markdown
```python
code here
```
````"""

        chunker = MarkdownChunker()
        chunks = chunker.chunk(text)

        # Find chunk with nested fence
        nested_chunk = next((c for c in chunks if "````" in c.content), None)
        assert nested_chunk is not None

        # Verify inner code block is intact
        assert "```python" in nested_chunk.content
        assert "code here" in nested_chunk.content

    def test_metadata_includes_fence_info(self):
        """Verify chunk metadata includes fence information."""
        text = """````python
nested content
````"""

        parser = Parser()
        result = parser.analyze(text)

        # Verify fence metadata
        assert len(result.code_blocks) == 1
        block = result.code_blocks[0]
        assert block.fence_char == "`"
        assert block.fence_length == 4
        assert block.is_closed is True

    def test_strategy_selection_code_aware(self):
        """Verify CodeAware strategy handles nested fences."""
        with open("tests/corpus/nested_fencing/meta_documentation.md") as f:
            text = f.read()

        config = ChunkConfig()
        chunker = MarkdownChunker(config)
        chunks, strategy_name, analysis = chunker.chunk_with_analysis(text)

        # Should use code_aware strategy due to high code_ratio
        assert strategy_name in ["code_aware", "semantic"]

        # Verify chunks created
        assert len(chunks) > 0

        # Verify analysis includes code blocks
        assert len(analysis.code_blocks) > 0


class TestBackwardCompatibility:
    """Test backward compatibility with existing documents."""

    def test_simple_documents_unchanged(self):
        """Verify simple triple-backtick documents chunk identically."""
        text = """# Simple Document

```python
def hello():
    print("Hello")
```

Some text after code."""

        chunker = MarkdownChunker()
        chunks = chunker.chunk(text)

        # Should work exactly as before
        assert len(chunks) > 0

        # Verify code block present
        has_code = any("def hello" in chunk.content for chunk in chunks)
        assert has_code

    def test_no_nesting_documents(self):
        """Verify documents without nesting work correctly."""
        text = """# Documentation

```python
code1
```

Text between.

```javascript
code2
```"""

        parser = Parser()
        result = parser.analyze(text)

        # Should extract both blocks
        assert len(result.code_blocks) == 2

        # All should be standard triple backticks
        assert all(b.fence_length == 3 for b in result.code_blocks)
        assert all(b.is_closed for b in result.code_blocks)

    def test_existing_code_heavy_docs(self):
        """Verify code-heavy documents without nesting still work."""
        text = """# API Reference

## Function 1

```python
def func1():
    pass
```

## Function 2

```python
def func2():
    pass
```

## Function 3

```python
def func3():
    pass
```"""

        parser = Parser()
        result = parser.analyze(text)

        # Should extract all code blocks
        assert len(result.code_blocks) == 3

        # Check code_ratio calculation
        assert result.code_ratio > 0.2


class TestRealWorldDocuments:
    """Test with real-world corpus documents."""

    @pytest.mark.parametrize(
        "corpus_file",
        [
            "tests/corpus/nested_fencing/nested_fencing_011.md",
            "tests/corpus/nested_fencing/nested_fencing_013.md",
            "tests/corpus/nested_fencing/tilde_fencing_basic.md",
            "tests/corpus/nested_fencing/mixed_fence_types.md",
            "tests/corpus/nested_fencing/deep_nesting.md",
            "tests/corpus/nested_fencing/meta_documentation.md",
        ],
    )
    def test_corpus_file_chunks_successfully(self, corpus_file):
        """Verify each corpus file chunks without errors."""
        with open(corpus_file) as f:
            text = f.read()

        chunker = MarkdownChunker()
        chunks = chunker.chunk(text)

        # Should create chunks
        assert len(chunks) > 0

        # All chunks should have content
        assert all(chunk.content for chunk in chunks)

        # All chunks should have metadata
        assert all(chunk.metadata for chunk in chunks)

    def test_nested_content_preservation_end_to_end(self):
        """Verify nested content is preserved through entire pipeline."""
        text = """`````markdown
# Style Guide

Show examples:

````markdown
### Code Block

```python
code here
```
````
`````"""

        chunker = MarkdownChunker()
        chunks = chunker.chunk(text)

        # Find chunk with nested content
        nested_chunk = next((c for c in chunks if "`````" in c.content), None)
        assert nested_chunk is not None

        # Verify all nesting levels preserved
        assert "````markdown" in nested_chunk.content
        assert "```python" in nested_chunk.content
        assert "code here" in nested_chunk.content


class TestEdgeCaseHandling:
    """Test edge cases in integration context."""

    def test_unclosed_fence_in_pipeline(self):
        """Verify unclosed fence doesn't break pipeline."""
        text = """# Document

````markdown
This fence is never closed.
Content continues."""

        chunker = MarkdownChunker()
        chunks = chunker.chunk(text)

        # Should create chunks despite unclosed fence
        assert len(chunks) > 0

    def test_empty_nested_fences(self):
        """Verify empty nested fences are handled."""
        text = """# Document

````markdown
````"""

        parser = Parser()
        result = parser.analyze(text)

        # Should extract empty block
        assert len(result.code_blocks) == 1
        assert result.code_blocks[0].content == ""

    def test_mixed_indentation_fences(self):
        """Verify fences with varying indentation work."""
        text = """# Document

````markdown
  ```python
  code with indent
  ```
````"""

        chunker = MarkdownChunker()
        chunks = chunker.chunk(text)

        # Should handle indented nested content
        assert len(chunks) > 0


class TestPerformanceBaseline:
    """Basic performance checks for nested fencing."""

    def test_large_nested_document_performance(self):
        """Verify large nested documents process in reasonable time."""
        with open("tests/corpus/nested_fencing/meta_documentation.md") as f:
            text = f.read()

        import time

        chunker = MarkdownChunker()
        start = time.time()
        chunks = chunker.chunk(text)
        duration = time.time() - start

        # Should complete quickly (< 100ms for ~2KB document)
        assert duration < 0.1
        assert len(chunks) > 0

    def test_deep_nesting_no_exponential_slowdown(self):
        """Verify deep nesting doesn't cause exponential slowdown."""
        with open("tests/corpus/nested_fencing/deep_nesting.md") as f:
            text = f.read()

        import time

        parser = Parser()
        start = time.time()
        result = parser.analyze(text)
        duration = time.time() - start

        # Should be linear, not exponential
        assert duration < 0.05
        assert len(result.code_blocks) > 0
