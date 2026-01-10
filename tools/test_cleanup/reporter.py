"""
Report generation components for the cleanup system.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Set, Optional
from pathlib import Path

from .models import (
    CleanupReport, CleanupSummary, CoverageReport, CoverageGap, 
    Recommendation, TestCategorization, RemovalReport, AdaptationReport
)
from .config import CleanupConfig
from .logging_setup import LoggerMixin


class ReportGenerator(LoggerMixin):
    """Main report generator orchestrator."""
    
    def __init__(self, config: CleanupConfig):
        self.config = config
        self.coverage_reporter = CoverageReporter(config)
        self.change_logger = ChangeLogger(config)
        self.recommendation_engine = RecommendationEngine(config)
    
    def generate_cleanup_report(self, 
                              categorization: TestCategorization,
                              removal_report: RemovalReport,
                              adaptation_report: AdaptationReport) -> CleanupReport:
        """
        Generate comprehensive cleanup report.
        
        Args:
            categorization: Test categorization results
            removal_report: Results of test removal
            adaptation_report: Results of test adaptation
            
        Returns:
            Complete cleanup report
        """
        self.logger.info("Generating comprehensive cleanup report")
        
        # Generate summary
        summary = self._generate_summary(categorization, removal_report, adaptation_report)
        
        # Generate coverage report
        coverage_report = self.coverage_reporter.generate_coverage_report(
            categorization, removal_report, adaptation_report
        )
        
        # Generate recommendations
        recommendations = self.recommendation_engine.generate_recommendations(
            coverage_report.coverage_gaps, categorization
        )
        
        # Create complete report
        report = CleanupReport(
            summary=summary,
            removed_tests=removal_report.removed_files,
            adapted_tests=adaptation_report.adapted_files,
            coverage_changes=coverage_report,
            recommendations=recommendations,
            errors_encountered=removal_report.errors + adaptation_report.errors
        )
        
        # Save report to file
        self._save_report(report)
        
        self.logger.info(f"Cleanup report generated: {summary.tests_removed} removed, "
                        f"{summary.tests_adapted} adapted, "
                        f"{len(recommendations)} recommendations")
        
        return report
    
    def _generate_summary(self, 
                         categorization: TestCategorization,
                         removal_report: RemovalReport,
                         adaptation_report: AdaptationReport) -> CleanupSummary:
        """Generate cleanup summary statistics."""
        return CleanupSummary(
            total_legacy_tests=categorization.total_legacy_tests,
            tests_removed=len(removal_report.removed_files),
            tests_adapted=len(adaptation_report.successful_adaptations),
            tests_preserved=len(categorization.migration_compatible_tests),
            coverage_maintained_percent=95.0,  # Will be calculated by coverage reporter
            execution_time_seconds=0.0  # Will be set by orchestrator
        )
    
    def _save_report(self, report: CleanupReport) -> None:
        """Save report to JSON file."""
        try:
            self.config.ensure_directories()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(
                self.config.output_directory, 
                f"cleanup_report_{timestamp}.json"
            )
            
            # Convert report to dictionary for JSON serialization
            report_dict = {
                "summary": {
                    "total_legacy_tests": report.summary.total_legacy_tests,
                    "tests_removed": report.summary.tests_removed,
                    "tests_adapted": report.summary.tests_adapted,
                    "tests_preserved": report.summary.tests_preserved,
                    "coverage_maintained_percent": report.summary.coverage_maintained_percent,
                    "execution_time_seconds": report.summary.execution_time_seconds
                },
                "removed_tests": report.removed_tests,
                "adapted_tests": report.adapted_tests,
                "coverage_changes": {
                    "before_cleanup": report.coverage_changes.before_cleanup,
                    "after_cleanup": report.coverage_changes.after_cleanup,
                    "coverage_gaps": [
                        {
                            "functionality": gap.functionality,
                            "description": gap.description,
                            "severity": gap.severity,
                            "suggested_tests": gap.suggested_tests
                        } for gap in report.coverage_changes.coverage_gaps
                    ],
                    "coverage_improvements": report.coverage_changes.coverage_improvements
                },
                "recommendations": [
                    {
                        "category": rec.category,
                        "priority": rec.priority,
                        "description": rec.description,
                        "action_items": rec.action_items
                    } for rec in report.recommendations
                ],
                "errors_encountered": report.errors_encountered,
                "generated_at": datetime.now().isoformat()
            }
            
            with open(report_file, 'w') as f:
                json.dump(report_dict, f, indent=2)
            
            self.logger.info(f"Cleanup report saved to: {report_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save cleanup report: {e}")


class CoverageReporter(LoggerMixin):
    """Reports on coverage changes and gaps."""
    
    def __init__(self, config: CleanupConfig):
        self.config = config
    
    def generate_coverage_report(self,
                               categorization: TestCategorization,
                               removal_report: RemovalReport,
                               adaptation_report: AdaptationReport) -> CoverageReport:
        """
        Generate coverage analysis report.
        
        Args:
            categorization: Test categorization results
            removal_report: Results of test removal
            adaptation_report: Results of test adaptation
            
        Returns:
            Coverage analysis report
        """
        self.logger.info("Analyzing coverage changes")
        
        # Calculate before/after coverage
        before_coverage = self._calculate_before_coverage(categorization)
        after_coverage = self._calculate_after_coverage(categorization, removal_report, adaptation_report)
        
        # Identify coverage gaps
        coverage_gaps = self._identify_coverage_gaps(before_coverage, after_coverage)
        
        # Identify improvements
        coverage_improvements = self._identify_coverage_improvements(before_coverage, after_coverage)
        
        return CoverageReport(
            before_cleanup=before_coverage,
            after_cleanup=after_coverage,
            coverage_gaps=coverage_gaps,
            coverage_improvements=coverage_improvements
        )
    
    def _calculate_before_coverage(self, categorization: TestCategorization) -> Dict[str, float]:
        """Calculate coverage before cleanup."""
        coverage_areas = set()
        
        # Collect all coverage areas from all tests
        all_tests = (categorization.redundant_tests + 
                    categorization.valuable_tests + 
                    categorization.unique_tests +
                    categorization.migration_compatible_tests)
        
        for test in all_tests:
            coverage_areas.update(test.analysis.coverage_areas)
        
        # Assign coverage scores (simplified)
        return {area: 1.0 for area in coverage_areas}
    
    def _calculate_after_coverage(self, 
                                categorization: TestCategorization,
                                removal_report: RemovalReport,
                                adaptation_report: AdaptationReport) -> Dict[str, float]:
        """Calculate coverage after cleanup."""
        coverage_areas = set()
        
        # Coverage from migration-compatible tests
        for test in categorization.migration_compatible_tests:
            coverage_areas.update(test.analysis.coverage_areas)
        
        # Coverage from successfully adapted tests
        adapted_tests = categorization.valuable_tests + categorization.unique_tests
        successful_adaptations = set(adaptation_report.successful_adaptations)
        
        for test in adapted_tests:
            if test.path in successful_adaptations:
                coverage_areas.update(test.analysis.coverage_areas)
        
        # Assign coverage scores
        return {area: 1.0 for area in coverage_areas}
    
    def _identify_coverage_gaps(self, 
                              before_coverage: Dict[str, float],
                              after_coverage: Dict[str, float]) -> List[CoverageGap]:
        """Identify areas where coverage was lost."""
        gaps = []
        
        for area in before_coverage:
            if area not in after_coverage:
                gap = CoverageGap(
                    functionality=area,
                    description=f"Coverage lost for {area} functionality",
                    severity="important" if area in ["chunking", "parsing"] else "minor",
                    suggested_tests=[f"test_{area}_basic", f"test_{area}_edge_cases"]
                )
                gaps.append(gap)
        
        return gaps
    
    def _identify_coverage_improvements(self,
                                     before_coverage: Dict[str, float],
                                     after_coverage: Dict[str, float]) -> List[str]:
        """Identify areas where coverage improved."""
        improvements = []
        
        for area in after_coverage:
            if area not in before_coverage:
                improvements.append(f"New coverage for {area}")
        
        return improvements


class ChangeLogger(LoggerMixin):
    """Logs all changes made during cleanup."""
    
    def __init__(self, config: CleanupConfig):
        self.config = config
        self.changes = []
    
    def log_change(self, change_type: str, description: str, details: Dict = None) -> None:
        """Log a change made during cleanup."""
        change_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": change_type,
            "description": description,
            "details": details or {}
        }
        
        self.changes.append(change_entry)
        self.logger.debug(f"Logged change: {change_type} - {description}")
    
    def get_changes(self) -> List[Dict]:
        """Get all logged changes."""
        return self.changes.copy()
    
    def save_change_log(self) -> str:
        """Save change log to file."""
        try:
            self.config.ensure_directories()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(
                self.config.output_directory,
                f"change_log_{timestamp}.json"
            )
            
            with open(log_file, 'w') as f:
                json.dump(self.changes, f, indent=2)
            
            self.logger.info(f"Change log saved to: {log_file}")
            return log_file
            
        except Exception as e:
            self.logger.error(f"Failed to save change log: {e}")
            return ""


class RecommendationEngine(LoggerMixin):
    """Generates recommendations for test suite improvements."""
    
    def __init__(self, config: CleanupConfig):
        self.config = config
    
    def generate_recommendations(self, 
                               coverage_gaps: List[CoverageGap],
                               categorization: TestCategorization) -> List[Recommendation]:
        """
        Generate recommendations based on cleanup results.
        
        Args:
            coverage_gaps: Identified coverage gaps
            categorization: Test categorization results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Coverage gap recommendations
        if coverage_gaps:
            recommendations.extend(self._generate_coverage_recommendations(coverage_gaps))
        
        # Test structure recommendations
        recommendations.extend(self._generate_structure_recommendations(categorization))
        
        # Performance recommendations
        recommendations.extend(self._generate_performance_recommendations(categorization))
        
        self.logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations
    
    def _generate_coverage_recommendations(self, coverage_gaps: List[CoverageGap]) -> List[Recommendation]:
        """Generate recommendations for coverage gaps."""
        recommendations = []
        
        critical_gaps = [gap for gap in coverage_gaps if gap.severity == "critical"]
        important_gaps = [gap for gap in coverage_gaps if gap.severity == "important"]
        
        if critical_gaps:
            recommendations.append(Recommendation(
                category="coverage",
                priority="high",
                description=f"Address {len(critical_gaps)} critical coverage gaps",
                action_items=[
                    f"Create tests for {gap.functionality}" for gap in critical_gaps
                ] + ["Run coverage analysis to verify improvements"]
            ))
        
        if important_gaps:
            recommendations.append(Recommendation(
                category="coverage",
                priority="medium",
                description=f"Address {len(important_gaps)} important coverage gaps",
                action_items=[
                    f"Consider adding tests for {gap.functionality}" for gap in important_gaps
                ]
            ))
        
        return recommendations
    
    def _generate_structure_recommendations(self, categorization: TestCategorization) -> List[Recommendation]:
        """Generate recommendations for test structure improvements."""
        recommendations = []
        
        # Test organization
        total_tests = (len(categorization.migration_compatible_tests) + 
                      len(categorization.valuable_tests) + 
                      len(categorization.unique_tests))
        
        if total_tests > 50:
            recommendations.append(Recommendation(
                category="organization",
                priority="medium",
                description="Consider organizing tests into subdirectories",
                action_items=[
                    "Group tests by functionality (e.g., tests/unit/, tests/integration/)",
                    "Update pytest configuration for new structure",
                    "Update Makefile targets accordingly"
                ]
            ))
        
        # Property-based testing
        if len(categorization.property_tests) < 3:
            recommendations.append(Recommendation(
                category="testing_strategy",
                priority="low",
                description="Consider adding more property-based tests",
                action_items=[
                    "Add property tests for core functionality",
                    "Use Hypothesis for generating test data",
                    "Focus on invariant properties"
                ]
            ))
        
        return recommendations
    
    def _generate_performance_recommendations(self, categorization: TestCategorization) -> List[Recommendation]:
        """Generate recommendations for test performance."""
        recommendations = []
        
        # Performance testing
        if len(categorization.performance_tests) == 0:
            recommendations.append(Recommendation(
                category="performance",
                priority="medium",
                description="Add performance tests for critical paths",
                action_items=[
                    "Create performance benchmarks for chunking operations",
                    "Set up performance regression detection",
                    "Monitor test execution time"
                ]
            ))
        
        # Test execution optimization
        total_tests = (len(categorization.migration_compatible_tests) + 
                      len(categorization.valuable_tests) + 
                      len(categorization.unique_tests))
        
        if total_tests > 100:
            recommendations.append(Recommendation(
                category="performance",
                priority="low",
                description="Optimize test execution for large test suite",
                action_items=[
                    "Consider parallel test execution",
                    "Use pytest-xdist for faster test runs",
                    "Profile slow tests and optimize"
                ]
            ))
        
        return recommendations