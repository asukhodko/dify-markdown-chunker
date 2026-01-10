"""
Configuration management for test cleanup system.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class CleanupConfig:
    """Configuration for test cleanup operations."""

    # Paths
    project_root: str
    test_directory: str = "tests"
    output_directory: str = "cleanup_reports"
    backup_directory: str = ".backup/test_cleanup"

    # Analysis settings
    min_coverage_threshold: float = 0.9  # 90% coverage preservation
    complexity_threshold: float = 10.0
    duplicate_similarity_threshold: float = 0.8

    # Processing settings
    create_backups: bool = True
    dry_run: bool = False
    preserve_unique_assertions: bool = True

    # Legacy module patterns to detect
    legacy_import_patterns: List[str] = None

    # File patterns
    test_file_patterns: List[str] = None
    exclude_patterns: List[str] = None

    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.legacy_import_patterns is None:
            self.legacy_import_patterns = [
                "markdown_chunker_v2",
                "markdown_chunker",
                "from markdown_chunker_v2",
                "from markdown_chunker",
                "import markdown_chunker_v2",
                "import markdown_chunker",
            ]

        if self.test_file_patterns is None:
            self.test_file_patterns = [
                "test_*.py",
                "*_test.py",
            ]

        if self.exclude_patterns is None:
            self.exclude_patterns = [
                "__pycache__",
                "*.pyc",
                ".pytest_cache",
                "test_migration_*.py",  # Keep migration-compatible tests
                "test_integration_basic.py",
                "test_error_handling.py",
                "test_dependencies.py",
                "test_entry_point.py",
                "test_manifest.py",
                "test_provider_*.py",
                "test_tool_*.py",
            ]

    @classmethod
    def from_project_root(cls, project_root: str) -> "CleanupConfig":
        """Create configuration from project root directory."""
        return cls(
            project_root=project_root,
            test_directory=os.path.join(project_root, "tests"),
            output_directory=os.path.join(project_root, "cleanup_reports"),
            backup_directory=os.path.join(project_root, ".backup", "test_cleanup"),
        )

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.output_directory,
            self.backup_directory,
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "project_root": self.project_root,
            "test_directory": self.test_directory,
            "output_directory": self.output_directory,
            "backup_directory": self.backup_directory,
            "min_coverage_threshold": self.min_coverage_threshold,
            "complexity_threshold": self.complexity_threshold,
            "duplicate_similarity_threshold": self.duplicate_similarity_threshold,
            "create_backups": self.create_backups,
            "dry_run": self.dry_run,
            "preserve_unique_assertions": self.preserve_unique_assertions,
            "legacy_import_patterns": self.legacy_import_patterns,
            "test_file_patterns": self.test_file_patterns,
            "exclude_patterns": self.exclude_patterns,
        }
