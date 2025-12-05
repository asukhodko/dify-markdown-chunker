"""Tests for serialization functionality.

Migration note: Updated for v2 API (December 2025)
"""

import json

from markdown_chunker_v2 import Chunk, ChunkConfig
from markdown_chunker_v2.types import ChunkingResult


class TestChunkSerialization:
    """Test Chunk serialization methods."""

    def test_chunk_to_dict_basic(self):
        """Test basic chunk to_dict conversion."""
        chunk = Chunk(
            content="# Test Header\n\nContent here.",
            start_line=1,
            end_line=3,
            metadata={"strategy": "structural", "type": "header"},
        )

        data = chunk.to_dict()

        assert data["content"] == "# Test Header\n\nContent here."
        assert data["start_line"] == 1
        assert data["end_line"] == 3
        assert data["size"] == len(chunk.content)
        assert data["line_count"] == 3  # end_line - start_line + 1
        assert "metadata" in data
        assert data["metadata"]["strategy"] == "structural"

    def test_chunk_from_dict_basic(self):
        """Test basic chunk from_dict creation."""
        data = {
            "content": "Test content",
            "start_line": 5,
            "end_line": 7,
            "metadata": {"strategy": "mixed"},
        }

        chunk = Chunk.from_dict(data)

        assert chunk.content == "Test content"
        assert chunk.start_line == 5
        assert chunk.end_line == 7
        assert chunk.metadata["strategy"] == "mixed"

    def test_chunk_roundtrip(self):
        """Test chunk serialization roundtrip."""
        original = Chunk(
            content="Test content",
            start_line=10,
            end_line=15,
            metadata={"key": "value", "number": 42},
        )

        # Serialize and deserialize
        data = original.to_dict()
        restored = Chunk.from_dict(data)

        assert restored.content == original.content
        assert restored.start_line == original.start_line
        assert restored.end_line == original.end_line
        assert restored.metadata["key"] == "value"
        assert restored.metadata["number"] == 42

    def test_chunk_json_serialization(self):
        """Test chunk can be serialized to JSON."""
        chunk = Chunk(
            content="JSON test", start_line=1, end_line=1, metadata={"test": True}
        )

        data = chunk.to_dict()
        json_str = json.dumps(data)
        restored_data = json.loads(json_str)
        restored_chunk = Chunk.from_dict(restored_data)

        assert restored_chunk.content == chunk.content
        assert restored_chunk.start_line == chunk.start_line


class TestChunkingResultSerialization:
    """Test ChunkingResult serialization methods."""

    def test_result_to_dict_basic(self):
        """Test basic result to_dict conversion."""
        chunks = [
            Chunk(content="chunk1", start_line=1, end_line=1),
            Chunk(content="chunk2", start_line=2, end_line=2),
        ]
        result = ChunkingResult(
            chunks=chunks, strategy_used="mixed", processing_time=0.5
        )

        data = result.to_dict()

        assert data["strategy_used"] == "mixed"
        assert data["processing_time"] == 0.5
        assert len(data["chunks"]) == 2
        assert data["chunk_count"] == 2

    def test_result_from_dict_basic(self):
        """Test basic result from_dict creation."""
        data = {
            "chunks": [{"content": "test", "start_line": 1, "end_line": 1}],
            "strategy_used": "sentences",
            "processing_time": 0.1,
        }

        result = ChunkingResult.from_dict(data)

        assert result.strategy_used == "sentences"
        assert result.processing_time == 0.1
        assert len(result.chunks) == 1
        assert result.chunks[0].content == "test"

    def test_result_roundtrip(self):
        """Test result serialization roundtrip."""
        original = ChunkingResult(
            chunks=[Chunk(content="test", start_line=1, end_line=1)],
            strategy_used="code",
            processing_time=0.25,
            total_chars=100,
            total_lines=10,
        )

        data = original.to_dict()
        restored = ChunkingResult.from_dict(data)

        assert restored.strategy_used == original.strategy_used
        assert restored.processing_time == original.processing_time
        assert restored.total_chars == original.total_chars
        assert restored.total_lines == original.total_lines

    def test_result_json_serialization(self):
        """Test result can be serialized to JSON."""
        result = ChunkingResult(
            chunks=[Chunk(content="json", start_line=1, end_line=1)],
            strategy_used="structural",
            processing_time=0.3,
        )

        data = result.to_dict()
        json_str = json.dumps(data)
        restored_data = json.loads(json_str)
        restored_result = ChunkingResult.from_dict(restored_data)

        assert restored_result.strategy_used == result.strategy_used
        assert len(restored_result.chunks) == len(result.chunks)


class TestChunkConfigSerialization:
    """Test ChunkConfig serialization methods."""

    def test_config_to_dict_basic(self):
        """Test basic config to_dict conversion."""
        config = ChunkConfig(max_chunk_size=2048, min_chunk_size=200, overlap_size=100)

        data = config.to_dict()

        assert data["max_chunk_size"] == 2048
        assert data["min_chunk_size"] == 200
        assert data["overlap_size"] == 100
        assert "enable_overlap" in data

    def test_config_from_dict_basic(self):
        """Test basic config from_dict creation."""
        data = {"max_chunk_size": 1024, "min_chunk_size": 50}

        config = ChunkConfig.from_dict(data)

        assert config.max_chunk_size == 1024
        assert config.min_chunk_size == 50
        # Defaults should be applied
        assert config.overlap_size == 200
        assert config.enable_overlap is True

    def test_config_roundtrip(self):
        """Test config serialization roundtrip."""
        original = ChunkConfig(
            max_chunk_size=3000,
            min_chunk_size=300,
            overlap_size=150,
        )

        data = original.to_dict()
        restored = ChunkConfig.from_dict(data)

        assert restored.max_chunk_size == original.max_chunk_size
        assert restored.min_chunk_size == original.min_chunk_size
        assert restored.overlap_size == original.overlap_size
        assert restored.enable_overlap == original.enable_overlap

    def test_config_json_serialization(self):
        """Test config can be serialized to JSON."""
        config = ChunkConfig(max_chunk_size=5000)

        data = config.to_dict()
        json_str = json.dumps(data)
        restored_data = json.loads(json_str)
        restored_config = ChunkConfig.from_dict(restored_data)

        assert restored_config.max_chunk_size == config.max_chunk_size

    def test_config_from_dict_with_defaults(self):
        """Test config from_dict applies defaults for missing values."""
        data = {"max_chunk_size": 8192}

        config = ChunkConfig.from_dict(data)

        # Should have defaults
        assert config.max_chunk_size == 8192
        assert config.min_chunk_size == 512  # default
        assert config.overlap_size == 200  # default
        assert config.enable_overlap is True  # default
