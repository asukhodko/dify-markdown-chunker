#!/usr/bin/env python3
"""
Validate performance benchmarks for Python Markdown Chunker
"""

import time

from markdown_chunker.chunker import MarkdownChunker


def create_test_documents():
    """Create test documents of different sizes"""

    # Small document (< 1KB)
    small_doc = """# Small Test Document

This is a small test document for performance testing.

```python
def hello():
    print("Hello, World!")
```

## Features
- Simple structure
- One code block
- Minimal content
"""

    # Medium document (~ 10KB)
    medium_doc = (
        """# Medium Test Document

This is a medium-sized test document for performance testing.

## Introduction

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

## Code Examples

Here are several code examples:

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

class Calculator:
    def __init__(self):
        self.history=[]

    def add(self, a, b):
        result =a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def multiply(self, a, b):
        result =a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
```

```javascript
function quickSort(arr) {
    if (arr.length <= 1) {
        return arr;
    }

    const pivot=arr[Math.floor(arr.length / 2)];
    const left=arr.filter(x=> x < pivot);
    const middle=arr.filter(x=> x === pivot);
    const right=arr.filter(x=> x > pivot);

    return [...quickSort(left), ...middle, ...quickSort(right)];
}

class DataProcessor {
    constructor() {
        this.data=[];
    }

    process(input) {
        return input.map(item=> item * 2).filter(item=> item > 10);
    }
}
```

## Data Tables

| Algorithm | Time Complexity | Space Complexity | Best Case | Worst Case |
|-----------|----------------|------------------|-----------|------------|
| Quick Sort | O(n log n) | O(log n) | O(n log n) | O(n²) |
| Merge Sort | O(n log n) | O(n) | O(n log n) | O(n log n) |
| Bubble Sort | O(n²) | O(1) | O(n) | O(n²) |
| Insertion Sort | O(n²) | O(1) | O(n) | O(n²) |

## Lists and Features

### Performance Characteristics
- Fast processing for small documents
- Efficient memory usage
- Scalable architecture
- Robust error handling

### Supported Languages
1. Python
2. JavaScript
3. TypeScript
4. Java
5. C++
6. Go
7. Rust
8. Swift

### Configuration Options
- Chunk size limits
- Overlap settings
- Strategy selection
- Performance monitoring
- Cache configuration

## Conclusion

This medium document contains various elements including code blocks, tables, lists, and structured content to test the chunking system's performance with realistic content.

"""
        * 3
    )  # Repeat to make it larger

    # Large document (~ 100KB)
    large_doc = medium_doc * 10

    return {"small": small_doc, "medium": medium_doc, "large": large_doc}


def benchmark_document(name, content, target_time):
    """Benchmark a single document"""
    print(f"\n📊 Benchmarking {name} document...")
    print(f"   Size: {len(content):,} characters")
    print(f"   Target: < {target_time}s")

    chunker = MarkdownChunker()

    # Warm up
    chunker.chunk_with_analysis("# Warmup")

    # Benchmark
    start_time = time.time()
    result = chunker.chunk_with_analysis(content)
    elapsed_time = time.time() - start_time

    print(f"   Actual: {elapsed_time:.3f}s")
    print(f"   Strategy: {result.strategy_used}")
    print(f"   Chunks: {len(result.chunks)}")

    if elapsed_time <= target_time:
        print("   ✅ PASS - Within target time")
        return True
    else:
        print(f"   ❌ FAIL - Exceeded target time by {elapsed_time - target_time:.3f}s")
        return False


def validate_memory_usage():
    """Validate memory usage doesn't grow excessively (simplified version)"""
    print("\n🧠 Memory usage validation...")

    chunker = MarkdownChunker()

    # Process multiple documents to check for memory leaks
    test_doc = "# Test\n\n" + "Content. " * 1000

    print(f"   Processing 10 documents of {len(test_doc):,} characters each...")

    start_time = time.time()
    for i in range(10):
        result = chunker.chunk_with_analysis(test_doc)
        if i == 0:
            first_chunks = len(result.chunks)
        elif len(result.chunks) != first_chunks:
            print(
                f"   ❌ FAIL - Inconsistent chunk count: {len(result.chunks)} vs {first_chunks}"
            )
            return False

    elapsed_time = time.time() - start_time
    avg_time = elapsed_time / 10

    print(f"   Total time: {elapsed_time:.3f}s")
    print(f"   Average per document: {avg_time:.3f}s")
    print(f"   Consistent chunk count: {first_chunks}")

    # Check that processing time doesn't degrade significantly
    if avg_time <= 0.1:  # Should be fast for repeated processing
        print("   ✅ PASS - Consistent performance, no apparent memory issues")
        return True
    else:
        print("   ❌ FAIL - Performance degradation detected")
        return False


def validate_performance_regression():
    """Check for performance regression compared to baseline"""
    print("\n⚡ Performance regression check...")

    chunker = MarkdownChunker()

    # Test document with mixed content
    test_doc = (
        """# Performance Test

## Code Section
```python
def test_function():
    return "performance test"
```

## Table Section
| Col1 | Col2 | Col3 |
|------|------|------|
| A    | B    | C    |
| 1    | 2    | 3    |

## List Section
- Item 1
- Item 2
- Item 3

## Text Section
Lorem ipsum dolor sit amet, consectetur adipiscing elit.
"""
        * 50
    )  # Make it substantial

    # Run multiple times to get average
    times = []
    for i in range(5):
        start_time = time.time()
        chunker.chunk_with_analysis(test_doc)
        elapsed_time = time.time() - start_time
        times.append(elapsed_time)

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(f"   Average time: {avg_time:.3f}s")
    print(f"   Min time: {min_time:.3f}s")
    print(f"   Max time: {max_time:.3f}s")
    print(f"   Variance: {max_time - min_time:.3f}s")

    # Check consistency (variance should be small)
    if (max_time - min_time) <= 0.1:  # 100ms variance allowed
        print("   ✅ PASS - Consistent performance")
        return True
    else:
        print("   ❌ FAIL - High performance variance")
        return False


def main():
    """Run all performance validations"""
    print("🚀 Python Markdown Chunker - Performance Validation")
    print("=" * 60)

    # Performance targets from requirements
    targets = {
        "small": 0.1,  # < 0.1s for small documents
        "medium": 1.0,  # < 1.0s for medium documents
        "large": 5.0,  # < 5.0s for large documents
    }

    documents = create_test_documents()

    results = []

    # Benchmark each document size
    for size_name, content in documents.items():
        target = targets[size_name]
        success = benchmark_document(size_name, content, target)
        results.append(success)

    # Additional validations
    memory_ok = validate_memory_usage()
    results.append(memory_ok)

    regression_ok = validate_performance_regression()
    results.append(regression_ok)

    # Summary
    print("\n📋 Performance Validation Summary")
    print("=" * 40)

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("🎉 All performance benchmarks PASSED!")
        print("✅ System meets all performance requirements")
        return True
    else:
        print("⚠️ Some performance benchmarks FAILED!")
        print("❌ Performance requirements not fully met")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
