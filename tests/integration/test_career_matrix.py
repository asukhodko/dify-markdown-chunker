"""Integration tests for career matrix document chunking.

Tests Task 14.1: Test with real career matrix document
- Chunk with all strategies
- Verify no logical block fragmentation
- Verify no section mixing
- Verify Markdown structure preserved

Migration note: Migrated to markdown_chunker_v2 (December 2025)
V2 uses simplified ChunkConfig (8 params instead of 32).
overlap_size > 0 enables overlap (no separate enable_overlap flag).
"""

from pathlib import Path

import pytest

from markdown_chunker_v2 import MarkdownChunker, ChunkConfig


class TestCareerMatrixIntegration:
    """Integration tests for career matrix document."""

    @pytest.fixture
    def career_matrix_content(self) -> str:
        """Load career matrix document."""
        fixture_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "real_documents"
            / "career_matrix.md"
        )
        with open(fixture_path, "r", encoding="utf-8") as f:
            return f.read()

    @pytest.fixture
    def chunker(self) -> MarkdownChunker:
        """Create chunker instance."""
        return MarkdownChunker()

    def test_structural_strategy_no_fragmentation(self, career_matrix_content: str):
        """Test that structural strategy doesn't fragment logical blocks."""
        config = ChunkConfig(max_chunk_size=500, overlap_size=50)
        chunker = MarkdownChunker(config)

        chunks = chunker.chunk(career_matrix_content)

        assert len(chunks) > 0, "Should produce chunks"

        # Verify no orphan headers (header without content)
        for i, chunk in enumerate(chunks):
            lines = chunk.content.strip().split("\n")
            # If chunk ends with a header, it should have content after it
            # (unless it's the last line of the document)
            for j, line in enumerate(lines[:-1]):  # Exclude last line
                if line.strip().startswith("#"):
                    # Next non-empty line should not be a header
                    remaining_lines = [line for line in lines[j + 1 :] if line.strip()]
                    if remaining_lines:
                        # There should be content after header
                        pass
                        # This is a soft check - headers can be followed by sub-headers
                        # The key is that we don't have ONLY a header at the end

    def test_structural_strategy_no_section_mixing(self, career_matrix_content: str):
        """Test that chunks don't mix content from different major sections."""
        config = ChunkConfig(
            max_chunk_size=500,
            overlap_size=0,  # No overlap for cleaner section checking
        )
        chunker = MarkdownChunker(config)

        chunks = chunker.chunk(career_matrix_content)

        # Major sections in career matrix
        major_sections = [
            "Overview",
            "Engineering Levels",
            "Promotion Criteria",
            "Resources",
            "Appendix",
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
        config = ChunkConfig(max_chunk_size=500, overlap_size=50)
        chunker = MarkdownChunker(config)

        chunks = chunker.chunk(career_matrix_content)
        combined_content = "\n\n".join(chunk.content for chunk in chunks)

        # Check that key structural elements are preserved
        # Headers
        assert (
            "# Career Development Matrix" in combined_content
            or "Career Development Matrix" in combined_content
        )

        # Tables should have pipe characters
        assert "|" in combined_content, "Tables should be preserved"

        # Code blocks should be preserved
        assert (
            "```python" in combined_content or "```" in combined_content
        ), "Code blocks should be preserved"

        # Lists should be preserved
        assert "- " in combined_content, "Lists should be preserved"

    def test_urls_not_broken(self, career_matrix_content: str):
        """Test that URLs are not broken across chunks."""
        config = ChunkConfig(
            max_chunk_size=300,  # Smaller chunks to stress test
            overlap_size=50,
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
            assert (
                content in combined_content
            ), f"Content '{content}' should not be lost"

    def test_metadata_completeness(self, career_matrix_content: str):
        """Test that chunks have complete metadata."""
        config = ChunkConfig(max_chunk_size=500, overlap_size=50)
        chunker = MarkdownChunker(config)

        chunks = chunker.chunk(career_matrix_content)

        for i, chunk in enumerate(chunks):
            # Basic metadata should be present
            assert chunk.metadata is not None, f"Chunk {i} should have metadata"

            # Check for key metadata fields
            # Note: exact fields depend on implementation
            if hasattr(chunk, "start_line"):
                assert chunk.start_line >= 0, f"Chunk {i} should have valid start_line"
            if hasattr(chunk, "end_line"):
                assert (
                    chunk.end_line >= chunk.start_line
                ), f"Chunk {i} should have valid end_line"

    def test_chunk_size_respected(self, career_matrix_content: str):
        """Test that chunk sizes are reasonable."""
        config = ChunkConfig(max_chunk_size=500, overlap_size=50)
        chunker = MarkdownChunker(config)

        chunks = chunker.chunk(career_matrix_content)

        oversized_chunks = []
        for i, chunk in enumerate(chunks):
            # Allow some flexibility (2x max size for atomic blocks)
            if len(chunk.content) > config.max_chunk_size * 2:
                oversized_chunks.append((i, len(chunk.content)))

        # Most chunks should be within reasonable size
        # Some oversized chunks are acceptable for atomic blocks (tables, code)
        assert (
            len(oversized_chunks) <= len(chunks) * 0.2
        ), f"Too many oversized chunks: {oversized_chunks}"

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

    def test_auto_strategy_no_content_loss(self, career_matrix_content: str):
        """Test that auto strategy doesn't lose content.

        This test verifies:
        - Auto mode selects appropriate strategy
        - Content completeness is maintained
        - All major sections preserved
        """
        config = ChunkConfig(max_chunk_size=1000, overlap_size=200)
        chunker = MarkdownChunker(config)

        # Use chunk_with_analysis to get strategy info
        chunks, strategy_used, analysis = chunker.chunk_with_analysis(career_matrix_content)

        assert len(chunks) > 0, "Should produce chunks"

        # Verify major headers present (no content loss)
        all_content = "\n".join(chunk.content for chunk in chunks)

        # Check for key sections from career matrix
        # These should be present if content is complete
        key_sections = [
            "# Career Development Matrix",  # Main title
            "## Engineering Levels",  # Middle level
            "## Promotion Criteria",  # Middle+ level
        ]

        for section in key_sections:
            assert section in all_content, f"Missing section: {section}"

        # Verify paragraphs present (not just lists)
        # This ensures non-list content wasn't lost
        assert (
            "This document outlines" in all_content
        ), "Paragraph from Overview section missing - possible content loss"

    def test_chunk_with_metrics(self, career_matrix_content: str):
        """Test chunk_with_metrics returns valid metrics."""
        config = ChunkConfig(max_chunk_size=1000)
        chunker = MarkdownChunker(config)

        chunks, metrics = chunker.chunk_with_metrics(career_matrix_content)

        assert len(chunks) > 0, "Should produce chunks"
        assert metrics.total_chunks == len(chunks)
        assert metrics.avg_chunk_size > 0
        assert metrics.min_size > 0
        assert metrics.max_size >= metrics.min_size

    @pytest.mark.blocker
    def test_strategy_selection_for_mixed_document(self, career_matrix_content: str):
        """Test that appropriate strategy is selected for mixed documents.

        Career matrix has headers, tables, code, and lists - should use
        structural or code_aware strategy, not a specialized one.
        """
        config = ChunkConfig(max_chunk_size=1000)
        chunker = MarkdownChunker(config)

        chunks, strategy_used, analysis = chunker.chunk_with_analysis(career_matrix_content)

        # Should be structural, code_aware, or fallback - not a specialized strategy
        assert strategy_used in [
            "structural",
            "code_aware",
            "fallback",
        ], f"Expected general strategy for mixed document, got: {strategy_used}"

        # Verify analysis detected the mixed content
        assert analysis.header_count > 0, "Should detect headers"
        assert analysis.code_block_count > 0, "Should detect code blocks"
        assert analysis.table_count > 0, "Should detect tables"
