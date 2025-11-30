"""Provider class for Advanced Markdown Chunker

This module implements the ToolProvider for the Advanced Markdown Chunker plugin.
No credentials are required as chunking is a local operation.

Author: asukhodko
Version: 2.0.0
Date: 2025-11-22
"""

from typing import Any
from dify_plugin import ToolProvider


class MarkdownChunkerProvider(ToolProvider):
    """Provider for Advanced Markdown Chunker tool.

    This provider manages the Advanced Markdown Chunker tool which provides
    intelligent, structure-aware chunking of Markdown documents for RAG systems.

    No credentials are required - chunking is a local operation that doesn't
    require external services or API keys.
    """

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """Validate provider credentials.

        For this chunker, no credentials are needed as all operations are local.
        This method is required by the ToolProvider interface but performs no
        validation.

        Args:
            credentials: Dictionary of credentials (unused for this provider)
        """
        pass
