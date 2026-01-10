#!/usr/bin/env python3
"""Migration adapter for dify-markdown-chunker to chunkana 0.1.3.

This adapter provides compatibility layer between the plugin's tool interface
and the chunkana library, ensuring exact behavioral compatibility.

CRITICAL CHANGE in 0.1.3:
- Chunking and rendering are now SEPARATE stages
- _perform_chunking() does NOT depend on include_metadata
- Boundaries are INVARIANT to include_metadata parameter

New in chunkana 0.1.3:
- SectionSplitter with header_stack repetition
- InvariantValidator with recall-based coverage
- Pipeline order fix: dangling fix → section split
- Removed section_integrity oversize reason

New in chunkana 0.1.2:
- Universal dangling header fix (all sections)
- section_tags recalculation after post-processing
- header_moved_from_id tracking with chunk_id (stable)
"""

import json
from pathlib import Path
from typing import Any

from chunkana import (
    ChunkerConfig,
    chunk_hierarchical,
    chunk_markdown,
)

from input_validator import InputValidator
from output_filter import FilterConfig, OutputFilter


# Compatibility alias for legacy tests
MarkdownChunker = None  # Will be set after MigrationAdapter is defined


class MigrationAdapter:
    """Adapter to migrate from embedded markdown_chunker to chunkana 0.1.3.

    CRITICAL: Chunking and rendering are separate stages.
    - _perform_chunking(): Single path, does NOT depend on include_metadata
    - _render_chunks(): Only formatting, does NOT modify boundaries

    Features enabled by default:
    - validate_invariants=True: Validates tree structure in hierarchical mode
    - strict_mode=False: Auto-fixes issues instead of raising exceptions
    """

    def __init__(self, leaf_only: bool = False) -> None:
        """Initialize adapter with captured config defaults.

        Args:
            leaf_only: Return only leaf chunks in hierarchical mode
        """
        self._config_defaults = self._load_config_defaults()
        self._output_filter = OutputFilter(FilterConfig(leaf_only=leaf_only))
        self._input_validator = InputValidator()
        self._leaf_only = leaf_only

    def _load_config_defaults(self) -> dict[str, Any]:
        """Load actual config defaults from pre-migration snapshot."""
        config_file = Path(__file__).parent / "tests" / "config_defaults_snapshot.json"

        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("defaults", {})

        # Fallback if snapshot not found
        return {}

    def build_chunker_config(
        self,
        max_chunk_size: int = 4096,
        chunk_overlap: int = 200,
        strategy: str = "auto",
    ) -> ChunkerConfig:
        """Build ChunkerConfig from tool parameters."""
        strategy_override = None if strategy == "auto" else strategy

        config_dict = self._config_defaults.copy()
        config_dict.update(
            {
                "max_chunk_size": max_chunk_size,
                "overlap_size": chunk_overlap,
                "strategy_override": strategy_override,
                "validate_invariants": True,
                "strict_mode": False,
            }
        )

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
        leaf_only: bool = False,
    ) -> tuple[bool, bool, bool, bool]:
        """Extract control flags from tool parameters."""
        return include_metadata, enable_hierarchy, debug, leaf_only

    def run_chunking(
        self,
        input_text: str,
        config: ChunkerConfig,
        include_metadata: bool = True,
        enable_hierarchy: bool = False,
        debug: bool = False,
    ) -> list[str]:
        """Run chunking with guaranteed boundary invariance.

        CRITICAL: Boundaries do NOT depend on include_metadata.

        Stage 1: Chunking (_perform_chunking)
            - Single path for all include_metadata values
            - Returns raw_chunks (list of dicts)

        Stage 2: Rendering (_render_chunks)
            - Only formatting, does NOT modify boundaries
            - Depends on include_metadata
        """
        # STAGE 1: CHUNKING (does NOT depend on include_metadata)
        raw_chunks = self._perform_chunking(input_text, config, enable_hierarchy, debug)

        # STAGE 2: RENDERING (depends on include_metadata)
        return self._render_chunks(raw_chunks, include_metadata, debug)

    def _perform_chunking(
        self,
        input_text: str,
        config: ChunkerConfig,
        enable_hierarchy: bool,
        debug: bool,
    ) -> list[dict[str, Any]]:
        """Single chunking path - does NOT depend on include_metadata.

        CRITICAL: This method does NOT take include_metadata parameter!
        Returns raw_chunks - list of dicts with content, start_line, end_line, metadata.

        Applies same normalization for hierarchical and non-hierarchical modes.
        """
        if enable_hierarchy:
            result = chunk_hierarchical(input_text, config)

            if debug:
                chunks = result.chunks
            else:
                chunks = result.get_flat_chunks()

            chunks_dict = [self._chunk_to_dict(c) for c in chunks]
        else:
            chunks = chunk_markdown(input_text, config)
            chunks_dict = [self._chunk_to_dict(c) for c in chunks]

        # IMPORTANT: validate_and_fix applied for BOTH modes (hier and non-hier)
        chunks_dict = self._input_validator.validate_and_fix(chunks_dict)

        # Filtering for hierarchical mode
        if enable_hierarchy:
            chunks_dict = self._output_filter.filter(chunks_dict, debug=debug)

        return chunks_dict

    def _render_chunks(
        self,
        raw_chunks: list[dict[str, Any]],
        include_metadata: bool,
        debug: bool,
    ) -> list[str]:
        """Render chunks to output format.

        CRITICAL: This method does NOT modify boundaries or content,
        only formats output.
        """
        if include_metadata:
            return self._render_with_metadata(raw_chunks, debug)
        else:
            return self._render_without_metadata(raw_chunks)

    def _render_with_metadata(
        self, raw_chunks: list[dict[str, Any]], debug: bool
    ) -> list[str]:
        """Render with metadata (dify-style)."""
        result = []

        for chunk in raw_chunks:
            content = chunk.get("content", "")
            metadata = chunk.get("metadata", {})
            start_line = chunk.get("start_line", 0)
            end_line = chunk.get("end_line", 0)

            if debug:
                output_metadata = metadata.copy()
            else:
                output_metadata = self._filter_metadata_for_rag(metadata)

            output_metadata["start_line"] = start_line
            output_metadata["end_line"] = end_line

            metadata_json = json.dumps(output_metadata, ensure_ascii=False, indent=2)
            formatted = f"<metadata>\n{metadata_json}\n</metadata>\n{content}"
            result.append(formatted)

        return result

    def _render_without_metadata(self, raw_chunks: list[dict[str, Any]]) -> list[str]:
        """Render without metadata (with embedded overlap).

        IMPORTANT: Embeds overlap content (previous_content + content + next_content)
        into the returned strings for context preservation.
        """
        return [self._embed_overlap(chunk) for chunk in raw_chunks]

    def _embed_overlap(self, chunk: dict[str, Any]) -> str:
        """
        Embed overlap content into chunk for include_metadata=False mode.

        Combines previous_content + content + next_content with proper
        markdown formatting.

        Args:
            chunk: Raw chunk dict with content and metadata

        Returns:
            String with embedded overlap content

        Example:
            Input chunk:
            {
                "content": "## Section\\n\\nMain content...",
                "metadata": {
                    "previous_content": "...end of previous section.",
                    "next_content": "## Next Section\\n\\nNext content..."
                }
            }

            Output:
            "...end of previous section.\\n\\n## Section\\n\\nMain content...\\n\\n"
            "## Next Section\\n\\nNext content..."
        """
        try:
            metadata = chunk.get("metadata", {})

            # Extract content parts
            prev = metadata.get("previous_content", "").strip()
            content = chunk.get("content", "").strip()
            next_ = metadata.get("next_content", "").strip()

            # Build parts list (filter empty)
            parts = []
            if prev:
                parts.append(prev)
            if content:
                parts.append(content)
            if next_:
                parts.append(next_)

            # Join with markdown separator
            if not parts:
                return ""

            return "\n\n".join(parts)

        except Exception:
            # Graceful fallback on any error
            return chunk.get("content", "")

    def _chunk_to_dict(self, chunk: Any) -> dict[str, Any]:
        """Convert Chunk object to dictionary."""
        return {
            "content": chunk.content,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "metadata": chunk.metadata.copy() if chunk.metadata else {},
        }

    def _filter_metadata_for_rag(self, metadata: dict) -> dict:
        """Filter metadata to keep only fields useful for RAG search."""
        excluded_fields = {
            "avg_line_length",
            "avg_word_length",
            "char_count",
            "line_count",
            "size_bytes",
            "word_count",
            "item_count",
            "nested_item_count",
            "unordered_item_count",
            "ordered_item_count",
            "max_nesting",
            "task_item_count",
            "execution_fallback_level",
            "execution_fallback_used",
            "execution_strategy_used",
            "preamble.char_count",
            "preamble.line_count",
            "preamble.has_metadata",
            "preamble.metadata_fields",
            "preamble.type",
            "preamble_type",
            "preview",
            "total_chunks",
        }

        filtered = {}
        for key, value in metadata.items():
            if key in excluded_fields:
                continue

            if key in {"is_leaf", "is_root"}:
                continue

            if (key.startswith("is_") or key.startswith("has_")) and not value:
                continue

            filtered[key] = value

        return filtered

# Compatibility alias for legacy tests that import MarkdownChunker
MarkdownChunker = MigrationAdapter