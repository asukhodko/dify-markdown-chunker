#!/usr/bin/env python3
"""
Remove near-duplicate files and rebuild corpus with diverse content.
"""

from pathlib import Path
import shutil

CORPUS_ROOT = Path(__file__).parent.parent / "tests" / "corpus"


def main():
    """Remove near-duplicates."""
    print("=" * 70)
    print("REMOVING NEAR-DUPLICATES")
    print("=" * 70)
    
    # Load list
    list_file = CORPUS_ROOT / "near_duplicates_to_remove.txt"
    
    with open(list_file) as f:
        files_to_remove = [line.strip() for line in f if line.strip()]
    
    print(f"\nFiles to remove: {len(files_to_remove)}")
    
    # Remove files
    removed_count = 0
    
    for file_path in files_to_remove:
        full_path = CORPUS_ROOT / file_path
        meta_path = full_path.with_suffix(".md.meta.json")
        
        if full_path.exists():
            full_path.unlink()
            removed_count += 1
            
        if meta_path.exists():
            meta_path.unlink()
    
    print(f"Removed: {removed_count} files")
    
    # Clean up list file
    list_file.unlink()
    
    print("\n✓ Near-duplicates removed")
    print("\nNext step: Run regenerate script to create unique replacements")


if __name__ == "__main__":
    main()
