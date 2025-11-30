"""
Utility classes and helper functions for markdown parsing.

This module consolidates utility functionality into a single location.

Consolidates:
- line_converter.py::LineNumberConverter
- text_recovery_utils.py::TextRecoveryUtils
- phantom_block_preventer.py::PhantomBlockPreventer

Classes:
    LineNumberConverter: Convert between 0-based and 1-based line numbers
    TextRecoveryUtils: Utilities for text recovery and reconstruction
    PhantomBlockPreventer: Prevent phantom block creation

Functions:
    create_text_recovery_utils: Factory function for TextRecoveryUtils
"""

import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Imports will be added during migration
# from .types import MarkdownNode, FencedBlock


class LineNumberConverter:
    """Utility class for converting between 0-based and 1-based line numbering."""

    @staticmethod
    def to_api_line_number(internal_line: int) -> int:
        """
        Convert 0-based internal line to 1-based API line.

        Args:
            internal_line: 0-based line number used internally

        Returns:
            1-based line number for API responses

        Raises:
            ValueError: If internal_line is negative
        """
        if internal_line < 0:
            raise ValueError(
                f"Internal line number must be non-negative, got {internal_line}"
            )
        return internal_line + 1

    @staticmethod
    def from_api_line_number(api_line: int) -> int:
        """
        Convert 1-based API line to 0-based internal line.

        Args:
            api_line: 1-based line number from API

        Returns:
            0-based line number for internal use

        Raises:
            ValueError: If api_line is less than 1
        """
        if api_line < 1:
            raise ValueError(f"API line number must be >= 1, got {api_line}")
        return api_line - 1

    @staticmethod
    def validate_api_line_number(line_number: int) -> bool:
        """
        Validate that a line number follows 1-based API conventions.

        Args:
            line_number: Line number to validate

        Returns:
            True if valid

        Raises:
            ValueError: If line number is invalid
        """
        if line_number < 1:
            raise ValueError(f"API line number must be >= 1, got {line_number}")
        return True

    @staticmethod
    def validate_line_range(start_line: int, end_line: int) -> bool:
        """
        Validate that a line range is valid for 1-based API.

        Args:
            start_line: Starting line number (1-based)
            end_line: Ending line number (1-based)

        Returns:
            True if valid

        Raises:
            ValueError: If range is invalid
        """
        LineNumberConverter.validate_api_line_number(start_line)
        LineNumberConverter.validate_api_line_number(end_line)

        if end_line < start_line:
            raise ValueError(
                f"End line ({end_line}) must be >= start line ({start_line})"
            )

        return True

    # Backward compatibility aliases
    @staticmethod
    def to_1_based(internal_line: int) -> int:
        """Alias for to_api_line_number (backward compatibility)."""
        return LineNumberConverter.to_api_line_number(internal_line)

    @staticmethod
    def to_0_based(api_line: int) -> int:
        """Alias for from_api_line_number (backward compatibility)."""
        return LineNumberConverter.from_api_line_number(api_line)


def convert_to_api_lines(start_internal: int, end_internal: int) -> Tuple[int, int]:
    """
    Convenience function to convert a range of internal lines to API lines.

    Args:
        start_internal: 0-based start line
        end_internal: 0-based end line

    Returns:
        Tuple of (1-based start line, 1-based end line)
    """
    start_api = LineNumberConverter.to_api_line_number(start_internal)
    end_api = LineNumberConverter.to_api_line_number(end_internal)
    LineNumberConverter.validate_line_range(start_api, end_api)
    return start_api, end_api


def convert_from_api_lines(start_api: int, end_api: int) -> Tuple[int, int]:
    """
    Convenience function to convert a range of API lines to internal lines.

    Args:
        start_api: 1-based start line
        end_api: 1-based end line

    Returns:
        Tuple of (0-based start line, 0-based end line)
    """
    LineNumberConverter.validate_line_range(start_api, end_api)
    start_internal = LineNumberConverter.from_api_line_number(start_api)
    end_internal = LineNumberConverter.from_api_line_number(end_api)
    return start_internal, end_internal


class TextRecoveryUtils:
    """Utilities for recovering original text from blocks and elements."""

    def __init__(self, source_text: str):
        """
        Initialize with source text.

        Args:
            source_text: Original markdown text
        """
        self.source_text = source_text
        self.lines = source_text.split("\n")

    def get_block_text(self, block, include_fences: bool = True) -> str:
        """
        Recover full text of a block with or without fences.

        Args:
            block: The fenced block to recover (FencedBlock)
            include_fences: Whether to include opening/closing fences

        Returns:
            Original text of the block
        """
        try:
            if include_fences:
                return self._get_block_with_fences(block)
            else:
                return block.content
        except Exception as e:
            logger.debug(
                f"Failed to get block text with fences: {e}. "
                f"Falling back to stored content."
            )
            return block.content  # Fallback to stored content

    def _get_block_with_fences(self, block) -> str:
        """Recover block with opening and closing fences."""
        # Convert 1-based line numbers to 0-based indices
        start_line_index = block.start_line - 1
        end_line_index = block.end_line - 1

        # Validate line indices
        if (
            start_line_index < 0
            or end_line_index >= len(self.lines)
            or start_line_index > end_line_index
        ):
            return getattr(block, "raw_content", block.content)

        # Extract lines including fences
        block_lines = self.lines[start_line_index : end_line_index + 1]
        return "\n".join(block_lines)

    def get_block_context(self, block, context_lines: int = 2) -> str:
        """
        Get block with surrounding context lines.

        Args:
            block: The fenced block (FencedBlock)
            context_lines: Number of context lines before and after

        Returns:
            Block with context, marked for easy identification
        """
        try:
            # Calculate context range
            start_line_index = max(0, block.start_line - 1 - context_lines)
            end_line_index = min(
                len(self.lines) - 1, block.end_line - 1 + context_lines
            )

            # Extract context lines
            context_lines_list = self.lines[start_line_index : end_line_index + 1]

            # Mark the actual block lines
            result_lines = []
            for i, line in enumerate(context_lines_list):
                actual_line_num = start_line_index + i + 1  # Convert to 1-based

                if block.start_line <= actual_line_num <= block.end_line:
                    result_lines.append(f">>> {line}")
                else:
                    result_lines.append(f"    {line}")

            return "\n".join(result_lines)
        except Exception as e:
            logger.debug(
                f"Failed to format block with context: {e}. "
                f"Falling back to simple block text."
            )
            return self.get_block_text(block, include_fences=True)

    def get_line_text(self, line_number: int) -> str:
        """
        Get text of a specific line.

        Args:
            line_number: Line number (1-based)

        Returns:
            Text of the line or empty string if invalid
        """
        if line_number < 1 or line_number > len(self.lines):
            return ""
        return self.lines[line_number - 1]

    def get_text_range(self, start_line: int, end_line: int) -> str:
        """
        Get text for a range of lines.

        Args:
            start_line: Start line number (1-based, inclusive)
            end_line: End line number (1-based, inclusive)

        Returns:
            Text for the line range
        """
        try:
            # Convert to 0-based indices
            start_index = start_line - 1
            end_index = end_line - 1

            # Validate range
            if (
                start_index < 0
                or end_index >= len(self.lines)
                or start_index > end_index
            ):
                return ""

            # Extract lines
            lines = self.lines[start_index : end_index + 1]
            return "\n".join(lines)
        except Exception as e:
            logger.debug(f"Failed to get line text: {e}. Returning empty string.")
            return ""

    def find_text_at_position(self, line: int, column: int, length: int = 10) -> str:
        """
        Find text at a specific position.

        Args:
            line: Line number (1-based)
            column: Column number (1-based)
            length: Number of characters to extract

        Returns:
            Text at the position
        """
        try:
            line_text = self.get_line_text(line)
            if not line_text:
                return ""

            # Convert to 0-based column
            start_col = max(0, column - 1)
            end_col = min(len(line_text), start_col + length)

            return line_text[start_col:end_col]
        except Exception as e:
            logger.debug(
                f"Failed to get text at position (line={line}, col={column}): {e}. "
                f"Returning empty string."
            )
            return ""

    def validate_block_recovery(self, block) -> List[str]:
        """
        Validate that block recovery works correctly.

        Args:
            block: The block to validate (FencedBlock)

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        try:
            # Test basic recovery
            recovered_text = self.get_block_text(block, include_fences=True)
            if not recovered_text:
                issues.append("Failed to recover block text")

            # Test content recovery
            content_text = self.get_block_text(block, include_fences=False)
            if content_text != block.content:
                issues.append("Content recovery doesn't match stored content")

            # Test line range validity
            if block.start_line < 1 or block.end_line < block.start_line:
                issues.append(
                    f"Invalid line range: {block.start_line}-{block.end_line}"
                )

            # Test line range within document bounds
            if block.end_line > len(self.lines):
                issues.append(
                    f"End line {block.end_line} exceeds document "
                    f"length {len(self.lines)}"
                )
        except Exception as e:
            issues.append(f"Recovery validation failed: {e}")

        return issues


class PhantomBlockPreventer:
    """Prevents creation of phantom blocks during extraction."""

    def validate_block_sequence(self, blocks: List) -> List[str]:
        """
        Validate sequence of blocks for phantom blocks.

        Args:
            blocks: List of FencedBlock objects

        Returns:
            List of warning messages
        """
        warnings = []

        if len(blocks) <= 1:
            return warnings

        # Sort blocks by start line for sequential analysis
        sorted_blocks = sorted(blocks, key=lambda b: b.start_line)

        for i in range(len(sorted_blocks) - 1):
            current = sorted_blocks[i]
            next_block = sorted_blocks[i + 1]

            # Check for overlapping blocks (potential phantom blocks)
            if current.end_line >= next_block.start_line:
                # This could be proper nesting or phantom blocks
                if not self._is_proper_nesting(current, next_block):
                    warnings.append(
                        "Potential phantom block: blocks at lines "
                        f"{current.start_line} and {next_block.start_line} "
                        "overlap improperly"
                    )

            # Check for suspiciously close blocks
            elif next_block.start_line - current.end_line == 1:
                # Adjacent blocks might indicate a phantom block
                if self._looks_like_phantom_block(current, next_block):
                    warnings.append(
                        "Suspicious adjacent blocks at lines "
                        f"{current.start_line} and {next_block.start_line}"
                    )

        return warnings

    def _is_proper_nesting(self, outer, inner) -> bool:
        """Check if blocks represent proper nesting."""
        # Proper nesting: inner block completely contained within outer
        return outer.start_line < inner.start_line and outer.end_line > inner.end_line

    def _looks_like_phantom_block(self, block1, block2) -> bool:
        """Check if adjacent blocks look like phantom blocks."""
        # Phantom blocks often have:
        # 1. Same fence type
        # 2. Very short content
        # 3. Adjacent positioning

        if block1.fence_type == block2.fence_type:
            # Same fence type is suspicious for adjacent blocks
            if len(block1.content.strip()) < 10 or len(block2.content.strip()) < 10:
                # Short content increases suspicion
                return True

        return False

    def filter_phantom_blocks(self, blocks: List) -> List:
        """
        Filter out likely phantom blocks from the list.

        Args:
            blocks: List of FencedBlock objects

        Returns:
            Filtered list of blocks
        """
        if len(blocks) <= 1:
            return blocks

        filtered_blocks = []
        sorted_blocks = sorted(blocks, key=lambda b: b.start_line)

        i = 0
        while i < len(sorted_blocks):
            current = sorted_blocks[i]

            # Check if this looks like a phantom block
            is_phantom = False

            if i < len(sorted_blocks) - 1:
                next_block = sorted_blocks[i + 1]

                # If blocks are adjacent and look suspicious
                if (
                    next_block.start_line - current.end_line == 1
                    and self._looks_like_phantom_block(current, next_block)
                ):
                    # Keep the longer/more substantial block
                    if len(current.content) >= len(next_block.content):
                        filtered_blocks.append(current)
                        i += 2  # Skip the next block
                    else:
                        is_phantom = True  # Skip current, will add next
                        i += 1
                else:
                    filtered_blocks.append(current)
                    i += 1
            else:
                # Last block
                if not is_phantom:
                    filtered_blocks.append(current)
                i += 1

        return filtered_blocks


# Convenience functions for TextRecoveryUtils
def create_text_recovery_utils(source_text: str):  # -> TextRecoveryUtils
    """
    Create text recovery utils (backward compatibility).

    Args:
        source_text: Original markdown text

    Returns:
        TextRecoveryUtils instance
    """
    return TextRecoveryUtils(source_text)


# Convenience functions for PhantomBlockPreventer
def validate_block_sequence(blocks: List) -> List[str]:
    """
    Convenience function to validate block sequence.

    Args:
        blocks: List of FencedBlock objects

    Returns:
        List of warning messages
    """
    preventer = PhantomBlockPreventer()
    return preventer.validate_block_sequence(blocks)


def filter_phantom_blocks(blocks: List) -> List:
    """
    Convenience function to filter phantom blocks.

    Args:
        blocks: List of FencedBlock objects

    Returns:
        Filtered list of blocks
    """
    preventer = PhantomBlockPreventer()
    return preventer.filter_phantom_blocks(blocks)
