#!/usr/bin/env python3
"""Tests for migration adapter."""

from chunkana import ChunkerConfig

from adapter import MigrationAdapter


class TestMigrationAdapter:
    """Test migration adapter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.adapter = MigrationAdapter()

    def test_build_chunker_config_defaults(self):
        """Test build_chunker_config with default parameters."""
        config = self.adapter.build_chunker_config()

        assert isinstance(config, ChunkerConfig)
        assert config.max_chunk_size == 4096
        assert config.overlap_size == 200
        assert config.strategy_override is None

    def test_build_chunker_config_custom_params(self):
        """Test build_chunker_config with custom parameters."""
        config = self.adapter.build_chunker_config(
            max_chunk_size=1000, chunk_overlap=100, strategy="code_aware"
        )

        assert config.max_chunk_size == 1000
        assert config.overlap_size == 100
        assert config.strategy_override == "code_aware"

    def test_build_chunker_config_auto_strategy(self):
        """Test that 'auto' strategy maps to None."""
        config = self.adapter.build_chunker_config(strategy="auto")
        assert config.strategy_override is None

    def test_parse_tool_flags_defaults(self):
        """Test parse_tool_flags with default values."""
        include_metadata, enable_hierarchy, debug, leaf_only = (
            self.adapter.parse_tool_flags()
        )

        assert include_metadata is True
        assert enable_hierarchy is False
        assert debug is False
        assert leaf_only is False

    def test_parse_tool_flags_custom(self):
        """Test parse_tool_flags with custom values."""
        include_metadata, enable_hierarchy, debug, leaf_only = (
            self.adapter.parse_tool_flags(
                include_metadata=False,
                enable_hierarchy=True,
                debug=True,
                leaf_only=True,
            )
        )

        assert include_metadata is False
        assert enable_hierarchy is True
        assert debug is True
        assert leaf_only is True

    def test_filter_metadata_for_rag(self):
        """Test metadata filtering for RAG."""
        metadata = {
            # Should be kept
            "section_type": "paragraph",
            "has_code": True,
            "language": "python",
            # Should be excluded
            "char_count": 1000,
            "word_count": 200,
            "avg_line_length": 50.5,
            "execution_strategy_used": "auto",
            "is_leaf": True,
            "has_tables": False,
        }

        filtered = self.adapter._filter_metadata_for_rag(metadata)

        # Should keep useful fields
        assert "section_type" in filtered
        assert "has_code" in filtered
        assert "language" in filtered

        # Should exclude statistical fields
        assert "char_count" not in filtered
        assert "word_count" not in filtered
        assert "avg_line_length" not in filtered

        # Should exclude execution fields
        assert "execution_strategy_used" not in filtered

        # Should exclude is_leaf, is_root
        assert "is_leaf" not in filtered

        # Should exclude has_* fields with False values
        assert "has_tables" not in filtered

    def test_run_chunking_basic(self):
        """Test basic chunking functionality."""
        config = self.adapter.build_chunker_config()

        # Simple test text
        text = "# Header\n\nThis is a paragraph.\n\n## Subheader\n\nAnother paragraph."

        result = self.adapter.run_chunking(
            input_text=text,
            config=config,
            include_metadata=True,
            enable_hierarchy=False,
            debug=False,
        )

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(chunk, str) for chunk in result)

        # Should contain metadata blocks
        assert any("<metadata>" in chunk for chunk in result)

    def test_run_chunking_no_metadata(self):
        """Test chunking without metadata."""
        config = self.adapter.build_chunker_config()

        text = "# Header\n\nThis is a paragraph."

        result = self.adapter.run_chunking(
            input_text=text,
            config=config,
            include_metadata=False,
            enable_hierarchy=False,
            debug=False,
        )

        assert isinstance(result, list)
        assert len(result) > 0

        # Should not contain metadata blocks
        assert all("<metadata>" not in chunk for chunk in result)

    def test_run_chunking_hierarchical(self):
        """Test hierarchical chunking."""
        config = self.adapter.build_chunker_config()

        text = "# Header\n\nThis is a paragraph.\n\n## Subheader\n\nAnother paragraph."

        result = self.adapter.run_chunking(
            input_text=text,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=False,
        )

        assert isinstance(result, list)
        assert len(result) > 0

    def test_run_chunking_hierarchical_debug(self):
        """Test hierarchical chunking with debug mode."""
        config = self.adapter.build_chunker_config()

        text = "# Header\n\nThis is a paragraph.\n\n## Subheader\n\nAnother paragraph."

        result_normal = self.adapter.run_chunking(
            input_text=text,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=False,
        )

        result_debug = self.adapter.run_chunking(
            input_text=text,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=True,
        )

        # Debug mode should potentially return more chunks (including intermediate)
        assert isinstance(result_normal, list)
        assert isinstance(result_debug, list)
        assert len(result_debug) >= len(result_normal)
