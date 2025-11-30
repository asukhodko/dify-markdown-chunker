"""
Performance tests for full chunking pipeline.

Tests performance requirements and resource usage for different document sizes.
"""

import time
from pathlib import Path

import pytest

from markdown_chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig

# Fixtures


@pytest.fixture
def documents_dir():
    """Path to real documents directory."""
    return Path(__file__).parent.parent / "fixtures" / "real_documents"


@pytest.fixture
def chunker():
    """Create chunker with default config."""
    return MarkdownChunker()


# Helper functions


def load_document(documents_dir, filename):
    """Load document content."""
    doc_path = documents_dir / filename
    with open(doc_path, "r", encoding="utf-8") as f:
        return f.read()


def measure_performance(chunker, content):
    """Measure chunking performance."""
    start_time = time.time()
    result = chunker.chunk(content, include_analysis=True)
    end_time = time.time()

    return {
        "time": end_time - start_time,
        "chunks": len(result.chunks),
        "size": len(content),
        "throughput": (
            len(content) / (end_time - start_time) if end_time > start_time else 0
        ),
    }


def generate_document(size_kb):
    """Generate a test document of specified size."""
    # Generate markdown with headers, paragraphs, and code blocks
    content = []
    content.append("# Test Document\n\n")

    num_sections = size_kb

    for i in range(num_sections):
        content.append(f"## Section {i + 1}\n\n")
        content.append("This is a test paragraph with some content. " * 10)
        content.append("\n\n")

        if i % 3 == 0:
            content.append("```python\n")
            content.append("def test_function():\n")
            content.append("    return 'test'\n")
            content.append("```\n\n")

    return "".join(content)


# Performance tests


class TestSmallDocumentPerformance:
    """Tests for small documents (5KB)."""

    def test_small_document_performance(self, documents_dir, chunker):
        """Test that small documents process quickly (<2s)."""
        content = load_document(documents_dir, "readme.md")

        # Warm up (first run is slower due to initialization)
        chunker.chunk(content)

        # Measure performance
        perf = measure_performance(chunker, content)

        # Verify performance (relaxed for CI/slow machines)
        assert perf["time"] < 2.0, f"Too slow: {perf['time']:.3f}s (target: <2.0s)"
        assert perf["chunks"] > 0, "No chunks created"

        # Calculate throughput
        throughput_kb = perf["throughput"] / 1024
        assert throughput_kb > 2, f"Low throughput: {throughput_kb:.1f} KB/s"

    def test_small_document_multiple_runs(self, documents_dir, chunker):
        """Test consistency across multiple runs."""
        content = load_document(documents_dir, "readme.md")

        times = []
        for _ in range(10):
            perf = measure_performance(chunker, content)
            times.append(perf["time"])

        # Check consistency (max should be < 5x avg)
        # Note: Increased tolerance for CI/WSL environments where performance
        # can be more variable due to system load and I/O overhead
        avg_time = sum(times) / len(times)
        max_time = max(times)

        assert max_time < avg_time * 5, "Performance too inconsistent"


class TestMediumDocumentPerformance:
    """Tests for medium documents (10-20KB)."""

    def test_medium_document_performance(self, documents_dir, chunker):
        """Test that medium documents process in reasonable time (<3s)."""
        content = load_document(documents_dir, "api_documentation.md")

        # Warm up
        chunker.chunk(content)

        # Measure performance
        perf = measure_performance(chunker, content)

        # Verify performance (relaxed for CI)
        assert perf["time"] < 3.0, f"Too slow: {perf['time']:.3f}s (target: <3.0s)"
        assert perf["chunks"] > 0, "No chunks created"

        # Calculate throughput
        throughput_kb = perf["throughput"] / 1024
        assert throughput_kb > 2, f"Low throughput: {throughput_kb:.1f} KB/s"

    def test_technical_spec_performance(self, documents_dir, chunker):
        """Test technical specification (20KB) performance."""
        content = load_document(documents_dir, "technical_spec.md")

        perf = measure_performance(chunker, content)

        # Should process in reasonable time
        assert perf["time"] < 1.0, f"Too slow: {perf['time']:.3f}s (target: <1.0s)"
        assert perf["chunks"] > 0, "No chunks created"


class TestLargeDocumentPerformance:
    """Tests for large documents (50-100KB)."""

    def test_large_document_performance(self, chunker):
        """Test that large documents process in reasonable time (<10s)."""
        # Generate 50KB document
        content = generate_document(50)

        # Warm up
        chunker.chunk(content[:1000])

        perf = measure_performance(chunker, content)

        # Verify performance (relaxed for CI)
        assert perf["time"] < 10.0, f"Too slow: {perf['time']:.3f}s (target: <10.0s)"
        assert perf["chunks"] > 0, "No chunks created"

        # Calculate throughput
        throughput_kb = perf["throughput"] / 1024
        assert throughput_kb > 5, f"Low throughput: {throughput_kb:.1f} KB/s"

    def test_100kb_document_performance(self, chunker):
        """Test 100KB document performance."""
        content = generate_document(100)

        perf = measure_performance(chunker, content)

        # Should process in reasonable time
        assert perf["time"] < 5.0, f"Too slow: {perf['time']:.3f}s (target: <5.0s)"
        assert perf["chunks"] > 0, "No chunks created"


class TestThroughputCalculation:
    """Tests for throughput calculation."""

    def test_throughput_calculation(self, documents_dir, chunker):
        """Test throughput across different document sizes."""
        documents = [
            ("readme.md", 5),
            ("tutorial.md", 8),
            ("api_documentation.md", 10),
            ("technical_spec.md", 20),
        ]

        # Warm up
        content = load_document(documents_dir, "readme.md")
        chunker.chunk(content)

        throughputs = []

        for filename, expected_kb in documents:
            content = load_document(documents_dir, filename)
            perf = measure_performance(chunker, content)

            throughput_kb = perf["throughput"] / 1024
            throughputs.append(throughput_kb)

            print(f"\n{filename}: {throughput_kb:.1f} KB/s ({perf['time']:.3f}s)")

        # Average throughput should be reasonable (relaxed)
        avg_throughput = sum(throughputs) / len(throughputs)
        assert avg_throughput > 1, f"Low average throughput: {avg_throughput:.1f} KB/s"

    def test_throughput_with_different_configs(self, documents_dir):
        """Test throughput with different configurations."""
        content = load_document(documents_dir, "api_documentation.md")

        configs = [
            ("default", ChunkConfig.default()),
            ("code_heavy", ChunkConfig.for_code_heavy()),
            ("rag", ChunkConfig.for_dify_rag()),
        ]

        for name, config in configs:
            chunker = MarkdownChunker(config)
            perf = measure_performance(chunker, content)

            throughput_kb = perf["throughput"] / 1024
            print(f"\n{name}: {throughput_kb:.1f} KB/s")

            # All configs should have reasonable performance
            assert perf["time"] < 1.0, f"{name}: Too slow ({perf['time']:.3f}s)"


class TestMemoryUsage:
    """Tests for memory usage."""

    def test_memory_usage_reasonable(self, chunker):
        """Test that memory usage is reasonable."""
        # Generate 10KB document
        content = generate_document(10)

        # Process document
        result = chunker.chunk(content, include_analysis=True)

        # Verify chunks created
        assert len(result.chunks) > 0

        # Memory usage should be proportional to document size
        # (This is a basic check - proper memory profiling would need external tools)
        total_chunk_size = sum(len(c.content) for c in result.chunks)

        # Total chunk size should be close to original (allowing for overlap)
        ratio = total_chunk_size / len(content)
        assert 0.8 <= ratio <= 2.0, f"Unexpected size ratio: {ratio:.2f}"

    def test_no_memory_leaks_multiple_documents(self, documents_dir, chunker):
        """Test that processing multiple documents doesn't leak memory."""
        documents = [
            "readme.md",
            "tutorial.md",
            "api_documentation.md",
            "blog_post.md",
        ]

        # Process each document multiple times
        for _ in range(3):
            for filename in documents:
                content = load_document(documents_dir, filename)
                result = chunker.chunk(content)

                # Verify chunks created
                assert len(result) > 0

        # If we got here without crashing, no obvious memory leaks


class TestPerformanceWithDifferentStrategies:
    """Tests for performance with different strategies."""

    def test_structural_strategy_performance(self, documents_dir, chunker):
        """Test structural strategy performance."""
        content = load_document(documents_dir, "technical_spec.md")

        perf = measure_performance(chunker, content)

        # Should be fast
        assert perf["time"] < 1.0, f"Too slow: {perf['time']:.3f}s"

    def test_code_strategy_performance(self, documents_dir, chunker):
        """Test code strategy performance."""
        content = load_document(documents_dir, "api_documentation.md")

        perf = measure_performance(chunker, content)

        # Should be fast
        assert perf["time"] < 0.5, f"Too slow: {perf['time']:.3f}s"

    def test_mixed_strategy_performance(self, documents_dir, chunker):
        """Test mixed strategy performance."""
        content = load_document(documents_dir, "blog_post.md")

        perf = measure_performance(chunker, content)

        # Should be fast
        assert perf["time"] < 0.3, f"Too slow: {perf['time']:.3f}s"


class TestPerformanceRegression:
    """Tests to catch performance regressions."""

    def test_baseline_performance(self, documents_dir, chunker):
        """Establish baseline performance metrics."""
        # This test documents expected performance
        # Very relaxed for CI/slow machines

        baselines = {
            "readme.md": 2.0,  # 2s
            "tutorial.md": 2.0,  # 2s
            "api_documentation.md": 3.0,  # 3s
            "blog_post.md": 2.0,  # 2s
            "technical_spec.md": 5.0,  # 5s
        }

        # Warm up
        content = load_document(documents_dir, "readme.md")
        chunker.chunk(content)

        for filename, max_time in baselines.items():
            content = load_document(documents_dir, filename)
            perf = measure_performance(chunker, content)

            # Allow 2x margin for extra slow machines
            assert (
                perf["time"] < max_time * 2
            ), f"{filename}: {perf['time']:.3f}s exceeds baseline {max_time * 2:.3f}s"

    def test_performance_with_overlap(self, documents_dir):
        """Test that overlap doesn't significantly slow down processing."""
        content = load_document(documents_dir, "api_documentation.md")

        # Without overlap
        config_no_overlap = ChunkConfig(enable_overlap=False)
        chunker_no_overlap = MarkdownChunker(config_no_overlap)
        perf_no_overlap = measure_performance(chunker_no_overlap, content)

        # With overlap
        config_overlap = ChunkConfig(enable_overlap=True, overlap_size=200)
        chunker_overlap = MarkdownChunker(config_overlap)
        perf_overlap = measure_performance(chunker_overlap, content)

        # Overlap should add minimal overhead (<50%)
        overhead = (perf_overlap["time"] - perf_no_overlap["time"]) / perf_no_overlap[
            "time"
        ]
        assert overhead < 0.5, f"Overlap overhead too high: {overhead:.1%}"
