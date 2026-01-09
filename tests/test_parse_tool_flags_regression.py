"""Regression test for parse_tool_flags unpacking error.

This test reproduces the error:
    "Validation error: too many values to unpack (expected 3)"

The error occurred when parse_tool_flags was updated to return 4 values
but calling code expected 3 values.
"""

import pytest

from adapter import MigrationAdapter


class TestParseToolFlagsRegression:
    """Regression tests for parse_tool_flags."""

    def test_parse_tool_flags_returns_four_values(self):
        """parse_tool_flags must return exactly 4 values."""
        adapter = MigrationAdapter()
        result = adapter.parse_tool_flags()

        # Must return exactly 4 values
        assert len(result) == 4, f"Expected 4 values, got {len(result)}"

    def test_parse_tool_flags_unpacking_with_four_variables(self):
        """Unpacking into 4 variables must work."""
        adapter = MigrationAdapter()

        # This is the correct way to unpack
        include_metadata, enable_hierarchy, debug, leaf_only = adapter.parse_tool_flags()

        assert include_metadata is True
        assert enable_hierarchy is False
        assert debug is False
        assert leaf_only is False

    def test_parse_tool_flags_with_leaf_only_parameter(self):
        """leaf_only parameter must be passed through."""
        adapter = MigrationAdapter()

        _, _, _, leaf_only = adapter.parse_tool_flags(leaf_only=True)

        assert leaf_only is True

    def test_tool_invoke_simulation(self):
        """Simulate tool invocation to catch unpacking errors early."""
        # This simulates what happens in markdown_chunk_tool.py
        adapter = MigrationAdapter(leaf_only=False)

        config = adapter.build_chunker_config(
            max_chunk_size=4096,
            chunk_overlap=200,
            strategy="auto",
        )

        # This line caused the error when unpacking into 3 variables
        include_metadata, enable_hierarchy, debug, leaf_only = adapter.parse_tool_flags(
            include_metadata=True,
            enable_hierarchy=False,
            debug=False,
            leaf_only=False,
        )

        # Run chunking to ensure full flow works
        result = adapter.run_chunking(
            input_text="# Test\n\nContent here.",
            config=config,
            include_metadata=include_metadata,
            enable_hierarchy=enable_hierarchy,
            debug=debug,
        )

        assert isinstance(result, list)
        assert len(result) > 0
