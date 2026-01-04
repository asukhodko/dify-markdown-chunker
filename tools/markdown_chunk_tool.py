"""Advanced Markdown Chunker Tool for Dify

This module implements the Tool class for the Advanced Markdown Chunker plugin.
It provides intelligent, structure-aware chunking of Markdown documents for RAG systems.

Author: asukhodko
Version: 2.1.5
Date: 2026-01-04
"""

from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from adapter import MigrationAdapter


class MarkdownChunkTool(Tool):
    """Tool for chunking Markdown documents with structural awareness.

    This tool analyzes Markdown content and intelligently splits it into chunks while:
    - Preserving document structure (headers, code blocks, lists, tables)
    - Maintaining semantic context across chunks
    - Supporting configurable chunk size and overlap
    - Providing rich metadata for each chunk

    Uses chunkana 0.1.0 library with migration adapter for compatibility.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """Chunk a Markdown document.

        Args:
            tool_parameters: Parameters from YAML:
                - input_text (str, required): Markdown text to chunk
                - max_chunk_size (int, optional): Maximum chunk size
                  (default: 4096)
                - chunk_overlap (int, optional): Overlap between chunks
                  (default: 200)
                - strategy (str, optional): Chunking strategy (default: "auto")
                - include_metadata (bool, optional): Include metadata
                  (default: True)
                - enable_hierarchy (bool, optional): Enable hierarchical
                  chunking (default: False)
                - debug (bool, optional): Debug mode - include all chunks
                  (default: False)

        Yields:
            ToolInvokeMessage: Success message with chunked results or
            error message
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

            # 3. Use migration adapter for chunking
            adapter = MigrationAdapter()

            # Build config using adapter
            config = adapter.build_chunker_config(
                max_chunk_size=max_chunk_size,
                chunk_overlap=chunk_overlap,
                strategy=strategy,
            )

            # Parse tool flags
            include_metadata, enable_hierarchy, debug = adapter.parse_tool_flags(
                include_metadata=include_metadata,
                enable_hierarchy=enable_hierarchy,
                debug=debug,
            )

            # 4. Run chunking through adapter
            formatted_result = adapter.run_chunking(
                input_text=input_text,
                config=config,
                include_metadata=include_metadata,
                enable_hierarchy=enable_hierarchy,
                debug=debug,
            )

            # 5. Return results as array of strings via 'result' variable
            # Each chunk is a separate string in the array
            yield self.create_variable_message("result", formatted_result)

        except ValueError as e:
            yield self.create_text_message(f"Validation error: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error chunking document: {str(e)}")
