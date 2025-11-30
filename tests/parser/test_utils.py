"""
Test utilities for common operations and assertions.

This module provides helper functions and utilities used across
multiple test modules.
"""

import os
from typing import Any, Dict, List

from markdown_chunker.parser.types import FencedBlock


class TestUtils:
    """Utilities for testing fenced block extraction."""

    @staticmethod
    def load_fixture(filename: str) -> str:
        """Load a test fixture file."""
        fixture_path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
        with open(fixture_path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def assert_block_boundaries(
        block: FencedBlock, expected_start: int, expected_end: int
    ):
        """Assert block has expected start and end lines."""
        assert (
            block.start_line == expected_start
        ), f"Expected start_line {expected_start}, got {block.start_line}"
        assert (
            block.end_line == expected_end
        ), f"Expected end_line {expected_end}, got {block.end_line}"

    @staticmethod
    def assert_block_content(block: FencedBlock, expected_content: str):
        """Assert block has expected content."""
        actual_content = block.content.strip()
        expected_content = expected_content.strip()
        assert (
            actual_content == expected_content
        ), f"Expected content '{expected_content}', got '{actual_content}'"

    @staticmethod
    def assert_nesting_level(block: FencedBlock, expected_level: int):
        """Assert block has expected nesting level."""
        assert (
            block.nesting_level == expected_level
        ), f"Expected nesting level {expected_level}, got {block.nesting_level}"

    @staticmethod
    def group_blocks_by_language(
        blocks: List[FencedBlock],
    ) -> Dict[str, List[FencedBlock]]:
        """Group blocks by language."""
        grouped = {}
        for block in blocks:
            language = block.language or "unknown"
            if language not in grouped:
                grouped[language] = []
            grouped[language].append(block)
        return grouped

    @staticmethod
    def group_blocks_by_nesting_level(
        blocks: List[FencedBlock],
    ) -> Dict[int, List[FencedBlock]]:
        """Group blocks by nesting level."""
        grouped = {}
        for block in blocks:
            level = block.nesting_level
            if level not in grouped:
                grouped[level] = []
            grouped[level].append(block)
        return grouped

    @staticmethod
    def assert_no_overlapping_blocks(blocks: List[FencedBlock]):
        """Assert that blocks don't overlap improperly."""
        sorted_blocks = sorted(blocks, key=lambda b: b.start_line)

        for i in range(len(sorted_blocks) - 1):
            current = sorted_blocks[i]
            next_block = sorted_blocks[i + 1]

            # Check for improper overlap
            if current.end_line >= next_block.start_line:
                # This could be proper nesting
                is_proper_nesting = (
                    current.start_line < next_block.start_line
                    and current.end_line > next_block.end_line
                )

                assert is_proper_nesting, (
                    f"Improper overlap between blocks {i} and {i+1}: "
                    f"Block {i} ends at {current.end_line}, "
                    f"Block {i+1} starts at {next_block.start_line}"
                )

    @staticmethod
    def assert_proper_containment(outer: FencedBlock, inner: FencedBlock):
        """Assert that inner block is properly contained in outer block."""
        assert outer.start_line < inner.start_line, (
            "Outer block should start before inner: "
            f"{outer.start_line} >= {inner.start_line}"
        )
        assert (
            outer.end_line > inner.end_line
        ), f"Outer block should end after inner: {outer.end_line} <= {inner.end_line}"

    @staticmethod
    def create_test_block(
        content: str = "test content",
        language: str = "python",
        start_line: int = 1,
        end_line: int = 3,
        nesting_level: int = 0,
        is_closed: bool = True,
    ) -> FencedBlock:
        """Create a test FencedBlock with default values."""
        return FencedBlock(
            content=content,
            language=language,
            fence_type="```",
            fence_length=3,
            start_line=start_line,
            end_line=end_line,
            start_offset=0,
            end_offset=len(content),
            nesting_level=nesting_level,
            is_closed=is_closed,
            raw_content=f"```{language}\n{content}\n```",
        )

    @staticmethod
    def assert_blocks_sorted_by_start_line(blocks: List[FencedBlock]):
        """Assert that blocks are sorted by start line."""
        for i in range(len(blocks) - 1):
            current = blocks[i]
            next_block = blocks[i + 1]
            assert current.start_line <= next_block.start_line, (
                f"Blocks not sorted: block {i} starts at {current.start_line}, "
                f"block {i+1} starts at {next_block.start_line}"
            )

    @staticmethod
    def get_block_summary(blocks: List[FencedBlock]) -> Dict[str, Any]:
        """Get a summary of extracted blocks."""
        if not blocks:
            return {
                "total_blocks": 0,
                "languages": [],
                "nesting_levels": [],
                "closed_blocks": 0,
                "unclosed_blocks": 0,
            }

        languages = list(set(b.language for b in blocks if b.language))
        nesting_levels = list(set(b.nesting_level for b in blocks))
        closed_count = sum(1 for b in blocks if b.is_closed)
        unclosed_count = len(blocks) - closed_count

        return {
            "total_blocks": len(blocks),
            "languages": sorted(languages),
            "nesting_levels": sorted(nesting_levels),
            "closed_blocks": closed_count,
            "unclosed_blocks": unclosed_count,
            "max_nesting_level": max(nesting_levels) if nesting_levels else 0,
        }

    @staticmethod
    def assert_block_count_by_language(
        blocks: List[FencedBlock], expected_counts: Dict[str, int]
    ):
        """Assert expected counts of blocks by language."""
        actual_counts = {}
        for block in blocks:
            language = block.language or "unknown"
            actual_counts[language] = actual_counts.get(language, 0) + 1

        for language, expected_count in expected_counts.items():
            actual_count = actual_counts.get(language, 0)
            assert (
                actual_count == expected_count
            ), f"Expected {expected_count} {language} blocks, got {actual_count}"

    @staticmethod
    def assert_nesting_hierarchy(blocks: List[FencedBlock]):
        """Assert that nesting hierarchy is valid."""
        by_level = TestUtils.group_blocks_by_nesting_level(blocks)

        # Check that each level properly contains the next level
        max_level = max(by_level.keys()) if by_level else 0

        for level in range(max_level):
            if level in by_level and (level + 1) in by_level:
                outer_blocks = by_level[level]
                inner_blocks = by_level[level + 1]

                # Each inner block should be contained in some outer block
                for inner in inner_blocks:
                    contained = False
                    for outer in outer_blocks:
                        if (
                            outer.start_line < inner.start_line
                            and outer.end_line > inner.end_line
                        ):
                            contained = True
                            break

                    assert contained, (
                        f"Block at level {level + 1} "
                        f"(lines {inner.start_line}-{inner.end_line}) "
                        f"not properly contained in any level {level} block"
                    )


# Convenience functions for common assertions
def assert_block_count(blocks: List[FencedBlock], expected_count: int):
    """Assert expected number of blocks."""
    actual_count = len(blocks)
    assert (
        actual_count == expected_count
    ), f"Expected {expected_count} blocks, got {actual_count}"


def assert_languages_present(blocks: List[FencedBlock], expected_languages: List[str]):
    """Assert that expected languages are present."""
    actual_languages = set(b.language for b in blocks if b.language)
    expected_set = set(expected_languages)

    missing = expected_set - actual_languages
    assert not missing, f"Missing expected languages: {missing}"


def assert_max_nesting_level(blocks: List[FencedBlock], expected_max_level: int):
    """Assert maximum nesting level."""
    if not blocks:
        actual_max = 0
    else:
        actual_max = max(b.nesting_level for b in blocks)

    assert (
        actual_max == expected_max_level
    ), f"Expected max nesting level {expected_max_level}, got {actual_max}"
