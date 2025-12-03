# Testing Strategy

This document provides complete specifications for the property-based test suite.

## Overview

The redesigned testing approach focuses on **WHAT the system must do** (properties) rather than **HOW it does it** (implementation details).

**Key Changes**:
- 1,853 tests → ~50 tests (-97%)
- Property-based testing with Hypothesis
- Each test runs 100+ generated examples
- Focus on 10 domain properties

## Test Organization

```
tests_v2/
├── property_tests/
│   ├── __init__.py
│   ├── test_core_properties.py          # PROP-1 through PROP-5
│   ├── test_integrity_properties.py     # PROP-6, PROP-7
│   ├── test_serialization_properties.py # PROP-8, PROP-9
│   └── test_metadata_properties.py      # PROP-10
├── unit_tests/
│   ├── test_parser.py                   # Parser edge cases
│   ├── test_strategies.py               # Strategy-specific logic
│   └── test_config.py                   # Configuration validation
├── integration_tests/
│   ├── test_integration.py              # Full pipeline
│   └── test_dify_plugin.py              # Dify integration
├── regression_tests/
│   └── test_regressions.py              # Known critical bugs
└── conftest.py                          # Shared fixtures
```

## Property Tests (10 tests × 100 examples = 1,000 scenarios)

### test_core_properties.py

**Complete Implementation**:

```python
"""
Property-based tests for core domain properties (PROP-1 through PROP-5).

These tests use Hypothesis to generate random markdown and verify
that the chunking system satisfies fundamental invariants.
"""

from hypothesis import given, strategies as st, settings, assume
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
import pytest
from typing import List

from markdown_chunker_v2 import MarkdownChunker, ChunkConfig, Chunk


# Custom strategies for generating markdown
@st.composite
def markdown_text(draw, min_size=10, max_size=10000):
    """Generate valid markdown text."""
    # Generate paragraphs
    num_paragraphs = draw(st.integers(min_value=1, max_value=20))
    paragraphs = []
    
    for _ in range(num_paragraphs):
        para_type = draw(st.sampled_from(['text', 'code', 'header', 'list']))
        
        if para_type == 'text':
            paragraphs.append(draw(st.text(min_size=10, max_size=500)))
        elif para_type == 'code':
            lang = draw(st.sampled_from(['python', 'javascript', 'java', '']))
            code_content = draw(st.text(min_size=5, max_size=200))
            paragraphs.append(f"```{lang}\n{code_content}\n```")
        elif para_type == 'header':
            level = draw(st.integers(min_value=1, max_value=6))
            header_text = draw(st.text(min_size=5, max_size=50))
            paragraphs.append(f"{'#' * level} {header_text}")
        elif para_type == 'list':
            items = draw(st.lists(st.text(min_size=5, max_size=50), min_size=1, max_size=5))
            paragraphs.append('\n'.join(f"- {item}" for item in items))
    
    return '\n\n'.join(paragraphs)


class TestCoreProperties:
    """Test suite for PROP-1 through PROP-5."""
    
    @settings(max_examples=100, deadline=5000)
    @given(markdown_text())
    def test_prop1_no_content_loss(self, markdown_text):
        """
        PROP-1: No Content Loss
        
        For any valid markdown document, concatenating all chunk contents
        (after removing overlap) must equal the original document.
        
        Mathematical definition:
        ∀ doc ∈ ValidMarkdown:
            concat(chunks) - overlaps ≡ doc
        """
        # Skip empty or very short documents
        assume(len(markdown_text.strip()) >= 10)
        
        # Chunk the document
        chunker = MarkdownChunker(ChunkConfig.default())
        result = chunker.chunk(markdown_text)
        
        # Reconstruct document from chunks
        reconstructed = self._reconstruct_document(result.chunks)
        
        # Normalize whitespace for comparison
        original_normalized = self._normalize(markdown_text)
        reconstructed_normalized = self._normalize(reconstructed)
        
        # Verify equivalence
        assert reconstructed_normalized == original_normalized, (
            f"Content loss detected!\n"
            f"Original length: {len(original_normalized)}\n"
            f"Reconstructed length: {len(reconstructed_normalized)}\n"
            f"Difference: {abs(len(original_normalized) - len(reconstructed_normalized))}"
        )
    
    @settings(max_examples=100, deadline=5000)
    @given(markdown_text())
    def test_prop2_size_bounds(self, markdown_text):
        """
        PROP-2: Size Bounds
        
        Every chunk must be ≤ max_chunk_size OR explicitly marked as oversize.
        
        Mathematical definition:
        ∀ chunk ∈ Chunks:
            len(chunk.content) ≤ config.max_chunk_size 
            ∨ chunk.metadata["allow_oversize"] = True
        """
        assume(len(markdown_text.strip()) >= 10)
        
        config = ChunkConfig.default()
        chunker = MarkdownChunker(config)
        result = chunker.chunk(markdown_text)
        
        for i, chunk in enumerate(result.chunks):
            if chunk.size > config.max_chunk_size:
                # Must be marked as oversize
                assert chunk.metadata.get("allow_oversize") is True, (
                    f"Chunk {i} exceeds max_chunk_size ({chunk.size} > {config.max_chunk_size}) "
                    f"but is not marked as allow_oversize.\n"
                    f"Content preview: {chunk.content[:100]}..."
                )
    
    @settings(max_examples=100, deadline=5000)
    @given(markdown_text())
    def test_prop3_monotonic_ordering(self, markdown_text):
        """
        PROP-3: Monotonic Ordering
        
        Chunks must appear in document order (start_line non-decreasing).
        
        Mathematical definition:
        ∀ i < j:
            chunks[i].start_line ≤ chunks[j].start_line
        """
        assume(len(markdown_text.strip()) >= 10)
        
        chunker = MarkdownChunker(ChunkConfig.default())
        result = chunker.chunk(markdown_text)
        
        for i in range(len(result.chunks) - 1):
            curr_chunk = result.chunks[i]
            next_chunk = result.chunks[i + 1]
            
            assert curr_chunk.start_line <= next_chunk.start_line, (
                f"Chunks out of order at index {i}:\n"
                f"  Chunk {i}: lines {curr_chunk.start_line}-{curr_chunk.end_line}\n"
                f"  Chunk {i+1}: lines {next_chunk.start_line}-{next_chunk.end_line}"
            )
    
    @settings(max_examples=100, deadline=5000)
    @given(markdown_text())
    def test_prop4_no_empty_chunks(self, markdown_text):
        """
        PROP-4: No Empty Chunks
        
        No chunk may be empty or contain only whitespace.
        
        Mathematical definition:
        ∀ chunk ∈ Chunks:
            chunk.content.strip() ≠ ""
        """
        assume(len(markdown_text.strip()) >= 10)
        
        chunker = MarkdownChunker(ChunkConfig.default())
        result = chunker.chunk(markdown_text)
        
        for i, chunk in enumerate(result.chunks):
            assert chunk.content.strip(), (
                f"Chunk {i} is empty or whitespace-only.\n"
                f"Content: '{chunk.content}'"
            )
    
    @settings(max_examples=100, deadline=5000)
    @given(markdown_text())
    def test_prop5_valid_line_numbers(self, markdown_text):
        """
        PROP-5: Valid Line Numbers
        
        All chunks must have start_line >= 1 and end_line >= start_line.
        
        Mathematical definition:
        ∀ chunk ∈ Chunks:
            chunk.start_line ≥ 1 ∧ chunk.end_line ≥ chunk.start_line
        """
        assume(len(markdown_text.strip()) >= 10)
        
        chunker = MarkdownChunker(ChunkConfig.default())
        result = chunker.chunk(markdown_text)
        
        for i, chunk in enumerate(result.chunks):
            assert chunk.start_line >= 1, (
                f"Chunk {i} has invalid start_line: {chunk.start_line} (must be >= 1)"
            )
            assert chunk.end_line >= chunk.start_line, (
                f"Chunk {i} has end_line ({chunk.end_line}) < start_line ({chunk.start_line})"
            )
    
    # Helper methods
    
    def _reconstruct_document(self, chunks: List[Chunk]) -> str:
        """Reconstruct document from chunks, removing overlap."""
        reconstructed = ""
        
        for i, chunk in enumerate(chunks):
            content = chunk.content
            
            # Remove overlap with previous chunk
            if i > 0 and chunk.metadata.get("has_overlap_prev"):
                overlap_size = chunk.metadata["overlap_prev_size"]
                content = content[overlap_size:]
            
            # Remove overlap with next chunk
            if i < len(chunks) - 1 and chunk.metadata.get("has_overlap_next"):
                overlap_size = chunk.metadata["overlap_next_size"]
                content = content[:-overlap_size]
            
            reconstructed += content
        
        return reconstructed
    
    def _normalize(self, text: str) -> str:
        """Normalize whitespace for comparison."""
        return text.strip().replace('\r\n', '\n')
```

### test_integrity_properties.py

```python
"""
Property-based tests for content integrity (PROP-6, PROP-7).
"""

from hypothesis import given, strategies as st, settings, assume
import re

from markdown_chunker_v2 import MarkdownChunker, ChunkConfig


@st.composite
def markdown_with_code_blocks(draw):
    """Generate markdown with code blocks."""
    blocks = []
    
    # Add some code blocks
    num_code_blocks = draw(st.integers(min_value=1, max_value=5))
    for _ in range(num_code_blocks):
        lang = draw(st.sampled_from(['python', 'javascript', 'java']))
        code = draw(st.text(min_size=10, max_size=200))
        blocks.append(f"```{lang}\n{code}\n```")
        
        # Add text between code blocks
        if draw(st.booleans()):
            text = draw(st.text(min_size=10, max_size=100))
            blocks.append(text)
    
    return '\n\n'.join(blocks)


@st.composite
def markdown_with_tables(draw):
    """Generate markdown with tables."""
    blocks = []
    
    # Add tables
    num_tables = draw(st.integers(min_value=1, max_value=3))
    for _ in range(num_tables):
        cols = draw(st.integers(min_value=2, max_value=5))
        rows = draw(st.integers(min_value=2, max_value=10))
        
        # Header row
        header = "| " + " | ".join(f"Col{i}" for i in range(cols)) + " |"
        separator = "| " + " | ".join("---" for _ in range(cols)) + " |"
        
        # Data rows
        data_rows = []
        for r in range(rows):
            row = "| " + " | ".join(f"Data{r}_{c}" for c in range(cols)) + " |"
            data_rows.append(row)
        
        table = "\n".join([header, separator] + data_rows)
        blocks.append(table)
        
        # Add text between tables
        if draw(st.booleans()):
            text = draw(st.text(min_size=10, max_size=100))
            blocks.append(text)
    
    return '\n\n'.join(blocks)


class TestIntegrityProperties:
    """Test suite for PROP-6 and PROP-7."""
    
    @settings(max_examples=100, deadline=5000)
    @given(markdown_with_code_blocks())
    def test_prop6_code_block_integrity(self, markdown_text):
        """
        PROP-6: Code Block Integrity
        
        Every code block must appear intact in exactly one chunk.
        
        Mathematical definition:
        ∀ code_block ∈ doc.code_blocks:
            ∃! chunk ∈ Chunks: code_block ⊆ chunk.content
        """
        assume(len(markdown_text.strip()) >= 10)
        
        # Extract all code blocks from original
        code_blocks = self._extract_code_blocks(markdown_text)
        assume(len(code_blocks) > 0)  # Skip if no code blocks
        
        # Chunk the document
        chunker = MarkdownChunker(ChunkConfig.default())
        result = chunker.chunk(markdown_text)
        
        # Verify each code block appears intact in exactly one chunk
        for code_block in code_blocks:
            chunks_containing = [
                chunk for chunk in result.chunks
                if code_block in chunk.content
            ]
            
            assert len(chunks_containing) == 1, (
                f"Code block appears in {len(chunks_containing)} chunks (expected 1).\n"
                f"Code block: {code_block[:100]}..."
            )
    
    @settings(max_examples=100, deadline=5000)
    @given(markdown_with_tables())
    def test_prop7_table_integrity(self, markdown_text):
        """
        PROP-7: Table Integrity
        
        Every table must appear intact in exactly one chunk.
        
        Mathematical definition:
        ∀ table ∈ doc.tables:
            ∃! chunk ∈ Chunks: table ⊆ chunk.content
        """
        assume(len(markdown_text.strip()) >= 10)
        
        # Extract all tables from original
        tables = self._extract_tables(markdown_text)
        assume(len(tables) > 0)  # Skip if no tables
        
        # Chunk the document
        chunker = MarkdownChunker(ChunkConfig.default())
        result = chunker.chunk(markdown_text)
        
        # Verify each table appears intact in exactly one chunk
        for table in tables:
            chunks_containing = [
                chunk for chunk in result.chunks
                if table in chunk.content
            ]
            
            assert len(chunks_containing) == 1, (
                f"Table appears in {len(chunks_containing)} chunks (expected 1).\n"
                f"Table: {table[:100]}..."
            )
    
    # Helper methods
    
    def _extract_code_blocks(self, text: str) -> list:
        """Extract all code blocks from markdown."""
        pattern = r'```[\w]*\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches
    
    def _extract_tables(self, text: str) -> list:
        """Extract all tables from markdown."""
        tables = []
        lines = text.split('\n')
        
        in_table = False
        current_table = []
        
        for line in lines:
            if '|' in line:
                current_table.append(line)
                in_table = True
            elif in_table:
                # Table ended
                tables.append('\n'.join(current_table))
                current_table = []
                in_table = False
        
        # Add last table if still in progress
        if current_table:
            tables.append('\n'.join(current_table))
        
        return tables
```

### test_serialization_properties.py

```python
"""
Property-based tests for serialization (PROP-8, PROP-9).
"""

from hypothesis import given, settings
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig
from .test_core_properties import markdown_text


class TestSerializationProperties:
    """Test suite for PROP-8 and PROP-9."""
    
    @settings(max_examples=100, deadline=5000)
    @given(markdown_text())
    def test_prop8_serialization_roundtrip(self, markdown_text):
        """
        PROP-8: Serialization Round-Trip
        
        Serializing to dict and back must preserve data.
        
        Mathematical definition:
        ∀ result ∈ ChunkingResult:
            ChunkingResult.from_dict(result.to_dict()) ≡ result
        """
        from hypothesis import assume
        assume(len(markdown_text.strip()) >= 10)
        
        # Chunk document
        chunker = MarkdownChunker(ChunkConfig.default())
        result = chunker.chunk(markdown_text)
        
        # Serialize to dict
        result_dict = result.to_dict()
        
        # Deserialize back
        from markdown_chunker_v2.types import ChunkingResult
        restored = ChunkingResult.from_dict(result_dict)
        
        # Verify equivalence
        assert len(restored.chunks) == len(result.chunks)
        assert restored.strategy_used == result.strategy_used
        
        # Check each chunk
        for original, restored_chunk in zip(result.chunks, restored.chunks):
            assert original.content == restored_chunk.content
            assert original.start_line == restored_chunk.start_line
            assert original.end_line == restored_chunk.end_line
    
    @settings(max_examples=100, deadline=5000)
    @given(markdown_text())
    def test_prop9_idempotence(self, markdown_text):
        """
        PROP-9: Idempotence
        
        Chunking same document twice must produce identical results.
        
        Mathematical definition:
        ∀ doc, config:
            chunk(doc, config) ≡ chunk(doc, config)
        """
        from hypothesis import assume
        assume(len(markdown_text.strip()) >= 10)
        
        config = ChunkConfig.default()
        chunker = MarkdownChunker(config)
        
        # Chunk twice
        result1 = chunker.chunk(markdown_text)
        result2 = chunker.chunk(markdown_text)
        
        # Verify identical results
        assert len(result1.chunks) == len(result2.chunks), (
            "Different chunk count between runs"
        )
        
        for i, (chunk1, chunk2) in enumerate(zip(result1.chunks, result2.chunks)):
            assert chunk1.content == chunk2.content, (
                f"Chunk {i} content differs between runs"
            )
            assert chunk1.start_line == chunk2.start_line
            assert chunk1.end_line == chunk2.end_line
```

## Running Tests

### Command-Line Usage

```bash
# Run all property tests
pytest tests_v2/property_tests/ -v

# Run with statistics
pytest tests_v2/property_tests/ --hypothesis-show-statistics

# Run specific property
pytest tests_v2/property_tests/test_core_properties.py::TestCoreProperties::test_prop1_no_content_loss -v

# Run with more examples (thorough testing)
pytest tests_v2/property_tests/ --hypothesis-max-examples=500

# Run with seed (reproducible)
pytest tests_v2/property_tests/ --hypothesis-seed=12345
```

### Expected Output

```
tests_v2/property_tests/test_core_properties.py::TestCoreProperties::test_prop1_no_content_loss PASSED [100 examples]
tests_v2/property_tests/test_core_properties.py::TestCoreProperties::test_prop2_size_bounds PASSED [100 examples]
tests_v2/property_tests/test_core_properties.py::TestCoreProperties::test_prop3_monotonic_ordering PASSED [100 examples]
tests_v2/property_tests/test_core_properties.py::TestCoreProperties::test_prop4_no_empty_chunks PASSED [100 examples]
tests_v2/property_tests/test_core_properties.py::TestCoreProperties::test_prop5_valid_line_numbers PASSED [100 examples]
tests_v2/property_tests/test_integrity_properties.py::TestIntegrityProperties::test_prop6_code_block_integrity PASSED [100 examples]
tests_v2/property_tests/test_integrity_properties.py::TestIntegrityProperties::test_prop7_table_integrity PASSED [100 examples]
tests_v2/property_tests/test_serialization_properties.py::TestSerializationProperties::test_prop8_serialization_roundtrip PASSED [100 examples]
tests_v2/property_tests/test_serialization_properties.py::TestSerializationProperties::test_prop9_idempotence PASSED [100 examples]

========== 10 passed, 1000 examples total in 15.23s ==========
```

## Success Criteria

- ✓ All 10 property tests pass
- ✓ Each test runs 100+ examples
- ✓ No flaky tests (deterministic)
- ✓ Fast execution (< 30s for full suite)
- ✓ Clear failure messages

This property-based approach provides far stronger guarantees than the old 1,853 implementation-focused tests!
