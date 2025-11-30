#!/usr/bin/env python3
"""
Analyze unused components after parser refactoring.

This script identifies:
1. Unused backward compatibility files
2. Orphaned test files
3. Deprecated functions with no callers
4. Duplicate test coverage
5. Skipped tests
"""

import os
import re
import sys
from collections import defaultdict
from pathlib import Path


def find_file_usage(filename, search_dir, exclude_self=True):
    """Find all files that import or reference a given file."""
    module_name = filename.replace(".py", "")
    results = []

    for py_file in Path(search_dir).rglob("*.py"):
        # Skip __pycache__ and .pyc files
        if "__pycache__" in str(py_file) or py_file.suffix == ".pyc":
            continue

        # Skip the file itself if requested
        if exclude_self and py_file.name == filename:
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for various import patterns
            patterns = [
                f"from.*{module_name}",
                f"import.*{module_name}",
                f"{module_name}\\.",  # Usage like module_name.function()
            ]

            for pattern in patterns:
                if re.search(pattern, content):
                    results.append(
                        {
                            "file": str(py_file.relative_to(search_dir)),
                            "pattern": pattern,
                        }
                    )
                    break
        except Exception as e:
            print(f"Warning: Could not read {py_file}: {e}", file=sys.stderr)

    return results


def find_function_usage(function_name, search_dir, exclude_file=None):
    """Find all usages of a function."""
    results = []

    for py_file in Path(search_dir).rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        if exclude_file and py_file.name == exclude_file:
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for function calls
            pattern = f"{function_name}\\s*\\("
            matches = re.finditer(pattern, content)

            for match in matches:
                # Get line number
                line_num = content[: match.start()].count("\n") + 1
                results.append(
                    {"file": str(py_file.relative_to(search_dir)), "line": line_num}
                )
        except Exception as e:
            print(f"Warning: Could not read {py_file}: {e}", file=sys.stderr)

    return results


def find_deprecated_functions(init_file):
    """Find all deprecated functions in __init__.py."""
    try:
        with open(init_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {init_file}: {e}", file=sys.stderr)
        return [], []

    # Find functions with NotImplementedError
    not_impl_pattern = r"def\s+(\w+)\s*\([^)]*\):[^}]*?raise\s+NotImplementedError"
    not_impl = re.findall(not_impl_pattern, content, re.DOTALL)

    # Find functions returning empty/stub values
    stub_pattern = r"def\s+(\w+)\s*\([^)]*\):[^}]*?return\s+\[\]"
    stubs = re.findall(stub_pattern, content, re.DOTALL)

    return not_impl, stubs


def find_skipped_tests(test_dir):
    """Find all skipped tests."""
    skipped = []

    for py_file in Path(test_dir).rglob("test_*.py"):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Find skip decorators and skip calls
            patterns = [
                r"@pytest\.mark\.skip\([^)]*\)",
                r"@pytest\.mark\.skipif\([^)]*\)",
                r"pytest\.skip\([^)]*\)",
            ]

            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1
                    skipped.append(
                        {
                            "file": str(py_file.relative_to(test_dir)),
                            "line": line_num,
                            "reason": match.group(0),
                        }
                    )
        except Exception as e:
            print(f"Warning: Could not read {py_file}: {e}", file=sys.stderr)

    return skipped


def find_test_files_for_modules(test_dir, module_names):
    """Find test files for given module names."""
    results = defaultdict(list)

    for module in module_names:
        pattern = f"*{module}*.py"
        test_files = list(Path(test_dir).rglob(pattern))

        for tf in test_files:
            if tf.name.startswith("test_"):
                results[module].append(str(tf.relative_to(test_dir)))

    return results


def main():
    # Determine base directory
    script_dir = Path(__file__).parent
    base_dir = script_dir.parent

    print("=" * 80)
    print("UNUSED COMPONENT ANALYSIS - Parser Refactoring Cleanup")
    print("=" * 80)
    print(f"\nBase directory: {base_dir}")

    # 1. Check backward compatibility files
    print("\n" + "=" * 80)
    print("1. BACKWARD COMPATIBILITY FILES")
    print("=" * 80)

    compat_files = ["enhanced_ast_builder.py", "markdown_ast.py", "fence_handler.py"]

    parser_dir = base_dir / "markdown_chunker" / "parser"

    for file in compat_files:
        file_path = parser_dir / file
        print(f"\n📄 {file}:")

        if not file_path.exists():
            print("  ❌ File does not exist")
            continue

        usage = find_file_usage(file, base_dir, exclude_self=True)

        if not usage:
            print("  ✅ NOT USED - Safe to delete")
        else:
            print(f"  ⚠️  Used in {len(usage)} file(s):")
            for u in usage[:10]:  # Show first 10
                print(f"     - {u['file']}")
            if len(usage) > 10:
                print(f"     ... and {len(usage) - 10} more")

    # 2. Find deprecated functions
    print("\n" + "=" * 80)
    print("2. DEPRECATED FUNCTIONS")
    print("=" * 80)

    init_file = parser_dir / "__init__.py"
    not_impl, stubs = find_deprecated_functions(init_file)

    print(f"\n🚫 Functions raising NotImplementedError: {len(not_impl)}")
    for func in not_impl:
        print(f"\n  Function: {func}()")
        usage = find_function_usage(func, base_dir, exclude_file="__init__.py")
        if not usage:
            print("    ✅ NOT USED - Safe to remove")
        else:
            print(f"    ⚠️  Used in {len(usage)} place(s):")
            for u in usage[:5]:
                print(f"       - {u['file']}:{u['line']}")

    print(f"\n📦 Stub functions (return []): {len(stubs)}")
    for func in stubs:
        print(f"\n  Function: {func}()")
        usage = find_function_usage(func, base_dir, exclude_file="__init__.py")
        if not usage:
            print("    ✅ NOT USED - Safe to remove")
        else:
            print(f"    ⚠️  Used in {len(usage)} place(s):")
            for u in usage[:5]:
                print(f"       - {u['file']}:{u['line']}")

    # 3. Find test files for deleted modules
    print("\n" + "=" * 80)
    print("3. ORPHANED TEST FILES")
    print("=" * 80)

    deleted_modules = [
        "api_validator",
        "ast_validator",
        "error_collector",
        "fenced_blocks",
        "input_validator",
        "interface",
        "line_converter",
        "nesting_resolver",
        "phantom_block",
        "simple_api",
        "stage2",
        "synchronized",
        "text_recovery",
        "benchmark",
    ]

    test_dir = base_dir / "tests"
    orphaned = find_test_files_for_modules(test_dir, deleted_modules)

    if not orphaned:
        print("\n✅ No orphaned test files found")
    else:
        for module, files in orphaned.items():
            print(f"\n📝 Tests for deleted module '{module}':")
            for tf in files:
                print(f"   - {tf}")

    # 4. Find skipped tests
    print("\n" + "=" * 80)
    print("4. SKIPPED TESTS")
    print("=" * 80)

    skipped = find_skipped_tests(test_dir)

    if not skipped:
        print("\n✅ No skipped tests found")
    else:
        print(f"\n⏭️  Found {len(skipped)} skipped test(s):")
        for skip in skipped[:20]:  # Show first 20
            print(f"   - {skip['file']}:{skip['line']}")
            print(f"     Reason: {skip['reason'][:60]}...")
        if len(skipped) > 20:
            print(f"   ... and {len(skipped) - 20} more")

    # 5. Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    total_unused = 0

    # Count unused compat files
    unused_compat = 0
    for file in compat_files:
        file_path = parser_dir / file
        if file_path.exists():
            usage = find_file_usage(file, base_dir, exclude_self=True)
            if not usage:
                unused_compat += 1

    # Count unused deprecated functions
    unused_funcs = 0
    for func in not_impl + stubs:
        usage = find_function_usage(func, base_dir, exclude_file="__init__.py")
        if not usage:
            unused_funcs += 1

    print("\n📊 Cleanup Opportunities:")
    print(
        f"   - Unused backward compatibility files: {unused_compat}/{len(compat_files)}"
    )
    print(
        f"   - Unused deprecated functions: {unused_funcs}/{len(not_impl) + len(stubs)}"
    )
    print(f"   - Orphaned test files: {sum(len(files) for files in orphaned.values())}")
    print(f"   - Skipped tests: {len(skipped)}")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Review the analysis results above")
    print("2. Decide which components to remove")
    print("3. Remove components incrementally")
    print("4. Run tests after each removal")
    print("5. Update documentation")


if __name__ == "__main__":
    main()
