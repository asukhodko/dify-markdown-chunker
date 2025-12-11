"""Integration tests for Dify plugin hierarchical chunking mode.

This module tests the integration of hierarchical chunking into the Dify plugin
to ensure the enable_hierarchy parameter works correctly end-to-end.
"""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest


class TestDifyHierarchicalIntegration:
    """Test hierarchical chunking integration with Dify plugin."""

    @pytest.fixture
    def tool(self):
        """Create MarkdownChunkTool instance."""
        root_dir = Path(__file__).parent.parent.parent
        tool_dir = root_dir / "tools"

        # Add root_dir FIRST to ensure markdown_chunker package is found
        paths_to_add = [str(root_dir), str(tool_dir)]
        added_paths = []

        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)
                added_paths.append(path)

        try:
            # Clear any cached imports
            modules_to_clear = [k for k in sys.modules.keys() if "markdown_chunker" in k]
            for mod in modules_to_clear:
                del sys.modules[mod]

            from markdown_chunk_tool import MarkdownChunkTool

            # Create mock runtime and session
            runtime = Mock()
            session = Mock()

            tool = MarkdownChunkTool(runtime=runtime, session=session)
            yield tool
        finally:
            for path in added_paths:
                if path in sys.path:
                    sys.path.remove(path)

    @pytest.fixture
    def sample_markdown(self):
        """Sample markdown with hierarchical structure."""
        return """# Document Title

Introduction text.

## Section 1

Section 1 content.

### Subsection 1.1

Subsection 1.1 content.

## Section 2

Section 2 content.

### Subsection 2.1

Subsection 2.1 content.
"""

    def test_hierarchical_mode_disabled_by_default(self, tool, sample_markdown):
        """Test that hierarchical mode is disabled by default."""
        params = {
            "input_text": sample_markdown,
            "max_chunk_size": 4096,
        }

        messages = list(tool._invoke(params))
        assert len(messages) == 1

        # Should return variable message with chunks
        msg = messages[0]
        assert msg.message.variable_name == "result"

        # Verify chunks don't have hierarchical metadata (parent_id, children_ids)
        # when hierarchy is disabled
        result = msg.message.variable_value
        assert len(result) > 0

        # With metadata enabled (default), check one chunk's metadata
        chunk_text = result[0]
        # Flat chunking should not include parent_id or children_ids in metadata
        assert "parent_id" not in chunk_text or '"parent_id": null' in chunk_text

    def test_hierarchical_mode_enabled(self, tool, sample_markdown):
        """Test that hierarchical mode creates hierarchy metadata."""
        params = {
            "input_text": sample_markdown,
            "max_chunk_size": 4096,
            "enable_hierarchy": True,
            "include_metadata": True,
        }

        messages = list(tool._invoke(params))
        assert len(messages) == 1

        msg = messages[0]
        assert msg.message.variable_name == "result"

        result = msg.message.variable_value
        assert len(result) > 0

        # At least one chunk should have hierarchy metadata
        has_hierarchy_metadata = False
        for chunk_text in result:
            if '"parent_id"' in chunk_text or '"children_ids"' in chunk_text:
                has_hierarchy_metadata = True
                break

        assert has_hierarchy_metadata, "No hierarchy metadata found in chunks"

    def test_hierarchical_mode_returns_leaf_chunks(self, tool, sample_markdown):
        """Test that hierarchical mode returns leaf chunks (not root/intermediate)."""
        params = {
            "input_text": sample_markdown,
            "max_chunk_size": 200,  # Small size to force multiple chunks
            "enable_hierarchy": True,
            "include_metadata": True,
        }

        messages = list(tool._invoke(params))
        msg = messages[0]

        # Handle both variable and text messages
        if hasattr(msg.message, 'variable_value'):
            result = msg.message.variable_value

            # Should have chunks
            assert len(result) >= 1

            # All returned chunks should be leaf chunks (is_leaf: true)
            for chunk_text in result:
                if '"is_leaf"' in chunk_text:
                    # If is_leaf is present, it should be true for all chunks
                    assert '"is_leaf": true' in chunk_text
        else:
            # Text message - check not an error
            assert "Error" not in msg.message.text

    def test_hierarchical_mode_with_metadata_disabled(self, tool, sample_markdown):
        """Test hierarchical mode with metadata disabled."""
        params = {
            "input_text": sample_markdown,
            "max_chunk_size": 4096,
            "enable_hierarchy": True,
            "include_metadata": False,
        }

        messages = list(tool._invoke(params))
        result = messages[0].message.variable_value

        # Should return clean chunks without metadata blocks
        assert len(result) > 0
        for chunk_text in result:
            assert "<metadata>" not in chunk_text

    def test_hierarchical_mode_preserves_content(self, tool, sample_markdown):
        """Test that hierarchical mode doesn't lose content."""
        # Run with hierarchy enabled
        params_hier = {
            "input_text": sample_markdown,
            "max_chunk_size": 4096,
            "enable_hierarchy": True,
            "include_metadata": False,
        }
        messages_hier = list(tool._invoke(params_hier))
        result_hier = messages_hier[0].message.variable_value

        # Hierarchical mode returns only leaf chunks
        # Check combined content includes key sections
        hier_content = "".join(result_hier)

        # Both should contain original content
        assert len(hier_content) > 0
        # Check that leaf content is preserved
        assert "Subsection 1.1" in hier_content
        assert "Section 2" in hier_content
        assert "Subsection 2.1" in hier_content

    def test_hierarchical_mode_with_different_strategies(self, tool):
        """Test hierarchical mode works with different chunking strategies."""
        markdown_with_code = """# Title

Text before code.

```python
def hello():
    print("world")
```

Text after code.
"""

        for strategy in ["auto", "code_aware", "structural", "fallback"]:
            params = {
                "input_text": markdown_with_code,
                "max_chunk_size": 4096,
                "strategy": strategy,
                "enable_hierarchy": True,
            }

            messages = list(tool._invoke(params))
            result = messages[0].message.variable_value

            # Should return chunks regardless of strategy
            assert len(result) > 0, f"Strategy {strategy} failed with hierarchy"

    def test_hierarchical_mode_empty_document(self, tool):
        """Test hierarchical mode with empty document."""
        params = {
            "input_text": "   ",
            "max_chunk_size": 4096,
            "enable_hierarchy": True,
        }

        messages = list(tool._invoke(params))

        # Should return error message
        msg = messages[0]
        assert "Error" in msg.message.text

    def test_hierarchical_mode_with_overlap(self, tool, sample_markdown):
        """Test hierarchical mode with chunk overlap enabled."""
        params = {
            "input_text": sample_markdown,
            "max_chunk_size": 200,
            "chunk_overlap": 50,
            "enable_hierarchy": True,
            "include_metadata": True,
        }

        messages = list(tool._invoke(params))
        result = messages[0].message.variable_value

        # Should have at least one chunk
        assert len(result) >= 1

        # If there are multiple chunks, check overlap metadata exists
        if len(result) > 1:
            has_overlap = False
            for chunk_text in result:
                if '"previous_content"' in chunk_text or '"next_content"' in chunk_text:
                    has_overlap = True
                    break

            assert has_overlap, "No overlap metadata found"

    def test_debug_mode_includes_all_chunks(self, tool, sample_markdown):
        """Test that debug mode includes root and intermediate chunks."""
        # First, test without debug (default)
        params_normal = {
            "input_text": sample_markdown,
            "max_chunk_size": 4096,
            "enable_hierarchy": True,
            "include_metadata": True,
            "debug": False,
        }
        messages_normal = list(tool._invoke(params_normal))
        result_normal = messages_normal[0].message.variable_value

        # Count chunks with is_leaf: false (should be 0)
        non_leaf_normal = sum(
            1 for chunk in result_normal
            if '"is_leaf": false' in chunk
        )
        assert non_leaf_normal == 0, "Normal mode should not include non-leaf chunks"

        # Now test with debug enabled
        params_debug = {
            "input_text": sample_markdown,
            "max_chunk_size": 4096,
            "enable_hierarchy": True,
            "include_metadata": True,
            "debug": True,
        }
        messages_debug = list(tool._invoke(params_debug))
        result_debug = messages_debug[0].message.variable_value

        # Debug mode should have MORE chunks (includes root and intermediate)
        assert len(result_debug) > len(result_normal), (
            f"Debug mode should have more chunks. "
            f"Normal: {len(result_normal)}, Debug: {len(result_debug)}"
        )

        # Count chunks with is_leaf: false (should be > 0)
        non_leaf_debug = sum(
            1 for chunk in result_debug
            if '"is_leaf": false' in chunk
        )
        assert non_leaf_debug > 0, "Debug mode should include non-leaf chunks"

        # Should have exactly one root chunk
        root_chunks = sum(
            1 for chunk in result_debug
            if '"is_root": true' in chunk
        )
        assert root_chunks == 1, f"Should have exactly 1 root chunk, got {root_chunks}"

        # Root chunk should have no parent
        has_root_with_no_parent = any(
            '"is_root": true' in chunk and '"parent_id": null' in chunk
            for chunk in result_debug
        )
        assert has_root_with_no_parent, "Root chunk should have parent_id: null"

    def test_debug_mode_without_hierarchy(self, tool, sample_markdown):
        """Test that debug mode without hierarchy has no effect."""
        # Debug without hierarchy should behave same as normal mode
        params = {
            "input_text": sample_markdown,
            "max_chunk_size": 4096,
            "enable_hierarchy": False,
            "debug": True,
        }

        messages = list(tool._invoke(params))
        result = messages[0].message.variable_value

        # Should not have hierarchical metadata
        assert len(result) > 0
        for chunk in result:
            # Flat chunking doesn't have is_leaf field
            assert '"is_leaf"' not in chunk or '"is_leaf": true' in chunk


class TestDifyHierarchicalEdgeCases:
    """Test edge cases for hierarchical mode integration."""

    @pytest.fixture
    def tool(self):
        """Create MarkdownChunkTool instance."""
        root_dir = Path(__file__).parent.parent.parent
        tool_dir = root_dir / "tools"

        # Add root_dir FIRST to ensure markdown_chunker package is found
        paths_to_add = [str(root_dir), str(tool_dir)]
        added_paths = []

        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)
                added_paths.append(path)

        try:
            # Clear any cached imports
            modules_to_clear = [k for k in sys.modules.keys() if "markdown_chunker" in k]
            for mod in modules_to_clear:
                del sys.modules[mod]

            from markdown_chunk_tool import MarkdownChunkTool

            # Create mock runtime and session
            runtime = Mock()
            session = Mock()

            tool = MarkdownChunkTool(runtime=runtime, session=session)
            yield tool
        finally:
            for path in added_paths:
                if path in sys.path:
                    sys.path.remove(path)

    def test_hierarchical_mode_single_section(self, tool):
        """Test hierarchical mode with single section document."""
        markdown = """# Single Section

Just one paragraph of text here.
"""

        params = {
            "input_text": markdown,
            "max_chunk_size": 4096,
            "enable_hierarchy": True,
        }

        messages = list(tool._invoke(params))
        result = messages[0].message.variable_value

        # Should return chunks
        assert len(result) > 0

    def test_hierarchical_mode_no_headers(self, tool):
        """Test hierarchical mode with document without headers."""
        markdown = """Just some plain text without any headers.

Another paragraph.

And one more.
"""

        params = {
            "input_text": markdown,
            "max_chunk_size": 4096,
            "enable_hierarchy": True,
        }

        messages = list(tool._invoke(params))
        result = messages[0].message.variable_value

        # Should still work and return chunks
        assert len(result) > 0

    def test_hierarchical_mode_deep_nesting(self, tool):
        """Test hierarchical mode with deeply nested headers."""
        markdown = """# Level 1

## Level 2

### Level 3

#### Level 4

##### Level 5

###### Level 6

Content at deepest level.
"""

        params = {
            "input_text": markdown,
            "max_chunk_size": 4096,
            "enable_hierarchy": True,
        }

        messages = list(tool._invoke(params))
        result = messages[0].message.variable_value

        # Should handle deep nesting
        assert len(result) > 0
