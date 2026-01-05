#!/usr/bin/env python3
"""Migration adapter for dify-markdown-chunker to chunkana 0.1.1.

This adapter provides compatibility layer between the plugin's tool interface
and the chunkana library, ensuring exact behavioral compatibility.

New in chunkana 0.1.1:
- Tree invariant validation (validate_invariants=True by default)
- Auto-fix mode for hierarchical issues (strict_mode=False by default)
- Dangling header prevention
- Micro-chunk minimization
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from chunkana import (
    ChunkerConfig,
    chunk_hierarchical,
    chunk_markdown,
    render_dify_style,
    render_with_embedded_overlap,
)


class MigrationAdapter:
    """Adapter to migrate from embedded markdown_chunker to chunkana 0.1.1.
    
    Features enabled by default:
    - validate_invariants=True: Validates tree structure in hierarchical mode
    - strict_mode=False: Auto-fixes issues instead of raising exceptions
    """

    def __init__(self):
        """Initialize adapter with captured config defaults."""
        self._config_defaults = self._load_config_defaults()

    def _load_config_defaults(self) -> Dict[str, Any]:
        """Load actual config defaults from pre-migration snapshot."""
        config_file = Path(__file__).parent / "tests" / "config_defaults_snapshot.json"

        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("defaults", {})

        # Fallback if snapshot not found (should not happen in normal migration)
        return {}

    def build_chunker_config(
        self,
        max_chunk_size: int = 4096,
        chunk_overlap: int = 200,
        strategy: str = "auto",
    ) -> ChunkerConfig:
        """Build ChunkerConfig from tool parameters.

        Maps tool parameters to ChunkerConfig fields with proper type conversion
        using captured defaults from pre-migration analysis.
        """
        # Map strategy parameter ("auto" -> None)
        strategy_override = None if strategy == "auto" else strategy

        # Use captured defaults for all other fields
        config_dict = self._config_defaults.copy()

        # Override with explicit parameters
        config_dict.update(
            {
                "max_chunk_size": max_chunk_size,
                "overlap_size": chunk_overlap,
                "strategy_override": strategy_override,
                # chunkana 0.1.1: Enable tree validation with auto-fix
                "validate_invariants": True,
                "strict_mode": False,
            }
        )

        # Filter out parameters not supported by ChunkerConfig constructor
        # enable_overlap is a computed property, not a constructor parameter
        unsupported_params = {"enable_overlap"}
        filtered_config = {
            k: v for k, v in config_dict.items() if k not in unsupported_params
        }

        return ChunkerConfig(**filtered_config)

    def parse_tool_flags(
        self,
        include_metadata: bool = True,
        enable_hierarchy: bool = False,
        debug: bool = False,
    ) -> Tuple[bool, bool, bool]:
        """Extract control flags from tool parameters.

        Returns:
            Tuple of (include_metadata, enable_hierarchy, debug)
        """
        return include_metadata, enable_hierarchy, debug

    def run_chunking(
        self,
        input_text: str,
        config: ChunkerConfig,
        include_metadata: bool = True,
        enable_hierarchy: bool = False,
        debug: bool = False,
    ) -> List[str]:
        """Run chunking with exact pre-migration behavior.

        This method replicates the exact logic from the original tool
        implementation.

        Debug behavior (based on pre-migration analysis):
        - enable_hierarchy=True, debug=True: returns result.chunks
          (ALL chunks - root, intermediate, leaf)
        - enable_hierarchy=True, debug=False: returns result.get_flat_chunks()
          (LEAF chunks only)
        - enable_hierarchy=False: debug flag ignored, returns regular chunks
        """
        # API selection logic (same as original tool)
        if enable_hierarchy:
            result = chunk_hierarchical(input_text, config)

            # Debug behavior: exact replication of original logic
            if debug:
                chunks = result.chunks  # All chunks including root/intermediate
            else:
                chunks = result.get_flat_chunks()  # Leaf chunks only
        else:
            chunks = chunk_markdown(input_text, config)

        # Format results (same logic as original tool)
        if include_metadata:
            # Metadata mode: use dify-style renderer with optional filtering
            if debug:
                # Debug mode: use raw dify-style renderer (no metadata filtering)
                formatted_result = render_dify_style(chunks)
            else:
                # Normal mode: filter metadata for RAG, then render manually
                formatted_result = []
                for chunk in chunks:
                    content = chunk.content
                    metadata = chunk.metadata or {}

                    # Filter metadata for RAG
                    output_metadata = self._filter_metadata_for_rag(metadata)
                    output_metadata["start_line"] = chunk.start_line
                    output_metadata["end_line"] = chunk.end_line

                    # Manual dify-style rendering with filtered metadata
                    metadata_json = json.dumps(
                        output_metadata, ensure_ascii=False, indent=2
                    )
                    formatted_chunk = (
                        f"<metadata>\n{metadata_json}\n</metadata>\n{content}"
                    )
                    formatted_result.append(formatted_chunk)
        else:
            # Clean mode: use embedded overlap renderer
            formatted_result = render_with_embedded_overlap(chunks)

        return formatted_result

    def _filter_metadata_for_rag(self, metadata: dict) -> dict:
        """Filter metadata to keep only fields useful for RAG search.

        This preserves the exact filtering logic from the original tool.
        """
        # Fields to EXCLUDE (not useful for RAG)
        excluded_fields = {
            # Statistical fields
            "avg_line_length",
            "avg_word_length",
            "char_count",
            "line_count",
            "size_bytes",
            "word_count",
            # Count fields
            "item_count",
            "nested_item_count",
            "unordered_item_count",
            "ordered_item_count",
            "max_nesting",
            "task_item_count",
            # Internal/execution fields
            "execution_fallback_level",
            "execution_fallback_used",
            "execution_strategy_used",
            # Preamble internal fields
            "preamble.char_count",
            "preamble.line_count",
            "preamble.has_metadata",
            "preamble.metadata_fields",
            "preamble.type",
            # Redundant fields
            "preamble_type",
            "preview",
            "total_chunks",
        }

        filtered = {}
        for key, value in metadata.items():
            if key in excluded_fields:
                continue

            # Skip is_leaf, is_root unless debug
            if key in {"is_leaf", "is_root"}:
                continue

            # Skip other is_*/has_* fields with False values
            if (key.startswith("is_") or key.startswith("has_")) and not value:
                continue

            filtered[key] = value

        return filtered
