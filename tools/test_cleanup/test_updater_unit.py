"""
Unit tests for infrastructure updater components.
"""

import pytest
import tempfile
import os
from pathlib import Path

from .updater import InfrastructureUpdater, MakefileUpdater, PytestConfigUpdater, DocumentationUpdater, ChangeReport
from .config import CleanupConfig


class TestMakefileUpdater:
    """Unit tests for MakefileUpdater."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = CleanupConfig.from_project_root("/tmp")
        self.updater = MakefileUpdater(self.config)
    
    def test_remove_file_references(self):
        """Test removal of file references from Makefile content."""
        content = """
test:
\tpython -m pytest test_remove_me.py test_keep.py

test-all:
\tpython -m pytest tests/test_remove_me.py tests/
"""
        
        updated_content, changes = self.updater._remove_file_references(content, "test_remove_me.py")
        
        assert "test_remove_me.py" not in updated_content
        assert "test_keep.py" in updated_content
        assert len(changes) > 0
        assert any("test_remove_me.py" in change for change in changes)
    
    def test_optimize_test_targets(self):
        """Test optimization of test targets."""
        content = """
test-all:
\tpython -m pytest tests/

test:
\tpython -m pytest tests/test_basic.py
"""
        
        updated_content, changes = self.updater._optimize_test_targets(content)
        
        # Should add ignore patterns to test-all
        assert "--ignore=" in updated_content or "tests/" in updated_content
        # Other targets should be preserved
        assert "test:" in updated_content
        assert "test_basic.py" in updated_content
    
    def test_update_targets_integration(self):
        """Test complete target update process."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.updater.makefile_path = os.path.join(temp_dir, "Makefile")
            
            # Create Makefile
            makefile_content = """
test:
\tpython -m pytest test_remove.py test_keep.py

test-all:
\tpython -m pytest tests/
"""
            with open(self.updater.makefile_path, 'w') as f:
                f.write(makefile_content)
            
            # Update targets
            removed_files = ["test_remove.py"]
            adapted_files = ["test_adapted.py"]
            changes = self.updater.update_targets(removed_files, adapted_files)
            
            # Verify changes were made
            assert len(changes) > 0
            
            # Verify file was updated
            with open(self.updater.makefile_path, 'r') as f:
                updated_content = f.read()
            
            assert "test_remove.py" not in updated_content
            assert "test_keep.py" in updated_content
    
    def test_update_targets_no_makefile(self):
        """Test handling when Makefile doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.updater.makefile_path = os.path.join(temp_dir, "Makefile")
            
            changes = self.updater.update_targets(["test.py"], [])
            
            # Should return empty changes list
            assert changes == []


class TestPytestConfigUpdater:
    """Unit tests for PytestConfigUpdater."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = CleanupConfig.from_project_root("/tmp")
        self.updater = PytestConfigUpdater(self.config)
    
    def test_update_pytest_ini_existing(self):
        """Test updating existing pytest.ini file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.updater.pytest_ini_path = os.path.join(temp_dir, "pytest.ini")
            
            # Create pytest.ini
            initial_content = """[tool:pytest]
testpaths = tests
addopts = -v
"""
            with open(self.updater.pytest_ini_path, 'w') as f:
                f.write(initial_content)
            
            # Update configuration
            excluded_dirs = ["tests/legacy", "tests/old"]
            changes = self.updater._update_pytest_ini(excluded_dirs)
            
            assert len(changes) > 0
            
            # Verify file was updated
            with open(self.updater.pytest_ini_path, 'r') as f:
                updated_content = f.read()
            
            assert "--ignore=tests/legacy" in updated_content
            assert "--ignore=tests/old" in updated_content
            assert "testpaths = tests" in updated_content  # Original content preserved
    
    def test_update_pytest_ini_no_pytest_section(self):
        """Test updating pytest.ini without existing pytest section."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.updater.pytest_ini_path = os.path.join(temp_dir, "pytest.ini")
            
            # Create pytest.ini without pytest section
            initial_content = """# Some comments
[other]
setting = value
"""
            with open(self.updater.pytest_ini_path, 'w') as f:
                f.write(initial_content)
            
            # Update configuration
            excluded_dirs = ["tests/legacy"]
            changes = self.updater._update_pytest_ini(excluded_dirs)
            
            assert len(changes) > 0
            
            # Verify pytest section was added
            with open(self.updater.pytest_ini_path, 'r') as f:
                updated_content = f.read()
            
            assert "[tool:pytest]" in updated_content
            assert "--ignore=tests/legacy" in updated_content
            assert "[other]" in updated_content  # Original content preserved
    
    def test_create_pytest_ini(self):
        """Test creating new pytest.ini file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.updater.pytest_ini_path = os.path.join(temp_dir, "pytest.ini")
            
            # Create new pytest.ini
            excluded_dirs = ["tests/legacy", "tests/old"]
            changes = self.updater._create_pytest_ini(excluded_dirs)
            
            assert len(changes) > 0
            assert os.path.exists(self.updater.pytest_ini_path)
            
            # Verify content
            with open(self.updater.pytest_ini_path, 'r') as f:
                content = f.read()
            
            assert "[tool:pytest]" in content
            assert "testpaths = tests" in content
            assert "--ignore=tests/legacy" in content
            assert "--ignore=tests/old" in content
    
    def test_update_config_integration(self):
        """Test complete configuration update process."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.updater.pytest_ini_path = os.path.join(temp_dir, "pytest.ini")
            self.updater.pyproject_path = os.path.join(temp_dir, "pyproject.toml")
            
            # Test with no existing config files
            excluded_dirs = ["tests/legacy"]
            changes = self.updater.update_config(excluded_dirs)
            
            assert len(changes) > 0
            assert os.path.exists(self.updater.pytest_ini_path)


class TestDocumentationUpdater:
    """Unit tests for DocumentationUpdater."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = CleanupConfig.from_project_root("/tmp")
        self.updater = DocumentationUpdater(self.config)
    
    def test_update_readme_new_section(self):
        """Test adding new testing section to README."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.updater.readme_path = os.path.join(temp_dir, "README.md")
            
            # Create README without testing section
            initial_content = """# Test Project

This is a test project.

## Installation

Install dependencies...
"""
            with open(self.updater.readme_path, 'w') as f:
                f.write(initial_content)
            
            # Update README
            changes = ChangeReport(removed_tests=["test1.py", "test2.py"], adapted_tests=["test3.py"])
            doc_changes = self.updater._update_readme(changes)
            
            assert len(doc_changes) > 0
            
            # Verify testing section was added
            with open(self.updater.readme_path, 'r') as f:
                updated_content = f.read()
            
            assert "## Testing" in updated_content
            assert "make test-all" in updated_content
            assert "2 redundant tests were removed" in updated_content
            assert "# Test Project" in updated_content  # Original content preserved
    
    def test_update_readme_replace_section(self):
        """Test replacing existing testing section in README."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.updater.readme_path = os.path.join(temp_dir, "README.md")
            
            # Create README with existing testing section
            initial_content = """# Test Project

## Testing

Old testing information.

## Other Section

Other content.
"""
            with open(self.updater.readme_path, 'w') as f:
                f.write(initial_content)
            
            # Update README
            changes = ChangeReport(removed_tests=["test1.py"], adapted_tests=[])
            doc_changes = self.updater._update_readme(changes)
            
            assert len(doc_changes) > 0
            
            # Verify testing section was replaced
            with open(self.updater.readme_path, 'r') as f:
                updated_content = f.read()
            
            assert "## Testing" in updated_content
            assert "Old testing information" not in updated_content
            assert "make test-all" in updated_content
            assert "## Other Section" in updated_content  # Other sections preserved
    
    def test_update_contributing(self):
        """Test updating CONTRIBUTING.md with test guidelines."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.updater.contributing_path = os.path.join(temp_dir, "CONTRIBUTING.md")
            
            # Create CONTRIBUTING.md
            initial_content = """# Contributing

Please contribute to this project.

## Code Style

Follow the style guide.
"""
            with open(self.updater.contributing_path, 'w') as f:
                f.write(initial_content)
            
            # Update CONTRIBUTING.md
            changes = ChangeReport()
            doc_changes = self.updater._update_contributing(changes)
            
            assert len(doc_changes) > 0
            
            # Verify guidelines were added
            with open(self.updater.contributing_path, 'r') as f:
                updated_content = f.read()
            
            assert "## Test Guidelines" in updated_content
            assert "MigrationAdapter" in updated_content
            assert "test_migration_*.py" in updated_content
            assert "# Contributing" in updated_content  # Original content preserved
    
    def test_update_testing_docs(self):
        """Test creating/updating TESTING.md."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.updater.testing_path = os.path.join(temp_dir, "TESTING.md")
            
            # Update testing docs
            changes = ChangeReport(
                removed_tests=["test1.py", "test2.py"],
                adapted_tests=["test3.py", "test4.py"]
            )
            doc_changes = self.updater._update_testing_docs(changes)
            
            assert len(doc_changes) > 0
            assert os.path.exists(self.updater.testing_path)
            
            # Verify content
            with open(self.updater.testing_path, 'r') as f:
                content = f.read()
            
            assert "# Testing Documentation" in content
            assert "Total tests removed**: 2" in content
            assert "Total tests adapted**: 2" in content
            assert "make test-all" in content
            assert "MigrationAdapter" in content
    
    def test_update_docs_integration(self):
        """Test complete documentation update process."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.updater.readme_path = os.path.join(temp_dir, "README.md")
            self.updater.contributing_path = os.path.join(temp_dir, "CONTRIBUTING.md")
            self.updater.testing_path = os.path.join(temp_dir, "TESTING.md")
            
            # Create initial files
            with open(self.updater.readme_path, 'w') as f:
                f.write("# Project\n\nDescription.")
            
            with open(self.updater.contributing_path, 'w') as f:
                f.write("# Contributing\n\nGuidelines.")
            
            # Update all documentation
            changes = ChangeReport(removed_tests=["test1.py"], adapted_tests=["test2.py"])
            doc_changes = self.updater.update_docs(changes)
            
            assert len(doc_changes) > 0
            
            # Verify all files were updated
            assert os.path.exists(self.updater.readme_path)
            assert os.path.exists(self.updater.contributing_path)
            assert os.path.exists(self.updater.testing_path)


class TestInfrastructureUpdater:
    """Unit tests for InfrastructureUpdater integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = CleanupConfig.from_project_root("/tmp")
        self.updater = InfrastructureUpdater(self.config)
    
    def test_update_makefile_integration(self):
        """Test Makefile update integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.updater.makefile_updater.makefile_path = os.path.join(temp_dir, "Makefile")
            
            # Create Makefile
            makefile_content = "test:\n\tpython -m pytest test_remove.py"
            with open(self.updater.makefile_updater.makefile_path, 'w') as f:
                f.write(makefile_content)
            
            # Update Makefile
            removed_files = ["test_remove.py"]
            adapted_files = ["test_adapted.py"]
            
            # Should not raise exception
            self.updater.update_makefile(removed_files, adapted_files)
            
            # Verify file exists and was modified
            assert os.path.exists(self.updater.makefile_updater.makefile_path)
    
    def test_update_pytest_config_integration(self):
        """Test pytest config update integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.updater.pytest_updater.pytest_ini_path = os.path.join(temp_dir, "pytest.ini")
            self.updater.pytest_updater.pyproject_path = os.path.join(temp_dir, "pyproject.toml")
            
            # Update pytest config
            excluded_dirs = ["tests/legacy"]
            
            # Should not raise exception
            self.updater.update_pytest_config(excluded_dirs)
            
            # Should create pytest.ini
            pytest_ini_path = os.path.join(temp_dir, "pytest.ini")
            assert os.path.exists(pytest_ini_path)
    
    def test_update_documentation_integration(self):
        """Test documentation update integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.updater.doc_updater.readme_path = os.path.join(temp_dir, "README.md")
            self.updater.doc_updater.contributing_path = os.path.join(temp_dir, "CONTRIBUTING.md")
            self.updater.doc_updater.testing_path = os.path.join(temp_dir, "TESTING.md")
            
            # Create initial README
            readme_path = os.path.join(temp_dir, "README.md")
            with open(readme_path, 'w') as f:
                f.write("# Project\n\nDescription.")
            
            # Update documentation
            changes = ChangeReport(removed_tests=["test1.py"], adapted_tests=["test2.py"])
            
            # Should not raise exception
            self.updater.update_documentation(changes)
            
            # Should update README and create TESTING.md
            assert os.path.exists(readme_path)
            testing_path = os.path.join(temp_dir, "TESTING.md")
            assert os.path.exists(testing_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])