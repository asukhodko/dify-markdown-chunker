#!/usr/bin/env python3
"""Generate synthetic large markdown files for streaming validation.

This script creates test files to validate streaming processing:
1. large_concat_1mb.md - 1MB file from concatenated corpus
2. large_concat_10mb.md - 10MB file from concatenated corpus
3. deep_fencing.md - Nested code blocks stress test
4. long_table.md - 5MB single table test
"""

import os
import sys
from pathlib import Path
from typing import List


def get_corpus_dir() -> Path:
    """Get the corpus directory path."""
    return Path(__file__).parent


def collect_existing_files() -> List[Path]:
    """Collect existing markdown files from corpus subdirectories."""
    corpus_dir = get_corpus_dir()
    md_files = []

    # Collect from subdirectories
    for subdir in corpus_dir.iterdir():
        if subdir.is_dir() and not subdir.name.startswith("."):
            md_files.extend(subdir.glob("*.md"))

    return sorted(md_files)


def generate_concat_file(target_size_mb: int, output_name: str) -> None:
    """Generate large concatenated file from existing corpus files."""
    corpus_dir = get_corpus_dir()
    output_path = corpus_dir / output_name
    target_bytes = target_size_mb * 1024 * 1024

    md_files = collect_existing_files()
    if not md_files:
        print("Warning: No markdown files found in corpus subdirectories")
        return

    print(f"Generating {output_name} (target: {target_size_mb}MB)...")

    with open(output_path, "w", encoding="utf-8") as out:
        current_size = 0
        file_index = 0

        while current_size < target_bytes:
            # Cycle through available files
            source_file = md_files[file_index % len(md_files)]
            file_index += 1

            # Add separator header
            separator = f"\n\n---\n# Source: {source_file.name}\n---\n\n"
            out.write(separator)
            current_size += len(separator.encode("utf-8"))

            # Read and write content
            try:
                with open(source_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    out.write(content)
                    current_size += len(content.encode("utf-8"))
            except Exception as e:
                print(f"Warning: Failed to read {source_file}: {e}")
                continue

            if file_index % 10 == 0:
                print(f"  Progress: {current_size / (1024*1024):.1f}MB")

    actual_size = os.path.getsize(output_path)
    print(f"  Created: {output_path} ({actual_size / (1024*1024):.2f}MB)")


def generate_deep_fencing() -> None:
    """Generate file with deeply nested code blocks."""
    corpus_dir = get_corpus_dir()
    output_path = corpus_dir / "deep_fencing.md"

    print("Generating deep_fencing.md...")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Deep Fencing Stress Test\n\n")
        f.write("This file tests nested and complex code fence scenarios.\n\n")

        # Section 1: Simple nested fences (markdown in code)
        f.write("## Section 1: Code Within Documentation\n\n")
        f.write("```markdown\n")
        f.write("# Example Documentation\n\n")
        f.write("Here's a code example:\n\n")
        f.write("```python\n")
        f.write("def hello():\n")
        f.write("    return 'world'\n")
        f.write("```\n")
        f.write("```\n\n")

        # Section 2: Multiple languages interleaved
        f.write("## Section 2: Multiple Languages\n\n")
        for lang in ["python", "javascript", "go", "rust", "java"]:
            f.write(f"### {lang.title()} Example\n\n")
            f.write(f"```{lang}\n")
            f.write(f"// Sample {lang} code\n")
            for i in range(20):
                f.write(f"function_{i}();\n")
            f.write("```\n\n")

        # Section 3: Backtick variations (3, 4, 5 backticks)
        f.write("## Section 3: Backtick Variations\n\n")
        f.write("Three backticks:\n\n")
        f.write("```\ncode block\n```\n\n")
        f.write("Four backticks:\n\n")
        f.write("````\ncode block with ``` inside\n````\n\n")
        f.write("Five backticks:\n\n")
        f.write("`````\ncode block with ```` inside\n`````\n\n")

        # Section 4: Tilde fences
        f.write("## Section 4: Tilde Fences\n\n")
        f.write("~~~python\n")
        f.write("def tilde_example():\n")
        f.write("    return True\n")
        f.write("~~~\n\n")

        # Section 5: Large code blocks
        f.write("## Section 5: Large Code Block\n\n")
        f.write("```python\n")
        for i in range(200):
            f.write(f"def function_{i}():\n")
            f.write(f"    '''Function number {i}'''\n")
            f.write(f"    result = {i} * 2\n")
            f.write("    return result\n\n")
        f.write("```\n\n")

        # Section 6: Mixed content with inline code
        f.write("## Section 6: Mixed Content\n\n")
        f.write("Text with `inline code` and **bold** and _italic_.\n\n")
        f.write("```python\n")
        f.write("# Comment with `backticks` inside\n")
        f.write("code_here()\n")
        f.write("```\n\n")
        f.write("More text with `more inline` code.\n\n")

    actual_size = os.path.getsize(output_path)
    print(f"  Created: {output_path} ({actual_size / 1024:.2f}KB)")


def generate_long_table() -> None:
    """Generate 5MB file with a single large table."""
    corpus_dir = get_corpus_dir()
    output_path = corpus_dir / "long_table.md"
    target_bytes = 5 * 1024 * 1024

    print("Generating long_table.md (target: 5MB)...")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Large Table Stress Test\n\n")
        f.write("This file contains a single very large table.\n\n")

        # Table header
        f.write("| ID | Name | Description | Value | Status | Timestamp |\n")
        f.write("|---|---|---|---|---|---|\n")

        # Generate rows until we hit target size
        row_num = 0
        current_size = 200  # Approximate header size

        while current_size < target_bytes:
            row = (
                f"| {row_num:06d} | "
                f"Item_{row_num} | "
                f"This is a description for item {row_num} with "
                f"some extra text to make it longer | "
                f"{row_num * 3.14159:.2f} | "
                f"{'Active' if row_num % 2 == 0 else 'Inactive'} | "
                f"2024-12-{(row_num % 28) + 1:02d} |\n"
            )
            f.write(row)
            current_size += len(row.encode("utf-8"))
            row_num += 1

            if row_num % 10000 == 0:
                mb_progress = current_size / (1024 * 1024)
                print(f"  Progress: {mb_progress:.1f}MB ({row_num} rows)")

    actual_size = os.path.getsize(output_path)
    size_mb = actual_size / (1024 * 1024)
    print(f"  Created: {output_path} ({size_mb:.2f}MB, {row_num} rows)")


def main() -> int:
    """Main entry point."""
    print("=== Generating Synthetic Large Files for Streaming Tests ===\n")

    # Generate concatenated files
    generate_concat_file(1, "large_concat_1mb.md")
    generate_concat_file(10, "large_concat_10mb.md")

    # Generate specialized test files
    generate_deep_fencing()
    generate_long_table()

    print("\n=== Generation Complete ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
