"""
Integration tests for streaming processing.

Tests streaming chunker with real corpus files and batch equivalence.
"""

import io
import os

import pytest

from markdown_chunker_v2 import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig
from markdown_chunker_v2.streaming import StreamingConfig


class TestStreamingChunker:
    """Test streaming chunker end-to-end."""

    def test_basic_streaming(self):
        """Test basic streaming functionality."""
        chunker = MarkdownChunker()
        text = "# Header\n\nParagraph 1\n\n## Section\n\nParagraph 2\n"

        # Create stream
        stream = io.StringIO(text)

        # Chunk stream
        chunks = list(chunker.chunk_stream(stream))

        # Verify chunks created
        assert len(chunks) > 0
        assert all(hasattr(c, "content") for c in chunks)
        assert all(hasattr(c, "metadata") for c in chunks)

    def test_streaming_metadata(self):
        """Test streaming-specific metadata."""
        chunker = MarkdownChunker()
        text = "# Header\n\nContent\n" * 100

        stream = io.StringIO(text)
        chunks = list(chunker.chunk_stream(stream))

        # Verify streaming metadata present
        for chunk in chunks:
            assert "stream_chunk_index" in chunk.metadata
            assert "stream_window_index" in chunk.metadata
            assert "bytes_processed" in chunk.metadata

    def test_file_streaming(self, tmp_path):
        """Test file-based streaming."""
        chunker = MarkdownChunker()

        # Create temp file
        test_file = tmp_path / "test.md"
        test_file.write_text("# Header\n\nContent\n" * 50)

        # Stream file
        chunks = list(chunker.chunk_file_streaming(str(test_file)))

        assert len(chunks) > 0


class TestBatchEquivalence:
    """Test streaming produces equivalent results to batch."""

    def test_small_file_equivalence(self):
        """Test streaming matches batch for small files."""
        chunker = MarkdownChunker(ChunkConfig(max_chunk_size=1000))
        text = """# Introduction

This is a test document with multiple sections.

## Section 1

Content for section 1 with some details.

## Section 2

More content here.

## Section 3

Final section content.
"""

        # Batch chunking
        batch_chunks = chunker.chunk(text)

        # Streaming chunking
        stream = io.StringIO(text)
        stream_chunks = list(chunker.chunk_stream(stream))

        # Compare content
        assert len(batch_chunks) == len(stream_chunks)
        for b, s in zip(batch_chunks, stream_chunks):
            assert b.content == s.content


class TestLargeCorpusFiles:
    """Test streaming with large corpus files."""

    @pytest.fixture
    def corpus_dir(self):
        """Get corpus directory."""
        return "tests/corpus/github_readmes"

    @pytest.mark.slow
    def test_youtube_dl_streaming(self, corpus_dir):
        """Test streaming with youtube-dl.md (101KB)."""
        file_path = os.path.join(corpus_dir, "python/youtube-dl.md")

        if not os.path.exists(file_path):
            pytest.skip(f"Corpus file not found: {file_path}")

        chunker = MarkdownChunker()
        chunks = list(chunker.chunk_file_streaming(file_path))

        # Verify chunks created
        assert len(chunks) > 0

        # Verify no empty chunks
        assert all(c.content.strip() for c in chunks)

        # Verify metadata
        assert all("stream_chunk_index" in c.metadata for c in chunks)

    @pytest.mark.slow
    def test_webpack_streaming(self, corpus_dir):
        """Test streaming with webpack.md (80KB)."""
        file_path = os.path.join(corpus_dir, "javascript/webpack.md")

        if not os.path.exists(file_path):
            pytest.skip(f"Corpus file not found: {file_path}")

        chunker = MarkdownChunker()
        chunks = list(chunker.chunk_file_streaming(file_path))

        assert len(chunks) > 0
        assert all(c.content.strip() for c in chunks)

    @pytest.mark.slow
    def test_axios_streaming(self, corpus_dir):
        """Test streaming with axios.md (72KB)."""
        file_path = os.path.join(corpus_dir, "javascript/axios.md")

        if not os.path.exists(file_path):
            pytest.skip(f"Corpus file not found: {file_path}")

        chunker = MarkdownChunker()
        chunks = list(chunker.chunk_file_streaming(file_path))

        assert len(chunks) > 0


class TestStreamingConfig:
    """Test streaming configuration."""

    def test_custom_buffer_size(self):
        """Test custom buffer size."""
        chunker = MarkdownChunker()
        config = StreamingConfig(buffer_size=50_000)

        text = "# Header\n\nContent\n" * 1000
        stream = io.StringIO(text)

        chunks = list(chunker.chunk_stream(stream, config))
        assert len(chunks) > 0

    def test_custom_overlap_lines(self):
        """Test custom overlap lines."""
        chunker = MarkdownChunker()
        config = StreamingConfig(overlap_lines=10)

        text = "# Header\n\nContent\n" * 100
        stream = io.StringIO(text)

        chunks = list(chunker.chunk_stream(stream, config))
        assert len(chunks) > 0


class TestCodeBlockIntegrity:
    """Test code blocks not split across windows."""

    def test_code_block_preserved(self):
        """Test code blocks stay intact."""
        chunker = MarkdownChunker()
        config = StreamingConfig(buffer_size=1000)

        text = """# Code Example

Here is some code:

```python
def hello():
    print("Hello, World!")
    return True
```

More text after code.
"""

        stream = io.StringIO(text)
        chunks = list(chunker.chunk_stream(stream, config))

        # Verify chunks created
        assert len(chunks) > 0

        # Verify all content preserved
        total_content = "".join(c.content for c in chunks)
        assert "```python" in total_content
        assert "def hello" in total_content
