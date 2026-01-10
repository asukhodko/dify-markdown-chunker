"""Dify Plugin Entry Point for Advanced Markdown Chunker

This module serves as the entry point for the Dify plugin that provides
advanced markdown chunking capabilities powered by the chunkana engine.

The plugin wraps the chunkana library through a migration adapter and exposes 
it as a Dify Tool that can be used in Knowledge Base processing pipelines.

Key Features:
- Intelligent strategy selection (code-aware, list-aware, structural, fallback)
- Structure-preserving chunking (code blocks, tables, lists intact)
- Hierarchical chunking with parent-child relationships
- Configurable chunk size and overlap
- Rich metadata embedding for improved RAG performance

Author: asukhodko
Version: 2.1.5 (chunkana-powered)
Date: 2026-01-10
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
