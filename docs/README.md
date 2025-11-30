# Python Markdown Chunker - Documentation

## 🎯 Overview

This documentation covers all stages of the Python Markdown Chunker project:

- **Stage 1**: Foundational infrastructure for Markdown parsing and block extraction
- **Stage 2**: Chunking strategies and algorithms
- **Stage 3**: Dify Plugin integration for Knowledge Base ingestion

---

## 📚 Stage 3: Dify Plugin (NEW!)

**Status:** ✅ Research completed, ready for implementation

### Documentation

📄 **[STAGE3_COMPLETE_GUIDE.md](STAGE3_COMPLETE_GUIDE.md)** - Самодостаточное руководство (всё в одном файле)
- Быстрый старт (10 минут)
- Все файлы с готовым кодом
- Пошаговая реализация
- Тестирование и отладка
- Troubleshooting

📄 **[STAGE3_TASK_DESCRIPTION.md](STAGE3_TASK_DESCRIPTION.md)** - Обновлённая постановка задачи
- Скорректированное описание этапа 3
- Все корректировки после исследования
- Полезные ссылки

**Goal:** Create a Dify Tool Plugin that integrates our advanced Markdown chunker
into Dify's Knowledge Pipeline for document ingestion.

**Time to implement:** 2-4 hours (with ready templates)

---

## 📚 Stage 1 & 2: Core Library

Stage 1 provides the foundational infrastructure for Markdown parsing and block extraction. This is the core layer that Stage 2 (chunking strategies) builds upon.

## 📚 Table of Contents

1. [Quick Start](#quick-start)
2. [Core Components](#core-components)
3. [Detailed Guides](#detailed-guides)
4. [For Stage 2 Developers](#for-stage-2-developers)
5. [Testing](#testing)

## 🚀 Quick Start

```python
from stage1 import process_markdown, analyze_markdown

# Basic usage - process complete document
result = process_markdown("# Hello\n\n```python\nprint('world')\n```")
print(f"Found {len(result.fenced_blocks)} code blocks")
print(f"Found {len(result.headers)} headers")
print(f"Found {len(result.lists)} lists")
print(f"Found {len(result.tables)} tables")

# Content analysis only
analysis = analyze_markdown("# Hello\n\n```python\nprint('world')\n```")
print(f"Content type: {analysis.content_type}")
print(f"Code ratio: {analysis.code_ratio:.2%}")
print(f"Complexity: {analysis.complexity_score}")

# Prepare data for Stage 2 chunking
from stage1 import prepare_for_stage2
stage2_data = prepare_for_stage2(markdown_text)
print(f"Chunking recommendations: {stage2_data['recommendations']}")
```

## 🧱 Core Components

### 1. Main Interface (`stage1.interface`)
- **Purpose**: Primary entry point for Stage 1 functionality
- **Key Class**: `Stage1Interface`
- **Main Function**: `process_markdown()`, `prepare_for_stage2()`
- **Documentation**: [Interface Guide](interface.md)

### 2. Markdown AST (`stage1.markdown_ast`)
- **Purpose**: Unified Markdown parsing with multiple parser support
- **Key Functions**: `parse_to_ast()`, `get_best_parser()`
- **Parsers**: markdown-it-py, mistune, commonmark
- **Documentation**: [AST Guide](markdown-ast.md)

### 3. Fenced Block Extractor (`stage1.fenced_block_extractor`)
- **Purpose**: Extract and analyze code blocks with nesting support
- **Key Functions**: `extract_fenced_blocks()`
- **Features**: Nesting, multiple fence types, language detection
- **Documentation**: [Fenced Blocks Guide](fenced-blocks.md)

### 4. Element Detector (`stage1.element_detector`)
- **Purpose**: Detect structural elements (headers, lists, tables)
- **Key Functions**: `detect_elements()`
- **Elements**: Headers, lists, tables, blockquotes, horizontal rules
- **Documentation**: [Elements Guide](elements.md)

### 5. Content Analyzer (`stage1.content_analyzer`)
- **Purpose**: Analyze content characteristics and metrics
- **Key Functions**: `analyze_content()`
- **Metrics**: Content type, complexity, language distribution
- **Documentation**: [Content Analysis Guide](content_analysis.md)

### 6. Configuration (`stage1.config`)
- **Purpose**: Flexible configuration system
- **Key Classes**: `Stage1Config`, `ParserConfig`, `ExtractorConfig`
- **Features**: Component configs, profiles, validation
- **Documentation**: [Configuration Guide](configuration.md)

### 7. Types (`stage1.types`)
- **Purpose**: Core data structures and types
- **Key Classes**: `MarkdownNode`, `FencedBlock`, `Header`, `List`, `Table`
- **Features**: Position tracking, hierarchy, validation
- **Documentation**: [Types Reference](types.md)

## 📖 Detailed Guides

Each component has comprehensive documentation with examples and integration patterns:

- **[🔧 Interface Guide](interface.md)** - Main API, convenience functions, Stage 2 integration
- **[🌳 AST Guide](markdown-ast.md)** - Parser selection, AST manipulation, position tracking
- **[📦 Fenced Blocks Guide](fenced-blocks.md)** - Code extraction, nesting, language detection
- **[🔍 Elements Guide](elements.md)** - Structural detection, hierarchy, anchor generation
- **[📊 Content Analysis Guide](content_analysis.md)** - Metrics, patterns, chunking recommendations
- **[⚙️ Configuration Guide](configuration.md)** - Setup, profiles, performance tuning
- **[📋 Types Reference](types.md)** - Data structures, methods, validation

## 🎯 For Stage 2 Developers

Stage 1 provides everything needed for chunking implementation:

### Complete Document Processing

```python
from stage1 import Stage1Interface

interface = Stage1Interface()
result = interface.process_document(markdown_text)

# Full parsed data available:
# - result.ast_nodes: Complete AST for structural analysis
# - result.fenced_blocks: Code blocks with metadata and positions
# - result.headers: Header hierarchy with anchors
# - result.lists: List structures with nesting
# - result.tables: Table data with alignment
# - result.content_analysis: Content characteristics and metrics
```

### Optimized Stage 2 Data

```python
from stage1 import prepare_for_stage2

# Get structured data optimized for chunking
data = prepare_for_stage2(markdown_text)

# Returns:
# - data['ast']: AST nodes for structural analysis
# - data['blocks']: Code blocks for preservation
# - data['elements']: All structural elements
# - data['analysis']: Content analysis and metrics
# - data['recommendations']: Chunking strategy recommendations
```

### Chunking Strategy Recommendations

```python
# Content analysis provides chunking guidance
analysis = result.content_analysis

if analysis.content_type == ContentType.CODE_HEAVY:
    # Use code-preserving chunking
    strategy = "preserve_code_blocks"
    chunk_size = 2000
elif analysis.content_type == ContentType.API_REFERENCE:
    # Use semantic section chunking
    strategy = "semantic_sections" 
    chunk_size = 1500
elif analysis.complexity_score > 0.7:
    # Use hierarchical chunking for complex content
    strategy = "hierarchical"
    chunk_size = 1000
else:
    # Use sliding window for simple content
    strategy = "sliding_window"
    chunk_size = 1200
```

### Integration Examples

```python
# Example Stage 2 integration pattern
from stage1 import prepare_for_stage2

def chunk_markdown(text: str, strategy: str = "auto"):
    # Get Stage 1 analysis
    stage1_data = prepare_for_stage2(text)
    
    # Choose strategy based on analysis
    if strategy == "auto":
        analysis = stage1_data['analysis']
        strategy = analysis.recommended_strategy
    
    # Use Stage 1 data for chunking
    if strategy == "preserve_code_blocks":
        return chunk_preserving_code(stage1_data)
    elif strategy == "semantic_sections":
        return chunk_by_sections(stage1_data)
    elif strategy == "hierarchical":
        return chunk_hierarchically(stage1_data)
    else:
        return chunk_sliding_window(stage1_data)
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
make test

# Generate coverage report
make coverage

# Check code quality
make lint

# Run performance benchmarks
make benchmark

# Test specific components
python -m pytest tests/test_interface.py
python -m pytest tests/test_fenced_blocks.py
python -m pytest tests/test_elements.py
```

## 📈 Performance

Stage 1 is optimized for performance with:

- **Parser selection**: Automatic best parser detection
- **Caching**: Results caching for repeated processing
- **Streaming**: Support for large document processing
- **Parallel processing**: Multi-document batch processing
- **Configuration profiles**: Performance vs feature trade-offs

## 🔧 Advanced Usage

### Custom Configuration

```python
from stage1.config import Stage1Config, ConfigProfiles

# Use predefined profiles
config = ConfigProfiles.fast_processing()        # Speed optimized
config = ConfigProfiles.comprehensive_analysis() # Feature complete
config = ConfigProfiles.code_focused()          # Code-heavy documents

# Custom configuration
config = Stage1Config(
    parser={"preferred_parser": "markdown-it-py"},
    extractor={"handle_nesting": True},
    analyzer={"analyze_languages": True}
)
```

### Batch Processing

```python
from stage1 import process_markdown

# Process multiple documents efficiently
documents = [doc1, doc2, doc3]
results = [process_markdown(doc) for doc in documents]

# Analyze document collection
total_code_blocks = sum(len(r.fenced_blocks) for r in results)
avg_complexity = sum(r.content_analysis.complexity_score for r in results) / len(results)
```
