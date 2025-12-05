"""Provider class for Dify plugin system.

This module provides the MarkdownChunkerProvider class that integrates
with the Dify plugin framework.
"""

from dify_plugin import ToolProvider


class MarkdownChunkerProvider(ToolProvider):
    """Provider for markdown chunker Dify plugin.
    
    This provider handles credential validation and plugin lifecycle
    for the markdown chunker tool. Since markdown chunker is a local
    processing tool, no external credentials are required.
    """
    
    def _validate_credentials(self, credentials: dict) -> None:
        """Validate provider credentials.
        
        For markdown chunker, no credentials are required as it's
        a local processing tool that doesn't connect to external services.
        
        Args:
            credentials: Dictionary of credentials (unused)
            
        Returns:
            None - always passes validation
        """
        # Markdown chunker doesn't require credentials
        # It's a local processing tool
        pass
