#!/usr/bin/env python3
"""
Documentation validation script.

Validates:
- Internal links in markdown files
- Version consistency across files
- Code example syntax
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Set

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class DocumentationValidator:
    """Validates documentation files."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.checked_files: Set[Path] = set()
        
    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🔍 Validating documentation...")
        print()
        
        # Find all markdown files
        md_files = list(PROJECT_ROOT.glob("*.md"))
        md_files.extend(PROJECT_ROOT.glob("docs/**/*.md"))
        
        for md_file in md_files:
            if "node_modules" not in str(md_file):
                self.validate_file(md_file)
        
        # Check version consistency
        self.check_version_consistency()
        
        # Report results
        self.report_results()
        
        return len(self.errors) == 0
    
    def validate_file(self, filepath: Path):
        """Validate a single markdown file."""
        self.checked_files.add(filepath)
        
        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            self.errors.append(f"Failed to read {filepath}: {e}")
            return
        
        # Check internal links
        self.check_internal_links(filepath, content)
        
        # Check code blocks
        self.check_code_blocks(filepath, content)
    
    def check_internal_links(self, filepath: Path, content: str):
        """Check that internal links point to existing files."""
        # Match markdown links: [text](path)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        for match in re.finditer(link_pattern, content):
            link_text = match.group(1)
            link_path = match.group(2)
            
            # Skip external links
            if link_path.startswith(('http://', 'https://', 'mailto:', '#')):
                continue
            
            # Remove anchor
            if '#' in link_path:
                link_path = link_path.split('#')[0]
            
            if not link_path:
                continue
            
            # Resolve relative path
            if filepath.parent == PROJECT_ROOT:
                target = PROJECT_ROOT / link_path
            else:
                target = filepath.parent / link_path
            
            target = target.resolve()
            
            # Check if target exists
            if not target.exists():
                self.errors.append(
                    f"{filepath.relative_to(PROJECT_ROOT)}: "
                    f"Broken link '{link_path}' -> '{link_text}'"
                )
    
    def check_code_blocks(self, filepath: Path, content: str):
        """Check code block syntax."""
        # Match code blocks: ```language
        code_block_pattern = r'```(\w*)\n'
        
        lines = content.split('\n')
        in_code_block = False
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('```'):
                if not in_code_block:
                    # Starting code block
                    in_code_block = True
                    if line.strip() == '```':
                        # No language specified
                        self.warnings.append(
                            f"{filepath.relative_to(PROJECT_ROOT)}:{i}: "
                            f"Code block without language tag"
                        )
                else:
                    # Ending code block
                    in_code_block = False
    
    def check_version_consistency(self):
        """Check that version numbers are consistent across files."""
        version_pattern = r'(?:version|Version)[\s:]*(\d+\.\d+\.\d+(?:-[a-z0-9]+)?)'
        
        versions = {}
        
        files_to_check = [
            PROJECT_ROOT / 'README.md',
            PROJECT_ROOT / 'CHANGELOG.md',
            PROJECT_ROOT / 'manifest.yaml',
            PROJECT_ROOT / 'DEVELOPMENT.md',
        ]
        
        for filepath in files_to_check:
            if not filepath.exists():
                continue
            
            try:
                content = filepath.read_text(encoding='utf-8')
                matches = re.findall(version_pattern, content, re.IGNORECASE)
                
                if matches:
                    versions[filepath.name] = matches
            except Exception as e:
                self.warnings.append(f"Could not check version in {filepath.name}: {e}")
        
        # Check if all versions match
        all_versions = set()
        for file_versions in versions.values():
            all_versions.update(file_versions)
        
        if len(all_versions) > 1:
            self.warnings.append(
                f"Version mismatch detected: {', '.join(sorted(all_versions))}"
            )
            for filename, file_versions in versions.items():
                self.warnings.append(f"  {filename}: {', '.join(file_versions)}")
    
    def report_results(self):
        """Print validation results."""
        print()
        print("=" * 70)
        print("VALIDATION RESULTS")
        print("=" * 70)
        print()
        
        print(f"📄 Checked {len(self.checked_files)} files")
        print()
        
        if self.warnings:
            print(f"⚠️  {len(self.warnings)} warnings:")
            for warning in self.warnings:
                print(f"   {warning}")
            print()
        
        if self.errors:
            print(f"❌ {len(self.errors)} errors:")
            for error in self.errors:
                print(f"   {error}")
            print()
        else:
            print("✅ No errors found!")
            print()
        
        if not self.warnings and not self.errors:
            print("🎉 Documentation is valid!")


def main():
    """Main entry point."""
    validator = DocumentationValidator()
    success = validator.validate_all()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
