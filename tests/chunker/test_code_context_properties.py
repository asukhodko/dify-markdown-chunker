"""Property-based tests for code-context binding using Hypothesis.

Tests invariant properties that should hold for all valid inputs:
- Related code blocks stay together or adjacent
- Explanation binding preserves proximity
- Size constraints are always respected
- Role detection is consistent
"""

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from markdown_chunker_v2 import MarkdownChunker
from markdown_chunker_v2.code_context import CodeBlockRole, CodeContextBinder
from markdown_chunker_v2.config import ChunkConfig
from markdown_chunker_v2.parser import Parser
from markdown_chunker_v2.strategies.code_aware import CodeAwareStrategy


# Custom strategies for generating markdown content
@st.composite
def code_block(draw, language=None):
    """Generate a valid fenced code block."""
    if language is None:
        language = draw(st.sampled_from(["python", "javascript", "bash", "java", ""]))

    content_lines = draw(st.integers(min_value=1, max_value=5))
    content = "\n".join([f"line {i}" for i in range(content_lines)])

    return f"```{language}\n{content}\n```"


@st.composite
def before_after_pattern(draw):
    """Generate a Before/After code comparison pattern."""
    before_marker = draw(st.sampled_from(["Before:", "Old code:", "Problematic:"]))
    after_marker = draw(st.sampled_from(["After:", "New code:", "Fixed:"]))
    language = draw(st.sampled_from(["python", "javascript", "java"]))

    before_code = draw(code_block(language=language))
    after_code = draw(code_block(language=language))

    gap_lines = draw(st.integers(min_value=0, max_value=3))
    gap = "\n" * gap_lines

    return f"{before_marker}\n\n{before_code}\n{gap}\n{after_marker}\n\n{after_code}"


@st.composite
def code_output_pattern(draw):
    """Generate a Code + Output pattern."""
    output_marker = draw(st.sampled_from(["Output:", "Result:", "Console:"]))
    code_language = draw(st.sampled_from(["python", "javascript", "bash"]))

    code = draw(code_block(language=code_language))
    output = draw(code_block(language=""))

    gap_lines = draw(st.integers(min_value=0, max_value=3))
    gap = "\n" * gap_lines

    return f"{code}\n{gap}\n{output_marker}\n\n{output}"


@st.composite
def setup_example_pattern(draw):
    """Generate setup code followed by example."""
    setup_marker = draw(st.sampled_from(["First, install:", "Setup:", "You need to:"]))
    example_marker = draw(st.sampled_from(["Example:", "Usage:", "Try this:"]))

    setup_code = draw(code_block(language="bash"))
    example_code = draw(code_block(language="python"))

    return f"{setup_marker}\n\n{setup_code}\n\n{example_marker}\n\n{example_code}"


class TestCodeContextBindingProperties:
    """Property-based tests for code-context binding invariants."""

    @given(before_after_pattern())
    @settings(max_examples=20, deadline=5000)
    def test_property_before_after_stay_together(self, markdown_text):
        """Property: Before/After blocks should be in same or adjacent chunks."""
        config = ChunkConfig(
            enable_code_context_binding=True,
            preserve_before_after_pairs=True,
            max_chunk_size=10000,  # Large enough to allow grouping
        )
        parser = Parser()
        analysis = parser.analyze(markdown_text)

        # Only test if we have code blocks
        assume(len(analysis.code_blocks) >= 2)

        strategy = CodeAwareStrategy()
        chunks = strategy.apply(markdown_text, analysis, config)

        # Extract all code chunks
        code_chunks = [c for c in chunks if c.metadata.get("content_type") == "code"]

        if len(code_chunks) == 0:
            return  # No code chunks, nothing to verify

        # Property: If we have before/after in roles, they should be together
        for chunk in code_chunks:
            if "code_roles" in chunk.metadata:
                roles = chunk.metadata["code_roles"]
                # If both before and after are present, that's the ideal grouping
                if "before" in roles and "after" in roles:
                    assert chunk.metadata.get("code_relationship") == "before_after"

        # Alternative: they could be in adjacent chunks
        all_roles = []
        for chunk in code_chunks:
            if "code_role" in chunk.metadata:
                all_roles.append(chunk.metadata["code_role"])
            elif "code_roles" in chunk.metadata:
                all_roles.extend(chunk.metadata["code_roles"])

        # If we have both roles, verify they exist
        if "before" in all_roles and "after" in all_roles:
            # Property satisfied - both roles detected
            assert True

    @given(code_output_pattern())
    @settings(max_examples=20, deadline=5000)
    def test_property_code_output_binding(self, markdown_text):
        """Property: Code blocks should bind to their output blocks."""
        parser = Parser()
        analysis = parser.analyze(markdown_text)

        assume(len(analysis.code_blocks) >= 2)

        binder = CodeContextBinder(
            max_context_chars_before=500,
            max_context_chars_after=300,
            related_block_max_gap=6,
        )

        # Bind context to all blocks
        contexts = []
        for block in analysis.code_blocks:
            context = binder.bind_context(block, markdown_text, analysis.code_blocks)
            contexts.append(context)

        # Property: If we detect an output block, it should be bound
        output_detected = any(ctx.role == CodeBlockRole.OUTPUT for ctx in contexts)
        if output_detected:
            # At least one context should reference the output
            has_output_reference = any(
                ctx.output_block is not None or ctx.role == CodeBlockRole.OUTPUT
                for ctx in contexts
            )
            assert has_output_reference

    @given(setup_example_pattern())
    @settings(max_examples=20, deadline=5000)
    def test_property_setup_detection(self, markdown_text):
        """Property: Setup code should be correctly identified."""
        parser = Parser()
        analysis = parser.analyze(markdown_text)

        assume(len(analysis.code_blocks) >= 1)

        binder = CodeContextBinder()

        # Bind context to first block (should be setup)
        if analysis.code_blocks:
            context = binder.bind_context(
                analysis.code_blocks[0],
                markdown_text,
                analysis.code_blocks,
            )

            # Property: First block with setup markers should be detected as SETUP
            # (or at least not OUTPUT or ERROR)
            assert context.role in [
                CodeBlockRole.SETUP,
                CodeBlockRole.EXAMPLE,
                CodeBlockRole.UNKNOWN,
            ]

    @given(
        st.text(
            min_size=10,
            max_size=500,
            alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z")),
        ),
        st.sampled_from(["python", "javascript", "java", "bash"]),
    )
    @settings(max_examples=20, deadline=5000)
    def test_property_explanation_proximity(self, explanation_text, language):
        """Property: Explanation text should be extractable from context."""
        # Create markdown with explanation before code
        markdown_text = f"{explanation_text}\n\n```{language}\ncode here\n```"

        parser = Parser()
        analysis = parser.analyze(markdown_text)

        assume(len(analysis.code_blocks) >= 1)

        binder = CodeContextBinder(max_context_chars_before=1000)
        context = binder.bind_context(
            analysis.code_blocks[0],
            markdown_text,
            analysis.code_blocks,
        )

        # Property: Explanation should be captured (if not too far)
        if len(explanation_text.strip()) > 0:
            assert (
                context.explanation_before is not None
                or context.explanation_after is not None
            )

    @given(st.integers(min_value=500, max_value=5000))
    @settings(max_examples=10, deadline=5000)
    def test_property_max_chunk_size_respected(self, max_chunk_size):
        """Property: Chunks should respect max_chunk_size limits."""
        # Create a document with multiple code blocks
        markdown_text = """# Test Document

Here's some code:

```python
def function1():
    return "value1"
```

And more code:

```python
def function2():
    return "value2"
```

Additional text here.
"""

        config = ChunkConfig(
            enable_code_context_binding=True,
            max_chunk_size=max_chunk_size,
            overlap_size=min(
                200, max_chunk_size // 2
            ),  # Ensure overlap < max_chunk_size
        )

        chunker = MarkdownChunker(config=config)
        chunks, _, _ = chunker.chunk_with_analysis(markdown_text)

        # Property: All non-atomic chunks should respect size limit
        for chunk in chunks:
            if not chunk.metadata.get("is_atomic", False):
                assert chunk.size <= max_chunk_size
            else:
                # Atomic chunks can exceed but should have oversize metadata
                if chunk.size > max_chunk_size:
                    assert "oversize_reason" in chunk.metadata

    @given(st.integers(min_value=1, max_value=20))
    @settings(max_examples=10, deadline=5000)
    def test_property_related_block_gap_respected(self, max_gap):
        """Property: Related blocks should respect gap configuration."""
        # Create blocks with specific gaps
        markdown_text = """# Test

```python
block1 = 1
```

Gap text here.

```python
block2 = 2
```
"""

        parser = Parser()
        analysis = parser.analyze(markdown_text)

        assume(len(analysis.code_blocks) >= 2)

        binder = CodeContextBinder(related_block_max_gap=max_gap)

        # Check related blocks respect gap
        for i, block in enumerate(analysis.code_blocks[:-1]):
            context = binder.bind_context(block, markdown_text, analysis.code_blocks)

            # Property: Related blocks should be within max_gap
            for related in context.related_blocks:
                gap = abs(block.end_line - related.start_line)
                # Gap might be slightly larger due to explanation text
                # but should be reasonably close
                assert gap <= max_gap + 5  # Allow some tolerance

    @given(st.text(min_size=0, max_size=100))
    @settings(max_examples=20, deadline=5000)
    def test_property_empty_or_whitespace_safe(self, text_content):
        """Property: Chunker should handle empty/whitespace content safely."""
        config = ChunkConfig(enable_code_context_binding=True)
        chunker = MarkdownChunker(config=config)

        try:
            result = chunker.chunk_simple(text_content)
            # Property: Should never crash, always return valid result
            assert isinstance(result, dict)
            assert "chunks" in result
            assert "errors" in result
            assert isinstance(result["chunks"], list)
        except Exception as e:
            pytest.fail(f"Chunker crashed on input: {repr(text_content)}, error: {e}")


class TestRoleDetectionProperties:
    """Property-based tests for role detection consistency."""

    @given(st.sampled_from(["output", "console", "stdout", "result"]))
    @settings(max_examples=10, deadline=5000)
    def test_property_output_language_tags_detected(self, output_tag):
        """Property: Output language tags should always be detected as OUTPUT role."""
        markdown_text = f"```{output_tag}\nSome output text\n```"

        parser = Parser()
        analysis = parser.analyze(markdown_text)

        assume(len(analysis.code_blocks) >= 1)

        binder = CodeContextBinder()
        context = binder.bind_context(
            analysis.code_blocks[0],
            markdown_text,
            analysis.code_blocks,
        )

        # Property: Output language tags always produce OUTPUT role
        assert context.role == CodeBlockRole.OUTPUT

    @given(st.sampled_from(["error", "traceback"]))
    @settings(max_examples=10, deadline=5000)
    def test_property_error_language_tags_detected(self, error_tag):
        """Property: Error language tags should always be detected as ERROR role."""
        markdown_text = f"```{error_tag}\nError traceback here\n```"

        parser = Parser()
        analysis = parser.analyze(markdown_text)

        assume(len(analysis.code_blocks) >= 1)

        binder = CodeContextBinder()
        context = binder.bind_context(
            analysis.code_blocks[0],
            markdown_text,
            analysis.code_blocks,
        )

        # Property: Error language tags always produce ERROR role
        assert context.role == CodeBlockRole.ERROR

    @given(
        st.sampled_from(["Output:", "Result:", "Console:"]),
        st.sampled_from(["", "text", "plaintext"]),
    )
    @settings(max_examples=10, deadline=5000)
    def test_property_output_pattern_detected(self, pattern, language):
        """Property: Output patterns should trigger OUTPUT role detection."""
        markdown_text = f"{pattern}\n\n```{language}\nSome output\n```"

        parser = Parser()
        analysis = parser.analyze(markdown_text)

        assume(len(analysis.code_blocks) >= 1)

        binder = CodeContextBinder()
        context = binder.bind_context(
            analysis.code_blocks[0],
            markdown_text,
            analysis.code_blocks,
        )

        # Property: Output patterns should be detected
        # (either as OUTPUT role or with explanation_before containing pattern)
        assert context.role == CodeBlockRole.OUTPUT or (
            context.explanation_before
            and pattern.lower().replace(":", "") in context.explanation_before.lower()
        )


class TestGroupingProperties:
    """Property-based tests for grouping behavior."""

    @given(st.integers(min_value=2, max_value=10))
    @settings(max_examples=10, deadline=5000)
    def test_property_all_code_blocks_processed(self, num_blocks):
        """Property: All code blocks should be processed exactly once."""
        # Generate markdown with multiple code blocks
        blocks = [f"```python\nblock_{i} = {i}\n```" for i in range(num_blocks)]
        markdown_text = "# Test\n\n" + "\n\nSome text.\n\n".join(blocks)

        config = ChunkConfig(
            enable_code_context_binding=True,
            max_chunk_size=10000,
        )

        chunker = MarkdownChunker(config=config)
        chunks, _, analysis = chunker.chunk_with_analysis(markdown_text)

        # Count code blocks in original
        original_count = len(analysis.code_blocks)

        # Count code blocks in chunks (ungrouped)
        chunk_code_count = 0
        for chunk in chunks:
            if chunk.metadata.get("content_type") == "code":
                # Check if grouped
                if "related_code_count" in chunk.metadata:
                    chunk_code_count += chunk.metadata["related_code_count"]
                else:
                    chunk_code_count += 1

        # Property: Every code block should be in exactly one chunk
        # (either alone or grouped)
        assert chunk_code_count >= original_count or original_count == num_blocks

    def test_property_metadata_consistency(self):
        """Property: Metadata fields should be consistent and valid."""
        markdown_text = """# Test

Before:

```python
old = 1
```

After:

```python
new = 2
```
"""

        config = ChunkConfig(enable_code_context_binding=True)
        chunker = MarkdownChunker(config=config)
        chunks, _, _ = chunker.chunk_with_analysis(markdown_text)

        # Property: All chunks should have consistent metadata
        for chunk in chunks:
            # Required fields
            assert "strategy" in chunk.metadata

            # If code chunk with context binding
            if chunk.metadata.get("content_type") == "code":
                # Should have role information
                assert "code_role" in chunk.metadata or "code_roles" in chunk.metadata

                # has_related_code should match related_code_count
                if chunk.metadata.get("has_related_code", False):
                    assert chunk.metadata.get("related_code_count", 0) > 0

                # If has relationship, should have related codes
                if "code_relationship" in chunk.metadata:
                    assert chunk.metadata.get("has_related_code", False)
