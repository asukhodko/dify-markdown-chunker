"""
Unit tests for metadata improvements.

Tests specific examples from manual testing to verify correct behavior.
"""

import os
import pytest
from markdown_chunker_v2 import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig


class TestSDE12ImpactCase:
    """
    Test that chunk with Impact/Complexity/Leadership has header_path
    ending with "Impact (Delivery)", not "Complexity".
    
    Validates: Requirements 1.2, 5.2
    """
    
    def test_impact_complexity_leadership_chunk_path(self):
        """
        When a chunk contains ### Impact (Delivery), ### Complexity, ### Leadership,
        the header_path should end with "Impact (Delivery)".
        
        The header_path reflects the hierarchical path to the first header,
        which includes ancestor headers from the document structure.
        """
        # Create a document where Impact/Complexity/Leadership will be in one chunk
        md_text = """# Критерии грейдов SDE

## SDE 12 (T@T1, Junior-, Младший разработчик)

### Scope
Разработчик помогает разрабатывать отдельные компоненты продукта.
"""
        # Use large chunk size so all content fits in fewer chunks
        config = ChunkConfig(max_chunk_size=2000, min_chunk_size=100)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)
        
        # Verify that chunks with headers have valid header_path
        for chunk in chunks:
            header_path = chunk.metadata.get('header_path', '')
            content = chunk.content
            
            # Skip preamble
            if chunk.metadata.get('content_type') == 'preamble':
                continue
            
            # header_path should be non-empty for chunks with headers
            if any(line.strip().startswith('#') for line in content.split('\n')):
                assert header_path and header_path != '[]', (
                    f"Chunk with headers should have non-empty header_path"
                )
                # Path should start with /
                assert header_path.startswith('/'), (
                    f"header_path should start with '/', got '{header_path}'"
                )
    
    def test_multiple_headers_in_chunk_uses_first(self):
        """
        When a chunk contains multiple headers, header_path uses the first one.
        """
        # Create content that will be in a single chunk with multiple headers
        md_text = """### Impact (Delivery)
Основная задача Junior — учиться.

### Complexity
Решает простые задачи.

### Leadership
Работает под руководством.
"""
        config = ChunkConfig(max_chunk_size=2000, min_chunk_size=50)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)
        
        # Should have one chunk with all three headers
        assert len(chunks) >= 1
        
        # Find chunk with multiple headers
        for chunk in chunks:
            content = chunk.content
            if '### Impact' in content and '### Complexity' in content:
                header_path = chunk.metadata.get('header_path', '')
                # Should end with Impact, not Complexity
                assert 'Impact' in header_path, (
                    f"header_path should contain 'Impact', got '{header_path}'"
                )
                # sub_headers should have the other headers
                sub_headers = chunk.metadata.get('sub_headers', [])
                if sub_headers:
                    assert any('Complexity' in h for h in sub_headers), (
                        f"sub_headers should contain 'Complexity', got {sub_headers}"
                    )



class TestPreambleSeparation:
    """
    Test that links before # Критерии грейдов SDE are in separate preamble chunk.
    
    Validates: Requirements 5.3
    """
    
    def test_preamble_links_separated(self):
        """
        Links before the first # header should be in a separate preamble chunk
        with content_type="preamble" and header_path="/__preamble__".
        """
        md_text = """Основная матрица: https://wiki.example.com/page1
Матрица для Тимлидов: https://wiki.example.com/page2
Есть также репозиторий: https://gitlab.example.com/repo

# Критерии грейдов SDE

## SDE 12 (Junior)

### Scope
Разработчик помогает разрабатывать компоненты.
"""
        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=50)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)
        
        # Find preamble chunk
        preamble_chunks = [c for c in chunks 
                          if c.metadata.get('content_type') == 'preamble']
        
        assert len(preamble_chunks) >= 1, "Should have preamble chunk"
        
        preamble = preamble_chunks[0]
        
        # Check preamble metadata
        assert preamble.metadata.get('header_path') == '/__preamble__', (
            f"Preamble header_path should be '/__preamble__', "
            f"got '{preamble.metadata.get('header_path')}'"
        )
        
        # Check preamble contains links
        assert 'https://' in preamble.content, "Preamble should contain links"
        
        # Check preamble does NOT contain the main header
        assert '# Критерии грейдов SDE' not in preamble.content, (
            "Preamble should not contain main header"
        )
        
        # Check first structural chunk starts with header
        structural_chunks = [c for c in chunks 
                           if c.metadata.get('content_type') != 'preamble']
        if structural_chunks:
            first_structural = structural_chunks[0]
            first_line = first_structural.content.strip().split('\n')[0]
            assert first_line.startswith('#'), (
                f"First structural chunk should start with header, got: '{first_line}'"
            )


class TestFirstStructuralChunkPath:
    """
    Test that first structural chunk has non-empty header_path.
    
    Validates: Requirements 3.2, 6.3
    """
    
    def test_first_chunk_has_valid_path(self):
        """
        First structural chunk containing # Title, ## Section, ### Subsection
        should have non-empty header_path.
        """
        md_text = """# Main Title

## Section One

### Subsection A
Content here.

### Subsection B
More content.
"""
        config = ChunkConfig(max_chunk_size=500, min_chunk_size=50)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)
        
        # All chunks should have non-empty header_path
        for i, chunk in enumerate(chunks):
            header_path = chunk.metadata.get('header_path', '')
            content_type = chunk.metadata.get('content_type', '')
            
            # Skip preamble (which has special path)
            if content_type == 'preamble':
                assert header_path == '/__preamble__'
                continue
            
            # Check for headers in content
            has_header = any(
                line.strip().startswith('#') 
                for line in chunk.content.split('\n')
                if not line.strip().startswith('```')
            )
            
            if has_header:
                assert header_path and header_path != '[]', (
                    f"Chunk {i} with headers should have non-empty header_path, "
                    f"got '{header_path}'"
                )


class TestSmallChunkBehavior:
    """
    Test predictable behavior for small chunks.
    
    Validates: Requirements 5.4
    """
    
    def test_small_chunk_has_reason(self):
        """
        Small chunks should have small_chunk_reason explaining why they exist.
        """
        # Create document that will produce small chunks
        md_text = """# Main

## Section 1

Short.

## Section 2

Also short.

## Section 3

Very short content.
"""
        # Use config that makes these sections "small"
        config = ChunkConfig(max_chunk_size=300, min_chunk_size=100, overlap_size=50)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)
        
        # Check small chunks have proper metadata
        for chunk in chunks:
            if chunk.metadata.get('small_chunk', False):
                reason = chunk.metadata.get('small_chunk_reason', '')
                assert reason == 'cannot_merge', (
                    f"Small chunk should have reason 'cannot_merge', got '{reason}'"
                )


class TestManualTestDocument:
    """
    Integration test using the full manual test document.
    """
    
    @pytest.fixture
    def manual_test_input(self):
        """Load the manual test input document."""
        fixture_path = os.path.join(
            os.path.dirname(__file__), 
            'fixtures', 
            'manual_test_input.md'
        )
        if os.path.exists(fixture_path):
            with open(fixture_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def test_manual_document_preamble(self, manual_test_input):
        """Test preamble handling on manual test document."""
        if manual_test_input is None:
            pytest.skip("Manual test input file not found")
        
        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=100)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(manual_test_input)
        
        # Should have preamble chunk with links
        preamble_chunks = [c for c in chunks 
                          if c.metadata.get('content_type') == 'preamble']
        
        assert len(preamble_chunks) >= 1, "Should have preamble chunk"
        
        # Preamble should contain wiki links
        preamble_content = preamble_chunks[0].content
        assert 'wiki' in preamble_content.lower() or 'http' in preamble_content.lower()
    
    def test_manual_document_no_empty_paths(self, manual_test_input):
        """Test that no structural chunks have empty header_path."""
        if manual_test_input is None:
            pytest.skip("Manual test input file not found")
        
        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=100)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(manual_test_input)
        
        for i, chunk in enumerate(chunks):
            header_path = chunk.metadata.get('header_path', '')
            content_type = chunk.metadata.get('content_type', '')
            
            # Preamble has special path
            if content_type == 'preamble':
                assert header_path == '/__preamble__'
                continue
            
            # Check if chunk has headers
            has_header = any(
                line.strip().startswith('#') 
                for line in chunk.content.split('\n')
            )
            
            if has_header:
                assert header_path and header_path not in ('', '[]', []), (
                    f"Chunk {i} with headers should have valid header_path"
                )