# Developer Guide

**Version:** 1.4.0  
**Last Updated:** 2025-11-16  
**Audience:** Contributors, Maintainers, Advanced Users

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Development Setup](#development-setup)
4. [Adding a New Strategy](#adding-a-new-strategy)
5. [Running Tests](#running-tests)
6. [Performance Profiling](#performance-profiling)
7. [Coding Standards](#coding-standards)
8. [Contribution Guidelines](#contribution-guidelines)
9. [Release Process](#release-process)

---

## Architecture Overview

### Two-Stage Pipeline

The system follows a two-stage architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    Stage 1: Analysis                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Parser     │→ │   Content    │→ │   Element    │  │
│  │  Interface   │  │   Analyzer   │  │   Detector   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Stage 2: Chunking                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Strategy   │→ │   Chunking   │→ │   Metadata   │  │
│  │   Selector   │  │   Strategy   │  │   Enricher   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Stage 1: Content Analysis

**Purpose:** Analyze markdown structure and extract metadata

**Components:**
- `ParserInterface`: Main entry point for Stage 1
- `ContentAnalyzer`: Analyzes content type, complexity, code ratio
- `ElementDetector`: Detects headers, lists, tables, code blocks
- `FencedBlockExtractor`: Extracts fenced code blocks
- `PreambleExtractor`: Extracts document preamble/metadata

**Output:** `Stage1Results` containing:
- AST (Abstract Syntax Tree)
- Content analysis metrics
- Detected elements (code, lists, tables, headers)
- Preamble information

### Stage 2: Adaptive Chunking

**Purpose:** Create semantically meaningful chunks

**Components:**
- `MarkdownChunker`: Main orchestrator
- `StrategySelector`: Selects optimal chunking strategy
- 6 Chunking Strategies (see below)
- `OverlapManager`: Adds overlap between chunks
- `MetadataEnricher`: Enriches chunk metadata
- `FallbackManager`: Handles errors with fallback chain

**Output:** List of `Chunk` objects with metadata

### Chunking Strategies

1. **CodeStrategy** - For code-heavy documents (≥70% code)
2. **StructuralStrategy** - For well-structured documents with headers
3. **MixedStrategy** - For diverse content with multiple element types
4. **ListStrategy** - For list-heavy documents (≥5 lists)
5. **TableStrategy** - For table-heavy documents (≥3 tables)
6. **SentencesStrategy** - Fallback for simple text

**Strategy Selection Algorithm:**

```python
if code_ratio >= 0.7 and code_blocks >= 3:
    return CodeStrategy()
elif table_count >= 3:
    return TableStrategy()
elif list_count >= 5:
    return ListStrategy()
elif complexity_score >= 0.3:
    return MixedStrategy()
elif header_count >= 3:
    return StructuralStrategy()
else:
    return SentencesStrategy()
```

---

## Project Structure

```
dify-markdown-chunker/
├── markdown_chunker/          # Main package
│   ├── parser/                # Stage 1: Analysis
│   │   ├── core.py           # ParserInterface, FencedBlockExtractor
│   │   ├── analyzer.py       # ContentAnalyzer
│   │   ├── ast.py            # AST builder
│   │   ├── preamble.py       # PreambleExtractor
│   │   ├── types.py          # Data structures
│   │   └── utils.py          # Utility functions
│   ├── chunker/               # Stage 2: Chunking
│   │   ├── core.py           # MarkdownChunker
│   │   ├── selector.py       # StrategySelector
│   │   ├── types.py          # Chunk, ChunkConfig, ChunkingResult
│   │   ├── strategies/       # Chunking strategies
│   │   │   ├── base.py       # BaseStrategy
│   │   │   ├── code_strategy.py
│   │   │   ├── structural_strategy.py
│   │   │   ├── mixed_strategy.py
│   │   │   ├── list_strategy.py
│   │   │   ├── table_strategy.py
│   │   │   └── sentences_strategy.py
│   │   └── components/       # Supporting components
│   │       ├── overlap_manager.py
│   │       ├── metadata_enricher.py
│   │       └── fallback_manager.py
│   └── api/                   # Public API
│       ├── __init__.py       # chunk_text(), chunk_file()
│       └── types.py          # API types
├── tests/                     # Test suite
│   ├── parser/               # Stage 1 tests
│   ├── chunker/              # Stage 2 tests
│   ├── integration/          # Integration tests
│   ├── fixtures/             # Test data
│   └── regression/           # Regression tests
├── docs/                      # Documentation
│   └── markdown-extractor/   # Algorithm documentation
├── benchmarks/                # Performance benchmarks
└── examples/                  # Usage examples
```

---

## Development Setup

### Prerequisites

- Python 3.8+
- pip or poetry
- git

### Installation

```bash
# Clone repository
git clone https://github.com/example/markdown-chunker.git
cd markdown-chunker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

### Development Dependencies

```bash
# Testing
pytest>=7.0.0
pytest-cov>=4.0.0

# Linting
ruff>=0.1.0
black>=23.0.0
mypy>=1.0.0

# Documentation
sphinx>=5.0.0
sphinx-rtd-theme>=1.0.0
```

### IDE Setup

**VS Code:**
```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true
}
```

**PyCharm:**
- Enable pytest as test runner
- Configure Black as formatter
- Enable Ruff for linting

---

## Adding a New Strategy

### Step 1: Create Strategy Class

Create a new file in `markdown_chunker/chunker/strategies/`:

```python
# markdown_chunker/chunker/strategies/my_strategy.py

from typing import List
from ..types import Chunk, ChunkConfig
from ...parser.types import Stage1Results
from .base import BaseStrategy


class MyStrategy(BaseStrategy):
    """
    Custom chunking strategy for [describe use case].
    
    This strategy is activated when [describe conditions].
    """
    
    def __init__(self):
        super().__init__()
        self.name = "my_strategy"
        self.priority = 50  # 0-100, higher = higher priority
    
    def can_handle(self, analysis, config: ChunkConfig) -> bool:
        """
        Determine if this strategy can handle the content.
        
        Args:
            analysis: ContentAnalysis from Stage 1
            config: ChunkConfig with thresholds
        
        Returns:
            True if strategy should be used
        """
        # Example: activate if document has specific characteristics
        return (
            analysis.some_metric > config.some_threshold
            and analysis.some_count >= 3
        )
    
    def apply(
        self,
        text: str,
        stage1_results: Stage1Results,
        config: ChunkConfig
    ) -> List[Chunk]:
        """
        Apply chunking strategy to create chunks.
        
        Args:
            text: Original markdown text
            stage1_results: Results from Stage 1 analysis
            config: Chunking configuration
        
        Returns:
            List of Chunk objects
        """
        chunks = []
        
        # Your chunking logic here
        # Example: split by some criteria
        sections = self._split_into_sections(text)
        
        for i, section in enumerate(sections):
            chunk = Chunk(
                content=section["content"],
                start_line=section["start_line"],
                end_line=section["end_line"],
                metadata={
                    "strategy": self.name,
                    "content_type": "custom",
                    "section_index": i,
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_into_sections(self, text: str):
        """Helper method for splitting logic."""
        # Implement your splitting logic
        pass
```

### Step 2: Register Strategy

Add to `MarkdownChunker.__init__()`:

```python
# markdown_chunker/chunker/core.py

from .strategies import MyStrategy

class MarkdownChunker:
    def __init__(self, config=None):
        # ... existing code ...
        
        self._strategies: List[BaseStrategy] = [
            CodeStrategy(),
            MixedStrategy(),
            ListStrategy(),
            TableStrategy(),
            StructuralStrategy(),
            SentencesStrategy(),
            MyStrategy(),  # Add your strategy
        ]
```

### Step 3: Add Tests

Create test file `tests/chunker/strategies/test_my_strategy.py`:

```python
import pytest
from markdown_chunker.chunker.strategies.my_strategy import MyStrategy
from markdown_chunker.chunker.types import ChunkConfig
from markdown_chunker.parser import ParserInterface


class TestMyStrategy:
    """Tests for MyStrategy."""
    
    @pytest.fixture
    def strategy(self):
        return MyStrategy()
    
    @pytest.fixture
    def parser(self):
        return ParserInterface()
    
    def test_can_handle_appropriate_content(self, strategy):
        """Test that strategy activates for appropriate content."""
        # Create mock analysis
        from markdown_chunker.parser.types import ContentAnalysis
        
        analysis = ContentAnalysis(
            content_type="custom",
            some_metric=0.8,
            some_count=5,
            # ... other required fields
        )
        
        config = ChunkConfig()
        assert strategy.can_handle(analysis, config)
    
    def test_apply_creates_chunks(self, strategy, parser):
        """Test that strategy creates valid chunks."""
        text = """
# Test Document

Content for testing.
"""
        
        stage1_results = parser.process_document(text)
        config = ChunkConfig()
        
        chunks = strategy.apply(text, stage1_results, config)
        
        assert len(chunks) > 0
        assert all(isinstance(c, Chunk) for c in chunks)
        assert all(c.metadata["strategy"] == "my_strategy" for c in chunks)
```

### Step 4: Update Documentation

Add strategy documentation to:
- `README.md` - Brief description
- `docs/ALGORITHM_MAPPING.md` - Implementation details
- This guide - Usage examples

---

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/chunker/test_core.py
```

### Run Specific Test

```bash
pytest tests/chunker/test_core.py::TestMarkdownChunker::test_chunk_basic
```

### Run with Coverage

```bash
pytest --cov=markdown_chunker --cov-report=html
```

View coverage report: `open htmlcov/index.html`

### Run Integration Tests Only

```bash
pytest tests/integration/
```

### Run Performance Tests

```bash
pytest tests/integration/test_performance_full_pipeline.py -v
```

### Run Tests in Parallel

```bash
pytest -n auto  # Requires pytest-xdist
```

### Test Categories

- **Unit Tests** (`tests/parser/`, `tests/chunker/`): Test individual components
- **Integration Tests** (`tests/integration/`): Test full pipeline
- **Regression Tests** (`tests/regression/`): Prevent known bugs
- **Performance Tests** (`tests/integration/test_performance_*.py`): Verify performance

---

## Performance Profiling

### Using cProfile

```python
import cProfile
import pstats
from markdown_chunker import MarkdownChunker

def profile_chunking():
    chunker = MarkdownChunker()
    with open("large_document.md") as f:
        content = f.read()
    
    chunker.chunk(content)

# Profile
cProfile.run('profile_chunking()', 'profile_stats')

# Analyze
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

### Using py-spy

```bash
# Install py-spy
pip install py-spy

# Profile running process
py-spy record -o profile.svg -- python your_script.py

# View flame graph
open profile.svg
```

### Built-in Performance Monitoring

```python
from markdown_chunker import MarkdownChunker

chunker = MarkdownChunker(enable_performance_monitoring=True)
chunks = chunker.chunk(content)

# Get stats
stats = chunker.get_performance_stats()
print(f"Chunk time: {stats['chunk']['avg_time']:.3f}s")
print(f"Analysis time: {stats['analysis']['avg_time']:.3f}s")
```

### Benchmarking

```bash
# Run benchmarks
python benchmarks/benchmark_chunker.py

# Compare strategies
python benchmarks/compare_strategies.py
```

---

## Coding Standards

### Style Guide

- Follow PEP 8
- Use Black for formatting (line length: 88)
- Use Ruff for linting
- Type hints for all public APIs

### Naming Conventions

- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Longer description if needed. Explain what the function does,
    when to use it, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is invalid
        TypeError: When param2 is wrong type
    
    Examples:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    
    See Also:
        - related_function(): Related functionality
        - OtherClass: Related class
    
    Notes:
        - Important implementation detail
        - Performance consideration
    """
    pass
```

### Type Hints

```python
from typing import List, Dict, Optional, Union

def process_chunks(
    chunks: List[Chunk],
    config: Optional[ChunkConfig] = None
) -> Dict[str, Union[int, float]]:
    """Process chunks and return statistics."""
    pass
```

### Error Handling

```python
# Use specific exceptions
from markdown_chunker.chunker.selector import StrategySelectionError

if strategy not in valid_strategies:
    raise StrategySelectionError(
        f"Invalid strategy '{strategy}'. "
        f"Valid strategies: {valid_strategies}"
    )

# Provide helpful error messages
if not text.strip():
    raise ValueError(
        "Input text is empty or whitespace-only. "
        "Please provide valid markdown content."
    )
```

---

## Contribution Guidelines

### Before Contributing

1. Check existing issues and PRs
2. Discuss major changes in an issue first
3. Read this guide thoroughly
4. Set up development environment

### Contribution Process

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/markdown-chunker.git
   cd markdown-chunker
   git remote add upstream https://github.com/example/markdown-chunker.git
   ```

2. **Create Branch**
   ```bash
   git checkout -b feature/my-feature
   # or
   git checkout -b fix/bug-description
   ```

3. **Make Changes**
   - Write code
   - Add tests
   - Update documentation
   - Run linter: `ruff check .`
   - Format code: `black .`

4. **Test**
   ```bash
   pytest
   pytest --cov=markdown_chunker
   ```

5. **Commit**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # or
   git commit -m "fix: resolve bug in strategy selection"
   ```

   **Commit Message Format:**
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation
   - `test:` Tests
   - `refactor:` Code refactoring
   - `perf:` Performance improvement
   - `chore:` Maintenance

6. **Push and PR**
   ```bash
   git push origin feature/my-feature
   ```
   
   Create PR on GitHub with:
   - Clear title and description
   - Link to related issue
   - Screenshots if UI changes
   - Test results

### Code Review

- Address reviewer feedback
- Keep PR focused and small
- Update tests if needed
- Maintain backward compatibility

---

## Release Process

### Version Numbering

Follow Semantic Versioning (SemVer):
- `MAJOR.MINOR.PATCH`
- `1.2.3` → `1.2.4` (patch: bug fixes)
- `1.2.3` → `1.3.0` (minor: new features, backward compatible)
- `1.2.3` → `2.0.0` (major: breaking changes)

### Release Checklist

1. **Update Version**
   - `pyproject.toml`
   - `markdown_chunker/__init__.py`
   - `CHANGELOG.md`

2. **Run Full Test Suite**
   ```bash
   pytest
   pytest --cov=markdown_chunker
   ```

3. **Update Documentation**
   - README.md
   - CHANGELOG.md
   - API documentation

4. **Create Release**
   ```bash
   git tag -a v1.2.3 -m "Release v1.2.3"
   git push origin v1.2.3
   ```

5. **Build and Publish**
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

6. **Create GitHub Release**
   - Tag: `v1.2.3`
   - Title: `Version 1.2.3`
   - Description: Copy from CHANGELOG.md

---

## Debugging with Logs

### Enabling Logging

Use logging to debug and monitor the chunking process:

```python
import logging

# Basic setup - show INFO and above
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from markdown_chunker import MarkdownChunker

chunker = MarkdownChunker()
chunks = chunker.chunk(markdown_text)
```

### Custom Logging Configuration

```python
from markdown_chunker.logging_config import setup_logging

# Setup with custom level
logger = setup_logging(level="DEBUG")

# Or with custom format
logger = setup_logging(
    level="INFO",
    format="%(levelname)s - %(name)s - %(message)s"
)
```

### Log Levels and Content

**DEBUG** - Detailed information for diagnosing problems:
- Element counts (code blocks, lists, tables, headers)
- Strategy metrics (can_handle, quality_score)
- Chunk statistics (sizes, counts)

**INFO** - Confirmation that things are working:
- Chunking start (text_length, strategy, config)
- Stage 1 analysis results (content_type, total_chars, total_lines)
- Strategy selection (name, reason, score)
- Chunking completion (chunks_count, processing_time)

**WARNING** - Indication of potential issues:
- Fallback events (level, final_strategy)
- Oversized chunks
- Configuration adjustments

**ERROR** - Serious problems:
- Stage 1 processing failures
- Strategy application errors
- Emergency chunking activation

### Debugging Specific Components

```python
import logging

# Debug only the chunker
logging.getLogger("markdown_chunker.chunker").setLevel(logging.DEBUG)

# Debug only strategies
logging.getLogger("markdown_chunker.chunker.strategies").setLevel(logging.DEBUG)

# Debug only parser
logging.getLogger("markdown_chunker.parser").setLevel(logging.DEBUG)
```

### Logging in Tests

```python
def test_with_logging(caplog):
    """Test with log capture."""
    import logging
    
    with caplog.at_level(logging.INFO):
        chunker = MarkdownChunker()
        chunks = chunker.chunk("# Test")
    
    # Check logs
    assert "Starting chunking" in caplog.text
    assert "Chunking complete" in caplog.text
```

---

## Type Checking

### Running mypy

Check types across the codebase:

```bash
# Check all code
mypy markdown_chunker/

# Check specific module
mypy markdown_chunker/chunker/

# With error codes
mypy markdown_chunker/ --show-error-codes

# Strict mode (gradually enable)
mypy markdown_chunker/ --strict
```

### Common Type Issues

**Missing return type:**
```python
# Before
def process(text):
    return text.upper()

# After
def process(text: str) -> str:
    return text.upper()
```

**Optional parameters:**
```python
# Before
def func(config: ChunkConfig = None):
    ...

# After
from typing import Optional

def func(config: Optional[ChunkConfig] = None):
    ...
```

**List/Dict annotations:**
```python
# Before
items = []

# After
from typing import List

items: List[str] = []
```

### Type Hints Best Practices

1. **Always annotate public APIs:**
   ```python
   def chunk(self, text: str, config: Optional[ChunkConfig] = None) -> List[Chunk]:
       ...
   ```

2. **Use Optional for nullable values:**
   ```python
   parent: Optional[HeaderInfo] = None
   ```

3. **Annotate complex types:**
   ```python
   metadata: Dict[str, Any] = {}
   ```

4. **Document type: ignore:**
   ```python
   result = some_function()  # type: ignore[no-any-return]  # TODO: Fix upstream
   ```

### IDE Integration

**VS Code:**
```json
{
  "python.linting.mypyEnabled": true,
  "python.linting.mypyArgs": [
    "--ignore-missing-imports",
    "--show-error-codes"
  ]
}
```

**PyCharm:**
- Settings → Tools → Python Integrated Tools → Type Checker: mypy
- Enable "Run mypy on save"

---

## Additional Resources

### Documentation

- [README.md](../README.md) - Project overview
- [ALGORITHM_MAPPING.md](ALGORITHM_MAPPING.md) - Algorithm implementation
- [API Reference](API_REFERENCE.md) - Full API reference
- [Architecture Documentation](architecture.md) - Detailed architecture specification

### Community

- GitHub Issues: Bug reports and feature requests
- Discussions: Questions and ideas
- Discord: Real-time chat (https://discord.gg/example)

### Related Projects

- [LangChain](https://python.langchain.com/) - Text splitters
- [LlamaIndex](https://www.llamaindex.ai/) - Document processors
- [Semantic Kernel](https://github.com/microsoft/semantic-kernel) - Chunking strategies

---

**Questions?** Open an issue or join our Discord!

**Happy coding! 🚀**
