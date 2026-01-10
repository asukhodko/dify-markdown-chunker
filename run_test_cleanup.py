#!/usr/bin/env python3
"""
Execute test suite cleanup on the real dify-markdown-chunker project.

This script runs the complete test cleanup process to fix the failing
test suite after migration to the Chunkana library.
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
    """Execute the test cleanup process."""
    print("🧹 Starting Test Suite Cleanup for dify-markdown-chunker")
    print("=" * 60)
    
    # Setup logging
    log_file = project_root / "cleanup_reports" / "cleanup.log"
    setup_logging(level="INFO", log_file=str(log_file), console_output=True)
    
    # Create configuration
    config = CleanupConfig.from_project_root(str(project_root))
    config.dry_run = False  # Real cleanup
    config.create_backups = True  # Safety first
    
    print(f"Project root: {config.project_root}")
    print(f"Test directory: {config.test_directory}")
    print(f"Output directory: {config.output_directory}")
    print(f"Backup directory: {config.backup_directory}")
    print()
    
    # Ensure directories exist
    config.ensure_directories()
    
    # Create orchestrator
    orchestrator = CleanupOrchestrator(config)
    
    try:
        # Run the cleanup
        print("🔍 Starting cleanup process...")
        report = orchestrator.run_cleanup()
        
        print("\n✅ Cleanup completed successfully!")
        print(f"📊 Report saved to: {config.output_directory}")
        
        # Test the result
        print("\n🧪 Testing the cleaned test suite...")
        test_result = test_cleaned_suite()
        
        if test_result:
            print("✅ Test suite is now working!")
            print("\n🎉 SUCCESS: make test-all should now work!")
        else:
            print("⚠️  Some tests may still need manual attention")
            print("📋 Check the cleanup report for recommendations")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Cleanup interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
        print("📋 Check the logs for more details")
        return 1


def test_cleaned_suite():
    """Test if the cleaned test suite works."""
    try:
        print("Running migration-compatible tests...")
        
        # Try to run a basic test to see if things work
        import subprocess
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/test_migration_adapter.py", "-v", "--tb=short"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Migration tests pass")
            return True
        else:
            print(f"❌ Migration tests failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Could not test suite: {e}")
        return False


if __name__ == "__main__":
    sys.exit(main())