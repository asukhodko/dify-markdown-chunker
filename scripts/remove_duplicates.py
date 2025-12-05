#!/usr/bin/env python3
"""
Remove duplicate and near-duplicate documents from corpus.
"""

import json
import shutil
from pathlib import Path
from collections import defaultdict

CORPUS_ROOT = Path(__file__).parent.parent / "tests" / "corpus"


def load_metadata():
    """Load metadata index."""
    metadata_path = CORPUS_ROOT / "metadata_index.json"
    with open(metadata_path) as f:
        return json.load(f)


def find_duplicates(metadata):
    """Find duplicate documents by content hash."""
    hash_groups = defaultdict(list)
    
    for doc in metadata:
        content_hash = doc.get("content_hash")
        if content_hash:
            hash_groups[content_hash].append(doc)
    
    # Return only groups with duplicates
    return {h: docs for h, docs in hash_groups.items() if len(docs) > 1}


def remove_duplicate_files(duplicates):
    """Remove duplicate files, keeping only the first one in each group."""
    removed_count = 0
    kept_files = set()
    
    print("\n=== Removing Duplicates ===\n")
    
    for hash_val, docs in duplicates.items():
        print(f"Hash {hash_val[:16]}... has {len(docs)} duplicates:")
        
        # Keep first, remove rest
        keep_doc = docs[0]
        print(f"  ✓ KEEP: {keep_doc['filename']} ({keep_doc['category']})")
        
        category = keep_doc['category']
        subcategory = keep_doc.get('subcategory')
        filename = keep_doc['filename']
        
        if subcategory:
            kept_path = CORPUS_ROOT / category / subcategory / filename
        else:
            kept_path = CORPUS_ROOT / category / filename
        
        kept_files.add(str(kept_path))
        
        # Remove duplicates
        for dup_doc in docs[1:]:
            category = dup_doc['category']
            subcategory = dup_doc.get('subcategory')
            filename = dup_doc['filename']
            
            if subcategory:
                file_path = CORPUS_ROOT / category / subcategory / filename
                meta_path = CORPUS_ROOT / category / subcategory / (filename + ".meta.json")
            else:
                file_path = CORPUS_ROOT / category / filename
                meta_path = CORPUS_ROOT / category / (filename + ".meta.json")
            
            # Remove files
            if file_path.exists():
                file_path.unlink()
                removed_count += 1
                print(f"  ✗ REMOVE: {filename}")
            
            if meta_path.exists():
                meta_path.unlink()
    
    print(f"\nRemoved {removed_count} duplicate files")
    return removed_count, kept_files


def rebuild_metadata_index():
    """Rebuild metadata index from remaining files."""
    print("\n=== Rebuilding Metadata Index ===\n")
    
    metadata_list = []
    
    for meta_file in CORPUS_ROOT.rglob("*.meta.json"):
        try:
            with open(meta_file) as f:
                metadata = json.load(f)
                metadata_list.append(metadata)
        except Exception as e:
            print(f"Warning: Failed to load {meta_file}: {e}")
    
    # Save updated index
    index_path = CORPUS_ROOT / "metadata_index.json"
    with open(index_path, "w") as f:
        json.dump(metadata_list, f, indent=2)
    
    print(f"Rebuilt index with {len(metadata_list)} documents")
    
    # Rebuild CSV
    import csv
    csv_path = CORPUS_ROOT / "metadata.csv"
    
    if metadata_list:
        fieldnames = [
            "filename", "category", "subcategory", "size_bytes", "line_count",
            "source", "code_ratio", "table_count", "list_count", "header_count",
            "expected_strategy"
        ]
        
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for meta in metadata_list:
                row = {k: meta.get(k, "") for k in fieldnames}
                writer.writerow(row)
        
        print(f"Rebuilt CSV with {len(metadata_list)} entries")
    
    return metadata_list


def main():
    """Main execution."""
    print("=" * 70)
    print("DUPLICATE REMOVAL")
    print("=" * 70)
    
    # Load metadata
    metadata = load_metadata()
    print(f"\nTotal documents: {len(metadata)}")
    
    # Find duplicates
    duplicates = find_duplicates(metadata)
    print(f"Duplicate hash groups: {len(duplicates)}")
    
    total_duplicates = sum(len(docs) - 1 for docs in duplicates.values())
    print(f"Total duplicate files: {total_duplicates}")
    
    if total_duplicates == 0:
        print("\n✓ No duplicates found!")
        return
    
    # Remove duplicates
    removed_count, kept_files = remove_duplicate_files(duplicates)
    
    # Rebuild metadata
    new_metadata = rebuild_metadata_index()
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Original documents: {len(metadata)}")
    print(f"Duplicates removed: {removed_count}")
    print(f"Remaining documents: {len(new_metadata)}")
    print(f"Unique documents: {len(set(d['content_hash'] for d in new_metadata))}")
    
    # Category breakdown
    from collections import Counter
    category_counts = Counter(d['category'] for d in new_metadata)
    
    print("\nRemaining by category:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count}")


if __name__ == "__main__":
    main()
