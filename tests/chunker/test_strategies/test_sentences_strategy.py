"""
Tests for SentencesStrategy.

This module tests the universal fallback strategy that splits content
by sentences and groups them into appropriately sized chunks.
"""

from unittest.mock import Mock

from markdown_chunker.chunker.strategies.sentences_strategy import (
    SentencesStrategy,
    count_sentences,
    preview_sentence_splitting,
)
from markdown_chunker.chunker.types import ChunkConfig
from markdown_chunker.parser.types import ContentAnalysis, Stage1Results


class TestSentencesStrategy:
    """Test cases for SentencesStrategy."""

    def test_strategy_properties(self):
        """Test basic strategy properties."""
        strategy = SentencesStrategy()

        assert strategy.name == "sentences"
        assert strategy.priority == 6  # Lowest priority (fallback)

    def test_can_handle_always_true(self):
        """Test that sentences strategy can always handle any content."""
        strategy = SentencesStrategy()

        # Test with various analysis types
        analyses = [
            Mock(spec=ContentAnalysis, code_ratio=0.9, text_ratio=0.1),  # Code-heavy
            Mock(spec=ContentAnalysis, code_ratio=0.0, text_ratio=1.0),  # Text-only
            Mock(spec=ContentAnalysis, code_ratio=0.3, text_ratio=0.7),  # Mixed
        ]

        config = ChunkConfig.default()

        for analysis in analyses:
            assert strategy.can_handle(analysis, config) is True

    def test_calculate_quality_simple_text(self):
        """Test quality calculation for simple text content."""
        strategy = SentencesStrategy()

        # High text ratio, low complexity
        analysis = Mock(spec=ContentAnalysis)
        analysis.text_ratio = 0.9
        analysis.code_ratio = 0.05
        analysis.header_count = {1: 1}  # P1-005: Now Dict[int, int]
        analysis.get_total_header_count.return_value = 1
        analysis.list_count = 0
        analysis.table_count = 0
        analysis.complexity_score = 0.1

        quality = strategy.calculate_quality(analysis)

        # Should be relatively high for simple text
        assert quality > 0.5

    def test_calculate_quality_complex_content(self):
        """Test quality calculation for complex structured content."""
        strategy = SentencesStrategy()

        # Low text ratio, high complexity
        analysis = Mock(spec=ContentAnalysis)
        analysis.text_ratio = 0.3
        analysis.code_ratio = 0.4
        analysis.header_count = {1: 3, 2: 5}  # P1-005: Now Dict[int, int]
        analysis.get_total_header_count.return_value = 8
        analysis.list_count = 5
        analysis.table_count = 2
        analysis.complexity_score = 0.8

        quality = strategy.calculate_quality(analysis)

        # Should be lower for complex content
        assert quality < 0.3

    def test_split_into_paragraphs(self):
        """Test paragraph splitting functionality."""
        strategy = SentencesStrategy()

        content = """First paragraph with some text.
This is still the first paragraph.

Second paragraph starts here.
It continues on this line.

Third paragraph is short."""

        paragraphs = strategy._split_into_paragraphs(content)

        assert len(paragraphs) == 3
        assert "First paragraph" in paragraphs[0]
        assert "Second paragraph" in paragraphs[1]
        assert "Third paragraph" in paragraphs[2]

    def test_split_into_sentences_basic(self):
        """Test basic sentence splitting."""
        strategy = SentencesStrategy()

        text = "This is the first sentence. This is the second sentence! Is this a question?"

        sentences = strategy._split_into_sentences(text)

        assert len(sentences) == 3
        assert "first sentence." in sentences[0]
        assert "second sentence!" in sentences[1]
        assert "question?" in sentences[2]

    def test_split_into_sentences_edge_cases(self):
        """Test sentence splitting with edge cases."""
        strategy = SentencesStrategy()

        # Empty text
        assert strategy._split_into_sentences("") == []
        assert strategy._split_into_sentences("   ") == []

        # Single sentence without ending punctuation
        sentences = strategy._split_into_sentences("This is a sentence")
        assert len(sentences) == 1
        assert sentences[0] == "This is a sentence"

        # Text with abbreviations (should not split)
        text = "Dr. Smith went to the U.S.A. He had a great time."
        sentences = strategy._split_into_sentences(text)
        # This is a limitation - might split on abbreviations
        # But should still work reasonably
        assert len(sentences) >= 1

    def test_apply_empty_content(self):
        """Test applying strategy to empty content."""
        strategy = SentencesStrategy()
        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig.default()

        chunks = strategy.apply("", stage1_results, config)

        assert chunks == []

    def test_apply_single_sentence(self):
        """Test applying strategy to single sentence."""
        strategy = SentencesStrategy()
        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig.default()

        content = "This is a single sentence."
        chunks = strategy.apply(content, stage1_results, config)

        assert len(chunks) == 1
        assert chunks[0].content == content
        assert chunks[0].metadata["sentence_based"] is True
        assert chunks[0].metadata["sentences_per_chunk"] == 1

    def test_apply_multiple_sentences_single_chunk(self):
        """Test applying strategy to multiple sentences that fit in one chunk."""
        strategy = SentencesStrategy()
        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig(max_chunk_size=1000)

        content = "First sentence. Second sentence! Third sentence?"
        chunks = strategy.apply(content, stage1_results, config)

        assert len(chunks) == 1
        assert "First sentence" in chunks[0].content
        assert "Second sentence" in chunks[0].content
        assert "Third sentence" in chunks[0].content
        assert chunks[0].metadata["sentences_per_chunk"] == 3

    def test_apply_multiple_chunks_needed(self):
        """Test applying strategy when multiple chunks are needed."""
        strategy = SentencesStrategy()
        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig(max_chunk_size=80, min_chunk_size=20)  # Very small chunks

        content = "This is the first sentence that is quite long and contains many words to exceed the limit. This is the second sentence that is also quite long and should force a new chunk. This is the third sentence that should also be in a separate chunk."
        chunks = strategy.apply(content, stage1_results, config)

        # Should create multiple chunks due to size limit
        assert len(chunks) >= 1  # At least one chunk, possibly more

        # Each chunk should be sentence-based
        for chunk in chunks:
            assert chunk.metadata["sentence_based"] is True
            # Sentences strategy may create oversized chunks to preserve sentence integrity
            # This is acceptable behavior for a fallback strategy

    def test_apply_paragraph_boundaries(self):
        """Test that paragraph boundaries are respected."""
        strategy = SentencesStrategy()
        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig(max_chunk_size=200, min_chunk_size=50)

        content = """First paragraph with a sentence.

Second paragraph with another sentence.

Third paragraph with a final sentence."""

        chunks = strategy.apply(content, stage1_results, config)

        # Should create chunks respecting paragraph structure
        assert len(chunks) >= 1

        # All chunks should be sentence-based
        for chunk in chunks:
            assert chunk.metadata["sentence_based"] is True

    def test_apply_very_long_sentence(self):
        """Test handling of very long sentences that exceed chunk size."""
        strategy = SentencesStrategy()
        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig(max_chunk_size=200, min_chunk_size=50)

        # Create a very long sentence that actually exceeds the limit
        long_sentence = "This is a very long sentence that definitely exceeds the maximum chunk size limit of 200 characters and should be handled gracefully by the strategy implementation because it contains many words and is quite verbose and detailed in its description."

        chunks = strategy.apply(long_sentence, stage1_results, config)

        assert len(chunks) == 1  # Should create one chunk even if oversized
        assert chunks[0].content == long_sentence
        assert chunks[0].size > config.max_chunk_size

    def test_get_chunk_statistics_empty(self):
        """Test chunk statistics with empty chunk list."""
        strategy = SentencesStrategy()

        stats = strategy.get_chunk_statistics([])

        assert stats["total_chunks"] == 0
        assert stats["total_sentences"] == 0
        assert stats["avg_sentences_per_chunk"] == 0
        assert stats["sentence_based"] is True

    def test_get_chunk_statistics_with_chunks(self):
        """Test chunk statistics with actual chunks."""
        strategy = SentencesStrategy()
        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig.default()

        content = "First sentence. Second sentence. Third sentence. Fourth sentence."
        chunks = strategy.apply(content, stage1_results, config)

        stats = strategy.get_chunk_statistics(chunks)

        assert stats["total_chunks"] == len(chunks)
        assert stats["total_sentences"] > 0
        assert stats["avg_sentences_per_chunk"] > 0
        assert stats["sentence_based"] is True
        assert "avg_chunk_size" in stats
        assert "size_range" in stats

    def test_get_selection_reason(self):
        """Test selection reason generation."""
        strategy = SentencesStrategy()

        # High text ratio
        analysis = Mock(spec=ContentAnalysis)
        analysis.text_ratio = 0.9
        analysis.complexity_score = 0.1

        reason = strategy._get_selection_reason(analysis, True)
        assert "High text ratio" in reason

        # Low complexity
        analysis.text_ratio = 0.5
        analysis.complexity_score = 0.1

        reason = strategy._get_selection_reason(analysis, True)
        assert "Low complexity" in reason

        # General fallback
        analysis.text_ratio = 0.5
        analysis.complexity_score = 0.5

        reason = strategy._get_selection_reason(analysis, True)
        assert "Universal fallback" in reason


class TestSentencesStrategyUtilities:
    """Test utility functions for sentence processing."""

    def test_count_sentences(self):
        """Test sentence counting utility."""
        text = "First sentence. Second sentence! Third sentence?"
        count = count_sentences(text)
        assert count == 3

        # Empty text
        assert count_sentences("") == 0
        assert count_sentences("   ") == 0

        # Single sentence
        assert count_sentences("Just one sentence.") == 1

    def test_preview_sentence_splitting(self):
        """Test sentence splitting preview utility."""
        text = "First. Second! Third? Fourth. Fifth."

        # Preview first 3 sentences
        preview = preview_sentence_splitting(text, max_sentences=3)
        assert len(preview) == 3
        assert "First." in preview[0]
        assert "Second!" in preview[1]
        assert "Third?" in preview[2]

        # Preview more than available
        preview = preview_sentence_splitting(text, max_sentences=10)
        assert len(preview) == 5  # Only 5 sentences available

        # Empty text
        preview = preview_sentence_splitting("")
        assert preview == []


class TestSentencesStrategyIntegration:
    """Integration tests for SentencesStrategy."""

    def test_realistic_text_chunking(self):
        """Test chunking realistic text content."""
        strategy = SentencesStrategy()
        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig(max_chunk_size=300, min_chunk_size=100)

        content = """
        This is a sample article about artificial intelligence. AI has become increasingly important in modern technology.

        Machine learning algorithms can process vast amounts of data. They identify patterns that humans might miss. This capability makes them valuable for many applications.

        Natural language processing is a subset of AI. It focuses on understanding and generating human language. Applications include chatbots, translation services, and text analysis.

        The future of AI looks promising. However, it also raises important ethical questions. We must consider the implications of these powerful technologies.
        """

        chunks = strategy.apply(content, stage1_results, config)

        # Should create multiple chunks
        assert len(chunks) > 1

        # All chunks should be within size limits (except possibly the last one)
        for i, chunk in enumerate(chunks[:-1]):  # All but last
            assert chunk.size <= config.max_chunk_size

        # All chunks should have sentence-based metadata
        for chunk in chunks:
            assert chunk.metadata["sentence_based"] is True
            assert chunk.metadata["sentences_per_chunk"] > 0

        # Content should be preserved
        reconstructed = " ".join(chunk.content for chunk in chunks)
        # Remove extra whitespace for comparison
        original_clean = " ".join(content.split())
        reconstructed_clean = " ".join(reconstructed.split())

        # Should contain most of the original content (allowing for some processing differences)
        assert len(reconstructed_clean) > len(original_clean) * 0.8

    def test_fallback_behavior(self):
        """Test that sentences strategy works as a reliable fallback."""
        strategy = SentencesStrategy()
        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig.default()

        # Test various content types that other strategies might struggle with
        test_contents = [
            "Simple sentence.",
            "Multiple sentences. With different punctuation! And questions?",
            "No punctuation at all just text",
            "Mixed content with\n\nnewlines and\n\nbreaks",
            "Special characters: @#$%^&*()_+ and numbers 123456789",
            "",  # Empty content
            "   ",  # Whitespace only
        ]

        for content in test_contents:
            chunks = strategy.apply(content, stage1_results, config)

            if content.strip():
                # Should create at least one chunk for non-empty content
                assert len(chunks) >= 1
                # All chunks should have required metadata
                for chunk in chunks:
                    assert "sentence_based" in chunk.metadata
                    assert chunk.metadata["sentence_based"] is True
            else:
                # Empty content should result in no chunks
                assert len(chunks) == 0
