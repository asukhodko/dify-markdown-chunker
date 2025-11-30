"""
Stage 1: Infrastructure foundation for Python Markdown Chunker.

This module provides the core components for parsing Markdown and extracting
fenced code blocks, serving as the foundation for Stage 2 chunking algorithms.

Enhanced API for Stage 1 includes:
- Fenced block extraction with nesting support
- AST building with inline token support
- API validation and error collection
- Simple API for quick start scenarios
- 1-based line numbering
- Input validation and normalization
"""

# flake8: noqa: E402
# Imports after docstring are intentional for better readability

# AST building - from ast.py
from .ast import ASTBuilder, EnhancedASTBuilder

# Core functionality - from core.py
from .core import (
    FencedBlockExtractor,
    ParserInterface,
    Stage1Interface,
    extract_fenced_blocks,
)

# Error handling - from errors.py
from .errors import (
    ContentAnalysisError,
    ElementDetectionError,
    ErrorCollector,
    ErrorInfo,
    ErrorSeverity,
    ErrorSummary,
    FencedBlockError,
    MarkdownParsingError,
    ParserSelectionError,
    ProcessingError,
    SourceLocation,
    WarningInfo,
    create_source_location,
)

# Keep old imports for backward compatibility (deprecated)
from .fence_handler import FenceHandler

# Preamble extraction - from preamble.py
from .preamble import (
    PreambleExtractor,
    PreambleInfo,
    PreambleType,
    extract_preamble,
)

# Core data types
from .types import ContentAnalysis, FencedBlock, MarkdownNode, Position, Stage1Results

# Utilities - from utils.py
from .utils import (
    LineNumberConverter,
    PhantomBlockPreventer,
    TextRecoveryUtils,
    convert_from_api_lines,
    convert_to_api_lines,
    create_text_recovery_utils,
    filter_phantom_blocks,
    validate_block_sequence,
)

# Validation - from validation.py
from .validation import (
    APIValidator,
    ASTValidator,
    InputValidator,
    Stage1APIValidator,
    ValidationIssue,
    ValidationResult,
    normalize_line_endings,
    validate_and_normalize_input,
    validate_ast_structure,
    validate_stage1_result,
)

# Note: MarkdownNode is imported from types.py for backward compatibility


# Backward compatibility functions
def parse_to_ast(md_text: str, parser_type: str = "auto"):
    """Parse Markdown to AST (backward compatibility wrapper)."""
    # Use old implementation from markdown_ast.py for backward compatibility
    from .markdown_ast import parse_to_ast as old_parse_to_ast

    return old_parse_to_ast(md_text, parser_type)


def process_markdown(md_text: str):
    """Process markdown (backward compatibility wrapper)."""
    parser = ParserInterface()
    return parser.process_document(md_text)


# Backward compatibility aliases for classes
# Create ValidationError as alias for MarkdownParsingError
class ValidationError(MarkdownParsingError):
    """Validation error (backward compatibility)."""


APIValidationError = ValidationError  # Old name for ValidationError

# Import old nesting resolver classes for backward compatibility
# Note: These will be removed in final cleanup
try:
    from .nesting_resolver import (
        BlockCandidate,
        NestingResolver,
        resolve_nesting,
        validate_block_nesting,
    )
except ImportError:
    # Fallback if nesting_resolver is removed
    class BlockCandidate:
        pass

    class NestingResolver:
        pass

    def resolve_nesting(*args, **kwargs):
        return []

    def validate_block_nesting(*args, **kwargs):
        return True


# Simple API for quick start (deprecated, kept for backward compatibility)
try:
    from .simple_api import (
        analyze,
        check_markdown_quality,
        check_quality,
        extract_code_blocks,
        get_code,
        get_document_structure,
        get_structure,
        parse_markdown,
        quick_analyze,
    )
except ImportError:
    # Fallback if simple_api is removed
    def analyze(*args, **kwargs):
        raise NotImplementedError("simple_api has been removed")

    check_markdown_quality = check_quality = extract_code_blocks = analyze
    get_code = get_document_structure = get_structure = analyze
    parse_markdown = quick_analyze = analyze

__version__ = "0.2.0"

# Public API
__all__ = [
    # Main functions
    "extract_fenced_blocks",
    "parse_markdown",
    "parse_to_ast",
    "process_markdown",
    "analyze",
    # Simple API
    "extract_code_blocks",
    "get_document_structure",
    "check_markdown_quality",
    "quick_analyze",
    "get_code",
    "get_structure",
    "check_quality",
    # Core classes
    "ParserInterface",
    "Stage1Interface",
    "FenceHandler",
    "FencedBlockExtractor",
    # Nesting resolver (backward compatibility)
    "BlockCandidate",
    "NestingResolver",
    "resolve_nesting",
    "validate_block_nesting",
    # AST classes
    "ASTBuilder",
    "EnhancedASTBuilder",
    "MarkdownNode",
    # Validation classes
    "InputValidator",
    "Stage1APIValidator",
    "APIValidator",
    "ASTValidator",
    "ValidationResult",
    "ValidationIssue",
    "ValidationError",
    "APIValidationError",
    # Error handling classes
    "ErrorCollector",
    "ErrorInfo",
    "WarningInfo",
    "ErrorSummary",
    "SourceLocation",
    "ProcessingError",
    "MarkdownParsingError",
    "FencedBlockError",
    "ParserSelectionError",
    "ElementDetectionError",
    "ContentAnalysisError",
    "ErrorSeverity",
    # Utility classes
    "LineNumberConverter",
    "TextRecoveryUtils",
    "PhantomBlockPreventer",
    # Preamble extraction
    "PreambleExtractor",
    "PreambleInfo",
    "PreambleType",
    "extract_preamble",
    # Data types
    "FencedBlock",
    "Position",
    "ContentAnalysis",
    "Stage1Results",
    # Validation functions
    "validate_and_normalize_input",
    "normalize_line_endings",
    "validate_stage1_result",
    "validate_ast_structure",
    # Error functions
    "create_source_location",
    # Utility functions
    "convert_to_api_lines",
    "convert_from_api_lines",
    "create_text_recovery_utils",
    "validate_block_sequence",
    "filter_phantom_blocks",
]
