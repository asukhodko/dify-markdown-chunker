"""
Input validator for chunkana library output.

Validates and fixes data from the library to ensure resilience
to library changes and missing fields.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class InputValidator:
    """Validates and fixes data from chunkana library."""

    def validate_and_fix(
        self, chunks: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Validate chunks and set default values for missing fields.

        Args:
            chunks: Raw chunks from chunkana

        Returns:
            Validated chunks with defaults applied
        """
        for i, chunk in enumerate(chunks):
            metadata = chunk.get("metadata", {})

            # Set default for is_leaf if missing
            if "is_leaf" not in metadata:
                metadata["is_leaf"] = True
                logger.warning(
                    f"[ChunkanaAdapter] Chunk {i} missing is_leaf, defaulting to True"
                )

            # Set default for is_root if missing
            if "is_root" not in metadata:
                metadata["is_root"] = False

            chunk["metadata"] = metadata

        return chunks
