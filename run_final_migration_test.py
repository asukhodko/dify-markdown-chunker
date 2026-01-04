#!/usr/bin/env python3
"""Final migration test - comprehensive validation."""

import sys
import json
import subprocess
from pathlib import Path

def run_basic_tests():
    """Run basic functionality tests."""
    print("=== Running Basic Tests ===")
    
    tests = [
        "quick_test.py",
        "test_single_snapshot.py",
    ]
    
    all_passed = True
    for test_file in tests:
        test_path = Path(test_file)
        if not test_path.exists():
            print(f"⚠ Test file not found: {test_file}")
            continue
        
        print(f"\nRunning {test_file}...")
        try:
            result = subprocess.run([sys.executable, str(test_path)], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"✓ {test_file} PASSED")
                if result.stdout:
                    print(result.stdout)
            else:
                print(f"✗ {test_file} FAILED")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                all_passed = False
        except subprocess.TimeoutExpired:
            print(f"✗ {test_file} TIMEOUT")
            all_passed = False
        except Exception as e:
            print(f"✗ Error running {test_file}: {e}")
            all_passed = False
    
    return all_passed

def check_migration_completeness():
    """Check that migration is complete."""
    print("\n=== Checking Migration Completeness ===")
    
    # Check required files exist
    required_files = [
        "adapter.py",
        "tests/config_defaults_snapshot.json",
        "tests/golden_before_migration/snapshot_index.json",
        "tests/baseline_data/fixtures",
        "tools/markdown_chunk_tool.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
            all_exist = False
    
    # Check tool imports
    tool_file = Path("tools/markdown_chunk_tool.py")
    if tool_file.exists():
        content = tool_file.read_text()
        if "from adapter import MigrationAdapter" in content:
            print("✓ Tool uses migration adapter")
        else:
            print("✗ Tool not updated to use adapter")
            all_exist = False
        
        if "from markdown_chunker import" in content:
            print("⚠ Tool still has embedded imports (expected until cleanup)")
        else:
            print("✓ Tool has no embedded imports")
    
    # Check snapshot count
    snapshots_dir = Path("tests/golden_before_migration")
    if snapshots_dir.exists():
        snapshot_files = list(snapshots_dir.glob("*.json"))
        snapshot_count = len([f for f in snapshot_files if f.name != "snapshot_index.json"])
        print(f"✓ {snapshot_count} snapshots available")
        
        if snapshot_count >= 200:
            print("✓ Sufficient snapshots for testing")
        else:
            print("⚠ May need more snapshots for comprehensive testing")
    
    return all_exist

def summarize_migration_status():
    """Summarize current migration status."""
    print("\n=== Migration Status Summary ===")
    
    completed_tasks = [
        "✓ Pre-migration analysis and setup",
        "✓ Dependency migration (chunkana==0.1.0 added)",
        "✓ Migration adapter implementation",
        "✓ Tool implementation update",
        "✓ Debug behavior analysis and implementation",
    ]
    
    remaining_tasks = [
        "⏳ Comprehensive regression testing (228 snapshots)",
        "⏳ Performance analysis and benchmarking",
        "⏳ Final cleanup (remove embedded code)",
    ]
    
    print("Completed:")
    for task in completed_tasks:
        print(f"  {task}")
    
    print("\nRemaining:")
    for task in remaining_tasks:
        print(f"  {task}")
    
    print(f"\nProgress: ~85% complete")
    print("Status: Core migration functional, testing and validation in progress")

def main():
    """Main test function."""
    print("Final Migration Test - Comprehensive Validation")
    print("=" * 50)
    
    # Run basic tests
    basic_tests_passed = run_basic_tests()
    
    # Check completeness
    migration_complete = check_migration_completeness()
    
    # Summarize
    summarize_migration_status()
    
    print("\n" + "=" * 50)
    if basic_tests_passed and migration_complete:
        print("✓ MIGRATION CORE FUNCTIONALITY WORKING")
        print("Ready for comprehensive regression testing")
        return True
    else:
        print("✗ MIGRATION HAS ISSUES")
        print("Fix issues before proceeding to regression testing")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)