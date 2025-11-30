"""
Tests for MetadataEnricher.
This module tests the metadata enrichment component that adds comprehensive
metadata to chunks.
"""

from markdown_chunker.chunker.components.metadata_enricher import MetadataEnricher
from markdown_chunker.chunker.types import Chunk, ChunkConfig


class TestMetadataEnricher:
    """Test cases for MetadataEnricher."""

    def test_initialization(self):
        """Test MetadataEnricher initialization."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        assert enricher.config == config

    def test_enrich_chunks_empty(self):
        """Test enriching empty chunk list."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        result = enricher.enrich_chunks([])

        assert result == []

    def test_enrich_single_chunk(self):
        """Test enriching a single chunk."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        chunk = Chunk(
            "Test content", 1, 5, {"strategy": "test", "content_type": "text"}
        )
        result = enricher.enrich_chunks([chunk])

        assert len(result) == 1
        enriched = result[0]

        # Check position metadata
        assert enriched.get_metadata("chunk_index") == 0
        assert enriched.get_metadata("total_chunks") == 1
        assert enriched.get_metadata("is_first_chunk") is True
        assert enriched.get_metadata("is_last_chunk") is True

        # Check statistics
        assert "word_count" in enriched.metadata
        assert "line_count" in enriched.metadata
        assert "char_count" in enriched.metadata

    def test_enrich_multiple_chunks(self):
        """Test enriching multiple chunks."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        chunks = [
            Chunk("First chunk", 1, 3, {"strategy": "test"}),
            Chunk("Second chunk", 4, 6, {"strategy": "test"}),
            Chunk("Third chunk", 7, 9, {"strategy": "test"}),
        ]

        result = enricher.enrich_chunks(chunks)

        assert len(result) == 3

        # Check first chunk
        assert result[0].get_metadata("chunk_index") == 0
        assert result[0].get_metadata("is_first_chunk") is True
        assert result[0].get_metadata("is_last_chunk") is False

        # Check middle chunk
        assert result[1].get_metadata("chunk_index") == 1
        assert result[1].get_metadata("is_first_chunk") is False
        assert result[1].get_metadata("is_last_chunk") is False

        # Check last chunk
        assert result[2].get_metadata("chunk_index") == 2
        assert result[2].get_metadata("is_first_chunk") is False
        assert result[2].get_metadata("is_last_chunk") is True

    def test_enrich_with_document_id(self):
        """Test enriching with document ID."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        chunk = Chunk("Content", 1, 3, {"strategy": "test"})
        result = enricher.enrich_chunks([chunk], document_id="doc123")

        assert result[0].get_metadata("document_id") == "doc123"

    def test_calculate_content_statistics(self):
        """Test content statistics calculation."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        content = "Line 1\nLine 2\nLine 3"
        stats = enricher._calculate_content_statistics(content)

        assert stats["line_count"] == 3
        assert stats["word_count"] == 6
        assert stats["char_count"] == len(content)
        assert "avg_line_length" in stats
        assert "avg_word_length" in stats

    def test_enrich_code_metadata(self):
        """Test code metadata enrichment."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        chunk = Chunk(
            "```python\ndef test():\n    pass\n```\nSome `inline` code",
            1,
            5,
            {"strategy": "code", "content_type": "code"},
        )

        result = enricher.enrich_chunks([chunk])
        enriched = result[0]

        assert enriched.get_metadata("code_block_count") == 1
        assert enriched.get_metadata("has_inline_code") is True

    def test_enrich_list_metadata(self):
        """Test list metadata enrichment."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        chunk = Chunk(
            "1. First item\n2. Second item\n- Unordered\n  - Nested",
            1,
            4,
            {"strategy": "list", "content_type": "list"},
        )

        result = enricher.enrich_chunks([chunk])
        enriched = result[0]

        assert enriched.get_metadata("ordered_item_count") == 2
        assert enriched.get_metadata("unordered_item_count") == 2
        assert enriched.get_metadata("has_nested_lists") is True

    def test_enrich_table_metadata(self):
        """Test table metadata enrichment."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        chunk = Chunk(
            "| Col1 | Col2 |\n|------|------|\n| A | B |\n| C | D |",
            1,
            4,
            {"strategy": "table", "content_type": "table"},
        )

        result = enricher.enrich_chunks([chunk])
        enriched = result[0]

        assert enriched.get_metadata("table_row_count") == 4
        assert enriched.get_metadata("table_count") == 1

    def test_enrich_structural_metadata(self):
        """Test structural metadata enrichment."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        chunk = Chunk(
            "# Header 1\n\nParagraph 1\n\n## Header 2\n\nParagraph 2",
            1,
            7,
            {"strategy": "structural", "content_type": "structured"},
        )

        result = enricher.enrich_chunks([chunk])
        enriched = result[0]

        assert enriched.get_metadata("header_count") == 2
        assert enriched.get_metadata("min_header_level") == 1
        assert enriched.get_metadata("max_header_level") == 2
        assert enriched.get_metadata("paragraph_count") == 2

    def test_add_searchability_metadata(self):
        """Test searchability metadata."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        content = "Visit https://example.com or email test@example.com. **Bold** and *italic* text."
        metadata = enricher._add_searchability_metadata(content)

        assert metadata["has_urls"] is True
        assert metadata["has_emails"] is True
        assert metadata["has_bold"] is True
        assert metadata["has_italic"] is True
        assert "preview" in metadata

    def test_validate_metadata_valid(self):
        """Test metadata validation with valid chunks."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        chunks = [
            Chunk(
                "Content 1",
                1,
                3,
                {"strategy": "test", "content_type": "text", "size_bytes": 100},
            ),
            Chunk(
                "Content 2",
                4,
                6,
                {"strategy": "test", "content_type": "text", "size_bytes": 100},
            ),
        ]

        enriched = enricher.enrich_chunks(chunks)
        validation = enricher.validate_metadata(enriched)

        assert validation["valid"] is True
        assert validation["issue_count"] == 0

    def test_validate_metadata_missing_fields(self):
        """Test metadata validation with missing fields."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        chunks = [Chunk("Content", 1, 3, {})]  # Missing required fields

        validation = enricher.validate_metadata(chunks)

        assert validation["valid"] is False
        assert validation["issue_count"] > 0

    def test_get_metadata_summary(self):
        """Test metadata summary generation."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        chunks = [
            Chunk("Content 1", 1, 3, {"strategy": "code", "content_type": "code"}),
            Chunk("Content 2", 4, 6, {"strategy": "code", "content_type": "code"}),
            Chunk("Content 3", 7, 9, {"strategy": "text", "content_type": "text"}),
        ]

        enriched = enricher.enrich_chunks(chunks)
        summary = enricher.get_metadata_summary(enriched)

        assert summary["total_chunks"] == 3
        assert summary["strategies"]["code"] == 2
        assert summary["strategies"]["text"] == 1
        assert "total_words" in summary
        assert "avg_words_per_chunk" in summary

    def test_get_metadata_summary_empty(self):
        """Test metadata summary with empty list."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        summary = enricher.get_metadata_summary([])

        assert summary["total_chunks"] == 0

    def test_preserves_original_metadata(self):
        """Test that enrichment preserves original metadata."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        chunk = Chunk(
            "Content", 1, 3, {"strategy": "test", "custom_field": "custom_value"}
        )

        result = enricher.enrich_chunks([chunk])
        enriched = result[0]

        # Original metadata should be preserved
        assert enriched.get_metadata("strategy") == "test"
        assert enriched.get_metadata("custom_field") == "custom_value"

        # New metadata should be added
        assert "chunk_index" in enriched.metadata
        assert "word_count" in enriched.metadata


class TestMetadataEnricherIntegration:
    """Integration tests for MetadataEnricher."""

    def test_realistic_document_enrichment(self):
        """Test enrichment with realistic document chunks."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        chunks = [
            Chunk(
                "# Introduction\n\nThis is the introduction with some **bold** text.",
                1,
                3,
                {"strategy": "structural", "content_type": "structured"},
            ),
            Chunk(
                "```python\ndef example():\n    return True\n```",
                4,
                7,
                {"strategy": "code", "content_type": "code", "language": "python"},
            ),
            Chunk(
                "| Name | Value |\n|------|-------|\n| A | 1 |\n| B | 2 |",
                8,
                11,
                {"strategy": "table", "content_type": "table"},
            ),
        ]

        result = enricher.enrich_chunks(chunks, document_id="test_doc")

        # All chunks should be enriched
        assert len(result) == 3

        # Check that each chunk has comprehensive metadata
        for chunk in result:
            assert "chunk_index" in chunk.metadata
            assert "document_id" in chunk.metadata
            assert "word_count" in chunk.metadata
            assert "line_count" in chunk.metadata
            assert "preview" in chunk.metadata

        # Validate metadata
        validation = enricher.validate_metadata(result)
        assert validation["valid"] is True

        # Get summary
        summary = enricher.get_metadata_summary(result)
        assert summary["total_chunks"] == 3
        assert len(summary["strategies"]) >= 1
        assert len(summary["content_types"]) >= 1

    def test_enrichment_with_all_content_types(self):
        """Test enrichment with all content types."""
        config = ChunkConfig.default()
        enricher = MetadataEnricher(config)

        chunks = [
            Chunk("Code content", 1, 2, {"strategy": "code", "content_type": "code"}),
            Chunk("List content", 3, 4, {"strategy": "list", "content_type": "list"}),
            Chunk(
                "Table content", 5, 6, {"strategy": "table", "content_type": "table"}
            ),
            Chunk(
                "Structural content",
                7,
                8,
                {"strategy": "structural", "content_type": "structured"},
            ),
            Chunk(
                "Text content", 9, 10, {"strategy": "sentences", "content_type": "text"}
            ),
        ]

        result = enricher.enrich_chunks(chunks)

        # All chunks should have strategy-specific enrichment
        assert len(result) == 5

        # Each chunk should have appropriate metadata
        for chunk in result:
            content_type = chunk.get_metadata("content_type")
            assert content_type in ["code", "list", "table", "structured", "text"]

            # Should have general metadata
            assert "word_count" in chunk.metadata
            assert "chunk_index" in chunk.metadata
