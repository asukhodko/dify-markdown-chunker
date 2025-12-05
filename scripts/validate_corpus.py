#!/usr/bin/env python3
"""
Validate the test corpus for quality and completeness.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

CORPUS_ROOT = Path(__file__).parent.parent / "tests" / "corpus"


def load_metadata() -> List[Dict]:
    """Load all metadata files."""
    metadata_index = CORPUS_ROOT / "metadata_index.json"
    if not metadata_index.exists():
        print("❌ metadata_index.json not found")
        return []
    
    with open(metadata_index) as f:
        return json.load(f)


def validate_file_count(metadata: List[Dict]) -> bool:
    """Validate total file count."""
    print("\n" + "="*70)
    print("FILE COUNT VALIDATION")
    print("="*70)
    
    total = len(metadata)
    target = 400
    
    print(f"Total files: {total}")
    print(f"Target: {target}+")
    
    if total >= target:
        print("✓ PASS: File count meets target")
        return True
    else:
        print(f"❌ FAIL: Only {total} files, need {target}+")
        return False


def validate_categories(metadata: List[Dict]) -> bool:
    """Validate category distribution."""
    print("\n" + "="*70)
    print("CATEGORY DISTRIBUTION")
    print("="*70)
    
    targets = {
        "technical_docs": 100,
        "github_readmes": 100,
        "changelogs": 50,
        "engineering_blogs": 50,
        "personal_notes": 30,
        "debug_logs": 20,
        "nested_fencing": 20,
        "research_notes": 20,
        "mixed_content": 20,
    }
    
    category_counts = defaultdict(int)
    for doc in metadata:
        category = doc.get("category", "unknown")
        category_counts[category] += 1
    
    all_pass = True
    
    print(f"\n{'Category':<25} {'Actual':<10} {'Target':<10} {'Status':<10}")
    print("-" * 70)
    
    for category, target in sorted(targets.items()):
        actual = category_counts[category]
        status = "✓ PASS" if actual >= target * 0.9 else "❌ FAIL"
        if actual < target * 0.9:
            all_pass = False
        
        print(f"{category:<25} {actual:<10} {target:<10} {status:<10}")
    
    return all_pass


def validate_size_distribution(metadata: List[Dict]) -> bool:
    """Validate document size distribution."""
    print("\n" + "="*70)
    print("SIZE DISTRIBUTION")
    print("="*70)
    
    size_ranges = {
        "tiny": (0, 1024),
        "small": (1024, 5120),
        "medium": (5120, 20480),
        "large": (20480, 102400),
        "very_large": (102400, float("inf")),
    }
    
    targets = {
        "tiny": 20,
        "small": 80,
        "medium": 160,
        "large": 120,
        "very_large": 30,
    }
    
    counts = defaultdict(int)
    
    for doc in metadata:
        size = doc.get("size_bytes", 0)
        for range_name, (min_size, max_size) in size_ranges.items():
            if min_size <= size < max_size:
                counts[range_name] += 1
                break
    
    print(f"\n{'Range':<15} {'Actual':<10} {'Target':<10} {'Percentage':<12} {'Status':<10}")
    print("-" * 70)
    
    total = len(metadata)
    all_pass = True
    
    for range_name in ["tiny", "small", "medium", "large", "very_large"]:
        actual = counts[range_name]
        target = targets[range_name]
        percentage = (actual / total * 100) if total > 0 else 0
        
        # Allow 50% tolerance for size distribution
        status = "✓ PASS" if actual >= target * 0.5 else "⚠ WARN"
        
        print(f"{range_name:<15} {actual:<10} {target:<10} {percentage:>6.1f}%     {status:<10}")
    
    return True  # Size distribution is informational, not a hard requirement


def validate_content_characteristics(metadata: List[Dict]) -> bool:
    """Validate content characteristic diversity."""
    print("\n" + "="*70)
    print("CONTENT CHARACTERISTICS")
    print("="*70)
    
    code_heavy = sum(1 for d in metadata if d.get("code_ratio", 0) >= 0.3)
    structural = sum(1 for d in metadata if d.get("header_count", 0) >= 3)
    table_rich = sum(1 for d in metadata if d.get("table_count", 0) >= 3)
    list_heavy = sum(1 for d in metadata if d.get("list_count", 0) >= 10)
    
    total = len(metadata)
    
    print(f"\n{'Characteristic':<30} {'Count':<10} {'Percentage':<12}")
    print("-" * 70)
    print(f"{'Code-heavy (ratio >= 30%)':<30} {code_heavy:<10} {code_heavy/total*100:>6.1f}%")
    print(f"{'Structural (headers >= 3)':<30} {structural:<10} {structural/total*100:>6.1f}%")
    print(f"{'Table-rich (tables >= 3)':<30} {table_rich:<10} {table_rich/total*100:>6.1f}%")
    print(f"{'List-heavy (lists >= 10)':<30} {list_heavy:<10} {list_heavy/total*100:>6.1f}%")
    
    # Check for diversity
    if code_heavy < 50:
        print("\n⚠ Warning: Low number of code-heavy documents")
    if structural < 100:
        print("⚠ Warning: Low number of structural documents")
    
    return True  # Informational


def validate_expected_strategies(metadata: List[Dict]) -> bool:
    """Validate expected strategy distribution."""
    print("\n" + "="*70)
    print("EXPECTED STRATEGY DISTRIBUTION")
    print("="*70)
    
    strategy_counts = defaultdict(int)
    for doc in metadata:
        strategy = doc.get("expected_strategy", "unknown")
        strategy_counts[strategy] += 1
    
    total = len(metadata)
    
    print(f"\n{'Strategy':<20} {'Count':<10} {'Percentage':<12}")
    print("-" * 70)
    
    for strategy, count in sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total * 100) if total > 0 else 0
        print(f"{strategy:<20} {count:<10} {percentage:>6.1f}%")
    
    # Check that we have documents for all strategies
    required_strategies = ["code_aware", "structural", "fallback"]
    missing = [s for s in required_strategies if strategy_counts[s] == 0]
    
    if missing:
        print(f"\n❌ Missing documents for strategies: {', '.join(missing)}")
        return False
    else:
        print("\n✓ All strategies represented")
        return True


def validate_file_integrity(metadata: List[Dict]) -> bool:
    """Validate that all files exist and are readable."""
    print("\n" + "="*70)
    print("FILE INTEGRITY")
    print("="*70)
    
    missing_files = []
    empty_files = []
    invalid_metadata = []
    
    for doc in metadata:
        filename = doc.get("filename")
        category = doc.get("category")
        subcategory = doc.get("subcategory")
        
        if not filename or not category:
            invalid_metadata.append(doc)
            continue
        
        # Construct file path
        if subcategory:
            file_path = CORPUS_ROOT / category / subcategory / filename
        else:
            file_path = CORPUS_ROOT / category / filename
        
        if not file_path.exists():
            missing_files.append(str(file_path))
            continue
        
        if file_path.stat().st_size == 0:
            empty_files.append(str(file_path))
    
    if missing_files:
        print(f"\n❌ Missing files: {len(missing_files)}")
        for f in missing_files[:5]:
            print(f"  - {f}")
        if len(missing_files) > 5:
            print(f"  ... and {len(missing_files) - 5} more")
    
    if empty_files:
        print(f"\n❌ Empty files: {len(empty_files)}")
        for f in empty_files[:5]:
            print(f"  - {f}")
    
    if invalid_metadata:
        print(f"\n❌ Invalid metadata entries: {len(invalid_metadata)}")
    
    if not missing_files and not empty_files and not invalid_metadata:
        print("\n✓ All files present and non-empty")
        return True
    else:
        return False


def validate_uniqueness(metadata: List[Dict]) -> bool:
    """Validate content uniqueness via hashes."""
    print("\n" + "="*70)
    print("CONTENT UNIQUENESS")
    print("="*70)
    
    hashes = defaultdict(list)
    
    for doc in metadata:
        content_hash = doc.get("content_hash")
        filename = doc.get("filename")
        
        if content_hash:
            hashes[content_hash].append(filename)
    
    duplicates = {h: files for h, files in hashes.items() if len(files) > 1}
    
    if duplicates:
        print(f"\n❌ Found {len(duplicates)} duplicate content hashes:")
        for hash_val, files in list(duplicates.items())[:5]:
            print(f"  Hash {hash_val[:16]}...:")
            for f in files:
                print(f"    - {f}")
        return False
    else:
        print(f"\n✓ All {len(hashes)} documents are unique")
        return True


def generate_summary_report(metadata: List[Dict]):
    """Generate final summary report."""
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    
    total_files = len(metadata)
    total_size = sum(d.get("size_bytes", 0) for d in metadata)
    total_lines = sum(d.get("line_count", 0) for d in metadata)
    
    avg_size = total_size / total_files if total_files > 0 else 0
    avg_lines = total_lines / total_files if total_files > 0 else 0
    
    print(f"\nTotal documents: {total_files}")
    print(f"Total size: {total_size / 1024 / 1024:.1f} MB")
    print(f"Total lines: {total_lines:,}")
    print(f"Average size: {avg_size / 1024:.1f} KB")
    print(f"Average lines: {avg_lines:.0f}")
    
    # Find extremes
    if metadata:
        largest = max(metadata, key=lambda d: d.get("size_bytes", 0))
        smallest = min(metadata, key=lambda d: d.get("size_bytes", 0))
        
        print(f"\nLargest: {largest.get('filename')} ({largest.get('size_bytes', 0) / 1024:.1f} KB)")
        print(f"Smallest: {smallest.get('filename')} ({smallest.get('size_bytes', 0)} bytes)")


def main():
    """Main validation."""
    print("="*70)
    print("CORPUS VALIDATION")
    print("="*70)
    print(f"Location: {CORPUS_ROOT}")
    
    # Load metadata
    metadata = load_metadata()
    if not metadata:
        print("\n❌ FAILED: No metadata found")
        sys.exit(1)
    
    # Run validations
    results = []
    
    results.append(("File Count", validate_file_count(metadata)))
    results.append(("Categories", validate_categories(metadata)))
    results.append(("Size Distribution", validate_size_distribution(metadata)))
    results.append(("Content Characteristics", validate_content_characteristics(metadata)))
    results.append(("Expected Strategies", validate_expected_strategies(metadata)))
    results.append(("File Integrity", validate_file_integrity(metadata)))
    results.append(("Content Uniqueness", validate_uniqueness(metadata)))
    
    # Summary
    generate_summary_report(metadata)
    
    # Final verdict
    print("\n" + "="*70)
    print("VALIDATION RESULTS")
    print("="*70)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{name:<30} {status}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "="*70)
    if all_passed:
        print("✓ CORPUS VALIDATION PASSED")
        print("="*70)
        sys.exit(0)
    else:
        print("❌ CORPUS VALIDATION FAILED")
        print("="*70)
        sys.exit(1)


if __name__ == "__main__":
    main()
