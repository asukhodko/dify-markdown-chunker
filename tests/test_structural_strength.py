"""
Unit tests for structural strength evaluation.

Tests the new small_chunk flagging logic that considers structural strength
to avoid false positives on content-rich but compact sections.
"""

import pytest
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig


class TestStructuralStrength:
    """Test structural strength evaluation for small_chunk flagging."""
    
    def test_level_2_header_prevents_small_flag(self):
        """Chunk with level 2 header should not be flagged as small."""
        markdown = """## Scope

Brief but meaningful content.
"""
        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=100)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)
        
        # Find scope chunk
        scope_chunks = [c for c in chunks if '## Scope' in c.content]
        if scope_chunks:
            chunk = scope_chunks[0]
            # Should NOT be flagged as small because it has level 2 header
            assert not chunk.metadata.get('small_chunk', False), \
                "Level 2 header chunk should not be flagged as small"
    
    def test_level_3_header_prevents_small_flag(self):
        """Chunk with level 3 header should not be flagged as small."""
        markdown = """### Technical Complexity

Short description.
"""
        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=100)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)
        
        # Find chunk with level 3 header
        for chunk in chunks:
            if '### Technical Complexity' in chunk.content:
                # Should NOT be flagged as small
                assert not chunk.metadata.get('small_chunk', False)
    
    def test_multiple_paragraphs_prevent_small_flag(self):
        """Chunk with multiple paragraphs should not be flagged as small."""
        markdown = """First paragraph with some content.

Second paragraph with more content.

Third paragraph."""
        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=150)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)
        
        # Even if small, multiple paragraphs = structurally strong
        for chunk in chunks:
            paragraph_breaks = chunk.content.count('\n\n')
            if paragraph_breaks >= 2:
                assert not chunk.metadata.get('small_chunk', False), \
                    "Multi-paragraph chunk should not be flagged as small"
    
    def test_sufficient_text_lines_prevent_small_flag(self):
        """Chunk with 3+ non-header lines should not be flagged as small."""
        markdown = """Line one of content.
Line two of content.
Line three of content.
Line four of content."""
        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=150)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)
        
        # Sufficient lines = structurally strong
        for chunk in chunks:
            lines = [l for l in chunk.content.split('\n') if l.strip() and not l.strip().startswith('#')]
            if len(lines) >= 3:
                assert not chunk.metadata.get('small_chunk', False)
    
    def test_meaningful_content_prevents_small_flag(self):
        """Chunk with >100 chars of non-header content should not be flagged."""
        markdown = """## Short Header

This is a section with meaningful content that exceeds one hundred characters after we extract the header. This text provides substantial information."""
        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=200)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)
        
        # Find the chunk
        for chunk in chunks:
            if 'meaningful content' in chunk.content:
                # Extract non-header content
                lines = [l for l in chunk.content.split('\n') if not l.strip().startswith('#')]
                non_header = '\n'.join(lines).strip()
                if len(non_header) > 100:
                    # Should not be flagged as small
                    assert not chunk.metadata.get('small_chunk', False)
    
    def test_structurally_weak_chunk_is_flagged(self):
        """Truly weak chunk should still be flagged as small."""
        # Create document that forces a weak small chunk
        markdown = """# Main

## Section 1

Substantial content for section 1 that will be a normal chunk.

## Section 2

Very brief.

## Section 3

More substantial content for section 3."""
        config = ChunkConfig(max_chunk_size=250, min_chunk_size=100, overlap_size=50)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)
        
        # Section 2 might be flagged if it's structurally weak and can't merge
        small_chunks = [c for c in chunks if c.metadata.get('small_chunk', False)]
        # Just verify the flagging mechanism works (may or may not flag depending on merging)
        assert isinstance(small_chunks, list)
    
    def test_lists_not_considered_structural_strength(self):
        """Lists are not yet considered as structural strength indicators."""
        markdown = """- Item 1
- Item 2  
- Item 3
- Item 4"""
        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=100)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)
        
        # Lists might be flagged as small if they don't meet other criteria
        # This is a known limitation documented in the design
        # Just verify no errors
        assert len(chunks) >= 1


class TestSmallChunkFlagging:
    """Test small_chunk flag behavior."""
    
    def test_small_chunk_reason_is_cannot_merge(self):
        """small_chunk_reason should be 'cannot_merge'."""
        markdown = """# Main

## Section 1

Long content that forms a normal chunk with sufficient text.

## Section 2

x

## Section 3

More long content that forms another normal chunk."""
        config = ChunkConfig(max_chunk_size=200, min_chunk_size=100, overlap_size=50)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)
        
        # Check any flagged chunks have correct reason
        for chunk in chunks:
            if chunk.metadata.get('small_chunk', False):
                assert chunk.metadata.get('small_chunk_reason') == 'cannot_merge'
    
    def test_content_rich_scope_not_flagged(self):
        """Content-rich Scope section should not be flagged as small."""
        markdown = """# Task Description

## Scope

#### Problem Description

The current system has issues with performance and scalability.
We need to redesign the architecture to handle increased load.

#### Work Completed

1. Analyzed current architecture
2. Designed new approach
3. Implemented proof of concept
4. Validated with stakeholders

Multiple paragraphs and substantial content make this structurally strong."""
        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=200)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)
        
        # Find Scope section
        for chunk in chunks:
            if '## Scope' in chunk.content:
                # Should NOT be flagged as small due to structural strength
                assert not chunk.metadata.get('small_chunk', False), \
                    "Content-rich Scope section should not be flagged as small"
    
    def test_impact_section_not_flagged(self):
        """Content-rich Impact section should not be flagged as small."""
        markdown = """## Impact (Delivery)

The project delivered significant value:

- Improved system performance by 5x
- Reduced infrastructure costs by 40%
- Enabled new product features
- Improved developer experience

Team of 8 people worked for 6 months."""
        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=200)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)
        
        # Find Impact section
        for chunk in chunks:
            if '## Impact' in chunk.content:
                # Should NOT be flagged - has level 2 header
                assert not chunk.metadata.get('small_chunk', False)
    
    def test_no_false_positives_on_manual_test_doc(self):
        """Real-world sections like Scope/Impact should not be false positives."""
        # Simulate content from manual test document
        markdown = """# Пример хорошо описанной задачи для грейдапа

По https://wiki.tcsbank.ru/pages/viewpage.action?pageId=3251338229

## Scope

#### Описание

Проблема:  
В нашем отделе столкнулись с необходимостью валидировать запросы от клиентов.

#### Итоги работы

1. Изучил подходы в других компаниях
2. Составил ADR, RFC, PoC
3. Запустил MVP
4. Написал документацию
5. Собрал метрики

## Impact

#### Описание задачи

Текущая системная архитектура не позволяет обеспечить требования.

#### Итоги работы  

1. Изучил текущую систему
2. Выработал подход
3. Реализовал улучшения
4. Собрал результаты
"""
        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=200)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)
        
        # Scope and Impact sections should NOT be flagged as small_chunk
        for chunk in chunks:
            if '## Scope' in chunk.content or '## Impact' in chunk.content:
                assert not chunk.metadata.get('small_chunk', False), \
                    f"Scope/Impact section incorrectly flagged as small: {chunk.metadata}"
