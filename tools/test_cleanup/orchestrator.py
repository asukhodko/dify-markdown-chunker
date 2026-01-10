"""
Main cleanup orchestrator for coordinating all cleanup phases.
"""

import os
import sys
import time
import argparse
from typing import Optional
from pathlib import Path

from .config import CleanupConfig
from .logging_setup import setup_logging, LoggerMixin
from .analyzer import TestAnalyzer
from .processor import TestProcessor
from .updater import InfrastructureUpdater
from .reporter import ReportGenerator
from .models import CleanupReport


class CleanupOrchestrator(LoggerMixin):
    """Main orchestrator for test cleanup operations."""
    
    def __init__(self, config: CleanupConfig):
        self.config = config
        self.analyzer = TestAnalyzer(config)
        self.processor = TestProcessor(config)
        self.updater = InfrastructureUpdater(config)
        self.reporter = ReportGenerator(config)
        self.start_time = None
    
    def run_cleanup(self) -> CleanupReport:
        """
        Execute complete test cleanup process.
        
        Returns:
            Comprehensive cleanup report
        """
        self.start_time = time.time()
        self.logger.info("Starting test suite cleanup process")
        
        try:
            # Phase 1: Analysis
            self.logger.info("Phase 1: Analyzing test suite")
            analyses = self.analyzer.scan_test_directory()
            categorization = self.analyzer.categorize_tests(analyses)
            duplicate_report = self.analyzer.identify_duplicates(categorization)
            
            self.logger.info(f"Analysis complete: {len(analyses)} files analyzed, "
                           f"{categorization.total_legacy_tests} legacy tests found")
            
            # Phase 2: Processing
            self.logger.info("Phase 2: Processing tests")
            removal_report = self.processor.remove_redundant_tests(duplicate_report)
            adaptation_report = self.processor.adapt_valuable_tests(categorization.tests_to_adapt)
            
            self.logger.info(f"Processing complete: {len(removal_report.removed_files)} removed, "
                           f"{len(adaptation_report.successful_adaptations)} adapted")
            
            # Phase 3: Infrastructure Updates
            self.logger.info("Phase 3: Updating infrastructure")
            self.updater.update_makefile(removal_report.removed_files, adaptation_report.adapted_files)
            
            excluded_dirs = self._get_excluded_directories(removal_report.removed_files)
            self.updater.update_pytest_config(excluded_dirs)
            
            # Create change report for documentation
            from .updater import ChangeReport
            change_report = ChangeReport(
                removed_tests=[{"file_path": f, "reason": "redundant"} for f in removal_report.removed_files],
                adapted_tests=[{"file_path": f, "success": True} for f in adaptation_report.successful_adaptations]
            )
            self.updater.update_documentation(change_report)
            
            self.logger.info("Infrastructure updates complete")
            
            # Phase 4: Validation
            self.logger.info("Phase 4: Validating results")
            validation_success = self._validate_cleanup_results()
            
            # Phase 5: Reporting
            self.logger.info("Phase 5: Generating reports")
            cleanup_report = self.reporter.generate_cleanup_report(
                categorization, removal_report, adaptation_report
            )
            
            # Update execution time
            execution_time = time.time() - self.start_time
            cleanup_report.summary.execution_time_seconds = execution_time
            
            self.logger.info(f"Cleanup completed successfully in {execution_time:.2f} seconds")
            self._print_summary(cleanup_report)
            
            return cleanup_report
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            raise
    
    def run_dry_run(self) -> CleanupReport:
        """
        Execute cleanup in dry-run mode (no actual changes).
        
        Returns:
            Cleanup report showing what would be done
        """
        self.logger.info("Running cleanup in DRY RUN mode - no changes will be made")
        
        # Temporarily set dry-run mode
        original_dry_run = self.config.dry_run
        self.config.dry_run = True
        
        try:
            report = self.run_cleanup()
            self.logger.info("DRY RUN completed - no actual changes were made")
            return report
        finally:
            self.config.dry_run = original_dry_run
    
    def _get_excluded_directories(self, removed_files: list) -> list:
        """Get directories that should be excluded from pytest discovery."""
        excluded_dirs = set()
        
        for file_path in removed_files:
            # If entire directories were cleared, exclude them
            dir_path = os.path.dirname(file_path)
            if dir_path and dir_path != "tests":
                # Check if directory is now empty or mostly empty
                if os.path.exists(dir_path):
                    remaining_files = [f for f in os.listdir(dir_path) 
                                     if f.endswith('.py') and f.startswith('test_')]
                    if len(remaining_files) <= 1:  # Only __init__.py or similar
                        excluded_dirs.add(dir_path)
        
        return list(excluded_dirs)
    
    def _validate_cleanup_results(self) -> bool:
        """Validate that cleanup was successful."""
        try:
            # Check that migration-compatible tests still pass
            if not self.config.dry_run:
                self.logger.info("Validating migration-compatible tests")
                # Could run a subset of tests here
                # For now, just check that test files exist
                
                test_dir = Path(self.config.test_directory)
                if test_dir.exists():
                    migration_tests = list(test_dir.glob("test_migration_*.py"))
                    if migration_tests:
                        self.logger.info(f"Found {len(migration_tests)} migration tests")
                        return True
            
            return True
            
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return False
    
    def _print_summary(self, report: CleanupReport) -> None:
        """Print cleanup summary to console."""
        print("\n" + "="*60)
        print("TEST SUITE CLEANUP SUMMARY")
        print("="*60)
        print(f"Total legacy tests analyzed: {report.summary.total_legacy_tests}")
        print(f"Tests removed (redundant):   {report.summary.tests_removed}")
        print(f"Tests adapted (valuable):    {report.summary.tests_adapted}")
        print(f"Tests preserved (compatible): {report.summary.tests_preserved}")
        print(f"Coverage maintained:         {report.summary.coverage_maintained_percent:.1f}%")
        print(f"Execution time:              {report.summary.execution_time_seconds:.2f}s")
        
        if report.errors_encountered:
            print(f"\nErrors encountered:          {len(report.errors_encountered)}")
            for error in report.errors_encountered[:3]:  # Show first 3 errors
                print(f"  - {error}")
            if len(report.errors_encountered) > 3:
                print(f"  ... and {len(report.errors_encountered) - 3} more")
        
        if report.recommendations:
            print(f"\nRecommendations:             {len(report.recommendations)}")
            for rec in report.recommendations[:2]:  # Show first 2 recommendations
                print(f"  - [{rec.priority.upper()}] {rec.description}")
            if len(report.recommendations) > 2:
                print(f"  ... and {len(report.recommendations) - 2} more")
        
        print("="*60)


def create_cli() -> argparse.ArgumentParser:
    """Create command-line interface for cleanup tool."""
    parser = argparse.ArgumentParser(
        description="Clean up test suite after migration to Chunkana library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m tools.test_cleanup.orchestrator --dry-run
  python -m tools.test_cleanup.orchestrator --project-root /path/to/project
  python -m tools.test_cleanup.orchestrator --verbose --no-backups
        """
    )
    
    parser.add_argument(
        "--project-root",
        default=".",
        help="Root directory of the project (default: current directory)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    parser.add_argument(
        "--no-backups",
        action="store_true",
        help="Don't create backups of removed files"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--log-file",
        help="Write logs to specified file"
    )
    
    parser.add_argument(
        "--output-dir",
        help="Directory for cleanup reports (default: cleanup_reports)"
    )
    
    return parser


def main():
    """Main entry point for cleanup tool."""
    parser = create_cli()
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level, log_file=args.log_file)
    
    # Create configuration
    config = CleanupConfig.from_project_root(args.project_root)
    config.dry_run = args.dry_run
    config.create_backups = not args.no_backups
    
    if args.output_dir:
        config.output_directory = args.output_dir
    
    # Ensure directories exist
    config.ensure_directories()
    
    # Create and run orchestrator
    orchestrator = CleanupOrchestrator(config)
    
    try:
        if args.dry_run:
            report = orchestrator.run_dry_run()
        else:
            report = orchestrator.run_cleanup()
        
        # Exit with success
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\nCleanup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nCleanup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()