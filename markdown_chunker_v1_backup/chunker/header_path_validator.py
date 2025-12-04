"""Header path validator for consistent metadata.

Ensures all chunks have complete, consistent header paths (MC-006 fix).
"""

import re
from typing import List

from markdown_chunker.chunker.types import Chunk


class HeaderPathValidator:
    """Ensure all chunks have complete, consistent header path metadata."""

    def validate_and_fix_paths(self, chunks: List[Chunk]) -> List[Chunk]:
        """Validate and fix header paths for all chunks.

        Args:
            chunks: List of chunks to validate

        Returns:
            List of chunks with validated/fixed paths
        """
        fixed_chunks = []

        for chunk in chunks:
            fixed_chunk = self._ensure_complete_path(chunk)
            fixed_chunk = self._assign_preamble_path(fixed_chunk)
            fixed_chunk = self._generate_section_id(fixed_chunk)
            fixed_chunks.append(fixed_chunk)

        return fixed_chunks

    def _ensure_complete_path(self, chunk: Chunk) -> Chunk:
        """Ensure chunk has complete header path with no missing levels.

        Args:
            chunk: Chunk to validate

        Returns:
            Chunk with complete path
        """
        section_path = chunk.metadata.get("section_path", [])

        if not section_path:
            # No path - might be preamble or unstructured content
            return chunk

        # Filter out None and empty strings
        clean_path = [p for p in section_path if p and p.strip()]

        if clean_path != section_path:
            # Path had gaps - fix it
            new_metadata = chunk.metadata.copy()
            new_metadata["section_path"] = clean_path

            # Update header_path string representation
            if clean_path:
                new_metadata["header_path"] = "/" + "/".join(clean_path)

            return Chunk(
                content=chunk.content,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                metadata=new_metadata,
            )

        return chunk

    def _assign_preamble_path(self, chunk: Chunk) -> Chunk:
        """Assign synthetic path to preamble chunks.

        Args:
            chunk: Chunk to check

        Returns:
            Chunk with preamble path if applicable
        """
        # Check if chunk has preamble content
        has_preamble = chunk.metadata.get("has_preamble", False)
        section_path = chunk.metadata.get("section_path", [])

        # If has preamble or no section path and starts before first header
        if has_preamble or (not section_path and chunk.start_line == 1):
            new_metadata = chunk.metadata.copy()
            new_metadata["is_preamble"] = True
            new_metadata["section_path"] = ["__preamble__"]
            new_metadata["header_path"] = "/__preamble__"
            new_metadata["section_id"] = "preamble"

            return Chunk(
                content=chunk.content,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                metadata=new_metadata,
            )

        return chunk

    def _generate_section_id(self, chunk: Chunk) -> Chunk:
        """Generate stable section ID from path.

        Args:
            chunk: Chunk to generate ID for

        Returns:
            Chunk with section_id
        """
        section_path = chunk.metadata.get("section_path", [])

        if not section_path:
            return chunk

        if chunk.metadata.get("section_id"):
            # Already has ID
            return chunk

        # Generate ID from path
        section_id = "-".join(section_path).lower()
        section_id = re.sub(r"[^a-z0-9-]", "-", section_id)
        section_id = re.sub(r"-+", "-", section_id).strip("-")

        if section_id:
            new_metadata = chunk.metadata.copy()
            new_metadata["section_id"] = section_id

            return Chunk(
                content=chunk.content,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                metadata=new_metadata,
            )

        return chunk
