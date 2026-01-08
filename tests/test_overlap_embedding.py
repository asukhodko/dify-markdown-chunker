#!/usr/bin/env python3
"""Tests for overlap embedding functionality.

Tests the fix for CRITICAL-01: Overlap not embedded in content when include_metadata=False.
"""

import pytest

from adapter import MigrationAdapter


class TestOverlapEmbedding:
    """Test overlap embedding in include_metadata=False mode."""

    @pytest.fixture
    def adapter(self):
        """Create adapter instance."""
        return MigrationAdapter()

    def test_embed_overlap_with_previous_and_next(self, adapter):
        """Test embedding with both previous and next content."""
        chunk = {
            "content": "## Main Section\n\nMain content here.",
            "metadata": {
                "previous_content": "...end of previous section.",
                "next_content": "## Next Section\n\nNext content..."
            }
        }
        
        result = adapter._embed_overlap(chunk)
        expected = "...end of previous section.\n\n## Main Section\n\nMain content here.\n\n## Next Section\n\nNext content..."
        assert result == expected

    def test_embed_overlap_first_chunk_only_next(self, adapter):
        """Test first chunk with only next content."""
        chunk = {
            "content": "## First Section\n\nFirst chunk content.",
            "metadata": {
                "next_content": "## Second Section\n\nSecond content..."
            }
        }
        
        result = adapter._embed_overlap(chunk)
        expected = "## First Section\n\nFirst chunk content.\n\n## Second Section\n\nSecond content..."
        assert result == expected

    def test_embed_overlap_last_chunk_only_previous(self, adapter):
        """Test last chunk with only previous content."""
        chunk = {
            "content": "## Last Section\n\nLast chunk content.",
            "metadata": {
                "previous_content": "...end of previous section."
            }
        }
        
        result = adapter._embed_overlap(chunk)
        expected = "...end of previous section.\n\n## Last Section\n\nLast chunk content."
        assert result == expected

    def test_embed_overlap_no_overlap_content(self, adapter):
        """Test chunk with no overlap content."""
        chunk = {
            "content": "## Only Section\n\nOnly content here.",
            "metadata": {}
        }
        
        result = adapter._embed_overlap(chunk)
        expected = "## Only Section\n\nOnly content here."
        assert result == expected

    def test_embed_overlap_no_metadata(self, adapter):
        """Test chunk with no metadata field."""
        chunk = {
            "content": "## Section\n\nContent without metadata."
        }
        
        result = adapter._embed_overlap(chunk)
        expected = "## Section\n\nContent without metadata."
        assert result == expected

    def test_embed_overlap_empty_strings(self, adapter):
        """Test with empty strings in overlap fields."""
        chunk = {
            "content": "## Main Section\n\nMain content.",
            "metadata": {
                "previous_content": "",
                "next_content": ""
            }
        }
        
        result = adapter._embed_overlap(chunk)
        expected = "## Main Section\n\nMain content."
        assert result == expected

    def test_embed_overlap_whitespace_only(self, adapter):
        """Test with whitespace-only overlap content."""
        chunk = {
            "content": "## Main Section\n\nMain content.",
            "metadata": {
                "previous_content": "   \n  ",
                "next_content": "\t\n   "
            }
        }
        
        result = adapter._embed_overlap(chunk)
        expected = "## Main Section\n\nMain content."
        assert result == expected

    def test_embed_overlap_strips_whitespace(self, adapter):
        """Test that overlap content is properly stripped."""
        chunk = {
            "content": "  ## Main Section\n\nMain content.  ",
            "metadata": {
                "previous_content": "  ...previous content.  \n",
                "next_content": "\n  ## Next Section\n\nNext content.  "
            }
        }
        
        result = adapter._embed_overlap(chunk)
        expected = "...previous content.\n\n## Main Section\n\nMain content.\n\n## Next Section\n\nNext content."
        assert result == expected

    def test_embed_overlap_zero_overlap_config(self, adapter):
        """Test with zero overlap configuration."""
        chunk = {
            "content": "## Section\n\nContent without overlap.",
            "metadata": {
                "overlap_size": 0
            }
        }
        
        result = adapter._embed_overlap(chunk)
        expected = "## Section\n\nContent without overlap."
        assert result == expected

    def test_embed_overlap_error_handling(self, adapter):
        """Test error handling with malformed data."""
        chunk = {
            "content": "## Section\n\nMain content.",
            "metadata": {
                "previous_content": None,  # Invalid type
                "next_content": 123        # Invalid type
            }
        }
        
        # Should fallback to content-only
        result = adapter._embed_overlap(chunk)
        expected = "## Section\n\nMain content."
        assert result == expected

    def test_embed_overlap_empty_content(self, adapter):
        """Test with empty content field."""
        chunk = {
            "content": "",
            "metadata": {
                "previous_content": "Previous content.",
                "next_content": "Next content."
            }
        }
        
        result = adapter._embed_overlap(chunk)
        expected = "Previous content.\n\nNext content."
        assert result == expected

    def test_embed_overlap_all_empty(self, adapter):
        """Test with all fields empty."""
        chunk = {
            "content": "",
            "metadata": {
                "previous_content": "",
                "next_content": ""
            }
        }
        
        result = adapter._embed_overlap(chunk)
        expected = ""
        assert result == expected


class TestRenderWithoutMetadata:
    """Test _render_without_metadata method with overlap embedding."""

    @pytest.fixture
    def adapter(self):
        """Create adapter instance."""
        return MigrationAdapter()

    def test_render_without_metadata_embeds_overlap(self, adapter):
        """Test that _render_without_metadata embeds overlap."""
        raw_chunks = [
            {
                "content": "## First Section\n\nFirst content.",
                "metadata": {
                    "next_content": "## Second Section\n\nSecond preview..."
                }
            },
            {
                "content": "## Second Section\n\nSecond content.",
                "metadata": {
                    "previous_content": "...first content end.",
                    "next_content": "## Third Section\n\nThird preview..."
                }
            },
            {
                "content": "## Third Section\n\nThird content.",
                "metadata": {
                    "previous_content": "...second content end."
                }
            }
        ]
        
        result = adapter._render_without_metadata(raw_chunks)
        
        assert len(result) == 3
        
        # First chunk: content + next
        assert "## First Section\n\nFirst content." in result[0]
        assert "## Second Section\n\nSecond preview..." in result[0]
        
        # Middle chunk: previous + content + next
        assert "...first content end." in result[1]
        assert "## Second Section\n\nSecond content." in result[1]
        assert "## Third Section\n\nThird preview..." in result[1]
        
        # Last chunk: previous + content
        assert "...second content end." in result[2]
        assert "## Third Section\n\nThird content." in result[2]

    def test_render_without_metadata_no_overlap(self, adapter):
        """Test rendering without any overlap content."""
        raw_chunks = [
            {
                "content": "## Section 1\n\nContent 1.",
                "metadata": {}
            },
            {
                "content": "## Section 2\n\nContent 2.",
                "metadata": {}
            }
        ]
        
        result = adapter._render_without_metadata(raw_chunks)
        
        assert len(result) == 2
        assert result[0] == "## Section 1\n\nContent 1."
        assert result[1] == "## Section 2\n\nContent 2."

    def test_render_without_metadata_mixed_overlap(self, adapter):
        """Test rendering with mixed overlap scenarios."""
        raw_chunks = [
            {
                "content": "Content 1",
                "metadata": {
                    "next_content": "Preview 2"
                }
            },
            {
                "content": "Content 2",
                "metadata": {}  # No overlap
            },
            {
                "content": "Content 3",
                "metadata": {
                    "previous_content": "End 2",
                    "next_content": "Preview 4"
                }
            }
        ]
        
        result = adapter._render_without_metadata(raw_chunks)
        
        assert len(result) == 3
        assert result[0] == "Content 1\n\nPreview 2"
        assert result[1] == "Content 2"
        assert result[2] == "End 2\n\nContent 3\n\nPreview 4"


class TestOverlapContract:
    """Test overlap contract compliance."""

    @pytest.fixture
    def adapter(self):
        """Create adapter instance."""
        return MigrationAdapter()

    @pytest.fixture
    def test_document(self):
        """Test document with multiple sections."""
        return """# Document Title

## First Section

This is the first section with some content.
It has multiple paragraphs to ensure proper chunking.

## Second Section

This is the second section with different content.
It also has multiple paragraphs for testing.

## Third Section

This is the third section with more content.
Final section for testing overlap behavior.
"""

    def test_overlap_contract_same_chunk_count(self, adapter, test_document):
        """Test that both modes produce same chunk count."""
        config = adapter.build_chunker_config(
            max_chunk_size=200,
            chunk_overlap=50
        )
        
        result_with = adapter.run_chunking(
            test_document, config, include_metadata=True
        )
        result_without = adapter.run_chunking(
            test_document, config, include_metadata=False
        )
        
        assert len(result_with) == len(result_without)

    def test_overlap_contract_embedded_content_contains_original(self, adapter, test_document):
        """Test that embedded content contains original content."""
        config = adapter.build_chunker_config(
            max_chunk_size=200,
            chunk_overlap=50
        )
        
        result_with = adapter.run_chunking(
            test_document, config, include_metadata=True
        )
        result_without = adapter.run_chunking(
            test_document, config, include_metadata=False
        )
        
        for i, (chunk_with, chunk_without) in enumerate(zip(result_with, result_without)):
            # Extract content from metadata format
            if chunk_with.startswith("<metadata>"):
                metadata_end = chunk_with.find("</metadata>")
                original_content = chunk_with[metadata_end + 11:].strip()
            else:
                original_content = chunk_with
            
            # Original content should be substring of embedded content
            assert original_content in chunk_without, f"Chunk {i}: original content not found in embedded"

    def test_overlap_contract_middle_chunks_have_overlap(self, adapter, test_document):
        """Test that middle chunks contain overlap content."""
        config = adapter.build_chunker_config(
            max_chunk_size=150,
            chunk_overlap=30
        )
        
        result = adapter.run_chunking(
            test_document, config, include_metadata=False
        )
        
        # If we have multiple chunks, middle ones should be longer due to overlap
        if len(result) > 2:
            # Middle chunks should generally be longer than if they had no overlap
            # This is a heuristic test - exact behavior depends on content
            middle_chunk = result[1]
            
            # Middle chunk should contain content from multiple sections
            # (this is document-specific, but our test doc should trigger this)
            assert len(middle_chunk) > 100  # Should be substantial with overlap

    def test_overlap_contract_zero_overlap_no_embedding(self, adapter, test_document):
        """Test that zero overlap configuration doesn't embed anything."""
        config = adapter.build_chunker_config(
            max_chunk_size=200,
            chunk_overlap=0  # No overlap
        )
        
        result_with = adapter.run_chunking(
            test_document, config, include_metadata=True
        )
        result_without = adapter.run_chunking(
            test_document, config, include_metadata=False
        )
        
        for i, (chunk_with, chunk_without) in enumerate(zip(result_with, result_without)):
            # Extract content from metadata format
            if chunk_with.startswith("<metadata>"):
                metadata_end = chunk_with.find("</metadata>")
                original_content = chunk_with[metadata_end + 11:].strip()
            else:
                original_content = chunk_with
            
            # With zero overlap, embedded should equal original
            assert chunk_without == original_content, f"Chunk {i}: zero overlap should not embed anything"