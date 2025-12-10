"""Integration tests for code-context binding in CodeAwareStrategy.

Tests the integration of CodeContextBinder with the chunking workflow,
including grouping of related blocks and metadata enrichment.
"""

from markdown_chunker_v2 import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig
from markdown_chunker_v2.parser import Parser
from markdown_chunker_v2.strategies.code_aware import CodeAwareStrategy


class TestCodeContextIntegration:
    """Test code-context binding integration with CodeAwareStrategy."""

    def test_feature_flag_disabled(self):
        """Test that context binding is disabled when feature flag is False."""
        md_text = """# Example

First, install the package:

```python
pip install mypackage
```

Output:

```
Successfully installed mypackage
```
"""
        config = ChunkConfig(enable_code_context_binding=False)
        parser = Parser()
        analysis = parser.analyze(md_text)
        strategy = CodeAwareStrategy()

        chunks = strategy.apply(md_text, analysis, config)

        # Should have chunks but without context metadata
        assert len(chunks) >= 1
        code_chunks = [c for c in chunks if c.metadata.get("content_type") == "code"]
        assert len(code_chunks) >= 1

        # Should not have context metadata
        for chunk in code_chunks:
            assert "code_role" not in chunk.metadata
            assert "has_related_code" not in chunk.metadata

    def test_feature_flag_enabled(self):
        """Test that context binding works when feature flag is True."""
        md_text = """# Example

First, install the package:

```python
pip install mypackage
```

Output:

```
Successfully installed mypackage
```
"""
        config = ChunkConfig(enable_code_context_binding=True)
        parser = Parser()
        analysis = parser.analyze(md_text)
        strategy = CodeAwareStrategy()

        chunks = strategy.apply(md_text, analysis, config)

        # Should have chunks with context metadata
        assert len(chunks) >= 1
        code_chunks = [c for c in chunks if c.metadata.get("content_type") == "code"]
        assert len(code_chunks) >= 1

        # Should have context metadata
        found_role = False
        for chunk in code_chunks:
            if "code_role" in chunk.metadata:
                found_role = True
                break
        assert found_role, "At least one code chunk should have role metadata"

    def test_single_code_block_metadata(self):
        """Test metadata enrichment for single code block."""
        md_text = """# Example

This is an example:

```python
print("Hello, World!")
```

This demonstrates basic output.
"""
        config = ChunkConfig(enable_code_context_binding=True)
        parser = Parser()
        analysis = parser.analyze(md_text)
        strategy = CodeAwareStrategy()

        chunks = strategy.apply(md_text, analysis, config)

        code_chunks = [c for c in chunks if c.metadata.get("content_type") == "code"]
        assert len(code_chunks) >= 1

        code_chunk = code_chunks[0]
        assert "code_role" in code_chunk.metadata
        assert "explanation_bound" in code_chunk.metadata
        assert "context_scope" in code_chunk.metadata

    def test_before_after_pairing(self):
        """Test Before/After code block pairing."""
        md_text = """# Refactoring Example

Before:

```python
def old_function():
    x = 1
    return x
```

After:

```python
def new_function():
    return 1
```
"""
        config = ChunkConfig(
            enable_code_context_binding=True,
            preserve_before_after_pairs=True,
        )
        parser = Parser()
        analysis = parser.analyze(md_text)
        strategy = CodeAwareStrategy()

        chunks = strategy.apply(md_text, analysis, config)

        # Look for grouped chunks - should be grouped into single chunk
        code_chunks = [c for c in chunks if c.metadata.get("content_type") == "code"]

        # Should have chunks with before/after relationship
        # May be grouped together or separate
        has_before_after_relationship = any(
            c.metadata.get("code_relationship") == "before_after" for c in code_chunks
        )

        # Check for before/after roles (either in grouped or separate chunks)
        all_roles = []
        for c in code_chunks:
            if "code_roles" in c.metadata:
                all_roles.extend(c.metadata["code_roles"])
            elif "code_role" in c.metadata:
                all_roles.append(c.metadata["code_role"])

        assert has_before_after_relationship or (
            "before" in all_roles and "after" in all_roles
        )

    def test_code_output_pairing(self):
        """Test Code + Output block pairing."""
        md_text = """# Output Example

Run this code:

```python
print("Hello")
```

Output:

```
Hello
```
"""
        config = ChunkConfig(
            enable_code_context_binding=True,
            bind_output_blocks=True,
        )
        parser = Parser()
        analysis = parser.analyze(md_text)
        strategy = CodeAwareStrategy()

        chunks = strategy.apply(md_text, analysis, config)

        code_chunks = [c for c in chunks if c.metadata.get("content_type") == "code"]
        assert len(code_chunks) >= 1

        # Check for code/output relationship (may be grouped or has output metadata)
        has_code_output_relationship = any(
            c.metadata.get("code_relationship") == "code_output" for c in code_chunks
        )
        has_output_metadata = any(
            c.metadata.get("has_output_block", False) for c in code_chunks
        )

        # Check for output role in grouped chunks
        has_output_role = False
        for c in code_chunks:
            if "code_roles" in c.metadata:
                if "output" in c.metadata["code_roles"]:
                    has_output_role = True

        assert has_code_output_relationship or has_output_metadata or has_output_role

    def test_setup_code_detection(self):
        """Test detection of setup/installation code."""
        md_text = """# Installation

First, you need to install the dependencies:

```bash
npm install react
```

Then use it in your code:

```javascript
import React from 'react';
```
"""
        config = ChunkConfig(enable_code_context_binding=True)
        parser = Parser()
        analysis = parser.analyze(md_text)
        strategy = CodeAwareStrategy()

        chunks = strategy.apply(md_text, analysis, config)

        code_chunks = [c for c in chunks if c.metadata.get("content_type") == "code"]
        assert len(code_chunks) >= 2

        # First block should be setup
        roles = [c.metadata.get("code_role", "") for c in code_chunks]
        assert "setup" in roles or "example" in roles

    def test_backward_compatibility(self):
        """Test backward compatibility with existing chunking behavior."""
        md_text = """# Simple Example

```python
def hello():
    return "world"
```

Some text here.
"""
        # Test with feature disabled
        config_disabled = ChunkConfig(enable_code_context_binding=False)
        parser = Parser()
        analysis = parser.analyze(md_text)
        strategy = CodeAwareStrategy()

        chunks_disabled = strategy.apply(md_text, analysis, config_disabled)

        # Test with feature enabled
        config_enabled = ChunkConfig(enable_code_context_binding=True)
        chunks_enabled = strategy.apply(md_text, analysis, config_enabled)

        # Should have same number of chunks
        assert len(chunks_disabled) == len(chunks_enabled)

        # Content should be identical
        for i in range(len(chunks_disabled)):
            assert chunks_disabled[i].content == chunks_enabled[i].content

    def test_mixed_code_and_tables(self):
        """Test handling of documents with both code and tables."""
        md_text = """# Mixed Content

Code example:

```python
x = 1
```

Table:

| A | B |
|---|---|
| 1 | 2 |

More code:

```python
y = 2
```
"""
        config = ChunkConfig(enable_code_context_binding=True)
        parser = Parser()
        analysis = parser.analyze(md_text)
        strategy = CodeAwareStrategy()

        chunks = strategy.apply(md_text, analysis, config)

        # Should have both code and table chunks
        code_chunks = [c for c in chunks if c.metadata.get("content_type") == "code"]
        table_chunks = [c for c in chunks if c.metadata.get("content_type") == "table"]

        assert len(code_chunks) >= 2
        assert len(table_chunks) >= 1

        # Code chunks should have context metadata
        for chunk in code_chunks:
            assert "code_role" in chunk.metadata

        # Table chunks should not have code context metadata
        for chunk in table_chunks:
            assert "code_role" not in chunk.metadata

    def test_empty_document(self):
        """Test handling of empty document."""
        md_text = ""
        config = ChunkConfig(enable_code_context_binding=True)
        parser = Parser()
        analysis = parser.analyze(md_text)
        strategy = CodeAwareStrategy()

        chunks = strategy.apply(md_text, analysis, config)
        assert len(chunks) == 0

    def test_document_without_code(self):
        """Test document with no code blocks."""
        md_text = """# Text Only

This document has no code blocks.

Just regular text content.
"""
        config = ChunkConfig(enable_code_context_binding=True)
        parser = Parser()
        analysis = parser.analyze(md_text)
        strategy = CodeAwareStrategy()

        chunks = strategy.apply(md_text, analysis, config)

        # Should still create chunks, but no code chunks
        assert len(chunks) >= 1
        code_chunks = [c for c in chunks if c.metadata.get("content_type") == "code"]
        assert len(code_chunks) == 0

    def test_configurable_context_chars(self):
        """Test configurable context extraction limits."""
        md_text = (
            """# Example

This is a very long explanation before the code block. """
            + ("More text. " * 50)
            + """

```python
print("test")
```

And more explanation after.
"""
        )
        config = ChunkConfig(
            enable_code_context_binding=True,
            max_context_chars_before=100,
            max_context_chars_after=50,
        )
        parser = Parser()
        analysis = parser.analyze(md_text)
        strategy = CodeAwareStrategy()

        chunks = strategy.apply(md_text, analysis, config)

        code_chunks = [c for c in chunks if c.metadata.get("content_type") == "code"]
        assert len(code_chunks) >= 1

        # Should have metadata about bound context
        assert code_chunks[0].metadata.get("explanation_bound", False)

    def test_configurable_block_gap(self):
        """Test configurable max gap for related blocks."""
        md_text = """# Sequential Examples

```python
# Example 1
x = 1
```

Some text here.
And more text.
And more text.
And more text.
And more text.

```python
# Example 2
y = 2
```
"""
        # Test with large gap
        config_large_gap = ChunkConfig(
            enable_code_context_binding=True,
            related_block_max_gap=10,
        )
        parser = Parser()
        analysis = parser.analyze(md_text)
        strategy = CodeAwareStrategy()

        chunks_large = strategy.apply(md_text, analysis, config_large_gap)

        # Test with small gap
        config_small_gap = ChunkConfig(
            enable_code_context_binding=True,
            related_block_max_gap=2,
        )
        chunks_small = strategy.apply(md_text, analysis, config_small_gap)

        # Both should produce chunks, but grouping may differ
        assert len(chunks_large) >= 1
        assert len(chunks_small) >= 1


class TestCodeContextEndToEnd:
    """End-to-end tests using MarkdownChunker."""

    def test_e2e_chunk_simple_with_context_binding(self):
        """Test chunk_simple with code-context binding enabled."""
        chunker = MarkdownChunker()

        md_text = """# Tutorial

Before:

```python
old_code = True
```

After:

```python
new_code = True
```
"""
        result = chunker.chunk_simple(
            md_text, config={"enable_code_context_binding": True}
        )

        assert result["total_chunks"] >= 1
        assert len(result["errors"]) == 0

        # Check for context metadata in chunks
        code_chunks = [
            c
            for c in result["chunks"]
            if c.get("metadata", {}).get("content_type") == "code"
        ]
        assert len(code_chunks) >= 1

    def test_e2e_chunk_with_analysis(self):
        """Test chunk_with_analysis with code-context binding."""
        chunker = MarkdownChunker(config=ChunkConfig(enable_code_context_binding=True))

        md_text = """# Example

Setup:

```bash
pip install mylib
```

Usage:

```python
import mylib
```
"""
        chunks, strategy_used, analysis = chunker.chunk_with_analysis(md_text)

        assert len(chunks) >= 1
        assert strategy_used == "code_aware"
        assert analysis.code_block_count >= 2

        # Check metadata
        code_chunks = [c for c in chunks if c.metadata.get("content_type") == "code"]
        assert len(code_chunks) >= 2

        # At least one should have role metadata
        roles = [c.metadata.get("code_role") for c in code_chunks]
        assert any(role is not None for role in roles)

    def test_e2e_complex_document(self):
        """Test complex document with multiple patterns."""
        chunker = MarkdownChunker(
            config=ChunkConfig(
                enable_code_context_binding=True,
                preserve_before_after_pairs=True,
                bind_output_blocks=True,
            )
        )

        md_text = """# Complex Tutorial

## Installation

First, you need to install:

```bash
npm install mypackage
```

## Basic Usage

Here's a simple example:

```javascript
const pkg = require('mypackage');
console.log('Hello');
```

Output:

```
Hello
```

## Refactoring

Before:

```javascript
function oldWay() {
    return 1;
}
```

After:

```javascript
const newWay = () => 1;
```

## Summary

That's it!
"""
        chunks, strategy_used, analysis = chunker.chunk_with_analysis(md_text)

        assert len(chunks) >= 1
        assert strategy_used == "code_aware"

        code_chunks = [c for c in chunks if c.metadata.get("content_type") == "code"]
        # May be grouped into fewer chunks
        assert len(code_chunks) >= 1

        # Check for various roles in grouped or individual chunks
        all_roles = []
        for c in code_chunks:
            if "code_roles" in c.metadata:
                all_roles.extend(c.metadata["code_roles"])
            elif "code_role" in c.metadata:
                all_roles.append(c.metadata["code_role"])

        # Should have mix of roles (setup, example, output, before, after)
        assert len(set(all_roles)) >= 2  # At least 2 different roles
