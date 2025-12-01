"""
StructuralStrategy - Header-based chunking strategy.

This strategy chunks documents based on header hierarchy, creating
semantically meaningful sections while preserving document structure.

Algorithm Documentation:
    - Structural Strategy: docs/markdown-extractor/03-strategies/structural-strategy.md
    - Strategy Selection: docs/markdown-extractor/02-algorithm-core/strategy-selection.md  # noqa: E501
"""

import logging
import re
from dataclasses import dataclass
from typing import List, Optional

from markdown_chunker.parser.types import ContentAnalysis, Stage1Results

from ..types import Chunk, ChunkConfig
from .base import BaseStrategy

# Set up logger for this module
logger = logging.getLogger(__name__)


@dataclass
class HeaderInfo:
    """Information about a header in the document."""

    level: int
    text: str
    line: int
    position: int
    parent: Optional["HeaderInfo"] = None
    children: Optional[List["HeaderInfo"]] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


@dataclass
class Section:
    """A document section defined by headers."""

    header: HeaderInfo
    content: str
    start_line: int
    end_line: int
    size: int
    has_subsections: bool = False
    subsections: Optional[List["Section"]] = None

    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []


class StructuralStrategy(BaseStrategy):
    """
    Strategy for structured documents with clear header hierarchy.

    This strategy:
    - Splits content by header boundaries
    - Preserves header hierarchy in metadata
    - Combines short sections to meet minimum size
    - Supports multi-level structures (H1-H6)
    - Adds header path information to chunks

    Priority: 5 (medium-low)
    """

    # Header detection patterns
    HEADER_PATTERNS = [
        # ATX headers (# ## ### etc.)
        r"^(#{1,6})\s+(.+?)(?:\s*#*)?$",
        # Setext headers (underlined with=or -)
        r"^(.+?)\n([=]{3,}|[-]{3,})$",
    ]

    def __init__(self):
        """Initialize structural strategy with Phase 2 components."""
        # Phase 2: Import section builder for semantic quality improvements
        try:
            from markdown_chunker.chunker.section_builder import SectionBuilder

            self.section_builder = SectionBuilder()
            self._phase2_available = True
        except ImportError:
            try:
                # Try relative import as fallback
                from ..section_builder import SectionBuilder

                self.section_builder = SectionBuilder()
                self._phase2_available = True
            except ImportError:
                try:
                    # Try direct import for testing
                    import os
                    import sys

                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
                    from section_builder import SectionBuilder

                    self.section_builder = SectionBuilder()
                    self._phase2_available = True
                except ImportError:
                    self.section_builder = None
                    self._phase2_available = False

    @property
    def name(self) -> str:
        """Strategy name."""
        return "structural"

    @property
    def priority(self) -> int:
        """Medium-low priority."""
        return 5

    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        """
        Check if strategy can handle the content.

        Requires:
        - At least 3 headers (configurable via header_count_threshold)
        - Header hierarchy with multiple levels (max_header_depth > 1)

        Args:
            analysis: Content analysis from Stage 1
            config: Chunking configuration

        Returns:
            True if document has sufficient structure for this strategy

        Examples:
            >>> analysis=ContentAnalysis(header_count=5, max_header_depth=3, ...)
            >>> config=ChunkConfig(header_count_threshold=3)
            >>> strategy=StructuralStrategy()
            >>> print(strategy.can_handle(analysis, config))
            True
        """
        return (
            analysis.get_total_header_count() >= config.header_count_threshold
            and analysis.max_header_depth > 1  # Has hierarchy
        )

    def calculate_quality(self, analysis: ContentAnalysis) -> float:
        """
        Calculate quality score for structural strategy.

        Higher quality for:
        - More headers (≥10: 0.5, ≥5: 0.4, ≥3: 0.3)
        - Deeper hierarchy (≥4 levels: 0.3, ≥3: 0.2, >1: 0.1)
        - Clear structure (+0.2 bonus)
        - Less code content (penalty: ×0.5 if code_ratio > 0.5)

        Args:
            analysis: Content analysis from Stage 1

        Returns:
            Quality score between 0.0 and 1.0

        Examples:
            >>> analysis=ContentAnalysis(
            ...     header_count=10,
            ...     max_header_depth=4,
            ...     code_ratio=0.2,
            ...     has_hierarchy=True,
            ...     ...
            ... )
            >>> strategy=StructuralStrategy()
            >>> score=strategy.calculate_quality(analysis)
            >>> print(f"{score:.2f}")  # 0.5 + 0.3 + 0.2=1.0
            1.00
        """
        score = 0.0

        # Header count contribution
        total_headers = analysis.get_total_header_count()
        if total_headers >= 10:
            score += 0.5
        elif total_headers >= 5:
            score += 0.4
        elif total_headers >= 3:
            score += 0.3

        # Hierarchy depth contribution
        if analysis.max_header_depth >= 4:
            score += 0.3
        elif analysis.max_header_depth >= 3:
            score += 0.2
        elif analysis.max_header_depth > 1:
            score += 0.1

        # Structure bonus
        if hasattr(analysis, "has_hierarchy") and analysis.has_hierarchy:
            score += 0.2

        # Penalty for high code ratio
        if analysis.code_ratio > 0.5:
            score *= 0.5

        return min(score, 1.0)

    def apply(
        self, content: str, stage1_results: Stage1Results, config: ChunkConfig
    ) -> List[Chunk]:
        """
        Apply structural strategy to create chunks.

        Args:
            content: Original markdown content
            stage1_results: Results from Stage 1 processing
            config: Chunking configuration

        Returns:
            List of chunks created by header-based splitting
        """
        if not content.strip():
            return []

        # Phase 2: Use section-aware chunking if available and enabled
        # Always try Phase 2 if available to test the implementation
        if self._phase2_available and hasattr(stage1_results, "ast"):
            try:
                return self._apply_section_aware(content, stage1_results, config)
            except Exception as e:
                # Log the error and fallback to Phase 1 implementation
                import logging

                logging.warning(
                    f"Phase 2 chunking failed, falling back to Phase 1: {e}"
                )
                pass

        # Phase 1: Original implementation
        # Extract headers from Stage 1 results or detect them
        headers = self._extract_headers(content, stage1_results)

        if not headers:
            # No headers found - cannot use structural strategy
            return []

        # Build header hierarchy (sets parent/child relationships)
        self._build_hierarchy(headers)

        # Create sections based on headers
        sections = self._create_sections(content, headers)

        # Process sections into chunks
        chunks = self._process_sections(sections, config)

        return self._validate_chunks(chunks, config)

    def _extract_headers(
        self, content: str, stage1_results: Stage1Results
    ) -> List[HeaderInfo]:
        """
        Extract headers from content or Stage 1 results.

        Args:
            content: Markdown content
            stage1_results: Stage 1 processing results

        Returns:
            List of HeaderInfo objects
        """
        headers = []

        # Try to use Stage 1 results first
        if hasattr(stage1_results, "elements") and stage1_results.elements.headers:
            for header in stage1_results.elements.headers:
                headers.append(
                    HeaderInfo(
                        level=header.level,
                        text=header.text,
                        line=max(1, header.line),  # Ensure 1-based line numbering
                        position=header.offset,
                    )
                )
        else:
            # Fallback to manual detection
            headers = self._detect_headers_manual(content)

        return sorted(headers, key=lambda h: h.position)

    def _detect_headers_manual(self, content: str) -> List[HeaderInfo]:
        """
        Manually detect headers in content using regex patterns.

        Args:
            content: Markdown content

        Returns:
            List of HeaderInfo objects
        """
        headers = []
        lines = content.split("\n")
        position = 0

        for line_num, line in enumerate(lines, 1):
            # ATX headers (# ## ### etc.)
            atx_match = re.match(r"^(#{1,6})\s+(.+?)(?:\s*#*)?$", line.strip())
            if atx_match:
                level = len(atx_match.group(1))
                text = atx_match.group(2).strip()

                headers.append(
                    HeaderInfo(level=level, text=text, line=line_num, position=position)
                )

            # Setext headers (check next line for underline)
            elif line.strip() and line_num < len(lines):
                next_line = lines[line_num] if line_num < len(lines) else ""
                if re.match(r"^[=]{3,}$", next_line.strip()):
                    # H1 (underlined with=)
                    headers.append(
                        HeaderInfo(
                            level=1, text=line.strip(), line=line_num, position=position
                        )
                    )
                elif re.match(r"^[-]{3,}$", next_line.strip()):
                    # H2 (underlined with -)
                    headers.append(
                        HeaderInfo(
                            level=2, text=line.strip(), line=line_num, position=position
                        )
                    )

            position += len(line) + 1  # +1 for newline

        return headers

    def _build_hierarchy(self, headers: List[HeaderInfo]) -> List[HeaderInfo]:
        """
        Build parent-child relationships between headers.

        Args:
            headers: List of headers sorted by position

        Returns:
            List of root headers with hierarchy built
        """
        if not headers:
            return []

        # Stack to track parent headers at each level
        parent_stack = []
        root_headers = []

        for header in headers:
            # Pop parents that are at same or deeper level
            while parent_stack and parent_stack[-1].level >= header.level:
                parent_stack.pop()

            # Set parent if available
            if parent_stack:
                header.parent = parent_stack[-1]
                parent_stack[-1].children.append(header)
            else:
                # This is a root header
                root_headers.append(header)

            # Add current header to stack
            parent_stack.append(header)

        return root_headers

    def _create_sections(
        self, content: str, headers: List[HeaderInfo]
    ) -> List[Section]:
        """
        Create sections based on header boundaries.

        Args:
            content: Original content
            headers: List of headers

        Returns:
            List of Section objects with subsection relationships
        """
        sections = []
        content_lines = content.split("\n")
        header_to_section = {}  # Map header id to section

        # First pass: create all sections
        for i, header in enumerate(headers):
            # Determine section boundaries
            start_line = header.line
            start_pos = header.position

            # Find end position
            if i + 1 < len(headers):
                end_line = headers[i + 1].line - 1
                end_pos = headers[i + 1].position
            else:
                end_line = len(content_lines)
                end_pos = len(content)

            # Extract section content
            section_content = content[start_pos:end_pos].strip()

            # Check for subsections
            has_subsections = len(header.children) > 0

            section = Section(
                header=header,
                content=section_content,
                start_line=start_line,
                end_line=end_line,
                size=len(section_content),
                has_subsections=has_subsections,
                subsections=[],  # Will be populated in second pass
            )

            sections.append(section)
            # Use id() to get unique identifier for header object
            header_to_section[id(header)] = section

        # Second pass: populate subsections based on header hierarchy
        for section in sections:
            if section.has_subsections:
                for child_header in section.header.children:
                    child_id = id(child_header)
                    if child_id in header_to_section:
                        child_section = header_to_section[child_id]
                        section.subsections.append(child_section)

        return sections

    def _process_sections(
        self, sections: List[Section], config: ChunkConfig
    ) -> List[Chunk]:
        """
        Process sections into chunks, handling size constraints.

        Args:
            sections: List of sections
            config: Chunking configuration

        Returns:
            List of chunks
        """
        chunks = []

        for section in sections:
            if section.size <= config.max_chunk_size:
                # Section fits in one chunk
                chunk = self._create_section_chunk(section, config)
                if chunk:
                    chunks.append(chunk)
            else:
                # Section too large - split it
                split_chunks = self._split_large_section(section, config)
                chunks.extend(split_chunks)

        # Combine small adjacent chunks if beneficial
        chunks = self._combine_small_chunks(chunks, config)

        return chunks

    def _create_section_chunk(self, section: Section, config: ChunkConfig) -> Chunk:
        """
        Create a chunk from a section.

        Args:
            section: Section to convert
            config: Chunking configuration

        Returns:
            Chunk with section content and metadata
        """
        header_path = self._build_header_path(section.header)

        metadata = {
            "header_level": section.header.level,
            "header_text": section.header.text,
            "header_path": header_path,
            "has_subsections": section.has_subsections,
        }

        # Add hierarchy information
        if section.header.parent:
            parent_path = self._build_header_path(section.header.parent)
            metadata["parent_header_path"] = parent_path

        return self._create_chunk(
            content=section.content,
            start_line=section.start_line,
            end_line=section.end_line,
            content_type="text",
            **metadata,
        )

    def _split_large_section(
        self, section: Section, config: ChunkConfig
    ) -> List[Chunk]:
        """
        Split a large section into multiple chunks.

        Args:
            section: Large section to split
            config: Chunking configuration

        Returns:
            List of chunks from the split section
        """
        # Try splitting by subsections first
        if section.has_subsections and section.subsections:
            subsection_chunks = self._split_by_subsections(section, config)
            if subsection_chunks:
                return subsection_chunks

        # Fall back to splitting by paragraphs
        return self._split_by_paragraphs(section, config)

    def _split_by_subsections(
        self, section: Section, config: ChunkConfig
    ) -> List[Chunk]:
        """
        Split section by its subsections recursively.

        Args:
            section: Section with subsections
            config: Chunking configuration

        Returns:
            List of chunks from subsections
        """
        chunks = []

        for subsection in section.subsections:
            if subsection.size <= config.max_chunk_size:
                # Subsection fits in one chunk - create chunk directly
                chunk = self._create_section_chunk(subsection, config)
                chunks.append(chunk)
            else:
                # Subsection too large - recursively split it
                sub_chunks = self._split_large_section(subsection, config)
                chunks.extend(sub_chunks)

        return chunks

    def _split_by_paragraphs(
        self, section: Section, config: ChunkConfig
    ) -> List[Chunk]:
        """
        Split section by paragraphs, preserving atomic elements (code blocks).

        Args:
            section: Section to split
            config: Chunking configuration

        Returns:
            List of chunks from paragraphs
        """
        chunks = []
        # Split content preserving code blocks as atomic units
        blocks = self._split_preserving_code_blocks(section.content)
        current_content = ""
        current_start_line = section.start_line

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            # Check if this is a code block (atomic - cannot be split)
            is_code_block = block.startswith("```") and block.count("```") >= 2

            # Check if adding this block would exceed size
            potential_content = self._build_potential_content(current_content, block)

            if len(potential_content) > config.max_chunk_size and current_content:
                # Create chunk with current content
                chunk = self._create_section_chunk_part(
                    section, current_content, current_start_line, config
                )
                chunks.append(chunk)

                # Start new chunk with this block
                current_content = block
                current_start_line = self._estimate_line_number(
                    section.content, len(current_content)
                )
            elif is_code_block and len(block) > config.max_chunk_size:
                # Code block is too large but atomic - flush current and add as oversize
                if current_content:
                    chunk = self._create_section_chunk_part(
                        section, current_content, current_start_line, config
                    )
                    chunks.append(chunk)

                # Add code block as separate chunk (may be oversize)
                chunk = self._create_section_chunk_part(
                    section, block, current_start_line, config
                )
                chunk.add_metadata("allow_oversize", True)
                chunk.add_metadata("atomic_element", "code_block")
                chunks.append(chunk)

                current_content = ""
                current_start_line = self._estimate_line_number(
                    section.content, len(block)
                )
            else:
                # Add block to current chunk
                current_content = self._build_potential_content(current_content, block)

        # Add final chunk if there's remaining content
        if current_content:
            chunk = self._create_section_chunk_part(
                section, current_content, current_start_line, config
            )
            chunks.append(chunk)

        return chunks

    def _split_preserving_code_blocks(self, content: str) -> List[str]:
        """
        Split content into blocks, keeping code blocks intact.

        Args:
            content: Content to split

        Returns:
            List of content blocks (code blocks kept whole)
        """
        blocks = []
        current_block = ""
        in_code_block = False

        for line in content.split("\n"):
            if line.strip().startswith("```"):
                if in_code_block:
                    # End of code block
                    current_block += line + "\n"
                    blocks.append(current_block.strip())
                    current_block = ""
                    in_code_block = False
                else:
                    # Start of code block - flush current content first
                    if current_block.strip():
                        # Split non-code content by paragraphs
                        paragraphs = re.split(r"\n\s*\n", current_block)
                        blocks.extend([p.strip() for p in paragraphs if p.strip()])
                    current_block = line + "\n"
                    in_code_block = True
            else:
                current_block += line + "\n"

        # Handle remaining content
        if current_block.strip():
            if in_code_block:
                # Unclosed code block - add as is
                blocks.append(current_block.strip())
            else:
                # Split remaining non-code content by paragraphs
                paragraphs = re.split(r"\n\s*\n", current_block)
                blocks.extend([p.strip() for p in paragraphs if p.strip()])

        return blocks

    def _build_potential_content(self, current: str, paragraph: str) -> str:
        """
        Build potential content by combining current and new paragraph.

        Args:
            current: Current content
            paragraph: New paragraph to add

        Returns:
            Combined content
        """
        if current:
            return current + "\n\n" + paragraph
        return paragraph

    def _create_section_chunk_part(
        self, section: Section, content: str, start_line: int, config: ChunkConfig
    ) -> Chunk:
        """
        Create a chunk from part of a section.

        Args:
            section: Original section
            content: Part of section content
            start_line: Starting line number
            config: Chunking configuration

        Returns:
            Chunk with partial section content
        """
        header_path = self._build_header_path(section.header)
        end_line = start_line + content.count("\n")

        metadata = {
            "header_level": section.header.level,
            "header_text": section.header.text,
            "header_path": header_path,
            "section_part": True,
            "original_section_size": section.size,
        }

        return self._create_chunk(
            content=content,
            start_line=start_line,
            end_line=end_line,
            content_type="text",
            **metadata,
        )

    def _combine_small_chunks(
        self, chunks: List[Chunk], config: ChunkConfig
    ) -> List[Chunk]:
        """
        Combine small adjacent chunks to meet minimum size requirements.

        Args:
            chunks: List of chunks to potentially combine
            config: Chunking configuration

        Returns:
            List of chunks with small ones combined
        """
        if not chunks or config.min_chunk_size <= 0:
            return chunks

        combined_chunks = []
        current_chunk = None

        for chunk in chunks:
            if current_chunk is None:
                current_chunk = chunk
            elif (
                current_chunk.size < config.min_chunk_size
                and current_chunk.size + chunk.size <= config.max_chunk_size
            ):
                # Combine with current chunk
                combined_content = current_chunk.content + "\n\n" + chunk.content
                combined_metadata = current_chunk.metadata.copy()
                combined_metadata["combined_sections"] = True

                # Remove content_type from metadata to avoid duplication
                if "content_type" in combined_metadata:
                    del combined_metadata["content_type"]

                current_chunk = self._create_chunk(
                    content=combined_content,
                    start_line=current_chunk.start_line,
                    end_line=chunk.end_line,
                    content_type="text",
                    **combined_metadata,
                )
            else:
                # Cannot combine - add current chunk and start new one
                combined_chunks.append(current_chunk)
                current_chunk = chunk

        # Add final chunk
        if current_chunk:
            combined_chunks.append(current_chunk)

        return combined_chunks

    def _build_header_path(self, header: HeaderInfo) -> str:
        """
        Build full header path from root to current header.

        Args:
            header: Header to build path for

        Returns:
            Full header path (e.g., "/Documentation/Getting Started/Installation")
        """
        path_parts = []
        current = header

        # Collect all parents
        while current:
            path_parts.insert(0, current.text)
            current = current.parent

        # Build path
        return "/" + "/".join(path_parts)

    def _estimate_line_number(self, content: str, position: int) -> int:
        """
        Estimate line number for a position in content.

        Args:
            content: Content string
            position: Character position

        Returns:
            Estimated line number
        """
        return content[:position].count("\n") + 1

    def _get_selection_reason(self, analysis: ContentAnalysis, can_handle: bool) -> str:
        """Get reason for strategy selection."""
        if can_handle:
            return (
                f"Document has {analysis.header_count} headers with "
                f"{analysis.max_header_depth} levels - "
                f"good for structural chunking"
            )
        else:
            if analysis.header_count < 3:
                return (
                    f"Too few headers ({analysis.header_count}) for structural strategy"
                )
            elif analysis.max_header_depth <= 1:
                return "No header hierarchy - structural strategy needs multiple levels"
            else:
                return "Document structure not suitable for structural strategy"

    def _apply_section_aware(
        self, content: str, stage1_results: Stage1Results, config: ChunkConfig
    ) -> List[Chunk]:
        """
        Apply Phase 2 section-aware chunking (semantic quality improvements).

        This method uses the SectionBuilder to create logical sections that
        respect document structure and preserve semantic coherence.

        Args:
            content: Original markdown content
            stage1_results: Results from Stage 1 processing
            config: Chunking configuration

        Returns:
            List of chunks with enhanced metadata and structure preservation
        """
        # Build sections from AST
        sections = self.section_builder.build_sections(
            stage1_results.ast, boundary_level=config.section_boundary_level
        )

        if not sections:
            return []

        chunks = []

        for section in sections:
            # Check if section fits in one chunk
            section_size = section.calculate_size()

            if section_size <= config.max_chunk_size:
                # Create single chunk from section
                chunk = self._create_chunk_from_section(section, config)
                if chunk:
                    # Check if chunk actually exceeds max size and mark as oversize
                    if len(chunk.content) > config.max_chunk_size:
                        chunk.metadata["is_oversize"] = True
                        chunk.metadata["oversize"] = True
                        chunk.metadata["allow_oversize"] = True
                        chunk.metadata["oversize_reason"] = "section_too_large"
                    chunks.append(chunk)
            else:
                # Section too large - split it (Tasks 5.1-5.3)
                section_chunks = self._split_large_section_phase2(section, config)
                chunks.extend(section_chunks)

        # Merge chunks with insufficient content (Task 8)
        chunks = self._merge_small_chunks(chunks, config)

        # Validate chunks (add oversize metadata, etc.)
        return self._validate_chunks(chunks, config)

    def _create_chunk_from_section(
        self, section, config: ChunkConfig
    ) -> Optional[Chunk]:
        """
        Create a single chunk from a section.

        Args:
            section: Section object from SectionBuilder
            config: Chunking configuration

        Returns:
            Chunk object or None if section is empty
        """
        # Collect content from section
        content_parts = []

        # Add header if present
        if section.header:
            content_parts.append(section.header.content)

        # Add content blocks
        for block in section.content_blocks:
            content_parts.append(block.content)

        if not content_parts:
            return None

        content = "\n\n".join(content_parts)

        # Build metadata
        metadata = {
            "content_type": "section",
            "strategy": self.name,
            "section_path": section.header_path,
            "start_offset": section.start_offset,
            "end_offset": section.end_offset,
            "block_ids": [block.metadata.get("id") for block in section.content_blocks],
            "has_code": any(b.block_type == "code" for b in section.content_blocks),
            "has_table": any(b.block_type == "table" for b in section.content_blocks),
            "has_list": any(b.block_type == "list" for b in section.content_blocks),
        }

        # Add header metadata for test compatibility
        if section.header_level > 0:
            metadata["header_level"] = section.header_level
        if section.header_text:
            metadata["header_text"] = section.header_text
        # Filter out empty strings from header_path before creating path string
        if section.header_path:
            filtered_path = [p for p in section.header_path if p and p.strip()]
            if filtered_path:
                metadata["header_path"] = "/" + "/".join(filtered_path)

        # Generate section ID
        if section.header_path:
            filtered_path = [p for p in section.header_path if p and p.strip()]
            if filtered_path:
                section_id = "-".join(filtered_path).lower()
                section_id = re.sub(r"[^a-z0-9-]", "-", section_id)
                section_id = re.sub(r"-+", "-", section_id).strip("-")
                if section_id:
                    metadata["section_id"] = section_id

        return Chunk(
            content=content,
            start_line=section.start_line,
            end_line=section.end_line,
            metadata=metadata,
        )

    def _split_large_section_phase2(self, section, config: ChunkConfig) -> List[Chunk]:
        """
        Split a large section into multiple chunks (Phase 2 Task 5.1).

        Rules:
        - Keep header with first chunk
        - Split only at LogicalBlock boundaries
        - Handle oversize atomic blocks (MUST create chunk, no data loss)
        - Add overlap between chunks if enabled

        Args:
            section: Section object that's too large
            config: Chunking configuration

        Returns:
            List of chunks from the section
        """
        chunks = []
        current_blocks = []
        current_size = 0

        # Always include header in first chunk
        if section.header:
            # Handle both Phase 1 HeaderInfo and Phase 2 LogicalBlock
            if hasattr(section.header, "content"):
                # Phase 2 LogicalBlock
                current_blocks.append(section.header)
                current_size = len(section.header.content)
            else:
                # Phase 1 HeaderInfo - convert to LogicalBlock-like structure
                header_content = f"{'#' * section.header.level} {section.header.text}"
                current_size = len(header_content)
                # Don't add to current_blocks for Phase 1 compatibility

        # Handle both Phase 1 and Phase 2 section structures
        content_blocks = getattr(section, "content_blocks", [])

        for block in content_blocks:
            # Handle both Phase 1 and Phase 2 block structures
            if hasattr(block, "content"):
                block_size = len(block.content)
            elif hasattr(block, "text"):
                # Phase 1 compatibility
                block_size = len(str(block.text))
            else:
                # Fallback
                block_size = len(str(block))

            # Check if single block exceeds max size (oversize atomic block)
            if block_size > config.max_chunk_size:
                # Finish current chunk if any
                if current_blocks:
                    chunk = self._create_chunk_from_blocks_simple(
                        current_blocks,
                        section.header_path,
                        section.start_line,
                        config,
                        is_oversize=False,
                        header_level=section.header_level,
                        header_text=section.header_text,
                    )
                    if chunk:
                        chunks.append(chunk)
                    current_blocks = []
                    current_size = 0

                # MUST create oversize chunk - cannot drop atomic blocks (data loss)
                # This is required by Requirements 1.5 and 5.5
                chunk = self._create_chunk_from_blocks_simple(
                    [block],
                    section.header_path,
                    section.start_line,
                    config,
                    is_oversize=True,
                    oversize_reason="atomic_block",
                    header_level=section.header_level,
                    header_text=section.header_text,
                )
                if chunk:
                    chunks.append(chunk)
                continue

            # Check if adding block would exceed size
            if current_size + block_size > config.max_chunk_size and current_blocks:
                # Create chunk from current blocks
                chunk = self._create_chunk_from_blocks_simple(
                    current_blocks,
                    section.header_path,
                    section.start_line,
                    config,
                    is_oversize=False,
                    header_level=section.header_level,
                    header_text=section.header_text,
                )
                if chunk:
                    chunks.append(chunk)

                # Start new chunk with overlap if enabled (Task 5.2)
                if config.enable_overlap and chunks:
                    overlap_blocks = self._get_overlap_blocks(
                        current_blocks, config.overlap_size
                    )
                    current_blocks = overlap_blocks + [block]
                    current_size = sum(len(b.content) for b in current_blocks)
                else:
                    current_blocks = [block]
                    current_size = block_size
            else:
                # Add block to current chunk
                current_blocks.append(block)
                current_size += block_size

        # Create final chunk
        if current_blocks:
            chunk = self._create_chunk_from_blocks_simple(
                current_blocks,
                section.header_path,
                section.start_line,
                config,
                is_oversize=False,
                header_level=section.header_level,
                header_text=section.header_text,
            )
            if chunk:
                chunks.append(chunk)

        # Mark overlap in chunks (Task 5.3)
        if config.enable_overlap and len(chunks) > 1:
            self._mark_overlap_in_chunks(chunks)

        return chunks

    def _create_chunk_from_blocks_simple(
        self,
        blocks,
        section_path,
        base_line,
        config,
        is_oversize: bool = False,
        oversize_reason: str = None,
        header_level: int = None,
        header_text: str = None,
    ) -> Optional[Chunk]:
        """
        Create chunk from list of blocks (Phase 2 Task 5.1).

        Args:
            blocks: List of LogicalBlock objects
            section_path: Section path for metadata
            base_line: Base line number
            config: Chunking configuration
            is_oversize: Whether chunk exceeds max_chunk_size
            oversize_reason: Reason for oversize (e.g., "atomic_block")
            header_level: Header level for compatibility with Phase 1 tests
            header_text: Header text for compatibility with Phase 1 tests

        Returns:
            Chunk object or None if no content
        """
        if not blocks:
            return None

        # Use text normalizer to join content blocks properly
        from ..text_normalizer import join_content_blocks

        content_parts = [block.content for block in blocks]
        try:
            content = join_content_blocks(content_parts, separator="\n\n")
        except ValueError as e:
            # Fallback to simple join if validation fails
            logger.warning(
                f"Content block joining validation failed: {e}. Using simple join."
            )
            content = "\n\n".join(content_parts)

        start_line = min(block.start_line for block in blocks)
        end_line = max(block.end_line for block in blocks)

        # Detect content types
        has_code = any(b.block_type == "code" for b in blocks)
        has_table = any(b.block_type == "table" for b in blocks)
        has_list = any(b.block_type == "list" for b in blocks)

        # Detect links using URLDetector
        has_links = False
        try:
            from ..url_detector import URLDetector

            detector = URLDetector()
            has_links = detector.has_urls(content)
        except Exception:
            # Fallback to simple detection
            has_links = bool(re.search(r"https?://|www\.|\[.+\]\(.+\)", content))

        metadata = {
            "content_type": "section",
            "strategy": self.name,
            "section_path": section_path,
            "start_offset": min(block.start_offset for block in blocks),
            "end_offset": max(block.end_offset for block in blocks),
            "block_ids": [block.metadata.get("id") for block in blocks],
            "has_code": has_code,
            "has_table": has_table,
            "has_list": has_list,
            "has_links": has_links,
            "is_oversize": is_oversize,
            "oversize": is_oversize,  # For backward compatibility
            "allow_oversize": is_oversize,  # For test compatibility
            "has_overlap": False,  # Will be set later if needed
        }

        # Add header metadata for Phase 1 test compatibility
        if header_level is not None:
            metadata["header_level"] = header_level
        if header_text is not None:
            metadata["header_text"] = header_text
        # Filter out empty strings from section_path before creating path string
        if section_path:
            filtered_path = [p for p in section_path if p and p.strip()]
            if filtered_path:
                metadata["header_path"] = "/" + "/".join(filtered_path)

        if is_oversize and oversize_reason:
            metadata["oversize_reason"] = oversize_reason

        # Generate stable section ID
        if section_path:
            filtered_path = [p for p in section_path if p and p.strip()]
            if filtered_path:
                section_id = "-".join(filtered_path).lower()
                section_id = re.sub(r"[^a-z0-9-]", "-", section_id)
                section_id = re.sub(r"-+", "-", section_id).strip("-")
                if section_id:
                    metadata["section_id"] = section_id

        return Chunk(
            content=content, start_line=start_line, end_line=end_line, metadata=metadata
        )

    def _get_overlap_blocks(self, previous_blocks, overlap_size: int):
        """
        Get blocks from end of previous chunk for overlap (Phase 2 Task 5.2).

        Returns complete blocks that fit within overlap_size.

        Args:
            previous_blocks: List of blocks from previous chunk
            overlap_size: Maximum size for overlap in characters

        Returns:
            List of blocks to use as overlap
        """
        overlap_blocks = []
        current_size = 0

        # Take blocks from end until we reach overlap_size
        for block in reversed(previous_blocks):
            block_size = len(block.content)
            if current_size + block_size <= overlap_size:
                overlap_blocks.insert(0, block)
                current_size += block_size
            else:
                break

        return overlap_blocks

    def _mark_overlap_in_chunks(self, chunks: List[Chunk]):
        """
        Mark which parts of chunks are overlap (Phase 2 Task 5.3).

        Requirement 7.5: Metadata SHALL indicate which part is overlap vs new content.

        Args:
            chunks: List of chunks to mark
        """
        for i in range(1, len(chunks)):
            current_chunk = chunks[i]
            prev_chunk = chunks[i - 1]

            # Get block IDs to identify overlap
            current_block_ids = current_chunk.metadata.get("block_ids", [])
            prev_block_ids = prev_chunk.metadata.get("block_ids", [])

            # Find overlapping block IDs
            overlap_block_ids = []
            for block_id in current_block_ids:
                if block_id in prev_block_ids:
                    overlap_block_ids.append(block_id)

            if overlap_block_ids:
                current_chunk.metadata["has_overlap"] = True
                current_chunk.metadata["overlap_block_ids"] = overlap_block_ids

                # Calculate overlap_start_offset
                # This is the offset where new (non-overlap) content begins
                # For simplicity, we estimate based on number of overlap blocks
                overlap_ratio = (
                    len(overlap_block_ids) / len(current_block_ids)
                    if current_block_ids
                    else 0
                )
                content_length = len(current_chunk.content)
                estimated_overlap_size = int(content_length * overlap_ratio)

                current_chunk.metadata["overlap_start_offset"] = 0
                current_chunk.metadata["new_content_start_offset"] = (
                    estimated_overlap_size
                )
            else:
                current_chunk.metadata["has_overlap"] = False

    def _merge_small_chunks(
        self, chunks: List[Chunk], config: ChunkConfig
    ) -> List[Chunk]:
        """
        Merge chunks that don't meet minimum content threshold (Phase 2 Task 8.1).

        Requirements 6.3, 6.4: Ensure chunks have meaningful content.

        Args:
            chunks: List of chunks to process
            config: Chunking configuration

        Returns:
            List of chunks with small chunks merged
        """
        if not chunks or config.min_content_per_chunk <= 0:
            return chunks

        merged = []
        i = 0

        while i < len(chunks):
            current = chunks[i]
            content_size = self._calculate_content_size(current.content)

            # Check if chunk meets minimum content threshold
            if content_size < config.min_content_per_chunk and i + 1 < len(chunks):
                # Try to merge with next chunk if they're in same section
                next_chunk = chunks[i + 1]

                if self._can_merge_chunks(current, next_chunk, config):
                    # Merge current and next
                    merged_chunk = self._merge_two_chunks(current, next_chunk)
                    merged.append(merged_chunk)
                    i += 2  # Skip next chunk
                else:
                    # Can't merge, keep as is (even if small)
                    merged.append(current)
                    i += 1
            else:
                # Chunk is large enough
                merged.append(current)
                i += 1

        return merged

    def _calculate_content_size(self, content: str) -> int:
        """
        Calculate actual content size excluding headers and markup (Phase 2 Task 8.2).

        This counts only meaningful text, not structural elements.

        Args:
            content: Chunk content

        Returns:
            Size of actual content in characters
        """
        lines = content.split("\n")
        content_lines = [
            line for line in lines if line.strip() and not line.strip().startswith("#")
        ]
        return sum(len(line) for line in content_lines)

    def _can_merge_chunks(
        self, chunk1: Chunk, chunk2: Chunk, config: ChunkConfig
    ) -> bool:
        """
        Check if two chunks can be merged without violating constraints.
        (Phase 2 Task 8.3)

        Args:
            chunk1: First chunk
            chunk2: Second chunk
            config: Chunking configuration

        Returns:
            True if chunks can be merged, False otherwise
        """
        # Must be from same section
        path1 = chunk1.get_section_path()
        path2 = chunk2.get_section_path()
        if path1 != path2:
            return False

        # Combined size must not exceed max (unless already oversize)
        is_oversize1 = chunk1.get_metadata("is_oversize", False)
        is_oversize2 = chunk2.get_metadata("is_oversize", False)

        if not (is_oversize1 or is_oversize2):
            combined_size = len(chunk1.content) + len(chunk2.content)
            if combined_size > config.max_chunk_size * 1.5:  # Allow some flexibility
                return False

        return True

    def _merge_two_chunks(self, chunk1: Chunk, chunk2: Chunk) -> Chunk:
        """
        Merge two chunks into one (Phase 2 Task 8.3).

        Args:
            chunk1: First chunk
            chunk2: Second chunk

        Returns:
            Merged chunk
        """
        # Combine content
        combined_content = chunk1.content + "\n\n" + chunk2.content

        # Merge metadata
        merged_metadata = chunk1.metadata.copy()
        merged_metadata["end_offset"] = chunk2.get_metadata("end_offset")

        # Merge block IDs
        block_ids1 = chunk1.get_metadata("block_ids", [])
        block_ids2 = chunk2.get_metadata("block_ids", [])
        merged_metadata["block_ids"] = block_ids1 + block_ids2

        # Update boolean flags (OR operation)
        merged_metadata["has_code"] = chunk1.get_metadata(
            "has_code", False
        ) or chunk2.get_metadata("has_code", False)
        merged_metadata["has_table"] = chunk1.get_metadata(
            "has_table", False
        ) or chunk2.get_metadata("has_table", False)
        merged_metadata["has_list"] = chunk1.get_metadata(
            "has_list", False
        ) or chunk2.get_metadata("has_list", False)
        merged_metadata["has_links"] = chunk1.get_metadata(
            "has_links", False
        ) or chunk2.get_metadata("has_links", False)

        return Chunk(
            content=combined_content,
            start_line=chunk1.start_line,
            end_line=chunk2.end_line,
            metadata=merged_metadata,
        )
