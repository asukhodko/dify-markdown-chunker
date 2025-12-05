#!/usr/bin/env python3
"""Regenerate corpus with highly diverse unique documents."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from corpus_builder.config import CORPUS_ROOT
from corpus_builder.diverse_generator import DiverseGenerator
import json

TARGETS = {
    "changelogs": 50,
    "debug_logs": 20,
    "engineering_blogs": 50,
    "github_readmes": 100,
    "mixed_content": 20,
    "nested_fencing": 20,
    "personal_notes": 30,
    "research_notes": 20,
    "technical_docs": 100,
}

def count_existing():
    """Count existing files per category."""
    counts = {}
    for category in TARGETS.keys():
        cat_dir = CORPUS_ROOT / category
        if cat_dir.exists():
            counts[category] = len(list(cat_dir.rglob("*.md")))
        else:
            counts[category] = 0
    return counts

def main():
    print("=" * 70)
    print("REGENERATING CORPUS WITH DIVERSE CONTENT")
    print("=" * 70)
    
    existing = count_existing()
    needed = {k: TARGETS[k] - existing[k] for k in TARGETS}
    
    print("\nCurrent status:")
    for cat in sorted(TARGETS.keys()):
        print(f"  {cat:20s}: {existing[cat]:3d}/{TARGETS[cat]:3d} (need {needed[cat]:3d})")
    
    total_needed = sum(max(0, n) for n in needed.values())
    print(f"\nTotal to generate: {total_needed}")
    
    if total_needed == 0:
        print("\n✓ Corpus is complete!")
        return
    
    # Generate for each category
    for category, count in needed.items():
        if count <= 0:
            continue
        
        print(f"\n{category.upper()}")
        print("-" * 70)
        
        output_dir = CORPUS_ROOT / category
        output_dir.mkdir(parents=True, exist_ok=True)
        
        gen = DiverseGenerator(output_dir, category)
        results = gen.generate(count)
        
        success = sum(1 for r in results if r.success)
        print(f"✓ Generated {success}/{count}")
    
    # Rebuild metadata
    print("\n" + "=" * 70)
    print("REBUILDING METADATA")
    print("=" * 70)
    
    metadata_list = []
    for meta_file in CORPUS_ROOT.rglob("*.meta.json"):
        try:
            with open(meta_file) as f:
                metadata_list.append(json.load(f))
        except:
            pass
    
    (CORPUS_ROOT / "metadata_index.json").write_text(json.dumps(metadata_list, indent=2))
    
    import csv
    with open(CORPUS_ROOT / "metadata.csv", "w", newline="") as f:
        if metadata_list:
            fieldnames = ["filename", "category", "subcategory", "size_bytes", "line_count",
                         "source", "code_ratio", "table_count", "list_count", "header_count",
                         "expected_strategy"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for meta in metadata_list:
                writer.writerow({k: meta.get(k, "") for k in fieldnames})
    
    print(f"✓ Metadata: {len(metadata_list)} documents")
    
    # Final summary
    final = count_existing()
    print("\n" + "=" * 70)
    print("FINAL CORPUS")
    print("=" * 70)
    for cat in sorted(TARGETS.keys()):
        status = "✓" if final[cat] >= TARGETS[cat] else "✗"
        print(f"  {status} {cat:20s}: {final[cat]:3d}/{TARGETS[cat]:3d}")
    print(f"\nTotal: {sum(final.values())} files")

if __name__ == "__main__":
    main()
