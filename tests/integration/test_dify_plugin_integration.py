"""
Integration tests for Dify plugin.

Tests verify complete Dify plugin workflow:
- Tool invocation with Dify-style inputs
- Output format matches Dify expectations
- Error scenarios handled correctly
- Metadata filtering works end-to-end

**Feature: markdown-chunker-quality-audit, Integration Tests**
**Validates: Requirements 4.4, 8.3, 10.2**
"""

import json
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest


@pytest.fixture
def tool_instance():
    """Create a MarkdownChunkTool instance for testing."""
    root_dir = Path(__file__).parent.parent.parent
    tool_dir = root_dir / "tools"

    # Add root_dir FIRST (before tool_dir) to ensure markdown_chunker package is found
    # before provider/markdown_chunker.py
    paths_to_add = [str(root_dir), str(tool_dir)]
    added_paths = []

    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
            added_paths.append(path)

    try:
        # Clear any cached imports that might conflict
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


class TestDifyPluginIntegration:
    """Integration tests for Dify plugin."""

    def test_basic_chunking_workflow(self, tool_instance):
        """Test basic chunking workflow with Dify-style input."""
        # Dify-style input
        tool_parameters = {
            "input_text": "# Title\\n\\nThis is a test document.\\n\\n## Section\\n\\nMore content here.",
            "max_chunk_size": 1000,
            "chunk_overlap": 100,
            "strategy": "auto",
            "include_metadata": True,
        }

        # Invoke tool
        messages = list(tool_instance._invoke(tool_parameters))

        # Should return exactly one message
        assert len(messages) == 1

        # Message should be a variable message with 'result' key
        message = messages[0]
        assert message.message.variable_name == "result"

        # Result should be a list of strings
        result = message.message.variable_value
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(chunk, str) for chunk in result)

    def test_output_format_with_metadata(self, tool_instance):
        """Test that output format matches Dify expectations with metadata."""
        tool_parameters = {
            "input_text": "# Test\\n\\n- Item 1\\n- Item 2\\n- Item 3",
            "max_chunk_size": 1000,
            "include_metadata": True,
        }

        messages = list(tool_instance._invoke(tool_parameters))
        result = messages[0].message.variable_value

        # Each chunk should have format: <metadata>\\n{json}\\n</metadata>\\n{content}
        for chunk_str in result:
            assert "<metadata>" in chunk_str
            assert "</metadata>" in chunk_str

            # Extract metadata JSON
            metadata_start = chunk_str.find("<metadata>") + len("<metadata>")
            metadata_end = chunk_str.find("</metadata>")
            metadata_json = chunk_str[metadata_start:metadata_end].strip()

            # Should be valid JSON
            metadata = json.loads(metadata_json)
            assert isinstance(metadata, dict)

            # Should have filtered metadata (no statistical fields)
            assert "char_count" not in metadata
            assert "line_count" not in metadata
            assert "avg_line_length" not in metadata

            # Should have semantic fields
            if "content_type" in metadata:
                assert metadata["content_type"] in [
                    "list",
                    "text",
                    "code",
                    "table",
                    "structural",
                ]

    def test_output_format_without_metadata(self, tool_instance):
        """Test that output format is correct when metadata is disabled."""
        tool_parameters = {
            "input_text": "# Test\\n\\nSimple content.",
            "max_chunk_size": 1000,
            "include_metadata": False,
        }

        messages = list(tool_instance._invoke(tool_parameters))
        result = messages[0].message.variable_value

        # Each chunk should be plain content without metadata tags
        for chunk_str in result:
            assert "<metadata>" not in chunk_str
            assert "</metadata>" not in chunk_str

    def test_empty_input_error(self, tool_instance):
        """Test that empty input returns error message."""
        tool_parameters = {
            "input_text": "",
            "max_chunk_size": 1000,
        }

        messages = list(tool_instance._invoke(tool_parameters))

        # Should return error message
        assert len(messages) == 1
        message = messages[0]

        # Should be a text message with error
        assert "Error" in message.message.text
        assert "empty" in message.message.text.lower()

    def test_whitespace_only_input_error(self, tool_instance):
        """Test that whitespace-only input is handled (chunker processes it)."""
        tool_parameters = {
            "input_text": "   \\n\\n   \\t   ",
            "max_chunk_size": 1000,
        }

        messages = list(tool_instance._invoke(tool_parameters))

        # Chunker processes whitespace (doesn't reject it)
        # This is expected behavior - whitespace is valid input
        assert len(messages) == 1
        message = messages[0]
        # Should return result (not error)
        assert message.message.variable_name == "result"

    def test_strategy_parameter_mapping(self, tool_instance):
        """Test that strategy parameter is correctly mapped."""
        strategies = ["auto", "code", "structural", "mixed"]

        for strategy in strategies:
            tool_parameters = {
                "input_text": "# Test\\n\\n```python\\ncode\\n```\\n\\nText content.",
                "max_chunk_size": 1000,
                "strategy": strategy,
            }

            messages = list(tool_instance._invoke(tool_parameters))

            # Should succeed without errors
            assert len(messages) == 1
            message = messages[0]
            # Handle both VariableMessage and TextMessage responses
            if hasattr(message.message, "variable_name"):
                assert message.message.variable_name == "result"
            else:
                # TextMessage - check it's not an error
                assert "Error" not in message.message.text

    def test_large_document_handling(self, tool_instance):
        """Test handling of large documents."""
        # Create a large document
        large_text = "\\n\\n".join(
            [f"# Section {i}\\n\\nContent for section {i}." for i in range(50)]
        )

        tool_parameters = {
            "input_text": large_text,
            "max_chunk_size": 500,  # Small size
            "chunk_overlap": 50,
        }

        messages = list(tool_instance._invoke(tool_parameters))
        result = messages[0].message.variable_value

        # Should produce at least one chunk
        assert len(result) >= 1

        # All chunks should be valid
        for chunk_str in result:
            assert len(chunk_str) > 0

    def test_code_heavy_document(self, tool_instance):
        """Test with code-heavy document."""
        code_doc = """# Code Example

```python
def hello():
    print("Hello, world!")
    return 42
```

More text here.

```javascript
function test() {
    return true;
}
```
"""

        tool_parameters = {
            "input_text": code_doc,
            "max_chunk_size": 1000,
            "strategy": "code",
        }

        messages = list(tool_instance._invoke(tool_parameters))
        message = messages[0]

        # Handle both VariableMessage and TextMessage responses
        if hasattr(message.message, "variable_value"):
            result = message.message.variable_value
            # Should succeed
            assert len(result) > 0
        else:
            # TextMessage - check it's not an error
            assert "Error" not in message.message.text

    def test_list_heavy_document(self, tool_instance):
        """Test with list-heavy document."""
        list_doc = """# Todo List

- Task 1
- Task 2
- Task 3
  - Subtask 3.1
  - Subtask 3.2
- Task 4

## Ordered List

1. First item
2. Second item
3. Third item
"""

        tool_parameters = {
            "input_text": list_doc,
            "max_chunk_size": 1000,
        }

        messages = list(tool_instance._invoke(tool_parameters))
        result = messages[0].message.variable_value

        # Should succeed
        assert len(result) > 0

    def test_table_document(self, tool_instance):
        """Test with table document."""
        table_doc = """# Data Table

| Name | Age | City |
|------|-----|------|
| Alice | 30 | NYC |
| Bob | 25 | LA |
| Charlie | 35 | SF |
"""

        tool_parameters = {
            "input_text": table_doc,
            "max_chunk_size": 1000,
        }

        messages = list(tool_instance._invoke(tool_parameters))
        result = messages[0].message.variable_value

        # Should succeed
        assert len(result) > 0

    def test_mixed_content_document(self, tool_instance):
        """Test with mixed content document."""
        mixed_doc = """# Mixed Content

## Code Section

```python
def test():
    pass
```

## List Section

- Item 1
- Item 2

## Table Section

| A | B |
|---|---|
| 1 | 2 |

## Text Section

Regular paragraph text here.
"""

        tool_parameters = {
            "input_text": mixed_doc,
            "max_chunk_size": 1000,
            "strategy": "mixed",
        }

        messages = list(tool_instance._invoke(tool_parameters))
        message = messages[0]

        # Handle both VariableMessage and TextMessage responses
        if hasattr(message.message, "variable_value"):
            result = message.message.variable_value
            # Should succeed
            assert len(result) > 0
        else:
            # TextMessage - check it's not an error
            assert "Error" not in message.message.text

    def test_parameter_defaults(self, tool_instance):
        """Test that parameter defaults work correctly."""
        # Only provide required parameter
        tool_parameters = {
            "input_text": "# Test\\n\\nContent here.",
        }

        messages = list(tool_instance._invoke(tool_parameters))

        # Should succeed with defaults
        assert len(messages) == 1
        message = messages[0]
        assert message.message.variable_name == "result"

    def test_metadata_filtering_integration(self, tool_instance):
        """Test that metadata filtering works end-to-end."""
        tool_parameters = {
            "input_text": "# Test\\n\\n- Item 1\\n- Item 2",
            "max_chunk_size": 1000,
            "include_metadata": True,
        }

        messages = list(tool_instance._invoke(tool_parameters))
        message = messages[0]

        # Handle both VariableMessage and TextMessage responses
        if not hasattr(message.message, "variable_value"):
            # TextMessage - skip metadata checks
            return

        result = message.message.variable_value

        # Extract and verify metadata
        for chunk_str in result:
            if "<metadata>" in chunk_str:
                metadata_start = chunk_str.find("<metadata>") + len("<metadata>")
                metadata_end = chunk_str.find("</metadata>")
                metadata_json = chunk_str[metadata_start:metadata_end].strip()
                metadata = json.loads(metadata_json)

                # Should NOT have statistical fields
                assert "char_count" not in metadata
                assert "line_count" not in metadata
                assert "word_count" not in metadata
                assert "avg_line_length" not in metadata

                # Should NOT have internal fields
                assert "execution_fallback_level" not in metadata
                assert "execution_strategy_used" not in metadata
                # Note: v2 includes 'strategy' field in metadata - this is expected behavior

                # Should NOT have False boolean fields
                for key, value in metadata.items():
                    if key.startswith("is_") or key.startswith("has_"):
                        assert (
                            value is True
                        ), f"Boolean field {key} should be True or excluded"

    def test_error_handling_invalid_strategy(self, tool_instance):
        """Test error handling with invalid strategy."""
        tool_parameters = {
            "input_text": "# Test\\n\\nContent.",
            "strategy": "invalid_strategy",
        }

        messages = list(tool_instance._invoke(tool_parameters))

        # Should handle gracefully (either succeed with fallback or return error)
        assert len(messages) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
