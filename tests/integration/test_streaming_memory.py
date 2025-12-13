"""Memory profiling tests for streaming processing.

Tests that streaming processing maintains low memory usage
regardless of input file size, using tracemalloc.
"""

import os
import tracemalloc
from typing import Tuple

import pytest

from markdown_chunker_v2.chunker import MarkdownChunker
from markdown_chunker_v2.streaming import StreamingConfig


@pytest.fixture
def corpus_dir():
    """Get the path to the test corpus directory."""
    tests_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(tests_dir, "corpus")


@pytest.fixture
def chunker():
    """Create a standard markdown chunker instance."""
    return MarkdownChunker()


def measure_memory_peak(func, *args, **kwargs) -> Tuple[int, object]:
    """Measure peak memory usage of a function.

    Returns:
        Tuple of (peak_memory_bytes, function_result)
    """
    tracemalloc.start()
    try:
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        return peak, result
    finally:
        tracemalloc.stop()


class TestStreamingMemoryProfile:
    """Test memory usage of streaming processing."""

    def test_small_file_memory(self, chunker, corpus_dir):
        """Baseline memory test with small file."""
        file_path = os.path.join(corpus_dir, "INDEX.md")
        if not os.path.exists(file_path):
            pytest.skip(f"File not found: {file_path}")

        def process():
            return list(chunker.chunk_file_streaming(file_path))

        peak_memory, chunks = measure_memory_peak(process)

        # Convert to MB
        peak_mb = peak_memory / (1024 * 1024)

        assert len(chunks) > 0, "No chunks produced"
        assert peak_mb < 50, f"Memory usage too high: {peak_mb:.2f}MB"
        print(f"\nSmall file memory: {peak_mb:.2f}MB")

    def test_1mb_file_memory(self, chunker, corpus_dir):
        """Test memory usage with 1MB file."""
        file_path = os.path.join(corpus_dir, "large_concat_1mb.md")
        if not os.path.exists(file_path):
            pytest.skip(f"File not found: {file_path}")

        config = StreamingConfig(buffer_size=100_000, max_memory_mb=50)

        def process():
            return list(chunker.chunk_file_streaming(file_path, config))

        peak_memory, chunks = measure_memory_peak(process)
        peak_mb = peak_memory / (1024 * 1024)

        assert len(chunks) > 0
        assert peak_mb < 50, f"Memory usage exceeded limit: {peak_mb:.2f}MB"
        print(f"\n1MB file memory: {peak_mb:.2f}MB")

    @pytest.mark.slow
    def test_10mb_file_memory(self, chunker, corpus_dir):
        """Test memory usage with 10MB file stays under limit."""
        file_path = os.path.join(corpus_dir, "large_concat_10mb.md")
        if not os.path.exists(file_path):
            pytest.skip(f"File not found: {file_path}")

        config = StreamingConfig(buffer_size=100_000, max_memory_mb=50)

        def process():
            # Process in streaming fashion - don't collect all
            chunk_count = 0
            for chunk in chunker.chunk_file_streaming(file_path, config):
                chunk_count += 1
                # Only keep reference to count, not chunks
            return chunk_count

        peak_memory, chunk_count = measure_memory_peak(process)
        peak_mb = peak_memory / (1024 * 1024)

        assert chunk_count > 0
        # Should stay well under 50MB even for 10MB file
        assert (
            peak_mb < 50
        ), f"Memory usage exceeded limit: {peak_mb:.2f}MB for 10MB file"
        print(f"\n10MB file memory: {peak_mb:.2f}MB, {chunk_count} chunks")

    @pytest.mark.slow
    def test_table_file_memory(self, chunker, corpus_dir):
        """Test memory usage with 5MB table file."""
        file_path = os.path.join(corpus_dir, "long_table.md")
        if not os.path.exists(file_path):
            pytest.skip(f"File not found: {file_path}")

        config = StreamingConfig(buffer_size=100_000, max_memory_mb=50)

        def process():
            chunk_count = 0
            for chunk in chunker.chunk_file_streaming(file_path, config):
                chunk_count += 1
            return chunk_count

        peak_memory, chunk_count = measure_memory_peak(process)
        peak_mb = peak_memory / (1024 * 1024)

        assert chunk_count > 0
        assert peak_mb < 50, f"Memory usage exceeded limit: {peak_mb:.2f}MB"
        print(f"\nTable file memory: {peak_mb:.2f}MB, {chunk_count} chunks")

    @pytest.mark.slow
    def test_streaming_vs_batch_memory(self, chunker, corpus_dir):
        """Compare memory usage: streaming vs batch processing."""
        file_path = os.path.join(corpus_dir, "large_concat_1mb.md")
        if not os.path.exists(file_path):
            pytest.skip(f"File not found: {file_path}")

        # Measure batch processing
        def batch_process():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return list(chunker.chunk(content))

        batch_peak, batch_chunks = measure_memory_peak(batch_process)
        batch_mb = batch_peak / (1024 * 1024)

        # Measure streaming processing
        def stream_process():
            return list(chunker.chunk_file_streaming(file_path))

        stream_peak, stream_chunks = measure_memory_peak(stream_process)
        stream_mb = stream_peak / (1024 * 1024)

        print(f"\nBatch memory: {batch_mb:.2f}MB")
        print(f"Streaming memory: {stream_mb:.2f}MB")

        # Streaming should use less or similar memory
        # For 1MB file, difference may not be huge, but streaming
        # should not use MORE memory
        assert stream_mb <= batch_mb * 1.5, (
            f"Streaming used significantly more memory: "
            f"{stream_mb:.2f}MB vs {batch_mb:.2f}MB"
        )


class TestMemoryEfficiency:
    """Test memory efficiency properties."""

    @pytest.mark.slow
    def test_no_full_file_load(self, chunker, corpus_dir):
        """Verify streaming doesn't load entire file into memory."""
        file_path = os.path.join(corpus_dir, "large_concat_10mb.md")
        if not os.path.exists(file_path):
            pytest.skip(f"File not found: {file_path}")

        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)

        config = StreamingConfig(buffer_size=100_000)

        def process():
            count = 0
            for _ in chunker.chunk_file_streaming(file_path, config):
                count += 1
            return count

        peak_memory, count = measure_memory_peak(process)
        peak_mb = peak_memory / (1024 * 1024)

        # Memory should be much less than file size
        assert peak_mb < file_size_mb * 0.5, (
            f"Memory usage {peak_mb:.2f}MB is too close to "
            f"file size {file_size_mb:.2f}MB"
        )
        print(
            f"\nFile: {file_size_mb:.2f}MB, "
            f"Memory: {peak_mb:.2f}MB ({count} chunks)"
        )

    @pytest.mark.slow
    def test_constant_memory_scaling(self, chunker, corpus_dir):
        """Test that memory doesn't scale with file size."""
        files = [
            ("INDEX.md", None),
            ("large_concat_1mb.md", 1),
            ("long_table.md", 5),
        ]

        config = StreamingConfig(buffer_size=100_000)
        results = []

        for filename, expected_mb in files:
            file_path = os.path.join(corpus_dir, filename)
            if not os.path.exists(file_path):
                continue

            def process():
                count = 0
                for _ in chunker.chunk_file_streaming(file_path, config):
                    count += 1
                return count

            peak_memory, count = measure_memory_peak(process)
            peak_mb = peak_memory / (1024 * 1024)
            results.append((filename, expected_mb, peak_mb))
            print(f"\n{filename}: {peak_mb:.2f}MB ({count} chunks)")

        if len(results) >= 2:
            # Memory should not grow proportionally with file size
            # 5MB file should not use 5x more memory than 1MB file
            small_mem = next((m for f, s, m in results if s == 1), None)
            large_mem = next((m for f, s, m in results if s == 5), None)

            if small_mem and large_mem:
                ratio = large_mem / small_mem
                assert ratio < 2.0, (
                    f"Memory scaling too high: "
                    f"5MB file uses {ratio:.2f}x more than 1MB file"
                )
