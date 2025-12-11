"""
Unit tests for hierarchical chunking functionality.

Tests HierarchyBuilder and HierarchicalChunkingResult classes.
"""

import pytest

from markdown_chunker_v2 import ChunkConfig, MarkdownChunker


class TestHierarchyBuilder:
    """Tests for HierarchyBuilder component."""

    @pytest.fixture
    def chunker(self):
        """Create chunker with default config."""
        return MarkdownChunker(ChunkConfig(max_chunk_size=500))

    def test_creates_hierarchy(self, chunker):
        """Hierarchy is created correctly."""
        text = """# Document Title

## Section 1

Content of section 1.

## Section 2

Content of section 2.

### Subsection 2.1

More content.
"""
        result = chunker.chunk_hierarchical(text)

        # Root created
        root = result.get_chunk(result.root_id)
        assert root is not None
        assert root.metadata.get("hierarchy_level") == 0

        # Root has children
        children = result.get_children(result.root_id)
        assert len(children) >= 1  # At least one child

    def test_assigns_unique_ids(self, chunker):
        """All chunks get unique IDs."""
        text = "# H1\n\n## H2\n\nText\n\n## H3\n\nMore"
        result = chunker.chunk_hierarchical(text)

        chunk_ids = [
            c.metadata.get("chunk_id")
            for c in result.chunks
            if c.metadata.get("chunk_id")
        ]

        # All IDs exist and are unique
        assert len(chunk_ids) == len(set(chunk_ids))
        assert len(chunk_ids) == len(result.chunks)

    def test_parent_child_links_valid(self, chunker):
        """All parent-child links are bidirectional."""
        text = "# Doc\n\n## Sec1\n\nText\n\n## Sec2\n\nMore"
        result = chunker.chunk_hierarchical(text)

        for chunk in result.chunks:
            parent_id = chunk.metadata.get("parent_id")
            if parent_id:
                # Parent exists
                parent = result.get_chunk(parent_id)
                assert parent is not None, f"Parent {parent_id} not found"

                # Parent's children includes this chunk
                children_ids = parent.metadata.get("children_ids", [])
                assert chunk.metadata["chunk_id"] in children_ids

    def test_sibling_links_correct(self, chunker):
        """Sibling links are correct and ordered."""
        text = "# Doc\n\n## Sec1\n\nA\n\n## Sec2\n\nB\n\n## Sec3\n\nC"
        result = chunker.chunk_hierarchical(text)

        # Find sections (level 2)
        sections = [
            c for c in result.chunks
            if c.metadata.get("header_level") == 2
        ]
        sections.sort(key=lambda c: c.start_line)

        for i, section in enumerate(sections):
            # Prev sibling
            if i > 0:
                prev_id = section.metadata.get("prev_sibling_id")
                assert prev_id == sections[i - 1].metadata["chunk_id"]
            else:
                assert section.metadata.get("prev_sibling_id") is None

            # Next sibling
            if i < len(sections) - 1:
                next_id = section.metadata.get("next_sibling_id")
                assert next_id == sections[i + 1].metadata["chunk_id"]
            else:
                assert section.metadata.get("next_sibling_id") is None

    def test_hierarchy_levels_assigned(self, chunker):
        """Hierarchy levels are correctly assigned."""
        text = """# L1

Content at level 1.

## L2

Content at level 2.

### L3

Content at level 3.
"""
        result = chunker.chunk_hierarchical(text)

        # Check level mapping
        for chunk in result.chunks:
            if chunk.metadata.get("is_root"):
                assert chunk.metadata.get("hierarchy_level") == 0
            else:
                header_level = chunk.metadata.get("header_level", 3)
                hierarchy_level = chunk.metadata.get("hierarchy_level", 3)
                # H1->1, H2->2, H3+->3
                expected = min(header_level, 3)
                assert hierarchy_level == expected

    def test_marks_leaves_correctly(self, chunker):
        """Leaf chunks are marked correctly."""
        text = "# Doc\n\n## Sec\n\nText"
        result = chunker.chunk_hierarchical(text)

        for chunk in result.chunks:
            children = chunk.metadata.get("children_ids", [])
            is_leaf = chunk.metadata.get("is_leaf", True)

            if len(children) == 0:
                assert is_leaf is True
            else:
                assert is_leaf is False


class TestHierarchicalChunkingResult:
    """Tests for HierarchicalChunkingResult navigation methods."""

    @pytest.fixture
    def chunker(self):
        """Create chunker with default config."""
        return MarkdownChunker(ChunkConfig(max_chunk_size=1000))

    def test_get_chunk_by_id(self, chunker):
        """get_chunk returns correct chunk."""
        text = "# Doc\n\n## Sec\n\nText"
        result = chunker.chunk_hierarchical(text)

        for chunk in result.chunks:
            chunk_id = chunk.metadata.get("chunk_id")
            retrieved = result.get_chunk(chunk_id)
            assert retrieved is chunk

    def test_get_children(self, chunker):
        """get_children returns all children."""
        text = "# Doc\n\n## Sec1\n\nText1\n\n## Sec2\n\nText2"
        result = chunker.chunk_hierarchical(text)

        root = result.get_chunk(result.root_id)
        children = result.get_children(result.root_id)

        # Verify all children belong to root
        for child in children:
            assert child.metadata.get("parent_id") == root.metadata["chunk_id"]

    def test_get_parent(self, chunker):
        """get_parent returns correct parent."""
        text = "# Doc\n\n## Sec\n\n### Sub\n\nContent"
        result = chunker.chunk_hierarchical(text)

        # Find deepest chunk
        deepest = max(
            result.chunks,
            key=lambda c: c.metadata.get("header_level", 0)
        )

        parent = result.get_parent(deepest.metadata["chunk_id"])
        assert parent is not None
        assert deepest.metadata["parent_id"] == parent.metadata["chunk_id"]

    def test_get_ancestors(self, chunker):
        """get_ancestors returns path to root."""
        text = "# Doc\n\n## Sec\n\n### Sub\n\nContent"
        result = chunker.chunk_hierarchical(text)

        # Find deepest chunk
        deepest = max(
            result.chunks,
            key=lambda c: c.metadata.get("header_level", 0)
        )

        ancestors = result.get_ancestors(deepest.metadata["chunk_id"])

        # Should have path to root
        assert len(ancestors) >= 1
        # Last ancestor is root
        assert ancestors[-1].metadata.get("chunk_id") == result.root_id

    def test_get_siblings(self, chunker):
        """get_siblings returns all siblings including self."""
        text = "# Doc\n\n## Sec1\n\nA\n\n## Sec2\n\nB\n\n## Sec3\n\nC"
        result = chunker.chunk_hierarchical(text)

        # Find a section
        sections = [
            c for c in result.chunks
            if c.metadata.get("header_level") == 2
        ]

        if len(sections) > 1:
            sec = sections[1]
            siblings = result.get_siblings(sec.metadata["chunk_id"])

            # Self is in siblings
            assert sec in siblings
            # All siblings have same parent
            parent_ids = {s.metadata.get("parent_id") for s in siblings}
            assert len(parent_ids) == 1

    def test_get_flat_chunks(self, chunker):
        """get_flat_chunks returns only leaf chunks."""
        text = "# Doc\n\n## Sec\n\nText"
        result = chunker.chunk_hierarchical(text)

        flat = result.get_flat_chunks()

        for chunk in flat:
            assert chunk.metadata.get("is_leaf") is True
            assert len(chunk.metadata.get("children_ids", [])) == 0

    def test_get_by_level(self, chunker):
        """get_by_level returns chunks at specific level."""
        text = "# Doc\n\n## Sec1\n\nA\n\n## Sec2\n\nB"
        result = chunker.chunk_hierarchical(text)

        level_0 = result.get_by_level(0)
        assert len(level_0) == 1  # Root only

        level_2 = result.get_by_level(2)
        assert len(level_2) >= 1  # At least one H2 section

    def test_to_tree_dict_serializable(self, chunker):
        """to_tree_dict creates JSON-serializable structure."""
        import json

        text = "# Doc\n\n## Sec\n\nText"
        result = chunker.chunk_hierarchical(text)

        tree = result.to_tree_dict()

        # Should serialize without errors
        json_str = json.dumps(tree)
        assert len(json_str) > 0

        # Should have expected structure
        assert "id" in tree
        assert "children" in tree
        assert tree["id"] == result.root_id


class TestHierarchyEdgeCases:
    """Edge case tests for hierarchical chunking."""

    @pytest.fixture
    def chunker(self):
        """Create chunker with default config."""
        return MarkdownChunker(ChunkConfig(max_chunk_size=500))

    def test_document_without_headers(self, chunker):
        """Document without headers still creates hierarchy."""
        text = "Just plain text without any headers."
        result = chunker.chunk_hierarchical(text)

        # Root created
        assert result.root_id
        # Flat chunks have content
        flat = result.get_flat_chunks()
        assert len(flat) >= 1

    def test_only_headers(self, chunker):
        """Document with only headers."""
        text = "# H1\n\n## H2\n\n### H3"
        result = chunker.chunk_hierarchical(text)

        # Should not crash
        assert len(result.chunks) >= 1

    def test_preamble_handling(self, chunker):
        """Preamble is child of root."""
        text = "Some preamble text.\n\n# Main Title\n\nContent."
        result = chunker.chunk_hierarchical(text)

        preamble = [
            c for c in result.chunks
            if c.metadata.get("content_type") == "preamble"
        ]

        if preamble:
            # Preamble is child of root
            assert preamble[0].metadata.get("parent_id") == result.root_id

    def test_deep_hierarchy(self, chunker):
        """Deep hierarchy (H6) is handled."""
        text = """# L1
## L2
### L3
#### L4
##### L5
###### L6

Deep content.
"""
        result = chunker.chunk_hierarchical(text)

        # Should not crash
        assert len(result.chunks) >= 1
        # Root created
        assert result.get_chunk(result.root_id) is not None

    def test_same_header_path_chunks(self, chunker):
        """Multiple chunks with same header_path are siblings."""
        # Very long section that will be split
        long_content = "\n\n".join([f"Paragraph {i}." * 20 for i in range(10)])
        text = f"# Doc\n\n## Long Section\n\n{long_content}"

        small_config = ChunkConfig(max_chunk_size=200, overlap_size=50)
        small_chunker = MarkdownChunker(small_config)
        result = small_chunker.chunk_hierarchical(text)

        # Find chunks with same path
        long_section_chunks = [
            c for c in result.chunks
            if "Long Section" in c.metadata.get("header_path", "")
        ]

        # They should be siblings
        if len(long_section_chunks) > 1:
            for i in range(1, len(long_section_chunks)):
                parent1 = long_section_chunks[i - 1].metadata.get("parent_id")
                parent2 = long_section_chunks[i].metadata.get("parent_id")
                # Same parent
                assert parent1 == parent2

    def test_empty_document(self, chunker):
        """Empty document doesn't crash."""
        result = chunker.chunk_hierarchical("")

        # Should not crash
        assert result.chunks == []

    def test_to_tree_dict_no_circular_refs(self, chunker):
        """Tree serialization has no circular references."""
        import json

        text = "# Doc\n\n## Sec\n\nText"
        result = chunker.chunk_hierarchical(text)

        tree = result.to_tree_dict()

        # Should serialize without circular reference errors
        json_str = json.dumps(tree)
        assert len(json_str) > 0


class TestHierarchyInvariants:
    """Property-based invariant tests for hierarchy."""

    @pytest.fixture
    def chunker(self):
        """Create chunker with default config."""
        return MarkdownChunker(ChunkConfig(max_chunk_size=2000))

    def test_no_orphans(self, chunker):
        """HIER-1: Every non-root chunk has valid parent."""
        text = "# Doc\n\n## Sec1\n\nText\n\n## Sec2\n\nMore"
        result = chunker.chunk_hierarchical(text)

        for chunk in result.chunks:
            if chunk.metadata.get("is_root"):
                assert chunk.metadata.get("parent_id") is None
            else:
                parent_id = chunk.metadata.get("parent_id")
                assert parent_id is not None
                parent = result.get_chunk(parent_id)
                assert parent is not None

    def test_symmetric_children(self, chunker):
        """HIER-2: Parent-child links are bidirectional."""
        text = "# Doc\n\n## Sec1\n\nText\n\n### Sub1\n\nDeeper"
        result = chunker.chunk_hierarchical(text)

        for chunk in result.chunks:
            children_ids = chunk.metadata.get("children_ids", [])
            for child_id in children_ids:
                child = result.get_chunk(child_id)
                assert child is not None
                assert child.metadata.get("parent_id") == chunk.metadata["chunk_id"]

    def test_sibling_ordering(self, chunker):
        """HIER-3: Siblings ordered by start_line."""
        text = "# Doc\n\n## Sec1\n\nA\n\n## Sec2\n\nB\n\n## Sec3\n\nC"
        result = chunker.chunk_hierarchical(text)

        for chunk in result.chunks:
            prev_id = chunk.metadata.get("prev_sibling_id")
            next_id = chunk.metadata.get("next_sibling_id")

            if prev_id:
                prev = result.get_chunk(prev_id)
                assert prev.start_line < chunk.start_line

            if next_id:
                next_chunk = result.get_chunk(next_id)
                assert chunk.start_line < next_chunk.start_line

    def test_level_consistency(self, chunker):
        """HIER-4: Children have level >= parent level."""
        text = "# Doc\n\n## Sec\n\n### Sub\n\nContent"
        result = chunker.chunk_hierarchical(text)

        for chunk in result.chunks:
            children_ids = chunk.metadata.get("children_ids", [])
            for child_id in children_ids:
                child = result.get_chunk(child_id)
                parent_level = chunk.metadata.get("hierarchy_level", 0)
                child_level = child.metadata.get("hierarchy_level", 0)
                assert child_level >= parent_level

    def test_index_completeness(self, chunker):
        """HIER-5: All chunks accessible via index."""
        text = "# Doc\n\n## Sec1\n\nText\n\n## Sec2\n\nMore"
        result = chunker.chunk_hierarchical(text)

        # All chunks in index
        for chunk in result.chunks:
            chunk_id = chunk.metadata.get("chunk_id")
            assert result.get_chunk(chunk_id) is chunk

        # Index size matches chunk count
        assert len(result._index) == len(result.chunks)

    def test_no_circular_refs(self, chunker):
        """HIER-6: Ancestor path terminates at root."""
        text = "# Doc\n\n## Sec\n\n### Sub\n\nContent"
        result = chunker.chunk_hierarchical(text)

        for chunk in result.chunks:
            ancestors = result.get_ancestors(chunk.metadata["chunk_id"])
            # Max depth check (should terminate)
            assert len(ancestors) < 100
            # Last ancestor is root if ancestors exist
            if ancestors:
                assert ancestors[-1].metadata.get("chunk_id") == result.root_id
