#!/usr/bin/env python3
"""
Find near-duplicates (similar structure/content even if hash differs).
"""

import json
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher

CORPUS_ROOT = Path(__file__).parent.parent / "tests" / "corpus"


def load_documents_by_category():
    """Load all documents grouped by category."""
    docs_by_category = defaultdict(list)
    
    for md_file in CORPUS_ROOT.rglob("*.md"):
        if md_file.name in ["README.md", "INDEX.md", "USAGE.md", 
                           "COMPLETION_SUMMARY.md", "COLLECTION_REPORT.md"]:
            continue
        
        try:
            content = md_file.read_text()
            category = md_file.parent.name
            
            # Handle subcategories
            if md_file.parent.parent.name in CORPUS_ROOT.name:
                category = md_file.parent.name
            else:
                category = md_file.parent.parent.name
            
            docs_by_category[category].append({
                "path": md_file,
                "content": content,
                "size": len(content),
            })
        except:
            pass
    
    return docs_by_category


def find_similar_documents(docs, similarity_threshold=0.7):
    """Find documents with similar content structure."""
    similar_groups = []
    
    for i, doc1 in enumerate(docs):
        group = [doc1]
        
        for j, doc2 in enumerate(docs[i+1:], i+1):
            # Skip if sizes are very different
            size_ratio = min(doc1["size"], doc2["size"]) / max(doc1["size"], doc2["size"])
            if size_ratio < 0.5:
                continue
            
            # Compare content structure (first 1000 chars)
            sample_size = min(1000, min(len(doc1["content"]), len(doc2["content"])))
            sample1 = doc1["content"][:sample_size]
            sample2 = doc2["content"][:sample_size]
            
            similarity = SequenceMatcher(None, sample1, sample2).ratio()
            
            if similarity >= similarity_threshold:
                group.append(doc2)
        
        if len(group) > 1:
            # Check if not already in another group
            paths_in_group = {str(d["path"]) for d in group}
            already_found = False
            
            for existing_group in similar_groups:
                existing_paths = {str(d["path"]) for d in existing_group}
                if paths_in_group & existing_paths:
                    already_found = True
                    break
            
            if not already_found:
                similar_groups.append(group)
    
    return similar_groups


def main():
    """Find and report near-duplicates."""
    print("=" * 70)
    print("NEAR-DUPLICATE DETECTION")
    print("=" * 70)
    
    docs_by_category = load_documents_by_category()
    
    all_near_dupes = {}
    total_near_dupes = 0
    
    for category, docs in docs_by_category.items():
        print(f"\nAnalyzing {category} ({len(docs)} documents)...")
        
        similar_groups = find_similar_documents(docs, similarity_threshold=0.7)
        
        if similar_groups:
            all_near_dupes[category] = similar_groups
            category_dupes = sum(len(group) - 1 for group in similar_groups)
            total_near_dupes += category_dupes
            
            print(f"  Found {len(similar_groups)} groups with {category_dupes} duplicates")
            
            for i, group in enumerate(similar_groups[:3]):  # Show first 3 groups
                print(f"\n  Group {i+1} ({len(group)} files):")
                for doc in group:
                    rel_path = doc["path"].relative_to(CORPUS_ROOT)
                    print(f"    - {rel_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Categories with near-duplicates: {len(all_near_dupes)}")
    print(f"Total near-duplicate files: {total_near_dupes}")
    
    if total_near_dupes > 0:
        print("\nRecommendation: Remove near-duplicates and regenerate with diverse content")
        
        # Save list of files to remove
        files_to_remove = []
        for category, groups in all_near_dupes.items():
            for group in groups:
                # Keep first, remove rest
                for doc in group[1:]:
                    files_to_remove.append(str(doc["path"].relative_to(CORPUS_ROOT)))
        
        output_file = CORPUS_ROOT / "near_duplicates_to_remove.txt"
        with open(output_file, "w") as f:
            for file_path in files_to_remove:
                f.write(file_path + "\n")
        
        print(f"\nList saved to: {output_file}")
        print(f"Files to remove: {len(files_to_remove)}")


if __name__ == "__main__":
    main()
