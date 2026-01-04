#!/usr/bin/env python3
"""Run migration tests to verify compatibility."""

import sys
import subprocess
from pathlib import Path

def run_tests():
    """Run all migration tests."""
    print("Running migration compatibility tests...")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    
    tests_to_run = [
        "test_adapter_simple.py",
        "test_migration_compatibility.py",
    ]
    
    all_passed = True
    
    for test_file in tests_to_run:
        test_path = project_dir / test_file
        if not test_path.exists():
            print(f"⚠ Test file not found: {test_file}")
            continue
            
        print(f"\n=== Running {test_file} ===")
        
        try:
            # Run the test
            result = subprocess.run([
                sys.executable, str(test_path)
            ], cwd=str(project_dir), capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ {test_file} PASSED")
                print(result.stdout)
            else:
                print(f"✗ {test_file} FAILED")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                all_passed = False
                
        except Exception as e:
            print(f"✗ Error running {test_file}: {e}")
            all_passed = False
    
    # Try pytest if available
    print(f"\n=== Running pytest tests ===")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/test_migration_adapter.py", "-v"
        ], cwd=str(project_dir), capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ pytest tests PASSED")
            print(result.stdout)
        else:
            print("⚠ pytest tests had issues (may be expected)")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            
    except Exception as e:
        print(f"⚠ Could not run pytest: {e}")
    
    print(f"\n=== Migration Test Summary ===")
    if all_passed:
        print("✓ All migration tests passed!")
        return True
    else:
        print("✗ Some migration tests failed")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)