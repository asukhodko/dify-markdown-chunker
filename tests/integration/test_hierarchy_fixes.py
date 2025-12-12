"""
Integration tests for hierarchical chunking fixes.

Tests validate fixes from manual_testing/manual-test-report.md:
- Fix #1: Redundant hierarchy layer
- Fix #2: Wrong hierarchy levels
- Fix #3: Wrong parent counts
- Fix #5: Root content duplication
- Fix #7: Missing strategy field
- Fix #8: Sibling chain validation
"""

import pytest

from markdown_chunker_v2 import ChunkConfig, MarkdownChunker


class TestHierarchyFixes:
    """Test fixes for hierarchical chunking issues."""

    @pytest.fixture
    def test_document(self):
        """Test document similar to manual test case."""
        return """https://education.t-systems.ru/sdet-levels/
https://education.t-systems.ru/sdoc-levels/
https://education.t-systems.ru/sde-levels/

# Критерии грейдов SDE

## SDE 12

### Scope
Решает однозначно поставленные задачи.

### Impact
Доставляет свою работу в прод.

## SDE 13

### Scope
Решает четко поставленные задачи.

# Примеры

Некоторые примеры применения критериев.
"""

    @pytest.fixture
    def chunker(self):
        """Create chunker with standard config."""
        return MarkdownChunker(ChunkConfig(max_chunk_size=2000))

    def test_fix_1_root_has_unique_header_path(self, chunker, test_document):
        """
        Fix #1: Root chunk should have header_path='/' not duplicate H1.

        Before: Root had same header_path as first H1 section.
        After: Root has unique path '/'.
        """
        result = chunker.chunk_hierarchical(test_document)
        root = result.get_chunk(result.root_id)

        # Root should have unique path
        assert root.metadata.get("header_path") == "/"

        # First H1 should have different path
        h1_chunks = [c for c in result.chunks if c.metadata.get("header_level") == 1]
        assert len(h1_chunks) > 0
        assert h1_chunks[0].metadata.get("header_path") != "/"

    def test_fix_2_hierarchy_levels_match_tree_depth(self, chunker, test_document):
        """
        Fix #2: hierarchy_level should reflect tree depth not header_level.

        Before: Preamble had hierarchy_level=0 (root level).
        After: Preamble has hierarchy_level=1 (child of root).
        """
        result = chunker.chunk_hierarchical(test_document)

        # Root should be level 0
        root = result.get_chunk(result.root_id)
        assert root.metadata.get("hierarchy_level") == 0

        # Preamble should be level 1 (child of root)
        preamble = next(
            (c for c in result.chunks if c.metadata.get("content_type") == "preamble"),
            None,
        )
        if preamble:
            assert preamble.metadata.get("hierarchy_level") == 1
            assert preamble.metadata.get("parent_id") == result.root_id

        # H1 sections should be level 1 (children of root)
        h1_chunks = [c for c in result.chunks if c.metadata.get("header_level") == 1]
        for h1 in h1_chunks:
            assert h1.metadata.get("hierarchy_level") == 1
            assert h1.metadata.get("parent_id") == result.root_id

        # H2 sections should be level 2 (children of H1)
        h2_chunks = [c for c in result.chunks if c.metadata.get("header_level") == 2]
        for h2 in h2_chunks:
            assert h2.metadata.get("hierarchy_level") == 2

    def test_fix_3_parent_child_counts_match(self, chunker, test_document):
        """
        Fix #3: children_ids count should match actual children.

        Validation ensures declared count equals actual count.
        """
        result = chunker.chunk_hierarchical(test_document)

        # Validation runs during build, if we get here it passed
        for chunk in result.chunks:
            chunk_id = chunk.metadata["chunk_id"]
            declared_count = len(chunk.metadata.get("children_ids", []))

            # Count actual children
            actual_children = [
                c for c in result.chunks if c.metadata.get("parent_id") == chunk_id
            ]

            assert declared_count == len(actual_children), (
                f"Chunk {chunk_id}: declared {declared_count} children, "
                f"has {len(actual_children)}"
            )

    def test_fix_5_root_content_not_duplicate_preamble(self, chunker, test_document):
        """
        Fix #5: Root content should be summary, not preamble duplication.

        Before: Root duplicated preamble URLs.
        After: Root extracts meaningful summary or uses first H1 content.
        """
        result = chunker.chunk_hierarchical(test_document)
        root = result.get_chunk(result.root_id)

        # Root content should not be just URLs
        root_content = root.content

        # Check that root is not just copying preamble URLs
        preamble = next(
            (c for c in result.chunks if c.metadata.get("content_type") == "preamble"),
            None,
        )
        if preamble:
            # Root should not be identical to preamble
            assert root.content != preamble.content

            # Root should have title
            assert "Критерии" in root_content or "Document" in root_content

    def test_fix_7_root_has_strategy_field(self, chunker, test_document):
        """
        Fix #7: Root chunk should have strategy field.

        Before: Root chunk missing 'strategy' field.
        After: Root chunk has strategy='hierarchical'.
        """
        result = chunker.chunk_hierarchical(test_document)
        root = result.get_chunk(result.root_id)

        # Root should have strategy field
        assert "strategy" in root.metadata
        assert root.metadata["strategy"] == "hierarchical"

    def test_fix_8_sibling_chains_valid(self, chunker, test_document):
        """
        Fix #8: Sibling chains should be complete and continuous.

        Validation ensures:
        - First sibling has prev_sibling_id=None
        - Last sibling has next_sibling_id=None
        - Chain is continuous (A.next=B implies B.prev=A)
        - Chain length matches sibling count
        """
        result = chunker.chunk_hierarchical(test_document)

        # Validation runs during build, if we get here chains are valid
        # Additional checks for completeness
        chunk_map = {c.metadata["chunk_id"]: c for c in result.chunks}

        # Group siblings by parent
        parent_groups = {}
        for chunk in result.chunks:
            parent_id = chunk.metadata.get("parent_id")
            if parent_id:
                parent_groups.setdefault(parent_id, []).append(chunk)

        # Verify each group
        for parent_id, siblings in parent_groups.items():
            if len(siblings) <= 1:
                continue

            # Find first sibling
            first_siblings = [
                s for s in siblings if s.metadata.get("prev_sibling_id") is None
            ]
            assert (
                len(first_siblings) == 1
            ), f"Parent {parent_id}: Expected 1 first sibling"

            # Find last sibling
            last_siblings = [
                s for s in siblings if s.metadata.get("next_sibling_id") is None
            ]
            assert (
                len(last_siblings) == 1
            ), f"Parent {parent_id}: Expected 1 last sibling"

            # Traverse chain
            current = first_siblings[0]
            chain_length = 1
            visited = {current.metadata["chunk_id"]}

            while current.metadata.get("next_sibling_id"):
                next_id = current.metadata["next_sibling_id"]
                next_chunk = chunk_map[next_id]

                # Verify backward link
                assert next_chunk.metadata.get("prev_sibling_id") == (
                    current.metadata["chunk_id"]
                ), f"Chain broken at {next_id}"

                # Check for cycles
                assert next_id not in visited, f"Cycle at {next_id}"

                visited.add(next_id)
                current = next_chunk
                chain_length += 1

            # Verify chain length
            assert chain_length == len(
                siblings
            ), f"Chain length {chain_length} != sibling count {len(siblings)}"

    def test_get_by_level_works_correctly(self, chunker, test_document):
        """
        Verify get_by_level() returns correct chunks after Fix #2.

        hierarchy_level now reflects tree depth, so get_by_level should work.
        """
        result = chunker.chunk_hierarchical(test_document)

        # Level 0: Only root
        level_0 = result.get_by_level(0)
        assert len(level_0) == 1
        assert level_0[0].metadata.get("is_root") is True

        # Level 1: Preamble + H1 sections
        level_1 = result.get_by_level(1)
        assert len(level_1) >= 2  # At least preamble and one H1

        # Level 2: H2 sections (if any)
        level_2 = result.get_by_level(2)
        # Should have some H2 sections from the document
        assert len(level_2) > 0

    def test_no_redundant_hierarchy_layer(self, chunker, test_document):
        """
        Verify no duplicate H1 section chunk (Fix #1).

        Before: Both root and first H1 had same header_path.
        After: Root has unique path, H1 is child.
        """
        result = chunker.chunk_hierarchical(test_document)
        root = result.get_chunk(result.root_id)

        # Get first H1
        h1_chunks = [c for c in result.chunks if c.metadata.get("header_level") == 1]
        assert len(h1_chunks) > 0

        first_h1 = h1_chunks[0]

        # Root and H1 should have different paths
        assert root.metadata["header_path"] != first_h1.metadata["header_path"]

        # H1 should be child of root, not duplicate
        assert first_h1.metadata.get("parent_id") == result.root_id

        # H1 should not be in same children_ids as another H1 section
        # (it should be sibling, not duplicate)
        root_children = result.get_children(result.root_id)
        h1_ids = [c.metadata["chunk_id"] for c in h1_chunks]

        # All H1s should be among root's children
        for h1_id in h1_ids:
            assert any(
                c.metadata["chunk_id"] == h1_id for c in root_children
            ), f"H1 {h1_id} not in root's children"


class TestHierarchyValidation:
    """Test validation features added in fixes."""

    def test_validation_can_be_disabled(self):
        """Validation can be disabled for performance."""
        from markdown_chunker_v2.hierarchy import HierarchyBuilder

        builder = HierarchyBuilder(validate_chains=False)
        assert builder.validate_chains is False

    def test_validation_enabled_by_default(self):
        """Validation is enabled by default."""
        from markdown_chunker_v2.hierarchy import HierarchyBuilder

        builder = HierarchyBuilder()
        assert builder.validate_chains is True
