"""Property-based tests for P0 test migration.

**Feature: p0-test-migration**

This module contains property-based tests to verify correctness properties
defined in the design document.
"""

import json

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from markdown_chunker_v2 import Chunk, ChunkConfig, MarkdownChunker
from markdown_chunker_v2.types import ChunkingResult


class TestChunkSimpleProperties:
    """Property tests for chunk_simple method."""

    @given(st.text(min_size=0, max_size=1000))
    @settings(max_examples=50, deadline=5000)
    def test_property_chunk_simple_json_serializable(self, text):
        """**Property 3: chunk_simple result is JSON-serializable**
        **Feature: p0-test-migration, Property 3: chunk_simple result is JSON-serializable**
        **Validates: Requirements 2.4**

        For any text input, the result of chunk_simple SHALL be serializable
        to JSON without errors.
        """
        chunker = MarkdownChunker()
        result = chunker.chunk_simple(text)

        # Must be JSON serializable
        try:
            json_str = json.dumps(result, ensure_ascii=False)
            # Must be deserializable back
            restored = json.loads(json_str)
            assert isinstance(restored, dict)
            assert "chunks" in restored
            assert "total_chunks" in restored
        except (TypeError, ValueError) as e:
            pytest.fail(f"chunk_simple result not JSON-serializable: {e}")


class TestChunkConfigProperties:
    """Property tests for ChunkConfig serialization."""

    @given(
        st.integers(min_value=500, max_value=10000),
        st.integers(min_value=50, max_value=200),
        st.integers(min_value=0, max_value=100),
        st.booleans(),
        st.one_of(st.none(), st.sampled_from(["structural", "fallback", "code_aware"])),
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_chunk_config_round_trip(
        self,
        max_chunk_size,
        min_chunk_size,
        overlap_size,
        preserve_atomic_blocks,
        strategy_override,
    ):
        """**Property 4: ChunkConfig round-trip serialization**
        **Feature: p0-test-migration, Property 4: ChunkConfig round-trip serialization**
        **Validates: Requirements 3.1, 3.2**

        For any valid ChunkConfig instance, calling to_dict() then from_dict()
        SHALL produce an equivalent ChunkConfig.
        """
        # Ensure constraints are met
        assume(min_chunk_size <= max_chunk_size)
        assume(overlap_size < max_chunk_size)

        original = ChunkConfig(
            max_chunk_size=max_chunk_size,
            min_chunk_size=min_chunk_size,
            overlap_size=overlap_size,
            preserve_atomic_blocks=preserve_atomic_blocks,
            strategy_override=strategy_override,
        )

        # Serialize to dict
        data = original.to_dict()
        assert isinstance(data, dict)

        # Deserialize back
        restored = ChunkConfig.from_dict(data)

        # Verify equivalence
        assert restored.max_chunk_size == original.max_chunk_size
        assert restored.min_chunk_size == original.min_chunk_size
        assert restored.overlap_size == original.overlap_size
        assert restored.preserve_atomic_blocks == original.preserve_atomic_blocks
        assert restored.strategy_override == original.strategy_override
        assert restored.enable_overlap == original.enable_overlap


def valid_chunk_strategy():
    """Generate valid chunks with proper constraints."""

    @st.composite
    def _valid_chunk(draw):
        content = draw(
            st.text(
                min_size=1,
                max_size=100,
                alphabet=st.characters(
                    whitelist_categories=("L", "N", "P", "S"),
                    min_codepoint=32,
                    max_codepoint=126,
                ),
            )
        )
        # Ensure content is not whitespace-only
        assume(content.strip())

        start_line = draw(st.integers(min_value=1, max_value=50))
        end_line = draw(st.integers(min_value=start_line, max_value=start_line + 50))

        metadata = {
            "chunk_index": draw(st.integers(min_value=0, max_value=10)),
            "content_type": draw(st.sampled_from(["text", "code", "table", "mixed"])),
            "strategy": draw(st.sampled_from(["structural", "fallback"])),
        }

        return Chunk(
            content=content, start_line=start_line, end_line=end_line, metadata=metadata
        )

    return _valid_chunk()


class TestChunkingResultProperties:
    """Property tests for ChunkingResult serialization."""

    @given(
        st.lists(valid_chunk_strategy(), min_size=0, max_size=3),
        st.sampled_from(["structural", "fallback", "auto"]),
        st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_chunking_result_round_trip(
        self, chunks, strategy_used, processing_time
    ):
        """**Property 5: ChunkingResult round-trip serialization**
        **Feature: p0-test-migration, Property 5: ChunkingResult round-trip serialization**
        **Validates: Requirements 3.3, 3.4**

        For any valid ChunkingResult instance, calling to_dict() then from_dict()
        SHALL produce an equivalent ChunkingResult.
        """
        original = ChunkingResult(
            chunks=chunks,
            strategy_used=strategy_used,
            processing_time=processing_time,
            total_chars=sum(len(c.content) for c in chunks),
            total_lines=sum(c.line_count for c in chunks),
        )

        # Serialize to dict
        data = original.to_dict()
        assert isinstance(data, dict)
        assert "chunks" in data

        # Deserialize back
        restored = ChunkingResult.from_dict(data)

        # Verify equivalence
        assert len(restored.chunks) == len(original.chunks)
        assert restored.strategy_used == original.strategy_used
        assert restored.processing_time == original.processing_time
        assert restored.chunk_count == original.chunk_count


class TestChunkProperties:
    """Property tests for Chunk serialization."""

    @given(
        st.text(
            min_size=1,
            max_size=200,
            alphabet=st.characters(
                whitelist_categories=("L", "N", "P", "S"),
                min_codepoint=32,
                max_codepoint=126,
            ),
        ).filter(lambda x: x.strip()),
        st.integers(min_value=1, max_value=50),
        st.integers(min_value=1, max_value=100),
        st.dictionaries(
            keys=st.from_regex(r"[a-z][a-z0-9_]*", fullmatch=True),
            values=st.one_of(
                st.text(max_size=50, alphabet="abcdefghijklmnopqrstuvwxyz"),
                st.integers(),
                st.booleans(),
            ),
            max_size=3,
        ),
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_chunk_to_dict_includes_line_count(
        self, content, start_line, end_line, metadata
    ):
        """**Property 6: Chunk.to_dict includes line_count**
        **Feature: p0-test-migration, Property 6: Chunk.to_dict includes line_count**
        **Validates: Requirements 3.5**

        For any Chunk instance, to_dict() SHALL include 'line_count' key
        equal to end_line - start_line + 1.
        """
        # Ensure start_line <= end_line
        if start_line > end_line:
            start_line, end_line = end_line, start_line

        chunk = Chunk(
            content=content, start_line=start_line, end_line=end_line, metadata=metadata
        )

        data = chunk.to_dict()

        # Verify line_count is present and correct
        assert "line_count" in data, "to_dict must include line_count"
        expected_line_count = end_line - start_line + 1
        assert (
            data["line_count"] == expected_line_count
        ), f"line_count should be {expected_line_count}, got {data['line_count']}"

        # Verify other required fields
        assert data["content"] == content
        assert data["start_line"] == start_line
        assert data["end_line"] == end_line
        assert data["size"] == len(content)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
