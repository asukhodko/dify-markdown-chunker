"""
Utility functions for benchmarking.

Provides helpers for timing, memory measurement, and test data generation.
"""

import time
import tracemalloc
from typing import Any, Callable, Dict, List, Tuple


def measure_time(func: Callable, *args, **kwargs) -> Tuple[Any, float]:
    """
    Measure execution time of a function.

    Args:
        func: Function to measure
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Tuple of (result, time_in_seconds)
    """
    start=time.time()
    result=func(*args, **kwargs)
    elapsed=time.time() - start
    return result, elapsed


def measure_memory(func: Callable, *args, **kwargs) -> Tuple[Any, float]:
    """
    Measure peak memory usage of a function.

    Args:
        func: Function to measure
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Tuple of (result, peak_memory_in_mb)
    """
    tracemalloc.start()
    result=func(*args, **kwargs)
    current, peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_mb=peak / 1024 / 1024  # Convert to MB
    return result, peak_mb


def measure_all(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """
    Measure both time and memory usage.

    Args:
        func: Function to measure
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func

    Returns:
        Dictionary with result, time, and memory metrics
    """
    tracemalloc.start()
    start=time.time()

    result=func(*args, **kwargs)

    elapsed=time.time() - start
    current, peak=tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "result": result,
        "time": elapsed,
        "memory_mb": peak / 1024 / 1024,
    }


def generate_markdown_document(size_kb: int, content_type: str="mixed") -> str:
    """
    Generate a markdown document of specified size.

    Args:
        size_kb: Target size in kilobytes
        content_type: Type of content ("text", "code", "mixed", "list", "table")

    Returns:
        Generated markdown text
    """
    if content_type == "text":
        return _generate_text_document(size_kb)
    elif content_type == "code":
        return _generate_code_document(size_kb)
    elif content_type == "list":
        return _generate_list_document(size_kb)
    elif content_type == "table":
        return _generate_table_document(size_kb)
    else:  # mixed
        return _generate_mixed_document(size_kb)


def _generate_text_document(size_kb: int) -> str:
    """Generate text-heavy document."""
    target_size=size_kb * 1024
    content=[]

    content.append("# Document Title\n\n")
    content.append("This is a comprehensive document with multiple sections.\n\n")

    section_num=1
    while len("".join(content)) < target_size:
        content.append(f"## Section {section_num}\n\n")
        content.append(
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
            "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
            "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.\n\n"
        )
        content.append(
            "Duis aute irure dolor in reprehenderit in voluptate velit esse "
            "cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat "
            "cupidatat non proident, sunt in culpa qui officia deserunt mollit.\n\n"
        )
        section_num += 1

    return "".join(content)[:target_size]


def _generate_code_document(size_kb: int) -> str:
    """Generate code-heavy document."""
    target_size=size_kb * 1024
    content=[]

    content.append("# Code Examples\n\n")

    func_num=1
    while len("".join(content)) < target_size:
        content.append(f"## Function {func_num}\n\n")
        content.append("```python\n")
        content.append(f"def example_function_{func_num}(param1, param2):\n")
        content.append('    """Example function documentation."""\n')
        content.append("    result=param1 + param2\n")
        content.append("    if result > 10:\n")
        content.append("        return result * 2\n")
        content.append("    return result\n")
        content.append("```\n\n")
        func_num += 1

    return "".join(content)[:target_size]


def _generate_list_document(size_kb: int) -> str:
    """Generate list-heavy document."""
    target_size=size_kb * 1024
    content=[]

    content.append("# Task List\n\n")

    item_num=1
    while len("".join(content)) < target_size:
        content.append(f"## Category {(item_num // 10) + 1}\n\n")
        for i in range(10):
            content.append(f"- Item {item_num}: Description of task or item\n")
            item_num += 1
        content.append("\n")

    return "".join(content)[:target_size]


def _generate_table_document(size_kb: int) -> str:
    """Generate table-heavy document."""
    target_size=size_kb * 1024
    content=[]

    content.append("# Data Tables\n\n")

    table_num=1
    while len("".join(content)) < target_size:
        content.append(f"## Table {table_num}\n\n")
        content.append("| Column 1 | Column 2 | Column 3 | Column 4 |\n")
        content.append("|----------|----------|----------|----------|\n")
        for i in range(10):
            content.append(f"| Data {i}A | Data {i}B | Data {i}C | Data {i}D |\n")
        content.append("\n")
        table_num += 1

    return "".join(content)[:target_size]


def _generate_mixed_document(size_kb: int) -> str:
    """Generate mixed content document."""
    target_size=size_kb * 1024
    content=[]

    content.append("# Mixed Content Document\n\n")
    content.append("This document contains various types of content.\n\n")

    section_num=1
    while len("".join(content)) < target_size:
        # Text section
        content.append(f"## Section {section_num}: Overview\n\n")
        content.append("Some explanatory text about this section.\n\n")

        # Code block
        content.append("```python\n")
        content.append(f"def process_{section_num}():\n")
        content.append("    return True\n")
        content.append("```\n\n")

        # List
        content.append("Key points:\n\n")
        content.append("- Point 1\n")
        content.append("- Point 2\n")
        content.append("- Point 3\n\n")

        # Table
        content.append("| Metric | Value |\n")
        content.append("|--------|-------|\n")
        content.append("| Speed  | Fast  |\n")
        content.append("| Size   | Small |\n\n")

        section_num += 1

    return "".join(content)[:target_size]


def format_size(size_bytes: int) -> str:
    """Format size in bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def format_time(seconds: float) -> str:
    """Format time in seconds to human-readable string."""
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f} μs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.2f} s"


def calculate_throughput(size_bytes: int, time_seconds: float) -> float:
    """
    Calculate throughput in KB/s.

    Args:
        size_bytes: Size of processed data in bytes
        time_seconds: Time taken in seconds

    Returns:
        Throughput in KB/s
    """
    if time_seconds == 0:
        return 0
    return (size_bytes / 1024) / time_seconds
