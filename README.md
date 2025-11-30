# Dify Markdown Chunker Plugin

Advanced Markdown chunking plugin for Dify with structural awareness and intelligent strategy selection.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Dify Plugin](https://img.shields.io/badge/dify-plugin-green.svg)](https://dify.ai/)

## Overview

This plugin provides production-ready markdown chunking capabilities for Dify with intelligent content analysis and adaptive chunking strategies:

- **Advanced Chunking**: 6 intelligent strategies (Code, Mixed, List, Table, Structural, Sentences)
- **Structural Awareness**: Preserves markdown structure and code blocks
- **Automatic Strategy Selection**: Analyzes content and selects optimal chunking approach
- **Comprehensive Testing**: 1366+ tests ensuring reliability
- **Property-Based Testing**: Correctness guarantees through formal properties

## Features

### Core Capabilities

- **Parser Module**: AST parsing, code block extraction, element detection
- **Chunker Module**: 6 adaptive strategies with automatic selection
- **API Module**: REST API adapters with validation
- **Utils Module**: Error handling and logging

### Dify Plugin Integration

- **Provider**: `MarkdownChunkerProvider` for Dify integration
- **Tools**: Chunking tools exposed to Dify workflows
- **Configuration**: Dify-specific settings and profiles

### Chunking Strategies

1. **Code Strategy**: Optimized for code-heavy documents
2. **Mixed Strategy**: Balanced approach for mixed content
3. **List Strategy**: Preserves list structures
4. **Table Strategy**: Handles tables intelligently
5. **Structural Strategy**: Follows document structure
6. **Sentences Strategy**: Fallback sentence-based chunking

## Installation

### As Dify Plugin

1. Download the plugin package
2. Install in your Dify instance following [Dify plugin installation guide](https://docs.dify.ai/plugins)
3. Configure the plugin in your Dify workflows

### For Development

```bash
# Clone the repository
git clone https://github.com/yourusername/dify-markdown-chunker.git
cd dify-markdown-chunker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install

# Run tests
make test
```

## Quick Start

### Using in Dify Workflows

```yaml
# In Dify workflow configuration
- tool: markdown_chunker
  config:
    max_chunk_size: 2048
    strategy: auto
```

### Using as Python Library

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

# Basic usage
chunker = MarkdownChunker()
result = chunker.chunk("# Hello\n\nWorld", include_analysis=True)

print(f"Strategy: {result.strategy_used}")
print(f"Chunks: {len(result.chunks)}")

# With custom config
config = ChunkConfig(
    max_chunk_size=2048,
    min_chunk_size=256,
    enable_overlap=True
)

chunker = MarkdownChunker(config)
chunks = chunker.chunk(markdown_text, include_analysis=True)
```

### Configuration Profiles

```python
from markdown_chunker import ChunkConfig

# For API documentation
config = ChunkConfig.for_api_docs()

# For code documentation
config = ChunkConfig.for_code_docs()

# For RAG systems (Dify default)
config = ChunkConfig.for_dify_rag()

# For search indexing
config = ChunkConfig.for_search_indexing()
```

## Project Structure

```
dify-markdown-chunker/
├── markdown_chunker/          # Core library
│   ├── parser/                # Content analysis and parsing
│   ├── chunker/               # Chunking strategies and logic
│   ├── api/                   # API adapters
│   └── utils/                 # Utilities
├── provider/                  # Dify plugin provider
├── tools/                     # Dify plugin tools
├── tests/                     # Comprehensive test suite (1366+ tests)
│   ├── parser/                # Parser tests
│   ├── chunker/               # Chunker tests
│   ├── integration/           # Integration tests
│   ├── api/                   # API tests
│   └── fixtures/              # Test fixtures
├── docs/                      # Documentation
├── benchmarks/                # Performance benchmarks
├── examples/                  # Usage examples
├── manifest.yaml              # Dify plugin manifest
├── requirements.txt           # Dependencies
└── Makefile                   # Development commands
```

## Development

### Running Tests

```bash
# All tests (1366+ tests)
make test

# With verbose output
make test-verbose

# With coverage report
make test-coverage

# Quick tests only
make test-quick
```

### Code Quality

```bash
# Format code
make format

# Run linter
make lint

# Type checking and quality checks
make quality-check
```

### Building Plugin Package

```bash
# Validate structure
make validate

# Build package
make package

# Validate package
make validate-package

# Full release build
make release
```

## Performance

Optimized for production use:

| Document Size | Processing Time | Throughput | Chunks |
|--------------|----------------|------------|--------|
| 1 KB         | ~800 ms        | 1.3 KB/s   | 6      |
| 10 KB        | ~150 ms        | 66 KB/s    | 44     |
| 50 KB        | ~1.9 s         | 27 KB/s    | 215    |
| 100 KB       | ~7 s           | 14 KB/s    | 429    |

## Documentation

- **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Development guide
- **[Algorithm Documentation](docs/ALGORITHM_MAPPING.md)** - Algorithm details
- **[Architecture](docs/architecture.md)** - System architecture
- **[Configuration](docs/configuration.md)** - Configuration options

## Dependencies

### Core Dependencies
- `markdown-it-py>=3.0.0` - Markdown parsing
- `mistune>=3.0.0` - Alternative parser
- `markdown>=3.4.0` - Markdown processing
- `pydantic>=2.0.0` - Data validation
- `dify_plugin==0.5.0b15` - Dify integration

### Development Dependencies
- `pytest>=8.0.0` - Testing framework
- `hypothesis>=6.0.0` - Property-based testing
- `black>=23.0.0` - Code formatter
- `isort>=5.12.0` - Import sorter
- `flake8>=6.0.0` - Linter

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests: `make test`
5. Format code: `make format`
6. Run quality checks: `make quality-check`
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Code Standards

- Follow PEP 8 style guide
- Use type hints
- Write comprehensive tests
- Document public APIs
- Maintain test coverage above 80%

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 2.0.0 (Current)
- Comprehensive test suite (1366+ tests)
- Property-based testing with Hypothesis
- Enhanced documentation
- Improved Makefile with development commands
- Performance benchmarks
- Usage examples

### Version 1.0.0
- Initial Dify plugin release
- Basic chunking functionality
- Dify integration

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Review documentation in `docs/`
- Check examples in `examples/`
- Run tests to verify functionality

## Acknowledgments

This plugin was developed as part of a larger RAG system project and has been extracted into a standalone Dify plugin for broader use.
