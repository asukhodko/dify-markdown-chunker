"""
Core data models for test cleanup system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from pathlib import Path


class TestType(Enum):
    """Types of tests identified in the test suite."""
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    PROPERTY = "property"
    REGRESSION = "regression"
    UNKNOWN = "unknown"


class TestCategory(Enum):
    """Categories for test processing decisions."""
    REDUNDANT = "redundant"
    VALUABLE = "valuable"
    UNIQUE = "unique"
    MIGRATION_COMPATIBLE = "migration_compatible"


@dataclass
class TestAnalysis:
    """Analysis results for a single test file."""
    file_path: str
    imports: List[str]
    test_functions: List[str]
    coverage_areas: List[str]
    test_type: TestType
    dependencies: List[str]
    complexity_score: float
    has_legacy_imports: bool = False
    line_count: int = 0
    
    @property
    def file_name(self) -> str:
        """Get the file name without path."""
        return Path(self.file_path).name


@dataclass
class TestFile:
    """Represents a test file with its metadata."""
    path: str
    analysis: TestAnalysis
    category: TestCategory
    
    @property
    def name(self) -> str:
        """Get the file name without path."""
        return Path(self.path).name


@dataclass
class TestCategorization:
    """Results of test categorization process."""
    redundant_tests: List[TestFile]
    valuable_tests: List[TestFile]
    unique_tests: List[TestFile]
    performance_tests: List[TestFile]
    property_tests: List[TestFile]
    migration_compatible_tests: List[TestFile]
    
    @property
    def total_legacy_tests(self) -> int:
        """Total number of legacy tests analyzed."""
        return (len(self.redundant_tests) + len(self.valuable_tests) + 
                len(self.unique_tests))
    
    @property
    def tests_to_remove(self) -> List[TestFile]:
        """Tests marked for removal."""
        return self.redundant_tests
    
    @property
    def tests_to_adapt(self) -> List[TestFile]:
        """Tests that need adaptation."""
        return self.valuable_tests + self.unique_tests


@dataclass
class CodeChange:
    """Represents a code change made during adaptation."""
    line_number: int
    old_code: str
    new_code: str
    change_type: str  # "import", "function_call", "assertion", etc.


@dataclass
class AdaptationPlan:
    """Plan for adapting a legacy test to new architecture."""
    original_file: str
    adapted_file: str
    import_changes: Dict[str, str]
    code_changes: List[CodeChange]
    preserved_assertions: List[str]
    adaptation_notes: List[str] = field(default_factory=list)


@dataclass
class RemovedTest:
    """Information about a removed test."""
    file_path: str
    test_functions: List[str]
    removal_reason: str
    preserved_assertions: List[str] = field(default_factory=list)


@dataclass
class AdaptedTest:
    """Information about an adapted test."""
    original_path: str
    adapted_path: str
    changes_made: List[str]
    adaptation_success: bool
    error_message: Optional[str] = None


@dataclass
class CoverageGap:
    """Represents a gap in test coverage."""
    functionality: str
    description: str
    severity: str  # "critical", "important", "minor"
    suggested_tests: List[str] = field(default_factory=list)


@dataclass
class CoverageReport:
    """Test coverage analysis results."""
    before_cleanup: Dict[str, float]
    after_cleanup: Dict[str, float]
    coverage_gaps: List[CoverageGap]
    coverage_improvements: List[str] = field(default_factory=list)
    
    @property
    def coverage_change_percent(self) -> float:
        """Calculate overall coverage change percentage."""
        before_total = sum(self.before_cleanup.values())
        after_total = sum(self.after_cleanup.values())
        if before_total == 0:
            return 0.0
        return ((after_total - before_total) / before_total) * 100


@dataclass
class Recommendation:
    """A recommendation for improving the test suite."""
    category: str
    priority: str  # "high", "medium", "low"
    description: str
    action_items: List[str]


@dataclass
class CleanupSummary:
    """Summary statistics for the cleanup operation."""
    total_legacy_tests: int
    tests_removed: int
    tests_adapted: int
    tests_preserved: int
    coverage_maintained_percent: float
    execution_time_seconds: float


@dataclass
class CleanupReport:
    """Comprehensive report of the cleanup operation."""
    summary: CleanupSummary
    removed_tests: List[RemovedTest]
    adapted_tests: List[AdaptedTest]
    coverage_changes: CoverageReport
    recommendations: List[Recommendation]
    errors_encountered: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary for serialization."""
        return {
            "summary": {
                "total_legacy_tests": self.summary.total_legacy_tests,
                "tests_removed": self.summary.tests_removed,
                "tests_adapted": self.summary.tests_adapted,
                "tests_preserved": self.summary.tests_preserved,
                "coverage_maintained_percent": self.summary.coverage_maintained_percent,
                "execution_time_seconds": self.summary.execution_time_seconds,
            },
            "removed_tests": [
                {
                    "file_path": test.file_path,
                    "test_functions": test.test_functions,
                    "removal_reason": test.removal_reason,
                    "preserved_assertions": test.preserved_assertions,
                }
                for test in self.removed_tests
            ],
            "adapted_tests": [
                {
                    "original_path": test.original_path,
                    "adapted_path": test.adapted_path,
                    "changes_made": test.changes_made,
                    "adaptation_success": test.adaptation_success,
                    "error_message": test.error_message,
                }
                for test in self.adapted_tests
            ],
            "coverage_changes": {
                "before_cleanup": self.coverage_changes.before_cleanup,
                "after_cleanup": self.coverage_changes.after_cleanup,
                "coverage_change_percent": self.coverage_changes.coverage_change_percent,
                "coverage_gaps": [
                    {
                        "functionality": gap.functionality,
                        "description": gap.description,
                        "severity": gap.severity,
                        "suggested_tests": gap.suggested_tests,
                    }
                    for gap in self.coverage_changes.coverage_gaps
                ],
            },
            "recommendations": [
                {
                    "category": rec.category,
                    "priority": rec.priority,
                    "description": rec.description,
                    "action_items": rec.action_items,
                }
                for rec in self.recommendations
            ],
            "errors_encountered": self.errors_encountered,
        }


@dataclass
class DuplicateReport:
    """Report of duplicate test detection."""
    duplicate_pairs: List[tuple[str, str]]  # (legacy_test, migration_test)
    redundant_files: List[str]
    unique_coverage_areas: List[str]
    
    @property
    def total_duplicates(self) -> int:
        """Total number of duplicate test pairs found."""
        return len(self.duplicate_pairs)


@dataclass
class RemovalReport:
    """Report of test removal operations."""
    removed_files: List[str]
    preserved_assertions: Dict[str, List[str]]  # file -> assertions
    makefile_updates: List[str]
    errors: List[str] = field(default_factory=list)


@dataclass
class AdaptationReport:
    """Report of test adaptation operations."""
    adapted_files: List[str]
    adaptation_plans: List[AdaptationPlan]
    successful_adaptations: List[str]
    failed_adaptations: List[str]
    errors: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of test suite validation."""
    all_tests_pass: bool
    failed_tests: List[str]
    execution_time: float
    coverage_metrics: Dict[str, float]
    performance_metrics: Dict[str, float]
    errors: List[str] = field(default_factory=list)


@dataclass
class ChangeReport:
    """Report of all changes made during cleanup."""
    removed_tests: List[RemovedTest] = field(default_factory=list)
    adapted_tests: List[AdaptedTest] = field(default_factory=list)
    makefile_changes: List[str] = field(default_factory=list)
    pytest_config_changes: List[str] = field(default_factory=list)
    documentation_changes: List[str] = field(default_factory=list)
    
    @property
    def total_changes(self) -> int:
        """Total number of changes made."""
        return (len(self.removed_tests) + len(self.adapted_tests) + 
                len(self.makefile_changes) + len(self.pytest_config_changes) +
                len(self.documentation_changes))