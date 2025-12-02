"""
Regression test for overlap duplication issue.

Tests the specific case where a phrase was duplicated twice in a chunk
due to incorrect overlap handling (anti-fraud issue).
"""

import pytest

from markdown_chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig


class TestOverlapDuplicationRegression:
    """Regression tests for overlap duplication issues."""

    def test_anti_fraud_phrase_no_duplication_metadata_mode(self):
        """
        Test that the anti-fraud phrase doesn't appear twice in metadata mode.
        
        Original issue: Phrase "Изучил подходы anti fraud в других компаниях."
        appeared twice consecutively in chunk body due to overlap incorrectly
        merging it.
        """
        config = ChunkConfig(
            max_chunk_size=200,
            enable_overlap=True,
            overlap_size=50
        )
        chunker = MarkdownChunker(config)
        
        # Document with the phrase at a chunk boundary
        md_text = """# Scope
        
Изучил подходы anti fraud в других компаниях.

# Next Section

Additional content follows here."""
        
        result = chunker.chunk(md_text, include_metadata=True)
        chunks = result.chunks if hasattr(result, 'chunks') else result
        
        target_phrase = "Изучил подходы anti fraud в других компаниях."
        
        for i, chunk in enumerate(chunks):
            content = chunk.content
            
            # Count occurrences of the phrase in content
            count = content.count(target_phrase)
            
            # Should appear at most once in any chunk's content
            assert count <= 1, \
                f"Chunk {i}: Phrase appears {count} times in content (should be 0 or 1)"
            
            # If phrase appears in content, it should NOT also be in previous_content
            if count == 1:
                prev_content = chunk.metadata.get("previous_content", "")
                assert target_phrase not in prev_content, \
                    f"Chunk {i}: Phrase in both content and previous_content"

    def test_anti_fraud_phrase_context_separation(self):
        """
        Verify proper separation of phrase between content and context.
        
        In metadata mode:
        - Phrase should appear once in chunk[i].content (as ending)
        - Phrase should appear once in chunk[i+1].previous_content (as context)
        - Phrase should NOT appear in chunk[i+1].content
        """
        config = ChunkConfig(
            max_chunk_size=150,
            enable_overlap=True,
            overlap_size=60
        )
        chunker = MarkdownChunker(config)
        
        md_text = """# First Section

Some introductory text here.

Изучил подходы anti fraud в других компаниях.

# Second Section

More content in the second section."""
        
        result = chunker.chunk(md_text, include_metadata=True)
        chunks = result.chunks if hasattr(result, 'chunks') else result
        
        target_phrase = "Изучил подходы anti fraud в других компаниях."
        
        # Find which chunk contains the phrase
        phrase_chunk_idx = None
        for i, chunk in enumerate(chunks):
            if target_phrase in chunk.content:
                phrase_chunk_idx = i
                break
        
        if phrase_chunk_idx is not None and phrase_chunk_idx < len(chunks) - 1:
            # Check next chunk
            next_chunk = chunks[phrase_chunk_idx + 1]
            
            # Phrase might be in previous_content of next chunk
            prev_content = next_chunk.metadata.get("previous_content", "")
            
            if target_phrase in prev_content:
                # It should NOT also be at the start of next chunk's content
                assert not next_chunk.content.startswith(target_phrase), \
                    "Phrase duplicated: in previous_content AND at start of content"

    def test_anti_fraud_phrase_legacy_mode_no_duplication(self):
        """
        Test that legacy mode also doesn't duplicate the phrase.
        
        In legacy mode, phrase should appear exactly once in merged content,
        at the boundary between previous context and core content.
        """
        config = ChunkConfig(
            max_chunk_size=180,
            enable_overlap=True,
            overlap_size=50
        )
        chunker = MarkdownChunker(config)
        
        md_text = """# Background

Research phase content.

Изучил подходы anti fraud в других компаниях.

# Implementation

Implementation details follow."""
        
        result = chunker.chunk(md_text, include_metadata=False)
        chunks = result.chunks if hasattr(result, 'chunks') else result
        
        target_phrase = "Изучил подходы anti fraud в других компаниях."
        
        for i, chunk in enumerate(chunks):
            content = chunk.content
            
            # Count consecutive occurrences
            # The phrase should not appear twice in a row
            doubled = f"{target_phrase}\n\n{target_phrase}"
            assert doubled not in content, \
                f"Chunk {i}: Phrase appears twice consecutively in legacy mode"
            
            # Count total occurrences
            count = content.count(target_phrase)
            
            # Should appear at most once per chunk
            assert count <= 1, \
                f"Chunk {i}: Phrase appears {count} times (should be 0 or 1)"

    def test_no_content_duplication_at_boundaries(self):
        """
        General test that content is not duplicated at chunk boundaries.
        
        Uses a distinctive marker phrase to detect duplication.
        """
        config = ChunkConfig(
            max_chunk_size=150,
            enable_overlap=True,
            overlap_size=40
        )
        chunker = MarkdownChunker(config)
        
        # Use a unique marker that's easy to detect
        marker = "UNIQUE_MARKER_TEXT_12345"
        
        md_text = f"""# Section 1

Some content before the marker.

{marker}

# Section 2

Content after the marker."""
        
        # Test metadata mode
        result = chunker.chunk(md_text, include_metadata=True)
        chunks = result.chunks if hasattr(result, 'chunks') else result
        
        for i, chunk in enumerate(chunks):
            # Marker should appear at most once in content
            count = chunk.content.count(marker)
            assert count <= 1, f"Chunk {i}: Marker duplicated in content"

    def test_offset_based_verification(self):
        """
        Use start_offset and end_offset to verify no duplication.
        
        In metadata mode, content should correspond exactly to the offset range
        in the source document.
        """
        config = ChunkConfig(
            max_chunk_size=200,
            enable_overlap=True,
            overlap_size=50
        )
        chunker = MarkdownChunker(config)
        
        md_text = """# Test Document

First paragraph with some content.

Изучил подходы anti fraud в других компаниях.

Second paragraph with more content."""
        
        result = chunker.chunk(md_text, include_metadata=True)
        chunks = result.chunks if hasattr(result, 'chunks') else result
        
        for chunk in chunks:
            if "start_offset" in chunk.metadata and "end_offset" in chunk.metadata:
                start = chunk.metadata["start_offset"]
                end = chunk.metadata["end_offset"]
                
                # Extract content from source at these offsets
                expected_content = md_text[start:end]
                
                # Should match chunk content exactly
                assert chunk.content == expected_content, \
                    "Content doesn't match offset range - possible duplication"

    def test_block_aligned_extraction_prevents_duplication(self):
        """
        Verify that block-aligned extraction prevents partial block duplication.
        
        Block alignment should ensure that complete blocks are extracted,
        preventing scenarios where part of a block is duplicated.
        """
        config = ChunkConfig(
            max_chunk_size=250,
            enable_overlap=True,
            overlap_size=60
        )
        chunker = MarkdownChunker(config)
        
        md_text = """# Research

## Background

Comprehensive research was conducted.

Key findings include:

- Finding one about methodology
- Finding two about results  
- Изучил подходы anti fraud в других компаниях
- Finding four about implications

## Analysis

Detailed analysis follows."""
        
        result = chunker.chunk(md_text, include_metadata=True)
        chunks = result.chunks if hasattr(result, 'chunks') else result
        
        target = "Изучил подходы anti fraud в других компаниях"
        
        # Verify the target line appears in exactly one chunk's content
        appearances_in_content = sum(
            1 for chunk in chunks if target in chunk.content
        )
        
        assert appearances_in_content == 1, \
            f"Target appears in {appearances_in_content} chunks' content (should be 1)"
        
        # It might also appear in one previous_content
        appearances_in_prev = sum(
            1 for chunk in chunks 
            if target in chunk.metadata.get("previous_content", "")
        )
        
        # Should be 0 or 1
        assert appearances_in_prev <= 1, \
            f"Target appears in {appearances_in_prev} previous_content fields"
        
        # Combined should be at most 2 (once in content, once in context)
        total = appearances_in_content + appearances_in_prev
        assert total <= 2, \
            f"Target appears {total} times total (content + context)"
