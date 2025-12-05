"""
V2 Test Implementation: Integration Tests

Implements test specifications SPEC-020 to SPEC-022 from
docs/v2-test-specification/v2-test-specification.md

Tests integration scenarios:
- SPEC-020: End-to-End Pipeline
- SPEC-021: Serialization Roundtrip
- SPEC-022: Error Recovery
"""

import json
import pytest
from hypothesis import given, settings, strategies as st, HealthCheck

from markdown_chunker_v2.chunker import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig
from markdown_chunker_v2.types import Chunk


# =============================================================================
# SPEC-020: End-to-End Pipeline
# =============================================================================

class TestSPEC020EndToEndPipeline:
    """
    SPEC-020: End-to-End Pipeline
    
    **Feature: v2-test-implementation, Integration: Full pipeline**
    **Validates: Requirements 2.1, 5.4**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-020
    """
    
    def test_full_pipeline_simple_document(self):
        """Test complete chunking workflow with simple document."""
        chunker = MarkdownChunker()
        text = """# Introduction

This is a sample document with various elements.

## Code Example

```python
def hello():
    print("Hello, world!")
```

## Table

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |

## Conclusion

This concludes our example.
"""
        chunks = chunker.chunk(text)
        
        # Validate basic properties
        assert len(chunks) > 0
        assert all(chunk.content.strip() for chunk in chunks)
        
        # Validate content preservation
        all_content = ''.join(chunk.content for chunk in chunks)
        assert 'Introduction' in all_content
        assert 'def hello' in all_content
        assert 'Column 1' in all_content
        assert 'Conclusion' in all_content
        
        # Validate metadata
        for chunk in chunks:
            assert 'strategy' in chunk.metadata
            assert 'chunk_index' in chunk.metadata
            assert chunk.start_line >= 1
            assert chunk.end_line >= chunk.start_line
    
    def test_full_pipeline_code_heavy_document(self):
        """Test pipeline with code-heavy document."""
        chunker = MarkdownChunker()
        text = """# API Reference

```python
class MyClass:
    def __init__(self):
        self.value = 0
    
    def increment(self):
        self.value += 1
        return self.value
```

Usage example:

```python
obj = MyClass()
print(obj.increment())  # 1
print(obj.increment())  # 2
```
"""
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        
        # Code should be preserved
        all_content = ''.join(chunk.content for chunk in chunks)
        assert 'class MyClass' in all_content
        assert 'def increment' in all_content
    
    def test_full_pipeline_with_config(self):
        """Test pipeline with custom configuration."""
        config = ChunkConfig(
            max_chunk_size=500,
            min_chunk_size=50,
            overlap_size=50
        )
        chunker = MarkdownChunker(config)
        
        text = "Paragraph. " * 100
        chunks = chunker.chunk(text)
        
        assert len(chunks) > 0
        
        # Check size constraints
        for chunk in chunks:
            assert chunk.size <= 500 or chunk.is_oversize
    
    def test_chunk_with_metrics(self):
        """Test chunk_with_metrics returns valid metrics."""
        chunker = MarkdownChunker()
        text = "# Header\n\nContent here.\n\n## Another\n\nMore content."
        
        chunks, metrics = chunker.chunk_with_metrics(text)
        
        assert len(chunks) > 0
        assert metrics.total_chunks == len(chunks)
        assert metrics.avg_chunk_size > 0
    
    def test_chunk_with_analysis(self):
        """Test chunk_with_analysis returns analysis info."""
        chunker = MarkdownChunker()
        text = "# Header\n\n```python\ncode\n```"
        
        chunks, strategy_name, analysis = chunker.chunk_with_analysis(text)
        
        assert len(chunks) > 0
        assert strategy_name in ['code_aware', 'structural', 'fallback']
        assert analysis is not None
        assert analysis.header_count >= 1


# =============================================================================
# SPEC-021: Serialization Roundtrip
# =============================================================================

class TestSPEC021SerializationRoundtrip:
    """
    SPEC-021: Serialization Roundtrip
    
    **Feature: v2-test-implementation, Property 7: Serialization roundtrip**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-021
    """
    
    def test_to_dict_from_dict_roundtrip(self):
        """Test Chunk.to_dict() and Chunk.from_dict() roundtrip."""
        original = Chunk(
            content="Test content",
            start_line=1,
            end_line=5,
            metadata={"key": "value", "number": 42}
        )
        
        # Roundtrip
        data = original.to_dict()
        restored = Chunk.from_dict(data)
        
        assert restored.content == original.content
        assert restored.start_line == original.start_line
        assert restored.end_line == original.end_line
        assert restored.metadata == original.metadata
    
    def test_to_json_from_json_roundtrip(self):
        """Test Chunk.to_json() and Chunk.from_json() roundtrip."""
        original = Chunk(
            content="Test content with unicode: 日本語",
            start_line=10,
            end_line=20,
            metadata={"strategy": "test", "index": 0}
        )
        
        # Roundtrip
        json_str = original.to_json()
        restored = Chunk.from_json(json_str)
        
        assert restored.content == original.content
        assert restored.start_line == original.start_line
        assert restored.end_line == original.end_line
    
    def test_chunking_result_serialization(self):
        """Test chunking results can be serialized and restored."""
        chunker = MarkdownChunker()
        text = "# Header\n\nContent here."
        chunks = chunker.chunk(text)
        
        # Serialize all chunks
        serialized = [c.to_dict() for c in chunks]
        json_str = json.dumps(serialized)
        
        # Restore
        restored_data = json.loads(json_str)
        restored_chunks = [Chunk.from_dict(d) for d in restored_data]
        
        assert len(restored_chunks) == len(chunks)
        for orig, rest in zip(chunks, restored_chunks):
            assert orig.content == rest.content
    
    @given(st.text(min_size=1, max_size=200).filter(lambda x: x.strip()))
    @settings(max_examples=30, deadline=5000, suppress_health_check=[HealthCheck.filter_too_much])
    def test_roundtrip_property(self, content: str):
        """Property: Serialization roundtrip preserves chunk data."""
        original = Chunk(
            content=content,
            start_line=1,
            end_line=max(1, content.count('\n') + 1),
            metadata={"test": True}
        )
        
        # Dict roundtrip
        restored_dict = Chunk.from_dict(original.to_dict())
        assert restored_dict.content == original.content
        
        # JSON roundtrip
        restored_json = Chunk.from_json(original.to_json())
        assert restored_json.content == original.content
    
    def test_from_dict_missing_fields(self):
        """Test from_dict raises error for missing required fields."""
        with pytest.raises(ValueError, match="Missing required field: content"):
            Chunk.from_dict({"start_line": 1, "end_line": 1})
        
        with pytest.raises(ValueError, match="Missing required field: start_line"):
            Chunk.from_dict({"content": "test", "end_line": 1})
    
    def test_from_json_invalid_json(self):
        """Test from_json raises error for invalid JSON."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            Chunk.from_json("not valid json")


# =============================================================================
# SPEC-022: Error Recovery
# =============================================================================

class TestSPEC022ErrorRecovery:
    """
    SPEC-022: Error Recovery
    
    **Feature: v2-test-implementation, Unit: Error recovery**
    **Validates: Requirements 3.1, 5.2**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-022
    """
    
    def test_empty_input_handled(self):
        """Test empty input is handled gracefully."""
        chunker = MarkdownChunker()
        
        # Should not raise
        result = chunker.chunk("")
        assert result == []
        
        result = chunker.chunk("   ")
        assert result == []
    
    def test_chunk_simple_error_handling(self):
        """Test chunk_simple handles errors gracefully."""
        chunker = MarkdownChunker()
        
        # Valid input
        result = chunker.chunk_simple("Test content")
        assert 'chunks' in result
        assert 'errors' in result
        assert len(result['errors']) == 0
    
    def test_chunk_simple_with_invalid_config(self):
        """Test chunk_simple with invalid config returns error."""
        chunker = MarkdownChunker()
        
        # This should handle the error gracefully
        result = chunker.chunk_simple("Test", config={'max_chunk_size': -1})
        
        # Should have error
        assert len(result['errors']) > 0 or result['total_chunks'] == 0
    
    def test_malformed_markdown_handled(self):
        """Test malformed markdown is handled gracefully."""
        chunker = MarkdownChunker()
        
        # Unclosed code block
        text = "```python\ncode without closing"
        result = chunker.chunk(text)
        # Should not crash, may produce chunks
        assert isinstance(result, list)
        
        # Malformed table
        text = "| incomplete table"
        result = chunker.chunk(text)
        assert isinstance(result, list)
    
    def test_very_long_input_handled(self):
        """Test very long input is handled."""
        chunker = MarkdownChunker()
        
        # 100KB of text
        text = "Word " * 20000
        result = chunker.chunk(text)
        
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_unicode_input_handled(self):
        """Test unicode input is handled correctly."""
        chunker = MarkdownChunker()
        
        text = """# Заголовок

Текст на русском языке.

## 日本語

日本語のテキスト。

## Emoji

🎉 🚀 ✨
"""
        result = chunker.chunk(text)
        
        assert len(result) > 0
        all_content = ''.join(c.content for c in result)
        assert 'Заголовок' in all_content
        assert '日本語' in all_content
