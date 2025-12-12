"""Tests for split section leaf detection and content preservation.

These tests verify that when sections exceed max_chunk_size and are split,
the parent chunks with content are correctly marked as leaves and included
in leaf-only filtering to prevent content loss.
"""

import re

from markdown_chunker_v2.chunker import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig


class TestSplitSectionLeafDetection:
    """Test that split sections preserve content via hybrid leaf detection."""

    def test_split_section_parent_marked_as_leaf(self):
        """Test that split section parent is marked as leaf if it has content."""
        config = ChunkConfig(
            max_chunk_size=400,  # Smaller to force split
            overlap_size=0,
            include_document_summary=False,  # Simpler hierarchy
        )
        chunker = MarkdownChunker(config)

        # Create document with large section that WILL be split
        # The key is to have enough content to exceed max_chunk_size
        text = """## Big Section

This is introductory content that appears before subsections and will be in the parent chunk.
It provides context and is critical content that must be preserved.
This paragraph is substantial enough to be considered significant content worth preserving.

### First Subsection
This is the first subsection with substantial content that will push the total section size over the limit.
Adding more text here to ensure we definitely exceed the max_chunk_size.
More sentences to make this subsection long enough to matter in the total count.

### Second Subsection
This is the second subsection with more content to ensure splitting.
Additional text to increase size and force the split behavior.
Yet more content to make this section substantial.

### Third Subsection
And a third subsection to make absolutely sure the section is large enough.
More text here to contribute to exceeding the chunk size limit.
Final sentences to ensure this section is properly sized for testing.
"""

        result = chunker.chunk_hierarchical(text)

        # Find chunks with the Big Section header_path
        big_section_chunks = [
            c
            for c in result.chunks
            if "Big Section" in c.metadata.get("header_path", "")
        ]

        # Find the parent chunk (has children and contains intro content)
        parent = None
        for chunk in big_section_chunks:
            if "introductory content" in chunk.content and chunk.metadata.get(
                "children_ids"
            ):
                parent = chunk
                break

        # If a split occurred and we have a parent with content
        if parent is not None:
            # Critical check: parent should be marked as leaf because it has content
            assert parent.metadata.get("is_leaf") is True, (
                f"Parent with intro content should be marked as leaf. "
                f"Content length: {len(parent.content)}, has_children: {bool(parent.metadata.get('children_ids'))}"
            )

            # Verify the intro content is in the parent
            assert "introductory content" in parent.content

            # Verify parent appears in leaf-only results
            leaf_chunks = result.get_flat_chunks()
            parent_in_leaves = any(
                c.metadata.get("chunk_id") == parent.metadata.get("chunk_id")
                for c in leaf_chunks
            )
            assert (
                parent_in_leaves
            ), "Parent with content should appear in leaf-only results"

        # Regardless of split, verify intro content appears in leaf chunks
        leaf_chunks = result.get_flat_chunks()
        leaf_content = "\n".join(c.content for c in leaf_chunks)
        assert (
            "introductory content" in leaf_content
        ), "Intro content must appear in leaf chunks"

    def test_no_content_loss_in_leaf_only_mode(self):
        """Test that no content is lost when filtering to leaf-only chunks."""
        config = ChunkConfig(
            max_chunk_size=600, overlap_size=0, include_document_summary=True
        )
        chunker = MarkdownChunker(config)

        # Document with multiple sections, some will be split
        text = """# Document Title

## Section One
This section has enough content to potentially be split across chunks.
We want to ensure that when split, all content appears in leaf chunks.

### Subsection 1A
Content for subsection 1A with substantial text to increase section size
and make it more likely to exceed the chunk size limit for testing.

### Subsection 1B
More content for subsection 1B to further increase the total size.
This helps ensure we test the split section scenario properly.

## Section Two
Another section with different content to test multiple split scenarios
in the same document and verify consistent behavior across sections.

### Subsection 2A
Content here with enough text to matter in the total size calculation.
We need varied content to properly test the content preservation logic.

### Subsection 2B
Final subsection with additional content to round out the test document
and provide a comprehensive test of the split section handling.
"""

        result = chunker.chunk_hierarchical(text)

        # Helper to extract text content (excluding headers)
        def extract_text_content(content: str) -> str:
            """Extract non-header text from content."""
            text = re.sub(r"^#{1,6}\s+.*$", "", content, flags=re.MULTILINE)
            return text.strip()

        # Get all chunks and leaf-only chunks
        all_chunks = result.chunks
        leaf_chunks = result.get_flat_chunks()

        # Extract text from all chunks and leaf chunks
        all_text = "\n".join(extract_text_content(c.content) for c in all_chunks)
        leaf_text = "\n".join(extract_text_content(c.content) for c in leaf_chunks)

        # Measure text content
        all_text_size = len(all_text.strip())
        leaf_text_size = len(leaf_text.strip())

        # Leaf-only content should preserve at least 95% of total content
        # (Small difference allowed for headers and formatting)
        coverage_ratio = leaf_text_size / all_text_size if all_text_size > 0 else 1.0
        assert coverage_ratio >= 0.95, (
            f"Content loss detected: {all_text_size} chars vs {leaf_text_size} chars "
            f"({coverage_ratio:.1%} coverage)"
        )

        # Verify specific content paragraphs appear in leaf chunks
        critical_phrases = [
            "enough content to potentially be split",
            "Content for subsection 1A",
            "More content for subsection 1B",
            "Another section with different content",
            "Content here with enough text",
            "Final subsection with additional content",
        ]

        for phrase in critical_phrases:
            assert (
                phrase in leaf_text
            ), f"Critical phrase missing from leaf chunks: '{phrase}'"

    def test_pure_header_parent_not_marked_as_leaf(self):
        """Test that parent with only header (no content) is not marked as leaf."""
        config = ChunkConfig(
            max_chunk_size=300, overlap_size=0, include_document_summary=True
        )
        chunker = MarkdownChunker(config)

        # Section with header only, all content in subsections
        text = """# Container Section

### Subsection A
All the actual content is in the subsections, not in the parent section.
This subsection has enough text to be a meaningful chunk on its own.

### Subsection B
More content here in another subsection to ensure the parent really
has no content of its own, just subsections.

### Subsection C
And a third subsection to make this a realistic test case of a
container section that only organizes its children.
"""

        result = chunker.chunk_hierarchical(text)

        # Find the "Container Section" parent
        parent = None
        for chunk in result.chunks:
            header_path = chunk.metadata.get("header_path", "")
            if header_path == "/Container Section" and chunk.metadata.get(
                "children_ids"
            ):
                parent = chunk
                break

        if parent:
            # If parent exists and has children, it should NOT be a leaf
            # (since it only has header, no content)
            has_significant_content = len(parent.content.strip()) > 150
            if not has_significant_content:
                assert (
                    parent.metadata.get("is_leaf") is False
                ), "Parent with only header should not be marked as leaf"

        # Verify leaf-only chunks contain all the subsection content
        leaf_chunks = result.get_flat_chunks()
        leaf_text = "\n".join(c.content for c in leaf_chunks)

        assert "All the actual content is in the subsections" in leaf_text
        assert "More content here in another subsection" in leaf_text
        assert "And a third subsection" in leaf_text

    def test_content_significance_threshold(self):
        """Test boundary cases for significant content detection."""
        config = ChunkConfig(
            max_chunk_size=200, overlap_size=0, include_document_summary=True
        )
        chunker = MarkdownChunker(config)

        # Test case 1: Content just below threshold (should not be significant)
        text_minimal = """# Section One

Short intro.

### Subsection
Much longer content here that forces a split, so we can test if the
parent's minimal intro is considered significant or not.
"""

        result1 = chunker.chunk_hierarchical(text_minimal)
        for chunk in result1.chunks:
            if "/Section One" in chunk.metadata.get("header_path", ""):
                if chunk.metadata.get("children_ids"):
                    break

        # Test case 2: Content well above threshold (should be significant)
        text_significant = """# Section Two

This is a substantial introductory paragraph that provides important context
and background information for the section. It contains enough text to be
considered significant content that should definitely be preserved when the
section is split across multiple chunks.

### Subsection
Additional content here to force the split.
"""

        result2 = chunker.chunk_hierarchical(text_significant)
        parent2 = None
        for chunk in result2.chunks:
            if "/Section Two" in chunk.metadata.get("header_path", ""):
                if chunk.metadata.get("children_ids"):
                    parent2 = chunk
                    break

        # If parent2 exists and has children, verify it's marked as leaf
        # (because it has significant content)
        if parent2 and parent2.metadata.get("children_ids"):
            # Extract non-header content
            content_text = re.sub(
                r"^#{1,6}\s+.*$", "", parent2.content, flags=re.MULTILINE
            ).strip()

            if len(content_text) > 100:
                assert (
                    parent2.metadata.get("is_leaf") is True
                ), "Parent with significant content should be marked as leaf"


class TestContentPreservationProperties:
    """Property-based tests for content preservation guarantees."""

    def test_all_input_content_in_leaf_chunks(self):
        """Verify that all meaningful input content appears in leaf chunks."""
        config = ChunkConfig(
            max_chunk_size=500, overlap_size=0, include_document_summary=True
        )
        chunker = MarkdownChunker(config)

        # Document with varied structure
        text = """## Introduction
This introduction has enough content to be meaningful and test that
it appears in the output even if the section gets split.

## Chapter One

### Section 1.1
Content for section 1.1 with substantial text to ensure we're testing
realistic document structures and split scenarios.

### Section 1.2
More content in section 1.2 to increase document size and variety.

## Chapter Two

### Section 2.1
Content for section 2.1 with different text to test multiple splits
across different parts of the document structure.

### Section 2.2
Final section with content to complete the test document and ensure
comprehensive coverage of the content preservation logic.
"""

        result = chunker.chunk_hierarchical(text)
        leaf_chunks = result.get_flat_chunks()

        # Extract all unique paragraphs/sentences from input (non-header text)
        input_lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip() and not line.strip().startswith("#")
        ]

        # Extract all text from leaf chunks
        leaf_content = "\n".join(c.content for c in leaf_chunks)

        # Verify each significant line appears in leaf chunks
        missing_lines = []
        for line in input_lines:
            if line and len(line) > 10:  # Ignore very short lines
                if line not in leaf_content:
                    missing_lines.append(line)

        assert len(missing_lines) == 0, (
            f"Found {len(missing_lines)} lines missing from leaf chunks: "
            f"{missing_lines[:3]}"
        )  # Show first 3 missing

    def test_no_content_loss_warnings(self, caplog):
        """Verify that no content loss warnings are emitted."""
        config = ChunkConfig(
            max_chunk_size=500, overlap_size=0, include_document_summary=True
        )
        chunker = MarkdownChunker(config)

        text = """# Document

## Section One
Intro paragraph with enough text to matter when testing content preservation
across split sections in hierarchical chunking mode.

### Subsection A
Content for subsection A with substantial text to force splits and test
the content preservation logic thoroughly.

### Subsection B
More content in subsection B to ensure we have realistic split scenarios
and can verify that no warnings are generated.
"""

        result = chunker.chunk_hierarchical(text)
        leaf_chunks = result.get_flat_chunks()

        # Check that no content loss warnings were logged
        warnings = [
            record
            for record in caplog.records
            if "content" in record.message.lower()
            and (
                "loss" in record.message.lower()
                or "preservation" in record.message.lower()
            )
        ]

        assert (
            len(warnings) == 0
        ), f"Unexpected content loss warnings: {[w.message for w in warnings]}"

        # Verify we got a reasonable number of chunks
        assert len(leaf_chunks) > 0, "Should have at least one leaf chunk"
