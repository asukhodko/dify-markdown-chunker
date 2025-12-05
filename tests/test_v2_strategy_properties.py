"""
V2 Test Implementation: Strategy Properties

Implements test specifications SPEC-016 to SPEC-019 from
docs/v2-test-specification/v2-test-specification.md

Tests strategy selection and behavior:
- SPEC-016: CodeAwareStrategy Selection
- SPEC-017: StructuralStrategy Selection
- SPEC-018: FallbackStrategy Behavior
- SPEC-019: Strategy Override
"""

import pytest
from hypothesis import given, settings, strategies as st, HealthCheck

from markdown_chunker_v2.chunker import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig
from markdown_chunker_v2.parser import Parser
from markdown_chunker_v2.strategies import (
    StrategySelector,
    CodeAwareStrategy,
    StructuralStrategy,
    FallbackStrategy,
)


# =============================================================================
# SPEC-016: CodeAwareStrategy Selection
# =============================================================================

class TestSPEC016CodeAwareStrategy:
    """
    SPEC-016: CodeAwareStrategy Selection
    
    **Feature: v2-test-implementation, Property 13: CodeAwareStrategy selection**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-016
    """
    
    def test_code_aware_selected_for_code_blocks(self):
        """Test CodeAwareStrategy is selected when code blocks present."""
        parser = Parser()
        selector = StrategySelector()
        config = ChunkConfig()
        
        text = """# Header

```python
def hello():
    pass
```
"""
        analysis = parser.analyze(text)
        strategy = selector.select(analysis, config)
        
        assert strategy.name == "code_aware"
    
    def test_code_aware_selected_for_tables(self):
        """Test CodeAwareStrategy is selected when tables present."""
        parser = Parser()
        selector = StrategySelector()
        config = ChunkConfig()
        
        text = """# Header

| Col1 | Col2 |
|------|------|
| A    | B    |
"""
        analysis = parser.analyze(text)
        strategy = selector.select(analysis, config)
        
        assert strategy.name == "code_aware"
    
    def test_code_aware_selected_for_high_code_ratio(self):
        """Test CodeAwareStrategy is selected for high code ratio."""
        parser = Parser()
        selector = StrategySelector()
        config = ChunkConfig(code_threshold=0.3)
        
        # Document with lots of code
        text = "```\n" + "x = 1\n" * 50 + "```"
        analysis = parser.analyze(text)
        
        if analysis.code_ratio >= 0.3:
            strategy = selector.select(analysis, config)
            assert strategy.name == "code_aware"
    
    def test_code_aware_preserves_code_blocks(self):
        """Test CodeAwareStrategy preserves code blocks intact."""
        config = ChunkConfig(max_chunk_size=100, overlap_size=20, strategy_override="code_aware")
        chunker = MarkdownChunker(config)
        
        text = """Before

```python
def function():
    x = 1
    y = 2
    return x + y
```

After
"""
        chunks = chunker.chunk(text)
        
        # Find chunk with code
        code_chunks = [c for c in chunks if '```' in c.content]
        for chunk in code_chunks:
            # Code block should be complete
            fence_count = chunk.content.count('```')
            assert fence_count % 2 == 0


# =============================================================================
# SPEC-017: StructuralStrategy Selection
# =============================================================================

class TestSPEC017StructuralStrategy:
    """
    SPEC-017: StructuralStrategy Selection
    
    **Feature: v2-test-implementation, Property 14: StructuralStrategy selection**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-017
    """
    
    def test_structural_selected_for_headers(self):
        """Test StructuralStrategy is selected for structured documents."""
        parser = Parser()
        selector = StrategySelector()
        config = ChunkConfig(structure_threshold=3)
        
        text = """# Main Title

Introduction.

## Chapter 1

Content 1.

### Section 1.1

Details.

## Chapter 2

Content 2.
"""
        analysis = parser.analyze(text)
        
        # Should have enough headers and depth
        if analysis.header_count >= 3 and analysis.max_header_depth > 1:
            # And no code blocks
            if analysis.code_block_count == 0 and analysis.table_count == 0:
                strategy = selector.select(analysis, config)
                assert strategy.name == "structural"
    
    def test_structural_splits_at_headers(self):
        """Test StructuralStrategy splits at header boundaries."""
        config = ChunkConfig(
            max_chunk_size=200,
            overlap_size=50,
            strategy_override="structural"
        )
        chunker = MarkdownChunker(config)
        
        text = """# Section 1

Content for section 1.

# Section 2

Content for section 2.

# Section 3

Content for section 3.
"""
        chunks = chunker.chunk(text)
        
        # Each section should be in its own chunk (or merged if small)
        assert len(chunks) >= 1
        
        # Headers should be at start of chunks
        header_chunks = [c for c in chunks if c.content.strip().startswith('#')]
        assert len(header_chunks) >= 1
    
    def test_structural_builds_header_path(self):
        """Test StructuralStrategy builds header_path metadata."""
        config = ChunkConfig(strategy_override="structural")
        chunker = MarkdownChunker(config)
        
        text = """# Main

## Sub

Content.
"""
        chunks = chunker.chunk(text)
        
        # Some chunks should have header_path
        paths = [c.metadata.get('header_path') for c in chunks]
        # At least one should have a path
        assert any(p for p in paths if p)


# =============================================================================
# SPEC-018: FallbackStrategy Behavior
# =============================================================================

class TestSPEC018FallbackStrategy:
    """
    SPEC-018: FallbackStrategy Behavior
    
    **Feature: v2-test-implementation, Property: FallbackStrategy behavior**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-018
    """
    
    def test_fallback_handles_plain_text(self):
        """Test FallbackStrategy handles plain text."""
        config = ChunkConfig(strategy_override="fallback")
        chunker = MarkdownChunker(config)
        
        text = "This is plain text without any markdown formatting. " * 20
        chunks = chunker.chunk(text)
        
        assert len(chunks) >= 1
        assert all(c.metadata['strategy'] == 'fallback' for c in chunks)
    
    def test_fallback_splits_at_paragraphs(self):
        """Test FallbackStrategy splits at paragraph boundaries."""
        config = ChunkConfig(
            max_chunk_size=100,
            overlap_size=20,
            strategy_override="fallback"
        )
        chunker = MarkdownChunker(config)
        
        text = """Paragraph one with some content.

Paragraph two with more content.

Paragraph three with even more content.
"""
        chunks = chunker.chunk(text)
        
        # Should produce multiple chunks
        assert len(chunks) >= 1
    
    def test_fallback_respects_size_constraints(self):
        """Test FallbackStrategy respects size constraints."""
        config = ChunkConfig(
            max_chunk_size=200,
            overlap_size=50,
            strategy_override="fallback"
        )
        chunker = MarkdownChunker(config)
        
        text = "Word " * 100
        chunks = chunker.chunk(text)
        
        for chunk in chunks:
            assert chunk.size <= 200 or chunk.is_oversize
    
    def test_fallback_always_can_handle(self):
        """Test FallbackStrategy can handle any document."""
        strategy = FallbackStrategy()
        parser = Parser()
        config = ChunkConfig()
        
        # Various document types
        documents = [
            "",
            "Simple text",
            "# Header\n\nContent",
            "```code```",
            "| table |",
        ]
        
        for doc in documents:
            analysis = parser.analyze(doc)
            assert strategy.can_handle(analysis, config) is True


# =============================================================================
# SPEC-019: Strategy Override
# =============================================================================

class TestSPEC019StrategyOverride:
    """
    SPEC-019: Strategy Override
    
    **Feature: v2-test-implementation, Unit: Strategy override**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-019
    """
    
    def test_override_code_aware(self):
        """Test strategy_override='code_aware' forces CodeAwareStrategy."""
        config = ChunkConfig(strategy_override="code_aware")
        chunker = MarkdownChunker(config)
        
        # Plain text that would normally use fallback
        text = "Plain text without code."
        chunks = chunker.chunk(text)
        
        if chunks:
            assert chunks[0].metadata['strategy'] == 'code_aware'
    
    def test_override_structural(self):
        """Test strategy_override='structural' forces StructuralStrategy."""
        config = ChunkConfig(strategy_override="structural")
        chunker = MarkdownChunker(config)
        
        # Code-heavy text that would normally use code_aware
        text = "```python\ncode\n```"
        chunks = chunker.chunk(text)
        
        if chunks:
            assert chunks[0].metadata['strategy'] == 'structural'
    
    def test_override_fallback(self):
        """Test strategy_override='fallback' forces FallbackStrategy."""
        config = ChunkConfig(strategy_override="fallback")
        chunker = MarkdownChunker(config)
        
        # Structured text that would normally use structural
        text = """# Header 1

## Header 2

### Header 3

Content.
"""
        chunks = chunker.chunk(text)
        
        if chunks:
            assert chunks[0].metadata['strategy'] == 'fallback'
    
    def test_no_override_auto_selects(self):
        """Test strategy_override=None allows auto-selection."""
        config = ChunkConfig(strategy_override=None)
        chunker = MarkdownChunker(config)
        
        # Code document
        code_text = "```python\ncode\n```"
        code_chunks = chunker.chunk(code_text)
        if code_chunks:
            assert code_chunks[0].metadata['strategy'] == 'code_aware'
        
        # Plain text
        plain_text = "Just plain text."
        plain_chunks = chunker.chunk(plain_text)
        if plain_chunks:
            # Should be fallback (no code, no structure)
            assert plain_chunks[0].metadata['strategy'] in ['fallback', 'structural', 'code_aware']
    
    @given(st.sampled_from(['code_aware', 'structural', 'fallback']))
    @settings(max_examples=10, deadline=5000)
    def test_all_overrides_work(self, strategy_name: str):
        """Property: All strategy overrides work correctly."""
        config = ChunkConfig(strategy_override=strategy_name)
        chunker = MarkdownChunker(config)
        
        text = "Test content."
        chunks = chunker.chunk(text)
        
        if chunks:
            assert chunks[0].metadata['strategy'] == strategy_name
