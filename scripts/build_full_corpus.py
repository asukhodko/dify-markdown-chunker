#!/usr/bin/env python3
"""
Build complete corpus with synthetic documents for all categories.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from corpus_builder.config import CORPUS_ROOT, TARGETS
from corpus_builder.synthetic_generator import SyntheticGenerator
from corpus_builder.comprehensive_generator import ComprehensiveGenerator
import json


def main():
    """Build complete corpus."""
    print("=" * 70)
    print("COMPREHENSIVE CORPUS BUILDER")
    print("=" * 70)
    print(f"Output: {CORPUS_ROOT}")
    print(f"Target: 410+ documents\n")
    
    all_results = {}
    total_generated = 0
    
    # 1. Technical Docs (100)
    print("\n1. Generating Technical Documentation (100 files)...")
    for subcat, count in [("kubernetes", 25), ("docker", 25), ("react", 25), ("aws", 25)]:
        output_dir = CORPUS_ROOT / "technical_docs" / subcat
        output_dir.mkdir(parents=True, exist_ok=True)
        gen = ComprehensiveGenerator(output_dir, "technical_docs", subcat)
        results = gen.generate(count)
        success = sum(1 for r in results if r.success)
        all_results[f"technical_docs/{subcat}"] = success
        total_generated += success
        print(f"  ✓ {subcat}: {success}/{count}")
    
    # 2. GitHub READMEs (100)
    print("\n2. Generating GitHub README-style Documents (100 files)...")
    for subcat, count in [("python", 25), ("javascript", 25), ("go", 25), ("rust", 25)]:
        output_dir = CORPUS_ROOT / "github_readmes" / subcat
        output_dir.mkdir(parents=True, exist_ok=True)
        gen = ComprehensiveGenerator(output_dir, "github_readmes", subcat)
        results = gen.generate(count)
        success = sum(1 for r in results if r.success)
        all_results[f"github_readmes/{subcat}"] = success
        total_generated += success
        print(f"  ✓ {subcat}: {success}/{count}")
    
    # 3. Changelogs (50)
    print("\n3. Generating Changelogs (50 files)...")
    output_dir = CORPUS_ROOT / "changelogs"
    output_dir.mkdir(parents=True, exist_ok=True)
    gen = ComprehensiveGenerator(output_dir, "changelogs")
    results = gen.generate(50)
    success = sum(1 for r in results if r.success)
    all_results["changelogs"] = success
    total_generated += success
    print(f"  ✓ changelogs: {success}/50")
    
    # 4. Engineering Blogs (50)
    print("\n4. Generating Engineering Blog Posts (50 files)...")
    output_dir = CORPUS_ROOT / "engineering_blogs"
    output_dir.mkdir(parents=True, exist_ok=True)
    gen = ComprehensiveGenerator(output_dir, "engineering_blogs")
    results = gen.generate(50)
    success = sum(1 for r in results if r.success)
    all_results["engineering_blogs"] = success
    total_generated += success
    print(f"  ✓ engineering_blogs: {success}/50")
    
    # 5. Personal Notes (30)
    print("\n5. Generating Personal Notes (30 files)...")
    for subcat, count in [("unstructured", 10), ("journals", 10), ("cheatsheets", 10)]:
        output_dir = CORPUS_ROOT / "personal_notes" / subcat
        output_dir.mkdir(parents=True, exist_ok=True)
        gen = SyntheticGenerator(output_dir, "personal_notes", subcat)
        results = gen.generate(count)
        success = sum(1 for r in results if r.success)
        all_results[f"personal_notes/{subcat}"] = success
        total_generated += success
        print(f"  ✓ {subcat}: {success}/{count}")
    
    # 6. Debug Logs (20)
    print("\n6. Generating Debug Logs (20 files)...")
    output_dir = CORPUS_ROOT / "debug_logs"
    output_dir.mkdir(parents=True, exist_ok=True)
    gen = SyntheticGenerator(output_dir, "debug_logs")
    results = gen.generate(20)
    success = sum(1 for r in results if r.success)
    all_results["debug_logs"] = success
    total_generated += success
    print(f"  ✓ debug_logs: {success}/20")
    
    # 7. Nested Fencing (20)
    print("\n7. Generating Nested Fencing Examples (20 files)...")
    output_dir = CORPUS_ROOT / "nested_fencing"
    output_dir.mkdir(parents=True, exist_ok=True)
    gen = SyntheticGenerator(output_dir, "nested_fencing")
    results = gen.generate(20)
    success = sum(1 for r in results if r.success)
    all_results["nested_fencing"] = success
    total_generated += success
    print(f"  ✓ nested_fencing: {success}/20")
    
    # 8. Research Notes (20)
    print("\n8. Generating Research Notes (20 files)...")
    output_dir = CORPUS_ROOT / "research_notes"
    output_dir.mkdir(parents=True, exist_ok=True)
    gen = SyntheticGenerator(output_dir, "research_notes")
    results = gen.generate(20)
    success = sum(1 for r in results if r.success)
    all_results["research_notes"] = success
    total_generated += success
    print(f"  ✓ research_notes: {success}/20")
    
    # 9. Mixed Content (20)
    print("\n9. Generating Mixed Content (20 files)...")
    output_dir = CORPUS_ROOT / "mixed_content"
    output_dir.mkdir(parents=True, exist_ok=True)
    gen = SyntheticGenerator(output_dir, "mixed_content")
    results = gen.generate(20)
    success = sum(1 for r in results if r.success)
    all_results["mixed_content"] = success
    total_generated += success
    print(f"  ✓ mixed_content: {success}/20")
    
    # Summary
    print("\n" + "=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print(f"\nTotal documents generated: {total_generated}")
    print(f"Target: 410")
    print(f"Status: {'✓ PASS' if total_generated >= 410 else '✗ INSUFFICIENT'}")
    
    # Generate metadata
    print("\nGenerating metadata index...")
    metadata_list = []
    
    for meta_file in CORPUS_ROOT.rglob("*.meta.json"):
        try:
            with open(meta_file) as f:
                metadata = json.load(f)
                metadata_list.append(metadata)
        except Exception as e:
            print(f"  Warning: Failed to load {meta_file}: {e}")
    
    # Save metadata
    index_path = CORPUS_ROOT / "metadata_index.json"
    with open(index_path, "w") as f:
        json.dump(metadata_list, f, indent=2)
    
    print(f"✓ Metadata index: {len(metadata_list)} files")
    
    # Generate CSV
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
        
        print(f"✓ Metadata CSV: {csv_path}")
    
    # Statistics
    print("\nStatistics:")
    total_size = sum(m.get("size_bytes", 0) for m in metadata_list)
    print(f"  Total size: {total_size / 1024 / 1024:.1f} MB")
    
    code_heavy = sum(1 for m in metadata_list if m.get("code_ratio", 0) >= 0.5)
    print(f"  Code-heavy docs: {code_heavy}")
    
    structural = sum(1 for m in metadata_list if m.get("header_count", 0) >= 3)
    print(f"  Structural docs: {structural}")
    
    print("\n✓ Corpus build complete!")


if __name__ == "__main__":
    main()
