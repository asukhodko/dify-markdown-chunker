# Interface Guide

## 🎯 Overview

The `stage1.interface` module provides the main entry point for all Stage 1 functionality. It orchestrates all components and provides a clean API for Stage 2 integration.

## 📋 Main Classes

### `Stage1Interface`

The primary interface for document processing:

```python
from stage1.interface import Stage1Interface
from stage1.config import Stage1Config

# Create interface with default configuration
interface = Stage1Interface()

# Create interface with custom configuration
config = Stage1Config(
    parser={"preferred_parser": "markdown-it-py"},
    extractor={"include_positions": True},
    analyzer={"analyze_languages": True}
)
interface = Stage1Interface(config)
```

#### Methods

##### `process_document(md_text: str) -> Stage1Results`

Process a complete Markdown document and return all extracted data:

```python
markdown_text = """
# API Documentation

## Introduction
This API provides comprehensive access to our services.

### Authentication
Use API keys for secure authentication:

```python
import requests

headers = {
    'Authorization': 'Bearer your-api-key',
    'Content-Type': 'application/json'
}

response = requests.get('https://api.example.com/users', headers=headers)
print(response.json())
```

### Endpoints

#### Users
- `GET /users` - List all users
- `POST /users` - Create a new user
- `GET /users/{id}` - Get user by ID

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /users   | List users  |
| POST   | /users   | Create user |
| DELETE | /users/{id} | Delete user |

### Rate Limits
- Free tier: 1000 requests/hour
- Pro tier: 10000 requests/hour
- Enterprise: Unlimited

> **Note**: Rate limits are enforced per API key.
"""

result = interface.process_document(markdown_text)

# Access all extracted data
print(f"AST nodes: {len(result.ast_nodes)}")
print(f"Code blocks: {len(result.fenced_blocks)}")
print(f"Headers: {len(result.headers)}")
print(f"Lists: {len(result.lists)}")
print(f"Tables: {len(result.tables)}")
print(f"Content type: {result.content_analysis.content_type}")
print(f"Processing time: {result.processing_time:.3f}s")
```

##### `get_processing_summary() -> Dict[str, Any]`

Get summary of processing capabilities and configuration:

```python
summary = interface.get_processing_summary()

print(f"Parser: {summary['parser']['name']}")
print(f"Parser features: {summary['parser']['features']}")
print(f"Available components: {summary['components']}")
print(f"Configuration: {summary['config']}")
```

##### `validate_configuration() -> ValidationResult`

Validate the current configuration:

```python
validation = interface.validate_configuration()

if validation.is_valid:
    print("Configuration is valid")
else:
    print("Configuration issues:")
    for issue in validation.issues:
        print(f"  - {issue}")
```

## 📊 Result Structure

### `Stage1Results`

The complete result of document processing:

```python
from stage1.types import Stage1Results

# Result structure
@dataclass
class Stage1Results:
    # Core data
    ast_nodes: List[MarkdownNode]      # Full AST representation
    fenced_blocks: List[FencedBlock]   # Extracted code blocks
    headers: List[Header]              # Headers with hierarchy
    lists: List[List]                  # List structures
    tables: List[Table]                # Table data
    content_analysis: ContentAnalysis  # Content metrics and analysis
    
    # Metadata
    processing_time: float             # Total processing duration
    parser_used: str                   # Which parser was used
    config_used: Stage1Config          # Configuration that was used
    
    # Statistics
    total_elements: int                # Total elements found
    processing_stats: Dict[str, Any]   # Detailed processing statistics

# Access result data
result = interface.process_document(markdown_text)

# Basic information
print(f"Processed in {result.processing_time:.3f}s using {result.parser_used}")
print(f"Found {result.total_elements} total elements")

# Detailed statistics
stats = result.processing_stats
print(f"Parse time: {stats['parse_time']:.3f}s")
print(f"Extract time: {stats['extract_time']:.3f}s")
print(f"Detect time: {stats['detect_time']:.3f}s")
print(f"Analyze time: {stats['analyze_time']:.3f}s")
```

### Result Methods

```python
# Get summary of results
summary = result.get_summary()
print(f"Document summary: {summary}")

# Export results to different formats
json_data = result.to_json()
dict_data = result.to_dict()

# Get specific element types
code_blocks = result.get_code_blocks()
headers_by_level = result.get_headers_by_level(2)  # Get H2 headers
tables_with_headers = result.get_tables_with_headers()
```

## 🎯 Convenience Functions

### `process_markdown(md_text: str, config: Optional[Stage1Config] = None) -> Stage1Results`

Quick processing without creating interface instance:

```python
from stage1 import process_markdown

# Simple processing
result = process_markdown("# Hello\n\n```python\nprint('world')\n```")
print(f"Found {len(result.fenced_blocks)} code blocks")

# With custom configuration
from stage1.config import Stage1Config, ParserConfig

config = Stage1Config(
    parser=ParserConfig(preferred_parser="mistune")
)
result = process_markdown(markdown_text, config)
```

### `analyze_markdown(md_text: str) -> ContentAnalysis`

Quick content analysis only:

```python
from stage1 import analyze_markdown

analysis = analyze_markdown(markdown_text)
print(f"Content type: {analysis.content_type}")
print(f"Complexity: {analysis.complexity_score}")
print(f"Code ratio: {analysis.code_ratio:.2%}")
print(f"Primary language: {analysis.primary_language}")
```

### `prepare_for_stage2(md_text: str, config: Optional[Stage1Config] = None) -> Dict[str, Any]`

Prepare all data needed for Stage 2 chunking:

```python
from stage1 import prepare_for_stage2

# Get structured data optimized for chunking
data = prepare_for_stage2(markdown_text)

# Returns dictionary with:
# - 'ast': Full AST for structural analysis
# - 'blocks': Code blocks with metadata
# - 'elements': All detected elements
# - 'analysis': Content analysis
# - 'recommendations': Chunking recommendations

print(f"Chunking recommendations: {data['recommendations']}")
```

## 🔧 Error Handling

The interface provides robust error handling with specific exception types:

```python
from stage1.errors import Stage1Error, ParsingError, ExtractionError

try:
    result = interface.process_document(malformed_markdown)
except ParsingError as e:
    print(f"Parsing failed: {e}")
    print(f"Fallback parser used: {e.fallback_parser}")
except ExtractionError as e:
    print(f"Extraction failed: {e}")
    print(f"Partial results available: {e.partial_results}")
except Stage1Error as e:
    print(f"General Stage 1 error: {e}")

# Check for warnings
if result.has_warnings():
    for warning in result.get_warnings():
        print(f"Warning: {warning}")
```

### Graceful Degradation

```python
# Interface continues processing even with component failures
result = interface.process_document(problematic_markdown)

# Check what succeeded
if result.ast_nodes:
    print("AST parsing succeeded")
if result.fenced_blocks:
    print("Block extraction succeeded")
if result.content_analysis:
    print("Content analysis succeeded")

# Get processing report
report = result.get_processing_report()
for component, status in report.items():
    print(f"{component}: {status}")
```

## 🎯 Integration with Stage 2

The interface is designed for seamless Stage 2 integration:

```python
# Stage 1: Parse and analyze
interface = Stage1Interface()
result = interface.process_document(markdown_text)

# Stage 2: Use parsed data for chunking (example)
"""
from stage2 import MarkdownChunker

chunker = MarkdownChunker()
chunks = chunker.chunk_from_stage1_result(result)
"""

# Or use the prepared data
stage2_data = prepare_for_stage2(markdown_text)
# Pass stage2_data to Stage 2 chunking algorithms
```

### Stage 2 Data Format

```python
# The prepare_for_stage2 function returns structured data:
stage2_data = prepare_for_stage2(markdown_text)

# AST data for structural analysis
ast_data = stage2_data['ast']
print(f"Root node type: {ast_data['root']['type']}")
print(f"Total nodes: {len(ast_data['nodes'])}")

# Code blocks for preservation
blocks_data = stage2_data['blocks']
for block in blocks_data:
    print(f"Block at lines {block['start_line']}-{block['end_line']}: {block['language']}")

# Elements for semantic chunking
elements_data = stage2_data['elements']
print(f"Headers: {len(elements_data['headers'])}")
print(f"Lists: {len(elements_data['lists'])}")
print(f"Tables: {len(elements_data['tables'])}")

# Analysis for chunking strategy
analysis_data = stage2_data['analysis']
print(f"Recommended chunk size: {analysis_data['recommended_chunk_size']}")
print(f"Recommended strategy: {analysis_data['recommended_strategy']}")

# Chunking recommendations
recommendations = stage2_data['recommendations']
print(f"Preserve code blocks: {recommendations['preserve_code_blocks']}")
print(f"Respect headers: {recommendations['respect_headers']}")
print(f"Overlap size: {recommendations['overlap_size']}")
```

## 📈 Performance Monitoring

The interface includes comprehensive performance monitoring:

```python
# Get detailed performance metrics
result = interface.process_document(large_document)

print(f"Total processing time: {result.processing_time:.3f}s")

# Component-wise timing
stats = result.processing_stats
print(f"Parsing: {stats['parse_time']:.3f}s")
print(f"Extraction: {stats['extract_time']:.3f}s")
print(f"Detection: {stats['detect_time']:.3f}s")
print(f"Analysis: {stats['analyze_time']:.3f}s")

# Memory usage
print(f"Peak memory: {stats['peak_memory']}MB")
print(f"Final memory: {stats['final_memory']}MB")

# Processing efficiency
efficiency = result.get_efficiency_metrics()
print(f"Characters per second: {efficiency['chars_per_second']}")
print(f"Elements per second: {efficiency['elements_per_second']}")
```

### Benchmarking

```python
from stage1.benchmark import benchmark_interface

# Benchmark interface performance
documents = [doc1, doc2, doc3]  # List of test documents
configs = [config1, config2]    # List of configurations to test

results = benchmark_interface(documents, configs)

for config_name, metrics in results.items():
    print(f"Configuration: {config_name}")
    print(f"  Average time: {metrics['avg_time']:.3f}s")
    print(f"  Throughput: {metrics['throughput']} docs/sec")
    print(f"  Memory efficiency: {metrics['memory_efficiency']}")
```

## 🔧 Advanced Usage

### Custom Processing Pipeline

```python
from stage1.interface import Stage1Interface

class CustomStage1Interface(Stage1Interface):
    """Custom interface with additional processing steps."""
    
    def process_document(self, md_text: str) -> Stage1Results:
        # Pre-processing
        md_text = self.preprocess_text(md_text)
        
        # Standard processing
        result = super().process_document(md_text)
        
        # Post-processing
        result = self.postprocess_result(result)
        
        return result
    
    def preprocess_text(self, text: str) -> str:
        # Custom preprocessing logic
        return text.strip()
    
    def postprocess_result(self, result: Stage1Results) -> Stage1Results:
        # Custom postprocessing logic
        return result

# Use custom interface
custom_interface = CustomStage1Interface()
result = custom_interface.process_document(markdown_text)
```

### Streaming Processing

```python
from stage1.interface import Stage1Interface

def process_large_document_streaming(file_path: str, chunk_size: int = 10000):
    """Process large documents in chunks."""
    interface = Stage1Interface()
    
    with open(file_path, 'r') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            
            # Process chunk
            result = interface.process_document(chunk)
            
            # Yield results for streaming processing
            yield result

# Process large file
for chunk_result in process_large_document_streaming('large_doc.md'):
    print(f"Processed chunk with {len(chunk_result.ast_nodes)} nodes")
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor
from stage1.interface import Stage1Interface

def process_documents_parallel(documents: List[str], max_workers: int = 4):
    """Process multiple documents in parallel."""
    
    def process_single(doc: str):
        interface = Stage1Interface()
        return interface.process_document(doc)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_single, documents))
    
    return results

# Process multiple documents
documents = [doc1, doc2, doc3, doc4]
results = process_documents_parallel(documents)
```