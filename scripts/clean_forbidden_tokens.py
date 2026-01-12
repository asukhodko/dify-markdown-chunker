#!/usr/bin/env python3
"""Clean forbidden tokens from documentation files.

This script removes or replaces forbidden tokens (document_loader, embedding, vector_store)
from all documentation files as per the requirements.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


class TokenCleaner:
    """Cleans forbidden tokens from documentation files."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.cleaned_files: List[str] = []
        self.replacements_made = 0
        
        # Define replacements for forbidden tokens
        self.replacements = {
            # Replace document_loader with proper Dify UI terms
            r'\bdocument_loader\b': 'Data Source File → Doc Extractor',
            r'\bDocument Loader\b': 'Data Source File → Doc Extractor',
            r'\bDocumentLoader\b': 'Data Source File → Doc Extractor',
            
            # Remove embedding references completely
            r'\bembedding\b': '',
            r'\bEmbedding\b': '',
            r'\bembeddings\b': '',
            r'\bEmbeddings\b': '',
            
            # Remove vector_store references completely  
            r'\bvector_store\b': '',
            r'\bVector Store\b': '',
            r'\bVectorStore\b': '',
            r'\bvector store\b': '',
        }
        
        # Patterns that need special handling (complete line removal)
        self.line_removal_patterns = [
            r'.*embedding.*vector.*',
            r'.*vector.*embedding.*',
            r'.*embed.*chunks.*vector.*',
            r'.*store.*vectors.*',
        ]
    
    def clean_all_docs(self) -> bool:
        """Clean all documentation files."""
        print("🧹 Starting cleanup of forbidden tokens...")
        
        # Clean docs directory
        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            self._clean_directory(docs_dir)
        
        # Report results
        self._report_results()
        
        return len(self.cleaned_files) > 0
    
    def _clean_directory(self, directory: Path):
        """Clean all markdown files in directory recursively."""
        for md_file in directory.rglob("*.md"):
            self._clean_file(md_file)
    
    def _clean_file(self, file_path: Path):
        """Clean a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            cleaned_content = self._clean_content(original_content)
            
            # Only write if content changed
            if cleaned_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                
                relative_path = file_path.relative_to(self.project_root)
                self.cleaned_files.append(str(relative_path))
                print(f"  ✅ Cleaned {relative_path}")
        
        except Exception as e:
            print(f"  ❌ Error cleaning {file_path}: {e}")
    
    def _clean_content(self, content: str) -> str:
        """Clean content by removing/replacing forbidden tokens."""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Check if entire line should be removed
            should_remove_line = False
            for pattern in self.line_removal_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    should_remove_line = True
                    self.replacements_made += 1
                    break
            
            if should_remove_line:
                continue
            
            # Apply token replacements
            cleaned_line = line
            for pattern, replacement in self.replacements.items():
                if re.search(pattern, cleaned_line, re.IGNORECASE):
                    cleaned_line = re.sub(pattern, replacement, cleaned_line, flags=re.IGNORECASE)
                    self.replacements_made += 1
            
            # Clean up multiple spaces and empty parentheses/brackets
            cleaned_line = re.sub(r'\s+', ' ', cleaned_line)
            cleaned_line = re.sub(r'\(\s*\)', '', cleaned_line)
            cleaned_line = re.sub(r'\[\s*\]', '', cleaned_line)
            cleaned_line = cleaned_line.strip()
            
            # Skip lines that became empty or only punctuation
            if cleaned_line and not re.match(r'^[,.\-→\s]*$', cleaned_line):
                cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def _report_results(self):
        """Report cleanup results."""
        print("\n" + "="*60)
        print("🧹 CLEANUP RESULTS")
        print("="*60)
        
        if self.cleaned_files:
            print(f"\n✅ Cleaned {len(self.cleaned_files)} files:")
            for file_path in self.cleaned_files:
                print(f"  - {file_path}")
            
            print(f"\n📊 Total replacements made: {self.replacements_made}")
        else:
            print("\n✅ No files needed cleaning")


def main():
    """Main function."""
    project_root = Path(__file__).parent.parent
    cleaner = TokenCleaner(project_root)
    
    success = cleaner.clean_all_docs()
    
    if success:
        print("\n🎉 Token cleanup completed!")
        print("\nNext steps:")
        print("1. Run 'python scripts/verify_docs.py' to check results")
        print("2. Review cleaned files to ensure content still makes sense")
        print("3. Commit changes if satisfied")
    else:
        print("\n✅ No cleanup needed - all files are already clean!")
    
    return 0


if __name__ == "__main__":
    exit(main())