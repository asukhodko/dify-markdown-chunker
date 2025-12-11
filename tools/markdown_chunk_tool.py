"""Advanced Markdown Chunker Tool for Dify

This module implements the Tool class for the Advanced Markdown Chunker plugin.
It provides intelligent, structure-aware chunking of Markdown documents for RAG systems.

Author: asukhodko
Version: 2.0.0
Date: 2025-12-04
"""

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from markdown_chunker import MarkdownChunker, ChunkConfig


class MarkdownChunkTool(Tool):
    """Tool for chunking Markdown documents with structural awareness.

    This tool analyzes Markdown content and intelligently splits it into chunks while:
    - Preserving document structure (headers, code blocks, lists, tables)
    - Maintaining semantic context across chunks
    - Supporting configurable chunk size and overlap
    - Providing rich metadata for each chunk

    Uses markdown_chunker v2 with 4-strategy architecture:
    1. CodeAware - for code-heavy documents
    2. ListAware - for list-heavy documents (changelogs, feature lists)
    3. Structural - for header-based documents
    4. Fallback - for simple text
    """

    def _filter_metadata_for_rag(self, metadata: dict) -> dict:
        """Filter metadata to keep only fields useful for RAG search.

        Removes statistical and internal fields that don't help with retrieval.

        Args:
            metadata: Full metadata dictionary from chunker

        Returns:
            Filtered metadata with only RAG-useful fields
        """
        # Fields to EXCLUDE (not useful for RAG)
        excluded_fields = {
            # Statistical fields
            'avg_line_length', 'avg_word_length', 'char_count', 'line_count',
            'size_bytes', 'word_count',
            # Count fields
            'item_count', 'nested_item_count', 'unordered_item_count',
            'ordered_item_count', 'max_nesting', 'task_item_count',
            # Internal/execution fields
            'execution_fallback_level', 'execution_fallback_used',
            'execution_strategy_used',
            # Preamble internal fields
            'preamble.char_count', 'preamble.line_count', 'preamble.has_metadata',
            'preamble.metadata_fields', 'preamble.type',
            # Redundant fields
            'preamble_type', 'preview', 'total_chunks',
        }

        filtered = {}
        for key, value in metadata.items():
            if key in excluded_fields:
                continue

            # Skip is_leaf, is_root unless debug
            if key in {'is_leaf', 'is_root'}:
                continue

            # Skip other is_*/has_* fields with False values
            if (key.startswith('is_') or key.startswith('has_')) and not value:
                continue

            filtered[key] = value

        return filtered

    def _format_chunk_output(self, chunk: Any, include_metadata: bool, debug: bool = False) -> str:
        """Format single chunk for output.

        Args:
            chunk: Chunk object
            include_metadata: Whether to include metadata in output
            debug: Debug mode - skip metadata filtering when True

        Returns:
            Formatted chunk string

        Behavior:
            - include_metadata=True: Returns <metadata> block + content.
              Overlap context stays in metadata fields (previous_content, next_content).
              - debug=True: Returns raw unfiltered metadata
              - debug=False: Returns filtered metadata for RAG
            - include_metadata=False: Returns clean content with overlap embedded.
              Formula: previous_content + "\n" + main + "\n" + next_content
              (with edge case handling for first/last chunks and zero overlap)
        """
        import json

        content = chunk.content
        metadata = chunk.metadata or {}

        if include_metadata:
            # Metadata mode: overlap stays in metadata fields
            if debug:
                # Debug mode: return raw metadata without filtering
                output_metadata = metadata.copy()
            else:
                # Normal mode: filter metadata for RAG
                output_metadata = self._filter_metadata_for_rag(metadata)
            
            output_metadata['start_line'] = chunk.start_line
            output_metadata['end_line'] = chunk.end_line
            metadata_json = json.dumps(output_metadata, ensure_ascii=False, indent=2)
            return f"<metadata>\n{metadata_json}\n</metadata>\n{content}"
        else:
            # Clean mode: embed overlap into content
            previous_content = metadata.get("previous_content", "")
            next_content = metadata.get("next_content", "")

            # Build content with overlap embedded
            parts = []
            if previous_content:
                parts.append(previous_content)
            parts.append(content)
            if next_content:
                parts.append(next_content)

            return "\n".join(parts)

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """Chunk a Markdown document.

        Args:
            tool_parameters: Parameters from YAML:
                - input_text (str, required): Markdown text to chunk
                - max_chunk_size (int, optional): Maximum chunk size (default: 4096)
                - chunk_overlap (int, optional): Overlap between chunks (default: 200)
                - strategy (str, optional): Chunking strategy (default: "auto")
                - include_metadata (bool, optional): Include metadata (default: True)
                - enable_hierarchy (bool, optional): Enable hierarchical chunking (default: False)
                - debug (bool, optional): Debug mode - include all chunks (default: False)

        Yields:
            ToolInvokeMessage: Success message with chunked results or error message
        """
        try:
            # 1. Extract and validate input_text
            input_text = tool_parameters.get("input_text", "")
            if not input_text or not input_text.strip():
                yield self.create_text_message(
                    "Error: input_text is required and cannot be empty"
                )
                return

            # 2. Extract optional parameters with defaults
            max_chunk_size = tool_parameters.get("max_chunk_size", 4096)
            chunk_overlap = tool_parameters.get("chunk_overlap", 200)
            strategy = tool_parameters.get("strategy", "auto")
            include_metadata = tool_parameters.get("include_metadata", True)
            enable_hierarchy = tool_parameters.get("enable_hierarchy", False)
            debug = tool_parameters.get("debug", False)

            # 3. Create ChunkConfig (v2 simplified API)
            strategy_override = None if strategy == "auto" else strategy

            config = ChunkConfig(
                max_chunk_size=max_chunk_size,
                overlap_size=chunk_overlap,
                strategy_override=strategy_override,
            )

            # 4. Chunk the document
            chunker = MarkdownChunker(config)
            if enable_hierarchy:
                result = chunker.chunk_hierarchical(input_text)
                # Debug mode: return ALL chunks (root, intermediate, leaf)
                # Normal mode: return only leaf chunks (content only)
                if debug:
                    chunks = result.chunks  # All chunks including root/intermediate
                else:
                    chunks = result.get_flat_chunks()  # Leaf chunks only
            else:
                chunks = chunker.chunk(input_text)

            # 5. Format results for Dify
            # NOTE: Dify UI expects result to be an array of strings
            # The 'result' variable is returned as an array, not through JSON channel.
            # JSON channel (json[0].data) is currently NOT used - all output goes through 'result'.
            # This allows Dify to display chunks as separate items in the Knowledge Base UI.
            formatted_result = [
                self._format_chunk_output(chunk, include_metadata, debug)
                for chunk in chunks
            ]

            # 6. Return results as array of strings via 'result' variable
            # Each chunk is a separate string in the array
            yield self.create_variable_message("result", formatted_result)

        except ValueError as e:
            yield self.create_text_message(f"Validation error: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error chunking document: {str(e)}")
