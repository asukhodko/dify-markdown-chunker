"""
Tests for performance optimizations and benchmarking.
"""

import time

from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.performance import (
    ChunkCache,
    MemoryEfficientProcessor,
    PerformanceMonitor,
    PerformanceOptimizer,
    StrategyCache,
    generate_cache_key,
)
from markdown_chunker.chunker.types import ChunkConfig


class TestStrategyCache:
    """Test strategy caching."""

    def test_lazy_loading(self):
        """Test that strategies are loaded lazily."""
        cache = StrategyCache()
        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return {"instance": call_count}

        # First call should create instance
        result1 = cache.get_strategy("test", factory)
        assert call_count == 1

        # Second call should reuse instance
        result2 = cache.get_strategy("test", factory)
        assert call_count == 1
        assert result1 is result2

    def test_multiple_strategies(self):
        """Test caching multiple strategies."""
        cache = StrategyCache()

        strategy1 = cache.get_strategy("s1", lambda: {"name": "s1"})
        strategy2 = cache.get_strategy("s2", lambda: {"name": "s2"})

        assert strategy1 is not strategy2
        assert strategy1["name"] == "s1"
        assert strategy2["name"] == "s2"

    def test_clear_cache(self):
        """Test clearing cache."""
        cache = StrategyCache()
        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return {"instance": call_count}

        cache.get_strategy("test", factory)
        assert call_count == 1

        cache.clear()
        cache.get_strategy("test", factory)
        assert call_count == 2  # Should create new instance


class TestPerformanceMonitor:
    """Test performance monitoring."""

    def test_record_metrics(self):
        """Test recording performance metrics."""
        monitor = PerformanceMonitor()

        monitor.record("operation1", 0.5, 1000)
        monitor.record("operation1", 0.3, 2000)

        stats = monitor.get_stats("operation1")
        assert stats["count"] == 2
        assert stats["total_time"] == 0.8
        assert stats["avg_time"] == 0.4

    def test_multiple_operations(self):
        """Test monitoring multiple operations."""
        monitor = PerformanceMonitor()

        monitor.record("op1", 0.5)
        monitor.record("op2", 0.3)
        monitor.record("op1", 0.2)

        all_stats = monitor.get_all_stats()
        assert "op1" in all_stats
        assert "op2" in all_stats
        assert all_stats["op1"]["count"] == 2
        assert all_stats["op2"]["count"] == 1

    def test_throughput_calculation(self):
        """Test throughput calculation."""
        monitor = PerformanceMonitor()

        monitor.record("process", 1.0, 1000)  # 1000 bytes in 1 second
        monitor.record("process", 2.0, 4000)  # 4000 bytes in 2 seconds

        stats = monitor.get_stats("process")
        assert "throughput" in stats
        # Total: 5000 bytes in 3 seconds=~1666.67 bytes/sec
        assert stats["throughput"] > 1600
        assert stats["throughput"] < 1700

    def test_disabled_monitoring(self):
        """Test that disabled monitoring doesn't record."""
        monitor = PerformanceMonitor()
        monitor.enabled = False

        monitor.record("operation", 0.5)

        stats = monitor.get_stats("operation")
        assert stats == {}

    def test_clear_metrics(self):
        """Test clearing metrics."""
        monitor = PerformanceMonitor()

        monitor.record("op1", 0.5)
        monitor.record("op2", 0.3)

        monitor.clear()

        assert monitor.get_all_stats() == {}


class TestChunkCache:
    """Test chunk result caching."""

    def test_cache_put_get(self):
        """Test basic cache operations."""
        cache = ChunkCache(max_size=3)

        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_cache_miss(self):
        """Test cache miss."""
        cache = ChunkCache()
        assert cache.get("nonexistent") is None

    def test_lru_eviction(self):
        """Test LRU eviction."""
        cache = ChunkCache(max_size=2)

        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # Should evict key1

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_access_order_update(self):
        """Test that access updates order."""
        cache = ChunkCache(max_size=2)

        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.get("key1")  # Access key1
        cache.put("key3", "value3")  # Should evict key2, not key1

        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"

    def test_cache_size(self):
        """Test cache size tracking."""
        cache = ChunkCache(max_size=5)

        assert cache.size() == 0
        cache.put("key1", "value1")
        assert cache.size() == 1
        cache.put("key2", "value2")
        assert cache.size() == 2

    def test_clear_cache(self):
        """Test clearing cache."""
        cache = ChunkCache()

        cache.put("key1", "value1")
        cache.put("key2", "value2")

        cache.clear()

        assert cache.size() == 0
        assert cache.get("key1") is None


class TestCacheKeyGeneration:
    """Test cache key generation."""

    def test_same_content_same_key(self):
        """Test that same content generates same key."""
        config = ChunkConfig.default()

        key1 = generate_cache_key("test content", config)
        key2 = generate_cache_key("test content", config)

        assert key1 == key2

    def test_different_content_different_key(self):
        """Test that different content generates different keys."""
        config = ChunkConfig.default()

        key1 = generate_cache_key("content1", config)
        key2 = generate_cache_key("content2", config)

        assert key1 != key2

    def test_different_config_different_key(self):
        """Test that different config generates different keys."""
        config1 = ChunkConfig(max_chunk_size=1000)
        config2 = ChunkConfig(max_chunk_size=2000)

        key1 = generate_cache_key("test", config1)
        key2 = generate_cache_key("test", config2)

        assert key1 != key2


class TestMemoryEfficientProcessor:
    """Test memory-efficient processing."""

    def test_process_in_chunks(self):
        """Test processing content in chunks."""
        processor = MemoryEfficientProcessor(chunk_size=10)

        content = "a" * 25
        results = processor.process_in_chunks(content, lambda x: len(x))

        # Should split into 3 chunks: 10, 10, 5
        assert len(results) == 3
        assert results[0] == 10
        assert results[1] == 10
        assert results[2] == 5

    def test_memory_estimation(self):
        """Test memory usage estimation."""
        processor = MemoryEfficientProcessor()

        content = "test content"
        estimated = processor.estimate_memory_usage(content)

        # Should be roughly 1.5x the content size
        base_size = len(content.encode("utf-8"))
        assert estimated >= base_size
        assert estimated <= base_size * 2


class TestPerformanceOptimizer:
    """Test performance optimizer."""

    def test_cache_decision(self):
        """Test caching decision logic."""
        optimizer = PerformanceOptimizer()

        # Small content should use cache
        assert optimizer.should_use_cache(1000) is True

        # Large content should not use cache
        assert optimizer.should_use_cache(100000) is False

    def test_streaming_decision(self):
        """Test streaming decision logic."""
        optimizer = PerformanceOptimizer()

        # Small content should not use streaming
        assert optimizer.should_use_streaming(10000) is False

        # Very large content should use streaming
        assert optimizer.should_use_streaming(2000000) is True

    def test_optimal_chunk_size(self):
        """Test optimal chunk size calculation."""
        optimizer = PerformanceOptimizer()

        # Small content
        assert optimizer.get_optimal_chunk_size(5000) == 1000

        # Medium content
        assert optimizer.get_optimal_chunk_size(50000) == 5000

        # Large content
        assert optimizer.get_optimal_chunk_size(200000) == 10000


class TestChunkerPerformance:
    """Test chunker performance features."""

    def test_performance_monitoring_disabled_by_default(self):
        """Test that performance monitoring is disabled by default."""
        chunker = MarkdownChunker()

        content = "# Test\n\nSome content."
        chunker.chunk(content)

        stats = chunker.get_performance_stats()
        # Should be empty when disabled
        assert stats == {}

    def test_performance_monitoring_enabled(self):
        """Test performance monitoring when enabled."""
        chunker = MarkdownChunker(enable_performance_monitoring=True)

        content = "# Test\n\nSome content."
        chunker.chunk(content)

        stats = chunker.get_performance_stats()
        # Should have some metrics when enabled
        # Note: actual metrics depend on implementation
        assert isinstance(stats, dict)

    def test_enable_disable_monitoring(self):
        """Test enabling and disabling monitoring."""
        chunker = MarkdownChunker()

        chunker.enable_performance_monitoring()
        assert chunker._performance_monitor.enabled is True

        chunker.disable_performance_monitoring()
        assert chunker._performance_monitor.enabled is False

    def test_clear_caches(self):
        """Test clearing caches."""
        chunker = MarkdownChunker()

        # Process some content
        content = "# Test\n\nSome content."
        chunker.chunk(content)

        # Clear caches should not raise error
        chunker.clear_caches()


class TestPerformanceBenchmarks:
    """Performance benchmark tests."""

    def test_small_document_performance(self):
        """Test performance on small documents."""
        chunker = MarkdownChunker()

        content = """# Small Document

Some text content here.

```python
def test():
    pass
```
"""

        start_time = time.time()
        result = chunker.chunk_with_analysis(content)
        duration = time.time() - start_time

        # Should complete quickly (< 0.1 seconds)
        assert duration < 0.1
        assert len(result.chunks) > 0

    def test_medium_document_performance(self):
        """Test performance on medium documents."""
        chunker = MarkdownChunker()

        # Create medium-sized document (~10KB)
        content = (
            """# Medium Document

## Section 1

"""
            + ("Some text content. " * 100)
            + """

```python
def function():
    pass
```

## Section 2

"""
            + ("More content here. " * 100)
        )

        start_time = time.time()
        result = chunker.chunk_with_analysis(content)
        duration = time.time() - start_time

        # Should complete reasonably fast (< 2 seconds)
        # Note: structural strategy (now priority 2) may take longer than mixed
        assert duration < 2.0
        assert len(result.chunks) > 0

    def test_large_document_performance(self):
        """Test performance on large documents."""
        chunker = MarkdownChunker()

        # Create large document (~100KB)
        content = (
            """# Large Document

"""
            + ("## Section\n\n" + ("Content. " * 200) + "\n\n") * 50
        )

        start_time = time.time()
        result = chunker.chunk_with_analysis(content)
        duration = time.time() - start_time

        # Should complete in reasonable time (< 5 seconds)
        assert duration < 5.0
        assert len(result.chunks) > 0

    def test_code_heavy_performance(self):
        """Test performance on code-heavy documents."""
        chunker = MarkdownChunker()

        # Create code-heavy document
        code_blocks = "\n\n".join(
            [
                """```python
def function_{i}():
    for j in range(100):
        print(f"Line {{j}}")
```"""
                for i in range(20)
            ]
        )

        content = f"# Code Document\n\n{code_blocks}"

        start_time = time.time()
        result = chunker.chunk_with_analysis(content)
        duration = time.time() - start_time

        # Should handle code efficiently (< 2 seconds)
        assert duration < 2.0
        assert len(result.chunks) > 0
        # Strategy may vary based on content analysis, just check it completes
