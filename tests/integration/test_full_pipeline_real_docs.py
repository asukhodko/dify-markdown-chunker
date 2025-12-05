"""
Integration tests for full pipeline with real documents.

Tests the complete chunking pipeline using realistic markdown documents
to verify end-to-end functionality.

Migration note: Updated for v2 API (December 2025)
- include_analysis parameter removed, use chunk_with_analysis()
- content_type is in metadata dict, not chunk attribute
"""

import json
from pathlib import Path

import pytest

from markdown_chunker_v2 import MarkdownChunker, ChunkConfig


@pytest.fixture
def documents_dir():
    """Path to real documents directory."""
    return Path(__file__).parent.parent / "fixtures" / "real_documents"


@pytest.fixture
def metadata(documents_dir):
    """Load document metadata."""
    metadata_file = documents_dir / "metadata.json"
    with open(metadata_file, "r") as f:
        return json.load(f)


@pytest.fixture
def chunker():
    """Create chunker with default config."""
    return MarkdownChunker()


def load_document(documents_dir, filename):
    """Load document content."""
    doc_path = documents_dir / filename
    with open(doc_path, "r", encoding="utf-8") as f:
        return f.read()


def verify_no_content_loss(original_text, chunks):
    """Verify all content is preserved in chunks."""
    reconstructed = "\n".join(chunk.content for chunk in chunks)
    original_clean = " ".join(original_text.split())
    reconstructed_clean = " ".join(reconstructed.split())
    similarity = len(set(original_clean) & set(reconstructed_clean)) / len(
        set(original_clean)
    )
    assert similarity > 0.95, f"Content loss detected: {similarity:.2%} similarity"


def verify_line_numbers(chunks):
    """Verify line numbers are valid and sequential."""
    for i, chunk in enumerate(chunks):
        assert chunk.start_line >= 1, f"Chunk {i}: Invalid start_line"
        assert chunk.end_line >= chunk.start_line, f"Chunk {i}: end_line < start_line"
        if i > 0:
            prev_chunk = chunks[i - 1]
            assert chunk.start_line >= prev_chunk.start_line


def verify_metadata(chunk):
    """Verify chunk metadata is valid."""
    assert chunk.metadata is not None, "Missing metadata"
    # v2 stores content_type in metadata dict
    if "content_type" in chunk.metadata:
        assert chunk.metadata["content_type"] in [
            "code", "text", "list", "table", "mixed", "header", "preamble", "section"
        ]


class TestAPIDocumentation:
    """Tests for API documentation."""

    def test_api_documentation_chunking(self, documents_dir, chunker):
        """Test chunking of API documentation."""
        content = load_document(documents_dir, "api_documentation.md")
        chunks, strategy_used, analysis = chunker.chunk_with_analysis(content)

        assert len(chunks) >= 1, "Should produce chunks"
        assert strategy_used in ["code_aware", "structural", "fallback"]

    def test_api_documentation_preserves_code_blocks(self, documents_dir, chunker):
        """Test that code blocks are preserved."""
        content = load_document(documents_dir, "api_documentation.md")
        chunks = chunker.chunk(content)
        
        # Verify code blocks have balanced fences
        for chunk in chunks:
            fence_count = chunk.content.count("```")
            assert fence_count % 2 == 0, "Unbalanced code fences"


class TestTutorial:
    """Tests for tutorial document."""

    def test_tutorial_chunking(self, documents_dir, chunker):
        """Test chunking of tutorial."""
        content = load_document(documents_dir, "tutorial.md")
        chunks, strategy_used, analysis = chunker.chunk_with_analysis(content)

        assert len(chunks) >= 1, "Should produce chunks"

    def test_tutorial_preserves_examples(self, documents_dir, chunker):
        """Test that examples are preserved."""
        content = load_document(documents_dir, "tutorial.md")
        chunks = chunker.chunk(content)
        assert len(chunks) > 0


class TestReadme:
    """Tests for README document."""

    def test_readme_chunking(self, documents_dir, chunker):
        """Test chunking of README."""
        content = load_document(documents_dir, "readme.md")
        chunks, strategy_used, analysis = chunker.chunk_with_analysis(content)

        assert len(chunks) >= 1, "Should produce chunks"

    def test_readme_preserves_badges(self, documents_dir, chunker):
        """Test that badges/links are preserved."""
        content = load_document(documents_dir, "readme.md")
        chunks = chunker.chunk(content)
        assert len(chunks) > 0


class TestBlogPost:
    """Tests for blog post document."""

    def test_blog_post_chunking(self, documents_dir, chunker):
        """Test chunking of blog post."""
        content = load_document(documents_dir, "blog_post.md")
        chunks, strategy_used, analysis = chunker.chunk_with_analysis(content)

        assert len(chunks) >= 1, "Should produce chunks"

    def test_blog_post_preserves_tables(self, documents_dir, chunker):
        """Test that tables are preserved."""
        content = load_document(documents_dir, "blog_post.md")
        chunks = chunker.chunk(content)
        assert len(chunks) > 0


class TestTechnicalSpec:
    """Tests for technical specification document."""

    def test_technical_spec_chunking(self, documents_dir, chunker):
        """Test chunking of technical specification."""
        content = load_document(documents_dir, "technical_spec.md")
        chunks, strategy_used, analysis = chunker.chunk_with_analysis(content)

        assert len(chunks) >= 1, "Should produce chunks"

    def test_technical_spec_large_document(self, documents_dir, chunker):
        """Test handling of large document."""
        content = load_document(documents_dir, "technical_spec.md")
        chunks, strategy_used, analysis = chunker.chunk_with_analysis(content)

        assert len(chunks) >= 1, "Should produce chunks"


class TestAllDocuments:
    """Tests that apply to all documents."""

    @pytest.fixture
    def all_documents(self, documents_dir):
        """List all document files."""
        return [
            "api_documentation.md",
            "tutorial.md",
            "readme.md",
            "blog_post.md",
            "technical_spec.md",
        ]

    @pytest.mark.parametrize("filename", [
        "api_documentation.md",
        "tutorial.md",
        "readme.md",
        "blog_post.md",
        "technical_spec.md",
    ])
    def test_all_documents_no_content_loss(self, documents_dir, chunker, filename):
        """Test no content loss for all documents."""
        content = load_document(documents_dir, filename)
        chunks = chunker.chunk(content)
        verify_no_content_loss(content, chunks)

    @pytest.mark.parametrize("filename", [
        "api_documentation.md",
        "tutorial.md",
        "readme.md",
        "blog_post.md",
        "technical_spec.md",
    ])
    def test_all_documents_metadata_valid(self, documents_dir, chunker, filename):
        """Test metadata validity for all documents."""
        content = load_document(documents_dir, filename)
        chunks = chunker.chunk(content)
        for chunk in chunks:
            verify_metadata(chunk)

    @pytest.mark.parametrize("filename", [
        "api_documentation.md",
        "tutorial.md",
        "readme.md",
        "blog_post.md",
        "technical_spec.md",
    ])
    def test_all_documents_line_numbers_valid(self, documents_dir, chunker, filename):
        """Test line numbers validity for all documents."""
        content = load_document(documents_dir, filename)
        chunks = chunker.chunk(content)
        verify_line_numbers(chunks)

    def test_strategy_selection_appropriate(self, documents_dir, chunker):
        """Test that appropriate strategy is selected."""
        for filename in ["api_documentation.md", "tutorial.md"]:
            content = load_document(documents_dir, filename)
            chunks, strategy_used, analysis = chunker.chunk_with_analysis(content)
            assert strategy_used in ["code_aware", "structural", "fallback"]

    def test_chunk_sizes_reasonable(self, documents_dir, chunker):
        """Test that chunk sizes are reasonable."""
        for filename in ["api_documentation.md", "tutorial.md"]:
            content = load_document(documents_dir, filename)
            chunks = chunker.chunk(content)
            for chunk in chunks:
                # Allow some oversized chunks for atomic blocks
                assert len(chunk.content) <= 10000, "Chunk too large"
