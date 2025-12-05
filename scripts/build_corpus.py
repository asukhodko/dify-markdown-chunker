#!/usr/bin/env python3
"""
Main script to build the test corpus.

This script orchestrates document collection and generation
to populate tests/corpus/ with 400+ markdown files.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from corpus_builder.config import CORPUS_ROOT, TARGETS
from corpus_builder.github_collector import GitHubCollector
from corpus_builder.synthetic_generator import SyntheticGenerator
from corpus_builder.base import CollectionResult


def setup_directories():
    """Create corpus directory structure."""
    print("Setting up directory structure...")
    
    # Main categories
    for category, config in TARGETS.items():
        category_dir = CORPUS_ROOT / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        # Subcategories
        if "subcategories" in config:
            for subcat in config["subcategories"].keys():
                (category_dir / subcat).mkdir(parents=True, exist_ok=True)
    
    print("✓ Directories created")


def collect_github_readmes(github_token: str = None) -> Dict[str, int]:
    """Collect GitHub README files."""
    print("\n" + "=" * 60)
    print("PHASE 1: Collecting GitHub READMEs")
    print("=" * 60)
    
    results = {}
    languages = ["python", "javascript", "go", "rust"]
    
    for lang in languages:
        output_dir = CORPUS_ROOT / "github_readmes" / lang
        collector = GitHubCollector(output_dir, lang, github_token)
        
        collected = collector.collect()
        success_count = sum(1 for r in collected if r.success)
        results[lang] = success_count
        
        print(f"Collected {success_count} {lang} READMEs")
    
    total = sum(results.values())
    print(f"\nTotal READMEs collected: {total}")
    
    return results


def generate_synthetic_documents() -> Dict[str, int]:
    """Generate all synthetic documents."""
    print("\n" + "=" * 60)
    print("PHASE 2: Generating Synthetic Documents")
    print("=" * 60)
    
    results = {}
    
    # Personal notes
    print("\nGenerating personal notes...")
    for subcat, count in [("unstructured", 10), ("journals", 10), ("cheatsheets", 10)]:
        output_dir = CORPUS_ROOT / "personal_notes" / subcat
        generator = SyntheticGenerator(output_dir, "personal_notes", subcat)
        generated = generator.generate(count)
        success_count = sum(1 for r in generated if r.success)
        results[f"personal_notes/{subcat}"] = success_count
        print(f"  Generated {success_count}/{count} {subcat}")
    
    # Debug logs
    print("\nGenerating debug logs...")
    output_dir = CORPUS_ROOT / "debug_logs"
    generator = SyntheticGenerator(output_dir, "debug_logs")
    generated = generator.generate(20)
    success_count = sum(1 for r in generated if r.success)
    results["debug_logs"] = success_count
    print(f"  Generated {success_count}/20 debug logs")
    
    # Nested fencing
    print("\nGenerating nested fencing examples...")
    output_dir = CORPUS_ROOT / "nested_fencing"
    generator = SyntheticGenerator(output_dir, "nested_fencing")
    generated = generator.generate(20)
    success_count = sum(1 for r in generated if r.success)
    results["nested_fencing"] = success_count
    print(f"  Generated {success_count}/20 nested fencing examples")
    
    # Research notes
    print("\nGenerating research notes...")
    output_dir = CORPUS_ROOT / "research_notes"
    generator = SyntheticGenerator(output_dir, "research_notes")
    generated = generator.generate(20)
    success_count = sum(1 for r in generated if r.success)
    results["research_notes"] = success_count
    print(f"  Generated {success_count}/20 research notes")
    
    # Mixed content
    print("\nGenerating mixed content...")
    output_dir = CORPUS_ROOT / "mixed_content"
    generator = SyntheticGenerator(output_dir, "mixed_content")
    generated = generator.generate(20)
    success_count = sum(1 for r in generated if r.success)
    results["mixed_content"] = success_count
    print(f"  Generated {success_count}/20 mixed content documents")
    
    total = sum(results.values())
    print(f"\nTotal synthetic documents: {total}")
    
    return results


def generate_report(github_results: Dict, synthetic_results: Dict):
    """Generate collection report."""
    print("\n" + "=" * 60)
    print("COLLECTION REPORT")
    print("=" * 60)
    
    # Count all files
    total_files = 0
    category_counts = {}
    
    for category_dir in CORPUS_ROOT.iterdir():
        if category_dir.is_dir() and not category_dir.name.startswith("."):
            count = sum(1 for f in category_dir.rglob("*.md"))
            category_counts[category_dir.name] = count
            total_files += count
    
    print(f"\nTotal files collected: {total_files}")
    print(f"Target: 400+")
    print(f"Status: {'✓ PASS' if total_files >= 400 else '✗ INSUFFICIENT'}")
    
    print("\nBreakdown by category:")
    for category, count in sorted(category_counts.items()):
        target = TARGETS.get(category, {}).get("total", "?")
        status = "✓" if count >= target else "✗"
        print(f"  {status} {category:20s}: {count:3d} / {target}")
    
    # Generate detailed report file
    report_path = CORPUS_ROOT / "COLLECTION_REPORT.md"
    
    report_content = f"""# Corpus Collection Report

Generated: {datetime.now().isoformat()}

## Summary

- **Total Files**: {total_files}
- **Target**: 400+
- **Status**: {'✓ PASS' if total_files >= 400 else '✗ INSUFFICIENT'}

## Category Breakdown

| Category | Collected | Target | Status |
|----------|-----------|--------|--------|
"""
    
    for category, count in sorted(category_counts.items()):
        target = TARGETS.get(category, {}).get("total", "?")
        status = "✓" if count >= target else "✗"
        report_content += f"| {category} | {count} | {target} | {status} |\n"
    
    report_content += f"""
## Collection Results

### GitHub READMEs

"""
    
    for lang, count in github_results.items():
        report_content += f"- {lang}: {count} files\n"
    
    report_content += "\n### Synthetic Documents\n\n"
    
    for category, count in synthetic_results.items():
        report_content += f"- {category}: {count} files\n"
    
    report_content += """
## Next Steps

1. Review collected documents for quality
2. Fill gaps in under-represented categories
3. Generate additional synthetic documents if needed
4. Run validation script to check distributions
"""
    
    report_path.write_text(report_content)
    print(f"\n✓ Detailed report saved to: {report_path}")
    
    # Generate metadata index
    print("\nGenerating metadata index...")
    generate_metadata_index()


def generate_metadata_index():
    """Generate master metadata index."""
    metadata_list = []
    
    for meta_file in CORPUS_ROOT.rglob("*.meta.json"):
        try:
            with open(meta_file) as f:
                metadata = json.load(f)
                metadata_list.append(metadata)
        except Exception as e:
            print(f"Warning: Failed to load {meta_file}: {e}")
    
    # Save as JSON
    index_path = CORPUS_ROOT / "metadata_index.json"
    with open(index_path, "w") as f:
        json.dump(metadata_list, f, indent=2)
    
    print(f"✓ Metadata index saved: {index_path} ({len(metadata_list)} files)")
    
    # Generate CSV for easy analysis
    import csv
    csv_path = CORPUS_ROOT / "metadata.csv"
    
    if metadata_list:
        fieldnames = [
            "filename",
            "category",
            "subcategory",
            "size_bytes",
            "line_count",
            "source",
            "code_ratio",
            "table_count",
            "list_count",
            "header_count",
            "expected_strategy",
        ]
        
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for meta in metadata_list:
                row = {k: meta.get(k, "") for k in fieldnames}
                writer.writerow(row)
        
        print(f"✓ Metadata CSV saved: {csv_path}")


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(description="Build test corpus for markdown chunker")
    parser.add_argument(
        "--github-token",
        help="GitHub personal access token (for higher rate limits)",
        default=os.environ.get("GITHUB_TOKEN"),
    )
    parser.add_argument(
        "--skip-github",
        action="store_true",
        help="Skip GitHub README collection",
    )
    parser.add_argument(
        "--skip-synthetic",
        action="store_true",
        help="Skip synthetic document generation",
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("CORPUS BUILDER")
    print("=" * 60)
    print(f"Output directory: {CORPUS_ROOT}")
    print(f"Target: 400+ documents")
    
    # Setup
    setup_directories()
    
    github_results = {}
    synthetic_results = {}
    
    # Phase 1: Collect GitHub READMEs
    if not args.skip_github:
        try:
            github_results = collect_github_readmes(args.github_token)
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Continuing to next phase...")
        except Exception as e:
            print(f"\n✗ Error in GitHub collection: {e}")
            print("Continuing to next phase...")
    else:
        print("\n⊘ Skipping GitHub README collection")
    
    # Phase 2: Generate synthetic documents
    if not args.skip_synthetic:
        try:
            synthetic_results = generate_synthetic_documents()
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
        except Exception as e:
            print(f"\n✗ Error in synthetic generation: {e}")
    else:
        print("\n⊘ Skipping synthetic document generation")
    
    # Generate report
    generate_report(github_results, synthetic_results)
    
    print("\n" + "=" * 60)
    print("CORPUS BUILD COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
