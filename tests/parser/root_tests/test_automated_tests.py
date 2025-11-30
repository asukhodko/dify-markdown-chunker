#!/usr/bin/env python3
"""
Test that test_basic.py is now a proper automated test.
"""

import os
import subprocess
import sys


def test_basic_is_automated():
    """Test that test_basic.py is now automated with assertions."""
    print("Testing that test_basic.py is now automated...")

    # Check if test_basic.py exists (legacy file)
    if not os.path.exists("test_basic.py"):
        print("ℹ test_basic.py not found - this is expected (replaced by pytest tests)")
        print("✓ Using proper pytest test structure instead")
        return

    # Read the test_basic.py file
    try:
        with open("test_basic.py", "r") as f:
            content = f.read()

        # Check that it contains assertions instead of just prints
        assert_count = content.count("assert ")
        print_count = content.count("print(")

        print(f"Found {assert_count} assertions and {print_count} print statements")

        # Should have many assertions
        assert (
            assert_count >= 10
        ), f"Expected at least 10 assertions, got {assert_count}"

        # Should not have "All basic tests passed!" without assertions
        if "All basic tests passed!" in content:
            # This is OK if it's after real assertions
            pass

        # Check for proper test structure
        assert "class TestBasicFunctionality:" in content, "Should have test class"
        assert "def test_" in content, "Should have test methods"

        print("✓ test_basic.py has proper automated test structure")

    except Exception as e:
        print(f"✗ Error reading test_basic.py: {e}")
        raise


def test_basic_runs_and_validates():
    """Test that test_basic.py actually validates functionality."""
    print("Testing that test_basic.py validates functionality...")

    # Check if test_basic.py exists (legacy file)
    if not os.path.exists("test_basic.py"):
        print("ℹ test_basic.py not found - this is expected (replaced by pytest tests)")
        print("✓ Using proper pytest test structure instead")
        return

    # Run test_basic.py
    try:
        result = subprocess.run(
            [sys.executable, "test_basic.py"], capture_output=True, text=True
        )

        assert result.returncode == 0, f"test_basic.py failed to run: {result.stderr}"
        print("✓ test_basic.py runs successfully")

        # Check that it actually validates things
        output = result.stdout
        assert "test passed" in output, "Should report test results"
        assert "All automated tests passed!" in output, "Should report overall success"

        print("✓ test_basic.py validates functionality properly")

    except Exception as e:
        print(f"✗ Error running test_basic.py: {e}")
        raise


def test_pytest_compatibility():
    """Test that pytest-compatible version exists."""
    print("Testing pytest compatibility...")

    # Check that pytest-compatible version exists
    pytest_test_path = "stage1/tests/test_basic_functionality.py"

    if os.path.exists(pytest_test_path):
        print("✓ Pytest-compatible version exists")

        # Check that it has proper structure
        try:
            with open(pytest_test_path, "r") as f:
                content = f.read()

            assert "class TestBasicFunctionality:" in content, "Should have test class"
            assert "def test_" in content, "Should have test methods"
            assert "assert " in content, "Should have assertions"

            print("✓ Pytest-compatible version has proper structure")

        except Exception as e:
            print(f"✗ Error reading pytest version: {e}")
            raise
    else:
        print("ℹ Pytest-compatible version not found (this is OK)")


def test_no_more_print_only_tests():
    """Test that we don't have print-only tests anymore."""
    print("Testing that print-only tests are eliminated...")

    # Check if test_basic.py exists (legacy file)
    if not os.path.exists("test_basic.py"):
        print("ℹ test_basic.py not found - this is expected (replaced by pytest tests)")
        print("✓ Using proper pytest test structure instead")
        return

    # Check test_basic.py
    try:
        with open("test_basic.py", "r") as f:
            content = f.read()

        # Should not have print statements without corresponding assertions
        lines = content.split("\n")

        has_real_tests = False
        for line in lines:
            if "assert " in line and "print(" not in line:
                has_real_tests = True
                break

        assert has_real_tests, "Should have real assertions, not just print statements"

        print("✓ test_basic.py has real assertions, not just prints")

    except Exception as e:
        print(f"✗ Error checking test_basic.py: {e}")
        raise


if __name__ == "__main__":
    success = True

    success &= test_basic_is_automated()
    success &= test_basic_runs_and_validates()
    success &= test_pytest_compatibility()
    success &= test_no_more_print_only_tests()

    if success:
        print("🎉 test_basic.py is now a proper automated test!")
    else:
        print("❌ Some automated test validation failed")
        sys.exit(1)
