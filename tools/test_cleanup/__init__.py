"""
Test Suite Cleanup Tools

This package provides tools for cleaning up the dify-markdown-chunker test suite
after migration to the Chunkana library.
"""

__version__ = "1.0.0"

from .models import (
    TestAnalysis,
    TestCategorization,
    AdaptationPlan,
    CleanupReport,
    TestType,
    CoverageReport,
)

from .config import CleanupConfig
from .logging_setup import setup_logging, get_logger, LoggerMixin
from .analyzer import TestAnalyzer, ImportAnalyzer, CoverageAnalyzer, TestCategorizer
from .processor import TestProcessor, RedundancyDetector, TestAdapter, FileManager
from .updater import InfrastructureUpdater, MakefileUpdater, PytestConfigUpdater, DocumentationUpdater
from .reporter import ReportGenerator, CoverageReporter, ChangeLogger, RecommendationEngine
from .orchestrator import CleanupOrchestrator

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