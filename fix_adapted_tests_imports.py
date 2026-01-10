#!/usr/bin/env python3
"""Fix import errors in all adapted test files.

This script fixes the import errors in adapted test files by:
1. Replacing legacy imports with migration adapter imports
2. Updating test methods to use MigrationAdapter interface
3. Ensuring all adapted tests follow the working pattern
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


class ImportFixer:
    """Fixes import errors in adapted test files."""
    
    def __init__(self):
        self.fixes_applied = 0
        self.files_processed = 0
        
    def fix_imports_in_file(self, file_path: Path) -> bool:
        """Fix imports in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix 1: Replace legacy ChunkerConfig imports
            content = re.sub(
                r'from chunkana import ChunkerConfig as ChunkConfig',
                'from adapter import MigrationAdapter',
                content
            )
            
            content = re.sub(
                r'from chunkana import ChunkerConfig',
                'from adapter import MigrationAdapter',
                content
            )
            
            # Fix 2: Replace other legacy imports
            content = re.sub(
                r'from markdown_chunker_v2.*',
                'from adapter import MigrationAdapter',
                content
            )
            
            content = re.sub(
                r'from markdown_chunker.*',
                'from adapter import MigrationAdapter',
                content
            )
            
            # Fix 3: Replace MarkdownChunker imports if not already using adapter
            if 'from adapter import MarkdownChunker' not in content:
                content = re.sub(
                    r'from adapter import MarkdownChunker',
                    'from adapter import MigrationAdapter',
                    content
                )
            
            # Fix 4: Replace ChunkerConfig usage with adapter.build_chunker_config()
            content = re.sub(
                r'ChunkerConfig\(',
                'self.adapter.build_chunker_config(',
                content
            )
            
            content = re.sub(
                r'ChunkConfig\(',
                'self.adapter.build_chunker_config(',
                content
            )
            
            # Fix 5: Add setup_method if missing
            if 'def setup_method(self):' not in content and 'class Test' in content:
                # Find the first class and add setup_method
                class_match = re.search(r'(class Test[^:]*:)', content)
                if class_match:
                    class_line = class_match.group(1)
                    setup_method = '''
    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = MigrationAdapter()
'''
                    content = content.replace(
                        class_line,
                        class_line + setup_method
                    )
            
            # Fix 6: Replace direct chunker usage with adapter
            content = re.sub(
                r'chunker = MarkdownChunker\(\)',
                'self.adapter = MigrationAdapter()',
                content
            )
            
            content = re.sub(
                r'chunker\.chunk\(',
                'self.adapter.run_chunking(',
                content
            )
            
            # Fix 7: Update method signatures for adapter interface
            content = re.sub(
                r'\.run_chunking\(([^,)]+),\s*([^,)]+)\)',
                r'.run_chunking(input_text=\1, config=\2, include_metadata=True)',
                content
            )
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def find_adapted_test_files(self, root_dir: Path) -> List[Path]:
        """Find all adapted test files that need fixing."""
        adapted_files = []
        
        for test_file in root_dir.rglob("*.py"):
            if "test_" in test_file.name and test_file.is_file():
                try:
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if it's an adapted file with import issues
                    has_legacy_imports = any([
                        'from chunkana import ChunkerConfig' in content,
                        'ChunkerConfig(' in content,
                        'ChunkConfig(' in content,
                        'from markdown_chunker' in content,
                    ])
                    
                    if has_legacy_imports:
                        adapted_files.append(test_file)
                        
                except Exception:
                    continue
        
        return adapted_files
    
    def fix_all_files(self, root_dir: Path) -> None:
        """Fix all adapted test files."""
        adapted_files = self.find_adapted_test_files(root_dir)
        
        print(f"Found {len(adapted_files)} files with import issues")
        
        for file_path in adapted_files:
            print(f"Processing: {file_path}")
            if self.fix_imports_in_file(file_path):
                self.fixes_applied += 1
                print(f"  ✅ Fixed imports")
            else:
                print(f"  ⚠️  No changes needed")
            
            self.files_processed += 1
        
        print(f"\nSummary:")
        print(f"  Files processed: {self.files_processed}")
        print(f"  Files fixed: {self.fixes_applied}")


def main():
    """Main function."""
    root_dir = Path("tests")
    
    if not root_dir.exists():
        print("Error: tests directory not found")
        return
    
    fixer = ImportFixer()
    fixer.fix_all_files(root_dir)


if __name__ == "__main__":
    main()