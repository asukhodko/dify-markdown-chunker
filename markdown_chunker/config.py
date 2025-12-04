"""
Configuration module for markdown chunker v2.0.

Simplified from 32 parameters to 8 essential parameters,
eliminating configuration explosion and decision paralysis.
"""

from dataclasses import dataclass

from .types import ConfigurationError


@dataclass
class ChunkConfig:
    """
    Chunking configuration with 8 essential parameters.

    Size Constraints (3 parameters):
        max_chunk_size: Maximum chunk size in characters
        min_chunk_size: Minimum chunk size in characters
        overlap_size: Overlap size between chunks (0 = disabled)

    Behavior Flags (3 parameters):
        preserve_atomic_blocks: Keep code blocks and tables intact
        extract_preamble: Extract document preamble
        allow_oversize: Allow atomic blocks to exceed max size

    Strategy Thresholds (2 parameters):
        code_threshold: Code ratio threshold for CodeAwareStrategy
        structure_threshold: Minimum header count for StructuralStrategy
    """

    # Size constraints (3)
    max_chunk_size: int = 4096
    min_chunk_size: int = 512
    overlap_size: int = 200

    # Behavior flags (3)
    preserve_atomic_blocks: bool = True
    extract_preamble: bool = True
    allow_oversize: bool = True

    # Strategy thresholds (2)
    code_threshold: float = 0.3
    structure_threshold: int = 3

    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        # Size constraints validation
        if self.max_chunk_size < self.min_chunk_size:
            raise ConfigurationError(
                f"max_chunk_size ({self.max_chunk_size}) must be >= "
                f"min_chunk_size ({self.min_chunk_size})"
            )

        if self.min_chunk_size < 1:
            raise ConfigurationError(
                f"min_chunk_size must be >= 1, got {self.min_chunk_size}"
            )

        if self.overlap_size < 0:
            raise ConfigurationError(
                f"overlap_size must be >= 0, got {self.overlap_size}"
            )

        if self.overlap_size >= self.max_chunk_size:
            raise ConfigurationError(
                f"overlap_size ({self.overlap_size}) must be < "
                f"max_chunk_size ({self.max_chunk_size})"
            )

        # Strategy threshold validation
        if not 0.0 <= self.code_threshold <= 1.0:
            raise ConfigurationError(
                f"code_threshold must be in [0.0, 1.0], " f"got {self.code_threshold}"
            )

        if self.structure_threshold < 1:
            raise ConfigurationError(
                f"structure_threshold must be >= 1, " f"got {self.structure_threshold}"
            )

    @classmethod
    def default(cls) -> "ChunkConfig":
        """
        Default configuration for general markdown.

        Balanced settings suitable for most documents.
        """
        return cls()

    @classmethod
    def for_code_docs(cls) -> "ChunkConfig":
        """
        Optimized for technical documentation with code.

        Features:
        - Larger chunks (6144) to accommodate code blocks
        - Lower code threshold (0.2) for more sensitive detection
        - Larger overlap (300) for better code context
        """
        return cls(
            max_chunk_size=6144,
            code_threshold=0.2,
            overlap_size=300,
        )

    @classmethod
    def for_rag(cls) -> "ChunkConfig":
        """
        Optimized for RAG/embedding systems.

        Features:
        - Smaller chunks (2048) for embedding limits
        - Moderate overlap (150) for context preservation
        """
        return cls(
            max_chunk_size=2048,
            overlap_size=150,
        )

    @property
    def target_chunk_size(self) -> int:
        """
        Derived target size (midpoint between min and max).

        This replaces the removed target_chunk_size parameter.
        """
        return (self.min_chunk_size + self.max_chunk_size) // 2

    @property
    def min_effective_chunk_size(self) -> int:
        """
        Derived minimum effective size (40% of max).

        This incorporates the MC-004 fix as default behavior.
        """
        return int(self.max_chunk_size * 0.4)

    @property
    def overlap_enabled(self) -> bool:
        """Check if overlap is enabled."""
        return self.overlap_size > 0

    def __repr__(self) -> str:
        """Readable representation of configuration."""
        return (
            f"ChunkConfig(max={self.max_chunk_size}, "
            f"min={self.min_chunk_size}, "
            f"overlap={self.overlap_size}, "
            f"code_threshold={self.code_threshold}, "
            f"structure_threshold={self.structure_threshold})"
        )
