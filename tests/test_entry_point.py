"""Property Test 2: Entry Point Validity

Validates: Requirements 1.3
Ensures main.py is valid and properly configured.
"""

import ast
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestEntryPointValidity:
    """Property 2: Entry Point Validity"""

    @pytest.fixture
    def main_py_path(self):
        """Get path to main.py."""
        return Path(__file__).parent.parent / "main.py"

    @pytest.fixture
    def main_py_content(self, main_py_path):
        """Read main.py content."""
        assert main_py_path.exists(), "main.py not found"
        return main_py_path.read_text(encoding="utf-8")

    @pytest.fixture
    def main_py_ast(self, main_py_content):
        """Parse main.py as AST."""
        try:
            return ast.parse(main_py_content)
        except SyntaxError as e:
            pytest.fail(f"main.py has syntax error: {e}")

    def test_syntax_validity(self, main_py_ast):
        """Test that main.py has valid Python syntax."""
        # If we got here, AST parsing succeeded
        assert main_py_ast is not None
        assert isinstance(main_py_ast, ast.Module)

    def test_required_imports(self, main_py_ast):
        """Test that required imports are present."""
        imports = []
        for node in ast.walk(main_py_ast):
            if isinstance(node, ast.ImportFrom):
                if node.module == "dify_plugin":
                    imports.extend([alias.name for alias in node.names])

        required_imports = ["Plugin", "DifyPluginEnv"]
        for imp in required_imports:
            assert imp in imports, f"Required import '{imp}' not found"

    def test_timeout_configuration(self, main_py_content):
        """Test that timeout is properly configured."""
        assert (
            "MAX_REQUEST_TIMEOUT=300" in main_py_content
        ), "MAX_REQUEST_TIMEOUT should be set to 300 seconds"

    def test_plugin_instantiation(self, main_py_ast):
        """Test that plugin is properly instantiated."""
        # Look for plugin=Plugin(...) assignment
        plugin_assignment = None
        for node in ast.walk(main_py_ast):
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "plugin"
            ):
                plugin_assignment = node
                break

        assert plugin_assignment is not None, "plugin variable assignment not found"
        assert isinstance(
            plugin_assignment.value, ast.Call
        ), "plugin should be a function call"
        assert isinstance(
            plugin_assignment.value.func, ast.Name
        ), "plugin should be called directly"
        assert (
            plugin_assignment.value.func.id == "Plugin"
        ), "plugin should be instance of Plugin"

    def test_main_guard(self, main_py_ast):
        """Test that if __name__ == '__main__' guard is present."""
        main_guard = None
        for node in ast.walk(main_py_ast):
            if (
                isinstance(node, ast.If)
                and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__"
            ):
                main_guard = node
                break

        assert main_guard is not None, "if __name__ == '__main__' guard not found"

    def test_plugin_run_call(self, main_py_ast):
        """Test that plugin.run() is called in main guard."""
        # Find the main guard and check for plugin.run() call
        main_guard = None
        for node in ast.walk(main_py_ast):
            if (
                isinstance(node, ast.If)
                and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__"
            ):
                main_guard = node
                break

        assert main_guard is not None, "Main guard not found"

        # Look for plugin.run() call in the main guard body
        run_call_found = False
        for stmt in main_guard.body:
            if (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Attribute)
                and isinstance(stmt.value.func.value, ast.Name)
                and stmt.value.func.value.id == "plugin"
                and stmt.value.func.attr == "run"
            ):
                run_call_found = True
                break

        assert run_call_found, "plugin.run() call not found in main guard"

    def test_docstring_present(self, main_py_ast):
        """Test that module has a docstring."""
        if (
            main_py_ast.body
            and isinstance(main_py_ast.body[0], ast.Expr)
            and isinstance(main_py_ast.body[0].value, ast.Constant)
            and isinstance(main_py_ast.body[0].value.value, str)
        ):
            docstring = main_py_ast.body[0].value.value
            assert len(docstring) > 50, "Docstring should be descriptive"
            assert "Dify Plugin" in docstring, "Docstring should mention Dify Plugin"
        else:
            pytest.fail("Module docstring not found")

    def test_importable_as_module(self, main_py_path):
        """Test that main.py can be imported without errors."""
        # Add the plugin directory to sys.path temporarily
        plugin_dir = main_py_path.parent
        if str(plugin_dir) not in sys.path:
            sys.path.insert(0, str(plugin_dir))

        try:
            # Mock the plugin.run() call to prevent actual execution
            with patch("dify_plugin.Plugin") as mock_plugin_class:
                mock_plugin_instance = MagicMock()
                mock_plugin_class.return_value = mock_plugin_instance

                # Import main module
                import importlib.util

                spec = importlib.util.spec_from_file_location("main", main_py_path)
                main_module = importlib.util.module_from_spec(spec)

                # This should not raise any import errors
                spec.loader.exec_module(main_module)

                # Verify plugin was instantiated
                mock_plugin_class.assert_called_once()

                # Verify the module has expected attributes
                assert hasattr(main_module, "plugin")
                assert hasattr(main_module, "MAX_REQUEST_TIMEOUT")
                assert main_module.MAX_REQUEST_TIMEOUT == 300

        finally:
            # Clean up sys.path
            if str(plugin_dir) in sys.path:
                sys.path.remove(str(plugin_dir))

    def test_no_global_execution(self, main_py_content):
        """Test that no code executes at module level (except under main guard)."""
        # This is a heuristic test - we check that there are no obvious
        # side effects at module level
        lines = main_py_content.split("\n")

        # Skip imports, assignments, and function definitions
        problematic_lines = []
        in_main_guard = False
        in_docstring = False

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Skip empty lines and comments
            if not stripped or stripped.startswith("#"):
                continue

            # Track docstring state
            if '"""' in stripped or "'''" in stripped:
                in_docstring = not in_docstring
                continue

            # Skip if we're in docstring
            if in_docstring:
                continue

            # Check if we're entering main guard
            if "if __name__ == '__main__'" in stripped:
                in_main_guard = True
                continue

            # Skip if we're in main guard
            if in_main_guard:
                continue

            # Skip imports, assignments, function/class definitions
            if (
                stripped.startswith(("import ", "from "))
                or "=" in stripped
                or stripped.startswith(("def ", "class "))
                or stripped.startswith('"')
                or stripped.startswith("'")
                or
                # Skip continuation lines (function calls, etc.)
                stripped.endswith("(")
                or stripped.startswith((")", "]", "}"))
            ):
                continue

            # If we get here, it might be problematic
            problematic_lines.append((i, stripped))

        if problematic_lines:
            lines_str = "\n".join(
                [f"Line {i}: {line}" for i, line in problematic_lines]
            )
            pytest.fail(f"Potential global execution found:\n{lines_str}")
