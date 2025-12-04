"""
Core parsing functionality for markdown documents.

This module consolidates the main parsing interface and fenced block extraction,
providing the primary entry point for Stage 1 markdown processing.

Algorithm Documentation:
    - Fenced Block Extraction: docs/markdown-extractor/06-algorithms/parsing.md
    - Pipeline: docs/markdown-extractor/02-algorithm-core/pipeline.md

Consolidates:
- interface.py::ParserInterface (main entry point)
- fenced_blocks.py::FencedBlockExtractor
- fence_handler.py::FenceHandler (unique logic merged)

Classes:
    FencedBlockExtractor: Extract fenced code blocks with nesting support
    ParserInterface: Main interface for Stage 1 processing

Functions:
    extract_fenced_blocks: Convenience function for fenced block extraction
"""

import logging
import re
from typing import Any, Dict, List, Optional, Pattern

from .errors import ErrorCollector
from .nesting_resolver import BlockCandidate, resolve_nesting
from .types import FencedBlock
from .utils import LineNumberConverter, PhantomBlockPreventer
from .validation import InputValidator

# Import NestingResolver if it exists (backward compatibility)
try:
    from .nesting_resolver import NestingResolver
except ImportError:
    NestingResolver = None  # type: ignore[misc,assignment]

# Import stage2_interface if it exists (backward compatibility)
try:
    from .stage2_interface import process_with_stage1_only
except ImportError:
    process_with_stage1_only = None


class FencedBlockExtractor:
    """Extractor for fenced code blocks with nesting support."""

    def __init__(self):
        # Patterns for detecting fences (from technical specification)
        # Updated to handle indentation and extra attributes
        self.fence_patterns = {
            "backtick": re.compile(
                r"^(\s*)(`{3,})\s*([a-zA-Z0-9_+-]*)\s*(.*?)$", re.MULTILINE
            ),
            "tilde": re.compile(
                r"^(\s*)(~{3,})\s*([a-zA-Z0-9_+-]*)\s*(.*?)$", re.MULTILINE
            ),
        }

        # Patterns for closing fences (also handle indentation)
        self.closing_patterns = {
            "backtick": re.compile(r"^(\s*)(`{3,})\s*$", re.MULTILINE),
            "tilde": re.compile(r"^(\s*)(~{3,})\s*$", re.MULTILINE),
        }

        # Initialize error collector and logger
        self.error_collector = ErrorCollector()
        self.logger = logging.getLogger(__name__)

    def extract_fenced_blocks(self, md_text: str) -> List[FencedBlock]:
        """Extract all fenced blocks with proper nested fence handling."""
        # Validate and normalize input
        normalized_text = InputValidator.validate_and_normalize(md_text)
        blocks = []
        lines = normalized_text.split("\n")
        open_blocks_stack: List[FencedBlock] = []  # Stack of currently open blocks

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if we're inside an open block
            if open_blocks_stack:
                current_block = open_blocks_stack[-1]

                # Check if this line closes the current block
                if self._is_closing_fence(line, current_block):
                    # Close the current block
                    current_block.end_line = LineNumberConverter.to_api_line_number(i)
                    current_block.end_offset = self._calculate_offset(lines, i + 1)
                    current_block.is_closed = True
                    current_block.raw_content = self._extract_block_content(
                        lines, current_block.start_line, current_block.end_line
                    )
                    # Extract content (excluding fence lines)
                    start_idx = LineNumberConverter.from_api_line_number(
                        current_block.start_line
                    )
                    end_idx = LineNumberConverter.from_api_line_number(
                        current_block.end_line
                    )
                    content_lines = lines[start_idx + 1 : end_idx]
                    current_block.content = "\n".join(content_lines)

                    blocks.append(open_blocks_stack.pop())
                # Otherwise, line is content (even if it looks like a fence!)

            else:
                # Not inside a block - try to start new block
                new_block = self._try_start_block(line, i, lines)
                if new_block:
                    open_blocks_stack.append(new_block)

            i += 1

        # Handle unclosed blocks
        for block in open_blocks_stack:
            block.end_line = LineNumberConverter.to_api_line_number(len(lines) - 1)
            block.end_offset = len("\n".join(lines))
            block.is_closed = False
            block.raw_content = self._extract_block_content(
                lines, block.start_line, block.end_line
            )
            # Extract content for unclosed blocks
            start_idx = LineNumberConverter.from_api_line_number(block.start_line)
            content_lines = lines[start_idx + 1 :]
            block.content = "\n".join(content_lines)
            blocks.append(block)

        # Apply phantom block prevention (still useful for edge cases)
        phantom_preventer = PhantomBlockPreventer()
        filtered_blocks = phantom_preventer.filter_phantom_blocks(blocks)

        # Resolve nesting relationships
        try:
            # Convert FencedBlocks to BlockCandidates
            candidates = [
                BlockCandidate(
                    start_line=block.start_line,
                    end_line=block.end_line,
                    block_type="code",
                    fence_char=block.fence_type[0] if block.fence_type else "`",
                    fence_length=block.fence_length,
                    language=block.language or "",
                )
                for block in filtered_blocks
            ]

            # Resolve nesting
            resolved_candidates = resolve_nesting(candidates)

            # Update original blocks with nesting information
            for block, candidate in zip(filtered_blocks, resolved_candidates):
                block.nesting_level = candidate.nesting_level

            return filtered_blocks

        except Exception as e:
            # Fallback: return filtered blocks without nesting resolution
            self.error_collector.add_warning(
                f"Nesting resolution failed: {e}",
                category="nesting_resolution",
                details=str(e),
            )
            return filtered_blocks
            # Return filtered blocks without nesting resolution
            return filtered_blocks

    def _try_extract_block_at_line(
        self, lines: List[str], start_line: int, full_text: str
    ) -> Optional[FencedBlock]:
        """Try to extract a block starting at the given line."""
        if start_line >= len(lines):
            return None

        line = lines[start_line]

        # Check for opening fence
        for fence_type, pattern in self.fence_patterns.items():
            match = pattern.match(line)
            if match:
                indent = match.group(1)  # Indentation
                fence_chars = match.group(2)  # Fence characters (``` or ~~~)
                language = match.group(3) if match.group(3) else None  # Language
                # Group 4 contains extra attributes, we ignore them for now

                # Find closing fence
                closing_pattern = self.closing_patterns[fence_type]
                end_line = self._find_closing_fence(
                    lines, start_line + 1, fence_chars, closing_pattern, indent
                )

                if end_line is not None:
                    # Extract content
                    content_lines = lines[start_line + 1 : end_line]
                    content = "\n".join(content_lines)

                    # Calculate positions
                    start_offset = self._calculate_offset(lines, start_line)
                    end_offset = self._calculate_offset(lines, end_line + 1)

                    return FencedBlock(
                        content=content,
                        language=language,
                        fence_type=fence_chars[:3],  # ``` or ~~~
                        fence_length=len(fence_chars),
                        start_line=LineNumberConverter.to_api_line_number(
                            start_line
                        ),  # Convert to 1-based
                        end_line=LineNumberConverter.to_api_line_number(
                            end_line
                        ),  # Convert to 1-based
                        start_offset=start_offset,
                        end_offset=end_offset,
                        nesting_level=0,  # Will be calculated later
                        is_closed=True,
                        raw_content="\n".join(lines[start_line : end_line + 1]),
                    )
                else:
                    # Unclosed block
                    content_lines = lines[start_line + 1 :]
                    content = "\n".join(content_lines)

                    start_offset = self._calculate_offset(lines, start_line)
                    end_offset = len(full_text)

                    return FencedBlock(
                        content=content,
                        language=language,
                        fence_type=fence_chars[:3],
                        fence_length=len(fence_chars),
                        start_line=LineNumberConverter.to_api_line_number(
                            start_line
                        ),  # Convert to 1-based
                        end_line=LineNumberConverter.to_api_line_number(
                            len(lines) - 1
                        ),  # Convert to 1-based
                        start_offset=start_offset,
                        end_offset=end_offset,
                        nesting_level=0,
                        is_closed=False,
                        raw_content="\n".join(lines[start_line:]),
                    )

        return None

    def _is_closing_fence(self, line: str, open_block: FencedBlock) -> bool:
        """Check if line closes the given open block."""
        stripped = line.strip()
        fence_char = open_block.fence_type[0]  # ` or ~

        # Must start with same fence character
        if not stripped.startswith(fence_char * 3):
            return False

        # Extract fence sequence
        fence_sequence = ""
        for char in stripped:
            if char == fence_char:
                fence_sequence += char
            else:
                break

        # Must be at least as long as opening fence
        if len(fence_sequence) < open_block.fence_length:
            return False

        # Must have no language/attributes (closing fence is bare)
        remainder = stripped[len(fence_sequence) :].strip()
        return remainder == ""

    def _try_start_block(
        self, line: str, line_num: int, lines: List[str]
    ) -> Optional[FencedBlock]:
        """Try to start a new fenced block at this line."""
        for fence_type, pattern in self.fence_patterns.items():
            match = pattern.match(line)
            if match:
                fence_chars = match.group(2)
                language = match.group(3) if match.group(3) else None

                # Calculate start offset
                start_offset = self._calculate_offset(lines, line_num)

                return FencedBlock(
                    content="",  # Will be filled when block closes
                    language=language,
                    fence_type=fence_chars[:3],  # ``` or ~~~
                    fence_length=len(fence_chars),
                    start_line=LineNumberConverter.to_api_line_number(line_num),
                    end_line=-1,  # Unknown until closed
                    start_offset=start_offset,
                    end_offset=-1,  # Unknown until closed
                    nesting_level=0,
                    is_closed=False,
                    raw_content="",
                )

        return None

    def _extract_block_content(
        self, lines: List[str], start_line: int, end_line: int
    ) -> str:
        """Extract raw content including fence lines."""
        start_idx = LineNumberConverter.from_api_line_number(start_line)
        end_idx = LineNumberConverter.from_api_line_number(end_line)
        return "\n".join(lines[start_idx : end_idx + 1])

    def _has_unclosed_block_above(
        self, lines: List[str], current_line: int, fence_char: str
    ) -> bool:
        """Check if there's an unclosed block above current line."""
        open_count = 0

        for i in range(current_line):
            line = lines[i].strip()
            # Only count fences of the same type without language
            if line.startswith(fence_char * 3) and not any(
                c.isalpha() for c in line[3:].strip()
            ):
                open_count += 1

        # If odd number of fences above, there's an unclosed block
        return open_count % 2 == 1

    def _find_closing_fence(
        self,
        lines: List[str],
        start_search: int,
        opening_fence: str,
        pattern: Pattern,
        opening_indent: str = "",
    ) -> Optional[int]:
        """Find the closing fence for a block, accounting for nesting."""
        fence_char = opening_fence[0]  # ` or ~
        open_count = 1  # We already have one opening fence

        for i in range(start_search, len(lines)):
            line = lines[i].strip()

            # Check if this line contains a fence of the same type
            if line.startswith(fence_char * 3):
                # Extract fence part (without language or other attributes)
                fence_part = ""
                for char in line:
                    if char == fence_char:
                        fence_part += char
                    else:
                        break

                # Check if this is a valid fence (at least 3 characters)
                if len(fence_part) >= 3:
                    # Check if opening fence or closing fence
                    remainder = line[len(fence_part) :].strip()

                    if remainder:  # Has language/attributes - opening fence
                        open_count += 1
                    else:  # No language/attributes - closing fence
                        open_count -= 1

                        # If we've closed all open fences, this is our fence
                        if open_count == 0:
                            return i

        return None

    def _calculate_offset(self, lines: List[str], line_num: int) -> int:
        """Calculate character offset from beginning of document."""
        if line_num == 0:
            return 0

        offset = 0
        for i in range(line_num):
            offset += len(lines[i]) + 1  # +1 for newline

        return offset

    def _validate_nesting_results(self, blocks: List[FencedBlock]) -> None:
        """Validate nesting resolution results."""
        for block in blocks:
            # Validate line numbers are still 1-based
            if block.start_line < 1 or block.end_line < 1:
                raise ValueError(
                    "Invalid line numbering in block: "
                    f"{block.start_line}-{block.end_line}"
                )

            # Validate nesting level is reasonable
            if block.nesting_level < 0 or block.nesting_level > 10:
                raise ValueError(f"Invalid nesting level: {block.nesting_level}")

            # Validate block integrity
            if block.start_line >= block.end_line and block.is_closed:
                raise ValueError(
                    "Invalid block boundaries: " f"{block.start_line}-{block.end_line}"
                )


class Stage1Interface:
    """Main interface for Stage 1 processing."""

    def __init__(self, config=None):
        """Initialize ParserInterface with configuration."""
        if config is None:
            from .config import Stage1Config

            config = Stage1Config.default()

        self.config = config
        self.error_collector = ErrorCollector()

        from .validation import Stage1APIValidator

        self.api_validator = Stage1APIValidator()

    def process_document(self, md_text: str):  # -> Stage1Results
        """Process a Markdown document through all Stage 1 components."""
        import time

        from .errors import (
            MarkdownParsingError,
            create_fallback_analysis,
            create_fallback_ast,
            create_fallback_elements,
            safe_analyze_content,
            safe_detect_elements,
            safe_extract_fenced_blocks,
            safe_parse_to_ast,
            validate_markdown_input,
        )
        from .types import Stage1Results
        from .validation import APIValidationError

        start_time = time.time()

        # Validate input
        validation_errors = validate_markdown_input(md_text)
        for error in validation_errors:
            self.error_collector.add_error(error)

        # If critical errors, fail early
        if self.error_collector.has_critical_errors():
            raise MarkdownParsingError("Critical validation errors prevent processing")

        # Parse AST
        ast = safe_parse_to_ast(md_text, self.config.parser.preferred_parser)
        if ast is None:
            ast = create_fallback_ast(md_text)
            parser_name = "fallback"
        else:
            parser_name = getattr(
                ast, "parser_name", self.config.parser.preferred_parser
            )

        # Extract fenced blocks
        fenced_blocks = safe_extract_fenced_blocks(md_text)

        # Detect elements
        elements = safe_detect_elements(md_text)
        if elements is None:
            elements = create_fallback_elements()

        # Analyze content
        analysis = safe_analyze_content(md_text)
        if analysis is None:
            analysis = create_fallback_analysis(md_text)

        processing_time = time.time() - start_time

        # Create results
        results = Stage1Results(
            ast=ast,
            fenced_blocks=fenced_blocks,
            elements=elements,
            analysis=analysis,
            parser_name=parser_name,
            processing_time=processing_time,
        )

        # Validate results before returning
        validation_result = self.api_validator.validate_process_document_result(results)

        if not validation_result.is_valid:
            all_errors = validation_result.get_all_errors()
            from .errors import ErrorSeverity, ProcessingError

            validation_error = ProcessingError(
                severity=ErrorSeverity.ERROR,
                component="api_validator",
                message=f"API validation failed with {len(all_errors)} errors",
                details="; ".join(all_errors[:3]),
            )
            self.error_collector.add_error(validation_error)

            if hasattr(results, "metadata"):
                results.metadata["validation_errors"] = all_errors
                results.metadata["validation_warnings"] = validation_result.warnings

            critical_errors = [
                error
                for error in all_errors
                if "AST is None" in error or "missing" in error.lower()
            ]

            if critical_errors:
                raise APIValidationError(critical_errors)

        return results

    def prepare_for_chunking(self, results):  # results: Stage1Results -> Dict[str, Any]
        """Prepare Stage 1 results for Stage 2 chunking."""
        return {
            "ast": results.ast,
            "fenced_blocks": results.fenced_blocks,
            "elements": results.elements,
            "analysis": results.analysis,
            "content_type": results.analysis.content_type,
            "complexity": results.analysis.complexity_score,
            "recommended_strategy": self._recommend_strategy(results.analysis),
            "metadata": {
                "parser_used": results.parser_name,
                "processing_time": results.processing_time,
                "total_chars": results.analysis.total_chars,
                "total_lines": results.analysis.total_lines,
                "languages": list(results.analysis.languages),
            },
        }

    def _recommend_strategy(self, analysis) -> str:
        """Recommend chunking strategy based on analysis."""
        if analysis.code_ratio >= 0.7 and analysis.code_block_count >= 3:
            return "code"
        elif analysis.has_mixed_content and analysis.complexity_score >= 0.3:
            return "mixed"
        elif analysis.list_count >= 5 or analysis.list_ratio > 0.6:
            return "list"
        elif analysis.table_count >= 3 or analysis.table_ratio > 0.4:
            return "table"
        elif analysis.get_total_header_count() >= 3 and analysis.max_header_depth > 1:
            return "structural"
        else:
            return "sentences"

    def get_processing_summary(
        self, results
    ):  # results: Stage1Results -> Dict[str, Any]
        """Get a summary of processing results."""
        return {
            "success": True,
            "parser_used": results.parser_name,
            "processing_time": results.processing_time,
            "document_stats": {
                "total_chars": results.analysis.total_chars,
                "total_lines": results.analysis.total_lines,
                "content_type": results.analysis.content_type,
                "complexity": results.analysis.complexity_score,
            },
            "elements_found": {
                "ast_nodes": results._count_ast_nodes(results.ast),
                "fenced_blocks": len(results.fenced_blocks),
                "headers": len(results.elements.headers),
                "lists": len(results.elements.lists),
                "tables": len(results.elements.tables),
            },
            "content_ratios": {
                "code": results.analysis.code_ratio,
                "text": results.analysis.text_ratio,
                "list": results.analysis.list_ratio,
                "table": results.analysis.table_ratio,
            },
            "recommended_strategy": self._recommend_strategy(results.analysis),
            "languages": list(results.analysis.languages),
            "errors": (
                self.error_collector.get_summary()
                if self.error_collector.has_errors()
                else None
            ),
        }

    def validate_results(self, results) -> bool:
        """Validate Stage 1 results for consistency."""
        try:
            if results.ast is None:
                return False
            if results.analysis.total_chars <= 0:
                return False
            total_ratio = (
                results.analysis.code_ratio
                + results.analysis.text_ratio
                + results.analysis.list_ratio
                + results.analysis.table_ratio
            )
            if abs(total_ratio - 1.0) > 0.1:
                return False
            if len(results.fenced_blocks) != results.analysis.code_block_count:
                return False
            if (
                len(results.elements.headers)
                != results.analysis.get_total_header_count()
            ):
                return False
            if len(results.elements.lists) != results.analysis.list_count:
                return False
            if len(results.elements.tables) != results.analysis.table_count:
                return False
            return True
        except Exception:
            return False

    def get_error_report(self) -> Dict[str, Any]:
        """Get detailed error report."""
        if not self.error_collector.has_errors():
            return {"has_errors": False}
        return {
            "has_errors": True,
            "error_count": len(self.error_collector.errors),
            "summary": self.error_collector.get_summary(),
            "errors": [
                {
                    "severity": error.severity.value,
                    "component": error.component,
                    "message": error.message,
                    "details": error.details,
                    "line_number": error.line_number,
                }
                for error in self.error_collector.errors
            ],
        }

    def reset(self) -> None:
        """Reset the interface state."""
        self.error_collector.clear()


# Backward compatibility alias
ParserInterface = Stage1Interface


# Backward compatibility convenience function
def extract_fenced_blocks(md_text: str) -> List[FencedBlock]:
    """
    Convenience function to extract fenced blocks.

    Args:
        md_text: Markdown text

    Returns:
        List of fenced blocks
    """
    extractor = FencedBlockExtractor()
    return extractor.extract_fenced_blocks(md_text)
