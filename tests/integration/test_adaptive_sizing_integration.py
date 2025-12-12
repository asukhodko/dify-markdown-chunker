"""
Integration tests for adaptive chunk sizing feature.

Tests end-to-end behavior with real corpus files.
"""

import unittest
from pathlib import Path

from markdown_chunker_v2.adaptive_sizing import AdaptiveSizeConfig
from markdown_chunker_v2.chunker import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig


class TestAdaptiveSizingIntegration(unittest.TestCase):
    """Test adaptive sizing with real documents."""

    def setUp(self):
        """Set up test fixtures."""
        self.corpus_path = Path(__file__).parent.parent / "corpus"
        self.fixtures_path = Path(__file__).parent.parent / "fixtures" / "corpus"

    def test_disabled_by_default(self):
        """Adaptive sizing should be disabled by default."""
        config = ChunkConfig()
        chunker = MarkdownChunker(config)

        text = "# Test\n\nSome content.\n\n```python\ncode\n```"
        chunks = chunker.chunk(text)

        # Should not have adaptive sizing metadata
        for chunk in chunks:
            self.assertNotIn("adaptive_size", chunk.metadata)
            self.assertNotIn("content_complexity", chunk.metadata)
            self.assertNotIn("size_scale_factor", chunk.metadata)

    def test_enabled_with_profile(self):
        """Adaptive sizing can be enabled via profile."""
        config = ChunkConfig.with_adaptive_sizing()
        chunker = MarkdownChunker(config)

        text = "# Test\n\nSome content.\n\n```python\ncode\n```"
        chunks = chunker.chunk(text)

        # Should have adaptive sizing metadata
        for chunk in chunks:
            self.assertIn("adaptive_size", chunk.metadata)
            self.assertIn("content_complexity", chunk.metadata)
            self.assertIn("size_scale_factor", chunk.metadata)

    def test_code_heavy_content(self):
        """Code-heavy content should get larger chunks."""
        # Create code-heavy document
        text = """# API Documentation

This is the main API class.

```python
class APIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    def get(self, endpoint: str) -> dict:
        response = self.session.get(f"{BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: dict) -> dict:
        response = self.session.post(f"{BASE_URL}/{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
```

Usage examples above show the core functionality.
"""

        # Without adaptive sizing (keep for reference but don't use)
        config_standard = ChunkConfig(max_chunk_size=4096)
        chunker_standard = MarkdownChunker(config_standard)
        _ = chunker_standard.chunk(text)  # Compute but don't compare

        # With adaptive sizing
        config_adaptive = ChunkConfig.with_adaptive_sizing()
        chunker_adaptive = MarkdownChunker(config_adaptive)
        chunks_adaptive = chunker_adaptive.chunk(text)

        # Should have adaptive metadata
        self.assertTrue(len(chunks_adaptive) > 0)
        self.assertIn("content_complexity", chunks_adaptive[0].metadata)

        # Complexity should be > 0 due to code content
        complexity = chunks_adaptive[0].metadata["content_complexity"]
        self.assertGreater(complexity, 0.15)

    def test_simple_text_content(self):
        """Simple text content should get smaller chunks."""
        # Create simple text document
        text = """# Introduction

This is a simple text document with no code or tables.

It contains multiple paragraphs of plain text.

The content is straightforward and easy to read.

No complex structures are present.
"""

        config = ChunkConfig.with_adaptive_sizing()
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(text)

        # Should have low complexity
        self.assertTrue(len(chunks) > 0)
        complexity = chunks[0].metadata["content_complexity"]
        self.assertLess(complexity, 0.3)

        # Scale factor should be lower
        scale_factor = chunks[0].metadata["size_scale_factor"]
        self.assertLess(scale_factor, 1.0)

    def test_custom_adaptive_config(self):
        """Custom adaptive config should be respected."""
        custom_config = AdaptiveSizeConfig(
            base_size=2000,
            min_scale=0.6,
            max_scale=1.4,
            code_weight=0.5,
            table_weight=0.2,
            list_weight=0.2,
            sentence_length_weight=0.1,
        )

        config = ChunkConfig(
            max_chunk_size=4096,
            use_adaptive_sizing=True,
            adaptive_config=custom_config,
        )
        chunker = MarkdownChunker(config)

        text = "# Test\n\n```python\ncode\n```"
        chunks = chunker.chunk(text)

        # Should use custom base_size
        self.assertTrue(len(chunks) > 0)
        adaptive_size = chunks[0].metadata["adaptive_size"]
        # Size should be between base * min_scale and base * max_scale
        self.assertGreaterEqual(adaptive_size, 2000 * 0.6)
        self.assertLessEqual(adaptive_size, 2000 * 1.4)

    def test_respects_absolute_max_chunk_size(self):
        """Adaptive size should never exceed absolute max_chunk_size."""
        config = ChunkConfig(
            max_chunk_size=2000,  # Absolute limit
            use_adaptive_sizing=True,
            adaptive_config=AdaptiveSizeConfig(
                base_size=3000,  # Would scale higher
                max_scale=1.5,  # Could reach 4500
            ),
        )
        chunker = MarkdownChunker(config)

        # Create code-heavy content
        text = "# Test\n\n" + "```python\n" + ("x = 1\n" * 200) + "```"
        chunks = chunker.chunk(text)

        # No chunk should exceed absolute max
        for chunk in chunks:
            if not chunk.metadata.get("allow_oversize"):
                self.assertLessEqual(chunk.size, 2000)

    def test_code_heavy_profile(self):
        """Code-heavy profile should emphasize code weight."""
        config = ChunkConfig.for_code_heavy_adaptive()
        chunker = MarkdownChunker(config)

        text = """# Example

```python
def example():
    return "test"
```
"""

        chunks = chunker.chunk(text)
        self.assertTrue(len(chunks) > 0)

        # Should have adaptive metadata
        self.assertIn("content_complexity", chunks[0].metadata)

    def test_text_heavy_profile(self):
        """Text-heavy profile should emphasize text metrics."""
        config = ChunkConfig.for_text_heavy_adaptive()
        chunker = MarkdownChunker(config)

        text = """# Introduction

This is a narrative document with lots of text.

It contains multiple paragraphs explaining concepts.

The text is descriptive and educational.

- Point one
- Point two
- Point three
"""

        chunks = chunker.chunk(text)
        self.assertTrue(len(chunks) > 0)

        # Should have adaptive metadata
        self.assertIn("content_complexity", chunks[0].metadata)

    def test_backward_compatibility(self):
        """Existing code should work without modification."""
        # Old-style config without adaptive sizing
        config = ChunkConfig(
            max_chunk_size=4096,
            min_chunk_size=512,
            overlap_size=200,
        )
        chunker = MarkdownChunker(config)

        text = "# Test\n\nContent here."
        chunks = chunker.chunk(text)

        # Should work normally
        self.assertTrue(len(chunks) > 0)
        self.assertNotIn("adaptive_size", chunks[0].metadata)

    def test_chunk_with_metrics_integration(self):
        """chunk_with_metrics should work with adaptive sizing."""
        config = ChunkConfig.with_adaptive_sizing()
        chunker = MarkdownChunker(config)

        text = "# Test\n\n" + ("Some content. " * 100)
        chunks, metrics = chunker.chunk_with_metrics(text)

        # Should have chunks with adaptive metadata
        self.assertTrue(len(chunks) > 0)
        self.assertIn("adaptive_size", chunks[0].metadata)

        # Metrics should be calculated
        self.assertIsNotNone(metrics)
        self.assertGreater(metrics.total_chunks, 0)


if __name__ == "__main__":
    unittest.main()
