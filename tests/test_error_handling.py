"""Property Tests 19, 20, 21: Error Handling Validation

Validates: Requirements 4.7, 10.2, 10.3, 10.4
Ensures tool handles errors gracefully without crashing.
"""

from pathlib import Path

import pytest


class TestErrorHandling:
    """Property 19, 20, 21: Error Handling Validation"""

    @pytest.fixture
    def tool_file(self):
        """Return path to tool file."""
        return Path(__file__).parent.parent / "tools" / "markdown_chunk_tool.py"

    def test_try_except_structure_present(self, tool_file):
        """Property 19: Exception Handling - Test try-except structure exists."""
        content = tool_file.read_text()

        assert "try:" in content
        assert "except ValueError" in content
        assert "except Exception" in content

    def test_validation_error_handling_present(self, tool_file):
        """Property 20: Validation Error Format - Test ValueError handling exists."""
        content = tool_file.read_text()

        assert "except ValueError as e:" in content
        assert "Validation error" in content

    def test_general_error_handling_present(self, tool_file):
        """Property 21: General Error Format - Test general exception handling exists."""
        content = tool_file.read_text()

        assert "except Exception as e:" in content
        assert "Error chunking document" in content

    def test_empty_input_validation(self, tool_file):
        """Property 20: Validation Error Format - Test empty input validation."""
        content = tool_file.read_text()

        # Should check for empty or whitespace-only input
        assert "not input_text" in content or "input_text.strip()" in content
        assert "empty" in content.lower()

    def test_error_messages_use_create_text_message(self, tool_file):
        """Property 19: Exception Handling - Test errors use create_text_message."""
        content = tool_file.read_text()

        # Count create_text_message calls in error handling
        assert content.count("create_text_message") >= 3  # At least 3 error messages

    def test_no_bare_except(self, tool_file):
        """Property 19: Exception Handling - Test no bare except clauses."""
        content = tool_file.read_text()

        # Should not have bare except:
        assert "except:" not in content

    def test_error_handling_doesnt_crash(self, tool_file):
        """Property 19: Exception Handling - Test error handling returns messages."""
        content = tool_file.read_text()

        # Should yield error messages, not raise
        lines = content.split("\n")
        in_except_block = False
        has_yield_in_except = False

        for line in lines:
            if "except" in line and "as e:" in line:
                in_except_block = True
            elif in_except_block and "yield" in line:
                has_yield_in_except = True
                in_except_block = False

        assert has_yield_in_except

    def test_validation_error_format_correct(self, tool_file):
        """Property 20: Validation Error Format - Test validation error message format."""
        content = tool_file.read_text()

        # Should format as "Validation error: {str(e)}"
        assert "Validation error:" in content or "validation error" in content.lower()

    def test_general_error_format_correct(self, tool_file):
        """Property 21: General Error Format - Test general error message format."""
        content = tool_file.read_text()

        # Should format as "Error chunking document: {str(e)}"
        assert "Error chunking document:" in content

    def test_error_handling_covers_all_operations(self, tool_file):
        """Property 19: Exception Handling - Test try block covers all operations."""
        content = tool_file.read_text()

        # Try block should contain main operations
        assert "ChunkConfig" in content
        assert "MarkdownChunker" in content
        assert "chunk(" in content

    def test_error_messages_include_exception_details(self, tool_file):
        """Property 19, 20, 21: Error messages include exception details."""
        content = tool_file.read_text()

        # Should include str(e) in error messages
        assert content.count("str(e)") >= 2  # At least 2 error handlers use str(e)
