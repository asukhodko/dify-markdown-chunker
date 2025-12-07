#!/usr/bin/env python3
"""
Comprehensive benchmark runner.

Executes all benchmark tests and generates performance report.
"""

import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def main():
    """Run all performance benchmarks and generate report."""
    print("=" * 70)
    print("MARKDOWN CHUNKER V2 - PERFORMANCE BENCHMARK SUITE")
    print("=" * 70)
    print()

    # Define test files to run
    test_files = [
        "tests/performance/test_benchmark_size.py",
        "tests/performance/test_benchmark_content_type.py",
        "tests/performance/test_benchmark_strategy.py",
        "tests/performance/test_benchmark_config.py",
        "tests/performance/test_benchmark_scalability.py",
    ]

    # Run pytest with verbose output
    args = [
        "-v",
        "-s",  # Show print output
        "--tb=short",  # Short traceback format
    ] + test_files

    print("Running benchmark tests...\n")
    exit_code = pytest.main(args)

    if exit_code == 0:
        print("\n" + "=" * 70)
        print("BENCHMARK SUITE COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nResults saved to: tests/performance/results/")
        print("  - latest_run.json")
        print("  - performance_report.md")
    else:
        print("\n" + "=" * 70)
        print("BENCHMARK SUITE COMPLETED WITH ERRORS")
        print("=" * 70)

    # Generate final report
    try:
        from .results_manager import ResultsManager

        results_dir = Path(__file__).parent / "results"
        manager = ResultsManager(results_dir)

        # Save reports
        manager.save_latest_run()
        manager.save_report()
        manager.export_csv()

        print("\nPerformance report generated successfully.")
    except Exception as e:
        print(f"\nError generating final report: {e}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
