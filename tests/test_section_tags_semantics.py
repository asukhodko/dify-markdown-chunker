"""
Tests for section_tags relative semantics.

These tests verify that section_tags contains headers that are children
of the root section (last header in header_path), using RELATIVE logic
based on contextual_level, not absolute max_structural_level.

**Feature: header-path-semantics**
**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 6.1, 6.2**
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from markdown_chunker_v2.config import ChunkConfig
from markdown_chunker_v2.parser import Parser
from markdown_chunker_v2.strategies.structural import StructuralStrategy


class TestSectionTagsRelativeLogic:
    """Test that section_tags uses relative logic based on contextual_level."""

    def test_h2_root_h3_children(self):
        """
        When root section is H2, H3 headers should be in section_tags.

        **Validates: Requirements 2.1, 2.2**
        """
        doc = """# Main
## DEV-4
### Scope
Content about scope
### Impact
Content about impact
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=2000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        # Find the DEV-4 chunk
        dev_chunk = next(
            c for c in chunks if "DEV-4" in c.metadata.get("header_path", "")
        )

        assert dev_chunk.metadata["header_path"] == "/Main/DEV-4"
        assert dev_chunk.metadata["section_tags"] == ["Scope", "Impact"]

    def test_h3_root_h4_children_with_max_level_3(self):
        """
        When max_structural_level=3 and root section is H3, H4 headers should be in section_tags.

        **Validates: Requirements 2.1**
        """
        doc = """# Main
## Category
### DEV-4
#### Scope
Content about scope
#### Impact
Content about impact
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=2000)
        strategy = StructuralStrategy(max_structural_level=3)

        chunks = strategy.apply(doc, analysis, config)

        # Find the DEV-4 chunk
        dev_chunk = next(
            c for c in chunks if c.metadata.get("header_path", "").endswith("DEV-4")
        )

        assert dev_chunk.metadata["header_path"] == "/Main/Category/DEV-4"
        assert dev_chunk.metadata["section_tags"] == ["Scope", "Impact"]

    def test_h3_in_section_tags_when_max_level_2(self):
        """
        When max_structural_level=2, H3 headers stay in section_tags (not header_path).

        **Validates: Requirements 2.1**
        """
        doc = """# Main
## Category
### DEV-4
#### Scope
Content
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=2000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        # Find the Category chunk
        cat_chunk = next(
            c for c in chunks if c.metadata.get("header_path", "").endswith("Category")
        )

        assert cat_chunk.metadata["header_path"] == "/Main/Category"
        # DEV-4 and Scope should both be in section_tags
        assert "DEV-4" in cat_chunk.metadata["section_tags"]
        assert "Scope" in cat_chunk.metadata["section_tags"]


class TestSectionTagsDeduplication:
    """Test that section_tags are deduplicated."""

    def test_duplicate_headers_deduplicated(self):
        """
        When same header text appears multiple times, section_tags should contain unique values.

        **Validates: Requirements 2.4**
        """
        doc = """# Main
## Section
### Note
First note content
### Note
Second note content
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=2000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        section_chunk = next(
            c for c in chunks if c.metadata.get("header_path", "").endswith("Section")
        )

        # Should have only one "Note" despite two occurrences
        assert section_chunk.metadata["section_tags"].count("Note") == 1


class TestSectionTagsOrderPreservation:
    """Test that section_tags preserve order of appearance."""

    def test_order_preserved(self):
        """
        section_tags should preserve the order headers appear in the chunk.

        **Validates: Requirements 2.5**
        """
        doc = """# Main
## Section
### Alpha
Content
### Beta
Content
### Gamma
Content
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=2000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        section_chunk = next(
            c for c in chunks if c.metadata.get("header_path", "").endswith("Section")
        )

        assert section_chunk.metadata["section_tags"] == ["Alpha", "Beta", "Gamma"]


class TestSectionTagsEmpty:
    """Test that section_tags is empty when appropriate."""

    def test_empty_when_no_child_headers(self):
        """
        section_tags should be empty when chunk has no headers deeper than root.

        **Validates: Requirements 2.3**
        """
        doc = """# Main
## Section
Just plain content without any subheaders.
More content here.
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=2000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        section_chunk = next(
            c for c in chunks if c.metadata.get("header_path", "").endswith("Section")
        )

        assert section_chunk.metadata["section_tags"] == []

    def test_empty_for_single_header_chunk(self):
        """
        section_tags should be empty for chunks containing only a single header.

        **Validates: Requirements 2.3, 4.2**
        """
        doc = """# Main Title
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=2000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        assert len(chunks) == 1
        assert chunks[0].metadata["section_tags"] == []


class TestHeaderPathStability:
    """Test that header_path is stable when local headers are reordered."""

    def test_header_path_stable_on_reorder(self):
        """
        header_path should remain the same when local headers are reordered.

        **Validates: Requirements 6.1**
        """
        doc1 = """# Main
## Section
### Alpha
Content
### Beta
Content
"""
        doc2 = """# Main
## Section
### Beta
Content
### Alpha
Content
"""
        parser = Parser()
        config = ChunkConfig(max_chunk_size=2000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks1 = strategy.apply(doc1, parser.analyze(doc1), config)
        chunks2 = strategy.apply(doc2, parser.analyze(doc2), config)

        section1 = next(
            c for c in chunks1 if c.metadata.get("header_path", "").endswith("Section")
        )
        section2 = next(
            c for c in chunks2 if c.metadata.get("header_path", "").endswith("Section")
        )

        # header_path should be identical
        assert section1.metadata["header_path"] == section2.metadata["header_path"]

    def test_section_tags_reflect_new_order(self):
        """
        section_tags should reflect the new order when local headers are reordered.

        **Validates: Requirements 6.2**
        """
        doc1 = """# Main
## Section
### Alpha
Content
### Beta
Content
"""
        doc2 = """# Main
## Section
### Beta
Content
### Alpha
Content
"""
        parser = Parser()
        config = ChunkConfig(max_chunk_size=2000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks1 = strategy.apply(doc1, parser.analyze(doc1), config)
        chunks2 = strategy.apply(doc2, parser.analyze(doc2), config)

        section1 = next(
            c for c in chunks1 if c.metadata.get("header_path", "").endswith("Section")
        )
        section2 = next(
            c for c in chunks2 if c.metadata.get("header_path", "").endswith("Section")
        )

        # section_tags should reflect the order in each document
        assert section1.metadata["section_tags"] == ["Alpha", "Beta"]
        assert section2.metadata["section_tags"] == ["Beta", "Alpha"]


class TestPreambleMetadata:
    """Test preamble chunk metadata."""

    def test_preamble_has_correct_metadata(self):
        """
        Preamble chunks should have header_path="/__preamble__" and section_tags=[].

        **Validates: Requirements 3.1, 3.2, 3.3**
        """
        doc = """This is preamble content.
More preamble here.

# First Header
Content under header.
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=2000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        preamble = chunks[0]
        assert preamble.metadata["header_path"] == "/__preamble__"
        assert preamble.metadata["section_tags"] == []
        assert preamble.metadata["content_type"] == "preamble"


class TestSectionTagsPropertyTests:
    """Property-based tests for section_tags semantics."""

    @given(
        st.lists(
            st.text(
                min_size=1,
                max_size=20,
                alphabet=st.characters(
                    whitelist_categories=("L", "N"),
                ),
            ).filter(lambda x: x.strip()),
            min_size=1,
            max_size=5,
            unique=True,
        )
    )
    @settings(max_examples=50)
    def test_property_section_tags_subset_of_chunk_headers(self, header_texts):
        """
        Property: section_tags should only contain headers that exist in the chunk.

        **Property: section_tags subset of chunk headers**
        **Validates: Requirements 2.1**
        """
        # Normalize header texts (strip whitespace as parser does)
        normalized_texts = [t.strip() for t in header_texts]

        # Build a document with H2 root and H3 children
        h3_sections = "\n".join(
            f"### {text}\nContent for {text}\n" for text in header_texts
        )
        doc = f"""# Main
## Section
{h3_sections}
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=5000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        # Find section chunk
        section_chunks = [
            c for c in chunks if c.metadata.get("header_path", "").endswith("Section")
        ]
        if section_chunks:
            section_chunk = section_chunks[0]
            # All section_tags should be from our normalized header_texts
            for tag in section_chunk.metadata.get("section_tags", []):
                assert tag in normalized_texts, f"Tag '{tag}' not in original headers"

    @given(st.integers(min_value=2, max_value=5))
    @settings(max_examples=20)
    def test_property_max_structural_level_affects_chunking(self, max_level):
        """
        Property: max_structural_level determines chunk boundaries.

        Headers at level <= max_structural_level create new chunks.
        Headers at level > max_structural_level stay in section_tags.

        **Property: max_structural_level enforcement**
        **Validates: Requirements 1.2, 2.1**
        """
        # Create document with headers at levels 1-5
        doc = """# Level 1
## Level 2
### Level 3
#### Level 4
##### Level 5
Content here
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=5000)
        strategy = StructuralStrategy(max_structural_level=max_level)

        chunks = strategy.apply(doc, analysis, config)

        # Count chunks (excluding potential preamble)
        structural_chunks = [
            c for c in chunks if c.metadata.get("content_type") != "preamble"
        ]

        # Number of chunks should equal number of headers at level <= max_level
        # In our doc: Level 1 (H1), Level 2 (H2), Level 3 (H3), Level 4 (H4), Level 5 (H5)
        expected_chunks = min(max_level, 5)  # We have 5 header levels
        assert len(structural_chunks) == expected_chunks

    @given(
        st.lists(
            st.text(
                min_size=1,
                max_size=15,
                alphabet=st.characters(whitelist_categories=("L",)),
            ).filter(lambda x: x.strip()),
            min_size=2,
            max_size=4,
            unique=True,
        )
    )
    @settings(max_examples=30)
    def test_property_section_tags_order_matches_document_order(self, header_texts):
        """
        Property: section_tags order should match the order headers appear in document.

        **Property: section_tags order preservation**
        **Validates: Requirements 2.5**
        """
        # Build document with headers in specific order
        h3_sections = "\n".join(f"### {text}\nContent\n" for text in header_texts)
        doc = f"""# Main
## Section
{h3_sections}
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=5000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        section_chunks = [
            c for c in chunks if c.metadata.get("header_path", "").endswith("Section")
        ]
        if section_chunks:
            section_chunk = section_chunks[0]
            tags = section_chunk.metadata.get("section_tags", [])
            # Tags should be in same order as header_texts
            assert tags == header_texts

    @given(
        st.text(
            min_size=1,
            max_size=20,
            alphabet=st.characters(
                whitelist_categories=("L", "N"), whitelist_characters=" "
            ),
        ).filter(lambda x: x.strip())
    )
    @settings(max_examples=30)
    def test_property_root_section_not_in_section_tags(self, header_text):
        """
        Property: The root section header should NOT appear in section_tags.

        **Property: root section exclusion**
        **Validates: Requirements 2.1**
        """
        doc = f"""# Main
## {header_text}
### Child
Content
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=5000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        # Find the chunk with our header in path
        for chunk in chunks:
            path = chunk.metadata.get("header_path", "")
            if header_text in path:
                tags = chunk.metadata.get("section_tags", [])
                # Root section should NOT be in section_tags
                assert (
                    header_text not in tags
                ), f"Root '{header_text}' should not be in section_tags"


class TestNestedSections:
    """Test deeply nested section structures."""

    def test_deeply_nested_h4_in_section_tags(self):
        """
        H4 headers should appear in section_tags when root is H2.

        **Validates: Requirements 5.1, 5.2**
        """
        doc = """# Main
## Scope
### Subsection
#### Описание
Content about description
#### Итоги работы
Content about results
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=5000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        scope_chunk = next(
            c for c in chunks if c.metadata.get("header_path", "").endswith("Scope")
        )

        assert scope_chunk.metadata["header_path"] == "/Main/Scope"
        # All nested headers should be in section_tags
        assert "Subsection" in scope_chunk.metadata["section_tags"]
        assert "Описание" in scope_chunk.metadata["section_tags"]
        assert "Итоги работы" in scope_chunk.metadata["section_tags"]

    def test_mixed_depth_headers(self):
        """
        Mixed depth headers (H3, H4, H5) should all appear in section_tags.

        **Validates: Requirements 2.1, 2.5**
        """
        doc = """# Main
## Section
### Level 3
#### Level 4
##### Level 5
Content
### Another Level 3
Content
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=5000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        section_chunk = next(
            c for c in chunks if c.metadata.get("header_path", "").endswith("Section")
        )

        tags = section_chunk.metadata["section_tags"]
        assert "Level 3" in tags
        assert "Level 4" in tags
        assert "Level 5" in tags
        assert "Another Level 3" in tags
        # Order should be preserved
        assert tags.index("Level 3") < tags.index("Level 4")
        assert tags.index("Level 4") < tags.index("Level 5")


class TestDEV4Contract:
    """
    Contract tests for DEV-4 grade matrix chunking.

    These tests ensure that all chunks within a section (e.g., DEV-4)
    have the SAME header_path pointing to the section root, with
    subsections in section_tags.

    **Validates: Requirements 1.2, 1.3, 2.2, 7.2, 7.3**
    """

    def test_dev4_all_chunks_same_header_path(self):
        """
        All chunks from DEV-4 section must have header_path ending with DEV-4,
        NOT with any H3 subsection like Complexity or Leadership.

        **Validates: Requirements 1.2, 1.3**
        """
        doc = """# Критерии грейдов DEV
## DEV-4 (Junior-, Младший разработчик)
### Scope
Content about scope here with enough text to potentially split.
### Impact (Delivery)
Content about impact delivery here.
### Complexity
Content about complexity here.
### Leadership
Content about leadership here.
### Improvement
Content about improvement here.
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=2000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        # Find DEV-4 chunk(s)
        dev4_chunks = [
            c for c in chunks if "DEV-4" in c.metadata.get("header_path", "")
        ]

        assert len(dev4_chunks) >= 1, "Should have at least one DEV-4 chunk"

        for chunk in dev4_chunks:
            path = chunk.metadata["header_path"]
            # header_path MUST end with DEV-4, NOT with any H3
            assert path.endswith(
                "DEV-4 (Junior-, Младший разработчик)"
            ), f"header_path should end with DEV-4, got: {path}"
            # header_level MUST be 2 (H2)
            assert (
                chunk.metadata["header_level"] == 2
            ), f"header_level should be 2, got: {chunk.metadata['header_level']}"

    def test_dev4_section_tags_contain_all_h3(self):
        """
        section_tags must contain all H3 subsections within the chunk.

        **Validates: Requirements 2.2, 7.3**
        """
        doc = """# Критерии грейдов DEV
## DEV-4 (Junior-, Младший разработчик)
### Complexity
Content about complexity.
### Leadership
Content about leadership.
### Improvement
Content about improvement.
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=2000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        dev4_chunk = next(
            c for c in chunks if "DEV-4" in c.metadata.get("header_path", "")
        )

        tags = dev4_chunk.metadata["section_tags"]
        assert "Complexity" in tags
        assert "Leadership" in tags
        assert "Improvement" in tags

    def test_no_h3_in_header_path_regression(self):
        """
        REGRESSION TEST: header_path must NEVER contain H3 subsections
        when max_structural_level=2.

        This test catches the bug where first H3 in chunk was incorrectly
        added to header_path instead of section_tags.
        """
        doc = """# Main
## Section
### Subsection1
Content
### Subsection2
Content
"""
        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=2000)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        for chunk in chunks:
            path = chunk.metadata.get("header_path", "")
            # Path should NOT contain Subsection1 or Subsection2
            assert (
                "Subsection1" not in path
            ), f"H3 'Subsection1' should NOT be in header_path: {path}"
            assert (
                "Subsection2" not in path
            ), f"H3 'Subsection2' should NOT be in header_path: {path}"


class TestSubChunksInheritHeaderPath:
    """
    Tests for sub-chunks inheriting header_path from parent section.

    When a section is split into multiple chunks due to max_chunk_size,
    ALL sub-chunks must have the SAME header_path as the parent section.
    """

    def test_sub_chunks_same_header_path(self):
        """
        All sub-chunks from a split section must have identical header_path.

        **Validates: Requirements 1.2, 1.3**
        """
        # Create a very large section that will definitely be split
        long_content = "Word " * 500  # ~2500 chars per subsection
        doc = f"""# Main
## Section
### Sub1
{long_content}
### Sub2
{long_content}
"""

        parser = Parser()
        analysis = parser.analyze(doc)
        # Very small chunk size to force splitting
        config = ChunkConfig(max_chunk_size=1500, overlap_size=100)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        # Find all chunks from "Section"
        section_chunks = [
            c for c in chunks if "Section" in c.metadata.get("header_path", "")
        ]

        # If section was split, verify all have same path
        if len(section_chunks) >= 2:
            paths = [c.metadata["header_path"] for c in section_chunks]
            assert all(
                p == paths[0] for p in paths
            ), f"All sub-chunks should have same header_path, got: {paths}"

        # header_path should end with "Section", not any H3
        for chunk in section_chunks:
            path = chunk.metadata["header_path"]
            assert path.endswith("Section"), f"Path should end with Section: {path}"
            assert "Sub1" not in path
            assert "Sub2" not in path

    def test_sub_chunks_header_level_from_parent(self):
        """
        All sub-chunks must have header_level from parent section.
        """
        doc = (
            """# Main
## Section
### Sub1
"""
            + "Content " * 100
            + """
### Sub2
"""
            + "Content " * 100
        )

        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=300, overlap_size=50)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        section_chunks = [
            c for c in chunks if "Section" in c.metadata.get("header_path", "")
        ]

        # All must have header_level=2 (H2)
        for chunk in section_chunks:
            assert (
                chunk.metadata["header_level"] == 2
            ), f"header_level should be 2, got: {chunk.metadata['header_level']}"

    def test_sub_chunks_individual_section_tags(self):
        """
        Each sub-chunk should have section_tags for headers IN THAT CHUNK ONLY.
        """
        doc = (
            """# Main
## Section
### Alpha
"""
            + "Content " * 100
            + """
### Beta
"""
            + "Content " * 100
            + """
### Gamma
"""
            + "Content " * 100
        )

        parser = Parser()
        analysis = parser.analyze(doc)
        config = ChunkConfig(max_chunk_size=250, overlap_size=50)
        strategy = StructuralStrategy(max_structural_level=2)

        chunks = strategy.apply(doc, analysis, config)

        section_chunks = [
            c for c in chunks if "Section" in c.metadata.get("header_path", "")
        ]

        # Each chunk should have section_tags only for headers it contains
        for chunk in section_chunks:
            tags = chunk.metadata.get("section_tags", [])
            content = chunk.content
            for tag in tags:
                assert (
                    f"### {tag}" in content or f"## {tag}" in content
                ), f"Tag '{tag}' not found in chunk content"
