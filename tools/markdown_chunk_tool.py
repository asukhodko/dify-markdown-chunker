"""Advanced Markdown Chunker Tool for Dify

This module implements the Tool class for the Advanced Markdown Chunker plugin.
It provides intelligent, structure-aware chunking of Markdown documents for RAG systems.

Author: asukhodko
Version: 2.0.0
Date: 2025-11-22
"""

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from markdown_chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig


class MarkdownChunkTool(Tool):
    """Tool for chunking Markdown documents with structural awareness.

    This tool analyzes Markdown content and intelligently splits it into chunks while:
    - Preserving document structure (headers, code blocks, lists, tables)
    - Maintaining semantic context across chunks
    - Supporting configurable chunk size and overlap
    - Providing rich metadata for each chunk

    The tool integrates the Advanced Markdown Chunker library (Stages 1-2) into
    Dify's Knowledge Base ingestion pipeline.
    """

    def _filter_metadata_for_rag(self, metadata: dict) -> dict:
        """Filter metadata to keep only fields useful for RAG search.

        Removes statistical and internal fields that don't help with retrieval.
        Preserves overlap context fields (previous_content, next_content) when present.

        Args:
            metadata: Full metadata dictionary from chunker

        Returns:
            Filtered metadata with only RAG-useful fields
        """
        # Fields to EXCLUDE (not useful for RAG)
        excluded_fields={
            # Statistical fields
            'avg_line_length', 'avg_word_length', 'char_count', 'line_count',
            'size_bytes', 'word_count',
            # Count fields
            'item_count', 'nested_item_count', 'unordered_item_count',
            'ordered_item_count', 'max_nesting', 'task_item_count',
            # Internal/execution fields
            'execution_fallback_level', 'execution_fallback_used',
            'execution_strategy_used', 'strategy',
            # Preamble internal fields
            'preamble.char_count', 'preamble.line_count', 'preamble.has_metadata',
            'preamble.metadata_fields', 'preamble.type',
            # Redundant fields
            'preamble_type', 'preview', 'total_chunks',
            # Legacy block-based overlap fields (replaced by previous_content/next_content)
            'has_overlap', 'overlap_type', 'overlap_size', 'overlap_block_count',
            'overlap_block_ids', 'overlap_start_offset', 'new_content_start_offset'
        }

        # Recursively filter metadata
        filtered={}
        for key, value in metadata.items():
            if key in excluded_fields:
                continue

            # Skip is_*/has_* fields with False values (only include if True)
            if (key.startswith('is_') or key.startswith('has_')) and (value is None or value is False):
                continue

            # Handle nested preamble object
            if key == 'preamble' and isinstance(value, dict):
                # Keep only preamble content, exclude internal fields
                if 'content' in value:
                    filtered[key] = {'content': value['content']}
            else:
                filtered[key] = value

        return filtered

    def _extract_chunks_list(self, result: Any) -> list:
        """Extract list of chunks from result, regardless of format.
        
        Handles both dict format (with 'chunks' key) and direct list format.
        
        Args:
            result: Result from chunker.chunk(), either dict or list
            
        Returns:
            List of chunk objects/dicts
        """
        if isinstance(result, dict) and 'chunks' in result:
            return result['chunks']
        elif isinstance(result, list):
            return result
        else:
            return []

    def _format_chunk_output(self, chunk: Any, include_metadata: bool) -> str:
        """Format single chunk for output.
        
        Args:
            chunk: Chunk object or dict
            include_metadata: Whether to include metadata in output
            
        Returns:
            Formatted chunk string
        """
        import json
        
        # Extract content and metadata from chunk (handle dict or object)
        if isinstance(chunk, dict):
            content = chunk.get('content', '')
            metadata = chunk.get('metadata', {})
        else:
            content = getattr(chunk, 'content', '')
            metadata = getattr(chunk, 'metadata', {})
        
        # Format based on metadata flag
        if include_metadata and metadata:
            filtered_metadata = self._filter_metadata_for_rag(metadata)
            metadata_json = json.dumps(filtered_metadata, ensure_ascii=False, indent=2)
            return f"<metadata>\n{metadata_json}\n</metadata>\n{content}"
        else:
            return content

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """Chunk a Markdown document.

        Args:
            tool_parameters: Parameters from YAML:
                - input_text (str, required): Markdown text to chunk
                - max_chunk_size (int, optional): Maximum chunk size (default: 1000)
                - chunk_overlap (int, optional): Overlap between chunks (default: 100)
                - strategy (str, optional): Chunking strategy (default: "auto")
                - include_metadata (bool, optional): Include metadata (default: True)

        Yields:
            ToolInvokeMessage: Success message with chunked results or error message
        """
        try:
            # 1. Extract and validate input_text
            input_text=tool_parameters.get("input_text", "")
            if not input_text or not input_text.strip():
                yield self.create_text_message(
                    "Error: input_text is required and cannot be empty"
                )
                return

            # 2. Extract optional parameters with defaults
            max_chunk_size=tool_parameters.get("max_chunk_size", 1000)
            chunk_overlap=tool_parameters.get("chunk_overlap", 100)
            strategy=tool_parameters.get("strategy", "auto")
            include_metadata=tool_parameters.get("include_metadata", True)

            # 3. Create ChunkConfig
            config=ChunkConfig(
                max_chunk_size=max_chunk_size,
                overlap_size=chunk_overlap,
                enable_overlap=True,  # Enable overlap feature
                block_based_overlap=False  # Use new metadata-mode overlap instead
            )

            # 4. Chunk the document
            chunker=MarkdownChunker(config)
            # Pass strategy to chunk() method, not to config
            # Convert "auto" to None for automatic selection
            strategy_param=None if strategy == "auto" else strategy
            result=chunker.chunk(
                input_text,
                strategy=strategy_param,
                include_analysis=include_metadata,
                return_format="dict",
                include_metadata=include_metadata  # Pass to control overlap mode
            )

            # 5. Format results for Dify using unified formatting logic
            # Dify UI expects result to be an array of strings
            # Format: "<metadata>\n{json}\n</metadata>\n{content}" or just "{content}"
            
            # Extract chunks list from result (handles both dict and list formats)
            chunks_list = self._extract_chunks_list(result)
            
            # Format each chunk consistently
            formatted_result = [
                self._format_chunk_output(chunk, include_metadata)
                for chunk in chunks_list
            ]

            # 6. Return results as array of strings
            yield self.create_variable_message("result", formatted_result)

        except ValueError as e:
            # Validation errors
            yield self.create_text_message(f"Validation error: {str(e)}")
        except Exception as e:
            # General errors
            yield self.create_text_message(f"Error chunking document: {str(e)}")
