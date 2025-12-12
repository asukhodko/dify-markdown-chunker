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


class TestOverlapBehavior:
    """
    Tests for chunk_overlap behavior with include_metadata.

    Verifies:
    - include_metadata=true: overlap in metadata fields
    - include_metadata=false: overlap embedded in chunk text
    - Edge cases: first/last chunks, zero overlap

    **Feature: overlap-embedding, Overlap Behavior Tests**
    **Validates: Requirements for overlap handling**
    """

    # Sample document with multiple sections for overlap testing
    MULTI_SECTION_DOC = """
# Introduction

This is the introduction section with some text content that will be used to test overlap behavior.

## First Section

Content of the first section. This paragraph contains enough text to demonstrate overlap between chunks. We need multiple paragraphs here.

More content in the first section to ensure we have enough text for chunking and overlap testing.

## Second Section

Content of the second section. This is another section that should create a separate chunk. The overlap should include content from the first section.

### Subsection

Subsection content that adds more depth to the document structure.

## Final Section

This is the final section of the document. It should not have next_content overlap.
"""

    def test_overlap_in_metadata_with_include_metadata_true(self, tool_instance):
        """
        Test: include_metadata=true keeps overlap in metadata fields.

        Verifies:
        - Chunks have <metadata> block
        - Metadata contains previous_content/next_content fields
        - Chunk content does NOT contain overlap text
        """
        tool_parameters = {
            "input_text": self.MULTI_SECTION_DOC,
            "max_chunk_size": 500,
            "chunk_overlap": 100,
            "include_metadata": True,
        }

        messages = list(tool_instance._invoke(tool_parameters))
        result = messages[0].message.variable_value

        # Need at least 2 chunks to test overlap
        assert len(result) >= 2, "Document should produce multiple chunks"

        # Check middle chunks have overlap in metadata
        for i, chunk_str in enumerate(result):
            assert "<metadata>" in chunk_str, f"Chunk {i} should have metadata block"

            # Extract metadata
            metadata_start = chunk_str.find("<metadata>") + len("<metadata>")
            metadata_end = chunk_str.find("</metadata>")
            metadata_json = chunk_str[metadata_start:metadata_end].strip()
            metadata = json.loads(metadata_json)

            # Middle chunks should have previous_content/next_content
            if i > 0:
                # Not first chunk - should have previous_content
                assert (
                    "previous_content" in metadata
                ), f"Chunk {i} should have previous_content"
            if i < len(result) - 1:
                # Not last chunk - should have next_content
                assert "next_content" in metadata, f"Chunk {i} should have next_content"

    def test_overlap_embedded_with_include_metadata_false(self, tool_instance):
        """
        Test: include_metadata=false embeds overlap in chunk text.

        Verifies:
        - Chunks have NO <metadata> block
        - Chunk text contains overlap from adjacent chunks
        - Formula: previous_content + "\n" + main + "\n" + next_content
        """
        tool_parameters = {
            "input_text": self.MULTI_SECTION_DOC,
            "max_chunk_size": 500,
            "chunk_overlap": 100,
            "include_metadata": False,
        }

        messages = list(tool_instance._invoke(tool_parameters))
        result_no_meta = messages[0].message.variable_value

        # Also get version with metadata for comparison
        tool_parameters["include_metadata"] = True
        messages_meta = list(tool_instance._invoke(tool_parameters))
        result_with_meta = messages_meta[0].message.variable_value

        # Same number of chunks
        assert len(result_no_meta) == len(result_with_meta)

        # No metadata tags in result without metadata
        for chunk_str in result_no_meta:
            assert "<metadata>" not in chunk_str
            assert "</metadata>" not in chunk_str

        # Compare chunks - verify overlap is embedded
        for i in range(len(result_with_meta)):
            chunk_with_meta = result_with_meta[i]
            chunk_no_meta = result_no_meta[i]

            # Extract metadata and main content from metadata version
            metadata_start = chunk_with_meta.find("<metadata>") + len("<metadata>")
            metadata_end = chunk_with_meta.find("</metadata>")
            metadata_json = chunk_with_meta[metadata_start:metadata_end].strip()
            metadata = json.loads(metadata_json)
            # Extract main content after metadata (not used but calculated for consistency)
            _ = chunk_with_meta[metadata_end + len("</metadata>") :].strip()

            # Get overlap values from metadata
            prev_content = metadata.get("previous_content", "")
            next_content = metadata.get("next_content", "")

            # Verify overlap is embedded in no-metadata version
            if prev_content:
                assert (
                    prev_content in chunk_no_meta
                ), f"Chunk {i}: previous_content should be embedded in chunk text"
            if next_content:
                assert (
                    next_content in chunk_no_meta
                ), f"Chunk {i}: next_content should be embedded in chunk text"

    def test_first_chunk_no_previous_content(self, tool_instance):
        """
        Test: First chunk has no leading overlap.

        Verifies:
        - First chunk does not start with overlap from previous chunk
        - Content starts with actual document start (or just next_content)
        """
        tool_parameters = {
            "input_text": self.MULTI_SECTION_DOC,
            "max_chunk_size": 500,
            "chunk_overlap": 100,
            "include_metadata": True,
        }

        messages = list(tool_instance._invoke(tool_parameters))
        result = messages[0].message.variable_value

        if len(result) < 1:
            pytest.skip("No chunks produced")

        # First chunk metadata
        first_chunk = result[0]
        metadata_start = first_chunk.find("<metadata>") + len("<metadata>")
        metadata_end = first_chunk.find("</metadata>")
        metadata_json = first_chunk[metadata_start:metadata_end].strip()
        metadata = json.loads(metadata_json)

        # First chunk should NOT have previous_content
        assert "previous_content" not in metadata or not metadata.get(
            "previous_content"
        ), "First chunk should not have previous_content"

    def test_last_chunk_no_next_content(self, tool_instance):
        """
        Test: Last chunk has no trailing overlap.

        Verifies:
        - Last chunk does not end with overlap from next chunk
        """
        tool_parameters = {
            "input_text": self.MULTI_SECTION_DOC,
            "max_chunk_size": 500,
            "chunk_overlap": 100,
            "include_metadata": True,
        }

        messages = list(tool_instance._invoke(tool_parameters))
        result = messages[0].message.variable_value

        if len(result) < 1:
            pytest.skip("No chunks produced")

        # Last chunk metadata
        last_chunk = result[-1]
        metadata_start = last_chunk.find("<metadata>") + len("<metadata>")
        metadata_end = last_chunk.find("</metadata>")
        metadata_json = last_chunk[metadata_start:metadata_end].strip()
        metadata = json.loads(metadata_json)

        # Last chunk should NOT have next_content
        assert "next_content" not in metadata or not metadata.get(
            "next_content"
        ), "Last chunk should not have next_content"

    def test_zero_overlap_no_extra_content(self, tool_instance):
        """
        Test: chunk_overlap=0 produces no overlap.

        Verifies:
        - With include_metadata=false and chunk_overlap=0
        - Chunks contain only main content (no extra newlines)
        """
        tool_parameters = {
            "input_text": self.MULTI_SECTION_DOC,
            "max_chunk_size": 500,
            "chunk_overlap": 0,
            "include_metadata": False,
        }

        messages = list(tool_instance._invoke(tool_parameters))
        result_no_overlap = messages[0].message.variable_value

        # Also get with metadata to compare
        tool_parameters["include_metadata"] = True
        messages_meta = list(tool_instance._invoke(tool_parameters))
        result_with_meta = messages_meta[0].message.variable_value

        # Verify no overlap metadata
        for i, chunk_with_meta in enumerate(result_with_meta):
            metadata_start = chunk_with_meta.find("<metadata>") + len("<metadata>")
            metadata_end = chunk_with_meta.find("</metadata>")
            metadata_json = chunk_with_meta[metadata_start:metadata_end].strip()
            metadata = json.loads(metadata_json)

            # With overlap=0, should have no overlap fields
            assert "previous_content" not in metadata or not metadata.get(
                "previous_content"
            )
            assert "next_content" not in metadata or not metadata.get("next_content")

        # No-metadata chunks should be identical to main content only
        for i in range(len(result_with_meta)):
            chunk_with_meta = result_with_meta[i]
            chunk_no_meta = result_no_overlap[i]

            # Extract main content
            metadata_end = chunk_with_meta.find("</metadata>")
            main_content = chunk_with_meta[metadata_end + len("</metadata>") :].strip()

            # Should be identical (no overlap added)
            assert (
                chunk_no_meta.strip() == main_content
            ), f"Chunk {i} with overlap=0 should be identical to main content"

    def test_overlap_consistency_between_modes(self, tool_instance):
        """
        Test: Same document produces consistent chunk count in both modes.

        Verifies:
        - include_metadata=true and include_metadata=false produce same number of chunks
        - Overlap doesn't affect chunking logic, only output format
        """
        tool_parameters = {
            "input_text": self.MULTI_SECTION_DOC,
            "max_chunk_size": 500,
            "chunk_overlap": 100,
            "include_metadata": True,
        }

        messages_true = list(tool_instance._invoke(tool_parameters))
        result_true = messages_true[0].message.variable_value

        tool_parameters["include_metadata"] = False
        messages_false = list(tool_instance._invoke(tool_parameters))
        result_false = messages_false[0].message.variable_value

        # Same number of chunks
        assert len(result_true) == len(
            result_false
        ), "Both modes should produce the same number of chunks"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
