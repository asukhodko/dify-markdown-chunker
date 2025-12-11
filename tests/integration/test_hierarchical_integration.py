"""
Integration tests for hierarchical chunking with real corpus documents.

Tests hierarchy with various document types from corpus.
"""

from pathlib import Path

import pytest

from markdown_chunker_v2 import ChunkConfig, MarkdownChunker


class TestHierarchyCorpusIntegration:
    """Integration tests with real corpus documents."""

    CORPUS_FILES = [
        "tests/corpus/github_readmes/python/youtube-dl.md",
        "tests/corpus/github_readmes/javascript/axios.md",
        "tests/corpus/changelogs/changelogs_005.md",
        "tests/corpus/github_readmes/python/pytorch.md",
    ]

    @pytest.fixture
    def chunker(self):
        """Create chunker with default config."""
        return MarkdownChunker(ChunkConfig(max_chunk_size=2000))

    @pytest.mark.parametrize("filepath", CORPUS_FILES)
    def test_corpus_hierarchy_invariants(self, chunker, filepath):
        """All hierarchy invariants hold on real corpus files."""
        path = Path(filepath)
        if not path.exists():
            pytest.skip(f"File {filepath} not found")

        text = path.read_text(encoding="utf-8")
        result = chunker.chunk_hierarchical(text)

        # Invariant 1: Root created
        assert result.root_id
        root = result.get_chunk(result.root_id)
        assert root is not None

        # Invariant 2: All chunks have chunk_id
        for chunk in result.chunks:
            assert chunk.metadata.get("chunk_id"), "Missing chunk_id"

        # Invariant 3: Exactly one root
        roots = [c for c in result.chunks if c.metadata.get("parent_id") is None]
        assert len(roots) == 1

        # Invariant 4: All children_ids reference valid chunks
        for chunk in result.chunks:
            for child_id in chunk.metadata.get("children_ids", []):
                assert result.get_chunk(child_id), f"Invalid child_id: {child_id}"

        # Invariant 5: All parent_id reference valid chunks
        for chunk in result.chunks:
            parent_id = chunk.metadata.get("parent_id")
            if parent_id:
                assert result.get_chunk(parent_id), f"Invalid parent_id: {parent_id}"

    @pytest.mark.parametrize("filepath", CORPUS_FILES)
    def test_corpus_navigation_works(self, chunker, filepath):
        """Navigation methods work correctly on corpus."""
        path = Path(filepath)
        if not path.exists():
            pytest.skip(f"File {filepath} not found")

        text = path.read_text(encoding="utf-8")
        result = chunker.chunk_hierarchical(text)

        # Test navigation from random chunks
        leaf_chunks = result.get_flat_chunks()
        if len(leaf_chunks) > 0:
            test_chunk = leaf_chunks[len(leaf_chunks) // 2]
            chunk_id = test_chunk.metadata["chunk_id"]

            # Can get parent
            parent = result.get_parent(chunk_id)
            # Either has parent or is child of root
            if parent:
                assert parent.metadata["chunk_id"] in [
                    test_chunk.metadata.get("parent_id")
                ]

            # Can get ancestors
            ancestors = result.get_ancestors(chunk_id)
            if ancestors:
                assert ancestors[-1].metadata["chunk_id"] == result.root_id

            # Can get siblings
            siblings = result.get_siblings(chunk_id)
            assert test_chunk in siblings

    @pytest.mark.parametrize("filepath", CORPUS_FILES)
    def test_corpus_flat_chunks_backward_compatible(self, chunker, filepath):
        """get_flat_chunks provides backward-compatible output."""
        path = Path(filepath)
        if not path.exists():
            pytest.skip(f"File {filepath} not found")

        text = path.read_text(encoding="utf-8")
        result = chunker.chunk_hierarchical(text)

        flat_chunks = result.get_flat_chunks()

        # All flat chunks are leaves
        for chunk in flat_chunks:
            assert chunk.metadata.get("is_leaf") is True

        # Flat chunks contain actual content
        for chunk in flat_chunks:
            assert len(chunk.content) > 0


class TestBackwardCompatibility:
    """Test backward compatibility with existing chunk() API."""

    def test_chunk_method_unchanged(self):
        """Original chunk() method still works."""
        chunker = MarkdownChunker()
        text = "# Header\n\nContent here."

        chunks = chunker.chunk(text)

        # Returns list of Chunk objects
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        # No hierarchy metadata in flat mode
        assert "chunk_id" not in chunks[0].metadata

    def test_hierarchical_is_opt_in(self):
        """Hierarchical features are opt-in via separate method."""
        chunker = MarkdownChunker()
        text = "# Header\n\nContent here."

        # chunk() returns flat list
        flat = chunker.chunk(text)
        assert "chunk_id" not in flat[0].metadata

        # chunk_hierarchical() adds hierarchy
        hierarchical = chunker.chunk_hierarchical(text)
        assert hasattr(hierarchical, "get_chunk")
        assert hierarchical.root_id

    def test_config_include_document_summary(self):
        """include_document_summary config parameter works."""
        # With summary (default)
        config = ChunkConfig(include_document_summary=True)
        chunker = MarkdownChunker(config)
        text = "# Header\n\nContent"

        result = chunker.chunk_hierarchical(text)
        root = result.get_chunk(result.root_id)
        assert root is not None
        assert root.metadata.get("is_root") is True

        # Without summary
        config_no_summary = ChunkConfig(include_document_summary=False)
        chunker_no_summary = MarkdownChunker(config_no_summary)
        result_no_summary = chunker_no_summary.chunk_hierarchical(text)

        # Should still have root_id (first chunk)
        assert result_no_summary.root_id


class TestPerformance:
    """Performance tests for hierarchical chunking."""

    def test_large_document_performance(self):
        """Hierarchy building is fast on large documents."""
        import time

        # Create document with 100 headers
        headers = ["# " + f"Section {i}\n\nContent {i}.\n\n" for i in range(100)]
        text = "".join(headers)

        chunker = MarkdownChunker()

        start = time.time()
        result = chunker.chunk_hierarchical(text)
        elapsed = time.time() - start

        # Should complete in < 1 second for 100 chunks
        assert elapsed < 1.0

        # Verify result is valid
        assert len(result.chunks) > 0
        assert result.root_id

    def test_navigation_is_fast(self):
        """Navigation operations are O(1)."""
        import time

        # Create large hierarchy
        headers = ["# " + f"Section {i}\n\nContent {i}.\n\n" for i in range(50)]
        text = "".join(headers)

        chunker = MarkdownChunker()
        result = chunker.chunk_hierarchical(text)

        # Test O(1) lookups
        chunk_ids = [c.metadata["chunk_id"] for c in result.chunks]

        start = time.time()
        for chunk_id in chunk_ids[:10]:
            result.get_chunk(chunk_id)
            result.get_children(chunk_id)
            result.get_parent(chunk_id)
        elapsed = time.time() - start

        # Should be very fast (< 10ms for 30 operations)
        assert elapsed < 0.01
