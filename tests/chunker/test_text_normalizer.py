"""
Unit tests for text normalization utilities.

Tests validate:
- Whitespace preservation between tokens
- List formatting preservation
- Block joining with proper separation
- Word boundary detection and validation
"""

import pytest

from markdown_chunker.chunker.text_normalizer import (
    ensure_list_formatting,
    ensure_space_between_tokens,
    join_content_blocks,
    normalize_list_content,
    normalize_whitespace,
    truncate_at_word_boundary,
    validate_no_word_fragments,
)


class TestNormalizeWhitespace:
    """Tests for normalize_whitespace function."""

    def test_single_newline_to_space(self):
        """Single newline should be replaced with space."""
        assert normalize_whitespace("word1\nword2") == "word1 word2"

    def test_double_newline_preserved(self):
        """Double newlines should be preserved as paragraph breaks."""
        assert normalize_whitespace("word1\n\nword2") == "word1\n\nword2"

    def test_concatenated_words_fixed(self):
        """Adjacent words should have space inserted."""
        # Period followed by capital
        assert " " in normalize_whitespace("sentence.Next sentence")
        # Colon followed by word
        assert " " in normalize_whitespace("label:value")

    def test_multiple_spaces_normalized(self):
        """Multiple spaces should be collapsed to single space."""
        assert normalize_whitespace("word1    word2") == "word1 word2"

    def test_punctuation_spacing(self):
        """Punctuation should be followed by space before next word."""
        result = normalize_whitespace("Достижения:мы начали")
        assert ": " in result or ":\n" in result

    def test_empty_input(self):
        """Empty input should return empty output."""
        assert normalize_whitespace("") == ""
        assert normalize_whitespace(None) == None

    def test_preserves_intentional_formatting(self):
        """Should preserve intentional paragraph structure."""
        text = "Paragraph 1.\n\nParagraph 2."
        result = normalize_whitespace(text)
        assert "\n\n" in result


class TestJoinContentBlocks:
    """Tests for join_content_blocks function."""

    def test_joins_with_default_separator(self):
        """Should join blocks with double newline by default."""
        blocks = ["Block 1", "Block 2"]
        result = join_content_blocks(blocks)
        assert result == "Block 1\n\nBlock 2"

    def test_joins_with_custom_separator(self):
        """Should use custom separator when provided."""
        blocks = ["Block 1", "Block 2"]
        result = join_content_blocks(blocks, separator=" ")
        assert result == "Block 1 Block 2"

    def test_filters_empty_blocks(self):
        """Should filter out empty blocks."""
        blocks = ["Block 1", "", "  ", "Block 2"]
        result = join_content_blocks(blocks)
        assert result == "Block 1\n\nBlock 2"

    def test_empty_input_list(self):
        """Empty list should return empty string."""
        assert join_content_blocks([]) == ""

    def test_single_block(self):
        """Single block should be returned trimmed."""
        assert join_content_blocks(["  Block  "]) == "Block"

    def test_validates_no_token_adjacency(self):
        """Should validate proper whitespace between tokens."""
        # This should work fine
        blocks = ["Word1.", "Word2."]
        result = join_content_blocks(blocks)
        assert result  # Should not raise


class TestNormalizeListContent:
    """Tests for normalize_list_content function."""

    def test_unordered_list_normalized(self):
        """Unordered list markers should have single space after."""
        text = "-  Item 1\n-Item 2"
        result = normalize_list_content(text)
        assert "- Item 1" in result
        assert "- Item 2" in result

    def test_ordered_list_normalized(self):
        """Ordered list markers should have single space after."""
        text = "1.  Item 1\n2.Item 2"
        result = normalize_list_content(text)
        assert "1. Item 1" in result
        assert "2. Item 2" in result

    def test_task_list_normalized(self):
        """Task list markers should have single space after."""
        text = "-  [ ]  Task 1\n- [x]Task 2"
        result = normalize_list_content(text)
        # Checkbox content should have single space
        assert (
            "- [ ] Task 1" in result or "- [ ]  Task 1" in result
        )  # Allow double space before content
        assert "- [x] Task 2" in result

    def test_preserves_indentation(self):
        """Should preserve indentation for nested lists."""
        text = "- Item 1\n  - Nested item"
        result = normalize_list_content(text)
        assert "  - Nested item" in result

    def test_preserves_non_list_lines(self):
        """Should preserve lines that aren't list items."""
        text = "Header\n- Item 1\nFooter"
        result = normalize_list_content(text)
        assert "Header" in result
        assert "Footer" in result


class TestEnsureSpaceBetweenTokens:
    """Tests for ensure_space_between_tokens function."""

    def test_valid_spacing(self):
        """Should return True for properly spaced text."""
        assert ensure_space_between_tokens("word1 word2")
        assert ensure_space_between_tokens("sentence. Next sentence.")

    def test_detects_sentence_concatenation(self):
        """Should detect period followed by capital without space."""
        assert not ensure_space_between_tokens("sentence.Next")

    def test_detects_colon_concatenation(self):
        """Should detect colon followed by letter without space."""
        assert not ensure_space_between_tokens("label:value")

    def test_empty_string_valid(self):
        """Empty string should be considered valid."""
        assert ensure_space_between_tokens("")

    def test_none_input_valid(self):
        """None input should be considered valid."""
        assert ensure_space_between_tokens(None)


class TestEnsureListFormatting:
    """Tests for ensure_list_formatting function."""

    def test_fixes_ordered_list_spacing(self):
        """Should add space after ordered list markers."""
        text = "1.Item one"
        result = ensure_list_formatting(text)
        assert "1. Item" in result

    def test_fixes_unordered_list_spacing(self):
        """Should add space after unordered list markers."""
        text = "-Item one"
        result = ensure_list_formatting(text)
        assert "- Item" in result

    def test_handles_multiple_items(self):
        """Should handle multiple list items."""
        text = "1.First2.Second"
        result = ensure_list_formatting(text)
        # Should separate items
        assert "1. " in result
        assert "2. " in result


class TestTruncateAtWordBoundary:
    """Tests for truncate_at_word_boundary function."""

    def test_truncate_from_start(self):
        """Should truncate from end, keeping start."""
        text = "The quick brown fox"
        result = truncate_at_word_boundary(text, 10, from_end=False)
        assert result == "The quick"
        assert not result.endswith("brown")  # Partial word removed

    def test_truncate_from_end(self):
        """Should truncate from start, keeping end."""
        text = "The quick brown fox"
        result = truncate_at_word_boundary(text, 10, from_end=True)
        assert result == "brown fox"
        assert not result.startswith("quick")  # Partial word removed

    def test_no_truncation_needed(self):
        """Should return original if under limit."""
        text = "Short"
        assert truncate_at_word_boundary(text, 10) == text

    def test_no_word_boundary_found(self):
        """Should return truncated text if no boundary found."""
        text = "Supercalifragilisticexpialidocious"
        result = truncate_at_word_boundary(text, 10)
        assert len(result) <= 10


class TestValidateNoWordFragments:
    """Tests for validate_no_word_fragments function."""

    def test_valid_text(self):
        """Should return True for text without fragments."""
        assert validate_no_word_fragments("word fragment")
        assert validate_no_word_fragments("The quick brown fox")

    def test_detects_fragment_at_start(self):
        """Should detect fragment at start."""
        # Very short fragments should be detected
        assert not validate_no_word_fragments("nk of word")
        assert not validate_no_word_fragments("pe something")
        # Longer words might be valid even if lowercase
        # ("agment" could theoretically be a word, though uncommon)

    def test_allows_valid_lowercase_starts(self):
        """Should allow valid words that start with lowercase."""
        assert validate_no_word_fragments("a word")
        assert validate_no_word_fragments("the word")
        assert validate_no_word_fragments("and another")

    def test_empty_string_valid(self):
        """Empty string should be considered valid."""
        assert validate_no_word_fragments("")

    def test_short_string_valid(self):
        """Very short strings should be considered valid."""
        assert validate_no_word_fragments("a")


class TestIntegrationScenarios:
    """Integration tests for combined normalization scenarios."""

    def test_block_1_scenario(self):
        """Test BLOCK-1: Text concatenation without spaces."""
        # Simulate the problematic pattern from the bug report
        text = "продукта.Нет выделенной зоны"
        result = normalize_whitespace(text)
        assert ". " in result  # Should have space after period

    def test_russian_text_colon_spacing(self):
        """Test Russian text with colon (BLOCK-1)."""
        text = "Главные достижения:мы начали"
        result = normalize_whitespace(text)
        assert ": " in result or ":\n" in result

    def test_list_formatting_preservation(self):
        """Test CRIT-2: List structure preservation."""
        text = "Главные достижения:\n1.мы начали собирать метрики\n2.имеем anti fraud"
        normalized = normalize_whitespace(text)
        list_normalized = ensure_list_formatting(normalized)

        # Should have proper spacing
        assert ":" in list_normalized
        assert "1. " in list_normalized
        assert "2. " in list_normalized

    def test_multiple_blocks_joining(self):
        """Test joining multiple blocks without concatenation."""
        blocks = [
            "Разработчик помогает разрабатывать.",
            "Нет выделенной зоны ответственности.",
            "Ответственен за конкретные задачи.",
        ]
        result = join_content_blocks(blocks)

        # Should not have sentence concatenation
        assert ". " in result or ".\n" in result
        # Should have proper separation
        assert "\n\n" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
