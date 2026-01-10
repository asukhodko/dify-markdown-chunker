#!/usr/bin/env python3
"""
Preview test suite cleanup without making changes.

This script shows what the cleanup process would do without actually
modifying any files.
"""

import os
import sys
from pathlib import Path

# Add tools directory to Python path
project_root = Path(__file__).parent
tools_dir = project_root / "tools"
sys.path.insert(0, str(tools_dir))

from test_cleanup import CleanupOrchestrator, CleanupConfig, setup_logging


def main():
    """Preview the test cleanup process."""
    print("👀 Previewing Test Suite Cleanup for dify-markdown-chunker")
    print("=" * 60)
    print("🔒 DRY RUN MODE - No changes will be made")
    print()
    
    # Setup logging
    log_file = project_root / "cleanup_reports" / "preview.log"
    setup_logging(level="INFO", log_file=str(log_file), console_output=True)
    
    # Create configuration for dry run
    config = CleanupConfig.from_project_root(str(project_root))
    config.dry_run = True  # Preview mode
    config.create_backups = True
    
    print(f"Project root: {config.project_root}")
    print(f"Test directory: {config.test_directory}")
    print(f"Will analyze: {config.test_directory}")
    print()
    
    # Ensure directories exist
    config.ensure_directories()
    
    # Create orchestrator
    orchestrator = CleanupOrchestrator(config)
    
    try:
        # Run the preview
        print("🔍 Analyzing test suite...")
        report = orchestrator.run_dry_run()
        
        print("\n📋 PREVIEW COMPLETE - Here's what would be done:")
        print("=" * 50)
        
        # Show detailed preview
        show_detailed_preview(report)
        
        print("\n🚀 To execute the actual cleanup, run:")
        print("   python run_test_cleanup.py")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Preview failed: {e}")
        return 1


def show_detailed_preview(report):
    """Show detailed preview of what would be done."""
    
    print(f"📊 ANALYSIS RESULTS:")
    print(f"   Total legacy tests found: {report.summary.total_legacy_tests}")
    print(f"   Tests that would be removed: {report.summary.tests_removed}")
    print(f"   Tests that would be adapted: {report.summary.tests_adapted}")
    print(f"   Migration-compatible tests: {report.summary.tests_preserved}")
    
    if hasattr(report, 'removed_tests') and report.removed_tests:
        print(f"\n🗑️  FILES TO BE REMOVED ({len(report.removed_tests)}):")
        for removed_file in report.removed_tests[:10]:  # Show first 10
            print(f"   - {removed_file}")
        if len(report.removed_tests) > 10:
            print(f"   ... and {len(report.removed_tests) - 10} more")
    
    if hasattr(report, 'adapted_tests') and report.adapted_tests:
        print(f"\n🔄 FILES TO BE ADAPTED ({len(report.adapted_tests)}):")
        for adapted_file in report.adapted_tests[:10]:  # Show first 10
            print(f"   - {adapted_file}")
        if len(report.adapted_tests) > 10:
            print(f"   ... and {len(report.adapted_tests) - 10} more")
    
    if report.recommendations:
        print(f"\n💡 RECOMMENDATIONS ({len(report.recommendations)}):")
        for rec in report.recommendations:
            print(f"   [{rec.priority.upper()}] {rec.description}")
    
    if report.errors_encountered:
        print(f"\n⚠️  POTENTIAL ISSUES ({len(report.errors_encountered)}):")
        for error in report.errors_encountered[:5]:
            print(f"   - {error}")


if __name__ == "__main__":
    sys.exit(main())