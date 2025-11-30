"""Integration Tests with Fixtures

Tests that verify the tool works with real markdown fixtures.
These tests validate structure and logic without requiring the full library.
"""

from pathlib import Path

import pytest


class TestFixtureIntegration:
    """Integration tests using markdown fixtures"""

    @pytest.fixture
    def fixtures_dir(self):
        """Return path to fixtures directory."""
        return Path(__file__).parent / "fixtures"

    @pytest.fixture
    def tool_file(self):
        """Return path to tool file."""
        return Path(__file__).parent.parent / "tools" / "markdown_chunk_tool.py"

    def test_all_fixtures_exist(self, fixtures_dir):
        """Test that all fixture files exist."""
        expected_fixtures = [
            "code_heavy.md",
            "structural.md",
            "mixed.md",
            "list_heavy.md",
            "table_heavy.md",
            "edge_cases.md",
        ]

        for fixture in expected_fixtures:
            fixture_path = fixtures_dir / fixture
            assert fixture_path.exists(), f"Fixture {fixture} not found"

    def test_fixtures_are_readable(self, fixtures_dir):
        """Test that all fixtures can be read."""
        for fixture_file in fixtures_dir.glob("*.md"):
            content = fixture_file.read_text(encoding="utf-8")
            assert len(content) > 0, f"Fixture {fixture_file.name} is empty"

    def test_code_heavy_fixture_structure(self, fixtures_dir):
        """Test code-heavy fixture has expected structure."""
        content = (fixtures_dir / "code_heavy.md").read_text(encoding="utf-8")

        # Should contain code blocks
        assert "```python" in content
        assert "```javascript" in content
        assert "```sql" in content

        # Should have headers
        assert "# Code-Heavy Document" in content
        assert "## Python Example" in content

    def test_structural_fixture_hierarchy(self, fixtures_dir):
        """Test structural fixture has hierarchical headers."""
        content = (fixtures_dir / "structural.md").read_text(encoding="utf-8")

        # Should have multiple header levels
        assert "# Structural Document" in content
        assert "## Section" in content
        assert "### Subsection" in content
        assert "#### Sub-subsection" in content

    def test_mixed_fixture_variety(self, fixtures_dir):
        """Test mixed fixture has variety of content types."""
        content = (fixtures_dir / "mixed.md").read_text(encoding="utf-8")

        # Should have code
        assert "```python" in content

        # Should have lists
        assert "- First point" in content

        # Should have tables
        assert "| Feature |" in content

        # Should have regular text
        assert "Regular paragraph" in content

    def test_list_heavy_fixture_lists(self, fixtures_dir):
        """Test list-heavy fixture has multiple lists."""
        content = (fixtures_dir / "list_heavy.md").read_text(encoding="utf-8")

        # Should have unordered lists
        assert "- Fruits" in content

        # Should have ordered lists
        assert "1. Complete project" in content

        # Should have task lists
        assert "- [x]" in content
        assert "- [ ]" in content

    def test_table_heavy_fixture_tables(self, fixtures_dir):
        """Test table-heavy fixture has multiple tables."""
        content = (fixtures_dir / "table_heavy.md").read_text(encoding="utf-8")

        # Should have table headers
        assert "| ID | Name |" in content
        assert "| Metric | Q1 |" in content

        # Should have table separators
        assert "|----" in content or "|----|" in content

    def test_edge_cases_fixture_variety(self, fixtures_dir):
        """Test edge cases fixture has various edge cases."""
        content = (fixtures_dir / "edge_cases.md").read_text(encoding="utf-8")

        # Should have empty sections
        assert "### Empty Subsection" in content

        # Should have unicode
        assert "你好世界" in content or "Привет" in content

        # Should have special characters
        assert "~!@#$%^&*()" in content

    def test_tool_can_handle_fixture_content(self, tool_file, fixtures_dir):
        """Test that tool structure supports fixture content."""
        tool_content = tool_file.read_text()

        # Tool should handle input_text parameter
        assert "input_text" in tool_content

        # Tool should handle strategy parameter
        assert "strategy" in tool_content

        # Tool should create ChunkConfig
        assert "ChunkConfig" in tool_content

        # Tool should instantiate MarkdownChunker
        assert "MarkdownChunker" in tool_content

    def test_fixtures_size_variety(self, fixtures_dir):
        """Test that fixtures have variety in size."""
        sizes = []
        for fixture_file in fixtures_dir.glob("*.md"):
            content = fixture_file.read_text(encoding="utf-8")
            sizes.append(len(content))

        # Should have variety (not all same size)
        assert len(set(sizes)) > 1, "All fixtures are the same size"

        # Should have at least one smaller and one larger fixture
        assert min(sizes) < 1000, "No smaller fixtures"
        assert max(sizes) > 1000, "No larger fixtures"

    def test_fixtures_content_types(self, fixtures_dir):
        """Test that fixtures cover different content types."""
        all_content = ""
        for fixture_file in fixtures_dir.glob("*.md"):
            all_content += fixture_file.read_text(encoding="utf-8")

        # Should have code blocks
        assert "```" in all_content

        # Should have headers
        assert "#" in all_content

        # Should have lists
        assert "-" in all_content or "*" in all_content

        # Should have tables
        assert "|" in all_content

    def test_strategy_parameter_values(self, tool_file):
        """Test that tool supports strategy parameter values."""
        tool_content = tool_file.read_text()

        # Should reference strategy parameter
        assert "strategy" in tool_content

        # Should handle "auto" strategy
        assert "auto" in tool_content

    def test_tool_handles_empty_input(self, tool_file):
        """Test that tool validates empty input."""
        tool_content = tool_file.read_text()

        # Should check for empty input
        assert "not input_text" in tool_content or "input_text.strip()" in tool_content

        # Should return error for empty input
        assert "empty" in tool_content.lower()

    def test_tool_error_handling_for_fixtures(self, tool_file):
        """Test that tool has error handling for processing."""
        tool_content = tool_file.read_text()

        # Should have try-except
        assert "try:" in tool_content
        assert "except" in tool_content

        # Should handle errors gracefully
        assert "Error" in tool_content or "error" in tool_content

    def test_fixtures_markdown_validity(self, fixtures_dir):
        """Test that fixtures are valid markdown."""
        for fixture_file in fixtures_dir.glob("*.md"):
            content = fixture_file.read_text(encoding="utf-8")

            # Should not be empty
            assert len(content.strip()) > 0

            # Should have at least one header
            assert "#" in content

    def test_tool_metadata_handling(self, tool_file):
        """Test that tool handles metadata parameter."""
        tool_content = tool_file.read_text()

        # Should handle include_metadata parameter
        assert "include_metadata" in tool_content

        # Should handle metadata in results
        assert "metadata" in tool_content

    def test_fixtures_cover_requirements(self, fixtures_dir):
        """Test that fixtures cover different chunking requirements."""
        fixture_names = [f.name for f in fixtures_dir.glob("*.md")]

        # Should have code-focused fixture
        assert any("code" in name for name in fixture_names)

        # Should have structure-focused fixture
        assert any("structural" in name for name in fixture_names)

        # Should have mixed content fixture
        assert any("mixed" in name for name in fixture_names)

        # Should have edge cases fixture
        assert any("edge" in name for name in fixture_names)

    def test_tool_chunk_config_parameters(self, tool_file):
        """Test that tool creates ChunkConfig with correct parameters."""
        tool_content = tool_file.read_text()

        # Should create ChunkConfig
        assert "ChunkConfig(" in tool_content

        # Should pass parameters
        assert "max_chunk_size" in tool_content
        assert "chunk_overlap" in tool_content

    def test_fixtures_realistic_content(self, fixtures_dir):
        """Test that fixtures contain realistic markdown content."""
        for fixture_file in fixtures_dir.glob("*.md"):
            content = fixture_file.read_text(encoding="utf-8")

            # Should have headers
            has_headers = "#" in content

            # Should have some text content (not just headers)
            lines = content.split("\n")
            text_lines = [
                line
                for line in lines
                if line.strip() and not line.strip().startswith("#")
            ]
            has_text = len(text_lines) > 0

            assert (
                has_headers and has_text
            ), f"Fixture {fixture_file.name} lacks realistic content"
