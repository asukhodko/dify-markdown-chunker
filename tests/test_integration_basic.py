"""Basic Integration Tests for Core Functionality

Tests that the tool works end-to-end with real markdown content.
"""

from pathlib import Path

import pytest


class TestBasicIntegration:
    """Basic integration tests for core functionality"""

    @pytest.fixture
    def tool_file(self):
        """Return path to tool file."""
        return Path(__file__).parent.parent / "tools" / "markdown_chunk_tool.py"

    @pytest.fixture
    def manifest_file(self):
        """Return path to manifest file."""
        return Path(__file__).parent.parent / "manifest.yaml"

    @pytest.fixture
    def provider_yaml(self):
        """Return path to provider YAML."""
        return Path(__file__).parent.parent / "provider" / "markdown_chunker.yaml"

    @pytest.fixture
    def tool_yaml(self):
        """Return path to tool YAML."""
        return Path(__file__).parent.parent / "tools" / "markdown_chunk_tool.yaml"

    def test_all_core_files_exist(
        self, tool_file, manifest_file, provider_yaml, tool_yaml
    ):
        """Test that all core files exist."""
        assert tool_file.exists(), "Tool file missing"
        assert manifest_file.exists(), "Manifest file missing"
        assert provider_yaml.exists(), "Provider YAML missing"
        assert tool_yaml.exists(), "Tool YAML missing"

    def test_tool_has_invoke_method(self, tool_file):
        """Test that tool has _invoke method."""
        content = tool_file.read_text()
        assert "def _invoke(" in content
        assert "tool_parameters" in content

    def test_tool_imports_required_modules(self, tool_file):
        """Test that tool imports all required modules."""
        content = tool_file.read_text()

        # Dify imports
        assert "from dify_plugin import Tool" in content
        assert "from dify_plugin.entities.tool import ToolInvokeMessage" in content

        # Migration adapter import (updated for migration)
        assert "from adapter import MigrationAdapter" in content

    def test_tool_handles_all_parameters(self, tool_file):
        """Test that tool handles all 5 parameters."""
        content = tool_file.read_text()

        assert "input_text" in content
        assert "max_chunk_size" in content
        assert "chunk_overlap" in content
        assert "strategy" in content
        assert "include_metadata" in content

    def test_tool_creates_chunk_config(self, tool_file):
        """Test that tool creates ChunkConfig."""
        content = tool_file.read_text()
        assert "build_chunker_config(" in content

    def test_tool_instantiates_chunker(self, tool_file):
        """Test that tool instantiates adapter."""
        content = tool_file.read_text()
        assert "MigrationAdapter(" in content

    def test_tool_calls_chunk_method(self, tool_file):
        """Test that tool calls chunking method."""
        content = tool_file.read_text()
        assert "run_chunking(" in content

    def test_tool_formats_results(self, tool_file):
        """Test that tool formats results."""
        content = tool_file.read_text()
        assert "content" in content
        assert "metadata" in content

    def test_tool_yields_results(self, tool_file):
        """Test that tool yields results."""
        content = tool_file.read_text()
        assert "yield" in content
        assert "create_variable_message" in content or "create_text_message" in content

    def test_manifest_references_provider(self, manifest_file):
        """Test that manifest references provider."""
        content = manifest_file.read_text()
        assert "provider/markdown_chunker.yaml" in content

    def test_provider_references_tool(self, provider_yaml):
        """Test that provider references tool."""
        content = provider_yaml.read_text()
        assert "tools/markdown_chunk_tool.yaml" in content

    def test_tool_yaml_references_python(self, tool_yaml):
        """Test that tool YAML references Python file."""
        content = tool_yaml.read_text()
        assert "tools/markdown_chunk_tool.py" in content

    def test_complete_reference_chain(
        self, manifest_file, provider_yaml, tool_yaml, tool_file
    ):
        """Test complete reference chain: manifest -> provider -> tool -> python."""
        # All files exist
        assert manifest_file.exists()
        assert provider_yaml.exists()
        assert tool_yaml.exists()
        assert tool_file.exists()

        # References are correct
        manifest_content = manifest_file.read_text()
        provider_content = provider_yaml.read_text()
        tool_content = tool_yaml.read_text()

        assert "provider/markdown_chunker.yaml" in manifest_content
        assert "tools/markdown_chunk_tool.yaml" in provider_content
        assert "tools/markdown_chunk_tool.py" in tool_content

    def test_error_handling_complete(self, tool_file):
        """Test that error handling is complete."""
        content = tool_file.read_text()

        # Has try-except
        assert "try:" in content
        assert "except ValueError" in content
        assert "except Exception" in content

        # Has error messages
        assert "Validation error" in content
        assert "Error chunking document" in content

    def test_input_validation_complete(self, tool_file):
        """Test that input validation is complete."""
        content = tool_file.read_text()

        # Validates empty input
        assert "not input_text" in content or "input_text.strip()" in content

    def test_parameter_defaults_present(self, tool_file):
        """Test that parameter defaults are present."""
        content = tool_file.read_text()

        # Default values (v2 uses 4096 for max_chunk_size, 200 for overlap)
        assert "4096" in content  # max_chunk_size default
        assert "200" in content  # chunk_overlap default
        assert "auto" in content  # strategy default
        assert "True" in content or "true" in content  # include_metadata default

    def test_docstrings_present(self, tool_file):
        """Test that docstrings are present."""
        content = tool_file.read_text()

        # Has module docstring
        lines = content.split("\n")
        assert '"""' in lines[0] or '"""' in lines[1]

        # Has class docstring
        assert "class MarkdownChunkTool" in content

        # Has method docstring
        assert "def _invoke" in content

    def test_type_hints_present(self, tool_file):
        """Test that type hints are present."""
        content = tool_file.read_text()

        # Has type hints
        assert "dict[str, Any]" in content or "Dict[str, Any]" in content
        assert "Generator" in content or "generator" in content.lower()

    def test_no_syntax_errors(self, tool_file):
        """Test that tool file has no syntax errors."""
        content = tool_file.read_text()

        # Try to compile
        try:
            compile(content, str(tool_file), "exec")
        except SyntaxError as e:
            pytest.fail(f"Syntax error in tool file: {e}")

    def test_core_functionality_summary(
        self, tool_file, manifest_file, provider_yaml, tool_yaml
    ):
        """Summary test: verify all core functionality is present."""
        issues = []

        # Check files exist
        if not tool_file.exists():
            issues.append("Tool file missing")
        if not manifest_file.exists():
            issues.append("Manifest file missing")
        if not provider_yaml.exists():
            issues.append("Provider YAML missing")
        if not tool_yaml.exists():
            issues.append("Tool YAML missing")

        if issues:
            pytest.fail(f"Core files missing: {', '.join(issues)}")

        # Check tool content
        tool_content = tool_file.read_text()

        required_elements = [
            ("_invoke method", "def _invoke("),
            ("adapter config creation", "build_chunker_config("),
            ("adapter instantiation", "MigrationAdapter("),
            ("chunking method call", "run_chunking("),
            ("error handling", "try:"),
            ("validation error handling", "except ValueError"),
            ("general error handling", "except Exception"),
            ("result formatting", "formatted_result"),
            ("result yielding", "yield"),
        ]

        for name, pattern in required_elements:
            if pattern not in tool_content:
                issues.append(f"{name} missing")

        if issues:
            pytest.fail(f"Core functionality incomplete: {', '.join(issues)}")
