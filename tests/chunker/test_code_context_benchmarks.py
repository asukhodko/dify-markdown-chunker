"""Performance benchmarks for code-context binding feature.

Measures the performance impact of code-context binding on chunking operations.
Target: Reasonable overhead (<100%) for significant quality improvements.
"""

import time

from markdown_chunker_v2 import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig

# Sample markdown documents for benchmarking
SIMPLE_CODE_DOC = """# Simple Example

This is a basic example.

```python
def hello():
    return "world"
```

That's all.
"""

MEDIUM_CODE_DOC = """# Tutorial

## Installation

First, you need to install the package:

```bash
pip install mypackage
```

## Basic Usage

Here's a simple example:

```python
import mypackage

result = mypackage.process()
print(result)
```

Output:

```
Processing complete!
```

## Advanced Usage

For advanced scenarios:

```python
import mypackage

# Configure with options
config = mypackage.Config(
    option1=True,
    option2="value"
)

result = mypackage.process(config)
```

This will produce better results.
"""

COMPLEX_CODE_DOC = """# Complete Guide

## Introduction

This guide covers all aspects of the library.

## Setup

### Installation

First, install dependencies:

```bash
npm install mylib
```

### Configuration

Create a config file:

```javascript
module.exports = {
    setting1: true,
    setting2: "value"
};
```

## Basic Examples

### Example 1: Simple Usage

Here's how to get started:

```javascript
const mylib = require('mylib');
const result = mylib.process();
console.log(result);
```

Output:

```
Success!
```

### Example 2: With Options

You can customize behavior:

```javascript
const mylib = require('mylib');
const result = mylib.process({
    option: 'custom'
});
```

## Refactoring

### Before

Problematic code:

```javascript
function oldWay() {
    var x = 1;
    var y = 2;
    return x + y;
}
```

### After

Improved version:

```javascript
const newWay = () => {
    const sum = 1 + 2;
    return sum;
};
```

## Error Handling

If something goes wrong:

```javascript
try {
    mylib.riskyOperation();
} catch (error) {
    console.error(error);
}
```

Error output:

```error
Error: Operation failed
    at riskyOperation (mylib.js:42)
```

## Summary

That covers the basics!
"""


class TestCodeContextBenchmarks:
    """Benchmark tests for code-context binding performance."""

    def test_comparative_performance_simple(self):
        """Compare performance: enabled vs disabled on simple doc."""
        config_disabled = ChunkConfig(enable_code_context_binding=False)
        config_enabled = ChunkConfig(enable_code_context_binding=True)

        chunker_disabled = MarkdownChunker(config=config_disabled)
        chunker_enabled = MarkdownChunker(config=config_enabled)

        # Measure disabled (baseline)
        iterations = 100
        start = time.perf_counter()
        for _ in range(iterations):
            chunker_disabled.chunk_simple(SIMPLE_CODE_DOC)
        baseline_time = time.perf_counter() - start

        # Measure enabled
        start = time.perf_counter()
        for _ in range(iterations):
            chunker_enabled.chunk_simple(SIMPLE_CODE_DOC)
        enabled_time = time.perf_counter() - start

        # Calculate overhead
        overhead_pct = ((enabled_time - baseline_time) / baseline_time) * 100

        print(f"\nSimple doc overhead: {overhead_pct:.2f}%")
        print(f"  Baseline: {baseline_time*1000:.2f}ms")
        print(f"  With binding: {enabled_time*1000:.2f}ms")

        # Target: <100% overhead (acceptable for added intelligence)
        assert overhead_pct < 100, f"Overhead too high: {overhead_pct:.2f}%"

    def test_comparative_performance_medium(self):
        """Compare performance: enabled vs disabled on medium doc."""
        config_disabled = ChunkConfig(enable_code_context_binding=False)
        config_enabled = ChunkConfig(enable_code_context_binding=True)

        chunker_disabled = MarkdownChunker(config=config_disabled)
        chunker_enabled = MarkdownChunker(config=config_enabled)

        # Measure disabled (baseline)
        iterations = 50
        start = time.perf_counter()
        for _ in range(iterations):
            chunker_disabled.chunk_simple(MEDIUM_CODE_DOC)
        baseline_time = time.perf_counter() - start

        # Measure enabled
        start = time.perf_counter()
        for _ in range(iterations):
            chunker_enabled.chunk_simple(MEDIUM_CODE_DOC)
        enabled_time = time.perf_counter() - start

        # Calculate overhead
        overhead_pct = ((enabled_time - baseline_time) / baseline_time) * 100

        print(f"\nMedium doc overhead: {overhead_pct:.2f}%")
        print(f"  Baseline: {baseline_time*1000:.2f}ms")
        print(f"  With binding: {enabled_time*1000:.2f}ms")

        # Target: <150% overhead for medium complexity docs
        assert overhead_pct < 150, f"Overhead too high: {overhead_pct:.2f}%"

    def test_comparative_performance_complex(self):
        """Compare performance: enabled vs disabled on complex doc."""
        config_disabled = ChunkConfig(enable_code_context_binding=False)
        config_enabled = ChunkConfig(enable_code_context_binding=True)

        chunker_disabled = MarkdownChunker(config=config_disabled)
        chunker_enabled = MarkdownChunker(config=config_enabled)

        # Measure disabled (baseline)
        iterations = 20
        start = time.perf_counter()
        for _ in range(iterations):
            chunker_disabled.chunk_simple(COMPLEX_CODE_DOC)
        baseline_time = time.perf_counter() - start

        # Measure enabled
        start = time.perf_counter()
        for _ in range(iterations):
            chunker_enabled.chunk_simple(COMPLEX_CODE_DOC)
        enabled_time = time.perf_counter() - start

        # Calculate overhead
        overhead_pct = ((enabled_time - baseline_time) / baseline_time) * 100

        print(f"\nComplex doc overhead: {overhead_pct:.2f}%")
        print(f"  Baseline: {baseline_time*1000:.2f}ms")
        print(f"  With binding: {enabled_time*1000:.2f}ms")

        # Target: <150% overhead for complex docs (acceptable given quality gains)
        assert overhead_pct < 150, f"Overhead too high: {overhead_pct:.2f}%"

    def test_scaling_with_code_blocks(self):
        """Test performance scaling with number of code blocks."""
        config = ChunkConfig(enable_code_context_binding=True)
        chunker = MarkdownChunker(config=config)

        # Generate documents with varying numbers of code blocks
        timings = []

        for num_blocks in [1, 5, 10, 20]:
            blocks = [
                f"```python\nblock_{i} = {i}\n```\n\nText here.\n"
                for i in range(num_blocks)
            ]
            markdown_text = "# Test\n\n" + "\n".join(blocks)

            # Time it
            iterations = 50
            start = time.perf_counter()
            for _ in range(iterations):
                chunker.chunk_simple(markdown_text)
            elapsed = time.perf_counter() - start

            avg_time = elapsed / iterations
            timings.append((num_blocks, avg_time))
            print(f"\n{num_blocks} blocks: {avg_time*1000:.2f}ms average")

        # Performance should scale roughly linearly (or sub-linearly)
        # Check that 20 blocks doesn't take more than 5x the time of 5 blocks
        time_5 = timings[1][1]  # 5 blocks
        time_20 = timings[3][1]  # 20 blocks
        ratio = time_20 / time_5

        print(f"\nScaling ratio (20 blocks / 5 blocks): {ratio:.2f}x")
        # Should scale sub-quadratically (allow up to 8x for 4x increase in blocks)
        assert ratio < 8, f"Scaling too poor: {ratio:.2f}x"


class TestMemoryUsage:
    """Test memory usage of code-context binding."""

    def test_memory_footprint_simple(self):
        """Test memory footprint on simple document."""
        import sys

        config = ChunkConfig(enable_code_context_binding=True)
        chunker = MarkdownChunker(config=config)

        result = chunker.chunk_simple(SIMPLE_CODE_DOC)

        # Check chunk sizes
        total_memory = sum(sys.getsizeof(str(chunk)) for chunk in result["chunks"])

        print(f"\nTotal memory for simple doc: {total_memory} bytes")

        # Should be reasonable (less than 10KB for simple doc)
        assert total_memory < 10000

    def test_metadata_overhead(self):
        """Test metadata memory overhead."""
        import sys

        config_disabled = ChunkConfig(enable_code_context_binding=False)
        config_enabled = ChunkConfig(enable_code_context_binding=True)

        chunker_disabled = MarkdownChunker(config=config_disabled)
        chunker_enabled = MarkdownChunker(config=config_enabled)

        result_disabled = chunker_disabled.chunk_simple(MEDIUM_CODE_DOC)
        result_enabled = chunker_enabled.chunk_simple(MEDIUM_CODE_DOC)

        # Measure metadata size
        metadata_disabled = sum(
            sys.getsizeof(str(chunk.get("metadata", {})))
            for chunk in result_disabled["chunks"]
        )
        metadata_enabled = sum(
            sys.getsizeof(str(chunk.get("metadata", {})))
            for chunk in result_enabled["chunks"]
        )

        overhead = metadata_enabled - metadata_disabled
        overhead_pct = (
            (overhead / metadata_disabled) * 100 if metadata_disabled > 0 else 0
        )

        print(f"\nMetadata overhead: {overhead} bytes ({overhead_pct:.2f}%)")

        # Metadata overhead should be reasonable (less than 200%)
        assert overhead_pct < 200


class TestQualityMetrics:
    """Test quality improvements from code-context binding."""

    def test_chunk_count_comparison(self):
        """Compare chunk counts with and without binding."""
        config_disabled = ChunkConfig(enable_code_context_binding=False)
        config_enabled = ChunkConfig(enable_code_context_binding=True)

        chunker_disabled = MarkdownChunker(config=config_disabled)
        chunker_enabled = MarkdownChunker(config=config_enabled)

        result_disabled = chunker_disabled.chunk_simple(COMPLEX_CODE_DOC)
        result_enabled = chunker_enabled.chunk_simple(COMPLEX_CODE_DOC)

        print(f"\nChunk count without binding: {result_disabled['total_chunks']}")
        print(f"Chunk count with binding: {result_enabled['total_chunks']}")

        # With binding, may have fewer chunks due to grouping
        # or similar count but better quality
        assert result_enabled["total_chunks"] > 0

    def test_metadata_richness(self):
        """Test metadata richness improvement."""
        config = ChunkConfig(enable_code_context_binding=True)
        chunker = MarkdownChunker(config=config)

        result = chunker.chunk_simple(COMPLEX_CODE_DOC)

        # Count chunks with rich metadata
        rich_metadata_count = 0
        for chunk in result["chunks"]:
            metadata = chunk.get("metadata", {})
            if "code_role" in metadata or "code_roles" in metadata:
                rich_metadata_count += 1

        print(
            f"\nChunks with rich metadata: {rich_metadata_count}/{result['total_chunks']}"
        )

        # At least some chunks should have rich metadata
        assert rich_metadata_count > 0

    def test_relationship_detection_rate(self):
        """Test how often relationships are detected."""
        config = ChunkConfig(enable_code_context_binding=True)
        chunker = MarkdownChunker(config=config)

        result = chunker.chunk_simple(COMPLEX_CODE_DOC)

        # Count chunks with relationships
        relationship_count = 0
        for chunk in result["chunks"]:
            metadata = chunk.get("metadata", {})
            if metadata.get("has_related_code", False):
                relationship_count += 1

        print(
            f"\nChunks with relationships: {relationship_count}/{result['total_chunks']}"
        )

        # Complex doc should have some relationships detected
        assert relationship_count > 0
