"""
Pytest configuration with optional coverage support.

This configuration automatically enables coverage if pytest-cov is available,
but allows tests to run without it if the package is not installed.
"""

import sys


def pytest_configure(config):
    """Configure pytest with optional coverage."""
    try:
        # Check if pytest-cov is available without importing
        __import__("pytest_cov")

        # Only add coverage if not already specified and pytest-cov is available
        if not any("--cov" in arg for arg in sys.argv):
            # Add coverage options programmatically
            config.option.cov = ["stage1"]
            config.option.cov_report = ["html", "term-missing"]
            print("✓ Coverage enabled (pytest-cov available)")

    except ImportError:
        # pytest-cov not available - skip coverage
        print("ℹ Coverage disabled (pytest-cov not available)")


def pytest_addoption(parser):
    """Add custom pytest options."""
    # Don't add --no-cov as it's already provided by pytest-cov
    # Just add our custom options if needed


def pytest_collection_modifyitems(config, items):
    """Modify test collection if needed."""
    # Add any test collection modifications here if needed
