"""
MetadataEnricher - Enriches chunk metadata with comprehensive information.
This component adds strategy-specific and general metadata to chunks to improve
their usability and searchability.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from ..types import Chunk, ChunkConfig


class MetadataEnricher:
    """
    Enriches chunk metadata with comprehensive information.

    This component:
    - Adds general metadata (timestamps, IDs, positions)
    - Enriches strategy-specific metadata
    - Calculates content statistics
    - Adds searchability metadata
    - Validates and normalizes metadata
    """

    def __init__(self, config: ChunkConfig):
        """
        Initialize MetadataEnricher.

        Args:
            config: Chunking configuration
        """
        self.config = config

    def enrich_chunks(
        self,
        chunks: List[Chunk],
        document_id: Optional[str] = None,
        fallback_info: Optional[Dict[str, Any]] = None,
    ) -> List[Chunk]:
        """
        Enrich metadata for all chunks.

        Args:
            chunks: List of chunks to enrich
            document_id: Optional document identifier
            fallback_info: Optional fallback information to include in metadata

        Returns:
            List of chunks with enriched metadata
        """
        if not chunks:
            return chunks

        enriched_chunks = []

        for i, chunk in enumerate(chunks):
            enriched_chunk = self._enrich_single_chunk(
                chunk,
                position=i,
                total_chunks=len(chunks),
                document_id=document_id,
                fallback_info=fallback_info,
            )
            enriched_chunks.append(enriched_chunk)

        return enriched_chunks

    def _enrich_single_chunk(
        self,
        chunk: Chunk,
        position: int,
        total_chunks: int,
        document_id: Optional[str] = None,
        fallback_info: Optional[Dict[str, Any]] = None,
    ) -> Chunk:
        """
        Enrich metadata for a single chunk.

        Args:
            chunk: Chunk to enrich
            position: Position in chunk list (0-based)
            total_chunks: Total number of chunks
            document_id: Optional document identifier
            fallback_info: Optional fallback information to include

        Returns:
            Chunk with enriched metadata
        """
        # Create new metadata dict with existing metadata
        enriched_metadata = chunk.metadata.copy()

        # Add position metadata
        enriched_metadata["chunk_index"] = position
        enriched_metadata["total_chunks"] = total_chunks
        enriched_metadata["is_first_chunk"] = position == 0
        enriched_metadata["is_last_chunk"] = position == total_chunks - 1

        # Add document ID if provided
        if document_id:
            enriched_metadata["document_id"] = document_id

        # Add fallback information if provided
        if fallback_info:
            enriched_metadata["execution_fallback_used"] = fallback_info.get(
                "fallback_used", False
            )
            enriched_metadata["execution_fallback_level"] = fallback_info.get(
                "fallback_level", 0
            )
            enriched_metadata["execution_strategy_used"] = fallback_info.get(
                "strategy_used", "unknown"
            )

        # Add content statistics
        stats = self._calculate_content_statistics(chunk.content)
        enriched_metadata.update(stats)

        # Add strategy-specific enrichment
        strategy = chunk.get_metadata("strategy", "unknown")
        content_type = chunk.get_metadata("content_type", "text")

        if strategy == "code" or content_type == "code":
            enriched_metadata.update(self._enrich_code_metadata(chunk))
        elif strategy == "list" or content_type == "list":
            enriched_metadata.update(self._enrich_list_metadata(chunk))
        elif strategy == "table" or content_type == "table":
            enriched_metadata.update(self._enrich_table_metadata(chunk))
        elif strategy == "structural" or content_type == "structured":
            enriched_metadata.update(self._enrich_structural_metadata(chunk))

        # Add searchability metadata
        enriched_metadata.update(self._add_searchability_metadata(chunk.content))

        # Create new chunk with enriched metadata
        enriched_chunk = Chunk(
            content=chunk.content,
            start_line=chunk.start_line,
            end_line=chunk.end_line,
            metadata=enriched_metadata,
        )

        # Fix header_path based on actual content
        enriched_chunk = self.fix_header_path(enriched_chunk)

        # Fix section paths for multi-section chunks
        enriched_chunk = self.fix_section_paths(enriched_chunk)

        # Fix section_id using consistent slugification
        enriched_chunk = self.fix_section_id(enriched_chunk)

        # Fix overlap metadata
        enriched_chunk = self.fix_overlap_metadata(enriched_chunk)

        return enriched_chunk

    def _calculate_content_statistics(self, content: str) -> Dict[str, Any]:
        """
        Calculate content statistics.

        Args:
            content: Content to analyze

        Returns:
            Dictionary with statistics
        """
        lines = content.split("\n")
        words = content.split()

        return {
            "line_count": len(lines),
            "word_count": len(words),
            "char_count": len(content),
            "avg_line_length": len(content) / len(lines) if lines else 0,
            "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
        }

    def _enrich_code_metadata(self, chunk: Chunk) -> Dict[str, Any]:
        """
        Enrich metadata for code chunks.

        Args:
            chunk: Code chunk

        Returns:
            Additional metadata
        """
        metadata = {}
        content = chunk.content

        # Count code blocks
        code_block_count = content.count("```")
        metadata["code_block_count"] = code_block_count // 2  # Pairs of backticks

        # Check for inline code
        inline_code_count = content.count("`") - code_block_count
        metadata["has_inline_code"] = inline_code_count > 0

        # Detect imports/includes
        has_imports = bool(
            re.search(
                r"\b(import|from|include|require|using)\b", content, re.IGNORECASE
            )
        )
        metadata["has_imports"] = has_imports

        # Detect comments
        has_comments = bool(re.search(r"(//|#|/\*|\*/).*", content))
        metadata["has_comments"] = has_comments

        return metadata

    def _enrich_list_metadata(self, chunk: Chunk) -> Dict[str, Any]:
        """
        Enrich metadata for list chunks.

        Args:
            chunk: List chunk

        Returns:
            Additional metadata
        """
        metadata = {}
        content = chunk.content

        # Count different list types
        ordered_items = len(re.findall(r"^\s*\d+\.", content, re.MULTILINE))
        unordered_items = len(re.findall(r"^\s*[-*+]\s+", content, re.MULTILINE))
        task_items = len(re.findall(r"^\s*[-*+]\s+\[[ xX]\]", content, re.MULTILINE))

        metadata["ordered_item_count"] = ordered_items
        metadata["unordered_item_count"] = unordered_items
        metadata["task_item_count"] = task_items

        # Detect nested lists
        indented_items = len(re.findall(r"^\s{2,}[-*+\d]", content, re.MULTILINE))
        metadata["has_nested_lists"] = indented_items > 0
        metadata["nested_item_count"] = indented_items

        return metadata

    def _enrich_table_metadata(self, chunk: Chunk) -> Dict[str, Any]:
        """
        Enrich metadata for table chunks.

        Args:
            chunk: Table chunk

        Returns:
            Additional metadata
        """
        metadata = {}
        content = chunk.content

        # Count table rows
        table_rows = len(re.findall(r"^\|.+\|$", content, re.MULTILINE))
        metadata["table_row_count"] = table_rows

        # Detect table separators
        separators = len(re.findall(r"^\|[\s:|-]+\|$", content, re.MULTILINE))
        metadata["table_count"] = separators  # One separator per table

        # Check for alignment
        has_alignment = bool(re.search(r"\|[\s]*:?-+:?[\s]*\|", content))
        metadata["has_column_alignment"] = has_alignment

        return metadata

    def _enrich_structural_metadata(self, chunk: Chunk) -> Dict[str, Any]:
        """
        Enrich metadata for structural chunks.

        Args:
            chunk: Structural chunk

        Returns:
            Additional metadata
        """
        metadata = {}
        content = chunk.content

        # Count headers
        headers = re.findall(r"^#{1,6}\s+.+$", content, re.MULTILINE)
        metadata["header_count"] = len(headers)

        if headers:
            # Get header levels
            header_levels = [len(re.match(r"^(#+)", h).group(1)) for h in headers]
            metadata["min_header_level"] = min(header_levels)
            metadata["max_header_level"] = max(header_levels)

        # Count paragraphs (excluding headers)
        paragraphs = [
            p
            for p in content.split("\n\n")
            if p.strip() and not re.match(r"^#{1,6}\s+", p.strip())
        ]
        metadata["paragraph_count"] = len(paragraphs)

        return metadata

    def _add_searchability_metadata(self, content: str) -> Dict[str, Any]:
        """
        Add metadata to improve searchability.

        Args:
            content: Content to analyze

        Returns:
            Searchability metadata
        """
        metadata: Dict[str, Any] = {}

        # Extract first sentence or line as preview
        first_line = content.split("\n")[0].strip()
        if first_line:
            # Limit preview length
            preview = first_line[:200] + "..." if len(first_line) > 200 else first_line
            metadata["preview"] = preview

        # Detect content features
        has_urls = bool(re.search(r"https?://\S+", content))
        has_emails = bool(
            re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", content)
        )
        has_numbers = bool(re.search(r"\d+", content))

        metadata["has_urls"] = has_urls
        metadata["has_emails"] = has_emails
        metadata["has_numbers"] = has_numbers

        # Detect special formatting
        has_bold = bool(re.search(r"\*\*[^*]+\*\*|__[^_]+__", content))
        has_italic = bool(re.search(r"\*[^*]+\*|_[^_]+_", content))
        has_code_inline = bool(re.search(r"`[^`]+`", content))

        metadata["has_bold"] = has_bold
        metadata["has_italic"] = has_italic
        metadata["has_inline_code"] = has_code_inline

        return metadata

    def validate_metadata(self, chunks: List[Chunk]) -> Dict[str, Any]:
        """
        Validate metadata across all chunks.

        Args:
            chunks: List of chunks to validate

        Returns:
            Validation report
        """
        if not chunks:
            return {"valid": True, "issues": []}

        issues = []

        # Check for required metadata fields
        required_fields = ["strategy", "content_type"]

        for i, chunk in enumerate(chunks):
            for field in required_fields:
                if field not in chunk.metadata:
                    issues.append(f"Chunk {i}: Missing required field '{field}'")

        # Check chunk indices
        for i, chunk in enumerate(chunks):
            chunk_index = chunk.get_metadata("chunk_index")
            if chunk_index is not None and chunk_index != i:
                issues.append(f"Chunk {i}: Incorrect chunk_index {chunk_index}")

        # Check total_chunks consistency
        total_chunks_values = set(
            chunk.get_metadata("total_chunks")
            for chunk in chunks
            if chunk.get_metadata("total_chunks") is not None
        )

        if len(total_chunks_values) > 1:
            issues.append(f"Inconsistent total_chunks values: {total_chunks_values}")
        elif total_chunks_values and list(total_chunks_values)[0] != len(chunks):
            issues.append(
                f"total_chunks ({list(total_chunks_values)[0]}) doesn't "
                f"match actual count ({len(chunks)})"
            )

        return {"valid": len(issues) == 0, "issue_count": len(issues), "issues": issues}

    def get_metadata_summary(self, chunks: List[Chunk]) -> Dict[str, Any]:
        """
        Get summary of metadata across all chunks.

        Args:
            chunks: List of chunks to summarize

        Returns:
            Metadata summary
        """
        if not chunks:
            return {"total_chunks": 0}

        # Collect statistics
        strategies: Dict[str, int] = {}
        content_types: Dict[str, int] = {}
        total_words = 0
        total_lines = 0

        for chunk in chunks:
            strategy = chunk.get_metadata("strategy", "unknown")
            strategies[strategy] = strategies.get(strategy, 0) + 1

            content_type = chunk.get_metadata("content_type", "unknown")
            content_types[content_type] = content_types.get(content_type, 0) + 1

            total_words += chunk.get_metadata("word_count", 0)
            total_lines += chunk.get_metadata("line_count", 0)

        return {
            "total_chunks": len(chunks),
            "strategies": strategies,
            "content_types": content_types,
            "total_words": total_words,
            "total_lines": total_lines,
            "avg_words_per_chunk": total_words / len(chunks) if chunks else 0,
            "avg_lines_per_chunk": total_lines / len(chunks) if chunks else 0,
        }

    def _extract_headers_from_content(self, content: str) -> List[Tuple[int, str]]:
        """
        Extract headers from chunk content.

        Args:
            content: Chunk content

        Returns:
            List of (level, header_text) tuples
        """
        headers = []
        for line in content.split("\n"):
            match = re.match(r"^(#{1,6})\s+(.+)$", line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                headers.append((level, text))
        return headers

    def _build_header_path(self, headers: List[Tuple[int, str]]) -> str:
        """
        Build header path from list of headers.

        Creates a hierarchical path based on header levels.

        Args:
            headers: List of (level, header_text) tuples

        Returns:
            Header path string like "/Section/Subsection/Topic"
        """
        if not headers:
            return ""

        # Build path maintaining hierarchy
        path_stack: List[Tuple[int, str]] = []

        for level, text in headers:
            # Remove headers at same or lower level
            while path_stack and path_stack[-1][0] >= level:
                path_stack.pop()
            path_stack.append((level, text))

        # Return the final path in /path/format
        if not path_stack:
            return ""
        return "/" + "/".join(text for _, text in path_stack)

    def fix_header_path(self, chunk: Chunk) -> Chunk:
        """
        Fix header_path metadata based on actual content in the chunk.

        Parses the chunk content to extract real headers and generates
        header_path based on found headers.

        Args:
            chunk: Chunk to fix

        Returns:
            Chunk with corrected header_path metadata
        """
        # Check if header_path is already correctly set (starts with /)
        existing_path = chunk.get_metadata("header_path", "")
        if (
            existing_path
            and isinstance(existing_path, str)
            and existing_path.startswith("/")
        ):
            # header_path is already in correct format, just add headers_in_chunk
            headers = self._extract_headers_from_content(chunk.content)
            if headers:
                new_metadata = chunk.metadata.copy()
                new_metadata["headers_in_chunk"] = [text for _, text in headers]
                new_metadata["header_levels"] = [level for level, _ in headers]
                return Chunk(
                    content=chunk.content,
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    metadata=new_metadata,
                )
            return chunk

        headers = self._extract_headers_from_content(chunk.content)

        if not headers:
            # No headers in content, keep existing or set empty
            return chunk

        # Build header path from actual headers
        header_path = self._build_header_path(headers)

        # Update metadata
        new_metadata = chunk.metadata.copy()
        new_metadata["header_path"] = header_path

        # Also store individual headers for reference
        new_metadata["headers_in_chunk"] = [text for _, text in headers]
        new_metadata["header_levels"] = [level for level, _ in headers]

        return Chunk(
            content=chunk.content,
            start_line=chunk.start_line,
            end_line=chunk.end_line,
            metadata=new_metadata,
        )

    @staticmethod
    def slugify(text: str) -> str:
        """
        Convert text to a consistent slug format.

        This method ensures that identical header texts produce identical
        section_ids across all chunks.

        Args:
            text: Text to slugify (typically a header)

        Returns:
            Slugified text (lowercase, alphanumeric with hyphens)
        """
        if not text:
            return ""

        # Convert to lowercase
        slug = text.lower()

        # Remove markdown formatting (bold, italic, code)
        slug = re.sub(r"\*\*([^*]+)\*\*", r"\1", slug)  # bold
        slug = re.sub(r"\*([^*]+)\*", r"\1", slug)  # italic
        slug = re.sub(r"`([^`]+)`", r"\1", slug)  # inline code
        slug = re.sub(r"__([^_]+)__", r"\1", slug)  # bold alt
        slug = re.sub(r"_([^_]+)_", r"\1", slug)  # italic alt

        # Replace non-alphanumeric characters with hyphens
        slug = re.sub(r"[^a-z0-9]+", "-", slug)

        # Remove leading/trailing hyphens
        slug = slug.strip("-")

        # Collapse multiple hyphens
        slug = re.sub(r"-+", "-", slug)

        return slug

    def generate_section_id(self, header_text: str) -> str:
        """
        Generate a consistent section_id from header text.

        Args:
            header_text: Header text to convert

        Returns:
            Section ID (slugified header)
        """
        return self.slugify(header_text)

    def fix_section_id(self, chunk: Chunk) -> Chunk:
        """
        Fix section_id metadata using consistent slugification.

        Ensures that identical headers produce identical section_ids.

        Args:
            chunk: Chunk to fix

        Returns:
            Chunk with corrected section_id metadata
        """
        headers = self._extract_headers_from_content(chunk.content)

        if not headers:
            return chunk

        new_metadata = chunk.metadata.copy()

        # Generate section_id from the first (primary) header
        primary_header = headers[0][1]  # (level, text) -> text
        section_id = self.generate_section_id(primary_header)

        if section_id:
            new_metadata["section_id"] = section_id

        # Also generate IDs for all headers in chunk
        header_ids = [self.generate_section_id(text) for _, text in headers]
        new_metadata["header_ids"] = header_ids

        return Chunk(
            content=chunk.content,
            start_line=chunk.start_line,
            end_line=chunk.end_line,
            metadata=new_metadata,
        )

    def fix_overlap_metadata(self, chunk: Chunk) -> Chunk:
        """
        Fix overlap_size metadata to reflect actual overlap size.

        If the chunk has overlap, validates that overlap_size matches
        the actual overlap content size.

        Args:
            chunk: Chunk to fix

        Returns:
            Chunk with corrected overlap_size metadata
        """
        has_overlap = chunk.get_metadata("has_overlap", False)

        if not has_overlap:
            return chunk

        # overlap_size should already be set correctly by OverlapManager
        # This method validates and ensures consistency
        overlap_size = chunk.get_metadata("overlap_size", 0)

        new_metadata = chunk.metadata.copy()

        # Ensure overlap_size is an integer
        if not isinstance(overlap_size, int):
            new_metadata["overlap_size"] = int(overlap_size) if overlap_size else 0

        # Add overlap ratio for debugging
        content_size = len(chunk.content)
        if content_size > 0 and overlap_size > 0:
            overlap_ratio = overlap_size / content_size
            new_metadata["overlap_ratio"] = round(overlap_ratio, 3)

        return Chunk(
            content=chunk.content,
            start_line=chunk.start_line,
            end_line=chunk.end_line,
            metadata=new_metadata,
        )

    def fix_section_paths(self, chunk: Chunk) -> Chunk:
        """
        Record all section paths for multi-section chunks.

        If a chunk contains content from multiple sections (multiple top-level
        headers), this method records all section paths in metadata.

        Args:
            chunk: Chunk to fix

        Returns:
            Chunk with section_paths metadata
        """
        headers = self._extract_headers_from_content(chunk.content)

        if not headers:
            return chunk

        min_level = min(level for level, _ in headers)

        # Build section paths for each top-level header
        section_paths: List[str] = []
        current_path_stack: List[Tuple[int, str]] = []

        for level, text in headers:
            # Update path stack
            while current_path_stack and current_path_stack[-1][0] >= level:
                current_path_stack.pop()
            current_path_stack.append((level, text))

            # If this is a top-level header, record the path
            if level == min_level:
                path = "/" + "/".join(t for _, t in current_path_stack)
                if path not in section_paths:
                    section_paths.append(path)

        # Update metadata
        new_metadata = chunk.metadata.copy()

        if len(section_paths) > 1:
            new_metadata["section_paths"] = section_paths
            new_metadata["multi_section"] = True
        elif section_paths:
            new_metadata["section_paths"] = section_paths
            new_metadata["multi_section"] = False

        return Chunk(
            content=chunk.content,
            start_line=chunk.start_line,
            end_line=chunk.end_line,
            metadata=new_metadata,
        )
