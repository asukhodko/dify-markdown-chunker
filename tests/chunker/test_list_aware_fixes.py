"""
Tests for list_aware strategy bug fixes.

Tests cover:
1. LISTAWARE-1: No list duplication within single chunk
2. LISTAWARE-2: header_path properly populated
"""

from markdown_chunker_v2.chunker import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig


class TestListAwareDuplicationFix:
    """Tests for LISTAWARE-1: List duplication bug fix."""

    def test_no_list_duplication_with_introduction(self):
        """Test that lists are not duplicated when bound with introduction paragraph."""
        md_text = """## Technical Complexity

Что я сделал:

- Исследовал все алгоритмы консенсуса
- Доработал алгоритм консенсуса Raft
- Проверил корректность алгоритма с помощью TLA+
- Разработал MVP
- Реализовал в виде библиотеки код
"""

        config = ChunkConfig(max_chunk_size=4096, strategy_override="list_aware")
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Should create 1-2 chunks depending on size
        assert len(chunks) >= 1

        # Check each chunk for duplication
        for chunk in chunks:
            content = chunk.content
            lines = content.split("\n")

            # Count occurrences of each line
            line_counts = {}
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("-") and len(stripped) > 5:
                    line_counts[stripped] = line_counts.get(stripped, 0) + 1

            # No line should appear more than once
            for line, count in line_counts.items():
                assert count == 1, (
                    f"List item appears {count} times in chunk: {line}\n"
                    f"Chunk content:\n{content}"
                )

    def test_no_duplication_simple_list(self):
        """Test simple list without introduction doesn't duplicate."""
        md_text = """# Features

- Feature A
- Feature B
- Feature C
"""

        config = ChunkConfig(strategy_override="list_aware")
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Combine all chunk content
        all_content = "\n".join(c.content for c in chunks)

        # Count each feature
        assert all_content.count("- Feature A") == 1
        assert all_content.count("- Feature B") == 1
        assert all_content.count("- Feature C") == 1

    def test_no_duplication_with_nested_lists(self):
        """Test nested lists are not duplicated."""
        md_text = """# Tasks

Что сделать:

- Parent task 1
  - Subtask 1.1
  - Subtask 1.2
- Parent task 2
  - Subtask 2.1
"""

        config = ChunkConfig(strategy_override="list_aware")
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        all_content = "\n".join(c.content for c in chunks)

        # Each task should appear exactly once
        assert all_content.count("Parent task 1") == 1
        assert all_content.count("Subtask 1.1") == 1
        assert all_content.count("Subtask 1.2") == 1
        assert all_content.count("Parent task 2") == 1
        assert all_content.count("Subtask 2.1") == 1


class TestListAwareHeaderPath:
    """Tests for LISTAWARE-2: header_path population."""

    def test_header_path_simple_hierarchy(self):
        """Test header_path is populated for simple hierarchy."""
        md_text = """# Main Title

## Section 1

Some text.

- Item 1
- Item 2
- Item 3

## Section 2

- Item A
- Item B
"""

        config = ChunkConfig(strategy_override="list_aware")
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Find chunks with lists
        list_chunks = [c for c in chunks if "Item" in c.content]
        assert len(list_chunks) >= 2

        # First list chunk should have header_path ending with Section 1
        first_list_chunk = list_chunks[0]
        assert "header_path" in first_list_chunk.metadata
        header_path = first_list_chunk.metadata["header_path"]
        assert isinstance(header_path, str)
        assert "Main Title" in header_path
        assert "Section 1" in header_path

        # Second list chunk should have header_path ending with Section 2
        if len(list_chunks) > 1:
            second_list_chunk = list_chunks[1]
            header_path = second_list_chunk.metadata["header_path"]
            assert "Section 2" in header_path

    def test_header_path_deep_hierarchy(self):
        """Test header_path with deeper nesting when lists appear after headers."""
        # Test with lists that DON'T have introduction binding
        # so they stay on their original lines with headers
        md_text = """# Критерии грейдов DEV

## DEV-4 (Junior II)

### Impact (Delivery)

- Complete assigned tasks
- Write unit tests
- Document code

### Technical Complexity

- Work on simple features
- Debug issues
"""

        config = ChunkConfig(strategy_override="list_aware", min_chunk_size=1)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Find chunks with lists
        list_chunks = [
            c for c in chunks if "-" in c.content and "Item" not in c.content
        ]

        # At least one list chunk should have header_path populated
        found_valid_path = False
        for chunk in list_chunks:
            header_path = chunk.metadata.get("header_path", "")
            if header_path and isinstance(header_path, str) and len(header_path) > 0:
                found_valid_path = True
                # Should contain at least top-level header
                assert "Критерии" in header_path or "DEV" in header_path
                break

        # At minimum, verify header_path field exists and is string type
        assert all(
            isinstance(c.metadata.get("header_path", ""), str) for c in chunks
        ), "All chunks should have header_path as string"
        # Verify at least one chunk has a populated header_path
        assert found_valid_path, "At least one list chunk should have populated header_path"

    def test_header_path_consistency_with_structural(self):
        """Test that header_path format matches structural strategy."""
        md_text = """# Title

## Subtitle

- List item 1
- List item 2
"""

        # Use list_aware strategy
        config_list = ChunkConfig(strategy_override="list_aware")
        chunker_list = MarkdownChunker(config_list)
        list_chunks = chunker_list.chunk(md_text)

        # Use structural strategy
        config_struct = ChunkConfig(strategy_override="structural")
        chunker_struct = MarkdownChunker(config_struct)
        struct_chunks = chunker_struct.chunk(md_text)

        # Both should have header_path
        list_chunk_with_list = [c for c in list_chunks if "List item" in c.content][0]
        struct_chunk_with_list = [c for c in struct_chunks if "List item" in c.content][
            0
        ]

        list_path = list_chunk_with_list.metadata.get("header_path", "")
        struct_path = struct_chunk_with_list.metadata.get("header_path")

        # Format should be consistent (string with / separators)
        assert isinstance(list_path, str)
        assert isinstance(struct_path, str)

        # Both should have similar structure
        assert list_path.startswith("/")
        assert "Title" in list_path
        assert "Subtitle" in list_path

    def test_header_level_metadata(self):
        """Test that header_level metadata is set correctly."""
        md_text = """# Level 1

## Level 2

### Level 3

- List under level 3
- Another item
"""

        config = ChunkConfig(strategy_override="list_aware")
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        list_chunk = [c for c in chunks if "List under level 3" in c.content][0]

        # Should have header_level = 3 (deepest header in path)
        assert "header_level" in list_chunk.metadata
        assert list_chunk.metadata["header_level"] == 3

    def test_empty_header_path_when_no_headers(self):
        """Test header_path is empty string when document has no headers."""
        md_text = """Just a simple list:

- Item 1
- Item 2
- Item 3
"""

        config = ChunkConfig(strategy_override="list_aware")
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        list_chunk = [c for c in chunks if "Item" in c.content][0]

        # Should have empty header_path
        header_path = list_chunk.metadata.get("header_path", None)
        assert header_path == ""
        assert list_chunk.metadata.get("header_level", -1) == 0
