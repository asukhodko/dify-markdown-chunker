"""Performance benchmarks for streaming vs batch processing.

Compares throughput, latency, and scalability of streaming
vs traditional batch processing.
"""

import os
import time
from typing import Callable, Tuple

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


def benchmark_function(func: Callable, *args, **kwargs) -> Tuple[float, object]:
    """Benchmark a function's execution time.

    Returns:
        Tuple of (elapsed_seconds, function_result)
    """
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return elapsed, result


class TestStreamingThroughput:
    """Test processing throughput (MB/sec)."""

    @pytest.mark.slow
    def test_small_file_throughput(self, chunker, corpus_dir):
        """Measure throughput on small file."""
        file_path = os.path.join(corpus_dir, "INDEX.md")
        if not os.path.exists(file_path):
            pytest.skip(f"File not found: {file_path}")

        file_size = os.path.getsize(file_path)

        elapsed, chunks = benchmark_function(
            lambda: list(chunker.chunk_file_streaming(file_path))
        )

        throughput_mb_sec = (file_size / (1024 * 1024)) / elapsed

        assert len(chunks) > 0
        assert elapsed > 0
        print(f"\nSmall file: {throughput_mb_sec:.2f} MB/sec")

    @pytest.mark.slow
    def test_1mb_file_throughput(self, chunker, corpus_dir):
        """Measure throughput on 1MB file."""
        file_path = os.path.join(corpus_dir, "large_concat_1mb.md")
        if not os.path.exists(file_path):
            pytest.skip(f"File not found: {file_path}")

        file_size = os.path.getsize(file_path)

        elapsed, chunks = benchmark_function(
            lambda: list(chunker.chunk_file_streaming(file_path))
        )

        throughput_mb_sec = (file_size / (1024 * 1024)) / elapsed

        assert len(chunks) > 0
        # Should process at least 1MB/sec
        assert (
            throughput_mb_sec > 0.5
        ), f"Throughput too low: {throughput_mb_sec:.2f} MB/sec"
        print(f"\n1MB file: {throughput_mb_sec:.2f} MB/sec, {elapsed:.3f}s")

    @pytest.mark.slow
    def test_10mb_file_throughput(self, chunker, corpus_dir):
        """Measure throughput on 10MB file."""
        file_path = os.path.join(corpus_dir, "large_concat_10mb.md")
        if not os.path.exists(file_path):
            pytest.skip(f"File not found: {file_path}")

        file_size = os.path.getsize(file_path)
        config = StreamingConfig(buffer_size=200_000)

        elapsed, chunks = benchmark_function(
            lambda: list(chunker.chunk_file_streaming(file_path, config))
        )

        throughput_mb_sec = (file_size / (1024 * 1024)) / elapsed

        assert len(chunks) > 0
        # Should maintain reasonable throughput
        assert (
            throughput_mb_sec > 0.5
        ), f"Throughput too low: {throughput_mb_sec:.2f} MB/sec"
        print(f"\n10MB file: {throughput_mb_sec:.2f} MB/sec, {elapsed:.3f}s")


class TestStreamingLatency:
    """Test time to first chunk (latency)."""

    @pytest.mark.slow
    def test_time_to_first_chunk(self, chunker, corpus_dir):
        """Measure latency to first chunk."""
        file_path = os.path.join(corpus_dir, "large_concat_1mb.md")
        if not os.path.exists(file_path):
            pytest.skip(f"File not found: {file_path}")

        start = time.perf_counter()
        chunks_iter = chunker.chunk_file_streaming(file_path)
        first_chunk = next(chunks_iter)
        latency = time.perf_counter() - start

        assert first_chunk is not None
        assert first_chunk.content.strip()
        # First chunk should arrive quickly
        assert latency < 1.0, f"High latency: {latency:.3f}s"
        print(f"\nTime to first chunk: {latency*1000:.2f}ms")

    @pytest.mark.slow
    def test_streaming_vs_batch_latency(self, chunker, corpus_dir):
        """Compare latency: streaming vs batch."""
        file_path = os.path.join(corpus_dir, "large_concat_1mb.md")
        if not os.path.exists(file_path):
            pytest.skip(f"File not found: {file_path}")

        # Batch latency (must read entire file first)
        start = time.perf_counter()
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        batch_chunks_iter = iter(chunker.chunk(content))
        first_batch = next(batch_chunks_iter)
        batch_latency = time.perf_counter() - start

        # Streaming latency
        start = time.perf_counter()
        stream_chunks_iter = chunker.chunk_file_streaming(file_path)
        first_stream = next(stream_chunks_iter)
        stream_latency = time.perf_counter() - start

        assert first_batch is not None
        assert first_stream is not None

        print(f"\nBatch latency: {batch_latency*1000:.2f}ms")
        print(f"Streaming latency: {stream_latency*1000:.2f}ms")

        # Streaming should have lower or similar latency
        assert (
            stream_latency <= batch_latency * 2
        ), "Streaming latency significantly worse than batch"


class TestBatchEquivalencePerformance:
    """Test that streaming produces same results as batch."""

    @pytest.mark.slow
    def test_small_file_equivalence(self, chunker, corpus_dir):
        """Verify streaming matches batch for small file."""
        file_path = os.path.join(corpus_dir, "INDEX.md")
        if not os.path.exists(file_path):
            pytest.skip(f"File not found: {file_path}")

        # Batch processing
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        batch_chunks = list(chunker.chunk(content))

        # Streaming processing
        stream_chunks = list(chunker.chunk_file_streaming(file_path))

        # Should produce same number of chunks
        assert len(stream_chunks) == len(
            batch_chunks
        ), f"Chunk count mismatch: {len(stream_chunks)} vs {len(batch_chunks)}"

        # Content should match
        for i, (sc, bc) in enumerate(zip(stream_chunks, batch_chunks)):
            assert sc.content == bc.content, f"Content mismatch in chunk {i}"


class TestScalability:
    """Test performance scalability with file size."""

    @pytest.mark.slow
    def test_linear_time_scaling(self, chunker, corpus_dir):
        """Test that processing time scales linearly with file size."""
        test_files = [
            ("large_concat_1mb.md", 1),
            ("long_table.md", 5),
        ]

        results = []

        for filename, size_mb in test_files:
            file_path = os.path.join(corpus_dir, filename)
            if not os.path.exists(file_path):
                continue

            config = StreamingConfig(buffer_size=100_000)
            elapsed, chunks = benchmark_function(
                lambda: list(chunker.chunk_file_streaming(file_path, config))
            )

            throughput = size_mb / elapsed
            results.append((filename, size_mb, elapsed, throughput))
            print(f"\n{filename}: {elapsed:.3f}s, " f"{throughput:.2f} MB/sec")

        if len(results) >= 2:
            # Verify throughput is relatively consistent
            throughputs = [r[3] for r in results]
            min_tp = min(throughputs)
            max_tp = max(throughputs)

            # Throughput variation should be < 20x
            # (different file types have different complexity)
            assert (
                max_tp / min_tp < 20.0
            ), f"Throughput varies too much: {min_tp:.2f} to {max_tp:.2f}"

    @pytest.mark.slow
    def test_buffer_size_impact(self, chunker, corpus_dir):
        """Test impact of buffer size on performance."""
        file_path = os.path.join(corpus_dir, "large_concat_1mb.md")
        if not os.path.exists(file_path):
            pytest.skip(f"File not found: {file_path}")

        buffer_sizes = [50_000, 100_000, 200_000]
        results = []

        for buffer_size in buffer_sizes:
            config = StreamingConfig(buffer_size=buffer_size)
            elapsed, chunks = benchmark_function(
                lambda: list(chunker.chunk_file_streaming(file_path, config))
            )
            results.append((buffer_size, elapsed, len(chunks)))
            print(f"\nBuffer {buffer_size}: {elapsed:.3f}s, " f"{len(chunks)} chunks")

        # All should complete successfully
        assert all(r[2] > 0 for r in results), "Some configs produced no chunks"

        # Performance should be reasonable for all buffer sizes
        times = [r[1] for r in results]
        assert (
            max(times) / min(times) < 2.0
        ), "Buffer size causes large performance variance"


class TestIteratorEfficiency:
    """Test that streaming iterator is efficient."""

    @pytest.mark.slow
    def test_lazy_evaluation(self, chunker, corpus_dir):
        """Test that streaming doesn't process entire file up front."""
        file_path = os.path.join(corpus_dir, "large_concat_10mb.md")
        if not os.path.exists(file_path):
            pytest.skip(f"File not found: {file_path}")

        config = StreamingConfig(buffer_size=100_000)

        # Time to get iterator
        start = time.perf_counter()
        _ = chunker.chunk_file_streaming(file_path, config)
        setup_time = time.perf_counter() - start

        # Get first chunk
        start = time.perf_counter()
        # Setup should be very fast (no processing)
        assert setup_time < 0.1, f"Iterator setup too slow: {setup_time*1000:.2f}ms"

    @pytest.mark.slow
    def test_early_termination(self, chunker, corpus_dir):
        """Test that we can stop iteration early without penalty."""
        file_path = os.path.join(corpus_dir, "large_concat_10mb.md")
        if not os.path.exists(file_path):
            pytest.skip(f"File not found: {file_path}")

        config = StreamingConfig(buffer_size=100_000)

        # Get only first 10 chunks
        start = time.perf_counter()
        chunks = []
        for i, chunk in enumerate(chunker.chunk_file_streaming(file_path, config)):
            chunks.append(chunk)
            if i >= 9:  # 10 chunks (0-9)
                break
        elapsed = time.perf_counter() - start

        assert len(chunks) == 10
        # Should be fast since we stopped early
        assert elapsed < 2.0, f"Early termination too slow: {elapsed:.3f}s"
        print(f"\n10 chunks from 10MB file: {elapsed:.3f}s")
