# Installation Guide

This guide covers installing the Dify Markdown Chunker plugin in different scenarios.

## 📦 As Dify Plugin

### Prerequisites

- Dify instance (self-hosted or cloud)
- Admin access to Dify settings

### Installation Steps

1. **Download the Plugin Package**
   - Get the latest `.difypkg` file from releases
   - Or build from source (see [Development Setup](#for-development))

2. **Install in Dify**
   - Open Dify UI
   - Navigate to: **Settings → Plugins → Install Plugin**
   - Click "Upload Plugin"
   - Select the `.difypkg` file
   - Wait for installation to complete

3. **Verify Installation**
   - Go to: **Settings → Plugins**
   - Find "Advanced Markdown Chunker" in the list
   - Status should show "Active"

4. **Configure in Workflows**
   - Create or edit a workflow
   - Add a tool node
   - Select "Advanced Markdown Chunker"
   - Configure chunking parameters

### Configuration in Dify

When using in Dify workflows, you can configure:

- **max_chunk_size**: Maximum chunk size in characters (default: 2048)
- **min_chunk_size**: Minimum chunk size in characters (default: 256)
- **strategy**: Chunking strategy (`auto`, `code`, `mixed`, `list`, `table`, `structural`, `sentences`)
- **enable_overlap**: Enable chunk overlap (default: false)
- **overlap_size**: Overlap size in characters (default: 100)

## 🐍 As Python Library

### Prerequisites

- Python 3.12 or higher
- pip package manager

### Installation

```bash
# Install from source
git clone <repository-url>
cd dify-markdown-chunker
pip install -e .
```

### Verify Installation

```python
# Test import
from markdown_chunker import MarkdownChunker

# Create chunker
chunker = MarkdownChunker()
print("Installation successful!")
```

## 🛠️ For Development

### Prerequisites

- Python 3.12+
- Git
- dify-plugin CLI (for building packages)

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd dify-markdown-chunker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"
```

### Install dify-plugin CLI

```bash
# Linux/Mac
curl -L https://github.com/langgenius/dify-plugin-daemon/releases/latest/download/dify-plugin-linux-amd64 -o /tmp/dify-plugin
chmod +x /tmp/dify-plugin
sudo mv /tmp/dify-plugin /usr/local/bin/dify-plugin

# Verify installation
dify-plugin version
```

### Verify Development Setup

```bash
# Run tests
make test

# Run linter
make lint

# Build package
make package
```

## 🔧 Troubleshooting

### Plugin Installation Issues

**Problem**: "Plugin package is invalid"
- **Solution**: Ensure you downloaded the correct `.difypkg` file
- **Solution**: Try rebuilding the package: `make package`

**Problem**: "Plugin installation failed"
- **Solution**: Check Dify logs for detailed error messages
- **Solution**: Verify Dify version compatibility

### Python Library Issues

**Problem**: `ModuleNotFoundError: No module named 'markdown_chunker'`
- **Solution**: Activate virtual environment: `source venv/bin/activate`
- **Solution**: Install dependencies: `pip install -r requirements.txt`

**Problem**: Import errors
- **Solution**: Use correct imports: `from markdown_chunker import MarkdownChunker`
- **Solution**: Don't use legacy imports: `from stage1 import ...`

### Development Setup Issues

**Problem**: Tests failing
- **Solution**: Ensure virtual environment is activated
- **Solution**: Install test dependencies: `pip install -e ".[dev]"`
- **Solution**: Run: `make test-verbose` for detailed output

**Problem**: dify-plugin CLI not found
- **Solution**: Install CLI following instructions above
- **Solution**: Check PATH includes `/usr/local/bin`

## 📚 Next Steps

After installation:

1. Read the [Quick Start Guide](quickstart.md)
2. Check the [Usage Guide](usage.md)
3. Review [Configuration Options](reference/configuration.md)
4. See [Dify Integration](architecture/dify-integration.md) for workflow setup

## 🆘 Getting Help

- **Installation Issues**: Check [Troubleshooting Guide](guides/troubleshooting.md)
- **Configuration Help**: See [Configuration Reference](reference/configuration.md)
- **Development Questions**: Review [Developer Guide](guides/developer-guide.md)
