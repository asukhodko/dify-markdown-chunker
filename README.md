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

### Quick Install

1. Download the latest `.difypkg` file from releases
2. In Dify UI: **Settings → Plugins → Install Plugin**
3. Upload the package file
4. Configure in your workflows

For detailed installation instructions, see **[Installation Guide](docs/installation.md)**.

### Development Setup

```bash
git clone https://github.com/asukhodko/dify-markdown-chunker.git
cd dify-markdown-chunker
python3 -m venv venv
source venv/bin/activate
make install
make test
```

See **[Development Guide](docs/guides/developer-guide.md)** for complete setup instructions.

## Quick Start

Get started in 5 minutes with these simple examples. For comprehensive examples and detailed usage, see **[Quick Start Guide](docs/quickstart.md)** and **[Usage Guide](docs/usage.md)**.

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
from markdown_chunker import MarkdownChunker

# Basic usage
chunker = MarkdownChunker()
result = chunker.chunk("# Hello\n\nWorld", include_analysis=True)

print(f"Strategy: {result.strategy_used}")
print(f"Chunks: {len(result.chunks)}")
```

For more examples including configuration profiles, overlap handling, and advanced features, see **[Quick Start Guide](docs/quickstart.md)**.

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

Comprehensive documentation is available in the **[docs/](docs/)** directory:

- **[Quick Start](docs/quickstart.md)** - Get started in 5 minutes
- **[Usage Guide](docs/usage.md)** - Detailed usage examples
- **[API Reference](docs/api/)** - Complete API documentation
- **[Architecture](docs/architecture/)** - System design and components
- **[Developer Guide](docs/guides/developer-guide.md)** - Development workflows
- **[Configuration Reference](docs/reference/configuration.md)** - All configuration options

See **[Documentation Index](docs/README.md)** for the complete documentation structure.

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

We welcome contributions! For detailed guidelines, see **[CONTRIBUTING.md](CONTRIBUTING.md)**.

**Quick Start:**
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run `make test` and `make quality-check`
5. Submit a Pull Request

**Development Resources:**
- **[Development Guide](docs/guides/developer-guide.md)** - Complete development workflows
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Quick reference for developers
- **[Testing Guide](docs/guides/testing-guide.md)** - Testing strategies and frameworks

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

**Current Version:** 2.0.0-a3 (December 2024)

### Recent Updates
- Redesigned overlap handling with metadata-based neighbor context
- Regression and duplication validation
- Comprehensive API reference documentation
- Enhanced documentation structure
- Type annotations improvements

For complete version history and detailed changes, see **[CHANGELOG.md](CHANGELOG.md)**.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Review documentation in `docs/`
- Check examples in `examples/`
- Run tests to verify functionality

## Acknowledgments

This plugin was developed as part of a larger RAG system project and has been extracted into a standalone Dify plugin for broader use.
