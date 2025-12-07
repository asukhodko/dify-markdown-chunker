"""
Measurement utilities for performance benchmarking.

Provides accurate, low-overhead timing and memory profiling infrastructure.
"""

import statistics
import time
import tracemalloc
from typing import Any, Callable, Dict, List, Tuple


def measure_time(func: Callable, *args, **kwargs) -> Tuple[Any, float]:
    """
    Measure execution time of a function with high precision.

    Args:
        func: Function to measure
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Tuple of (function_result, elapsed_time_seconds)
    """
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed_time = time.perf_counter() - start_time
    return result, elapsed_time


def measure_memory(func: Callable, *args, **kwargs) -> Tuple[Any, float]:
    """
    Measure peak memory usage during function execution.

    Args:
        func: Function to measure
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Tuple of (function_result, peak_memory_mb)
    """
    tracemalloc.start()
    result = func(*args, **kwargs)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_mb = peak / 1024 / 1024
    return result, peak_mb


def measure_all(func: Callable, *args, **kwargs) -> Tuple[Any, float, float]:
    """
    Measure both execution time and memory usage.

    Args:
        func: Function to measure
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Tuple of (function_result, elapsed_time_seconds, peak_memory_mb)
    """
    tracemalloc.start()
    start_time = time.perf_counter()

    result = func(*args, **kwargs)

    elapsed_time = time.perf_counter() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_mb = peak / 1024 / 1024
    return result, elapsed_time, peak_mb


def run_benchmark(
    func: Callable,
    args: tuple = (),
    kwargs: dict = None,
    warmup_runs: int = 2,
    measurement_runs: int = 5,
) -> Dict[str, Any]:
    """
    Run a benchmark with warm-up and multiple measurement runs.

    Args:
        func: Function to benchmark
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        warmup_runs: Number of warm-up runs to perform
        measurement_runs: Number of measurement runs for statistics

    Returns:
        Dictionary with benchmark statistics
    """
    if kwargs is None:
        kwargs = {}

    # Warm-up runs to eliminate cold-start effects
    for _ in range(warmup_runs):
        func(*args, **kwargs)

    # Measurement runs
    times = []
    memories = []
    results = []

    for _ in range(measurement_runs):
        result, elapsed, memory = measure_all(func, *args, **kwargs)
        times.append(elapsed)
        memories.append(memory)
        results.append(result)

    return {
        "time": {
            "mean": statistics.mean(times),
            "min": min(times),
            "max": max(times),
            "stddev": statistics.stdev(times) if len(times) > 1 else 0.0,
        },
        "memory": {
            "mean": statistics.mean(memories),
            "min": min(memories),
            "max": max(memories),
            "stddev": statistics.stdev(memories) if len(memories) > 1 else 0.0,
        },
        "result": results[0],  # Return first result for inspection
    }


def calculate_throughput(size_bytes: int, time_seconds: float) -> Dict[str, float]:
    """
    Calculate throughput metrics.

    Args:
        size_bytes: Size of processed data in bytes
        time_seconds: Processing time in seconds

    Returns:
        Dictionary with throughput metrics
    """
    if time_seconds == 0:
        return {"kb_per_sec": 0.0, "mb_per_sec": 0.0}

    size_kb = size_bytes / 1024
    size_mb = size_bytes / 1024 / 1024

    return {
        "kb_per_sec": size_kb / time_seconds,
        "mb_per_sec": size_mb / time_seconds,
    }


def aggregate_results(results: List[Dict]) -> Dict[str, Any]:
    """
    Aggregate benchmark results from multiple runs.

    Args:
        results: List of benchmark result dictionaries

    Returns:
        Aggregated statistics
    """
    if not results:
        return {}

    times = [r["time"]["mean"] for r in results]
    memories = [r["memory"]["mean"] for r in results]

    return {
        "time": {
            "mean": statistics.mean(times),
            "min": min(times),
            "max": max(times),
            "stddev": statistics.stdev(times) if len(times) > 1 else 0.0,
        },
        "memory": {
            "mean": statistics.mean(memories),
            "min": min(memories),
            "max": max(memories),
            "stddev": statistics.stdev(memories) if len(memories) > 1 else 0.0,
        },
    }
