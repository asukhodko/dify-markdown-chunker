"""
Infrastructure update components for the cleanup system.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Set, Optional

from .models import ChangeReport, RemovalReport, AdaptationReport
from .config import CleanupConfig
from .logging_setup import LoggerMixin


class InfrastructureUpdater(LoggerMixin):
    """Main updater for test infrastructure components."""
    
    def __init__(self, config: CleanupConfig):
        self.config = config
        self.makefile_updater = MakefileUpdater(config)
        self.pytest_updater = PytestConfigUpdater(config)
        self.doc_updater = DocumentationUpdater(config)
    
    def update_makefile(self, removed_files: List[str], adapted_files: List[str]) -> None:
        """
        Update Makefile targets and references.
        
        Args:
            removed_files: List of removed test files
            adapted_files: List of adapted test files
        """
        self.logger.info(f"Updating Makefile for {len(removed_files)} removed and {len(adapted_files)} adapted files")
        self.makefile_updater.update_targets(removed_files, adapted_files)
    
    def update_pytest_config(self, excluded_dirs: List[str]) -> None:
        """
        Update pytest configuration to exclude removed directories.
        
        Args:
            excluded_dirs: List of directories to exclude from test discovery
        """
        self.logger.info(f"Updating pytest config to exclude {len(excluded_dirs)} directories")
        self.pytest_updater.update_config(excluded_dirs)
    
    def update_documentation(self, changes: ChangeReport) -> None:
        """
        Update project documentation to reflect test structure changes.
        
        Args:
            changes: Report of all changes made during cleanup
        """
        self.logger.info("Updating project documentation")
        self.doc_updater.update_docs(changes)


class MakefileUpdater(LoggerMixin):
    """Updates Makefile targets and references."""
    
    def __init__(self, config: CleanupConfig):
        self.config = config
        self.makefile_path = os.path.join(config.project_root, "Makefile")
    
    def update_targets(self, removed_files: List[str], adapted_files: List[str]) -> List[str]:
        """
        Update Makefile targets to reflect file changes.
        
        Args:
            removed_files: List of removed test files
            adapted_files: List of adapted test files
            
        Returns:
            List of changes made to the Makefile
        """
        if not os.path.exists(self.makefile_path):
            self.logger.warning("Makefile not found")
            return []
        
        try:
            with open(self.makefile_path, 'r') as f:
                content = f.read()
            
            original_content = content
            changes = []
            
            # Remove references to deleted files
            for removed_file in removed_files:
                content, file_changes = self._remove_file_references(content, removed_file)
                changes.extend(file_changes)
            
            # Add references to adapted files
            for adapted_file in adapted_files:
                content, file_changes = self._add_adapted_file_references(content, adapted_file)
                changes.extend(file_changes)
            
            # Update test targets to be more specific
            content, target_changes = self._optimize_test_targets(content)
            changes.extend(target_changes)
            
            # Write updated Makefile
            if content != original_content and not self.config.dry_run:
                with open(self.makefile_path, 'w') as f:
                    f.write(content)
                self.logger.info(f"Updated Makefile with {len(changes)} changes")
            elif content != original_content:
                self.logger.info(f"DRY RUN: Would update Makefile with {len(changes)} changes")
            
            return changes
            
        except Exception as e:
            self.logger.error(f"Failed to update Makefile: {e}")
            return []
    
    def _remove_file_references(self, content: str, removed_file: str) -> tuple[str, List[str]]:
        """Remove references to a deleted file from Makefile content."""
        changes = []
        lines = content.splitlines()
        modified_lines = []
        
        file_name = os.path.basename(removed_file)
        file_stem = os.path.splitext(file_name)[0]
        
        for line in lines:
            original_line = line
            
            # Remove direct file references
            if file_name in line or file_stem in line:
                # Remove the file from test target lists
                line = re.sub(rf'\s*{re.escape(file_name)}\s*', ' ', line)
                line = re.sub(rf'\s*{re.escape(file_stem)}\s*', ' ', line)
                line = re.sub(r'\s+', ' ', line).strip()  # Clean up whitespace
                
                if line != original_line:
                    changes.append(f"Removed {file_name} reference: {original_line.strip()} -> {line}")
            
            modified_lines.append(line)
        
        return '\n'.join(modified_lines), changes
    
    def _add_adapted_file_references(self, content: str, adapted_file: str) -> tuple[str, List[str]]:
        """Add references to adapted files in appropriate test targets."""
        changes = []
        
        # For now, adapted files will be discovered automatically by pytest
        # We could add explicit references if needed
        
        return content, changes
    
    def _optimize_test_targets(self, content: str) -> tuple[str, List[str]]:
        """Optimize test targets for better organization."""
        changes = []
        lines = content.splitlines()
        modified_lines = []
        
        for line in lines:
            original_line = line
            
            # Update test-all target to be more specific
            if line.strip().startswith('python -m pytest tests/') and 'test-all:' in content:
                # Ensure test-all runs all tests but excludes problematic ones
                if 'tests/' in line and not any(exclude in line for exclude in ['--ignore', '-k']):
                    line = line.replace('tests/', 'tests/ --ignore=tests/legacy_removed/')
                    if line != original_line:
                        changes.append(f"Optimized test-all target: {original_line.strip()} -> {line.strip()}")
            
            modified_lines.append(line)
        
        return '\n'.join(modified_lines), changes


class PytestConfigUpdater(LoggerMixin):
    """Updates pytest configuration files."""
    
    def __init__(self, config: CleanupConfig):
        self.config = config
        self.pytest_ini_path = os.path.join(config.project_root, "pytest.ini")
        self.pyproject_path = os.path.join(config.project_root, "pyproject.toml")
    
    def update_config(self, excluded_dirs: List[str]) -> List[str]:
        """
        Update pytest configuration to exclude directories.
        
        Args:
            excluded_dirs: Directories to exclude from test discovery
            
        Returns:
            List of changes made
        """
        changes = []
        
        # Try pytest.ini first
        if os.path.exists(self.pytest_ini_path):
            ini_changes = self._update_pytest_ini(excluded_dirs)
            changes.extend(ini_changes)
        
        # Try pyproject.toml if no pytest.ini
        elif os.path.exists(self.pyproject_path):
            toml_changes = self._update_pyproject_toml(excluded_dirs)
            changes.extend(toml_changes)
        
        else:
            # Create pytest.ini if neither exists
            ini_changes = self._create_pytest_ini(excluded_dirs)
            changes.extend(ini_changes)
        
        return changes
    
    def _update_pytest_ini(self, excluded_dirs: List[str]) -> List[str]:
        """Update pytest.ini configuration."""
        try:
            with open(self.pytest_ini_path, 'r') as f:
                content = f.read()
            
            original_content = content
            changes = []
            
            # Add or update testpaths and ignore patterns
            lines = content.splitlines()
            modified_lines = []
            in_pytest_section = False
            added_ignores = False
            
            for line in lines:
                if line.strip() == '[tool:pytest]' or line.strip() == '[pytest]':
                    in_pytest_section = True
                    modified_lines.append(line)
                elif line.startswith('[') and in_pytest_section:
                    # End of pytest section
                    if not added_ignores and excluded_dirs:
                        ignore_line = f"addopts = --ignore={' --ignore='.join(excluded_dirs)}"
                        modified_lines.append(ignore_line)
                        changes.append(f"Added ignore patterns: {ignore_line}")
                        added_ignores = True
                    in_pytest_section = False
                    modified_lines.append(line)
                elif in_pytest_section and line.startswith('addopts'):
                    # Update existing addopts
                    for excluded_dir in excluded_dirs:
                        if f"--ignore={excluded_dir}" not in line:
                            line += f" --ignore={excluded_dir}"
                    modified_lines.append(line)
                    changes.append(f"Updated addopts: {line}")
                    added_ignores = True
                else:
                    modified_lines.append(line)
            
            # Add pytest section if it doesn't exist
            if not in_pytest_section and not any('[pytest]' in line or '[tool:pytest]' in line for line in lines):
                modified_lines.extend([
                    '',
                    '[tool:pytest]',
                    f"addopts = --ignore={' --ignore='.join(excluded_dirs)}" if excluded_dirs else "addopts = -v"
                ])
                changes.append("Added [tool:pytest] section with ignore patterns")
            
            updated_content = '\n'.join(modified_lines)
            
            if updated_content != original_content and not self.config.dry_run:
                with open(self.pytest_ini_path, 'w') as f:
                    f.write(updated_content)
                self.logger.info(f"Updated pytest.ini with {len(changes)} changes")
            elif updated_content != original_content:
                self.logger.info(f"DRY RUN: Would update pytest.ini with {len(changes)} changes")
            
            return changes
            
        except Exception as e:
            self.logger.error(f"Failed to update pytest.ini: {e}")
            return []
    
    def _update_pyproject_toml(self, excluded_dirs: List[str]) -> List[str]:
        """Update pyproject.toml pytest configuration."""
        # For now, just log that we would update it
        # Full TOML parsing would require additional dependencies
        self.logger.info(f"Would update pyproject.toml to exclude {excluded_dirs}")
        return [f"Would exclude {dir} from pyproject.toml" for dir in excluded_dirs]
    
    def _create_pytest_ini(self, excluded_dirs: List[str]) -> List[str]:
        """Create new pytest.ini configuration."""
        try:
            content = f"""[tool:pytest]
testpaths = tests
addopts = -v --tb=short{' --ignore=' + ' --ignore='.join(excluded_dirs) if excluded_dirs else ''}
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
"""
            
            if not self.config.dry_run:
                with open(self.pytest_ini_path, 'w') as f:
                    f.write(content)
                self.logger.info("Created new pytest.ini configuration")
            else:
                self.logger.info("DRY RUN: Would create new pytest.ini configuration")
            
            return ["Created pytest.ini with ignore patterns"]
            
        except Exception as e:
            self.logger.error(f"Failed to create pytest.ini: {e}")
            return []


class DocumentationUpdater(LoggerMixin):
    """Updates project documentation."""
    
    def __init__(self, config: CleanupConfig):
        self.config = config
        self.readme_path = os.path.join(config.project_root, "README.md")
        self.contributing_path = os.path.join(config.project_root, "CONTRIBUTING.md")
        self.testing_path = os.path.join(config.project_root, "TESTING.md")
    
    def update_docs(self, changes: ChangeReport) -> List[str]:
        """
        Update project documentation to reflect test structure changes.
        
        Args:
            changes: Report of all changes made during cleanup
            
        Returns:
            List of documentation updates made
        """
        doc_changes = []
        
        # Update README.md
        if os.path.exists(self.readme_path):
            readme_changes = self._update_readme(changes)
            doc_changes.extend(readme_changes)
        
        # Update CONTRIBUTING.md
        if os.path.exists(self.contributing_path):
            contrib_changes = self._update_contributing(changes)
            doc_changes.extend(contrib_changes)
        
        # Update or create TESTING.md
        testing_changes = self._update_testing_docs(changes)
        doc_changes.extend(testing_changes)
        
        return doc_changes
    
    def _update_readme(self, changes: ChangeReport) -> List[str]:
        """Update README.md with test structure information."""
        try:
            with open(self.readme_path, 'r') as f:
                content = f.read()
            
            original_content = content
            doc_changes = []
            
            # Add or update testing section
            testing_section = f"""
## Testing

This project uses pytest for testing. The test suite has been cleaned up and optimized:

- **Migration-compatible tests**: Tests that work with the current adapter-based architecture
- **Adapted tests**: Legacy tests that have been adapted to use the migration adapter
- **Removed tests**: {len(getattr(changes, 'removed_tests', []))} redundant tests were removed during cleanup

### Running Tests

```bash
# Run all tests
make test-all

# Run only migration-compatible tests
make test

# Run specific test categories
pytest tests/test_migration_*.py  # Migration tests
pytest tests/test_integration_*.py  # Integration tests
```

### Test Structure

The test suite is organized as follows:
- `tests/test_migration_*.py` - Tests using the migration adapter
- `tests/test_integration_*.py` - Integration tests
- `tests/test_*_adapted.py` - Adapted legacy tests

"""
            
            # Insert or replace testing section
            if "## Testing" in content:
                # Replace existing testing section
                pattern = r'## Testing.*?(?=\n## |\n# |\Z)'
                content = re.sub(pattern, testing_section.strip(), content, flags=re.DOTALL)
                doc_changes.append("Updated existing Testing section in README.md")
            else:
                # Add testing section before the end
                content = content.rstrip() + "\n" + testing_section
                doc_changes.append("Added Testing section to README.md")
            
            if content != original_content and not self.config.dry_run:
                with open(self.readme_path, 'w') as f:
                    f.write(content)
                self.logger.info("Updated README.md with test structure information")
            elif content != original_content:
                self.logger.info("DRY RUN: Would update README.md with test structure information")
            
            return doc_changes
            
        except Exception as e:
            self.logger.error(f"Failed to update README.md: {e}")
            return []
    
    def _update_contributing(self, changes: ChangeReport) -> List[str]:
        """Update CONTRIBUTING.md with test guidelines."""
        try:
            with open(self.contributing_path, 'r') as f:
                content = f.read()
            
            original_content = content
            doc_changes = []
            
            # Add test guidelines section
            guidelines_section = """
## Test Guidelines

When contributing tests to this project:

1. **Use the migration adapter**: New tests should use `MigrationAdapter` instead of legacy modules
2. **Follow naming conventions**: 
   - `test_migration_*.py` for tests using the migration adapter
   - `test_integration_*.py` for integration tests
   - `test_*_adapted.py` for adapted legacy tests
3. **Run the full test suite**: Ensure `make test-all` passes before submitting
4. **Avoid redundant tests**: Check if similar functionality is already tested

### Test Categories

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions
- **Migration tests**: Test adapter functionality
- **Property tests**: Test universal properties with generated data

"""
            
            # Insert guidelines section
            if "## Test Guidelines" in content:
                pattern = r'## Test Guidelines.*?(?=\n## |\n# |\Z)'
                content = re.sub(pattern, guidelines_section.strip(), content, flags=re.DOTALL)
                doc_changes.append("Updated Test Guidelines section in CONTRIBUTING.md")
            else:
                content = content.rstrip() + "\n" + guidelines_section
                doc_changes.append("Added Test Guidelines section to CONTRIBUTING.md")
            
            if content != original_content and not self.config.dry_run:
                with open(self.contributing_path, 'w') as f:
                    f.write(content)
                self.logger.info("Updated CONTRIBUTING.md with test guidelines")
            elif content != original_content:
                self.logger.info("DRY RUN: Would update CONTRIBUTING.md with test guidelines")
            
            return doc_changes
            
        except Exception as e:
            self.logger.error(f"Failed to update CONTRIBUTING.md: {e}")
            return []
    
    def _update_testing_docs(self, changes: ChangeReport) -> List[str]:
        """Update or create TESTING.md with detailed test information."""
        try:
            testing_content = f"""# Testing Documentation

This document describes the testing strategy and structure for this project after the test suite cleanup.

## Test Suite Overview

The test suite has been cleaned up and optimized to work with the migration adapter architecture:

- **Total tests removed**: {len(getattr(changes, 'removed_tests', []))}
- **Total tests adapted**: {len(getattr(changes, 'adapted_tests', []))}
- **Migration-compatible tests**: Tests that work without modification

## Test Categories

### Migration Tests (`test_migration_*.py`)
Tests that use the `MigrationAdapter` to bridge legacy functionality with the new Chunkana library.

### Integration Tests (`test_integration_*.py`)
Tests that verify component interactions and end-to-end functionality.

### Adapted Tests (`test_*_adapted.py`)
Legacy tests that have been adapted to work with the new architecture while preserving their original test logic.

## Running Tests

### All Tests
```bash
make test-all
```

### Migration-Compatible Tests Only
```bash
make test
```

### Specific Test Categories
```bash
# Migration tests
pytest tests/test_migration_*.py -v

# Integration tests  
pytest tests/test_integration_*.py -v

# Adapted tests
pytest tests/test_*_adapted.py -v
```

### Test Coverage
```bash
make test-coverage
```

## Test Development Guidelines

1. **New tests should use MigrationAdapter**: Don't import legacy modules directly
2. **Follow naming conventions**: Use appropriate prefixes for test categories
3. **Preserve test intent**: When adapting tests, maintain the original test logic
4. **Add property tests**: Use Hypothesis for testing universal properties
5. **Test error conditions**: Ensure error handling is properly tested

## Test Infrastructure

- **pytest.ini**: Configuration for test discovery and execution
- **Makefile**: Test targets for different test categories
- **Migration adapter**: Bridge between legacy and new implementations

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure you're using `MigrationAdapter` instead of legacy imports
2. **Test discovery**: Check that test files follow naming conventions
3. **Assertion failures**: Verify that adapted tests preserve original assertions

### Getting Help

If you encounter issues with tests:
1. Check the test logs for specific error messages
2. Verify that the migration adapter is working correctly
3. Review the test adaptation documentation
4. Run tests in verbose mode for more details

## Test Cleanup History

This test suite was cleaned up on {self._get_current_date()} with the following changes:
- Removed redundant tests that duplicated existing coverage
- Adapted valuable legacy tests to use the migration adapter
- Updated test infrastructure for better organization
- Preserved unique test logic and assertions

For more details, see the cleanup reports in the project documentation.
"""
            
            if not self.config.dry_run:
                with open(self.testing_path, 'w') as f:
                    f.write(testing_content)
                self.logger.info("Created/updated TESTING.md documentation")
            else:
                self.logger.info("DRY RUN: Would create/update TESTING.md documentation")
            
            return ["Created/updated TESTING.md with comprehensive test documentation"]
            
        except Exception as e:
            self.logger.error(f"Failed to update TESTING.md: {e}")
            return []
    
    def _get_current_date(self) -> str:
        """Get current date for documentation."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")


# Define ChangeReport for type hints (simplified version)
class ChangeReport:
    """Simplified change report for documentation updates."""
    def __init__(self, removed_tests=None, adapted_tests=None):
        self.removed_tests = removed_tests or []
        self.adapted_tests = adapted_tests or []