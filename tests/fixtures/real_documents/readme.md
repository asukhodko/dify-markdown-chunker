# Python Markdown Chunker

[![PyPI version](https://badge.fury.io/py/markdown-chunker.svg)](https://badge.fury.io/py/markdown-chunker)
[![Tests](https://github.com/example/markdown-chunker/workflows/tests/badge.svg)](https://github.com/example/markdown-chunker/actions)
[![Coverage](https://codecov.io/gh/example/markdown-chunker/branch/main/graph/badge.svg)](https://codecov.io/gh/example/markdown-chunker)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful and flexible Python library for intelligently chunking Markdown documents. Perfect for RAG (Retrieval-Augmented Generation) applications, search indexing, and content processing.

## Features

- 🎯 **Smart Chunking**: Automatically selects optimal strategy based on content
- 📊 **6 Chunking Strategies**: Code, structural, sentences, lists, tables, and mixed
- 🔄 **Overlap Support**: Configurable chunk overlap for better context
- 🛡️ **Fallback Chain**: 4-level fallback ensures reliable processing
- 📝 **Rich Metadata**: Detailed chunk metadata including type, strategy, and line numbers
- ⚡ **High Performance**: Processes 100KB documents in <500ms
- 🎨 **Flexible Configuration**: Pre-configured profiles for common use cases
- 🔍 **Content Analysis**: Automatic detection of code, lists, tables, and structure
- 📦 **Zero Dependencies**: Pure Python implementation
- ✅ **Well Tested**: 1100+ tests with 100% pass rate

## Installation

```bash
pip install markdown-chunker
```

## Quick Start

```python
from markdown_chunker import MarkdownChunker

chunker = MarkdownChunker()
chunks = chunker.chunk("# Hello\n\nWorld")

for chunk in chunks:
    print(f"Chunk: {chunk.content}")
    print(f"Lines: {chunk.start_line}-{chunk.end_line}")
```

## Use Cases

### RAG Applications

```python
from markdown_chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig

config = ChunkConfig.for_dify_rag()
chunker = MarkdownChunker(config)

chunks = chunker.chunk(documentation)
# Store chunks in vector database
```

### Search Indexing

```python
config = ChunkConfig.for_search_indexing()
chunker = MarkdownChunker(config)

chunks = chunker.chunk(content)
# Index chunks in search engine
```

### Code Documentation

```python
config = ChunkConfig.for_code_heavy()
chunker = MarkdownChunker(config)

chunks = chunker.chunk(api_docs)
# Process code examples separately
```

## Configuration

Customize chunking behavior:

```python
config = ChunkConfig(
    max_chunk_size=2048,
    min_chunk_size=256,
    enable_overlap=True,
    overlap_size=100,
    preserve_code_blocks=True
)

chunker = MarkdownChunker(config)
```

## Strategies

The library includes 6 intelligent chunking strategies:

1. **Code Strategy**: For code-heavy documents (≥70% code)
2. **Structural Strategy**: Header-based chunking for well-structured docs
3. **Sentences Strategy**: Simple sentence-based chunking
4. **List Strategy**: Optimized for list-heavy content
5. **Table Strategy**: Preserves table integrity
6. **Mixed Strategy**: For complex documents with diverse content

## Performance

- Small documents (5KB): <100ms
- Medium documents (50KB): <500ms
- Large documents (100KB): <2s
- Throughput: ~200KB/s

## Requirements

- Python 3.8+
- No external dependencies

## Documentation

- [Tutorial](tutorial.md) - Step-by-step guide
- [API Documentation](api_documentation.md) - Complete API reference
- [Examples](examples/) - Code examples
- [Contributing](CONTRIBUTING.md) - Contribution guidelines

## Development

```bash
# Clone repository
git clone https://github.com/example/markdown-chunker.git
cd markdown-chunker

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Format code
black .
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=markdown_chunker

# Run specific test file
pytest tests/test_chunker.py
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- 📧 Email: support@example.com
- 💬 Discord: https://discord.gg/example
- 🐛 Issues: https://github.com/example/markdown-chunker/issues
- 📖 Docs: https://docs.example.com

## Acknowledgments

Built with inspiration from:
- LangChain's text splitters
- Semantic Kernel's chunking strategies
- LlamaIndex's document processors

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Roadmap

- [ ] Streaming support for large files
- [ ] Custom strategy plugins
- [ ] Multi-language support
- [ ] CLI tool
- [ ] Web UI for testing

---

Made with ❤️ by the Markdown Chunker Team
