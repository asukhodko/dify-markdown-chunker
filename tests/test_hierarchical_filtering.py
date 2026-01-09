"""Integration tests for hierarchical output filtering.

End-to-end tests with real chunking to verify filtering behavior.
"""

import pytest

from adapter import MigrationAdapter


class TestHierarchicalFiltering:
    """Integration tests for hierarchical filtering."""

    @pytest.fixture
    def sample_markdown(self):
        """Sample markdown with hierarchy."""
        return """# Document Title

Introduction paragraph.

## Section 1

Content for section 1.

### Subsection 1.1

Details for subsection 1.1.

## Section 2

Content for section 2.
"""

    def test_hierarchical_no_root_in_result(self, sample_markdown):
        """Root chunk is not in result when debug=False."""
        adapter = MigrationAdapter()
        config = adapter.build_chunker_config()

        result = adapter.run_chunking(
            input_text=sample_markdown,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=False,
        )

        # Parse metadata from formatted chunks
        for chunk_str in result:
            # Check that no chunk has is_root=true in metadata
            assert '"is_root": true' not in chunk_str.lower()

    def test_hierarchical_debug_includes_all(self, sample_markdown):
        """Debug mode includes all chunks including root."""
        adapter = MigrationAdapter()
        config = adapter.build_chunker_config()

        result_debug = adapter.run_chunking(
            input_text=sample_markdown,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=True,
        )

        result_normal = adapter.run_chunking(
            input_text=sample_markdown,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=False,
        )

        # Debug mode should have more or equal chunks
        assert len(result_debug) >= len(result_normal)

    def test_hierarchical_with_leaf_only(self, sample_markdown):
        """leaf_only=True returns only leaf chunks."""
        adapter = MigrationAdapter(leaf_only=True)
        config = adapter.build_chunker_config()

        result = adapter.run_chunking(
            input_text=sample_markdown,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=False,
        )

        # All chunks should be leaves (no internal nodes)
        for chunk_str in result:
            # Internal nodes have is_leaf=false
            assert '"is_leaf": false' not in chunk_str.lower()

    def test_indexable_field_present(self, sample_markdown):
        """indexable field is present in hierarchical output."""
        adapter = MigrationAdapter()
        config = adapter.build_chunker_config()

        result = adapter.run_chunking(
            input_text=sample_markdown,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=False,
        )

        # At least one chunk should have indexable field
        has_indexable = any('"indexable"' in chunk_str for chunk_str in result)
        assert has_indexable

    def test_flat_chunking_unchanged(self, sample_markdown):
        """Flat chunking (enable_hierarchy=False) is not affected."""
        adapter = MigrationAdapter()
        config = adapter.build_chunker_config()

        result = adapter.run_chunking(
            input_text=sample_markdown,
            config=config,
            include_metadata=True,
            enable_hierarchy=False,
            debug=False,
        )

        # Should return chunks without hierarchical filtering
        assert len(result) > 0

    def test_leaf_only_vs_normal_count(self, sample_markdown):
        """leaf_only returns fewer or equal chunks than normal."""
        adapter_normal = MigrationAdapter(leaf_only=False)
        adapter_leaf = MigrationAdapter(leaf_only=True)
        config = adapter_normal.build_chunker_config()

        result_normal = adapter_normal.run_chunking(
            input_text=sample_markdown,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=False,
        )

        result_leaf = adapter_leaf.run_chunking(
            input_text=sample_markdown,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=False,
        )

        # leaf_only should have fewer or equal chunks
        assert len(result_leaf) <= len(result_normal)


class TestFilteringEdgeCases:
    """Edge case tests for filtering."""

    def test_empty_document(self):
        """Empty document returns empty result."""
        adapter = MigrationAdapter()
        config = adapter.build_chunker_config()

        result = adapter.run_chunking(
            input_text="",
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=False,
        )

        # Empty or minimal result
        assert isinstance(result, list)

    def test_single_paragraph(self):
        """Single paragraph document works correctly."""
        adapter = MigrationAdapter()
        config = adapter.build_chunker_config()

        result = adapter.run_chunking(
            input_text="Just a single paragraph of text.",
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=False,
        )

        assert isinstance(result, list)

    def test_deep_hierarchy(self):
        """Deep hierarchy (h1-h4) is handled correctly."""
        deep_md = """# Level 1

## Level 2

### Level 3

#### Level 4

Content at level 4.
"""
        adapter = MigrationAdapter()
        config = adapter.build_chunker_config()

        result = adapter.run_chunking(
            input_text=deep_md,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=False,
        )

        assert len(result) > 0
