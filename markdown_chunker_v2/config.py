"""
Simplified configuration for markdown_chunker v2.

Only 8 core parameters instead of 32.
"""

import warnings
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ChunkConfig:
    """
    Configuration for markdown chunking.
    
    Simplified from 32 parameters to 8 core parameters.
    All MC-* bugfix behaviors are now enabled by default.
    
    Attributes:
        max_chunk_size: Maximum size of a chunk in characters (default: 4096)
        min_chunk_size: Minimum size of a chunk in characters (default: 512)
        overlap_size: Size of overlap between chunks (0 = disabled, default: 200)
        preserve_atomic_blocks: Keep code blocks and tables intact (default: True)
        extract_preamble: Extract content before first header as preamble (default: True)
        code_threshold: Code ratio threshold for CodeAwareStrategy (default: 0.3)
        structure_threshold: Min headers for StructuralStrategy (default: 3)
        strategy_override: Force specific strategy (default: None)
    """
    
    # Size parameters
    max_chunk_size: int = 4096
    min_chunk_size: int = 512
    overlap_size: int = 200
    
    # Behavior parameters
    preserve_atomic_blocks: bool = True
    extract_preamble: bool = True
    
    # Strategy selection thresholds
    code_threshold: float = 0.3
    structure_threshold: int = 3
    
    # Override
    strategy_override: Optional[str] = None
    
    def __post_init__(self):
        """Validate configuration."""
        if self.max_chunk_size <= 0:
            raise ValueError(f"max_chunk_size must be positive, got {self.max_chunk_size}")
        
        if self.min_chunk_size <= 0:
            raise ValueError(f"min_chunk_size must be positive, got {self.min_chunk_size}")
        
        if self.min_chunk_size > self.max_chunk_size:
            # Auto-adjust instead of error
            self.min_chunk_size = self.max_chunk_size // 2
        
        if self.overlap_size < 0:
            raise ValueError(f"overlap_size must be non-negative, got {self.overlap_size}")
        
        if self.overlap_size >= self.max_chunk_size:
            raise ValueError(f"overlap_size ({self.overlap_size}) must be less than max_chunk_size ({self.max_chunk_size})")
        
        if not 0 <= self.code_threshold <= 1:
            raise ValueError(f"code_threshold must be between 0 and 1, got {self.code_threshold}")
        
        if self.structure_threshold < 1:
            raise ValueError(f"structure_threshold must be >= 1, got {self.structure_threshold}")
        
        if self.strategy_override is not None:
            valid_strategies = {"code_aware", "structural", "fallback"}
            if self.strategy_override not in valid_strategies:
                raise ValueError(f"strategy_override must be one of {valid_strategies}, got {self.strategy_override}")
    
    @property
    def enable_overlap(self) -> bool:
        """Whether overlap is enabled."""
        return self.overlap_size > 0
    
    @classmethod
    def from_legacy(cls, **kwargs) -> "ChunkConfig":
        """
        Create config from legacy parameters with deprecation warnings.
        
        Maps old parameter names to new ones and ignores removed parameters.
        """
        # Parameter mapping: old_name -> new_name
        param_mapping = {
            "max_size": "max_chunk_size",
            "min_size": "min_chunk_size",
        }
        
        # Parameters that are removed (always enabled or removed)
        removed_params = {
            "enable_overlap",  # Use overlap_size > 0
            "block_based_splitting",  # Always enabled
            "preserve_code_blocks",  # Always enabled
            "preserve_tables",  # Always enabled
            "enable_deduplication",  # Removed
            "enable_regression_validation",  # Removed
            "enable_header_path_validation",  # Removed
            "use_enhanced_parser",  # Always enabled
            "use_legacy_overlap",  # Removed
            "enable_block_overlap",  # Use overlap_size > 0
            "enable_sentence_splitting",  # Removed
            "enable_paragraph_merging",  # Removed
            "enable_list_preservation",  # Always enabled
            "enable_metadata_enrichment",  # Always enabled
            "enable_size_normalization",  # Removed
            "enable_fallback_strategy",  # Always enabled
        }
        
        new_kwargs = {}
        
        for key, value in kwargs.items():
            if key in removed_params:
                warnings.warn(
                    f"Parameter '{key}' is deprecated and ignored in v2.0. "
                    f"See MIGRATION.md for details.",
                    DeprecationWarning,
                    stacklevel=2
                )
            elif key in param_mapping:
                new_key = param_mapping[key]
                warnings.warn(
                    f"Parameter '{key}' is renamed to '{new_key}' in v2.0.",
                    DeprecationWarning,
                    stacklevel=2
                )
                new_kwargs[new_key] = value
            else:
                new_kwargs[key] = value
        
        return cls(**new_kwargs)
    
    @classmethod
    def default(cls) -> "ChunkConfig":
        """Create default configuration."""
        return cls()
    
    @classmethod
    def for_code_heavy(cls) -> "ChunkConfig":
        """Configuration optimized for code-heavy documents."""
        return cls(
            max_chunk_size=8192,
            min_chunk_size=1024,
            overlap_size=100,
            code_threshold=0.2,
        )
    
    @classmethod
    def for_structured(cls) -> "ChunkConfig":
        """Configuration optimized for structured documents."""
        return cls(
            max_chunk_size=4096,
            min_chunk_size=512,
            overlap_size=200,
            structure_threshold=2,
        )
    
    @classmethod
    def minimal(cls) -> "ChunkConfig":
        """Minimal configuration with small chunks."""
        return cls(
            max_chunk_size=1024,
            min_chunk_size=256,
            overlap_size=50,
        )
    
    def to_dict(self) -> dict:
        """
        Serialize config to dictionary.
        
        Returns:
            Dictionary with all config parameters including computed properties.
        """
        return {
            "max_chunk_size": self.max_chunk_size,
            "min_chunk_size": self.min_chunk_size,
            "overlap_size": self.overlap_size,
            "preserve_atomic_blocks": self.preserve_atomic_blocks,
            "extract_preamble": self.extract_preamble,
            "code_threshold": self.code_threshold,
            "structure_threshold": self.structure_threshold,
            "strategy_override": self.strategy_override,
            "enable_overlap": self.enable_overlap,  # computed property
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ChunkConfig":
        """
        Create config from dictionary.
        
        Handles legacy parameters and uses defaults for missing keys.
        
        Args:
            data: Dictionary with config parameters
            
        Returns:
            ChunkConfig instance
        """
        config_data = data.copy()
        
        # Handle legacy enable_overlap parameter
        if "enable_overlap" in config_data:
            enable = config_data.pop("enable_overlap")
            if enable and "overlap_size" not in config_data:
                config_data["overlap_size"] = 200  # default
            elif not enable:
                config_data["overlap_size"] = 0
        
        # Remove unknown parameters
        valid_params = {
            "max_chunk_size", "min_chunk_size", "overlap_size",
            "preserve_atomic_blocks", "extract_preamble",
            "code_threshold", "structure_threshold", "strategy_override"
        }
        config_data = {k: v for k, v in config_data.items() if k in valid_params}
        
        return cls(**config_data)
