"""Unit tests for BlockPacker.

Tests block extraction, URL pool detection, and packing algorithm.
"""

from markdown_chunker.chunker.block_packer import Block, BlockPacker, BlockType
from markdown_chunker.chunker.types import ChunkConfig


class TestBlockExtraction:
    """Test block extraction from content."""

    def setup_method(self):
        """Set up test fixtures."""
        self.packer = BlockPacker()

    def test_extract_code_block(self):
        """Test code block extraction."""
        content = """# Header

```python
def hello():
    print("world")
```

More text."""

        blocks = self.packer.extract_blocks(content)

        # Should have header, code, and paragraph blocks
        code_blocks = [b for b in blocks if b.type == BlockType.CODE]
        assert len(code_blocks) == 1
        assert "def hello" in code_blocks[0].content
        assert code_blocks[0].metadata.get("language") == "python"

    def test_extract_table(self):
        """Test table block extraction."""
        content = """# Header

| Col1 | Col2 |
|------|------|
| A    | B    |
| C    | D    |

More text."""

        blocks = self.packer.extract_blocks(content)

        table_blocks = [b for b in blocks if b.type == BlockType.TABLE]
        assert len(table_blocks) == 1
        assert "| Col1 | Col2 |" in table_blocks[0].content
        assert "| A    | B    |" in table_blocks[0].content

    def test_extract_list(self):
        """Test list block extraction."""
        content = """# Header

- Item 1
- Item 2
- Item 3

More text."""

        blocks = self.packer.extract_blocks(content)

        list_blocks = [b for b in blocks if b.type == BlockType.LIST]
        assert len(list_blocks) == 1
        assert "Item 1" in list_blocks[0].content
        assert "Item 2" in list_blocks[0].content
        assert "Item 3" in list_blocks[0].content

    def test_extract_header(self):
        """Test header block extraction."""
        content = """# Main Header

## Subsection

### Sub-subsection"""

        blocks = self.packer.extract_blocks(content)

        header_blocks = [b for b in blocks if b.type == BlockType.HEADER]
        assert len(header_blocks) == 3
        assert header_blocks[0].metadata["level"] == 1
        assert header_blocks[1].metadata["level"] == 2
        assert header_blocks[2].metadata["level"] == 3

    def test_extract_paragraphs(self):
        """Test paragraph extraction."""
        content = """# Header

This is paragraph 1.

This is paragraph 2.

This is paragraph 3."""

        blocks = self.packer.extract_blocks(content)

        para_blocks = [b for b in blocks if b.type == BlockType.PARAGRAPH]
        assert len(para_blocks) == 3
        assert "paragraph 1" in para_blocks[0].content
        assert "paragraph 2" in para_blocks[1].content
        assert "paragraph 3" in para_blocks[2].content


class TestURLPoolDetection:
    """Test URL pool detection (MC-005)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.packer = BlockPacker()

    def test_detect_url_pool(self):
        """Test detection of URL pool (3+ consecutive URLs)."""
        content = """# Links

Link 1: https://example.com/one
Link 2: https://example.com/two
Link 3: https://example.com/three

Regular paragraph."""

        blocks = self.packer.extract_blocks(content)

        url_pool_blocks = [b for b in blocks if b.type == BlockType.URL_POOL]
        assert len(url_pool_blocks) == 1
        assert "https://example.com/one" in url_pool_blocks[0].content
        assert "https://example.com/two" in url_pool_blocks[0].content
        assert "https://example.com/three" in url_pool_blocks[0].content

    def test_no_url_pool_for_two_urls(self):
        """Test that 2 URLs don't create a pool."""
        content = """# Links

Link 1: https://example.com/one
Link 2: https://example.com/two

Regular paragraph."""

        blocks = self.packer.extract_blocks(content)

        url_pool_blocks = [b for b in blocks if b.type == BlockType.URL_POOL]
        assert len(url_pool_blocks) == 0

    def test_url_pool_with_blank_lines(self):
        """Test URL pool detection with blank lines between URLs."""
        content = """Link 1: https://example.com/one

Link 2: https://example.com/two

Link 3: https://example.com/three

Regular paragraph."""

        blocks = self.packer.extract_blocks(content)

        url_pool_blocks = [b for b in blocks if b.type == BlockType.URL_POOL]
        # Should detect pool despite blank lines
        assert len(url_pool_blocks) >= 1


class TestBlockPacking:
    """Test packing blocks into chunks."""

    def setup_method(self):
        """Set up test fixtures."""
        self.packer = BlockPacker()
        self.config = ChunkConfig(max_chunk_size=200)

    def test_pack_small_blocks(self):
        """Test packing small blocks into single chunk."""
        blocks = [
            Block(
                type=BlockType.HEADER,
                content="# Header",
                start_line=1,
                end_line=1,
                size=8,
                metadata={},
            ),
            Block(
                type=BlockType.PARAGRAPH,
                content="Short paragraph.",
                start_line=3,
                end_line=3,
                size=16,
                metadata={},
            ),
        ]

        chunks = self.packer.pack_blocks_into_chunks(blocks, self.config)

        assert len(chunks) == 1
        assert "# Header" in chunks[0].content
        assert "Short paragraph" in chunks[0].content

    def test_pack_large_blocks_splits(self):
        """Test that large blocks cause splits."""
        blocks = [
            Block(
                type=BlockType.PARAGRAPH,
                content="A" * 150,  # 150 chars
                start_line=1,
                end_line=1,
                size=150,
                metadata={},
            ),
            Block(
                type=BlockType.PARAGRAPH,
                content="B" * 100,  # 100 chars
                start_line=3,
                end_line=3,
                size=100,
                metadata={},
            ),
        ]

        chunks = self.packer.pack_blocks_into_chunks(blocks, self.config)

        # Should create 2 chunks (combined 250 > 200 limit)
        assert len(chunks) == 2

    def test_pack_with_section_header(self):
        """Test packing with section header prepended."""
        blocks = [
            Block(
                type=BlockType.PARAGRAPH,
                content="Content here.",
                start_line=1,
                end_line=1,
                size=13,
                metadata={},
            )
        ]

        chunks = self.packer.pack_blocks_into_chunks(
            blocks, self.config, section_header="## Section"
        )

        assert len(chunks) == 1
        assert "## Section" in chunks[0].content
        assert "Content here" in chunks[0].content

    def test_preserves_block_boundaries(self):
        """Test that blocks are never split (MC-002)."""
        # Create a large block that exceeds max_chunk_size
        large_block = Block(
            type=BlockType.CODE,
            content="```python\n" + ("x = 1\n" * 50) + "```",
            start_line=1,
            end_line=52,
            size=300,  # Exceeds 200 limit
            metadata={},
        )

        chunks = self.packer.pack_blocks_into_chunks([large_block], self.config)

        # Should create 1 chunk with oversized content rather than split block
        assert len(chunks) == 1
        assert "```python" in chunks[0].content
        assert "```" in chunks[0].content.strip()[-10:]  # Ends with closing fence

    def test_metadata_preserved(self):
        """Test that block metadata is preserved in chunks."""
        blocks = [
            Block(
                type=BlockType.CODE,
                content="```python\ncode\n```",
                start_line=1,
                end_line=3,
                size=20,
                metadata={"language": "python"},
            )
        ]

        chunks = self.packer.pack_blocks_into_chunks(blocks, self.config)

        assert len(chunks) == 1
        assert "block_types" in chunks[0].metadata
        assert "code" in chunks[0].metadata["block_types"]


class TestBlockBoundaries:
    """Test that blocks respect structural boundaries."""

    def setup_method(self):
        """Set up test fixtures."""
        self.packer = BlockPacker()

    def test_list_not_split(self):
        """Test that lists are extracted as complete blocks."""
        content = """- Item 1
- Item 2
- Item 3
- Item 4
- Item 5"""

        blocks = self.packer.extract_blocks(content)

        list_blocks = [b for b in blocks if b.type == BlockType.LIST]
        assert len(list_blocks) == 1

        # All items in single block
        assert "Item 1" in list_blocks[0].content
        assert "Item 5" in list_blocks[0].content

    def test_table_not_split(self):
        """Test that tables are extracted as complete blocks."""
        content = """| A | B |
|---|---|
| 1 | 2 |
| 3 | 4 |
| 5 | 6 |"""

        blocks = self.packer.extract_blocks(content)

        table_blocks = [b for b in blocks if b.type == BlockType.TABLE]
        assert len(table_blocks) == 1

        # All rows in single block
        assert "| 1 | 2 |" in table_blocks[0].content
        assert "| 5 | 6 |" in table_blocks[0].content

    def test_code_block_not_split(self):
        """Test that code blocks are extracted as complete blocks."""
        content = """```python
def func1():
    pass

def func2():
    pass
```"""

        blocks = self.packer.extract_blocks(content)

        code_blocks = [b for b in blocks if b.type == BlockType.CODE]
        assert len(code_blocks) == 1

        # Both functions in single block
        assert "func1" in code_blocks[0].content
        assert "func2" in code_blocks[0].content
