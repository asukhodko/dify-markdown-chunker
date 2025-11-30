# Content Analysis Guide

## 🎯 Overview

The `stage1.content_analyzer` module provides comprehensive analysis of Markdown content characteristics, metrics, and patterns to help inform chunking strategies in Stage 2.

## 📋 Main Functions

### `analyze_content(md_text: str) -> ContentAnalysis`

Analyze Markdown content and return detailed metrics:

```python
from stage1.content_analyzer import analyze_content

markdown = """
# API Documentation

## Introduction
This API provides comprehensive access to our services with RESTful endpoints.

### Authentication
Use API keys for secure authentication:

```python
import requests

headers = {
    'Authorization': 'Bearer your-api-key',
    'Content-Type': 'application/json'
}

response = requests.get('https://api.example.com/users', headers=headers)
```

### Rate Limits
- 1000 requests per hour for free tier
- 10000 requests per hour for premium tier
- Burst limit: 100 requests per minute

| Tier | Hourly Limit | Burst Limit |
|------|--------------|-------------|
| Free | 1,000        | 100/min     |
| Pro  | 10,000       | 500/min     |
| Enterprise | Unlimited | 1000/min   |

## Error Handling

The API returns standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 429: Rate Limited
- 500: Server Error
"""

analysis = analyze_content(markdown)

# Basic metrics
print(f"Content type: {analysis.content_type}")
print(f"Total lines: {analysis.total_lines}")
print(f"Total characters: {analysis.total_characters}")
print(f"Word count: {analysis.word_count}")

# Content ratios
print(f"Code ratio: {analysis.code_ratio:.2%}")
print(f"Text ratio: {analysis.text_ratio:.2%}")
print(f"Whitespace ratio: {analysis.whitespace_ratio:.2%}")

# Complexity metrics
print(f"Complexity score: {analysis.complexity_score}")
print(f"Nesting depth: {analysis.max_nesting_depth}")
print(f"Structure score: {analysis.structure_score}")
```

## 🏗️ ContentAnalysis Structure

### Core Metrics

```python
from stage1.types import ContentAnalysis, ContentType

analysis = analyze_content(markdown_text)

# Content classification
print(f"Content type: {analysis.content_type}")  # ContentType enum
print(f"Primary language: {analysis.primary_language}")  # Most common code language
print(f"Is multilingual: {analysis.is_multilingual}")  # Multiple languages detected

# Size metrics
print(f"Total lines: {analysis.total_lines}")
print(f"Non-empty lines: {analysis.non_empty_lines}")
print(f"Total characters: {analysis.total_characters}")
print(f"Word count: {analysis.word_count}")
print(f"Average line length: {analysis.avg_line_length}")

# Content distribution
print(f"Code ratio: {analysis.code_ratio}")        # Proportion of code content
print(f"Text ratio: {analysis.text_ratio}")        # Proportion of text content
print(f"Whitespace ratio: {analysis.whitespace_ratio}")  # Proportion of whitespace
print(f"Header ratio: {analysis.header_ratio}")    # Proportion of headers
```

### Content Types

```python
from stage1.types import ContentType

# Available content types
ContentType.DOCUMENTATION    # Technical documentation
ContentType.TUTORIAL        # Step-by-step tutorials
ContentType.API_REFERENCE   # API documentation
ContentType.CODE_HEAVY      # Primarily code examples
ContentType.TEXT_HEAVY      # Primarily text content
ContentType.MIXED           # Balanced mix of content
ContentType.UNKNOWN         # Cannot determine type
```

### Complexity Metrics

```python
# Structural complexity
print(f"Complexity score: {analysis.complexity_score}")      # 0.0-1.0
print(f"Structure score: {analysis.structure_score}")        # 0.0-1.0
print(f"Max nesting depth: {analysis.max_nesting_depth}")    # Maximum list/quote nesting
print(f"Header depth: {analysis.header_depth}")              # Deepest header level

# Content patterns
print(f"Has code blocks: {analysis.has_code_blocks}")
print(f"Has tables: {analysis.has_tables}")
print(f"Has lists: {analysis.has_lists}")
print(f"Has images: {analysis.has_images}")
print(f"Has links: {analysis.has_links}")
```

### Language Analysis

```python
# Programming languages detected
print(f"Languages: {analysis.languages}")           # Dict[str, int] - language counts
print(f"Primary language: {analysis.primary_language}")  # Most common language
print(f"Language diversity: {analysis.language_diversity}")  # Number of different languages

# Language-specific metrics
for lang, count in analysis.languages.items():
    print(f"{lang}: {count} blocks")
```

## 🔍 Advanced Analysis

### ContentAnalyzer Class

For detailed analysis with custom configuration:

```python
from stage1.content_analyzer import ContentAnalyzer
from stage1.config import AnalyzerConfig

# Create analyzer with custom config
config = AnalyzerConfig(
    analyze_languages=True,
    detect_patterns=True,
    calculate_complexity=True,
    include_readability=True
)

analyzer = ContentAnalyzer(config)
analysis = analyzer.analyze_content(markdown_text)

# Get detailed metrics
detailed_metrics = analyzer.get_detailed_metrics()
print(f"Processing time: {detailed_metrics['processing_time']}")
print(f"Memory usage: {detailed_metrics['memory_usage']}")
```

### Pattern Detection

```python
# Detect common documentation patterns
patterns = analysis.detected_patterns

print(f"API documentation: {patterns.get('api_docs', False)}")
print(f"Tutorial format: {patterns.get('tutorial', False)}")
print(f"Reference manual: {patterns.get('reference', False)}")
print(f"Code examples: {patterns.get('code_examples', False)}")
print(f"FAQ format: {patterns.get('faq', False)}")
```

### Readability Metrics

```python
# Text readability analysis
readability = analysis.readability_metrics

print(f"Average sentence length: {readability.avg_sentence_length}")
print(f"Average word length: {readability.avg_word_length}")
print(f"Reading level: {readability.reading_level}")
print(f"Technical density: {readability.technical_density}")
```

## 📊 Chunking Recommendations

### Chunk Size Suggestions

```python
# Get chunking recommendations based on analysis
recommendations = analysis.get_chunking_recommendations()

print(f"Recommended chunk size: {recommendations.chunk_size}")
print(f"Overlap size: {recommendations.overlap_size}")
print(f"Split strategy: {recommendations.split_strategy}")
print(f"Preserve code blocks: {recommendations.preserve_code_blocks}")
print(f"Preserve tables: {recommendations.preserve_tables}")
```

### Content-Aware Splitting

```python
# Analyze splitting points
split_points = analysis.get_natural_split_points()

for point in split_points:
    print(f"Line {point.line}: {point.reason} (confidence: {point.confidence})")
```

## 🎯 Integration Examples

### With Fenced Block Extractor

```python
from stage1.content_analyzer import analyze_content
from stage1.fenced_block_extractor import extract_fenced_blocks

# Analyze content and extract blocks
analysis = analyze_content(markdown_text)
blocks = extract_fenced_blocks(markdown_text)

# Correlate analysis with extracted blocks
print(f"Analysis found {analysis.code_ratio:.1%} code content")
print(f"Extractor found {len(blocks)} code blocks")

# Language distribution
for lang, count in analysis.languages.items():
    actual_blocks = [b for b in blocks if b.language == lang]
    print(f"{lang}: analysis={count}, extracted={len(actual_blocks)}")
```

### With Element Detector

```python
from stage1.content_analyzer import analyze_content
from stage1.element_detector import detect_elements

# Analyze content and detect elements
analysis = analyze_content(markdown_text)
elements = detect_elements(markdown_text)

# Compare metrics
print(f"Analysis complexity: {analysis.complexity_score}")
print(f"Headers found: {len(elements.headers)} (depth: {analysis.header_depth})")
print(f"Lists found: {len(elements.lists)} (max nesting: {analysis.max_nesting_depth})")
print(f"Tables found: {len(elements.tables)}")
```

### For Stage 2 Chunking

```python
from stage1 import analyze_markdown

# Quick analysis for chunking decisions
analysis = analyze_markdown(markdown_text)

# Choose chunking strategy based on content
if analysis.content_type == ContentType.CODE_HEAVY:
    strategy = "preserve_code_blocks"
    chunk_size = 2000  # Larger chunks for code
elif analysis.content_type == ContentType.API_REFERENCE:
    strategy = "semantic_sections"
    chunk_size = 1500  # Medium chunks for API docs
elif analysis.complexity_score > 0.7:
    strategy = "hierarchical"
    chunk_size = 1000  # Smaller chunks for complex content
else:
    strategy = "sliding_window"
    chunk_size = 1200  # Default size

print(f"Recommended strategy: {strategy}")
print(f"Recommended chunk size: {chunk_size}")
```

## ⚡ Performance Optimization

### Caching Analysis Results

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_analyze(md_text: str) -> ContentAnalysis:
    return analyze_content(md_text)

# Use cached analysis for repeated content
analysis1 = cached_analyze(document1)
analysis2 = cached_analyze(document1)  # Uses cache
```

### Batch Analysis

```python
def analyze_multiple_documents(documents: List[str]) -> List[ContentAnalysis]:
    """Efficiently analyze multiple documents."""
    analyzer = ContentAnalyzer()
    results = []
    
    for doc in documents:
        analysis = analyzer.analyze_content(doc)
        results.append(analysis)
    
    return results

# Analyze document collection
analyses = analyze_multiple_documents(document_list)

# Aggregate statistics
total_words = sum(a.word_count for a in analyses)
avg_complexity = sum(a.complexity_score for a in analyses) / len(analyses)
```

## 🔧 Configuration Options

### AnalyzerConfig

```python
from stage1.config import AnalyzerConfig

config = AnalyzerConfig(
    # Feature toggles
    analyze_languages=True,          # Detect programming languages
    detect_patterns=True,            # Identify document patterns
    calculate_complexity=True,       # Compute complexity metrics
    include_readability=True,        # Calculate readability scores
    
    # Performance settings
    max_analysis_time=5.0,          # Maximum analysis time (seconds)
    enable_caching=True,            # Cache analysis results
    
    # Language detection
    min_code_block_size=10,         # Minimum size for language detection
    language_confidence_threshold=0.7,  # Confidence threshold for detection
    
    # Complexity calculation
    complexity_weights={            # Custom weights for complexity factors
        'nesting': 0.3,
        'code_ratio': 0.2,
        'structure': 0.3,
        'length': 0.2
    }
)

analyzer = ContentAnalyzer(config)
```

## 📈 Metrics Reference

### Score Interpretations

```python
# Complexity Score (0.0 - 1.0)
# 0.0 - 0.3: Simple content (plain text, basic formatting)
# 0.3 - 0.6: Moderate complexity (some code, lists, tables)
# 0.6 - 0.8: Complex content (nested structures, multiple languages)
# 0.8 - 1.0: Very complex (deep nesting, mixed content types)

# Structure Score (0.0 - 1.0)
# 0.0 - 0.3: Poor structure (no headers, flat content)
# 0.3 - 0.6: Basic structure (some headers, simple organization)
# 0.6 - 0.8: Good structure (clear hierarchy, well-organized)
# 0.8 - 1.0: Excellent structure (deep hierarchy, consistent formatting)

# Content Ratios (0.0 - 1.0)
# code_ratio: Proportion of content that is code
# text_ratio: Proportion of content that is prose text
# whitespace_ratio: Proportion of content that is whitespace/formatting
```