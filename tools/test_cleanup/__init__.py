"""
Test Suite Cleanup Tools

This package provides tools for cleaning up the dify-markdown-chunker test suite
after migration to the Chunkana library.
"""

__version__ = "1.0.0"

from .analyzer import CoverageAnalyzer, ImportAnalyzer, TestAnalyzer, TestCategorizer
from .config import CleanupConfig
from .logging_setup import LoggerMixin, get_logger, setup_logging
from .models import (
    AdaptationPlan,
    CleanupReport,
    CoverageReport,
    TestAnalysis,
    TestCategorization,
    TestType,
)
from .orchestrator import CleanupOrchestrator
from .processor import FileManager, RedundancyDetector, TestAdapter, TestProcessor
from .reporter import (
    ChangeLogger,
    CoverageReporter,
    RecommendationEngine,
    ReportGenerator,
)
from .updater import (
    DocumentationUpdater,
    InfrastructureUpdater,
    MakefileUpdater,
    PytestConfigUpdater,
)

# Components will be imported as they are implemented
# from .processor import TestProcessor
# from .updater import InfrastructureUpdater
# from .reporter import ReportGenerator
# from .orchestrator import CleanupOrchestrator

__all__ = [
    "TestAnalysis",
    "TestCategorization",
    "AdaptationPlan",
    "CleanupReport",
    "TestType",
    "CoverageReport",
    "CleanupConfig",
    "setup_logging",
    "get_logger",
    "LoggerMixin",
    "TestAnalyzer",
    "ImportAnalyzer",
    "CoverageAnalyzer",
    "TestCategorizer",
    "TestProcessor",
    "RedundancyDetector",
    "TestAdapter",
    "FileManager",
    "InfrastructureUpdater",
    "MakefileUpdater",
    "PytestConfigUpdater",
    "DocumentationUpdater",
    "ReportGenerator",
    "CoverageReporter",
    "ChangeLogger",
    "RecommendationEngine",
    "CleanupOrchestrator",
    # Components will be added as they are implemented
    # "TestProcessor",
    # "InfrastructureUpdater",
    # "ReportGenerator",
    # "CleanupOrchestrator",
]
