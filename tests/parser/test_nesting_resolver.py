"""
Tests for nesting resolver.

This module tests the nesting resolution functionality for fenced blocks.
"""

import pytest

from markdown_chunker.parser.nesting_resolver import (
    BlockCandidate,
    NestingResolver,
    get_children,
    get_max_nesting_depth,
    get_nesting_tree,
    resolve_nesting,
    validate_block_nesting,
)


class TestBlockCandidate:
    """Test BlockCandidate class."""

    def test_contains_true(self):
        """Test that contains() returns True for proper containment."""
        outer = BlockCandidate(start_line=1, end_line=10)
        inner = BlockCandidate(start_line=3, end_line=7)

        assert outer.contains(inner)
        assert not inner.contains(outer)

    def test_contains_false_separate(self):
        """Test that contains() returns False for separate blocks."""
        block1 = BlockCandidate(start_line=1, end_line=5)
        block2 = BlockCandidate(start_line=10, end_line=15)

        assert not block1.contains(block2)
        assert not block2.contains(block1)

    def test_contains_false_adjacent(self):
        """Test that contains() returns False for adjacent blocks."""
        block1 = BlockCandidate(start_line=1, end_line=5)
        block2 = BlockCandidate(start_line=5, end_line=10)

        assert not block1.contains(block2)
        assert not block2.contains(block1)

    def test_overlaps_true(self):
        """Test that overlaps() returns True for overlapping blocks."""
        block1 = BlockCandidate(start_line=1, end_line=7)
        block2 = BlockCandidate(start_line=5, end_line=10)

        assert block1.overlaps(block2)
        assert block2.overlaps(block1)

    def test_overlaps_false_separate(self):
        """Test that overlaps() returns False for separate blocks."""
        block1 = BlockCandidate(start_line=1, end_line=5)
        block2 = BlockCandidate(start_line=10, end_line=15)

        assert not block1.overlaps(block2)
        assert not block2.overlaps(block1)

    def test_overlaps_false_containment(self):
        """Test that overlaps() returns False for proper containment."""
        outer = BlockCandidate(start_line=1, end_line=10)
        inner = BlockCandidate(start_line=3, end_line=7)

        assert not outer.overlaps(inner)
        assert not inner.overlaps(outer)


class TestNestingResolver:
    """Test NestingResolver class."""

    def test_flat_blocks_no_nesting(self):
        """Test resolution of flat blocks (no nesting)."""
        resolver = NestingResolver()
        resolver.add_block(BlockCandidate(start_line=1, end_line=5))
        resolver.add_block(BlockCandidate(start_line=10, end_line=15))
        resolver.add_block(BlockCandidate(start_line=20, end_line=25))

        blocks = resolver.resolve()

        assert len(blocks) == 3
        for block in blocks:
            assert block.nesting_level == 0
            assert block.parent_block is None

    def test_simple_nesting_one_level(self):
        """Test resolution of simple one-level nesting."""
        resolver = NestingResolver()
        outer = BlockCandidate(start_line=1, end_line=10)
        inner = BlockCandidate(start_line=3, end_line=7)

        resolver.add_block(outer)
        resolver.add_block(inner)

        blocks = resolver.resolve()

        # Find blocks in resolved list
        outer_resolved = next(b for b in blocks if b.start_line == 1)
        inner_resolved = next(b for b in blocks if b.start_line == 3)

        assert outer_resolved.nesting_level == 0
        assert outer_resolved.parent_block is None

        assert inner_resolved.nesting_level == 1
        assert inner_resolved.parent_block == outer_resolved

    def test_deep_nesting_multiple_levels(self):
        """Test resolution of deep nesting (multiple levels)."""
        resolver = NestingResolver()
        level0 = BlockCandidate(start_line=1, end_line=20)
        level1 = BlockCandidate(start_line=3, end_line=18)
        level2 = BlockCandidate(start_line=5, end_line=15)
        level3 = BlockCandidate(start_line=7, end_line=12)

        resolver.add_block(level0)
        resolver.add_block(level1)
        resolver.add_block(level2)
        resolver.add_block(level3)

        blocks = resolver.resolve()

        # Find blocks
        b0 = next(b for b in blocks if b.start_line == 1)
        b1 = next(b for b in blocks if b.start_line == 3)
        b2 = next(b for b in blocks if b.start_line == 5)
        b3 = next(b for b in blocks if b.start_line == 7)

        assert b0.nesting_level == 0
        assert b1.nesting_level == 1
        assert b2.nesting_level == 2
        assert b3.nesting_level == 3

        assert b0.parent_block is None
        assert b1.parent_block == b0
        assert b2.parent_block == b1
        assert b3.parent_block == b2

    def test_overlapping_blocks_raises_error(self):
        """Test that overlapping blocks raise ValueError."""
        resolver = NestingResolver()
        resolver.add_block(BlockCandidate(start_line=1, end_line=10))
        resolver.add_block(BlockCandidate(start_line=5, end_line=15))

        with pytest.raises(ValueError, match="Invalid nesting.*overlap"):
            resolver.resolve()

    def test_multiple_children_same_parent(self):
        """Test resolution with multiple children of same parent."""
        resolver = NestingResolver()
        parent = BlockCandidate(start_line=1, end_line=20)
        child1 = BlockCandidate(start_line=3, end_line=7)
        child2 = BlockCandidate(start_line=10, end_line=15)

        resolver.add_block(parent)
        resolver.add_block(child1)
        resolver.add_block(child2)

        blocks = resolver.resolve()

        p = next(b for b in blocks if b.start_line == 1)
        c1 = next(b for b in blocks if b.start_line == 3)
        c2 = next(b for b in blocks if b.start_line == 10)

        assert p.nesting_level == 0
        assert c1.nesting_level == 1
        assert c2.nesting_level == 1

        assert c1.parent_block == p
        assert c2.parent_block == p

    def test_empty_blocks_list(self):
        """Test resolution with no blocks."""
        resolver = NestingResolver()
        blocks = resolver.resolve()

        assert blocks == []


class TestResolveNesting:
    """Test resolve_nesting convenience function."""

    def test_resolve_nesting_flat(self):
        """Test resolve_nesting with flat blocks."""
        blocks = [
            BlockCandidate(start_line=1, end_line=5),
            BlockCandidate(start_line=10, end_line=15),
        ]

        resolved = resolve_nesting(blocks)

        assert len(resolved) == 2
        assert all(b.nesting_level == 0 for b in resolved)

    def test_resolve_nesting_nested(self):
        """Test resolve_nesting with nested blocks."""
        blocks = [
            BlockCandidate(start_line=1, end_line=10),
            BlockCandidate(start_line=3, end_line=7),
        ]

        resolved = resolve_nesting(blocks)

        outer = next(b for b in resolved if b.start_line == 1)
        inner = next(b for b in resolved if b.start_line == 3)

        assert outer.nesting_level == 0
        assert inner.nesting_level == 1
        assert inner.parent_block == outer

    def test_resolve_nesting_empty(self):
        """Test resolve_nesting with empty list."""
        resolved = resolve_nesting([])
        assert resolved == []


class TestValidateBlockNesting:
    """Test validate_block_nesting function."""

    def test_validate_valid_nesting(self):
        """Test validation of valid nesting."""
        blocks = [
            BlockCandidate(start_line=1, end_line=10),
            BlockCandidate(start_line=3, end_line=7),
        ]

        assert validate_block_nesting(blocks) is True

    def test_validate_invalid_nesting(self):
        """Test validation of invalid nesting (overlapping)."""
        blocks = [
            BlockCandidate(start_line=1, end_line=10),
            BlockCandidate(start_line=5, end_line=15),
        ]

        assert validate_block_nesting(blocks) is False

    def test_validate_empty_list(self):
        """Test validation of empty list."""
        assert validate_block_nesting([]) is True


class TestUtilityFunctions:
    """Test utility functions."""

    def test_get_nesting_tree(self):
        """Test get_nesting_tree function."""
        blocks = [
            BlockCandidate(start_line=1, end_line=20, nesting_level=0),
            BlockCandidate(start_line=3, end_line=18, nesting_level=1),
            BlockCandidate(start_line=5, end_line=15, nesting_level=2),
            BlockCandidate(start_line=25, end_line=30, nesting_level=0),
        ]

        tree = get_nesting_tree(blocks)

        assert len(tree) == 3
        assert len(tree[0]) == 2
        assert len(tree[1]) == 1
        assert len(tree[2]) == 1

    def test_get_children(self):
        """Test get_children function."""
        parent = BlockCandidate(start_line=1, end_line=20)
        child1 = BlockCandidate(start_line=3, end_line=7, parent_block=parent)
        child2 = BlockCandidate(start_line=10, end_line=15, parent_block=parent)
        other = BlockCandidate(start_line=25, end_line=30)

        all_blocks = [parent, child1, child2, other]
        children = get_children(parent, all_blocks)

        assert len(children) == 2
        assert child1 in children
        assert child2 in children
        assert other not in children

    def test_get_max_nesting_depth(self):
        """Test get_max_nesting_depth function."""
        blocks = [
            BlockCandidate(start_line=1, end_line=20, nesting_level=0),
            BlockCandidate(start_line=3, end_line=18, nesting_level=1),
            BlockCandidate(start_line=5, end_line=15, nesting_level=2),
            BlockCandidate(start_line=7, end_line=12, nesting_level=3),
        ]

        assert get_max_nesting_depth(blocks) == 3

    def test_get_max_nesting_depth_empty(self):
        """Test get_max_nesting_depth with empty list."""
        assert get_max_nesting_depth([]) == 0


class TestEdgeCases:
    """Test edge cases."""

    def test_adjacent_blocks_not_overlapping(self):
        """Test that adjacent blocks are not considered overlapping."""
        blocks = [
            BlockCandidate(start_line=1, end_line=5),
            BlockCandidate(start_line=5, end_line=10),
        ]

        assert validate_block_nesting(blocks) is True

    def test_single_block(self):
        """Test resolution with single block."""
        blocks = [BlockCandidate(start_line=1, end_line=10)]
        resolved = resolve_nesting(blocks)

        assert len(resolved) == 1
        assert resolved[0].nesting_level == 0
        assert resolved[0].parent_block is None

    def test_blocks_with_metadata(self):
        """Test that block metadata is preserved during resolution."""
        blocks = [
            BlockCandidate(
                start_line=1,
                end_line=10,
                block_type="code",
                language="python",
                fence_char="`",
                fence_length=3,
            ),
            BlockCandidate(
                start_line=3,
                end_line=7,
                block_type="code",
                language="javascript",
                fence_char="`",
                fence_length=4,
            ),
        ]

        resolved = resolve_nesting(blocks)

        outer = next(b for b in resolved if b.start_line == 1)
        inner = next(b for b in resolved if b.start_line == 3)

        assert outer.language == "python"
        assert outer.fence_length == 3
        assert inner.language == "javascript"
        assert inner.fence_length == 4
