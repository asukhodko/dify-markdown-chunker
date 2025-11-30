"""
Configuration system for Stage 1.

This module provides configuration classes and constants based on the
technical specification from docs/markdown-extractor/TECHNICAL-SPECIFICATION.md.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Constants from technical specification
CODE_RATIO_THRESHOLD = 0.7  # Threshold for Code Strategy
LIST_RATIO_THRESHOLD = 0.6  # Threshold for List Strategy
MIXED_CONTENT_THRESHOLD = 0.3  # Threshold for Mixed Strategy
MAX_NESTING_DEPTH = 10  # Maximum nesting depth
MIN_CODE_BLOCKS = 3  # Minimum code blocks for Code Strategy
MIN_LISTS = 5  # Minimum lists for List Strategy
MIN_TABLES = 3  # Minimum tables for Table Strategy
MIN_HEADERS = 3  # Minimum headers for Structural Strategy

# File size limits
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
STREAMING_THRESHOLD = 10 * 1024 * 1024  # 10MB

# Chunk size constants (for future use in Stage 2)
MAX_CHUNK_SIZE = 4096  # characters
MIN_CHUNK_SIZE = 100  # characters

# Overlap constants (for future use in Stage 2)
OVERLAP_TARGET = 250  # characters
OVERLAP_MIN = 50  # characters
OVERLAP_MAX = 500  # characters


@dataclass
class ParserConfig:
    """Configuration for Markdown parser."""

    preferred_parser: str = "auto"  # auto, markdown-it-py, mistune, commonmark
    preserve_positions: bool = True
    strict_mode: bool = False
    max_file_size: int = MAX_FILE_SIZE
    encoding: str = "utf-8"
    fallback_on_error: bool = True

    def __post_init__(self):
        """Validate configuration."""
        valid_parsers = ["auto", "markdown-it-py", "mistune", "commonmark"]
        if self.preferred_parser not in valid_parsers:
            raise ValueError(
                f"Invalid parser: {self.preferred_parser}. "
                f"Must be one of {valid_parsers}"
            )

        if self.max_file_size <= 0:
            raise ValueError("max_file_size must be positive")


@dataclass
class ExtractorConfig:
    """Configuration for fenced block extractor."""

    handle_nesting: bool = True
    max_nesting_depth: int = MAX_NESTING_DEPTH
    preserve_fence_info: bool = True
    validate_blocks: bool = True
    # Note: extract_function_names and extract_class_names are Stage 2 features

    def __post_init__(self):
        """Validate configuration."""
        if self.max_nesting_depth <= 0:
            raise ValueError("max_nesting_depth must be positive")


@dataclass
class DetectorConfig:
    """Configuration for element detector."""

    detect_headers: bool = True
    detect_lists: bool = True
    detect_tables: bool = True
    max_list_nesting: int = MAX_NESTING_DEPTH
    generate_anchors: bool = True
    parse_task_lists: bool = True

    def __post_init__(self):
        """Validate configuration."""
        if self.max_list_nesting <= 0:
            raise ValueError("max_list_nesting must be positive")


@dataclass
class AnalyzerConfig:
    """Configuration for content analyzer."""

    code_ratio_threshold: float = CODE_RATIO_THRESHOLD
    list_ratio_threshold: float = LIST_RATIO_THRESHOLD
    mixed_content_threshold: float = MIXED_CONTENT_THRESHOLD
    calculate_complexity: bool = True
    detect_languages: bool = True

    def __post_init__(self):
        """Validate configuration."""
        if not (0.0 <= self.code_ratio_threshold <= 1.0):
            raise ValueError("code_ratio_threshold must be between 0.0 and 1.0")

        if not (0.0 <= self.list_ratio_threshold <= 1.0):
            raise ValueError("list_ratio_threshold must be between 0.0 and 1.0")

        if not (0.0 <= self.mixed_content_threshold <= 1.0):
            raise ValueError("mixed_content_threshold must be between 0.0 and 1.0")


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark framework."""

    run_benchmarks: bool = False
    test_cases: Optional[List[str]] = None
    include_memory_usage: bool = False
    iterations: int = 1
    warmup_iterations: int = 0

    def __post_init__(self):
        """Validate configuration."""
        if self.iterations <= 0:
            raise ValueError("iterations must be positive")

        if self.warmup_iterations < 0:
            raise ValueError("warmup_iterations must be non-negative")


@dataclass
class LoggingConfig:
    """Configuration for logging."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

    def __post_init__(self):
        """Validate configuration."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            raise ValueError(
                f"Invalid log level: {self.level}. Must be one of {valid_levels}"
            )


@dataclass
class Stage1Config:
    """Main configuration for Stage 1."""

    parser: ParserConfig = field(default_factory=ParserConfig)
    extractor: ExtractorConfig = field(default_factory=ExtractorConfig)
    detector: DetectorConfig = field(default_factory=DetectorConfig)
    analyzer: AnalyzerConfig = field(default_factory=AnalyzerConfig)
    benchmark: BenchmarkConfig = field(default_factory=BenchmarkConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def default(cls) -> "Stage1Config":
        """Create default configuration."""
        return cls()

    @classmethod
    def fast(cls) -> "Stage1Config":
        """Create fast configuration for large files."""
        config = cls()
        config.extractor.validate_blocks = False
        config.detector.generate_anchors = False
        config.analyzer.calculate_complexity = False
        config.analyzer.detect_languages = False
        return config

    @classmethod
    def detailed(cls) -> "Stage1Config":
        """Create detailed configuration with full analysis."""
        config = cls()
        config.benchmark.run_benchmarks = True
        config.benchmark.include_memory_usage = True
        config.logging.level = "DEBUG"
        return config

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Stage1Config":
        """Create configuration from dictionary."""
        config = cls()

        if "parser" in data:
            config.parser = ParserConfig(**data["parser"])

        if "extractor" in data:
            config.extractor = ExtractorConfig(**data["extractor"])

        if "detector" in data:
            config.detector = DetectorConfig(**data["detector"])

        if "analyzer" in data:
            config.analyzer = AnalyzerConfig(**data["analyzer"])

        if "benchmark" in data:
            config.benchmark = BenchmarkConfig(**data["benchmark"])

        if "logging" in data:
            config.logging = LoggingConfig(**data["logging"])

        return config

    @classmethod
    def from_file(cls, file_path: str) -> "Stage1Config":
        """Load configuration from JSON file."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)

    @classmethod
    def from_env(cls) -> "Stage1Config":
        """Create configuration from environment variables."""
        config = cls()

        # Parser configuration
        if os.getenv("STAGE1_PARSER_TYPE"):
            config.parser.preferred_parser = os.getenv("STAGE1_PARSER_TYPE")

        if os.getenv("STAGE1_PRESERVE_POSITIONS"):
            config.parser.preserve_positions = (
                os.getenv("STAGE1_PRESERVE_POSITIONS").lower() == "true"
            )

        if os.getenv("STAGE1_STRICT_MODE"):
            config.parser.strict_mode = (
                os.getenv("STAGE1_STRICT_MODE").lower() == "true"
            )

        # Analyzer configuration
        if os.getenv("STAGE1_CODE_RATIO_THRESHOLD"):
            config.analyzer.code_ratio_threshold = float(
                os.getenv("STAGE1_CODE_RATIO_THRESHOLD")
            )

        if os.getenv("STAGE1_LIST_RATIO_THRESHOLD"):
            config.analyzer.list_ratio_threshold = float(
                os.getenv("STAGE1_LIST_RATIO_THRESHOLD")
            )

        # Logging configuration
        if os.getenv("STAGE1_LOG_LEVEL"):
            config.logging.level = os.getenv("STAGE1_LOG_LEVEL")

        if os.getenv("STAGE1_LOG_FILE"):
            config.logging.file_path = os.getenv("STAGE1_LOG_FILE")

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "parser": {
                "preferred_parser": self.parser.preferred_parser,
                "preserve_positions": self.parser.preserve_positions,
                "strict_mode": self.parser.strict_mode,
                "max_file_size": self.parser.max_file_size,
                "encoding": self.parser.encoding,
                "fallback_on_error": self.parser.fallback_on_error,
            },
            "extractor": {
                "handle_nesting": self.extractor.handle_nesting,
                "max_nesting_depth": self.extractor.max_nesting_depth,
                "preserve_fence_info": self.extractor.preserve_fence_info,
                "validate_blocks": self.extractor.validate_blocks,
            },
            "detector": {
                "detect_headers": self.detector.detect_headers,
                "detect_lists": self.detector.detect_lists,
                "detect_tables": self.detector.detect_tables,
                "max_list_nesting": self.detector.max_list_nesting,
                "generate_anchors": self.detector.generate_anchors,
                "parse_task_lists": self.detector.parse_task_lists,
            },
            "analyzer": {
                "code_ratio_threshold": self.analyzer.code_ratio_threshold,
                "list_ratio_threshold": self.analyzer.list_ratio_threshold,
                "mixed_content_threshold": self.analyzer.mixed_content_threshold,
                "calculate_complexity": self.analyzer.calculate_complexity,
                "detect_languages": self.analyzer.detect_languages,
            },
            "benchmark": {
                "run_benchmarks": self.benchmark.run_benchmarks,
                "test_cases": self.benchmark.test_cases,
                "include_memory_usage": self.benchmark.include_memory_usage,
                "iterations": self.benchmark.iterations,
                "warmup_iterations": self.benchmark.warmup_iterations,
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "file_path": self.logging.file_path,
                "max_file_size": self.logging.max_file_size,
                "backup_count": self.logging.backup_count,
            },
        }

    def save_to_file(self, file_path: str) -> None:
        """Save configuration to JSON file."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    def _validate_component(
        self, component_name: str, config_class, data: dict
    ) -> Optional[str]:
        """Validate a single component configuration."""
        try:
            config_class(**data[component_name])
            return None
        except Exception as e:
            return f"{component_name.title()} config error: {e}"

    def validate(self) -> List[str]:
        """Validate the entire configuration and return any errors."""
        errors = []
        data = self.to_dict()

        # List of components to validate
        components = [
            ("parser", ParserConfig),
            ("extractor", ExtractorConfig),
            ("detector", DetectorConfig),
            ("analyzer", AnalyzerConfig),
            ("benchmark", BenchmarkConfig),
            ("logging", LoggingConfig),
        ]

        # Validate each component
        for component_name, config_class in components:
            error = self._validate_component(component_name, config_class, data)
            if error:
                errors.append(error)

        return errors


def setup_logging(config: LoggingConfig) -> None:
    """Setup logging based on configuration."""
    import logging
    import logging.handlers

    # Set level
    level = getattr(logging, config.level.upper())
    logging.basicConfig(level=level, format=config.format)

    # Add file handler if specified
    if config.file_path:
        handler = logging.handlers.RotatingFileHandler(
            config.file_path,
            maxBytes=config.max_file_size,
            backupCount=config.backup_count,
        )
        handler.setFormatter(logging.Formatter(config.format))
        logging.getLogger().addHandler(handler)


# Default configuration instance
default_config = Stage1Config.default()
