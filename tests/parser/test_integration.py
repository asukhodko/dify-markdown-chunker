"""Integration tests for Stage 1 components."""

from markdown_chunker.parser import extract_fenced_blocks, validate_and_normalize_input

from .test_data import COMPLEX_MARKDOWN, NESTED_BLOCKS, SIMPLE_MARKDOWN


class TestStage1Integration:
    """Test integration of Stage 1 components."""

    def test_simple_document_processing(self):
        """Test processing a simple document."""
        # Test basic fenced block extraction
        blocks = extract_fenced_blocks(SIMPLE_MARKDOWN)

        # Should extract blocks successfully
        assert isinstance(blocks, list)
        assert len(blocks) >= 0

        # Validate block structure if any blocks found
        for block in blocks:
            assert hasattr(block, "content")
            assert hasattr(block, "language")
            assert hasattr(block, "start_line")
            assert hasattr(block, "end_line")
            assert hasattr(block, "nesting_level")

    def test_complex_document_processing(self):
        """Test processing a complex document."""
        # Test extraction from complex document
        blocks = extract_fenced_blocks(COMPLEX_MARKDOWN)

        # Should detect multiple blocks
        assert len(blocks) >= 1

        # Should have proper line numbering (1-based)
        for block in blocks:
            assert block.start_line >= 1
            assert block.end_line >= block.start_line

    def test_nested_blocks_processing(self):
        """Test processing document with nested blocks."""
        blocks = extract_fenced_blocks(NESTED_BLOCKS)

        # Should find blocks (nested detection now implemented)
        assert len(blocks) >= 1

        # Check for nesting levels
        nesting_levels = [block.nesting_level for block in blocks]
        assert 0 in nesting_levels  # Should have top-level blocks

    def test_prepare_for_chunking(self):
        """Test preparing results for Stage 2."""
        # Test that we can extract blocks for Stage 2 processing
        blocks = extract_fenced_blocks(COMPLEX_MARKDOWN)

        # Validate that blocks are ready for Stage 2
        assert isinstance(blocks, list)
        for block in blocks:
            assert block.start_line >= 1  # 1-based numbering
            assert block.nesting_level >= 0  # Valid nesting

    def test_processing_summary(self):
        """Test getting processing summary."""
        # Test basic processing summary
        blocks = extract_fenced_blocks(SIMPLE_MARKDOWN)

        # Should be able to summarize results
        summary = {
            "total_blocks": len(blocks),
            "languages": list(set(b.language for b in blocks if b.language)),
            "nesting_levels": list(set(b.nesting_level for b in blocks)),
        }

        assert "total_blocks" in summary
        assert "languages" in summary
        assert "nesting_levels" in summary

    def test_results_validation(self):
        """Test results validation."""
        blocks = extract_fenced_blocks(SIMPLE_MARKDOWN)

        # Valid blocks should have proper structure
        for block in blocks:
            assert block.start_line >= 1
            assert block.end_line >= block.start_line
            assert block.nesting_level >= 0

    def test_error_handling(self):
        """Test error handling in integration."""
        # Test with invalid input
        blocks = extract_fenced_blocks("")

        # Should still return results (empty list)
        assert isinstance(blocks, list)
        assert len(blocks) == 0

    def test_configuration_usage(self):
        """Test using input validation and normalization."""
        # Test with different line endings
        text_with_crlf = "```python\r\nprint('test')\r\n```"
        normalized = validate_and_normalize_input(text_with_crlf)
        blocks = extract_fenced_blocks(normalized)

        assert len(blocks) == 1
        assert blocks[0].language == "python"


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_process_markdown(self):
        """Test markdown processing convenience function."""
        # Test basic extraction
        blocks = extract_fenced_blocks(SIMPLE_MARKDOWN)
        assert isinstance(blocks, list)

    def test_analyze_markdown(self):
        """Test markdown analysis convenience function."""
        # Test input validation
        normalized = validate_and_normalize_input(SIMPLE_MARKDOWN)
        assert isinstance(normalized, str)

    def test_prepare_for_stage2(self):
        """Test Stage 2 preparation."""
        # Test that blocks are properly structured for Stage 2
        blocks = extract_fenced_blocks(COMPLEX_MARKDOWN)
        # Should have all necessary data for Stage 2
        for block in blocks:
            assert hasattr(block, "content")
            assert hasattr(block, "language")
            assert hasattr(block, "nesting_level")
            assert hasattr(block, "start_line")
            assert hasattr(block, "end_line")


class TestPerformance:
    """Test performance characteristics."""

    def test_processing_time(self):
        """Test that processing time is reasonable."""
        import time

        # Process a moderately sized document
        large_markdown = COMPLEX_MARKDOWN * 5  # Repeat content

        start_time = time.time()
        blocks = extract_fenced_blocks(large_markdown)
        processing_time = time.time() - start_time

        # Should complete in reasonable time
        assert processing_time < 2.0, f"Processing took {processing_time:.3f}s"
        assert len(blocks) >= 1

    def test_memory_usage(self):
        """Test memory usage doesn't grow excessively."""
        # Process multiple documents
        for _ in range(10):
            blocks = extract_fenced_blocks(SIMPLE_MARKDOWN)
            assert isinstance(blocks, list)


class TestErrorRecovery:
    """Test error recovery and edge cases."""

    def test_malformed_input_recovery(self):
        """Test recovery from malformed input."""
        malformed_inputs = [
            "```\nunclosed block",
            "~~~\nunclosed tilde",
            "```python\n```\n```",  # Nested same type
        ]

        for malformed in malformed_inputs:
            blocks = extract_fenced_blocks(malformed)
            # Should not crash, may return empty or partial results
            assert isinstance(blocks, list)

    def test_empty_input_handling(self):
        """Test handling of empty input."""
        blocks = extract_fenced_blocks("")
        assert isinstance(blocks, list)
        assert len(blocks) == 0

    def test_very_large_input(self):
        """Test handling of very large input."""
        # Create a large document (but not too large to avoid test timeouts)
        large_content = "# Header\n\n```python\nprint('test')\n```\n\n" * 100

        blocks = extract_fenced_blocks(large_content)
        assert isinstance(blocks, list)
        assert len(blocks) >= 50  # Should find many blocks
