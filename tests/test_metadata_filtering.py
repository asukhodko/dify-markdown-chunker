"""Unit Tests: Metadata Filtering

Tests that metadata filtering works correctly:
- Excludes statistical fields
- Excludes internal fields
- Includes only is_*/has_* fields with True values
- Keeps RAG-useful fields
"""

import sys
from pathlib import Path

import pytest


class TestMetadataFiltering:
    """Test metadata filtering for RAG optimization."""

    @pytest.fixture
    def tool_class(self):
        """Import the tool class."""
        root_dir = Path(__file__).parent.parent
        tool_dir = root_dir / "tools"

        paths_to_add = [str(root_dir), str(tool_dir)]
        added_paths = []

        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)
                added_paths.append(path)

        try:
            from markdown_chunk_tool import MarkdownChunkTool

            return MarkdownChunkTool
        finally:
            for path in added_paths:
                if path in sys.path:
                    sys.path.remove(path)

    def test_filter_excludes_statistical_fields(self, tool_class):
        """Test that statistical fields are excluded."""
        from unittest.mock import Mock

        tool = tool_class(runtime=Mock(), session=Mock())

        metadata = {
            "content_type": "list",
            "avg_line_length": 50,
            "avg_word_length": 5.5,
            "char_count": 100,
            "line_count": 10,
            "size_bytes": 100,
            "word_count": 20,
        }

        filtered = tool._filter_metadata_for_rag(metadata)

        # Should keep content_type
        assert "content_type" in filtered

        # Should exclude statistical fields
        assert "avg_line_length" not in filtered
        assert "avg_word_length" not in filtered
        assert "char_count" not in filtered
        assert "line_count" not in filtered
        assert "size_bytes" not in filtered
        assert "word_count" not in filtered

    def test_filter_excludes_count_fields(self, tool_class):
        """Test that count fields are excluded."""
        from unittest.mock import Mock

        tool = tool_class(runtime=Mock(), session=Mock())

        metadata = {
            "content_type": "list",
            "item_count": 5,
            "nested_item_count": 2,
            "unordered_item_count": 3,
            "ordered_item_count": 2,
            "max_nesting": 2,
            "task_item_count": 1,
        }

        filtered = tool._filter_metadata_for_rag(metadata)

        # Should exclude count fields
        assert "item_count" not in filtered
        assert "nested_item_count" not in filtered
        assert "unordered_item_count" not in filtered
        assert "ordered_item_count" not in filtered
        assert "max_nesting" not in filtered
        assert "task_item_count" not in filtered

    def test_filter_excludes_internal_fields(self, tool_class):
        """Test that internal execution fields are excluded."""
        from unittest.mock import Mock

        tool = tool_class(runtime=Mock(), session=Mock())

        metadata = {
            "content_type": "list",
            "execution_fallback_level": 0,
            "execution_fallback_used": False,
            "execution_strategy_used": "list",
            "strategy": "list",
            "total_chunks": 10,
            "preview": "Some text...",
        }

        filtered = tool._filter_metadata_for_rag(metadata)

        # Should exclude internal fields
        assert "execution_fallback_level" not in filtered
        assert "execution_fallback_used" not in filtered
        assert "execution_strategy_used" not in filtered
        assert "strategy" not in filtered
        assert "total_chunks" not in filtered
        assert "preview" not in filtered

    def test_filter_includes_only_true_boolean_fields(self, tool_class):
        """Test that is_*/has_* fields are included only when True."""
        from unittest.mock import Mock

        tool = tool_class(runtime=Mock(), session=Mock())

        metadata = {
            "content_type": "list",
            "is_first_chunk": True,
            "is_last_chunk": False,
            "is_continuation": False,
            "has_urls": True,
            "has_emails": False,
            "has_bold": False,
            "has_italic": True,
            "has_nested_lists": True,
            "has_overlap": False,
        }

        filtered = tool._filter_metadata_for_rag(metadata)

        # Should include True values
        assert filtered["is_first_chunk"] is True
        assert filtered["has_urls"] is True
        assert filtered["has_italic"] is True
        assert filtered["has_nested_lists"] is True

        # Should exclude False values
        assert "is_last_chunk" not in filtered
        assert "is_continuation" not in filtered
        assert "has_emails" not in filtered
        assert "has_bold" not in filtered
        assert "has_overlap" not in filtered

    def test_filter_keeps_semantic_fields(self, tool_class):
        """Test that semantic fields useful for RAG are kept."""
        from unittest.mock import Mock

        tool = tool_class(runtime=Mock(), session=Mock())

        metadata = {
            "content_type": "list",
            "list_type": "ordered",
            "chunk_index": 5,
            "overlap_type": "prefix",
            "overlap_size": 100,
            "start_number": 1,
            "language": "python",
        }

        filtered = tool._filter_metadata_for_rag(metadata)

        # Should keep all semantic fields
        assert filtered["content_type"] == "list"
        assert filtered["list_type"] == "ordered"
        assert filtered["chunk_index"] == 5
        # Note: overlap_type and overlap_size are legacy fields removed in overlap redesign
        # They should not be present in new implementation
        assert "overlap_type" not in filtered  # Legacy field removed
        assert "overlap_size" not in filtered  # Legacy field removed
        assert filtered["start_number"] == 1
        assert filtered["language"] == "python"

    def test_filter_handles_preamble(self, tool_class):
        """Test that preamble is filtered to keep only content."""
        from unittest.mock import Mock

        tool = tool_class(runtime=Mock(), session=Mock())

        metadata = {
            "content_type": "list",
            "preamble": {
                "content": "This is preamble text",
                "char_count": 100,
                "line_count": 5,
                "has_metadata": False,
                "metadata_fields": {},
                "type": "general",
            },
        }

        filtered = tool._filter_metadata_for_rag(metadata)

        # Should keep preamble with only content
        assert "preamble" in filtered
        assert "content" in filtered["preamble"]
        assert filtered["preamble"]["content"] == "This is preamble text"

        # Should not include internal preamble fields
        assert "char_count" not in filtered["preamble"]
        assert "line_count" not in filtered["preamble"]
        assert "has_metadata" not in filtered["preamble"]

    def test_filter_realistic_example(self, tool_class):
        """Test with realistic metadata from actual chunking."""
        from unittest.mock import Mock

        tool = tool_class(runtime=Mock(), session=Mock())

        # Realistic metadata from your example (updated for overlap redesign)
        metadata = {
            "content_type": "list",
            "list_type": "ordered",
            "has_nested_items": True,
            "is_continuation": False,
            "start_number": 8,
            # Legacy overlap fields removed in redesign:
            # "has_overlap": True,
            # "overlap_size": 73,
            # "overlap_type": "prefix",
            # New overlap fields (if present):
            "previous_content": "Some context from previous chunk",
            "next_content": "Some context from next chunk",
            "chunk_index": 42,
            "is_first_chunk": False,
            "is_last_chunk": True,
            "has_nested_lists": True,
            "has_urls": False,
            "has_emails": False,
            "has_numbers": True,
            "has_bold": False,
            "has_italic": False,
            "has_inline_code": False,
            # Fields that should be excluded
            "char_count": 200,
            "line_count": 10,
            "word_count": 50,
            "item_count": 3,
        }

        filtered = tool._filter_metadata_for_rag(metadata)

        # Should keep semantic fields
        assert filtered["content_type"] == "list"
        assert filtered["list_type"] == "ordered"
        assert filtered["start_number"] == 8
        # New overlap fields should be kept
        assert filtered["previous_content"] == "Some context from previous chunk"
        assert filtered["next_content"] == "Some context from next chunk"
        assert filtered["chunk_index"] == 42

        # Should keep only True boolean fields
        assert filtered["has_nested_items"] is True
        # Note: has_overlap is a legacy field, no longer used
        assert filtered["is_last_chunk"] is True
        assert filtered["has_nested_lists"] is True
        assert filtered["has_numbers"] is True

        # Should exclude False boolean fields
        assert "is_continuation" not in filtered
        assert "is_first_chunk" not in filtered
        assert "has_urls" not in filtered
        assert "has_emails" not in filtered
        assert "has_bold" not in filtered
        assert "has_italic" not in filtered
        assert "has_inline_code" not in filtered

        # Should exclude statistical fields
        assert "char_count" not in filtered
        assert "line_count" not in filtered
        assert "word_count" not in filtered
        assert "item_count" not in filtered

    def test_filter_empty_metadata(self, tool_class):
        """Test that empty metadata is handled correctly."""
        from unittest.mock import Mock

        tool = tool_class(runtime=Mock(), session=Mock())

        metadata = {}
        filtered = tool._filter_metadata_for_rag(metadata)

        assert filtered == {}

    def test_filter_preserves_non_boolean_values(self, tool_class):
        """Test that non-boolean values are preserved regardless of value."""
        from unittest.mock import Mock

        tool = tool_class(runtime=Mock(), session=Mock())

        metadata = {
            "content_type": "text",
            "chunk_index": 0,
            "depth": 0,  # Zero should be kept
            "start_number": 1,
            "language": None,  # None should be kept
        }

        filtered = tool._filter_metadata_for_rag(metadata)

        # All non-boolean fields should be kept
        assert filtered["content_type"] == "text"
        assert filtered["chunk_index"] == 0
        assert filtered["depth"] == 0
        assert filtered["start_number"] == 1
        assert filtered["language"] is None
