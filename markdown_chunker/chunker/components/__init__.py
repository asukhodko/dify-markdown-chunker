"""
Support components for Stage 2 chunking system.

This package contains utility components that support the main chunking
functionality including overlap management, metadata enrichment, and
error handling.
"""

from .fallback_manager import FallbackManager
from .metadata_enricher import MetadataEnricher
from .overlap_manager import OverlapManager

# Other components (will be uncommented as implemented)
# from .chunk_validator import ChunkValidator

__all__ = [
    "FallbackManager",
    "OverlapManager",
    "MetadataEnricher",
    # Other components (to be uncommented as implemented)
    # 'ChunkValidator',
]
