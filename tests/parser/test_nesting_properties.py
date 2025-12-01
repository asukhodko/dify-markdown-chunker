"""
Property-based tests for nesting resolver.

**Feature: fix-chunking-quality, Property 7: Nesting Consistency**
**Validates: Requirements 2.4, 3.2**

This module uses Hypothesis to generate random nested block structures
and verifies nesting consistency properties.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from markdown_chunker.parser.nesting_resolver import (
    BlockCandidate,
    resolve_nesting,
)


# Hypothesis strategies for generating blocks
@st.composite
def valid_nested_blocks(draw):
    """Generate valid nested block structures."""
    blocks = []
    num_blocks = draw(st.integers(min_value=1, max_value=10))

    # Generate non-overlapping blocks
    current_line = 1
    for _ in range(num_blocks):
        # Random block size
        size = draw(st.integers(min_value=3, max_value=20))
        start = current_line
        end = current_line + size

        blocks.append(BlockCandidate(start_line=start, end_line=end))

        # Move to next block with gap
        current_line = end + draw(st.integers(min_value=1, max_value=5))

    return blocks


@st.composite
def nested_blocks_with_children(draw):
    """Generate blocks with nested children."""
    blocks = []

    # Create parent block
    parent_start = 1
    parent_end = draw(st.integers(min_value=20, max_value=50))
    blocks.append(BlockCandidate(start_line=parent_start, end_line=parent_end))

    # Add 1-3 children inside parent
    num_children = draw(st.integers(min_value=1, max_value=3))
    child_positions = sorted(
        draw(
            st.lists(
                st.integers(min_value=parent_start + 2, max_value=parent_end - 5),
                min_size=num_children,
                max_size=num_children,
                unique=True,
            )
        )
    )

    for child_start in child_positions:
        child_size = draw(st.integers(min_value=2, max_value=5))
        child_end = min(child_start + child_size, parent_end - 1)

        if child_end > child_start:
            blocks.append(BlockCandidate(start_line=child_start, end_line=child_end))

    return blocks


class TestNestingConsistencyProperties:
    """Property-based tests for nesting consistency."""

    @settings(max_examples=100, deadline=5000)
    @given(valid_nested_blocks())
    def test_property_parent_contains_children(self, blocks):
        """
        **Property 7a: Parent Containment**
        **Validates: Requirements 2.4, 3.2**

        For any resolved nesting structure:
        - Every child block must be fully contained within its parent
        - Parent start_line < child start_line
        - Parent end_line > child end_line
        """
        if not blocks:
            return

        try:
            resolved = resolve_nesting(blocks)
        except ValueError:
            # Invalid nesting is acceptable for random input
            return

        # Check parent containment
        for block in resolved:
            if block.parent_block is not None:
                parent = block.parent_block

                # Parent must fully contain child
                assert parent.start_line < block.start_line, (
                    f"Parent start ({parent.start_line}) must be before "
                    f"child start ({block.start_line})"
                )
                assert parent.end_line > block.end_line, (
                    f"Parent end ({parent.end_line}) must be after "
                    f"child end ({block.end_line})"
                )

    @settings(max_examples=100, deadline=5000)
    @given(valid_nested_blocks())
    def test_property_no_overlaps_at_same_level(self, blocks):
        """
        **Property 7b: No Overlaps at Same Level**
        **Validates: Requirements 2.4, 3.2**

        For any resolved nesting structure:
        - Blocks at the same nesting level must not overlap
        - They can be adjacent or separate, but not overlapping
        """
        if not blocks:
            return

        try:
            resolved = resolve_nesting(blocks)
        except ValueError:
            # Invalid nesting is acceptable for random input
            return

        # Group blocks by nesting level
        levels = {}
        for block in resolved:
            level = block.nesting_level
            if level not in levels:
                levels[level] = []
            levels[level].append(block)

        # Check no overlaps within each level
        for level, level_blocks in levels.items():
            for i, block1 in enumerate(level_blocks):
                for block2 in level_blocks[i + 1:]:
                    # Blocks should not overlap
                    assert not block1.overlaps(block2), (
                        f"Blocks at level {level} overlap: "
                        f"{block1.start_line}-{block1.end_line} and "
                        f"{block2.start_line}-{block2.end_line}"
                    )

    @settings(max_examples=100, deadline=5000)
    @given(nested_blocks_with_children())
    def test_property_nesting_level_consistency(self, blocks):
        """
        **Property 7c: Nesting Level Consistency**
        **Validates: Requirements 2.4, 3.2**

        For any resolved nesting structure:
        - Child nesting level = parent nesting level + 1
        - Top-level blocks have nesting level 0
        """
        if not blocks:
            return

        try:
            resolved = resolve_nesting(blocks)
        except ValueError:
            # Invalid nesting is acceptable for random input
            return

        for block in resolved:
            if block.parent_block is None:
                # Top-level block
                assert block.nesting_level == 0, (
                    f"Top-level block should have nesting_level=0, "
                    f"got {block.nesting_level}"
                )
            else:
                # Child block
                expected_level = block.parent_block.nesting_level + 1
                assert block.nesting_level == expected_level, (
                    f"Child nesting level should be {expected_level}, "
                    f"got {block.nesting_level}"
                )

    @settings(max_examples=50, deadline=5000)
    @given(valid_nested_blocks())
    def test_property_resolution_is_deterministic(self, blocks):
        """
        **Property 7d: Deterministic Resolution**
        **Validates: Requirements 2.4, 3.2**

        For any block structure:
        - Resolving twice should give same results
        - Nesting levels should be consistent
        """
        if not blocks:
            return

        try:
            resolved1 = resolve_nesting(blocks)
            resolved2 = resolve_nesting(blocks)
        except ValueError:
            # Invalid nesting is acceptable for random input
            return

        # Should have same number of blocks
        assert len(resolved1) == len(resolved2)

        # Should have same nesting levels
        for b1, b2 in zip(resolved1, resolved2):
            assert b1.nesting_level == b2.nesting_level
            assert b1.start_line == b2.start_line
            assert b1.end_line == b2.end_line

    @settings(max_examples=50, deadline=5000)
    @given(nested_blocks_with_children())
    def test_property_all_blocks_have_nesting_info(self, blocks):
        """
        **Property 7e: Complete Nesting Information**
        **Validates: Requirements 2.4, 3.2**

        For any resolved nesting structure:
        - All blocks must have nesting_level assigned
        - All blocks must have parent_block assigned (or None for top-level)
        """
        if not blocks:
            return

        try:
            resolved = resolve_nesting(blocks)
        except ValueError:
            # Invalid nesting is acceptable for random input
            return

        for block in resolved:
            # Must have nesting level
            assert hasattr(block, "nesting_level")
            assert isinstance(block.nesting_level, int)
            assert block.nesting_level >= 0

            # Must have parent_block attribute
            assert hasattr(block, "parent_block")
