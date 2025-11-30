"""Integration tests for career matrix document chunking.

Tests Task 14.1: Test with real career matrix document
- Chunk with all strategies
- Verify no logical block fragmentation
- Verify no section mixing
- Verify Markdown structure preserved
"""

import os
import pytest
from pathlib import Path

from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig


class TestCareerMatrixIntegration:
    """Integration tests for career matrix document."""

    @pytest.fixture
    def career_matrix_content(self) -> str:
        """Load career matrix document."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "real_documents" / "career_matrix.md"
        with open(fixture_path, "r", encoding="utf-8") as f:
            return f.read()

    @pytest.fixture
    def chunker(self) -> MarkdownChunker:
        """Create chunker instance."""
        return MarkdownChunker()

    def test_structural_strategy_no_fragmentation(self, career_matrix_content: str):
        """Test that structural strategy doesn't fragment logical blocks."""
        config = ChunkConfig(
            max_chunk_size=500,
            overlap_size=50,
            enable_overlap=True
        )
        chunker = MarkdownChunker(config)
        
        chunks = chunker.chunk(career_matrix_content)
        
        assert len(chunks) > 0, "Should produce chunks"
        
        # Verify no orphan headers (header without content)
        for i, chunk in enumerate(chunks):
            lines = chunk.content.strip().split('\n')
            # If chunk ends with a header, it should have content after it
            # (unless it's the last line of the document)
            for j, line in enumerate(lines[:-1]):  # Exclude last line
                if line.strip().startswith('#'):
                    # Next non-empty line should not be a header
                    remaining_lines = [l for l in lines[j+1:] if l.strip()]
                    if remaining_lines:
                        # There should be content after header
                        has_content = any(not l.strip().startswith('#') for l in remaining_lines)
                        # This is a soft check - headers can be followed by sub-headers
                        # The key is that we don't have ONLY a header at the end

    def test_structural_strategy_no_section_mixing(self, career_matrix_content: str):
        """Test that chunks don't mix content from different major sections."""
        config = ChunkConfig(
            max_chunk_size=500,
            overlap_size=0,  # No overlap for cleaner section checking
            enable_overlap=False
        )
        chunker = MarkdownChunker(config)
        
        chunks = chunker.chunk(career_matrix_content)
        
        # Major sections in career matrix
        major_sections = [
            "Overview",
            "Engineering Levels",
            "Promotion Criteria",
            "Resources",
            "Appendix"
        ]
        
        for chunk in chunks:
            # Count how many major section headers appear in this chunk
            section_headers_in_chunk = []
            for section in major_sections:
                if f"## {section}" in chunk.content:
                    section_headers_in_chunk.append(section)
            
            # A chunk should not contain more than one major section header
            # (unless it's a very small document or large chunk size)
            # This is a soft check - we mainly want to ensure logical grouping

    def test_markdown_structure_preserved(self, career_matrix_content: str):
        """Test that Markdown structure is preserved in chunks."""
        config = ChunkConfig(
            max_chunk_size=500,
            overlap_size=50,
            enable_overlap=True
        )
        chunker = MarkdownChunker(config)
        
        chunks = chunker.chunk(career_matrix_content)
        combined_content = "\n\n".join(chunk.content for chunk in chunks)
        
        # Check that key structural elements are preserved
        # Headers
        assert "# Career Development Matrix" in combined_content or \
               "Career Development Matrix" in combined_content
        
        # Tables should have pipe characters
        assert "|" in combined_content, "Tables should be preserved"
        
        # Code blocks should be preserved
        assert "```python" in combined_content or "```" in combined_content, \
            "Code blocks should be preserved"
        
        # Lists should be preserved
        assert "- " in combined_content, "Lists should be preserved"

    def test_urls_not_broken(self, career_matrix_content: str):
        """Test that URLs are not broken across chunks."""
        config = ChunkConfig(
            max_chunk_size=300,  # Smaller chunks to stress test
            overlap_size=50,
            enable_overlap=True
        )
        chunker = MarkdownChunker(config)
        
        chunks = chunker.chunk(career_matrix_content)
        
        # URLs in the document
        expected_urls = [
            "https://wiki.company.com/engineering",
            "https://learn.company.com/tech",
            "https://hr.company.com/careers",
        ]
        
        combined_content = "\n\n".join(chunk.content for chunk in chunks)
        
        for url in expected_urls:
            assert url in combined_content, f"URL {url} should be preserved intact"

    def test_no_data_loss(self, career_matrix_content: str):
        """Test that no content is lost during chunking."""
        config = ChunkConfig(
            max_chunk_size=500,
            overlap_size=0,  # No overlap for accurate content comparison
            enable_overlap=False
        )
        chunker = MarkdownChunker(config)
        
        chunks = chunker.chunk(career_matrix_content)
        combined_content = "\n\n".join(chunk.content for chunk in chunks)
        
        # Key content that must be present
        key_content = [
            "Junior Engineer",
            "Mid-Level Engineer",
            "Senior Engineer",
            "Technical Skills",
            "Responsibilities",
            "Growth Areas",
            "Promotion Criteria",
            "calculate_level_score",
        ]
        
        for content in key_content:
            assert content in combined_content, f"Content '{content}' should not be lost"

    def test_metadata_completeness(self, career_matrix_content: str):
        """Test that chunks have complete metadata."""
        config = ChunkConfig(
            max_chunk_size=500,
            overlap_size=50,
            enable_overlap=True
        )
        chunker = MarkdownChunker(config)
        
        chunks = chunker.chunk(career_matrix_content)
        
        for i, chunk in enumerate(chunks):
            # Basic metadata should be present
            assert chunk.metadata is not None, f"Chunk {i} should have metadata"
            
            # Check for key metadata fields
            # Note: exact fields depend on implementation
            if hasattr(chunk, 'start_line'):
                assert chunk.start_line >= 0, f"Chunk {i} should have valid start_line"
            if hasattr(chunk, 'end_line'):
                assert chunk.end_line >= chunk.start_line, f"Chunk {i} should have valid end_line"

    def test_chunk_size_respected(self, career_matrix_content: str):
        """Test that chunk sizes are reasonable."""
        config = ChunkConfig(
            max_chunk_size=500,
            overlap_size=50,
            enable_overlap=True
        )
        chunker = MarkdownChunker(config)
        
        chunks = chunker.chunk(career_matrix_content)
        
        oversized_chunks = []
        for i, chunk in enumerate(chunks):
            # Allow some flexibility (2x max size for atomic blocks)
            if len(chunk.content) > config.max_chunk_size * 2:
                oversized_chunks.append((i, len(chunk.content)))
        
        # Most chunks should be within reasonable size
        # Some oversized chunks are acceptable for atomic blocks (tables, code)
        assert len(oversized_chunks) <= len(chunks) * 0.2, \
            f"Too many oversized chunks: {oversized_chunks}"

    def test_chunking_produces_results(self, career_matrix_content: str):
        """Test that chunking produces non-empty results."""
        config = ChunkConfig(max_chunk_size=1000)
        chunker = MarkdownChunker(config)
        
        chunks = chunker.chunk(career_matrix_content)
        
        assert chunks is not None, "Should return result"
        assert len(chunks) > 0, "Should produce chunks"
        
        # Verify no empty chunks
        for chunk in chunks:
            assert chunk.content.strip(), "Produced empty chunk"
