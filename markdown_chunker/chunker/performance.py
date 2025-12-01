"""
Performance optimization utilities for Stage 2 chunker.

This module provides lazy loading, caching, and performance monitoring.
"""

import time
import weakref
from functools import lru_cache, wraps
from typing import Any, Callable, Dict, List, Optional


class StrategyCache:
    """Cache for strategy instances with lazy loading."""

    def __init__(self) -> None:
        self._strategies: Dict[str, Any] = {}
        self._weak_cache: weakref.WeakValueDictionary = weakref.WeakValueDictionary()

    def get_strategy(self, strategy_name: str, factory: Callable) -> Any:
        """Get strategy instance, creating it lazily if needed."""
        if strategy_name not in self._strategies:
            self._strategies[strategy_name] = factory()
        return self._strategies[strategy_name]

    def clear(self) -> None:
        """Clear all cached strategies."""
        self._strategies.clear()
        self._weak_cache.clear()


class PerformanceMonitor:
    """Monitor and track performance metrics."""

    def __init__(self) -> None:
        self.metrics: Dict[str, list] = {}
        self.enabled = True

    def record(self, operation: str, duration: float, size: int = 0) -> None:
        """Record a performance metric."""
        if not self.enabled:
            return

        if operation not in self.metrics:
            self.metrics[operation] = []

        self.metrics[operation].append(
            {"duration": duration, "size": size, "timestamp": time.time()}
        )

    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for an operation."""
        if operation not in self.metrics or not self.metrics[operation]:
            return {}

        durations = [m["duration"] for m in self.metrics[operation]]
        sizes = [m["size"] for m in self.metrics[operation] if m["size"] > 0]

        stats = {
            "count": len(durations),
            "total_time": sum(durations),
            "avg_time": sum(durations) / len(durations),
            "min_time": min(durations),
            "max_time": max(durations),
        }

        if sizes:
            stats["avg_size"] = sum(sizes) / len(sizes)
            stats["throughput"] = (
                sum(sizes) / sum(durations) if sum(durations) > 0 else 0
            )

        return stats

    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all operations."""
        return {op: self.get_stats(op) for op in self.metrics.keys()}

    def clear(self) -> None:
        """Clear all metrics."""
        self.metrics.clear()


def timed(operation_name: Optional[str] = None):
    """Decorator to time function execution."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            # Try to get monitor from first arg (self)
            if args and hasattr(args[0], "_performance_monitor"):
                monitor = args[0]._performance_monitor
                op_name = operation_name or f"{func.__name__}"
                monitor.record(op_name, duration)

            return result

        return wrapper

    return decorator


@lru_cache(maxsize=128)
def cached_sentence_split(text: str, max_length: int = 1000) -> tuple:
    """Cached sentence splitting for frequently used texts."""
    # Only cache small to medium texts
    if len(text) > max_length:
        return tuple()  # Don't cache large texts

    import re

    # Simple sentence splitting
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return tuple(sentences)


class ChunkCache:
    """Cache for chunk results to avoid reprocessing."""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache: Dict[str, Any] = {}
        self._access_order: List[str] = []

    def get(self, key: str) -> Optional[Any]:
        """Get cached result."""
        if key in self._cache:
            # Update access order
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None

    def put(self, key: str, value: Any) -> None:
        """Put result in cache."""
        if key in self._cache:
            # Update existing
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            self._cache[key] = value
            return

        # Check size limit
        if len(self._cache) >= self.max_size:
            # Remove least recently used
            lru_key = self._access_order.pop(0)
            del self._cache[lru_key]

        self._cache[key] = value
        self._access_order.append(key)

    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()
        self._access_order.clear()

    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)


def generate_cache_key(content: str, config: Any) -> str:
    """Generate cache key from content and config."""
    import hashlib

    # Hash content
    content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()[:16]

    # Include relevant config parameters
    config_str = (
        f"{config.max_chunk_size}_{config.min_chunk_size}_{config.enable_overlap}"
    )
    config_hash = hashlib.md5(config_str.encode("utf-8")).hexdigest()[:8]

    return f"{content_hash}_{config_hash}"


class MemoryEfficientProcessor:
    """Process large documents in a memory-efficient way."""

    def __init__(self, chunk_size: int = 10000):
        self.chunk_size = chunk_size

    def process_in_chunks(self, content: str, processor: Callable) -> list:
        """Process content in chunks to reduce memory usage."""
        results = []

        # Split content into manageable chunks
        for i in range(0, len(content), self.chunk_size):
            chunk = content[i : i + self.chunk_size]
            result = processor(chunk)
            results.append(result)

        return results

    def estimate_memory_usage(self, content: str) -> int:
        """Estimate memory usage for processing content."""
        # Rough estimate: content size + overhead
        base_size = len(content.encode("utf-8"))
        overhead = base_size * 0.5  # 50% overhead for processing
        return int(base_size + overhead)


class PerformanceOptimizer:
    """Main performance optimization coordinator."""

    def __init__(self) -> None:
        self.strategy_cache = StrategyCache()
        self.chunk_cache = ChunkCache()
        self.monitor = PerformanceMonitor()
        self.memory_processor = MemoryEfficientProcessor()

    def should_use_cache(self, content_size: int) -> bool:
        """Determine if caching should be used."""
        # Cache small to medium documents
        return content_size < 50000

    def should_use_streaming(self, content_size: int) -> bool:
        """Determine if streaming should be used."""
        # Use streaming for very large documents
        return content_size > 1000000  # 1MB

    def get_optimal_chunk_size(self, content_size: int) -> int:
        """Get optimal chunk size based on content size."""
        if content_size < 10000:
            return 1000
        elif content_size < 100000:
            return 5000
        else:
            return 10000

    def clear_all_caches(self) -> None:
        """Clear all caches."""
        self.strategy_cache.clear()
        self.chunk_cache.clear()
        self.monitor.clear()
