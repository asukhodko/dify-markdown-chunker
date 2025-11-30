"""Tests for configuration profiles."""

from markdown_chunker.chunker.types import ChunkConfig


class TestConfigProfiles:
    """Test configuration profile factory methods."""

    def test_for_api_default(self):
        """Test API default profile."""
        config = ChunkConfig.for_api_default()

        assert config.max_chunk_size == 4096
        assert config.min_chunk_size == 512
        assert config.target_chunk_size == 2048
        assert config.overlap_size == 200
        assert config.enable_overlap is True
        assert config.allow_oversize is True

    def test_for_dify_rag(self):
        """Test Dify RAG profile."""
        config = ChunkConfig.for_dify_rag()

        assert config.max_chunk_size == 3072
        assert config.min_chunk_size == 256
        assert config.target_chunk_size == 1536
        assert config.overlap_size == 150
        assert config.enable_overlap is True
        assert config.preserve_code_blocks is True
        assert config.preserve_list_hierarchy is True
        assert config.allow_oversize is False

    def test_for_fast_processing(self):
        """Test fast processing profile."""
        config = ChunkConfig.for_fast_processing()

        assert config.max_chunk_size == 8192
        assert config.min_chunk_size == 1024
        assert config.target_chunk_size == 4096
        assert config.overlap_size == 100
        assert config.enable_overlap is False
        assert config.allow_oversize is True
        assert config.enable_streaming is True

    def test_all_profiles_valid(self):
        """Test all profiles are created successfully."""
        profiles = [
            ChunkConfig.for_api_default(),
            ChunkConfig.for_dify_rag(),
            ChunkConfig.for_fast_processing(),
        ]

        # All should be created without exceptions
        for config in profiles:
            assert isinstance(config, ChunkConfig)
            assert config.max_chunk_size > config.min_chunk_size

    def test_profiles_have_different_settings(self):
        """Test profiles have distinct settings."""
        api = ChunkConfig.for_api_default()
        dify = ChunkConfig.for_dify_rag()
        fast = ChunkConfig.for_fast_processing()

        # Max chunk sizes should be different
        assert api.max_chunk_size != dify.max_chunk_size
        assert dify.max_chunk_size != fast.max_chunk_size

        # Overlap settings should differ
        assert api.enable_overlap != fast.enable_overlap
