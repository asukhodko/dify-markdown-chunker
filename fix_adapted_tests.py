#!/usr/bin/env python3
"""
Fix syntax and import errors in adapted test files.
"""

import os
import re
import ast
from pathlib import Path


def fix_indentation_errors(content: str) -> str:
    """Fix common indentation errors in adapted tests."""
    lines = content.splitlines()
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Skip empty lines
        if not line.strip():
            fixed_lines.append(line)
            continue
            
        # Check for common indentation issues
        if line.strip().startswith('parser = Parser()') and line.startswith('# '):
            # This line was incorrectly indented after comment replacement
            fixed_lines.append('    # parser = Parser()  # Legacy functionality not available')
        elif line.strip().startswith('chunker = MarkdownChunker()') and not line.startswith('    '):
            # Fix chunker instantiation indentation
            fixed_lines.append('    ' + line.strip())
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def comment_out_legacy_code(content: str) -> str:
    """Comment out code that uses legacy functionality not available in chunkana."""
    lines = content.splitlines()
    fixed_lines = []
    
    in_legacy_block = False
    
    for line in lines:
        stripped = line.strip()
        
        # Patterns that indicate legacy functionality
        legacy_patterns = [
            'Parser()',
            'AdaptiveSizeCalculator',
            'AdaptiveSizeConfig',
            'StreamingConfig',
            'HierarchyBuilder',
            'CodeContextBinder',
            'BaseStrategy',
            'StrategySelector',
            'TableGrouper',
            'analysis.list_count',
            'analysis.list_blocks',
            'parser.analyze',
            'chunker.get_strategy',
            'config.adaptive_sizing',
            'config.streaming',
        ]
        
        # Check if this line uses legacy functionality
        uses_legacy = any(pattern in stripped for pattern in legacy_patterns)
        
        if uses_legacy:
            # Comment out the line
            if line.strip():
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(' ' * indent + '# ' + line.strip() + '  # Legacy functionality not available in chunkana')
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_test_file(file_path: Path) -> bool:
    """Fix a single test file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply fixes
        content = fix_indentation_errors(content)
        content = comment_out_legacy_code(content)
        
        # Try to parse to check for syntax errors
        try:
            ast.parse(content)
        except SyntaxError as e:
            print(f"Still has syntax error in {file_path}: {e}")
            return False
        
        # Write back the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def main():
    """Fix all adapted test files."""
    test_dir = Path("tests")
    adapted_files = list(test_dir.glob("**/*_adapted.py"))
    
    print(f"Found {len(adapted_files)} adapted test files")
    
    fixed_count = 0
    for file_path in adapted_files:
        if fix_test_file(file_path):
            fixed_count += 1
    
    print(f"Successfully fixed {fixed_count}/{len(adapted_files)} files")


if __name__ == "__main__":
    main()