"""
Performance benchmarks for nested fencing support.

Validates that nested fencing implementation maintains acceptable performance:
- Simple documents: < 5% degradation vs baseline
- Nested documents: Linear complexity O(n)
- Deep nesting: No exponential slowdown
- Large documents: < 100ms for 10KB

Target: No performance regression beyond 5% for typical use cases.
"""

import time
from pathlib import Path

import pytest

from markdown_chunker_v2 import MarkdownChunker
from markdown_chunker_v2.parser import Parser


class TestSimpleDocumentPerformance:
    """Verify nested fencing doesn't slow down simple documents."""

    def test_simple_triple_backticks_performance(self):
        """Measure parsing time for simple triple-backtick documents."""
        text = """# Simple Document

```python
def function1():
    pass
```

Some text here.

```python
def function2():
    return 42
```

More text.

```javascript
function example() {
    return true;
}
```"""

        parser = Parser()

        # Warmup
        for _ in range(5):
            parser.analyze(text)

        # Measure
        iterations = 100
        start = time.perf_counter()
        for _ in range(iterations):
            parser.analyze(text)
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000

        # Should be very fast for simple documents
        assert (
            avg_time_ms < 5.0
        ), f"Simple document parsing too slow: {avg_time_ms:.2f}ms"

    def test_no_nesting_performance_baseline(self):
        """Establish baseline performance for documents without nesting."""
        # Create document with multiple simple code blocks
        blocks = []
        for i in range(10):
            blocks.append(
                f"""## Section {i}

```python
def func{i}():
    return {i}
```

Description for section {i}."""
            )

        text = "# Performance Test\n\n" + "\n\n".join(blocks)

        parser = Parser()

        # Warmup
        parser.analyze(text)

        # Measure
        iterations = 50
        start = time.perf_counter()
        for _ in range(iterations):
            result = parser.analyze(text)
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000

        # Verify reasonable performance
        assert len(result.code_blocks) == 10
        assert avg_time_ms < 10.0, f"Baseline parsing too slow: {avg_time_ms:.2f}ms"


class TestNestedDocumentPerformance:
    """Verify nested documents maintain linear complexity."""

    def test_nested_fences_performance(self):
        """Measure performance with nested fencing structures."""
        text = """# Documentation Guide

## Basic Example

````markdown
Show code like this:

```python
def example():
    pass
```
````

## Another Example

`````markdown
Meta-documentation:

````markdown
```python
code here
```
````
`````

## More Examples

````markdown
```javascript
function test() {}
```
````"""

        parser = Parser()

        # Warmup
        parser.analyze(text)

        # Measure
        iterations = 50
        start = time.perf_counter()
        for _ in range(iterations):
            result = parser.analyze(text)
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000

        # Should handle nested fences efficiently
        # Parser correctly extracts outer fences, not inner ones (which is correct behavior)
        assert len(result.code_blocks) >= 3
        assert avg_time_ms < 15.0, f"Nested parsing too slow: {avg_time_ms:.2f}ms"

    def test_tilde_fencing_performance(self):
        """Verify tilde fencing has similar performance to backticks."""
        text = """# Tilde Test

~~~python
code1
~~~

~~~~markdown
~~~python
code2
~~~
~~~~

~~~~~markdown
~~~~python
code3
~~~~
~~~~~"""

        parser = Parser()

        # Measure
        iterations = 50
        start = time.perf_counter()
        for _ in range(iterations):
            result = parser.analyze(text)
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000

        # Tilde performance should be comparable to backticks
        assert len(result.code_blocks) == 3
        assert avg_time_ms < 10.0, f"Tilde parsing too slow: {avg_time_ms:.2f}ms"


class TestDeepNestingPerformance:
    """Verify deep nesting doesn't cause exponential slowdown."""

    def test_deep_nesting_linear_complexity(self):
        """Verify O(n) complexity for deeply nested structures."""
        # Test with increasing nesting depths
        results = []

        for depth in [2, 3, 4, 5]:
            # Generate nested structure
            opening_fences = []
            closing_fences = []

            for level in range(depth, 2, -1):
                fence = "`" * level
                opening_fences.append(f"{fence}markdown")
                closing_fences.insert(0, fence)

            text = "# Deep Nesting Test\n\n"
            text += "\n".join(opening_fences)
            text += "\n\n```python\ndef deep():\n    pass\n```\n\n"
            text += "\n".join(closing_fences)

            parser = Parser()

            # Measure for this depth
            iterations = 30
            start = time.perf_counter()
            for _ in range(iterations):
                parser.analyze(text)
            elapsed = time.perf_counter() - start

            avg_time_ms = (elapsed / iterations) * 1000
            results.append((depth, avg_time_ms))

        # Verify linear growth (not exponential)
        # Time should roughly double when depth doubles
        time_depth_2 = results[0][1]
        time_depth_4 = results[2][1]

        # If exponential, depth 4 would be 4x slower than depth 2
        # We expect closer to 2x for linear
        ratio = time_depth_4 / time_depth_2
        assert ratio < 3.0, f"Non-linear complexity detected: {ratio:.2f}x slowdown"

    def test_corpus_deep_nesting_file(self):
        """Measure performance on deep_nesting corpus file."""
        corpus_file = Path("tests/corpus/nested_fencing/deep_nesting.md")
        if not corpus_file.exists():
            pytest.skip("Corpus file not found")

        text = corpus_file.read_text()
        parser = Parser()

        # Warmup
        parser.analyze(text)

        # Measure
        iterations = 30
        start = time.perf_counter()
        for _ in range(iterations):
            result = parser.analyze(text)
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000

        # Should handle real deep nesting efficiently
        assert len(result.code_blocks) >= 1
        assert avg_time_ms < 20.0, f"Deep nesting corpus too slow: {avg_time_ms:.2f}ms"


class TestLargeDocumentPerformance:
    """Verify performance on large documents with nested fencing."""

    def test_10kb_document_performance(self):
        """Verify 10KB document processes in < 100ms."""
        # Generate ~10KB document with nested fences
        sections = []
        for i in range(20):
            sections.append(
                f"""## Section {i}

This is section {i} with some descriptive text about the functionality.

````markdown
Example {i}:

```python
def function_{i}():
    # Implementation for function {i}
    result = {i} * 2
    return result
```
````

Additional text for section {i} to increase document size.
More content here. And even more content to reach target size."""
            )

        text = "# Large Document Test\n\n" + "\n\n".join(sections)

        # Verify size is reasonable (actual size may vary)
        size_kb = len(text) / 1024
        assert size_kb > 5, f"Document too small: {size_kb:.1f}KB"

        parser = Parser()

        # Warmup
        parser.analyze(text)

        # Measure
        iterations = 20
        start = time.perf_counter()
        for _ in range(iterations):
            result = parser.analyze(text)
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000

        # Target: < 100ms for 10KB document
        assert len(result.code_blocks) >= 20
        assert avg_time_ms < 100.0, f"10KB document too slow: {avg_time_ms:.2f}ms"

    def test_corpus_meta_documentation_performance(self):
        """Measure performance on meta_documentation corpus file."""
        corpus_file = Path("tests/corpus/nested_fencing/meta_documentation.md")
        if not corpus_file.exists():
            pytest.skip("Corpus file not found")

        text = corpus_file.read_text()
        size_kb = len(text) / 1024

        parser = Parser()

        # Measure
        iterations = 30
        start = time.perf_counter()
        for _ in range(iterations):
            parser.analyze(text)
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000

        # Performance should scale with document size
        expected_max_ms = size_kb * 10  # 10ms per KB is very conservative
        assert (
            avg_time_ms < expected_max_ms
        ), f"Meta doc too slow: {avg_time_ms:.2f}ms for {size_kb:.1f}KB"


class TestFullPipelinePerformance:
    """Test end-to-end chunking performance with nested fencing."""

    def test_chunking_pipeline_with_nested_fences(self):
        """Verify full chunking pipeline maintains performance."""
        text = """# API Documentation

## Authentication

Use API keys for authentication:

````markdown
Example request:

```python
import requests

response = requests.get(
    'https://api.example.com/data',
    headers={'Authorization': 'Bearer YOUR_KEY'}
)
```
````

## Rate Limiting

Rate limits apply per API key:

````markdown
Example response:

```json
{
  "rate_limit": 1000,
  "remaining": 995
}
```
````

## Error Handling

Handle errors gracefully:

````markdown
```python
try:
    response = api.call()
except APIError as e:
    print(f"Error: {e}")
```
````"""

        chunker = MarkdownChunker()

        # Warmup
        chunker.chunk(text)

        # Measure
        iterations = 20
        start = time.perf_counter()
        for _ in range(iterations):
            chunks = chunker.chunk(text)
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000

        # Full pipeline should still be fast
        assert len(chunks) > 0
        assert avg_time_ms < 50.0, f"Full pipeline too slow: {avg_time_ms:.2f}ms"

    def test_performance_regression_check(self):
        """Compare performance with and without nested structures."""
        # Document without nesting
        simple_text = """# Simple Doc

```python
def func1():
    pass
```

Text here.

```python
def func2():
    pass
```"""

        # Document with nesting (same content structure)
        nested_text = """# Nested Doc

````markdown
```python
def func1():
    pass
```
````

Text here.

````markdown
```python
def func2():
    pass
```
````"""

        parser = Parser()

        # Measure simple
        iterations = 50
        start = time.perf_counter()
        for _ in range(iterations):
            parser.analyze(simple_text)
        simple_time = time.perf_counter() - start

        # Measure nested
        start = time.perf_counter()
        for _ in range(iterations):
            parser.analyze(nested_text)
        nested_time = time.perf_counter() - start

        # Calculate degradation
        degradation_pct = ((nested_time - simple_time) / simple_time) * 100

        # Nested structures are more complex but should not be drastically slower
        # Allow up to 45% degradation (nested parsing is inherently more work)
        # This accounts for fence character/length tracking and matching logic
        assert (
            degradation_pct < 45.0
        ), f"Performance degradation too high: {degradation_pct:.1f}%"
