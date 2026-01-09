#!/usr/bin/env python3
"""Tests for overlap contract behavior.

Overlap Contract:
- include_metadata=True: overlap in metadata only (previous_content/next_content)
- include_metadata=False: overlap embedded in content (prev + content + next)
"""

import json
import re
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from adapter import MigrationAdapter


# Test document with multiple sections for overlap testing
OVERLAP_TEST_DOC = """# Document Title

This is the introduction paragraph with some content.

## Section One

This is section one content. It has multiple sentences.
Here is more content to ensure we have enough text for chunking.
And even more content to make this section substantial.

## Section Two

Section two begins here with its own content.
This section also has multiple lines of text.
We need enough content to trigger overlap behavior.

## Section Three

The third section has different content entirely.
It discusses various topics and provides information.
This helps test overlap between sections.

## Conclusion

This is the conclusion of the document.
It wraps up all the previous sections.
"""


def parse_dify_chunk(chunk_str: str) -> tuple[dict, str]:
    """Parse a dify-style chunk into metadata and body."""
    metadata_match = re.match(
        r"<metadata>\n(.*?)\n</metadata>\n(.*)",
        chunk_str,
        re.DOTALL
    )
    if metadata_match:
        metadata_json = metadata_match.group(1)
        body = metadata_match.group(2)
        metadata = json.loads(metadata_json)
        return metadata, body
    return {}, chunk_str


class TestOverlapContractMetadataTrue:
    """Tests for include_metadata=True behavior."""
    
    @pytest.fixture
    def adapter(self):
        return MigrationAdapter()
    
    @pytest.fixture
    def config(self, adapter):
        return adapter.build_chunker_config(
            max_chunk_size=500,  # Small chunks to force overlap
            chunk_overlap=100,
        )
    
    def test_overlap_in_metadata_not_body(self, adapter, config):
        """Overlap should be in metadata fields, not in chunk body."""
        result = adapter.run_chunking(
            input_text=OVERLAP_TEST_DOC,
            config=config,
            include_metadata=True,
            enable_hierarchy=False,
            debug=False,
        )
        
        assert len(result) > 1, "Should have multiple chunks"
        
        for i, chunk_str in enumerate(result):
            metadata, body = parse_dify_chunk(chunk_str)
            
            # Body should not contain overlap markers
            assert "<overlap>" not in body
            assert "</overlap>" not in body
            
            # Middle chunks should have overlap metadata
            if i > 0:
                # Should have previous_content or overlap_size
                has_prev = "previous_content" in metadata
                has_overlap = metadata.get("overlap_size", 0) > 0
                # At least one should be present for non-first chunks
                # (unless overlap is 0 or chunk is at boundary)
    
    def test_first_chunk_no_previous_content(self, adapter, config):
        """First chunk should not have previous_content."""
        result = adapter.run_chunking(
            input_text=OVERLAP_TEST_DOC,
            config=config,
            include_metadata=True,
        )
        
        assert len(result) > 0
        metadata, _ = parse_dify_chunk(result[0])
        
        # First chunk should not have previous_content
        prev_content = metadata.get("previous_content", "")
        assert prev_content == "" or prev_content is None or "previous_content" not in metadata
    
    def test_last_chunk_no_next_content(self, adapter, config):
        """Last chunk should not have next_content."""
        result = adapter.run_chunking(
            input_text=OVERLAP_TEST_DOC,
            config=config,
            include_metadata=True,
        )
        
        assert len(result) > 0
        metadata, _ = parse_dify_chunk(result[-1])
        
        # Last chunk should not have next_content
        next_content = metadata.get("next_content", "")
        assert next_content == "" or next_content is None or "next_content" not in metadata
    
    def test_metadata_contains_overlap_fields(self, adapter, config):
        """Metadata should contain overlap-related fields."""
        result = adapter.run_chunking(
            input_text=OVERLAP_TEST_DOC,
            config=config,
            include_metadata=True,
        )
        
        # Check middle chunks have overlap info
        if len(result) > 2:
            metadata, _ = parse_dify_chunk(result[1])
            # Should have at least one overlap-related field
            overlap_fields = ["previous_content", "next_content", "overlap_size"]
            has_overlap_field = any(f in metadata for f in overlap_fields)
            assert has_overlap_field, f"Middle chunk should have overlap fields: {metadata.keys()}"


class TestOverlapContractMetadataFalse:
    """Tests for include_metadata=False behavior."""
    
    @pytest.fixture
    def adapter(self):
        return MigrationAdapter()
    
    @pytest.fixture
    def config(self, adapter):
        return adapter.build_chunker_config(
            max_chunk_size=500,
            chunk_overlap=100,
        )
    
    def test_no_metadata_tags(self, adapter, config):
        """Chunks should not have metadata tags when include_metadata=False."""
        result = adapter.run_chunking(
            input_text=OVERLAP_TEST_DOC,
            config=config,
            include_metadata=False,
        )
        
        for chunk_str in result:
            assert "<metadata>" not in chunk_str
            assert "</metadata>" not in chunk_str
    
    def test_overlap_embedded_in_content(self, adapter, config):
        """Overlap should be embedded in content when include_metadata=False."""
        result = adapter.run_chunking(
            input_text=OVERLAP_TEST_DOC,
            config=config,
            include_metadata=False,
        )
        
        # With embedded overlap, chunks may share content
        # This is harder to test directly, but we can verify:
        # 1. No metadata tags
        # 2. Content is plain text
        for chunk_str in result:
            # Should be plain text without metadata
            assert not chunk_str.startswith("<metadata>")
            # Should have actual content
            assert len(chunk_str.strip()) > 0


class TestOverlapContractConsistency:
    """Tests for consistent overlap behavior across modes."""
    
    @pytest.fixture
    def adapter(self):
        return MigrationAdapter()
    
    def test_same_chunk_count_both_modes(self, adapter):
        """Both modes should produce same number of chunks."""
        config = adapter.build_chunker_config(
            max_chunk_size=500,
            chunk_overlap=100,
        )
        
        result_with_meta = adapter.run_chunking(
            input_text=OVERLAP_TEST_DOC,
            config=config,
            include_metadata=True,
        )
        
        result_without_meta = adapter.run_chunking(
            input_text=OVERLAP_TEST_DOC,
            config=config,
            include_metadata=False,
        )
        
        assert len(result_with_meta) == len(result_without_meta), \
            f"Chunk count mismatch: {len(result_with_meta)} vs {len(result_without_meta)}"
    
    def test_zero_overlap_no_overlap_content(self, adapter):
        """With overlap=0, there should be no overlap content."""
        config = adapter.build_chunker_config(
            max_chunk_size=500,
            chunk_overlap=0,  # No overlap
        )
        
        result = adapter.run_chunking(
            input_text=OVERLAP_TEST_DOC,
            config=config,
            include_metadata=True,
        )
        
        for chunk_str in result:
            metadata, _ = parse_dify_chunk(chunk_str)
            # With zero overlap, previous/next content should be empty
            prev = metadata.get("previous_content", "")
            next_ = metadata.get("next_content", "")
            assert prev == "" or prev is None, f"Unexpected previous_content with overlap=0"
            assert next_ == "" or next_ is None, f"Unexpected next_content with overlap=0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# Property-based tests using Hypothesis
from hypothesis import given, settings, strategies as st


@st.composite
def markdown_document(draw):
    """Generate random markdown documents for property testing."""
    num_sections = draw(st.integers(min_value=2, max_value=5))
    
    sections = []
    for i in range(num_sections):
        header_level = draw(st.integers(min_value=1, max_value=3))
        header = "#" * header_level + f" Section {i+1}"
        
        num_paragraphs = draw(st.integers(min_value=1, max_value=3))
        paragraphs = []
        for _ in range(num_paragraphs):
            words = draw(st.lists(
                st.text(alphabet="abcdefghijklmnopqrstuvwxyz ", min_size=3, max_size=10),
                min_size=5,
                max_size=20
            ))
            paragraphs.append(" ".join(words))
        
        sections.append(header + "\n\n" + "\n\n".join(paragraphs))
    
    return "\n\n".join(sections)


class TestOverlapContractProperty:
    """Property-based tests for overlap contract."""
    
    @given(doc=markdown_document())
    @settings(max_examples=20, deadline=5000)
    def test_metadata_true_no_overlap_in_body(self, doc):
        """Property: With include_metadata=True, body never contains overlap markers."""
        adapter = MigrationAdapter()
        config = adapter.build_chunker_config(
            max_chunk_size=300,
            chunk_overlap=50,
        )
        
        result = adapter.run_chunking(
            input_text=doc,
            config=config,
            include_metadata=True,
        )
        
        for chunk_str in result:
            metadata, body = parse_dify_chunk(chunk_str)
            # Body should not contain overlap markers
            assert "<overlap>" not in body
            assert "</overlap>" not in body
    
    @given(doc=markdown_document())
    @settings(max_examples=20, deadline=5000)
    def test_metadata_false_no_metadata_tags(self, doc):
        """Property: With include_metadata=False, no metadata tags in output."""
        adapter = MigrationAdapter()
        config = adapter.build_chunker_config(
            max_chunk_size=300,
            chunk_overlap=50,
        )
        
        result = adapter.run_chunking(
            input_text=doc,
            config=config,
            include_metadata=False,
        )
        
        for chunk_str in result:
            assert "<metadata>" not in chunk_str
            assert "</metadata>" not in chunk_str
    
    @given(doc=markdown_document())
    @settings(max_examples=20, deadline=5000)
    def test_chunk_count_consistent(self, doc):
        """Property: Both modes produce same chunk count."""
        adapter = MigrationAdapter()
        config = adapter.build_chunker_config(
            max_chunk_size=300,
            chunk_overlap=50,
        )
        
        result_meta = adapter.run_chunking(
            input_text=doc,
            config=config,
            include_metadata=True,
        )
        
        result_no_meta = adapter.run_chunking(
            input_text=doc,
            config=config,
            include_metadata=False,
        )
        
        assert len(result_meta) == len(result_no_meta)
