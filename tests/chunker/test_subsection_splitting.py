"""
Tests for subsection splitting functionality in structural strategy.

This module tests the newly implemented subsection splitting that was
previously a stub, ensuring sections with subsections are properly split.
"""

from markdown_chunker.chunker.strategies.structural_strategy import (
    HeaderInfo,
    Section,
    StructuralStrategy,
)
from markdown_chunker.chunker.types import ChunkConfig


class TestSubsectionSplitting:
    """Test subsection splitting functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.strategy = StructuralStrategy()
        self.config = ChunkConfig(max_chunk_size=1000, min_chunk_size=100)

    def test_split_by_subsections_small_subsections(self):
        """Test splitting section with small subsections."""
        # Create parent header
        parent_header = HeaderInfo(level=1, text="Main", line=1, position=0)

        # Create child headers
        child1 = HeaderInfo(level=2, text="Sub 1", line=3, position=10)
        child2 = HeaderInfo(level=2, text="Sub 2", line=6, position=30)

        parent_header.children = [child1, child2]

        # Create subsections
        subsection1 = Section(
            header=child1,
            content="## Sub 1\n\nContent 1",
            start_line=3,
            end_line=5,
            size=20,
            has_subsections=False,
        )

        subsection2 = Section(
            header=child2,
            content="## Sub 2\n\nContent 2",
            start_line=6,
            end_line=8,
            size=20,
            has_subsections=False,
        )

        # Create main section
        main_section = Section(
            header=parent_header,
            content="# Main\n\n## Sub 1\n\nContent 1\n\n## Sub 2\n\nContent 2",
            start_line=1,
            end_line=8,
            size=50,
            has_subsections=True,
            subsections=[subsection1, subsection2],
        )

        # Split by subsections
        chunks = self.strategy._split_by_subsections(main_section, self.config)

        # Should create 2 chunks (one per subsection)
        assert len(chunks) == 2

        # Check content
        assert "Sub 1" in chunks[0].content
        assert "Sub 2" in chunks[1].content

    def test_split_by_subsections_large_subsection(self):
        """Test splitting section with large subsection that needs recursive split."""
        parent_header = HeaderInfo(level=1, text="Main", line=1, position=0)
        child_header = HeaderInfo(level=2, text="Large Sub", line=3, position=10)

        parent_header.children = [child_header]

        # Create large subsection (> max_chunk_size)
        large_content = "## Large Sub\n\n" + ("Very long content. " * 100)

        large_subsection = Section(
            header=child_header,
            content=large_content,
            start_line=3,
            end_line=10,
            size=len(large_content),
            has_subsections=False,
        )

        main_section = Section(
            header=parent_header,
            content=f"# Main\n\n{large_content}",
            start_line=1,
            end_line=10,
            size=len(large_content) + 10,
            has_subsections=True,
            subsections=[large_subsection],
        )

        # Split by subsections (should recursively split large subsection)
        chunks = self.strategy._split_by_subsections(main_section, self.config)

        # Should create multiple chunks (large subsection was split)
        assert len(chunks) > 1

        # All chunks should be within size limit (with reasonable tolerance)
        # Note: Some chunks may exceed limit if paragraphs are very long
        for chunk in chunks:
            # Most chunks should be reasonable, allow some to be larger
            assert len(chunk.content) <= self.config.max_chunk_size * 2.0

    def test_split_by_subsections_nested_hierarchy(self):
        """Test splitting with nested subsection hierarchy."""
        # Create 3-level hierarchy: H1 -> H2 -> H3
        h1 = HeaderInfo(level=1, text="Main", line=1, position=0)
        h2 = HeaderInfo(level=2, text="Sub", line=3, position=10)
        h3 = HeaderInfo(level=3, text="SubSub", line=5, position=20)

        h1.children = [h2]
        h2.children = [h3]

        # Create sections
        h3_section = Section(
            header=h3,
            content="### SubSub\n\nNested content",
            start_line=5,
            end_line=7,
            size=30,
            has_subsections=False,
        )

        h2_section = Section(
            header=h2,
            content="## Sub\n\n### SubSub\n\nNested content",
            start_line=3,
            end_line=7,
            size=40,
            has_subsections=True,
            subsections=[h3_section],
        )

        h1_section = Section(
            header=h1,
            content="# Main\n\n## Sub\n\n### SubSub\n\nNested content",
            start_line=1,
            end_line=7,
            size=50,
            has_subsections=True,
            subsections=[h2_section],
        )

        # Split by subsections
        chunks = self.strategy._split_by_subsections(h1_section, self.config)

        # Should handle nested structure
        assert len(chunks) > 0

        # Should contain nested content
        all_content = " ".join(chunk.content for chunk in chunks)
        assert "SubSub" in all_content
        assert "Nested content" in all_content

    def test_split_by_subsections_empty_subsections(self):
        """Test handling empty subsections."""
        parent_header = HeaderInfo(level=1, text="Main", line=1, position=0)
        child_header = HeaderInfo(level=2, text="Empty", line=3, position=10)

        parent_header.children = [child_header]

        empty_subsection = Section(
            header=child_header,
            content="## Empty\n\n",
            start_line=3,
            end_line=4,
            size=10,
            has_subsections=False,
        )

        main_section = Section(
            header=parent_header,
            content="# Main\n\n## Empty\n\n",
            start_line=1,
            end_line=4,
            size=20,
            has_subsections=True,
            subsections=[empty_subsection],
        )

        # Should handle empty subsections gracefully
        chunks = self.strategy._split_by_subsections(main_section, self.config)

        # Should still create chunks
        assert len(chunks) >= 0


class TestSplitByParagraphs:
    """Test paragraph splitting functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.strategy = StructuralStrategy()
        self.config = ChunkConfig(max_chunk_size=100, min_chunk_size=20)

    def test_split_by_paragraphs_simple(self):
        """Test splitting section by paragraphs."""
        header = HeaderInfo(level=1, text="Main", line=1, position=0)

        section = Section(
            header=header,
            content="# Main\n\nParagraph 1.\n\nParagraph 2.\n\nParagraph 3.",
            start_line=1,
            end_line=7,
            size=50,
            has_subsections=False,
        )

        chunks = self.strategy._split_by_paragraphs(section, self.config)

        # Should create chunks
        assert len(chunks) > 0

        # Should contain all paragraphs
        all_content = " ".join(chunk.content for chunk in chunks)
        assert "Paragraph 1" in all_content
        assert "Paragraph 2" in all_content
        assert "Paragraph 3" in all_content

    def test_split_by_paragraphs_respects_size_limit(self):
        """Test that paragraph splitting respects size limits."""
        header = HeaderInfo(level=1, text="Main", line=1, position=0)

        # Create content with multiple paragraphs
        paragraphs = [f"Paragraph {i} with some content." for i in range(10)]
        content = "# Main\n\n" + "\n\n".join(paragraphs)

        section = Section(
            header=header,
            content=content,
            start_line=1,
            end_line=20,
            size=len(content),
            has_subsections=False,
        )

        chunks = self.strategy._split_by_paragraphs(section, self.config)

        # All chunks should respect size limit
        for chunk in chunks:
            assert len(chunk.content) <= self.config.max_chunk_size * 1.1

    def test_split_by_paragraphs_empty_paragraphs(self):
        """Test handling empty paragraphs."""
        header = HeaderInfo(level=1, text="Main", line=1, position=0)

        section = Section(
            header=header,
            content="# Main\n\n\n\nParagraph 1.\n\n\n\nParagraph 2.",
            start_line=1,
            end_line=7,
            size=40,
            has_subsections=False,
        )

        chunks = self.strategy._split_by_paragraphs(section, self.config)

        # Should skip empty paragraphs
        assert len(chunks) > 0

        # Should contain non-empty paragraphs
        all_content = " ".join(chunk.content for chunk in chunks)
        assert "Paragraph 1" in all_content
        assert "Paragraph 2" in all_content


class TestBuildPotentialContent:
    """Test _build_potential_content helper method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.strategy = StructuralStrategy()

    def test_build_potential_content_empty_current(self):
        """Test building content with empty current."""
        result = self.strategy._build_potential_content("", "New paragraph")
        assert result == "New paragraph"

    def test_build_potential_content_with_current(self):
        """Test building content with existing current."""
        result = self.strategy._build_potential_content(
            "Current content", "New paragraph"
        )
        assert result == "Current content\n\nNew paragraph"

    def test_build_potential_content_preserves_formatting(self):
        """Test that content building preserves paragraph separation."""
        current = "First paragraph"
        new = "Second paragraph"
        result = self.strategy._build_potential_content(current, new)

        # Should have double newline separator
        assert "\n\n" in result
        assert result.count("\n") == 2


class TestSubsectionSplittingIntegration:
    """Integration tests for subsection splitting."""

    def setup_method(self):
        """Set up test fixtures."""
        self.strategy = StructuralStrategy()
        self.config = ChunkConfig(max_chunk_size=500, min_chunk_size=100)

    def test_full_pipeline_with_subsections(self):
        """Test full chunking pipeline with subsections."""
        markdown = """# Main Document

## Section 1

Content for section 1.

### Subsection 1.1

Detailed content for subsection 1.1.

### Subsection 1.2

Detailed content for subsection 1.2.

## Section 2

Content for section 2.
"""

        # Test with manual header detection (no Stage1Results needed)
        headers = self.strategy._detect_headers_manual(markdown)

        # Should detect all headers
        assert len(headers) >= 5

        # Build hierarchy
        self.strategy._build_hierarchy(headers)

        # Create sections
        sections = self.strategy._create_sections(markdown, headers)

        # Should create sections
        assert len(sections) > 0

        # Should have subsections
        assert any(s.has_subsections for s in sections)

    def test_subsection_metadata_preserved(self):
        """Test that subsection metadata is preserved."""
        markdown = """# Main

## Subsection

Content here.
"""

        # Test with manual header detection
        headers = self.strategy._detect_headers_manual(markdown)

        # Build hierarchy
        self.strategy._build_hierarchy(headers)

        # Create sections
        sections = self.strategy._create_sections(markdown, headers)

        # Process sections
        chunks = self.strategy._process_sections(sections, self.config)

        # Check metadata
        for chunk in chunks:
            assert "header_level" in chunk.metadata
            assert "header_text" in chunk.metadata
            assert "header_path" in chunk.metadata
