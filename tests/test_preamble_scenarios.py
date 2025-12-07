"""
Tests for preamble handling and structural strategy selection.

Based on manual testing requirements from manual_testing/ directory.
"""

import pytest

from markdown_chunker_v2.chunker import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig
from markdown_chunker_v2.parser import Parser
from markdown_chunker_v2.strategies import StrategySelector


class TestPreambleScenario:
    """Tests for preamble scenario using structured document with preamble."""

    @pytest.fixture
    def test_document(self):
        """Create a test document with preamble."""
        return """Preamble text introducing the document.

This is additional preamble content before the first header.
It provides context and introduction.

More preamble content here.
Multiple paragraphs of preamble.

# Main Title

## Section 1

Content of section 1.

### Subsection 1.1

- Item 1
- Item 2
- Item 3

### Subsection 1.2

More content here.

## Section 2

Content of section 2.

### Subsection 2.1

- Item A
- Item B
- Item C

### Subsection 2.2

Final content.
"""

    @pytest.fixture
    def config(self):
        """Configuration matching manual test parameters."""
        return ChunkConfig(
            max_chunk_size=1000,
            overlap_size=200,
        )

    def test_strategy_selection_is_structural(self, test_document, config):
        """Test that structural strategy is selected (not list_aware)."""
        parser = Parser()
        analysis = parser.analyze(test_document)
        selector = StrategySelector()
        strategy = selector.select(analysis, config)

        assert strategy.name == "structural", (
            f"Expected structural strategy, got {strategy.name}. "
            f"Document has {analysis.header_count} headers, "
            f"{analysis.list_count} list blocks (ratio {analysis.list_ratio:.2%}). "
            f"Structural documents should use structural strategy even if they contain lists."
        )

    def test_first_chunk_is_preamble(self, test_document, config):
        """Test that first chunk has correct preamble metadata."""
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(test_document)

        assert len(chunks) > 0, "Document should produce at least one chunk"

        first_chunk = chunks[0]

        # Check metadata fields
        assert (
            first_chunk.metadata["content_type"] == "preamble"
        ), "First chunk should have content_type='preamble'"
        assert (
            first_chunk.metadata["header_path"] == "/__preamble__"
        ), "Preamble should have header_path='/__preamble__'"
        assert (
            first_chunk.metadata["header_level"] == 0
        ), "Preamble should have header_level=0"
        assert (
            first_chunk.metadata["chunk_index"] == 0
        ), "First chunk should have chunk_index=0"
        assert (
            "section_tags" in first_chunk.metadata
        ), "Metadata should contain section_tags field"
        assert (
            first_chunk.metadata["section_tags"] == []
        ), "Preamble section_tags should be empty list"

        # Verify line numbers
        assert first_chunk.start_line == 1, "Preamble should start at line 1"
        # Preamble should end before or at first header line (line 8 in our test doc)
        assert (
            first_chunk.end_line <= 8
        ), "Preamble should end at or before first header"

    def test_preamble_content_accuracy(self, test_document, config):
        """Test that preamble content matches expected text."""
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(test_document)

        first_chunk = chunks[0]
        
        # First chunk should be preamble
        assert first_chunk.metadata["content_type"] == "preamble"
        
        # Preamble should contain the intro text
        assert "Preamble text" in first_chunk.content
        assert "introducing the document" in first_chunk.content
        
        # First header should NOT be in preamble
        assert "# Main Title" not in first_chunk.content

    def test_preamble_next_content_present(self, test_document, config):
        """Test that next_content field is present and contains next section."""
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(test_document)

        first_chunk = chunks[0]

        # next_content should be present for first chunk if there are more chunks
        if len(chunks) > 1:
            assert (
                "next_content" in first_chunk.metadata
            ), "First chunk metadata should contain next_content field when there are more chunks"

            next_content = first_chunk.metadata["next_content"]

            # Should not be empty
            assert next_content and next_content.strip(), "next_content should not be empty"

            # Should contain the first header
            assert (
                "# Main Title" in next_content
            ), "next_content should contain the first header '# Main Title'"

    def test_strategy_field_in_metadata(self, test_document, config):
        """Test that strategy field is present in metadata."""
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(test_document)

        for chunk in chunks:
            assert (
                "strategy" in chunk.metadata
            ), f"Chunk {chunk.metadata.get('chunk_index')} missing strategy field"
            assert chunk.metadata["strategy"] == "structural", (
                f"Chunk {chunk.metadata.get('chunk_index')} has wrong strategy: "
                f"{chunk.metadata.get('strategy')}"
            )


class TestDocumentWithoutPreamble:
    """Tests for documents that start directly with a header."""

    def test_no_preamble_when_starts_with_header(self):
        """Test document starting with # has no preamble chunk."""
        md_text = """# First Header

This is the first section content.

## Subsection

More content here.
"""

        config = ChunkConfig(max_chunk_size=1000, overlap_size=200)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        assert len(chunks) > 0, "Document should produce chunks"

        # First chunk should NOT be preamble
        first_chunk = chunks[0]
        assert (
            first_chunk.metadata["content_type"] != "preamble"
        ), "Document starting with header should not have preamble chunk"
        assert (
            first_chunk.metadata["header_path"] != "/__preamble__"
        ), "First chunk should not have preamble header_path"

        # First chunk should be regular section (fallback strategy may use "text")
        # Accept either "section" (structural) or "text" (fallback)
        assert first_chunk.metadata["content_type"] in [
            "section",
            "text",
        ], f"First chunk should be a section or text, got {first_chunk.metadata['content_type']}"

    def test_no_preamble_with_only_whitespace_before_header(self):
        """Test that whitespace-only content before header doesn't create preamble."""
        md_text = """


# First Header

Content here.
"""

        config = ChunkConfig(max_chunk_size=1000, overlap_size=200)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Should not have preamble chunk
        preamble_chunks = [
            c for c in chunks if c.metadata.get("content_type") == "preamble"
        ]
        assert (
            len(preamble_chunks) == 0
        ), "Whitespace-only content should not create preamble chunk"


class TestLongPreamble:
    """Tests for documents with long preamble close to max_chunk_size."""

    def test_long_preamble_near_limit(self):
        """Test preamble close to max_chunk_size is handled correctly."""
        # Create a preamble of ~900 characters (near 1000 limit)
        preamble_lines = [
            f"Preamble line {i} with some additional text content." for i in range(15)
        ]
        preamble = "\n".join(preamble_lines)

        # Add enough structure to trigger structural strategy
        md_text = f"""{preamble}

# Main Title

## Section 1

Section content.

## Section 2

More content.

## Section 3

Final content.
"""

        config = ChunkConfig(max_chunk_size=1000, overlap_size=200)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Should have at least one chunk
        assert len(chunks) > 0

        # First chunk should be preamble (now that we have enough structure)
        first_chunk = chunks[0]
        assert first_chunk.metadata["content_type"] == "preamble"

        # Preamble should not be split mid-sentence
        # (Current implementation may split if too large, but should be clean)
        assert first_chunk.start_line == 1

    def test_preamble_exceeding_limit(self):
        """Test preamble exceeding max_chunk_size."""
        # Create a preamble larger than max_chunk_size
        preamble_lines = [
            f"Preamble line {i} with substantial additional text content that makes it longer."
            for i in range(30)
        ]
        preamble = "\n".join(preamble_lines)

        # Add enough structure to trigger structural strategy
        md_text = f"""{preamble}

# Main Title

## Section 1

Content here.

## Section 2

More content.

## Section 3

Final content.
"""

        config = ChunkConfig(max_chunk_size=1000, overlap_size=200)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Should produce multiple chunks
        assert len(chunks) > 1

        # First chunk should still be preamble
        first_chunk = chunks[0]
        assert first_chunk.metadata["content_type"] == "preamble"

        # Check that chunking is reasonable
        assert len(first_chunk.content) > 0


class TestMultipleChunks:
    """Tests for documents requiring multiple chunks."""

    def test_multiple_chunks_with_preamble(self):
        """Test document with preamble that produces multiple chunks."""
        # Create document with preamble + large content
        preamble = "Preamble content before headers.\nMore preamble."

        sections = []
        for i in range(10):
            section = f"""## Section {i}

This is section {i} with substantial content that will help fill up the chunks.
It needs to be long enough to trigger multiple chunks.
More text here to increase size.
Additional paragraphs to make it realistic.
Even more content.
"""
            sections.append(section)

        md_text = f"""{preamble}

# Main Title

{"".join(sections)}
"""

        config = ChunkConfig(max_chunk_size=1000, overlap_size=200)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Should produce multiple chunks
        assert len(chunks) > 2, f"Expected multiple chunks, got {len(chunks)}"

        # Check chunk_index sequence
        indices = [c.metadata["chunk_index"] for c in chunks]
        assert indices == list(
            range(len(chunks))
        ), "chunk_index should be sequential starting from 0"

        # First chunk should be preamble
        assert chunks[0].metadata["content_type"] == "preamble"

        # Subsequent chunks should be sections
        for i in range(1, len(chunks)):
            assert (
                chunks[i].metadata["content_type"] == "section"
            ), f"Chunk {i} should be a section, got {chunks[i].metadata['content_type']}"

    def test_chunk_overlap_consistency(self):
        """Test that chunk overlap is applied consistently."""
        md_text = """Preamble text here.

# Header 1

""" + (
            "Content paragraph. " * 200
        )  # Large content

        config = ChunkConfig(max_chunk_size=500, overlap_size=100)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Check that overlap metadata exists
        for chunk in chunks:
            assert (
                "previous_content" in chunk.metadata or "next_content" in chunk.metadata
            ), f"Chunk {chunk.metadata['chunk_index']} should have overlap metadata"


class TestRichMarkdownStructure:
    """Tests for documents with complex markdown elements."""

    def test_document_with_nested_headers(self):
        """Test document with deeply nested headers."""
        md_text = """# Level 1

## Level 2

### Level 3

#### Level 4

Content at level 4.
"""

        config = ChunkConfig(max_chunk_size=1000, overlap_size=200)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Verify structural strategy is used
        for chunk in chunks:
            assert chunk.metadata["strategy"] == "structural"

        # Check header_path contains hierarchy
        # (At least one chunk should have nested path)
        header_paths = [c.metadata.get("header_path") for c in chunks]
        assert any(
            "/" in path for path in header_paths if path
        ), "Should have hierarchical header paths"

    def test_document_with_lists_and_headers(self):
        """Test document combining headers, lists, and quotes."""
        md_text = """Preamble with intro.

# Main Section

Introduction paragraph.

## Features

- Feature 1
- Feature 2
  - Nested feature 2.1
  - Nested feature 2.2
- Feature 3

## Notes

> This is a quote.
> Multiple lines.

### Subsection

Final content.
"""

        config = ChunkConfig(max_chunk_size=1000, overlap_size=200)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Should use structural strategy (removed code block so it doesn't trigger code_aware)
        assert all(c.metadata["strategy"] == "structural" for c in chunks)

        # Should have preamble
        assert chunks[0].metadata["content_type"] == "preamble"

    def test_document_with_tables(self):
        """Test document with markdown tables."""
        md_text = """# Data

## Table 1

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |

## Summary

Final text.
"""

        config = ChunkConfig(max_chunk_size=1000, overlap_size=200)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Should use code_aware strategy (tables trigger code_aware, not structural)
        assert all(c.metadata["strategy"] == "code_aware" for c in chunks), (
            f"Expected code_aware for document with tables, got strategies: "
            f"{[c.metadata['strategy'] for c in chunks]}"
        )

        # Tables should not be split in the middle (current implementation preserves atomic blocks)
        for chunk in chunks:
            content = chunk.content
            # If chunk has table separator, it should have header row
            if "|---" in content:
                lines_before_sep = content[: content.index("|---")].split("\n")
                # Should have at least one line before separator (the header)
                assert any(
                    "|" in line for line in lines_before_sep
                ), "Table header should be present before separator"


class TestStrategySelectionLogic:
    """Tests for strategy selection logic fixes."""

    def test_structural_preferred_over_list_aware_for_hierarchical_docs(self):
        """
        Test that structural strategy is preferred over list_aware
        for documents with strong hierarchical structure.
        """
        # Document with many headers but some lists
        md_text = """# Main Title

## Section 1

Content here.

### Subsection 1.1

- List item 1
- List item 2

### Subsection 1.2

More content.

## Section 2

### Subsection 2.1

- Item A
- Item B

### Subsection 2.2

Final content.
"""

        parser = Parser()
        analysis = parser.analyze(md_text)
        config = ChunkConfig()
        selector = StrategySelector()
        strategy = selector.select(analysis, config)

        # Should select structural, not list_aware
        assert strategy.name == "structural", (
            f"Expected structural strategy for hierarchical document, got {strategy.name}. "
            f"Headers: {analysis.header_count}, Lists: {analysis.list_count}, "
            f"List ratio: {analysis.list_ratio:.2%}"
        )

    def test_list_aware_for_list_heavy_without_structure(self):
        """Test that list_aware is still selected for list-heavy documents without structure."""
        md_text = """Some introduction text.

- Item 1
- Item 2
- Item 3

Another paragraph.

- Item 4
- Item 5
- Item 6

More text.

- Item 7
- Item 8

Yet more text.

- Item 9
- Item 10

Final paragraph.

- Item 11
- Item 12
- Item 13
"""

        parser = Parser()
        analysis = parser.analyze(md_text)
        config = ChunkConfig()
        selector = StrategySelector()
        strategy = selector.select(analysis, config)

        # Should select list_aware for list-heavy docs without structure
        assert strategy.name == "list_aware", (
            f"Expected list_aware for list-heavy document without structure, got {strategy.name}. "
            f"Lists: {analysis.list_count}, List ratio: {analysis.list_ratio:.2%}"
        )


class TestNextContentBehavior:
    """Tests for next_content and previous_content metadata behavior."""

    def test_next_content_present_in_non_final_chunks(self):
        """Test that next_content is present in all but the last chunk."""
        md_text = """Preamble content.

# Section 1

Content of section 1.

# Section 2

Content of section 2.

# Section 3

Content of section 3.
"""

        config = ChunkConfig(max_chunk_size=100, overlap_size=50)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Should have multiple chunks
        assert len(chunks) > 1

        # All but last chunk should have next_content
        for i in range(len(chunks) - 1):
            assert (
                "next_content" in chunks[i].metadata
            ), f"Chunk {i} should have next_content field"
            assert chunks[i].metadata[
                "next_content"
            ], f"Chunk {i} next_content should not be empty"

        # Last chunk should NOT have next_content
        assert "next_content" not in chunks[-1].metadata or not chunks[-1].metadata.get(
            "next_content"
        ), "Last chunk should not have next_content"

    def test_previous_content_present_in_non_first_chunks(self):
        """Test that previous_content is present in all but the first chunk."""
        md_text = """Preamble content.

# Section 1

Content of section 1.

# Section 2

Content of section 2.

# Section 3

Content of section 3.
"""

        config = ChunkConfig(max_chunk_size=100, overlap_size=50)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Should have multiple chunks
        assert len(chunks) > 1

        # First chunk should NOT have previous_content
        assert "previous_content" not in chunks[0].metadata or not chunks[
            0
        ].metadata.get(
            "previous_content"
        ), "First chunk should not have previous_content"

        # All but first chunk should have previous_content
        for i in range(1, len(chunks)):
            assert (
                "previous_content" in chunks[i].metadata
            ), f"Chunk {i} should have previous_content field"
            assert chunks[i].metadata[
                "previous_content"
            ], f"Chunk {i} previous_content should not be empty"

    def test_next_content_size_limit(self):
        """Test that next_content is limited in size."""
        # Create large sections
        large_section = "This is a very long section. " * 100
        md_text = f"""# Section 1

{large_section}

# Section 2

{large_section}
"""

        config = ChunkConfig(max_chunk_size=2000, overlap_size=200)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Check next_content in all non-final chunks
        for i in range(len(chunks) - 1):
            if "next_content" in chunks[i].metadata:
                next_content = chunks[i].metadata["next_content"]
                next_chunk_size = len(chunks[i + 1].content)
                # Adaptive cap: should not exceed 35% of next chunk size
                expected_max = int(next_chunk_size * 0.35)
                # Allow some overhead for word boundary adjustment
                assert len(next_content) <= expected_max * 1.2, (
                    f"Chunk {i} next_content size {len(next_content)} exceeds adaptive limit "
                    f"(expected <= {expected_max * 1.2}, next chunk size: {next_chunk_size})"
                )

    def test_next_content_contains_beginning_of_next_chunk(self):
        """Test that next_content actually contains the beginning of the next chunk."""
        md_text = """# Section 1

Content of section 1.

# Section 2 - Unique Title

Content of section 2.
"""

        config = ChunkConfig(max_chunk_size=100, overlap_size=50)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        if len(chunks) > 1:
            # Find a chunk with next_content
            for i in range(len(chunks) - 1):
                if "next_content" in chunks[i].metadata:
                    next_content = chunks[i].metadata["next_content"]
                    next_chunk_content = chunks[i + 1].content

                    # next_content should be a prefix of next chunk's content
                    # (or very close due to word boundary adjustments)
                    assert any(
                        next_chunk_content.startswith(next_content[: len(part)])
                        for part in [
                            next_content,
                            next_content.split()[0] if next_content else "",
                        ]
                    ), (
                        f"next_content should match beginning of next chunk. "
                        f"next_content: {next_content[:50]}..., "
                        f"next chunk: {next_chunk_content[:50]}..."
                    )

    def test_overlap_size_metadata_field(self):
        """Test that overlap_size metadata field is present when applicable."""
        md_text = """# Section 1

Content 1.

# Section 2

Content 2.

# Section 3

Content 3.
"""

        config = ChunkConfig(max_chunk_size=100, overlap_size=50)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Chunks with previous_content should have overlap_size metadata
        for i, chunk in enumerate(chunks):
            if "previous_content" in chunk.metadata:
                assert (
                    "overlap_size" in chunk.metadata
                ), f"Chunk {i} has previous_content but missing overlap_size metadata"
                # overlap_size should be reasonable
                overlap_size = chunk.metadata["overlap_size"]
                assert (
                    overlap_size > 0
                ), f"Chunk {i} overlap_size should be positive, got {overlap_size}"

    def test_adaptive_overlap_for_large_chunks(self):
        """Test that overlap scales with chunk size for large chunks."""
        # Create document with very large chunks (8KB each)
        large_content = "This is substantial content for a large chunk. " * 200
        md_text = f"""# Section 1

{large_content}

# Section 2

{large_content}

# Section 3

{large_content}
"""

        config = ChunkConfig(max_chunk_size=10000, overlap_size=500)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Verify chunks are large
        assert len(chunks) > 1
        for chunk in chunks:
            # Most chunks should be sizeable
            if "next_content" in chunk.metadata or "previous_content" in chunk.metadata:
                # For large chunks, overlap should be allowed to scale
                # Max = 35% of chunk size, which for 8KB chunk = ~2800 chars
                chunk_size = len(chunk.content)
                max_expected_overlap = int(chunk_size * 0.35)

                if "next_content" in chunk.metadata:
                    next_overlap = len(chunk.metadata["next_content"])
                    # Should be capped at 35% of next chunk size
                    assert (
                        next_overlap <= max_expected_overlap * 1.2
                    ), f"Overlap {next_overlap} exceeds adaptive limit for chunk size {chunk_size}"

    def test_adaptive_overlap_for_small_chunks(self):
        """Test that overlap respects configured size for small chunks."""
        md_text = """# S1

Small.

# S2

Tiny.

# S3

Brief.
"""

        config = ChunkConfig(max_chunk_size=100, overlap_size=50)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # For small chunks, configured overlap_size should be effective limit
        for i in range(len(chunks) - 1):
            if "next_content" in chunks[i].metadata:
                next_content = chunks[i].metadata["next_content"]
                # For small chunks, 35% might be less than configured overlap
                # So either cap applies
                next_chunk_size = len(chunks[i + 1].content)
                adaptive_cap = int(next_chunk_size * 0.35)
                effective_cap = min(config.overlap_size, adaptive_cap)

                assert (
                    len(next_content) <= effective_cap * 1.2
                ), "Overlap should respect minimum of configured and adaptive cap"

    def test_overlap_scales_proportionally(self):
        """Test that larger chunks get proportionally larger overlap."""
        # Create documents with different chunk sizes
        small_doc = """# Section 1

Small content.

# Section 2

More small.
"""

        large_content = "Large content paragraph. " * 300
        large_doc = f"""# Section 1

{large_content}

# Section 2

{large_content}
"""

        # Same overlap_size config
        config_small = ChunkConfig(max_chunk_size=200, overlap_size=100)
        config_large = ChunkConfig(max_chunk_size=10000, overlap_size=100)

        chunker_small = MarkdownChunker(config_small)
        chunker_large = MarkdownChunker(config_large)

        chunks_small = chunker_small.chunk(small_doc)
        chunks_large = chunker_large.chunk(large_doc)

        # Collect overlap sizes
        small_overlaps = [
            len(c.metadata.get("next_content", ""))
            for c in chunks_small
            if "next_content" in c.metadata
        ]
        large_overlaps = [
            len(c.metadata.get("next_content", ""))
            for c in chunks_large
            if "next_content" in c.metadata
        ]

        if small_overlaps and large_overlaps:
            # Large chunks should allow larger overlap (adaptive)
            avg_small = sum(small_overlaps) / len(small_overlaps)
            avg_large = sum(large_overlaps) / len(large_overlaps)

            # Large chunk overlaps can be larger (not limited to config value)
            # They scale with chunk size up to 35%
            assert avg_large >= avg_small, (
                f"Large chunks should allow larger overlap: "
                f"small avg={avg_small}, large avg={avg_large}"
            )
