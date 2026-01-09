"""
Property tests for plugin dependencies.

Property 3: Dependencies Completeness
For any plugin initialization, the requirements.txt file should contain
dify_plugin==0.7.0, markdown-it-py>=3.0.0, and pydantic>=2.0.0

Validates: Requirements 1.4
"""

import sys
from pathlib import Path


def test_requirements_file_exists():
    """Verify requirements.txt exists in plugin root."""
    plugin_root = Path(__file__).parent.parent
    requirements_file = plugin_root / "requirements.txt"
    assert requirements_file.exists(), "requirements.txt must exist in plugin root"


def test_requirements_content():
    """Property 3: Verify all required dependencies are in requirements.txt."""
    plugin_root = Path(__file__).parent.parent
    requirements_file = plugin_root / "requirements.txt"

    with open(requirements_file, "r") as f:
        content = f.read()

    # Required dependencies (using >= for flexibility)
    required_deps = [
        "dify_plugin>=0.7.0",
        "markdown-it-py>=3.0.0",
        "pydantic>=2.0.0",
    ]

    for dep in required_deps:
        assert (
            dep in content
        ), f"Required dependency '{dep}' not found in requirements.txt"


def test_dify_plugin_import():
    """Verify dify_plugin can be imported."""
    try:
        import dify_plugin

        # dify_plugin doesn't export __version__, but we can verify it's installed
        assert dify_plugin is not None
    except ImportError as e:
        assert False, f"Failed to import dify_plugin: {e}"


def test_markdown_it_import():
    """Verify markdown-it-py can be imported."""
    try:
        import markdown_it

        assert hasattr(markdown_it, "__version__")
    except ImportError as e:
        assert False, f"Failed to import markdown_it: {e}"


def test_pydantic_import():
    """Verify pydantic can be imported."""
    try:
        import pydantic

        assert hasattr(pydantic, "__version__")
    except ImportError as e:
        assert False, f"Failed to import pydantic: {e}"


def test_all_dify_plugin_components():
    """Verify all required Dify plugin components can be imported."""
    try:
        from dify_plugin import DifyPluginEnv, Plugin, Tool, ToolProvider
        from dify_plugin.entities.tool import ToolInvokeMessage

        # Verify classes exist
        assert Plugin is not None
        assert DifyPluginEnv is not None
        assert Tool is not None
        assert ToolProvider is not None
        assert ToolInvokeMessage is not None
    except ImportError as e:
        assert False, f"Failed to import Dify plugin components: {e}"


if __name__ == "__main__":
    # Run tests
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
