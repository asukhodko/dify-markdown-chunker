#!/usr/bin/env python3
"""
Add typing imports to strategy files.
"""

from pathlib import Path

# Files that need typing imports
files_to_fix = {
    "markdown_chunker/chunker/strategies/code_strategy.py": [
        "Any",
        "Dict",
        "List",
        "Optional",
    ],
    "markdown_chunker/chunker/strategies/list_strategy.py": [
        "Any",
        "Dict",
        "List",
        "Optional",
    ],
    "markdown_chunker/chunker/strategies/structural_strategy.py": [
        "Any",
        "Dict",
        "List",
        "Optional",
    ],
    "markdown_chunker/chunker/strategies/table_strategy.py": [
        "Any",
        "Dict",
        "List",
        "Optional",
    ],
    "markdown_chunker/chunker/strategies/sentences_strategy.py": [
        "Any",
        "Dict",
        "List",
        "Optional",
    ],
}


def add_typing_import(file_path: Path, imports: list):
    """Add typing import to a file"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if typing import already exists
    if "from typing import" in content:
        print(f"  ⏭️  Skipped (already has typing): {file_path.name}")
        return False

    # Find the first import line
    lines = content.split("\n")
    import_idx = None

    for i, line in enumerate(lines):
        if line.startswith(("import ", "from ")) and "typing" not in line:
            import_idx = i
            break

    if import_idx is not None:
        # Add typing import before the first import
        typing_line = f"from typing import {', '.join(sorted(imports))}"
        lines.insert(import_idx, typing_line)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        print(f"  ✅ Fixed: {file_path.name}")
        return True

    return False


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    print("Adding typing imports to strategy files...")

    fixed = 0
    for file_rel_path, imports in files_to_fix.items():
        file_path = project_root / file_rel_path
        if file_path.exists():
            if add_typing_import(file_path, imports):
                fixed += 1

    print(f"\n✅ Fixed {fixed} files")


if __name__ == "__main__":
    main()
