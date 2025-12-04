"""
Integration tests for the complete chunking pipeline.

These tests verify that the 3-stage pipeline works end-to-end:
1. Parser analyzes content
2. Strategy is selected and applied
3. Post-processing produces valid results
"""

import unittest

from markdown_chunker import ChunkConfig, MarkdownChunker, chunk_markdown


class TestChunkingIntegration(unittest.TestCase):
    """Integration tests for complete chunking workflow."""

    def test_simple_text_chunking(self):
        """Test chunking simple text uses fallback strategy."""
        text = """
        This is a simple paragraph of text.
        
        This is another paragraph.
        
        And a third paragraph here.
        """

        result = chunk_markdown(text)

        self.assertGreater(result.chunk_count, 0)
        self.assertEqual(result.strategy_used, "fallback")
        self.assertEqual(len(result.chunks), result.chunk_count)

    def test_code_heavy_chunking(self):
        """Test chunking code-heavy document uses code_aware strategy."""
        text = """
# Code Examples

Here's some code:

```python
def hello():
    return "world"
```

More code:

```javascript
function greet() {
    return "hello";
}
```
"""

        result = chunk_markdown(text)

        self.assertGreater(result.chunk_count, 0)
        self.assertEqual(result.strategy_used, "code_aware")
        self.assertGreater(result.metadata["code_block_count"], 0)

    def test_structured_chunking(self):
        """Test chunking structured document uses structural strategy."""
        text = """
# Main Title

Some introduction text here.

## Section 1

Content for section 1.

## Section 2

Content for section 2.

## Section 3

Content for section 3.

## Section 4

Content for section 4.
"""

        result = chunk_markdown(text)

        self.assertGreater(result.chunk_count, 0)
        self.assertEqual(result.strategy_used, "structural")
        self.assertGreaterEqual(result.metadata["header_count"], 3)

    def test_table_chunking(self):
        """Test chunking document with tables uses table strategy."""
        text = """
# Data Table

Here's a table:

| Name | Age | City |
|------|-----|------|
| John | 30  | NYC  |
| Jane | 25  | LA   |
| Bob  | 35  | SF   |

Some text after the table.
"""

        result = chunk_markdown(text)

        self.assertGreater(result.chunk_count, 0)
        self.assertEqual(result.strategy_used, "table")
        self.assertEqual(result.metadata["table_count"], 1)

    def test_custom_config(self):
        """Test chunking with custom configuration."""
        text = "# Title\n\n" + "Lorem ipsum dolor sit amet. " * 100

        config = ChunkConfig(max_chunk_size=500, min_chunk_size=100, overlap_size=50)

        chunker = MarkdownChunker(config)
        result = chunker.chunk(text)

        self.assertGreater(result.chunk_count, 0)

        # Verify chunks respect size constraints (mostly)
        for chunk in result.chunks:
            # Allow some variance due to atomic blocks
            if chunk.metadata.get("chunk_type") not in ("code", "table"):
                self.assertLessEqual(len(chunk.content), config.max_chunk_size * 1.1)

    def test_empty_input(self):
        """Test handling of empty input."""
        result = chunk_markdown("")

        self.assertEqual(result.chunk_count, 0)
        self.assertEqual(len(result.chunks), 0)
        self.assertEqual(result.strategy_used, "none")

    def test_chunk_metadata(self):
        """Test that chunks have proper metadata."""
        text = """
# Title

Some content here.

## Subsection

More content.
"""

        result = chunk_markdown(text)

        for i, chunk in enumerate(result.chunks):
            # Check metadata enrichment
            self.assertEqual(chunk.metadata["chunk_index"], i)
            self.assertEqual(chunk.metadata["total_chunks"], result.chunk_count)
            self.assertIn("strategy", chunk.metadata)

            # Check line numbers
            self.assertGreaterEqual(chunk.start_line, 1)
            self.assertGreaterEqual(chunk.end_line, chunk.start_line)

    def test_factory_configs(self):
        """Test factory configuration methods."""
        text = "# Test\n\n```python\ncode\n```\n\nText content."

        # Test RAG config
        rag_result = chunk_markdown(text, ChunkConfig.for_rag())
        self.assertGreater(rag_result.chunk_count, 0)

        # Test code docs config
        code_result = chunk_markdown(text, ChunkConfig.for_code_docs())
        self.assertGreater(code_result.chunk_count, 0)


if __name__ == "__main__":
    unittest.main()
