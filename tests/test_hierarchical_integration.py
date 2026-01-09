#!/usr/bin/env python3
"""Tests for hierarchical chunking integration with chunkana 0.1.1.

These tests verify that hierarchical mode works correctly with the new
tree invariant validation in chunkana 0.1.1.
"""

import json
import re
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from adapter import MigrationAdapter


# Test document with clear hierarchy
HIERARCHICAL_TEST_DOC = """# Main Document

This is the main document introduction.

## Chapter One

Chapter one introduction paragraph.

### Section 1.1

Content for section 1.1 with details.
More content to make this section substantial.

### Section 1.2

Content for section 1.2 with different details.
Additional content for testing purposes.

## Chapter Two

Chapter two introduction paragraph.

### Section 2.1

Content for section 2.1.
This section has its own content.

### Section 2.2

Content for section 2.2.
Final section content here.

## Conclusion

This is the conclusion of the document.
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


class TestHierarchicalModeBasic:
    """Basic tests for hierarchical mode."""
    
    @pytest.fixture
    def adapter(self):
        return MigrationAdapter()
    
    @pytest.fixture
    def config(self, adapter):
        return adapter.build_chunker_config(
            max_chunk_size=500,
            chunk_overlap=50,
        )
    
    def test_hierarchical_produces_chunks(self, adapter, config):
        """Hierarchical mode should produce chunks."""
        result = adapter.run_chunking(
            input_text=HIERARCHICAL_TEST_DOC,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=False,
        )
        
        assert len(result) > 0, "Should produce at least one chunk"
    
    def test_hierarchical_debug_produces_more_chunks(self, adapter, config):
        """Debug mode should include non-leaf chunks."""
        result_normal = adapter.run_chunking(
            input_text=HIERARCHICAL_TEST_DOC,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=False,
        )
        
        result_debug = adapter.run_chunking(
            input_text=HIERARCHICAL_TEST_DOC,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=True,
        )
        
        # Debug mode includes all chunks (root, intermediate, leaf)
        # Normal mode includes only leaf chunks
        assert len(result_debug) >= len(result_normal), \
            f"Debug should have >= chunks: {len(result_debug)} vs {len(result_normal)}"


class TestHierarchicalInvariants:
    """Tests for tree invariants in hierarchical mode."""
    
    @pytest.fixture
    def adapter(self):
        return MigrationAdapter()
    
    @pytest.fixture
    def config(self, adapter):
        return adapter.build_chunker_config(
            max_chunk_size=500,
            chunk_overlap=50,
        )
    
    def test_is_leaf_consistency(self, adapter, config):
        """is_leaf should be consistent with children_ids."""
        result = adapter.run_chunking(
            input_text=HIERARCHICAL_TEST_DOC,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=True,  # Include all chunks to check invariants
        )
        
        for chunk_str in result:
            metadata, _ = parse_dify_chunk(chunk_str)
            
            children_ids = metadata.get("children_ids", [])
            is_leaf = metadata.get("is_leaf", True)
            
            # Invariant: is_leaf == (children_ids is empty)
            if children_ids:
                assert not is_leaf, \
                    f"Chunk with children should have is_leaf=False: {metadata.get('chunk_id')}"
            else:
                assert is_leaf, \
                    f"Chunk without children should have is_leaf=True: {metadata.get('chunk_id')}"
    
    def test_chunk_ids_present(self, adapter, config):
        """All chunks should have chunk_id."""
        result = adapter.run_chunking(
            input_text=HIERARCHICAL_TEST_DOC,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=True,
        )
        
        chunk_ids = set()
        for chunk_str in result:
            metadata, _ = parse_dify_chunk(chunk_str)
            chunk_id = metadata.get("chunk_id")
            assert chunk_id is not None, "All chunks should have chunk_id"
            assert chunk_id not in chunk_ids, f"Duplicate chunk_id: {chunk_id}"
            chunk_ids.add(chunk_id)
    
    def test_parent_child_references_valid(self, adapter, config):
        """Parent-child references should be valid."""
        result = adapter.run_chunking(
            input_text=HIERARCHICAL_TEST_DOC,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=True,
        )
        
        # Collect all chunk IDs
        chunk_ids = set()
        chunks_by_id = {}
        
        for chunk_str in result:
            metadata, _ = parse_dify_chunk(chunk_str)
            chunk_id = metadata.get("chunk_id")
            if chunk_id:
                chunk_ids.add(chunk_id)
                chunks_by_id[chunk_id] = metadata
        
        # Verify parent references
        for chunk_id, metadata in chunks_by_id.items():
            parent_id = metadata.get("parent_id")
            if parent_id:
                assert parent_id in chunk_ids, \
                    f"Parent {parent_id} not found for chunk {chunk_id}"
            
            # Verify children references
            children_ids = metadata.get("children_ids", [])
            for child_id in children_ids:
                assert child_id in chunk_ids, \
                    f"Child {child_id} not found for chunk {chunk_id}"


class TestDebugModeBehavior:
    """Tests for debug mode behavior."""
    
    @pytest.fixture
    def adapter(self):
        return MigrationAdapter()
    
    @pytest.fixture
    def config(self, adapter):
        return adapter.build_chunker_config(
            max_chunk_size=500,
            chunk_overlap=50,
        )
    
    def test_debug_false_returns_flat_chunks(self, adapter, config):
        """Debug=False should return flat chunks (leaves + significant non-leaves)."""
        result = adapter.run_chunking(
            input_text=HIERARCHICAL_TEST_DOC,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=False,
        )
        
        # In chunkana 0.1.1, get_flat_chunks() returns:
        # - All leaf chunks
        # - Non-leaf chunks with significant content (>100 chars)
        # This prevents content loss
        for chunk_str in result:
            metadata, body = parse_dify_chunk(chunk_str)
            children_ids = metadata.get("children_ids", [])
            
            # If chunk has children, it should have significant content
            if children_ids:
                # Non-leaf chunks in flat output should have substantial content
                assert len(body.strip()) > 50, \
                    f"Non-leaf chunk in flat output should have significant content"
    
    def test_debug_true_includes_all_chunks(self, adapter, config):
        """Debug=True should include root and intermediate chunks."""
        result = adapter.run_chunking(
            input_text=HIERARCHICAL_TEST_DOC,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=True,
        )
        
        has_non_leaf = False
        for chunk_str in result:
            metadata, _ = parse_dify_chunk(chunk_str)
            children_ids = metadata.get("children_ids", [])
            if children_ids:
                has_non_leaf = True
                break
        
        # Debug mode should include at least some non-leaf chunks
        # (unless document is too small to have hierarchy)
        # This is a soft assertion - small docs may not have hierarchy
        if len(result) > 3:
            assert has_non_leaf, "Debug mode should include non-leaf chunks for hierarchical docs"
    
    def test_non_hierarchical_debug_behavior(self, adapter, config):
        """Debug flag in non-hierarchical mode should not break chunking."""
        # Debug=True with hierarchy=False
        result_debug = adapter.run_chunking(
            input_text=HIERARCHICAL_TEST_DOC,
            config=config,
            include_metadata=True,
            enable_hierarchy=False,
            debug=True,
        )
        
        # Debug=False with hierarchy=False
        result_normal = adapter.run_chunking(
            input_text=HIERARCHICAL_TEST_DOC,
            config=config,
            include_metadata=True,
            enable_hierarchy=False,
            debug=False,
        )
        
        # Both should produce chunks
        assert len(result_debug) > 0
        assert len(result_normal) > 0
        
        # Chunk count should be the same (debug only affects metadata in non-hierarchical)
        assert len(result_debug) == len(result_normal)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
