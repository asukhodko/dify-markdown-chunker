#!/usr/bin/env python3
"""
Compare markdown_chunker_v2 results against baseline.

This script compares the new v2 implementation against the saved baseline
to verify that chunking behavior is consistent.

**Feature: architecture-redesign**
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from markdown_chunker_v2 import MarkdownChunker, ChunkConfig


def load_baseline(baseline_path: str = "baseline.json") -> dict:
    """Load baseline results."""
    with open(baseline_path, "r", encoding="utf-8") as f:
        return json.load(f)


def chunk_corpus_v2(corpus_dir: str = "tests/fixtures/corpus") -> dict:
    """Chunk all documents in corpus using v2."""
    corpus_path = Path(corpus_dir)
    results = {}
    
    chunker = MarkdownChunker()
    
    for md_file in corpus_path.rglob("*.md"):
        relative_path = str(md_file.relative_to(corpus_path))
        
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        try:
            chunks = chunker.chunk(content)
            
            results[relative_path] = {
                "input_size": len(content),
                "input_lines": content.count("\n") + 1,
                "chunk_count": len(chunks),
                "chunks": [
                    {
                        "content": c.content[:100] + "..." if len(c.content) > 100 else c.content,
                        "start_line": c.start_line,
                        "end_line": c.end_line,
                        "size": c.size,
                        "strategy": c.strategy,
                    }
                    for c in chunks
                ],
                "total_output_size": sum(c.size for c in chunks),
            }
        except Exception as e:
            results[relative_path] = {"error": str(e)}
    
    return results


def compare_results(baseline: dict, v2_results: dict) -> dict:
    """Compare baseline and v2 results."""
    comparison = {
        "total_files": len(baseline),
        "matching_files": 0,
        "chunk_count_diff": [],
        "size_diff": [],
        "errors": [],
    }
    
    for file_path, baseline_data in baseline.items():
        if file_path not in v2_results:
            comparison["errors"].append(f"Missing in v2: {file_path}")
            continue
        
        v2_data = v2_results[file_path]
        
        if "error" in v2_data:
            comparison["errors"].append(f"Error in v2 for {file_path}: {v2_data['error']}")
            continue
        
        # Compare chunk counts
        baseline_count = baseline_data["chunk_count"]
        v2_count = v2_data["chunk_count"]
        count_diff = abs(baseline_count - v2_count)
        count_diff_pct = count_diff / baseline_count * 100 if baseline_count > 0 else 0
        
        comparison["chunk_count_diff"].append({
            "file": file_path,
            "baseline": baseline_count,
            "v2": v2_count,
            "diff": count_diff,
            "diff_pct": count_diff_pct,
        })
        
        # Compare total output size
        baseline_size = baseline_data["total_output_size"]
        v2_size = v2_data["total_output_size"]
        size_diff = abs(baseline_size - v2_size)
        size_diff_pct = size_diff / baseline_size * 100 if baseline_size > 0 else 0
        
        comparison["size_diff"].append({
            "file": file_path,
            "baseline": baseline_size,
            "v2": v2_size,
            "diff": size_diff,
            "diff_pct": size_diff_pct,
        })
        
        # Check if within tolerance
        if count_diff_pct <= 20 and size_diff_pct <= 20:  # 20% tolerance
            comparison["matching_files"] += 1
    
    return comparison


def print_report(comparison: dict) -> bool:
    """Print comparison report and return success status."""
    print("=" * 60)
    print("BASELINE COMPARISON REPORT")
    print("=" * 60)
    
    print(f"\nTotal files: {comparison['total_files']}")
    print(f"Matching files (within 20% tolerance): {comparison['matching_files']}")
    
    # Chunk count differences
    print("\n--- Chunk Count Differences ---")
    for item in sorted(comparison["chunk_count_diff"], key=lambda x: -x["diff_pct"]):
        status = "✓" if item["diff_pct"] <= 20 else "✗"
        print(f"{status} {item['file']}: {item['baseline']} -> {item['v2']} ({item['diff_pct']:.1f}%)")
    
    # Size differences
    print("\n--- Size Differences ---")
    for item in sorted(comparison["size_diff"], key=lambda x: -x["diff_pct"]):
        status = "✓" if item["diff_pct"] <= 20 else "✗"
        print(f"{status} {item['file']}: {item['baseline']} -> {item['v2']} ({item['diff_pct']:.1f}%)")
    
    # Errors
    if comparison["errors"]:
        print("\n--- Errors ---")
        for error in comparison["errors"]:
            print(f"✗ {error}")
    
    # Summary
    print("\n" + "=" * 60)
    success_rate = comparison["matching_files"] / comparison["total_files"] * 100
    print(f"Success rate: {success_rate:.1f}%")
    
    # Pass if >= 80% of files match within tolerance
    passed = success_rate >= 80
    print(f"Status: {'PASSED' if passed else 'FAILED'}")
    print("=" * 60)
    
    return passed


def main():
    """Main entry point."""
    print("Loading baseline...")
    baseline = load_baseline()
    
    print(f"Chunking corpus with v2 ({len(baseline)} files)...")
    v2_results = chunk_corpus_v2()
    
    print("Comparing results...")
    comparison = compare_results(baseline, v2_results)
    
    passed = print_report(comparison)
    
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
