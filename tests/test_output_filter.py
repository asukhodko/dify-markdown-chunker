"""Unit tests for OutputFilter component.

Tests filtering behavior for hierarchical chunking output.
"""

import pytest

from output_filter import FilterConfig, OutputFilter


class TestOutputFilter:
    """Tests for OutputFilter class."""

    def test_root_excluded_in_production(self):
        """Root chunk is excluded when debug=False."""
        chunks = [
            {"content": "root", "metadata": {"is_root": True, "is_leaf": False}},
            {"content": "leaf1", "metadata": {"is_root": False, "is_leaf": True}},
        ]

        filter_obj = OutputFilter(FilterConfig())
        result = filter_obj.filter(chunks, debug=False)

        assert len(result) == 1
        assert result[0]["content"] == "leaf1"

    def test_root_included_in_debug(self):
        """Root chunk is included when debug=True."""
        chunks = [
            {"content": "root", "metadata": {"is_root": True, "is_leaf": False}},
            {"content": "leaf1", "metadata": {"is_root": False, "is_leaf": True}},
        ]

        filter_obj = OutputFilter(FilterConfig())
        result = filter_obj.filter(chunks, debug=True)

        assert len(result) == 2

    def test_leaf_only_filter(self):
        """Only leaf chunks returned when leaf_only=True."""
        chunks = [
            {"content": "internal", "metadata": {"is_root": False, "is_leaf": False}},
            {"content": "leaf1", "metadata": {"is_root": False, "is_leaf": True}},
            {"content": "leaf2", "metadata": {"is_root": False, "is_leaf": True}},
        ]

        filter_obj = OutputFilter(FilterConfig(leaf_only=True))
        result = filter_obj.filter(chunks, debug=False)

        assert len(result) == 2
        assert all(c["metadata"]["is_leaf"] for c in result)

    def test_leaf_only_excludes_root_and_internal(self):
        """leaf_only=True excludes both root and internal nodes."""
        chunks = [
            {"content": "root", "metadata": {"is_root": True, "is_leaf": False}},
            {"content": "internal", "metadata": {"is_root": False, "is_leaf": False}},
            {"content": "leaf", "metadata": {"is_root": False, "is_leaf": True}},
        ]

        filter_obj = OutputFilter(FilterConfig(leaf_only=True))
        result = filter_obj.filter(chunks, debug=False)

        assert len(result) == 1
        assert result[0]["content"] == "leaf"

    def test_indexable_field_added_to_all_chunks(self):
        """indexable field is added to all chunks."""
        chunks = [
            {"content": "root", "metadata": {"is_root": True}},
            {"content": "leaf", "metadata": {"is_root": False}},
        ]

        filter_obj = OutputFilter(FilterConfig())
        result = filter_obj.filter(chunks, debug=True)

        assert "indexable" in result[0]["metadata"]
        assert "indexable" in result[1]["metadata"]

    def test_indexable_false_for_root(self):
        """Root chunk has indexable=False."""
        chunks = [
            {"content": "root", "metadata": {"is_root": True}},
        ]

        filter_obj = OutputFilter(FilterConfig())
        result = filter_obj.filter(chunks, debug=True)

        assert result[0]["metadata"]["indexable"] is False

    def test_indexable_true_for_leaf(self):
        """Leaf chunks have indexable=True."""
        chunks = [
            {"content": "leaf", "metadata": {"is_root": False, "is_leaf": True}},
        ]

        filter_obj = OutputFilter(FilterConfig())
        result = filter_obj.filter(chunks, debug=True)

        assert result[0]["metadata"]["indexable"] is True

    def test_indexable_for_non_leaf_depends_on_content(self):
        """Non-leaf chunks have indexable based on significant content."""
        # Short content (< 100 chars) -> indexable=False
        chunks_short = [
            {"content": "internal", "metadata": {"is_root": False, "is_leaf": False}},
        ]

        filter_obj = OutputFilter(FilterConfig())
        result_short = filter_obj.filter(chunks_short, debug=True)
        assert result_short[0]["metadata"]["indexable"] is False

        # Long content (> 100 chars) -> indexable=True
        long_content = "This is a non-leaf chunk with significant content. " * 5
        chunks_long = [
            {"content": long_content, "metadata": {"is_root": False, "is_leaf": False}},
        ]

        result_long = filter_obj.filter(chunks_long, debug=True)
        assert result_long[0]["metadata"]["indexable"] is True

    def test_empty_chunks_list(self):
        """Empty list returns empty list."""
        filter_obj = OutputFilter(FilterConfig())
        result = filter_obj.filter([], debug=False)

        assert result == []

    def test_metadata_preservation(self):
        """Original metadata fields are preserved."""
        chunks = [
            {
                "content": "leaf",
                "metadata": {
                    "is_root": False,
                    "is_leaf": True,
                    "header_path": "/Section/Subsection",
                    "content_type": "text",
                },
            },
        ]

        filter_obj = OutputFilter(FilterConfig())
        result = filter_obj.filter(chunks, debug=False)

        assert result[0]["metadata"]["header_path"] == "/Section/Subsection"
        assert result[0]["metadata"]["content_type"] == "text"

    def test_default_config(self):
        """Default config has leaf_only=False."""
        filter_obj = OutputFilter()
        assert filter_obj.config.leaf_only is False
        assert filter_obj.config.add_indexable is True

    def test_missing_is_root_treated_as_false(self):
        """Chunk without is_root is not filtered as root."""
        chunks = [
            {"content": "chunk", "metadata": {"is_leaf": True}},
        ]

        filter_obj = OutputFilter(FilterConfig())
        result = filter_obj.filter(chunks, debug=False)

        assert len(result) == 1

    def test_missing_is_leaf_treated_as_true_for_leaf_only(self):
        """Chunk without is_leaf passes leaf_only filter (default True)."""
        chunks = [
            {"content": "chunk", "metadata": {"is_root": False}},
        ]

        filter_obj = OutputFilter(FilterConfig(leaf_only=True))
        result = filter_obj.filter(chunks, debug=False)

        assert len(result) == 1
