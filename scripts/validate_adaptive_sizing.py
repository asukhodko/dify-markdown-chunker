#!/usr/bin/env python3
"""
Validate adaptive sizing behavior on corpus files.

This script tests adaptive sizing on various corpus documents and verifies
that complexity scores and scale factors behave as expected.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from markdown_chunker_v2 import MarkdownChunker, ChunkConfig
from markdown_chunker_v2.config import AdaptiveSizeConfig


def test_corpus_file(file_path: Path, chunker: MarkdownChunker) -> dict:
    """Test a single corpus file and return complexity statistics."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = chunker.chunk(content)

    complexities = []
    scale_factors = []
    adaptive_sizes = []
    actual_sizes = []

    for chunk in chunks:
        if "content_complexity" in chunk.metadata:
            complexities.append(chunk.metadata["content_complexity"])
            scale_factors.append(chunk.metadata["size_scale_factor"])
            adaptive_sizes.append(chunk.metadata["adaptive_size"])
            actual_sizes.append(len(chunk.content))

    if not complexities:
        return None

    return {
        "file": file_path.name,
        "num_chunks": len(chunks),
        "num_adaptive": len(complexities),
        "min_complexity": min(complexities),
        "max_complexity": max(complexities),
        "avg_complexity": sum(complexities) / len(complexities),
        "min_scale": min(scale_factors),
        "max_scale": max(scale_factors),
        "avg_scale": sum(scale_factors) / len(scale_factors),
        "avg_adaptive_size": sum(adaptive_sizes) / len(adaptive_sizes),
        "avg_actual_size": sum(actual_sizes) / len(actual_sizes),
    }


def main():
    """Main validation script."""
    print("=" * 80)
    print("ADAPTIVE SIZING CORPUS VALIDATION")
    print("=" * 80)
    print()

    # Setup chunker with adaptive sizing
    config = ChunkConfig(
        use_adaptive_sizing=True,
        adaptive_config=AdaptiveSizeConfig(
            base_size=1500, min_scale=0.5, max_scale=1.5
        ),
    )
    chunker = MarkdownChunker(config)

    # Find corpus files
    corpus_dir = Path(__file__).parent.parent / "tests" / "fixtures" / "corpus"
    markdown_files = list(corpus_dir.rglob("*.md"))

    print(f"Found {len(markdown_files)} markdown files in corpus")
    print()

    # Test files
    results = []
    for file_path in sorted(markdown_files)[:10]:  # Test first 10 files
        result = test_corpus_file(file_path, chunker)
        if result:
            results.append(result)

    # Display results
    print(f"{'File':<30} {'Chunks':>7} {'Complexity':>12} {'Scale':>12} {'Size':>12}")
    print("-" * 80)

    for result in results:
        print(
            f"{result['file']:<30} "
            f"{result['num_adaptive']:>7} "
            f"{result['avg_complexity']:>12.2f} "
            f"{result['avg_scale']:>12.2f} "
            f"{result['avg_actual_size']:>12.0f}"
        )

    print()
    print("=" * 80)
    print("VALIDATION CHECKS")
    print("=" * 80)
    print()

    # Validation checks
    all_complexities = [r["avg_complexity"] for r in results]
    all_scales = [r["avg_scale"] for r in results]

    checks = []

    # Check 1: Complexity range
    min_c = min(all_complexities)
    max_c = max(all_complexities)
    checks.append(
        (
            "Complexity bounded [0.0, 1.0]",
            0.0 <= min_c <= max_c <= 1.0,
            f"Range: [{min_c:.2f}, {max_c:.2f}]",
        )
    )

    # Check 2: Scale factor range
    min_s = min(all_scales)
    max_s = max(all_scales)
    checks.append(
        (
            "Scale factor bounded [0.5, 1.5]",
            0.5 <= min_s <= max_s <= 1.5,
            f"Range: [{min_s:.2f}, {max_s:.2f}]",
        )
    )

    # Check 3: Variance in complexity
    variance = max_c - min_c
    checks.append(
        (
            "Complexity shows variance",
            variance > 0.1,
            f"Variance: {variance:.2f}",
        )
    )

    # Check 4: Variance in scale factors
    scale_variance = max_s - min_s
    checks.append(
        (
            "Scale factors show variance",
            scale_variance > 0.1,
            f"Variance: {scale_variance:.2f}",
        )
    )

    # Check 5: Average sizes reasonable
    avg_size = sum(r["avg_actual_size"] for r in results) / len(results)
    checks.append(
        (
            "Average chunk size reasonable",
            500 < avg_size < 5000,
            f"Avg: {avg_size:.0f} chars",
        )
    )

    # Print checks
    all_passed = True
    for check_name, passed, details in checks:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:>8}  {check_name:<35} {details}")
        if not passed:
            all_passed = False

    print()
    print("=" * 80)

    if all_passed:
        print("✓ ALL VALIDATION CHECKS PASSED")
        print("=" * 80)
        return 0
    else:
        print("✗ SOME VALIDATION CHECKS FAILED")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
