"""
Output filter for hierarchical chunking results.

Filters hierarchical output for downstream consumers (vector DB, indexers)
to prevent accidental indexing of technical nodes (root, internal nodes).

CRITICAL CHANGE in 0.1.3:
- _add_indexable_field() uses setdefault() - respects library value
- _filter_for_indexing() uses indexable field, not just is_leaf
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class FilterConfig:
    """Configuration for output filtering."""

    leaf_only: bool = False  # Return only leaf chunks
    add_indexable: bool = True  # Add indexable field to metadata


class OutputFilter:
    """Filters hierarchical output for downstream consumers."""

    def __init__(self, config: FilterConfig | None = None) -> None:
        self.config = config or FilterConfig()

    def filter(
        self, chunks: list[dict[str, Any]], debug: bool = False
    ) -> list[dict[str, Any]]:
        """
        Filter chunks for indexing.

        Args:
            chunks: Raw result from chunkana
            debug: Include all chunks for debugging

        Returns:
            Filtered list of chunks with indexable field
        """
        # Add indexable field (respecting library value)
        chunks = self._add_indexable_field(chunks)

        if debug:
            return chunks  # All chunks for debugging

        # Exclude root chunk
        chunks = [
            c for c in chunks if not c.get("metadata", {}).get("is_root", False)
        ]

        # Optionally: filter for indexing (uses indexable, not just is_leaf)
        if self.config.leaf_only:
            chunks = self._filter_for_indexing(chunks)

        return chunks

    def _add_indexable_field(
        self, chunks: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Add indexable field to metadata, RESPECTING library value.

        CRITICAL: Uses setdefault() - does NOT overwrite if already set.

        - If library set indexable: respect it
        - If not set:
          - Root: indexable=False
          - Leaf: indexable=True
          - Non-leaf: indexable=True if has significant content
        """
        for chunk in chunks:
            metadata = chunk.get("metadata", {})

            # CRITICAL: setdefault, not overwrite!
            if "indexable" not in metadata:
                is_root = metadata.get("is_root", False)
                is_leaf = metadata.get("is_leaf", True)

                if is_root:
                    metadata["indexable"] = False
                elif is_leaf:
                    metadata["indexable"] = True
                else:
                    # Non-leaf: indexable if has significant content
                    metadata["indexable"] = self._has_significant_content(chunk)

            chunk["metadata"] = metadata

        return chunks

    def _filter_for_indexing(
        self, chunks: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Filter for indexing.

        Includes chunks with indexable=True (not just is_leaf=True).
        This ensures non-leaf chunks with significant content are included.
        """
        return [c for c in chunks if c.get("metadata", {}).get("indexable", True)]

    def _has_significant_content(self, chunk: dict[str, Any]) -> bool:
        """Check if chunk has >100 chars of non-header content."""
        content = chunk.get("content", "").strip()
        if not content:
            return False

        lines = content.split("\n")
        non_header_lines = [line for line in lines if not line.strip().startswith("#")]
        non_header_content = "\n".join(non_header_lines).strip()

        return len(non_header_content) > 100
