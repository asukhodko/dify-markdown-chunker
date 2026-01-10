#!/usr/bin/env python3
"""Final fixes for quality issues."""

import re
from pathlib import Path

def fix_file(file_path, content):
    """Write content to file."""
    file_path.write_text(content)
    print(f"Fixed {file_path}")

def main():
    base_dir = Path("tools/test_cleanup")
    
    # Fix processor.py indentation
    processor_file = base_dir / "processor.py"
    content = processor_file.read_text()
    content = content.replace("        TestFile,", "    TestFile,")
    fix_file(processor_file, content)
    
    # Fix test_categorizer_unit.py unused variables
    categorizer_file = base_dir / "test_categorizer_unit.py"
    content = categorizer_file.read_text()
    content = re.sub(r"        legacy_coverage = .*\n", "", content)
    content = re.sub(r"        migration_coverage = .*\n", "", content)
    fix_file(categorizer_file, content)
    
    # Fix updater.py long lines and unused variables
    updater_file = base_dir / "updater.py"
    content = updater_file.read_text()
    
    # Fix long ignore_opts line
    content = content.replace(
        "            ignore_opts = ' --ignore=' + ' --ignore='.join(excluded_dirs) if excluded_dirs else ''",
        "            if excluded_dirs:\n                ignore_opts = ' --ignore=' + ' --ignore='.join(excluded_dirs)\n            else:\n                ignore_opts = ''"
    )
    
    # Remove unused adapted_count
    content = re.sub(r"            adapted_count = len\(getattr\(changes, 'adapted_tests', \[\]\)\)\n", "", content)
    
    # Fix whitespace-only lines
    content = re.sub(r"\n[ \t]+\n", "\n\n", content)
    
    # Break long f-strings by using variables
    content = content.replace(
        'testing_section = f"""',
        'testing_section = f"""'
    )
    
    # Replace long docstrings with shorter versions
    long_docstring_pattern = r'(testing_content = f"""# Testing Documentation.*?""")'
    
    def replace_docstring(match):
        return '''testing_content = f"""# Testing Documentation

This document describes the testing strategy and structure for this project.

## Test Suite Overview

The test suite has been cleaned up and optimized:

- **Total tests removed**: {removed_count}
- **Total tests adapted**: {adapted_count}
- **Migration-compatible tests**: Tests that work without modification

## Running Tests

```bash
make test-all  # Run all tests
make test      # Run migration-compatible tests only
```

## Test Development Guidelines

1. Use `MigrationAdapter` for new tests
2. Follow naming conventions for test categories
3. Run full test suite before submitting
4. Avoid redundant tests

For detailed information, see project documentation.
"""'''
    
    content = re.sub(long_docstring_pattern, replace_docstring, content, flags=re.DOTALL)
    
    fix_file(updater_file, content)
    
    # Fix analyzer.py type issue
    analyzer_file = base_dir / "analyzer.py"
    content = analyzer_file.read_text()
    content = content.replace(
        "similarity = len(intersection) / len(union) if union else 0",
        "similarity = len(intersection) / len(union) if union else 0.0"
    )
    fix_file(analyzer_file, content)
    
    # Fix orchestrator.py type issue
    orchestrator_file = base_dir / "orchestrator.py"
    content = orchestrator_file.read_text()
    content = content.replace(
        "self.start_time = time.time()",
        "self.start_time: float = time.time()"
    )
    fix_file(orchestrator_file, content)
    
    print("All final fixes applied!")

if __name__ == "__main__":
    main()