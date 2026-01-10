#!/usr/bin/env python3
"""
Script to clean up legacy tests and rename adapted tests.

This script:
1. Deletes all legacy test files (without _adapted suffix)
2. Renames adapted test files (removes _adapted suffix)
3. Preserves working migration-compatible tests
"""

import os
import shutil
from pathlib import Path

# Working tests that should be preserved (not deleted)
WORKING_TESTS = {
    'test_migration_adapter.py',
    'test_migration_regression.py', 
    'test_integration_basic.py',
    'test_error_handling.py',
    'test_dependencies.py',
    'test_entry_point.py',
    'test_manifest.py',
    'test_provider_class.py',
    'test_provider_yaml.py',
    'test_tool_yaml.py',
    'test_boundary_invariance.py',
    'test_hierarchical_filtering.py',
    'test_hierarchical_integration.py',
    'test_input_validator.py',
    'test_output_filter.py',
    'test_overlap_contract.py',
    'test_overlap_embedding.py',
    'test_parse_tool_flags_regression.py',
}

def find_all_test_files():
    """Find all test files in the tests directory."""
    test_files = []
    tests_dir = Path('tests')
    
    for file_path in tests_dir.rglob('test_*.py'):
        if file_path.is_file():
            test_files.append(file_path)
    
    return test_files

def categorize_test_files(test_files):
    """Categorize test files into working, legacy, and adapted."""
    working = []
    legacy = []
    adapted = []
    
    for file_path in test_files:
        filename = file_path.name
        
        if filename in WORKING_TESTS:
            working.append(file_path)
        elif filename.endswith('_adapted.py'):
            adapted.append(file_path)
        else:
            legacy.append(file_path)
    
    return working, legacy, adapted

def delete_legacy_tests(legacy_files):
    """Delete legacy test files."""
    print(f"Deleting {len(legacy_files)} legacy test files...")
    
    for file_path in legacy_files:
        try:
            os.remove(file_path)
            print(f"  ✓ Deleted: {file_path}")
        except Exception as e:
            print(f"  ✗ Failed to delete {file_path}: {e}")

def rename_adapted_tests(adapted_files):
    """Rename adapted test files (remove _adapted suffix)."""
    print(f"Renaming {len(adapted_files)} adapted test files...")
    
    for file_path in adapted_files:
        try:
            # Calculate new name (remove _adapted)
            new_name = file_path.name.replace('_adapted.py', '.py')
            new_path = file_path.parent / new_name
            
            # Rename the file
            shutil.move(str(file_path), str(new_path))
            print(f"  ✓ Renamed: {file_path} -> {new_path}")
        except Exception as e:
            print(f"  ✗ Failed to rename {file_path}: {e}")

def clean_empty_directories():
    """Remove empty directories after cleanup."""
    print("Cleaning up empty directories...")
    
    tests_dir = Path('tests')
    
    # Get all directories, sorted by depth (deepest first)
    all_dirs = []
    for dir_path in tests_dir.rglob('*'):
        if dir_path.is_dir() and dir_path != tests_dir:
            all_dirs.append(dir_path)
    
    # Sort by depth (deepest first) to remove nested empty dirs first
    all_dirs.sort(key=lambda p: len(p.parts), reverse=True)
    
    for dir_path in all_dirs:
        try:
            # Check if directory is empty (only contains __pycache__ or is completely empty)
            contents = list(dir_path.iterdir())
            non_cache_contents = [f for f in contents if f.name != '__pycache__']
            
            if not non_cache_contents:
                # Remove __pycache__ if it exists
                pycache = dir_path / '__pycache__'
                if pycache.exists():
                    shutil.rmtree(pycache)
                
                # Remove the directory if it's now empty
                if not list(dir_path.iterdir()):
                    os.rmdir(dir_path)
                    print(f"  ✓ Removed empty directory: {dir_path}")
        except Exception as e:
            print(f"  ✗ Failed to remove directory {dir_path}: {e}")

def main():
    """Main cleanup function."""
    print("🧹 Starting legacy test cleanup...")
    print("=" * 50)
    
    # Find all test files
    test_files = find_all_test_files()
    print(f"Found {len(test_files)} total test files")
    
    # Categorize files
    working, legacy, adapted = categorize_test_files(test_files)
    
    print(f"  - Working tests (preserve): {len(working)}")
    print(f"  - Legacy tests (delete): {len(legacy)}")
    print(f"  - Adapted tests (rename): {len(adapted)}")
    print()
    
    # Delete legacy tests
    if legacy:
        delete_legacy_tests(legacy)
        print()
    
    # Rename adapted tests
    if adapted:
        rename_adapted_tests(adapted)
        print()
    
    # Clean up empty directories
    clean_empty_directories()
    print()
    
    print("✅ Legacy test cleanup completed!")
    print("=" * 50)
    
    # Final summary
    remaining_files = find_all_test_files()
    print(f"Final result: {len(remaining_files)} test files remaining")
    
    # Check for any remaining _adapted files
    remaining_adapted = [f for f in remaining_files if f.name.endswith('_adapted.py')]
    if remaining_adapted:
        print(f"⚠️  Warning: {len(remaining_adapted)} _adapted files still exist:")
        for f in remaining_adapted:
            print(f"    {f}")
    else:
        print("✅ All _adapted files successfully renamed")

if __name__ == '__main__':
    main()