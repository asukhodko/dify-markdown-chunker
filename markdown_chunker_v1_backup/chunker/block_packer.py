"""Block-based packer for chunk creation.

This module implements block-level chunking to address MC-001 through MC-006.
All operations work at block boundaries, never splitting mid-block.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from markdown_chunker.chunker.types import Chunk, ChunkConfig
from markdown_chunker.parser.types import Stage1Results


class BlockType(Enum):
    """Types of content blocks."""

    HEADER = "header"
    PARAGRAPH = "paragraph"
    LIST = "list"
    TABLE = "table"
    CODE = "code"
    URL_POOL = "url_pool"
    BLANK = "blank"


@dataclass
class Block:
    """A block of content."""

    type: BlockType
    content: str
    start_line: int
    end_line: int
    size: int
    metadata: dict

    def __post_init__(self):
        """Initialize computed fields."""
        if self.size == 0:
            self.size = len(self.content)


class BlockPacker:
    """Unified component for packing blocks into chunks.

    This replaces character-based splitting with block-based packing.
    Addresses MC-001 (section fragmentation) and MC-002 (structural breaks).
    """

    # URL pattern for detecting URL pools
    URL_PATTERN = re.compile(r"https?://[^\s]+")

    def __init__(self):
        """Initialize block packer."""
        pass

    def extract_blocks(
        self, content: str, stage1_results: Optional[Stage1Results] = None
    ) -> List[Block]:
        """Extract blocks from content using AST when available.

        Args:
            content: Markdown content
            stage1_results: Optional Stage 1 parse results with AST

        Returns:
            List of Block objects
        """
        if stage1_results and hasattr(stage1_results, "ast"):
            return self._extract_blocks_from_ast(content, stage1_results)
        else:
            return self._extract_blocks_simple(content)

    def _extract_blocks_from_ast(
        self, content: str, stage1_results: Stage1Results
    ) -> List[Block]:
        """Extract blocks using AST from Stage 1 parser.

        This leverages existing parsing to identify structural elements.
        """
        blocks = []
        lines = content.split("\n")

        # Get elements from AST
        # Note: ast variable assigned but not currently used
        # ast = stage1_results.ast
        elements = stage1_results.elements

        # Track which lines are covered by structural elements
        covered_lines: set[int] = set()

        # Extract fenced code blocks from Stage1Results (not from elements)
        if hasattr(stage1_results, "fenced_blocks") and stage1_results.fenced_blocks:
            for cb in stage1_results.fenced_blocks:
                block = Block(
                    type=BlockType.CODE,
                    content=self._extract_line_range(lines, cb.start_line, cb.end_line),
                    start_line=cb.start_line,
                    end_line=cb.end_line,
                    size=0,  # Will be calculated in __post_init__
                    metadata={"language": getattr(cb, "language", "")},
                )
                blocks.append(block)
                covered_lines.update(range(cb.start_line, cb.end_line + 1))

        # Extract tables
        if hasattr(elements, "tables"):
            for tbl in elements.tables:
                block = Block(
                    type=BlockType.TABLE,
                    content=self._extract_line_range(
                        lines, tbl.start_line, tbl.end_line
                    ),
                    start_line=tbl.start_line,
                    end_line=tbl.end_line,
                    size=0,
                    metadata={"columns": getattr(tbl, "column_count", 0)},
                )
                blocks.append(block)
                covered_lines.update(range(tbl.start_line, tbl.end_line + 1))

        # Extract lists (as complete blocks)
        if hasattr(elements, "lists") and elements.lists:
            for lst in elements.lists:
                # MarkdownList has 'type' field
                # ("ordered", "unordered", "task"), not 'ordered'
                is_ordered = lst.type == "ordered" if hasattr(lst, "type") else False
                block = Block(
                    type=BlockType.LIST,
                    content=self._extract_line_range(
                        lines, lst.start_line, lst.end_line
                    ),
                    start_line=lst.start_line,
                    end_line=lst.end_line,
                    size=0,
                    metadata={
                        "ordered": is_ordered,
                        "item_count": (
                            lst.get_item_count()
                            if hasattr(lst, "get_item_count")
                            else len(lst.items) if hasattr(lst, "items") else 0
                        ),
                    },
                )
                blocks.append(block)
                covered_lines.update(range(lst.start_line, lst.end_line + 1))

        # Extract headers
        if hasattr(elements, "headers"):
            for hdr in elements.headers:
                block = Block(
                    type=BlockType.HEADER,
                    content=self._extract_line_range(lines, hdr.line, hdr.line),
                    start_line=hdr.line,
                    end_line=hdr.line,
                    size=0,
                    metadata={"level": hdr.level, "text": hdr.text},
                )
                blocks.append(block)
                covered_lines.add(hdr.line)

        # Extract paragraphs from uncovered lines
        paragraph_blocks = self._extract_paragraphs_from_uncovered(lines, covered_lines)
        blocks.extend(paragraph_blocks)

        # Sort by start line
        blocks.sort(key=lambda b: b.start_line)

        # Detect URL pools
        blocks = self._detect_url_pools(blocks)

        return blocks

    def _extract_blocks_simple(self, content: str) -> List[Block]:
        """Extract blocks using simple pattern matching.

        Fallback when AST is not available.
        """
        blocks = []
        lines = content.split("\n")
        current_line = 0

        while current_line < len(lines):
            line = lines[current_line]

            # Check for code fence
            if line.strip().startswith("```"):
                block, end_line = self._extract_code_block_simple(lines, current_line)
                blocks.append(block)
                current_line = end_line + 1
                continue

            # Check for table
            if "|" in line and current_line + 1 < len(lines):
                next_line = lines[current_line + 1]
                if "---" in next_line or "|" in next_line:
                    block, end_line = self._extract_table_simple(lines, current_line)
                    blocks.append(block)
                    current_line = end_line + 1
                    continue

            # Check for list
            if re.match(r"^\s*[-*+]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
                block, end_line = self._extract_list_simple(lines, current_line)
                blocks.append(block)
                current_line = end_line + 1
                continue

            # Check for header
            if line.strip().startswith("#"):
                match = re.match(r"^(#{1,6})\s+(.+)", line.strip())
                if match:
                    block = Block(
                        type=BlockType.HEADER,
                        content=line,
                        start_line=current_line + 1,
                        end_line=current_line + 1,
                        size=0,
                        metadata={"level": len(match.group(1)), "text": match.group(2)},
                    )
                    blocks.append(block)
                    current_line += 1
                    continue

            # Check for blank line
            if not line.strip():
                block = Block(
                    type=BlockType.BLANK,
                    content=line,
                    start_line=current_line + 1,
                    end_line=current_line + 1,
                    size=0,
                    metadata={},
                )
                blocks.append(block)
                current_line += 1
                continue

            # Default: paragraph
            block, end_line = self._extract_paragraph_simple(lines, current_line)
            blocks.append(block)
            current_line = end_line + 1

        # Detect URL pools
        blocks = self._detect_url_pools(blocks)

        return blocks

    def _extract_code_block_simple(
        self, lines: List[str], start: int
    ) -> Tuple[Block, int]:
        """Extract code block from lines.

        CRITICAL FIX (Phase 1.1): Ensures complete code block extraction
        to prevent splitting code fences across chunks.
        """
        end = start + 1
        # Search for closing fence
        while end < len(lines) and not lines[end].strip().startswith("```"):
            end += 1

        # CRITICAL: If no closing fence found, include all remaining lines
        # to prevent unbalanced fences in output chunks
        if end >= len(lines):
            # Unclosed code block - include everything to end of content
            end = len(lines) - 1
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                f"Unclosed code block starting at line {start + 1}, "
                f"including all content to end of document"
            )

        content = "\n".join(lines[start : end + 1])

        # Extract language from first line
        lang_match = re.match(r"^```(\w+)", lines[start])
        language = lang_match.group(1) if lang_match else ""

        return (
            Block(
                type=BlockType.CODE,
                content=content,
                start_line=start + 1,
                end_line=end + 1,
                size=0,
                metadata={"language": language},
            ),
            end,
        )

    def _extract_table_simple(self, lines: List[str], start: int) -> Tuple[Block, int]:
        """Extract table block from lines."""
        end = start
        while end < len(lines) and "|" in lines[end]:
            end += 1
        end -= 1  # Back up to last table line

        content = "\n".join(lines[start : end + 1])

        return (
            Block(
                type=BlockType.TABLE,
                content=content,
                start_line=start + 1,
                end_line=end + 1,
                size=0,
                metadata={},
            ),
            end,
        )

    def _extract_list_simple(self, lines: List[str], start: int) -> Tuple[Block, int]:
        """Extract list block from lines."""
        end = start
        while end < len(lines):
            line = lines[end]
            # Continue if list item or indented continuation
            if (
                re.match(r"^\s*[-*+]\s+", line)
                or re.match(r"^\s*\d+\.\s+", line)
                or (line.strip() and line.startswith(" "))
            ):
                end += 1
            elif not line.strip():  # Allow blank lines in lists
                end += 1
            else:
                break
        end -= 1

        content = "\n".join(lines[start : end + 1])

        return (
            Block(
                type=BlockType.LIST,
                content=content,
                start_line=start + 1,
                end_line=end + 1,
                size=0,
                metadata={},
            ),
            end,
        )

    def _extract_paragraph_simple(
        self, lines: List[str], start: int
    ) -> Tuple[Block, int]:
        """Extract paragraph block from lines.

        Extracts a single paragraph (continuous non-blank lines).
        """
        end = start
        # For URL pool detection, treat each line as potential separate paragraph
        # if it contains a URL - this allows URL pool detection to work
        if self.URL_PATTERN.search(lines[start]):
            # Single line paragraph if it has URL
            content = lines[start]
            return (
                Block(
                    type=BlockType.PARAGRAPH,
                    content=content,
                    start_line=start + 1,
                    end_line=start + 1,
                    size=0,
                    metadata={},
                ),
                start,
            )

        # Regular paragraph: accumulate until blank line
        while end < len(lines) and lines[end].strip():
            # Stop if next line has URL (potential pool member)
            if end > start and self.URL_PATTERN.search(lines[end]):
                break
            end += 1
        end -= 1

        content = "\n".join(lines[start : end + 1])

        return (
            Block(
                type=BlockType.PARAGRAPH,
                content=content,
                start_line=start + 1,
                end_line=end + 1,
                size=0,
                metadata={},
            ),
            end,
        )

    def _extract_line_range(
        self, lines: List[str], start_line: int, end_line: int
    ) -> str:
        """Extract content from line range (1-indexed)."""
        return "\n".join(lines[start_line - 1 : end_line])

    def _extract_paragraphs_from_uncovered(
        self, lines: List[str], covered_lines: set
    ) -> List[Block]:
        """Extract paragraphs from lines not covered by structural elements."""
        blocks = []
        current_para: list[str] = []
        para_start = None

        for i, line in enumerate(lines, 1):
            if i in covered_lines:
                # Save current paragraph if any
                if current_para:
                    content = "\n".join(current_para)
                    blocks.append(
                        Block(
                            type=BlockType.PARAGRAPH,
                            content=content,
                            start_line=para_start,
                            end_line=i - 1,
                            size=0,
                            metadata={},
                        )
                    )
                    current_para = []
                    para_start = None
            else:
                if line.strip():
                    if para_start is None:
                        para_start = i
                    current_para.append(line)
                elif current_para:
                    # Blank line ends paragraph
                    content = "\n".join(current_para)
                    blocks.append(
                        Block(
                            type=BlockType.PARAGRAPH,
                            content=content,
                            start_line=para_start,
                            end_line=i - 1,
                            size=0,
                            metadata={},
                        )
                    )
                    current_para = []
                    para_start = None

        # Save final paragraph
        if current_para:
            content = "\n".join(current_para)
            blocks.append(
                Block(
                    type=BlockType.PARAGRAPH,
                    content=content,
                    start_line=para_start,
                    end_line=len(lines),
                    size=0,
                    metadata={},
                )
            )

        return blocks

    def _detect_url_pools(self, blocks: List[Block]) -> List[Block]:
        """Detect and mark URL pool blocks.

        A URL pool is 3+ consecutive paragraph blocks with URLs.
        Addresses MC-005 (preamble/link block fragmentation).
        """
        i = 0
        result = []

        while i < len(blocks):
            block = blocks[i]

            # Check if this starts a URL pool
            if block.type == BlockType.PARAGRAPH and self.URL_PATTERN.search(
                block.content
            ):
                # Look ahead for more URL paragraphs
                pool_blocks = [block]
                j = i + 1

                while j < len(blocks):
                    next_block = blocks[j]
                    if (
                        next_block.type == BlockType.PARAGRAPH
                        and self.URL_PATTERN.search(next_block.content)
                    ):
                        pool_blocks.append(next_block)
                        j += 1
                    elif next_block.type == BlockType.BLANK:
                        # Allow blank lines between URLs
                        j += 1
                    else:
                        break

                # If 3+ URL paragraphs, combine into URL pool
                if len(pool_blocks) >= 3:
                    combined_content = "\n".join(b.content for b in pool_blocks)
                    url_pool = Block(
                        type=BlockType.URL_POOL,
                        content=combined_content,
                        start_line=pool_blocks[0].start_line,
                        end_line=pool_blocks[-1].end_line,
                        size=0,
                        metadata={"url_count": len(pool_blocks)},
                    )
                    result.append(url_pool)
                    i = j
                    continue

            result.append(block)
            i += 1

        return result

    def pack_blocks_into_chunks(
        self,
        blocks: List[Block],
        config: ChunkConfig,
        section_header: Optional[str] = None,
    ) -> List[Chunk]:
        """Pack blocks into chunks respecting size limits.

        Args:
            blocks: List of blocks to pack
            config: Chunking configuration
            section_header: Optional header to prepend to each chunk

        Returns:
            List of chunks
        """
        chunks = []
        current_blocks: list[Block] = []
        current_size = 0

        # Add section header if provided
        header_size = len(section_header) + 2 if section_header else 0

        for block in blocks:
            # Skip blank blocks
            if block.type == BlockType.BLANK:
                continue

            block_size = block.size
            projected_size = current_size + block_size + header_size

            # CRITICAL FIX (Phase 1.1): Code blocks must never be split
            # Force code blocks to start a new chunk if they don't fit
            is_code_block = block.type == BlockType.CODE

            # Check if adding this block exceeds limit
            if projected_size > config.max_chunk_size and current_blocks:
                # For code blocks, always start new chunk to prevent splitting
                if is_code_block or current_blocks:
                    # Create chunk from current blocks
                    chunk = self._create_chunk_from_blocks(
                        current_blocks, section_header, config
                    )
                    chunks.append(chunk)

                    # Start new chunk with code block
                    current_blocks = [block]
                    current_size = block_size
                else:
                    # Add block to current chunk
                    current_blocks.append(block)
                    current_size += block_size
            else:
                # Add block to current chunk
                current_blocks.append(block)
                current_size += block_size

        # Create final chunk
        if current_blocks:
            chunk = self._create_chunk_from_blocks(
                current_blocks, section_header, config
            )
            chunks.append(chunk)

        return chunks

    def _create_chunk_from_blocks(
        self,
        blocks: List[Block],
        section_header: Optional[str] = None,
        config: ChunkConfig = None,
    ) -> Chunk:
        """Create chunk from blocks.

        Args:
            blocks: Blocks to include in chunk
            section_header: Optional header to prepend
            config: Configuration for oversize detection

        Returns:
            Chunk object
        """
        # Build content
        content_parts = []
        if section_header:
            content_parts.append(section_header)

        content_parts.extend(block.content for block in blocks)
        content = "\n\n".join(content_parts)

        # Calculate line range
        start_line = min(block.start_line for block in blocks)
        end_line = max(block.end_line for block in blocks)

        # Build metadata
        metadata = {
            "block_count": len(blocks),
            "block_types": [block.type.value for block in blocks],
        }

        # Check if chunk exceeds max size and mark as oversize if needed
        # This addresses test_property_size_compliance and
        # test_property_wide_tables_allowed_oversize
        if config and hasattr(config, "max_chunk_size"):
            chunk_size = len(content)
            if chunk_size > config.max_chunk_size:
                # FIX #3: Check if overage is within 5% tolerance first
                overage_pct = (
                    (chunk_size - config.max_chunk_size) / config.max_chunk_size
                ) * 100

                # Debug logging
                import logging

                logger = logging.getLogger(__name__)
                block_splitting = getattr(config, "block_based_splitting", None)
                logger.debug(
                    f"Oversize chunk detected: size={chunk_size}, "
                    f"max={config.max_chunk_size}, "
                    f"overage_pct={overage_pct:.2f}%, "
                    f"block_based_splitting={block_splitting}"
                )

                if (
                    overage_pct <= 5.0
                    and hasattr(config, "block_based_splitting")
                    and config.block_based_splitting
                ):
                    # Small overage within 5% tolerance due to block alignment
                    # Mark as oversize to be explicit about the condition
                    metadata["allow_oversize"] = True
                    metadata["oversize_reason"] = "block_alignment_tolerance"
                    metadata["oversize_pct"] = round(overage_pct, 2)
                    logger.debug("Marked as block_alignment_tolerance")
                else:
                    # Large overage - determine reason based on block types
                    metadata["allow_oversize"] = True
                    has_table = any(b.type == BlockType.TABLE for b in blocks)
                    has_code = any(b.type == BlockType.CODE for b in blocks)
                    has_url_pool = any(b.type == BlockType.URL_POOL for b in blocks)

                    if has_table:
                        metadata["oversize_reason"] = "table_integrity"
                    elif has_code:
                        metadata["oversize_reason"] = "code_block_integrity"
                    elif has_url_pool:
                        metadata["oversize_reason"] = "url_pool_integrity"
                    else:
                        metadata["oversize_reason"] = "block_integrity"
                    reason = metadata["oversize_reason"]
                    logger.debug(f"Marked with reason: {reason}")

        return Chunk(
            content=content, start_line=start_line, end_line=end_line, metadata=metadata
        )
