# Project Information

## Overview

**Dify Markdown Chunker** is an advanced Markdown chunking plugin for the Dify platform. It provides intelligent document segmentation with structural awareness and automatic strategy selection.

## Key Features

- **6 Chunking Strategies**: Code, Mixed, List, Table, Structural, Sentences
- **Automatic Strategy Selection**: Analyzes content and chooses optimal approach
- **Structural Awareness**: Preserves markdown structure, code blocks, tables, and lists
- **Comprehensive Testing**: 1366+ tests with property-based testing
- **Production Ready**: Optimized for RAG systems and knowledge bases

## Technology Stack

- **Language**: Python 3.12+
- **Framework**: Dify Plugin SDK
- **Testing**: pytest, Hypothesis (property-based testing)
- **Parsing**: markdown-it-py, mistune
- **Validation**: pydantic

## Project Statistics

- **Lines of Code**: ~15,000
- **Test Coverage**: 80%+
- **Tests**: 1366+
- **Documentation**: Comprehensive (API, Developer Guide, Architecture)
- **Performance**: Optimized for documents up to 100KB

## Architecture

### Core Components

1. **Parser Module** (`markdown_chunker/parser/`)
   - AST parsing
   - Code block extraction
   - Element detection
   - Content analysis

2. **Chunker Module** (`markdown_chunker/chunker/`)
   - Strategy implementations
   - Strategy selector
   - Chunk processor
   - Overlap handler

3. **API Module** (`markdown_chunker/api/`)
   - REST API adapters
   - Request/response models
   - Validation

4. **Dify Integration** (`provider/`, `tools/`)
   - Plugin provider
   - Tool implementations
   - Configuration

### Design Principles

- **Modularity**: Clear separation of concerns
- **Extensibility**: Easy to add new strategies
- **Testability**: Comprehensive test coverage
- **Performance**: Optimized for production use
- **Maintainability**: Clean code, good documentation

## Development

### Prerequisites

- Python 3.12+
- dify-plugin CLI
- Git

### Quick Start

```bash
# Clone repository
git clone <repository_url>
cd dify-markdown-chunker

# Setup environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
make install

# Run tests
make test

# Build package
make package
```

### Development Commands

```bash
make test           # Run all tests
make test-quick     # Run quick tests
make test-coverage  # Run with coverage
make lint           # Run linter
make format         # Format code
make validate       # Validate structure
make package        # Build plugin package
make release        # Full release build
```

## Documentation

- **[README.md](README.md)** - Main documentation
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[docs/](docs/)** - Detailed documentation
  - API Reference
  - Developer Guide
  - Algorithm Documentation
  - Architecture
  - Configuration

## Testing

### Test Categories

1. **Unit Tests**: Component-level testing
2. **Integration Tests**: End-to-end workflows
3. **Property Tests**: Universal properties (Hypothesis)
4. **Performance Tests**: Benchmarking
5. **Fixture Tests**: Real-world documents

### Test Coverage

- Parser: 85%+
- Chunker: 90%+
- API: 80%+
- Integration: 75%+

## Performance

### Benchmarks

| Document Size | Processing Time | Throughput | Chunks |
|--------------|----------------|------------|--------|
| 1 KB         | ~800 ms        | 1.3 KB/s   | 6      |
| 10 KB        | ~150 ms        | 66 KB/s    | 44     |
| 50 KB        | ~1.9 s         | 27 KB/s    | 215    |
| 100 KB       | ~7 s           | 14 KB/s    | 429    |

### Optimization

- Streaming processing for large files (>10MB)
- Efficient regex patterns
- Memory pooling
- Caching of analysis results

## Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

Current version: **2.0.0**

## License

MIT License - see [LICENSE](LICENSE) file

## Support

- **Issues**: GitHub Issues
- **Documentation**: `docs/` directory
- **Examples**: `examples/` directory
- **Community**: Dify Discord

## Roadmap

### Planned Features

- [ ] Support for more markdown extensions
- [ ] Custom strategy plugins
- [ ] Advanced metadata extraction
- [ ] Multi-language support improvements
- [ ] Performance optimizations
- [ ] Enhanced error reporting

### Future Improvements

- Streaming API for large documents
- Parallel processing support
- Custom delimiter support
- Advanced table handling
- Improved code language detection

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Acknowledgments

This plugin was developed as part of a larger RAG system project and has been extracted into a standalone Dify plugin for broader use.

Special thanks to:
- Dify team for the excellent platform
- Contributors and testers
- Open source community

## Contact

- **Repository**: GitHub
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
