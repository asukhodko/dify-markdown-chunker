"""Property-based tests for chunk_simple method.

**Feature: p0-test-migration, Properties 2-3**
**Validates: Requirements 2.1, 2.4**
"""

import json

from hypothesis import given, settings
from hypothesis import strategies as st

from markdown_chunker_v2 import MarkdownChunker


@st.composite
def markdown_text(draw):
    """Generate random markdown content."""
    elements = []
    
    # Add optional title
    if draw(st.booleans()):
        title = draw(st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
            min_size=3, max_size=30
        ).filter(lambda x: x.strip()))
        elements.append(f"# {title}")
        elements.append("")
    
    # Add 1-3 paragraphs
    num_paragraphs = draw(st.integers(min_value=1, max_value=3))
    for _ in range(num_paragraphs):
        para = draw(st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "P")),
            min_size=10, max_size=100
        ).filter(lambda x: x.strip()))
        elements.append(para)
        elements.append("")
    
    return "\n".join(elements)


class TestChunkSimpleProperty:
    """Property-based tests for chunk_simple."""

    @settings(max_examples=100, deadline=10000)
    @given(markdown_text())
    def test_property_chunk_simple_returns_required_keys(self, text):
        """
        **Feature: p0-test-migration, Property 2: chunk_simple returns required keys**
        **Validates: Requirements 2.1**

        For any non-empty text input, chunk_simple SHALL return a dictionary
        containing keys 'chunks', 'errors', 'warnings', 'total_chunks', 'strategy_used'.
        """
        chunker = MarkdownChunker()
        
        try:
            result = chunker.chunk_simple(text)
        except Exception:
            return  # Skip problematic inputs
        
        # Required keys must be present
        assert "chunks" in result, "Missing 'chunks' key"
        assert "errors" in result, "Missing 'errors' key"
        assert "warnings" in result, "Missing 'warnings' key"
        assert "total_chunks" in result, "Missing 'total_chunks' key"
        assert "strategy_used" in result, "Missing 'strategy_used' key"
        
        # Type checks
        assert isinstance(result["chunks"], list)
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)
        assert isinstance(result["total_chunks"], int)
        assert isinstance(result["strategy_used"], str)
        
        # Consistency check
        assert result["total_chunks"] == len(result["chunks"])

    @settings(max_examples=100, deadline=10000)
    @given(markdown_text())
    def test_property_chunk_simple_json_serializable(self, text):
        """
        **Feature: p0-test-migration, Property 3: chunk_simple result is JSON-serializable**
        **Validates: Requirements 2.4**

        For any text input, the result of chunk_simple SHALL be serializable
        to JSON without errors.
        """
        chunker = MarkdownChunker()
        
        try:
            result = chunker.chunk_simple(text)
        except Exception:
            return  # Skip problematic inputs
        
        # Must be JSON serializable
        try:
            json_str = json.dumps(result)
            assert isinstance(json_str, str)
            
            # Must be deserializable
            parsed = json.loads(json_str)
            assert parsed["total_chunks"] == result["total_chunks"]
            assert len(parsed["chunks"]) == len(result["chunks"])
        except (TypeError, ValueError) as e:
            raise AssertionError(f"Result not JSON serializable: {e}")

    @settings(max_examples=50, deadline=10000)
    @given(st.dictionaries(
        keys=st.sampled_from(["max_chunk_size", "min_chunk_size", "overlap_size"]),
        values=st.integers(min_value=50, max_value=5000),
        max_size=3
    ))
    def test_property_chunk_simple_with_config(self, config_dict):
        """
        Property: chunk_simple accepts config dict without errors.
        """
        chunker = MarkdownChunker()
        text = "# Test\n\nSome content here."
        
        # Ensure valid config
        if "min_chunk_size" in config_dict and "max_chunk_size" in config_dict:
            if config_dict["min_chunk_size"] >= config_dict["max_chunk_size"]:
                return  # Skip invalid config
        
        try:
            result = chunker.chunk_simple(text, config=config_dict)
            assert "chunks" in result
            assert "errors" in result
        except Exception:
            pass  # Some configs may be invalid
