"""
MetadataEnricher - Enriches chunk metadata with comprehensive information.
This component adds strategy-specific and general metadata to chunks to improve
their usability and searchability.
"""

import re
from typing import Any, Dict, List, Optional

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
