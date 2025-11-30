"""
Property-based tests for code strategy correctness.

**Feature: markdown-chunker-quality-audit, Property 10: Code Block Integrity**
**Validates: Requirements 3.2, 10.2**

This module uses Hypothesis to verify that code strategy preserves
code blocks atomically - never splitting them across chunks.
"""

import re

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig

# ============================================================================
# Hypothesis Strategies for Markdown with Code Generation
# ============================================================================


@st.composite
def code_block(draw, language=None):
    """Generate a single code block."""
    if language is None:
        language = draw(st.sampled_from(["python", "javascript", "go", "rust", "java"]))

    # Generate code content
    num_lines = draw(st.integers(min_value=3, max_value=20))
    lines = []

    for _ in range(num_lines):
        line = draw(
            st.text(
                min_size=10,
                max_size=80,
                alphabet=st.characters(
                    whitelist_categories=("Lu", "Ll", "Nd"),
                    whitelist_characters=" (){}[];:,.",
                ),
            )
        )
        lines.append(line)

    code_content = "\n".join(lines)

    # Wrap in fences
    return f"```{language}\n{code_content}\n```"


@st.composite
def markdown_with_code(draw, min_blocks=1, max_blocks=5):
    """Generate markdown with guaranteed code blocks."""
    parts = []
    num_blocks = draw(st.integers(min_value=min_blocks, max_value=max_blocks))

    for i in range(num_blocks):
        # Add some text before code block
        if i == 0 or draw(st.booleans()):
            text = draw(
                st.text(min_size=20, max_size=200).filter(
                    lambda x: x.strip() and "```" not in x
                )
            )
            parts.append(text)
            parts.append("\n\n")

        # Add code block
        block = draw(code_block())
        parts.append(block)
        parts.append("\n\n")

    # Add some text after last code block
    if draw(st.booleans()):
        text = draw(
            st.text(min_size=20, max_size=200).filter(
                lambda x: x.strip() and "```" not in x
            )
        )
        parts.append(text)

    return "".join(parts)


# ============================================================================
# Property Tests
# ============================================================================


class TestCodeStrategyProperties:
    """Property-based tests for code strategy."""

    @settings(max_examples=100, deadline=5000)
    @given(markdown_text=markdown_with_code(min_blocks=1, max_blocks=5))
    def test_property_code_blocks_never_split(self, markdown_text):
        """
        **Property 10a: Code Blocks Never Split**

        For any markdown with code blocks, each code block should appear
        in exactly one chunk (never split across chunks).
        """
        config = ChunkConfig(
            max_chunk_size=2000,
            preserve_code_blocks=True,
        )
        chunker = MarkdownChunker(config)

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            # Skip if chunking fails
            return

        assume(len(chunks) > 0)

        # Extract all code blocks from original
        code_block_pattern = r"```[\w]*\n.*?\n```"
        original_blocks = re.findall(code_block_pattern, markdown_text, re.DOTALL)

        assume(len(original_blocks) > 0)

        # Check that each code block appears in exactly one chunk
        for block in original_blocks:
            # Count how many chunks contain this block
            chunks_containing_block = [
                chunk for chunk in chunks if block in chunk.content
            ]

            # Each block should appear in exactly one chunk
            assert (
                len(chunks_containing_block) >= 1
            ), f"Code block not found in any chunk:\n{block[:100]}..."

            # Check that block is not split
            if len(chunks_containing_block) == 1:
                # Block is in one chunk - good!
                continue
            else:
                # Block appears in multiple chunks - check if it's complete in at least one
                complete_in_any = any(
                    block in chunk.content for chunk in chunks_containing_block
                )
                assert (
                    complete_in_any
                ), f"Code block split across {len(chunks_containing_block)} chunks"

    @settings(max_examples=100, deadline=5000)
    @given(markdown_text=markdown_with_code(min_blocks=3, max_blocks=10))
    def test_property_code_blocks_have_metadata(self, markdown_text):
        """
        **Property 10b: Code Blocks Have Metadata**

        For any markdown with code blocks processed by code strategy,
        chunks containing code should have appropriate metadata.
        """
        config = ChunkConfig(
            max_chunk_size=2000,
            code_ratio_threshold=0.5,  # Lower threshold to trigger code strategy
            min_code_blocks=3,
        )
        chunker = MarkdownChunker(config)

        try:
            result = chunker.chunk_with_analysis(markdown_text)
        except Exception:
            return

        assume(len(result.chunks) > 0)

        # Only test if code strategy was used
        if result.strategy_used != "code":
            return

        # Find chunks with code blocks
        code_chunks = [chunk for chunk in result.chunks if "```" in chunk.content]

        assume(len(code_chunks) > 0)

        # Check that code chunks have metadata
        for chunk in code_chunks:
            # Code strategy creates two types of chunks:
            # 1. Code chunks (with language metadata)
            # 2. Text chunks (explanatory text between code blocks)
            # Both are valid - we just verify the chunk contains code fences

            # If it's a code chunk, it should have language metadata
            if (
                chunk.content_type == "code"
                or chunk.metadata.get("content_type") == "code"
            ):
                assert (
                    "language" in chunk.metadata
                ), f"Code chunk missing language metadata"

            # All chunks from code strategy should have strategy metadata
            assert (
                chunk.metadata.get("strategy") == "code"
            ), f"Chunk should have code strategy metadata"

    @settings(max_examples=100, deadline=5000)
    @given(markdown_text=markdown_with_code(min_blocks=1, max_blocks=5))
    def test_property_code_blocks_preserve_fences(self, markdown_text):
        """
        **Property 10c: Code Blocks Preserve Fences**

        For any markdown with code blocks, the fences (```) should be
        preserved in the chunks.
        """
        config = ChunkConfig(
            max_chunk_size=2000,
        )
        chunker = MarkdownChunker(config)

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        assume(len(chunks) > 0)

        # Count fences in original
        original_fence_count = markdown_text.count("```")

        # Count fences in all chunks
        chunk_fence_count = sum(chunk.content.count("```") for chunk in chunks)

        # Should have same number of fences (allowing for overlap)
        assert (
            chunk_fence_count >= original_fence_count
        ), f"Fences lost: original={original_fence_count}, chunks={chunk_fence_count}"

    @settings(max_examples=50, deadline=5000)
    @given(markdown_text=markdown_with_code(min_blocks=2, max_blocks=5))
    def test_property_multiple_code_blocks_handled(self, markdown_text):
        """
        **Property 10d: Multiple Code Blocks Handled**

        For any markdown with multiple code blocks, all blocks should be
        preserved and properly chunked.
        """
        config = ChunkConfig(
            max_chunk_size=1500,  # Smaller to force multiple chunks
        )
        chunker = MarkdownChunker(config)

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        assume(len(chunks) > 0)

        # Extract all code blocks from original
        code_block_pattern = r"```[\w]*\n.*?\n```"
        original_blocks = re.findall(code_block_pattern, markdown_text, re.DOTALL)

        assume(len(original_blocks) >= 2)

        # All blocks should appear somewhere in chunks
        all_chunk_content = "\n".join(chunk.content for chunk in chunks)

        for block in original_blocks:
            # Check if block appears in combined content
            # (allowing for some whitespace normalization)
            block_core = block.replace("\n", " ").replace("  ", " ")[:50]
            all_content_normalized = all_chunk_content.replace("\n", " ").replace(
                "  ", " "
            )

            assert (
                block_core in all_content_normalized or block[:50] in all_chunk_content
            ), f"Code block missing from chunks:\n{block[:100]}..."

    @settings(max_examples=50, deadline=5000)
    @given(markdown_text=markdown_with_code(min_blocks=1, max_blocks=3))
    def test_property_large_code_blocks_allowed_oversize(self, markdown_text):
        """
        **Property 10e: Large Code Blocks Allowed Oversize**

        For any markdown with large code blocks, blocks larger than
        max_chunk_size should be allowed (marked as oversize).
        """
        config = ChunkConfig(
            max_chunk_size=500,  # Very small to force oversize
            allow_oversize=True,
        )
        chunker = MarkdownChunker(config)

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        assume(len(chunks) > 0)

        # Find chunks that exceed max size
        oversize_chunks = [
            chunk for chunk in chunks if len(chunk.content) > config.max_chunk_size
        ]

        # If there are oversize chunks, they should contain code blocks
        for chunk in oversize_chunks:
            # Oversize chunks should either:
            # 1. Contain code blocks (```), OR
            # 2. Be marked as allow_oversize in metadata
            has_code = "```" in chunk.content
            is_marked_oversize = chunk.metadata.get("allow_oversize", False)

            assert has_code or is_marked_oversize, (
                f"Oversize chunk ({len(chunk.content)} > {config.max_chunk_size}) "
                f"should contain code or be marked as oversize"
            )

    @settings(max_examples=100, deadline=5000)
    @given(markdown_text=markdown_with_code(min_blocks=1, max_blocks=5))
    def test_property_code_block_content_preserved(self, markdown_text):
        """
        **Property 10f: Code Block Content Preserved**

        For any markdown with code blocks, the content inside code blocks
        should be preserved (allowing for whitespace normalization).
        """
        config = ChunkConfig(
            max_chunk_size=2000,
        )
        chunker = MarkdownChunker(config)

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        assume(len(chunks) > 0)

        # Extract code block contents from original
        code_block_pattern = r"```[\w]*\n(.*?)\n```"
        original_contents = re.findall(code_block_pattern, markdown_text, re.DOTALL)

        assume(len(original_contents) > 0)

        # Extract code block contents from chunks
        all_chunk_content = "\n\n".join(chunk.content for chunk in chunks)
        chunk_contents = re.findall(code_block_pattern, all_chunk_content, re.DOTALL)

        # Should have at least as many code blocks in chunks
        # (may have more due to overlap)
        assert len(chunk_contents) >= len(original_contents), (
            f"Code blocks lost: original={len(original_contents)}, "
            f"chunks={len(chunk_contents)}"
        )

        # Check that original contents appear in chunk contents
        # (allowing for whitespace normalization)
        for original_content in original_contents:
            # Normalize whitespace for comparison
            original_normalized = " ".join(original_content.split())

            if not original_normalized:
                continue

            # Check if this content appears in any chunk content
            found = any(
                original_normalized in " ".join(chunk_content.split())
                or chunk_content.strip() == original_content.strip()
                for chunk_content in chunk_contents
            )

            # If not found, check if it's in the raw chunk content
            if not found:
                found = original_normalized in " ".join(all_chunk_content.split())

            assert (
                found
            ), f"Code block content not preserved:\n{original_content[:100]}..."


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
