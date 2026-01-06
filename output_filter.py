"""
Output filter for hierarchical chunking results.

Filters hierarchical output for downstream consumers (vector DB, indexers)
to prevent accidental indexing of technical nodes (root, internal nodes).
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
        # Add indexable field to all chunks
        chunks = self._add_indexable_field(chunks)

        if debug:
            return chunks  # All chunks for debugging

        # Exclude root chunk
        chunks = [
            c for c in chunks if not c.get("metadata", {}).get("is_root", False)
        ]

        # Optionally: only leaf chunks
        if self.config.leaf_only:
            chunks = [
                c for c in chunks if c.get("metadata", {}).get("is_leaf", True)
            ]

        return chunks

    def _add_indexable_field(
        self, chunks: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Add indexable field to metadata of each chunk.

        - Root: indexable=False
        - Leaf: indexable=True
        - Internal: indexable=True (contains meaningful content)
        """
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            is_root = metadata.get("is_root", False)
            # Root is not indexable, everything else is
            metadata["indexable"] = not is_root
            chunk["metadata"] = metadata

        return chunks
