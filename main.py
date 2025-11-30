"""Dify Plugin Entry Point for Advanced Markdown Chunker

This module serves as the entry point for the Dify plugin that provides
advanced markdown chunking capabilities for Knowledge Base ingestion.

The plugin wraps the markdown_chunker library and exposes it as a Dify Tool
that can be used in Knowledge Base processing pipelines.

Author: asukhodko
Version: 2.0.0
Date: 2025-11-22
"""

from dify_plugin import Plugin, DifyPluginEnv

# Configure plugin with 300 second timeout for large documents
MAX_REQUEST_TIMEOUT=300

# Create plugin instance
plugin=Plugin(
    DifyPluginEnv(
        max_request_timeout=MAX_REQUEST_TIMEOUT
    )
)

if __name__ == '__main__':
    # Run the plugin
    # In debug mode: connects to remote Dify instance via .env configuration
    # In production: runs as packaged plugin within Dify
    plugin.run()
