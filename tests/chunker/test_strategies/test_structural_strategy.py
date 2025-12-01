"""
Tests for StructuralStrategy.

This module tests the header-based chunking strategy that creates
chunks based on document structure and header hierarchy.
"""

from unittest.mock import Mock

from markdown_chunker.chunker.strategies.structural_strategy import (
    HeaderInfo,
    Section,
    StructuralStrategy,
)
from markdown_chunker.chunker.types import ChunkConfig
from markdown_chunker.parser.types import (
    ContentAnalysis,
    ElementCollection,
    Stage1Results,
)


class TestStructuralStrategy:
    """Test cases for StructuralStrategy."""

    def test_strategy_properties(self):
        """Test basic strategy properties."""
        strategy = StructuralStrategy()

        assert strategy.name == "structural"
        assert strategy.priority == 2  # High priority per Requirement 6.5

    def test_can_handle_sufficient_headers(self):
        """Test can_handle with sufficient headers and hierarchy."""
        strategy = StructuralStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.header_count = {1: 2, 2: 3}  # P1-005: Now Dict[int, int]
        analysis.get_total_header_count.return_value = 5
        analysis.max_header_depth = 3

        config = ChunkConfig(header_count_threshold=3)

        assert strategy.can_handle(analysis, config) is True

    def test_can_handle_insufficient_headers(self):
        """Test can_handle with insufficient headers."""
        strategy = StructuralStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.header_count = {1: 2}  # P1-005: Now Dict[int, int]
        analysis.get_total_header_count.return_value = 2
        analysis.max_header_depth = 3

        config = ChunkConfig(header_count_threshold=3)

        assert strategy.can_handle(analysis, config) is False

    def test_can_handle_no_hierarchy(self):
        """Test can_handle with no header hierarchy."""
        strategy = StructuralStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.header_count = {1: 5}  # P1-005: Now Dict[int, int]
        analysis.get_total_header_count.return_value = 5
        analysis.max_header_depth = 1  # No hierarchy

        config = ChunkConfig(header_count_threshold=3)

        assert strategy.can_handle(analysis, config) is False

    def test_calculate_quality_high_structure(self):
        """Test quality calculation for highly structured content."""
        strategy = StructuralStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.header_count = {1: 3, 2: 5, 3: 4}  # P1-005: Now Dict[int, int]
        analysis.get_total_header_count.return_value = 12
        analysis.max_header_depth = 4
        analysis.code_ratio = 0.2
        analysis.has_hierarchy = True

        quality = strategy.calculate_quality(analysis)

        # Should be high quality for structured content
        assert quality > 0.8

    def test_calculate_quality_code_heavy(self):
        """Test quality calculation for code-heavy content."""
        strategy = StructuralStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.header_count = {1: 3, 2: 5}  # P1-005: Now Dict[int, int]
        analysis.get_total_header_count.return_value = 8
        analysis.max_header_depth = 3
        analysis.code_ratio = 0.7  # High code ratio
        analysis.has_hierarchy = True

        quality = strategy.calculate_quality(analysis)

        # Should be lower quality due to high code ratio
        assert quality < 0.6

    def test_detect_headers_manual_atx(self):
        """Test manual header detection with ATX headers."""
        strategy = StructuralStrategy()

        content = """# Main Title

## Section 1

Some content here.

### Subsection 1.1

More content.

## Section 2

Final content."""

        headers = strategy._detect_headers_manual(content)

        assert len(headers) == 4
        assert headers[0].level == 1
        assert headers[0].text == "Main Title"
        assert headers[1].level == 2
        assert headers[1].text == "Section 1"
        assert headers[2].level == 3
        assert headers[2].text == "Subsection 1.1"
        assert headers[3].level == 2
        assert headers[3].text == "Section 2"

    def test_detect_headers_manual_setext(self):
        """Test manual header detection with Setext headers."""
        strategy = StructuralStrategy()

        content = """Main Title
==========

Section 1
---------

Some content here."""

        headers = strategy._detect_headers_manual(content)

        assert len(headers) == 2
        assert headers[0].level == 1
        assert headers[0].text == "Main Title"
        assert headers[1].level == 2
        assert headers[1].text == "Section 1"

    def test_build_hierarchy_simple(self):
        """Test building header hierarchy with simple structure."""
        strategy = StructuralStrategy()

        headers = [
            HeaderInfo(level=1, text="Main", line=1, position=0),
            HeaderInfo(level=2, text="Sub1", line=3, position=20),
            HeaderInfo(level=2, text="Sub2", line=5, position=40),
            HeaderInfo(level=3, text="SubSub", line=7, position=60),
        ]

        root_headers = strategy._build_hierarchy(headers)

        assert len(root_headers) == 1
        assert root_headers[0].text == "Main"
        assert len(root_headers[0].children) == 2
        assert root_headers[0].children[0].text == "Sub1"
        assert root_headers[0].children[1].text == "Sub2"
        assert len(root_headers[0].children[1].children) == 1
        assert root_headers[0].children[1].children[0].text == "SubSub"

    def test_build_hierarchy_multiple_roots(self):
        """Test building hierarchy with multiple root headers."""
        strategy = StructuralStrategy()

        headers = [
            HeaderInfo(level=1, text="Root1", line=1, position=0),
            HeaderInfo(level=2, text="Sub1", line=3, position=20),
            HeaderInfo(level=1, text="Root2", line=5, position=40),
            HeaderInfo(level=2, text="Sub2", line=7, position=60),
        ]

        root_headers = strategy._build_hierarchy(headers)

        assert len(root_headers) == 2
        assert root_headers[0].text == "Root1"
        assert root_headers[1].text == "Root2"
        assert len(root_headers[0].children) == 1
        assert len(root_headers[1].children) == 1

    def test_build_header_path_simple(self):
        """Test building header path for simple hierarchy."""
        strategy = StructuralStrategy()

        root = HeaderInfo(level=1, text="Documentation", line=1, position=0)
        child = HeaderInfo(
            level=2, text="Getting Started", line=3, position=20, parent=root
        )
        grandchild = HeaderInfo(
            level=3, text="Installation", line=5, position=40, parent=child
        )

        path = strategy._build_header_path(grandchild)

        assert path == "/Documentation/Getting Started/Installation"

    def test_build_header_path_root(self):
        """Test building header path for root header."""
        strategy = StructuralStrategy()

        root = HeaderInfo(level=1, text="Main Title", line=1, position=0)
        path = strategy._build_header_path(root)

        assert path == "/Main Title"

    def test_create_sections(self):
        """Test creating sections from headers."""
        strategy = StructuralStrategy()

        content = """# Main Title

Introduction text.

## Section 1

Section 1 content.

## Section 2

Section 2 content."""

        headers = [
            HeaderInfo(level=1, text="Main Title", line=1, position=0),
            HeaderInfo(level=2, text="Section 1", line=5, position=35),
            HeaderInfo(level=2, text="Section 2", line=9, position=70),
        ]

        sections = strategy._create_sections(content, headers)

        assert len(sections) == 3
        assert "Main Title" in sections[0].content
        assert "Introduction text" in sections[0].content
        assert "Section 1 content" in sections[1].content
        assert "Section 2 content" in sections[2].content

    def test_apply_empty_content(self):
        """Test applying strategy to empty content."""
        strategy = StructuralStrategy()
        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig.default()

        chunks = strategy.apply("", stage1_results, config)

        assert chunks == []

    def test_apply_no_headers(self):
        """Test applying strategy to content without headers."""
        strategy = StructuralStrategy()

        # Mock Stage 1 results with no headers
        elements = Mock(spec=ElementCollection)
        elements.headers = []

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.elements = elements

        config = ChunkConfig.default()
        content = "Just some plain text without any headers."

        chunks = strategy.apply(content, stage1_results, config)

        assert chunks == []

    def test_apply_simple_structure(self):
        """Test applying strategy to simple structured content."""
        strategy = StructuralStrategy()

        # Mock Stage 1 results with headers
        headers = [
            Mock(level=1, text="Main Title", line=1, offset=0),
            Mock(level=2, text="Section 1", line=4, offset=30),
            Mock(level=2, text="Section 2", line=7, offset=60),
        ]

        elements = Mock(spec=ElementCollection)
        elements.headers = headers

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.elements = elements

        config = ChunkConfig.default()
        content = """# Main Title

Introduction content.

## Section 1

Section 1 content here.

## Section 2

Section 2 content here."""

        chunks = strategy.apply(content, stage1_results, config)

        assert len(chunks) >= 1  # Should create at least one chunk

        # Check that chunks have structural metadata
        for chunk in chunks:
            assert "header_level" in chunk.metadata
            assert "header_text" in chunk.metadata
            assert "header_path" in chunk.metadata

    def test_apply_large_section_splitting(self):
        """Test that large sections are split appropriately."""
        strategy = StructuralStrategy()

        # Create content with a very large section
        large_content = "This is a very long section. " * 200  # ~6000 characters

        headers = [Mock(level=1, text="Large Section", line=1, offset=0)]

        elements = Mock(spec=ElementCollection)
        elements.headers = headers

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.elements = elements

        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=200)
        content = f"# Large Section\n\n{large_content}"

        chunks = strategy.apply(content, stage1_results, config)

        # Should create multiple chunks due to size limit
        assert len(chunks) > 1

        # Most chunks should be within size limits
        oversized_chunks = [c for c in chunks if c.size > config.max_chunk_size]
        assert len(oversized_chunks) <= 1  # At most one oversized chunk allowed

    def test_combine_small_chunks(self):
        """Test combining small chunks to meet minimum size."""
        strategy = StructuralStrategy()

        # Create small chunks
        small_chunks = [
            strategy._create_chunk(
                "Small content 1", 1, 1, "text", header_text="Header 1"
            ),
            strategy._create_chunk(
                "Small content 2", 2, 2, "text", header_text="Header 2"
            ),
            strategy._create_chunk(
                "Small content 3", 3, 3, "text", header_text="Header 3"
            ),
        ]

        config = ChunkConfig(min_chunk_size=50, max_chunk_size=200)

        combined = strategy._combine_small_chunks(small_chunks, config)

        # Should combine small chunks
        assert len(combined) < len(small_chunks)

        # Combined chunks should meet minimum size or be the last chunk
        for i, chunk in enumerate(combined[:-1]):  # All but last
            assert (
                chunk.size >= config.min_chunk_size
                or "combined_sections" in chunk.metadata
            )

    def test_get_selection_reason(self):
        """Test selection reason generation."""
        strategy = StructuralStrategy()

        # Can handle
        analysis = Mock(spec=ContentAnalysis)
        analysis.header_count = 5
        analysis.max_header_depth = 3

        reason = strategy._get_selection_reason(analysis, True)
        assert "5 headers" in reason
        assert "3 levels" in reason

        # Cannot handle - too few headers
        analysis.header_count = 2
        reason = strategy._get_selection_reason(analysis, False)
        assert "Too few headers" in reason

        # Cannot handle - no hierarchy
        analysis.header_count = 5
        analysis.max_header_depth = 1
        reason = strategy._get_selection_reason(analysis, False)
        assert "No header hierarchy" in reason


class TestHeaderInfo:
    """Test cases for HeaderInfo data structure."""

    def test_header_info_creation(self):
        """Test creating HeaderInfo."""
        header = HeaderInfo(level=2, text="Test Header", line=5, position=100)

        assert header.level == 2
        assert header.text == "Test Header"
        assert header.line == 5
        assert header.position == 100
        assert header.parent is None
        assert header.children == []

    def test_header_info_with_parent(self):
        """Test HeaderInfo with parent relationship."""
        parent = HeaderInfo(level=1, text="Parent", line=1, position=0)
        child = HeaderInfo(level=2, text="Child", line=3, position=20, parent=parent)

        # Manually add child to parent (this would be done by build_hierarchy)
        parent.children.append(child)

        assert child.parent is parent
        assert child in parent.children


class TestSection:
    """Test cases for Section data structure."""

    def test_section_creation(self):
        """Test creating Section."""
        header = HeaderInfo(level=2, text="Test Section", line=5, position=100)

        section = Section(
            header=header,
            content="Section content here",
            start_line=5,
            end_line=7,
            size=20,
        )

        assert section.header is header
        assert section.content == "Section content here"
        assert section.start_line == 5
        assert section.end_line == 7
        assert section.size == 20
        assert section.has_subsections is False
        assert section.subsections == []


class TestStructuralStrategyIntegration:
    """Integration tests for StructuralStrategy."""

    def test_realistic_documentation_chunking(self):
        """Test chunking realistic documentation structure."""
        strategy = StructuralStrategy()

        content = """# API Documentation

This is the main API documentation.

## Authentication

You need an API key to access the API.

### Getting an API Key

Visit the developer portal to get your key.

### Using the API Key

Include it in the Authorization header.

## Endpoints

The API provides several endpoints.

### Users

Manage user accounts.

#### GET /users

List all users.

#### POST /users

Create a new user.

### Products

Manage products.

#### GET /products

List all products."""

        # Mock Stage 1 results
        headers = [
            Mock(level=1, text="API Documentation", line=1, offset=0),
            Mock(level=2, text="Authentication", line=5, offset=50),
            Mock(level=3, text="Getting an API Key", line=9, offset=100),
            Mock(level=3, text="Using the API Key", line=13, offset=150),
            Mock(level=2, text="Endpoints", line=17, offset=200),
            Mock(level=3, text="Users", line=21, offset=250),
            Mock(level=4, text="GET /users", line=25, offset=300),
            Mock(level=4, text="POST /users", line=29, offset=350),
            Mock(level=3, text="Products", line=33, offset=400),
            Mock(level=4, text="GET /products", line=37, offset=450),
        ]

        elements = Mock(spec=ElementCollection)
        elements.headers = headers

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.elements = elements

        config = ChunkConfig(max_chunk_size=500, min_chunk_size=100)

        chunks = strategy.apply(content, stage1_results, config)

        # Should create multiple chunks
        assert len(chunks) > 1

        # All chunks should have structural metadata
        for chunk in chunks:
            assert chunk.metadata["strategy"] == "structural"
            assert "header_level" in chunk.metadata
            assert "header_text" in chunk.metadata
            assert "header_path" in chunk.metadata

        # Check that hierarchy is preserved in paths
        paths = [chunk.metadata["header_path"] for chunk in chunks]

        # Should have hierarchical paths
        assert any("/API Documentation" in path for path in paths)
        assert any("/Authentication" in path for path in paths)
        assert any("/Getting an API Key" in path for path in paths)

    def test_fallback_to_manual_detection(self):
        """Test fallback to manual header detection when Stage 1 fails."""
        strategy = StructuralStrategy()

        # Mock Stage 1 results with no headers
        elements = Mock(spec=ElementCollection)
        elements.headers = []

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.elements = elements

        content = """# Manual Detection Test

## Section 1

Content for section 1.

## Section 2

Content for section 2."""

        config = ChunkConfig.default()

        chunks = strategy.apply(content, stage1_results, config)

        # Should still work with manual detection
        assert len(chunks) >= 1

        # Should have detected headers manually
        for chunk in chunks:
            assert "header_level" in chunk.metadata
            assert "header_text" in chunk.metadata
