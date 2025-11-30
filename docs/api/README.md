# API Reference

Complete API documentation for Python Markdown Chunker v1.0.0.

## Table of Contents

- [Main API](#main-api)
- [Configuration](#configuration)
- [Data Types](#data-types)
- [Parser API](#parser-api)
- [API Adapters](#api-adapters)
- [Error Handling](#error-handling)
- [JSON Schemas](#json-schemas)

---

## Main API

### MarkdownChunker

Main class for chunking markdown documents.

```python
from markdown_chunker import MarkdownChunker
```

#### Constructor

```python
MarkdownChunker(config: ChunkConfig = None)
```

**Parameters:**
- `config` (ChunkConfig, optional): Configuration for chunking. Defaults to `ChunkConfig()`.

**Example:**
```python
from markdown_chunker import MarkdownChunker, ChunkConfig

config = ChunkConfig(max_chunk_size=2048)
chunker = MarkdownChunker(config)
```

#### Methods

##### chunk_with_analysis()

Chunk markdown content with full analysis and metadata.

```python
chunk_with_analysis(text: str) -> ChunkingResult
```

**Parameters:**
- `text` (str): Markdown content to chunk

**Returns:**
- `ChunkingResult`: Complete chunking result with metadata

**Example:**
```python
result = chunker.chunk_with_analysis("# Hello\n\nWorld")
print(f"Strategy: {result.strategy_used}")
print(f"Chunks: {len(result.chunks)}")
```

##### chunk_simple()

Simplified chunking that returns dictionaries instead of objects.

```python
chunk_simple(text: str, config: dict = None) -> dict
```

**Parameters:**
- `text` (str): Markdown content to chunk
- `config` (dict, optional): Configuration as dictionary

**Returns:**
- `dict`: Chunking result as dictionary

**Example:**
```python
result = chunker.chunk_simple("# Hello\n\nWorld")
print(result['chunks'][0]['content'])
print(result['strategy_used'])
```

---

### Convenience Functions

#### chunk_text()

Quick function to chunk markdown text.

```python
from markdown_chunker import chunk_text

chunks = chunk_text(text: str, config: ChunkConfig = None) -> list[Chunk]
```

**Parameters:**
- `text` (str): Markdown content
- `config` (ChunkConfig, optional): Configuration

**Returns:**
- `list[Chunk]`: List of chunks

**Example:**
```python
chunks = chunk_text("# Hello\n\nWorld")
for chunk in chunks:
    print(chunk.content)
```

#### chunk_file()

Quick function to chunk markdown file.

```python
from markdown_chunker import chunk_file

chunks = chunk_file(file_path: str, config: ChunkConfig = None) -> list[Chunk]
```

**Parameters:**
- `file_path` (str): Path to markdown file
- `config` (ChunkConfig, optional): Configuration

**Returns:**
- `list[Chunk]`: List of chunks

**Example:**
```python
chunks = chunk_file("document.md")
print(f"Created {len(chunks)} chunks")
```

---

## Configuration

### ChunkConfig

Configuration for chunking behavior.

```python
from markdown_chunker import ChunkConfig
```

#### Constructor

```python
ChunkConfig(
    max_chunk_size: int = 4096,
    min_chunk_size: int = 512,
    overlap_size: int = 200,
    enable_overlap: bool = True,
    code_ratio_threshold: float = 0.7,
    list_count_threshold: int = 5,
    table_count_threshold: int = 3,
    min_complexity: float = 0.3
)
```

**Parameters:**
- `max_chunk_size` (int): Maximum chunk size in characters
- `min_chunk_size` (int): Minimum chunk size in characters
- `overlap_size` (int): Overlap size between chunks
- `enable_overlap` (bool): Enable chunk overlap
- `code_ratio_threshold` (float): Threshold for code content ratio (0.0-1.0)
- `list_count_threshold` (int): Minimum list items for list strategy
- `table_count_threshold` (int): Minimum tables for table strategy
- `min_complexity` (float): Minimum complexity score (0.0-1.0)

#### Configuration Profiles

Pre-configured settings for common use cases.

##### for_api_docs()

Optimized for API documentation.

```python
config = ChunkConfig.for_api_docs()
```

**Settings:**
- max_chunk_size: 3072
- min_chunk_size: 256
- overlap_size: 150
- code_ratio_threshold: 0.6

##### for_code_docs()

Optimized for code documentation.

```python
config = ChunkConfig.for_code_docs()
```

**Settings:**
- max_chunk_size: 2048
- min_chunk_size: 128
- enable_overlap: False
- code_ratio_threshold: 0.8

##### for_chat_context()

Optimized for chat/LLM context.

```python
config = ChunkConfig.for_chat_context()
```

**Settings:**
- max_chunk_size: 1536
- min_chunk_size: 200
- overlap_size: 200

##### for_search_indexing()

Optimized for search indexing.

```python
config = ChunkConfig.for_search_indexing()
```

**Settings:**
- max_chunk_size: 1024
- min_chunk_size: 100
- overlap_size: 100

##### for_large_documents()

Optimized for large documents.

```python
config = ChunkConfig.for_large_documents()
```

**Settings:**
- max_chunk_size: 6144
- min_chunk_size: 1024
- overlap_size: 300

#### Serialization

```python
# To dictionary
config_dict = config.to_dict()

# From dictionary
config = ChunkConfig.from_dict(config_dict)
```

---

## Data Types

### Chunk

Represents a single chunk of markdown content.

```python
from markdown_chunker import Chunk
```

#### Properties

- `content` (str): Chunk content
- `start_line` (int): Starting line number (1-based)
- `end_line` (int): Ending line number (1-based)
- `size` (int): Size in characters
- `content_type` (str): Type of content (e.g., "code", "mixed", "text")
- `metadata` (dict): Additional metadata

#### Methods

```python
# Serialization
chunk_dict = chunk.to_dict()
chunk = Chunk.from_dict(chunk_dict)
```

#### Example

```python
chunk = chunks[0]
print(f"Content: {chunk.content}")
print(f"Lines: {chunk.start_line}-{chunk.end_line}")
print(f"Size: {chunk.size} characters")
print(f"Type: {chunk.content_type}")
```

### ChunkingResult

Complete result of chunking operation.

```python
from markdown_chunker import ChunkingResult
```

#### Properties

- `chunks` (list[Chunk]): List of chunks
- `strategy_used` (str): Strategy that was used
- `processing_time` (float): Processing time in seconds
- `statistics` (dict): Chunking statistics
- `metadata` (dict): Additional metadata

#### Methods

```python
# Serialization
result_dict = result.to_dict()
result = ChunkingResult.from_dict(result_dict)
```

#### Example

```python
result = chunker.chunk_with_analysis(markdown)
print(f"Strategy: {result.strategy_used}")
print(f"Chunks: {len(result.chunks)}")
print(f"Time: {result.processing_time:.3f}s")
print(f"Stats: {result.statistics}")
```

---

## Parser API

### ParserInterface

Interface for content analysis and parsing.

```python
from markdown_chunker import ParserInterface
```

#### Constructor

```python
parser = ParserInterface()
```

#### Methods

##### process_document()

Analyze document structure and content.

```python
process_document(text: str) -> ParserResult
```

**Parameters:**
- `text` (str): Markdown content

**Returns:**
- `ParserResult`: Analysis results

**Example:**
```python
parser = ParserInterface()
results = parser.process_document(markdown)

print(f"Content type: {results.analysis.content_type}")
print(f"Complexity: {results.analysis.complexity_score}")
print(f"Code blocks: {len(results.fenced_blocks)}")
```

### ContentAnalysis

Content analysis results.

```python
from markdown_chunker import ContentAnalysis
```

#### Properties

- `content_type` (str): Detected content type
- `complexity_score` (float): Complexity score (0.0-1.0)
- `code_ratio` (float): Ratio of code content
- `list_count` (int): Number of lists
- `table_count` (int): Number of tables
- `header_count` (int): Number of headers

---

## API Adapters

### APIAdapter

Adapter for REST API integration.

```python
from markdown_chunker.api import APIAdapter
```

#### Constructor

```python
adapter = APIAdapter()
```

#### Methods

##### process_request()

Process an API request.

```python
process_request(request: APIRequest) -> APIResponse
```

**Parameters:**
- `request` (APIRequest): API request object

**Returns:**
- `APIResponse`: API response object

**Example:**
```python
from markdown_chunker.api import APIAdapter, APIRequest

adapter = APIAdapter()

request = APIRequest(
    content="# Hello\n\nWorld",
    config={"max_chunk_size": 2048},
    strategy="auto"
)

response = adapter.process_request(request)

if response.success:
    print(f"Chunks: {len(response.chunks)}")
else:
    print(f"Error: {response.error['message']}")
```

### APIRequest

API request data structure.

```python
from markdown_chunker.api import APIRequest
```

#### Constructor

```python
APIRequest(
    content: str,
    config: dict = None,
    strategy: str = "auto",
    metadata: dict = None
)
```

**Parameters:**
- `content` (str): Markdown content to chunk
- `config` (dict, optional): Configuration as dictionary
- `strategy` (str, optional): Strategy to use ("auto", "code", "mixed", etc.)
- `metadata` (dict, optional): Additional metadata

### APIResponse

API response data structure.

```python
from markdown_chunker.api import APIResponse
```

#### Properties

- `success` (bool): Whether request succeeded
- `chunks` (list[dict]): List of chunks as dictionaries
- `metadata` (dict): Response metadata
- `error` (dict, optional): Error information if failed

---

## Error Handling

### ErrorHandler

Centralized error handling.

```python
from markdown_chunker.utils import ErrorHandler
```

#### Constructor

```python
handler = ErrorHandler(logger=None)
```

**Parameters:**
- `logger` (logging.Logger, optional): Logger instance

#### Methods

##### handle_error()

Handle an error with consistent formatting.

```python
handle_error(
    error: Union[Exception, str],
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    context: dict = None,
    reraise: bool = True
) -> dict
```

**Parameters:**
- `error` (Exception | str): Error to handle
- `severity` (ErrorSeverity): Error severity
- `context` (dict, optional): Additional context
- `reraise` (bool): Whether to reraise exception

**Returns:**
- `dict`: Formatted error dictionary

##### handle_validation_error()

Handle validation errors.

```python
handle_validation_error(
    message: str,
    field: str = None,
    value: Any = None
) -> dict
```

##### get_summary()

Get error summary.

```python
get_summary() -> dict
```

**Returns:**
- `dict`: Summary with error and warning counts

**Example:**
```python
from markdown_chunker.utils import ErrorHandler, ValidationError

handler = ErrorHandler()

try:
    if not content:
        raise ValidationError("Content required", field="content")
except Exception as e:
    error_dict = handler.handle_error(e, reraise=False)
    
summary = handler.get_summary()
print(f"Errors: {summary['error_count']}")
```

### Custom Exceptions

#### ChunkingError

Base exception for chunking operations.

```python
from markdown_chunker.utils import ChunkingError

raise ChunkingError("Chunking failed", "CHUNK_001", {"detail": "info"})
```

#### ValidationError

Exception for validation errors.

```python
from markdown_chunker.utils import ValidationError

raise ValidationError("Invalid value", field="max_size")
```

#### ConfigurationError

Exception for configuration errors.

```python
from markdown_chunker.utils import ConfigurationError

raise ConfigurationError("Invalid config")
```

#### ProcessingError

Exception for processing errors.

```python
from markdown_chunker.utils import ProcessingError

raise ProcessingError("Processing failed")
```

---

## JSON Schemas

### Request Schema

```json
{
  "content": "string (required)",
  "config": {
    "max_chunk_size": "integer (optional, default: 4096)",
    "min_chunk_size": "integer (optional, default: 512)",
    "overlap_size": "integer (optional, default: 200)",
    "enable_overlap": "boolean (optional, default: true)",
    "code_ratio_threshold": "float (optional, default: 0.7)",
    "list_count_threshold": "integer (optional, default: 5)",
    "table_count_threshold": "integer (optional, default: 3)",
    "min_complexity": "float (optional, default: 0.3)"
  },
  "strategy": "string (optional, default: 'auto')",
  "metadata": "object (optional)"
}
```

### Response Schema (Success)

```json
{
  "success": true,
  "chunks": [
    {
      "content": "string",
      "start_line": "integer",
      "end_line": "integer",
      "size": "integer",
      "content_type": "string",
      "metadata": "object"
    }
  ],
  "metadata": {
    "strategy_used": "string",
    "processing_time": "float",
    "statistics": {
      "total_chunks": "integer",
      "total_size": "integer",
      "avg_chunk_size": "float"
    }
  }
}
```

### Response Schema (Error)

```json
{
  "success": false,
  "error": {
    "message": "string",
    "code": "string",
    "type": "string",
    "field": "string (optional)",
    "details": "object (optional)"
  }
}
```

### Example Request

```json
{
  "content": "# API Documentation\n\n## Overview\n\nThis is an API.",
  "config": {
    "max_chunk_size": 2048,
    "enable_overlap": true
  },
  "strategy": "auto"
}
```

### Example Response

```json
{
  "success": true,
  "chunks": [
    {
      "content": "# API Documentation\n\n## Overview\n\nThis is an API.",
      "start_line": 1,
      "end_line": 5,
      "size": 52,
      "content_type": "text",
      "metadata": {
        "strategy": "structural",
        "complexity": 0.2
      }
    }
  ],
  "metadata": {
    "strategy_used": "structural",
    "processing_time": 0.015,
    "statistics": {
      "total_chunks": 1,
      "total_size": 52,
      "avg_chunk_size": 52.0
    }
  }
}
```

---

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Input validation failed | 400 |
| `CONFIGURATION_ERROR` | Invalid configuration | 400 |
| `PROCESSING_ERROR` | Processing failed | 500 |
| `CHUNKING_ERROR` | Chunking operation failed | 500 |
| `CONTENT_EMPTY` | Content is empty | 400 |
| `CONTENT_TOO_LARGE` | Content exceeds size limit | 413 |
| `INVALID_STRATEGY` | Unknown strategy specified | 400 |
| `INVALID_CONFIG` | Configuration validation failed | 400 |

---

## Usage Examples

### Basic Chunking

```python
from markdown_chunker import MarkdownChunker

chunker = MarkdownChunker()
result = chunker.chunk_with_analysis("# Hello\n\nWorld")

for chunk in result.chunks:
    print(f"Chunk: {chunk.content}")
```

### With Configuration

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

config = ChunkConfig(
    max_chunk_size=2048,
    enable_overlap=True
)

chunker = MarkdownChunker(config)
result = chunker.chunk_with_analysis(markdown)
```

### Using Profiles

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

config = ChunkConfig.for_api_docs()
chunker = MarkdownChunker(config)
result = chunker.chunk_with_analysis(markdown)
```

### Simplified API

```python
from markdown_chunker import MarkdownChunker

chunker = MarkdownChunker()
result = chunker.chunk_simple("# Hello\n\nWorld")

print(result['chunks'][0]['content'])
print(result['strategy_used'])
```

### API Integration

```python
from markdown_chunker.api import APIAdapter, APIRequest

adapter = APIAdapter()

request = APIRequest(
    content="# Hello\n\nWorld",
    config={"max_chunk_size": 2048}
)

response = adapter.process_request(request)

if response.success:
    for chunk in response.chunks:
        print(chunk['content'])
```

### Error Handling

```python
from markdown_chunker import MarkdownChunker
from markdown_chunker.utils import ErrorHandler, ValidationError

handler = ErrorHandler()
chunker = MarkdownChunker()

try:
    if not content:
        raise ValidationError("Content required")
    result = chunker.chunk_with_analysis(content)
except Exception as e:
    error = handler.handle_error(e, reraise=False)
    print(f"Error: {error['message']}")
```

### Serialization

```python
from markdown_chunker import MarkdownChunker
import json

chunker = MarkdownChunker()
result = chunker.chunk_with_analysis("# Test")

# Serialize
result_dict = result.to_dict()
json_str = json.dumps(result_dict, indent=2)

# Deserialize
from markdown_chunker.chunker.types import ChunkingResult
restored = ChunkingResult.from_dict(result_dict)
```

---

## Version History

### v1.0.0 (Current)

- ✅ Restructured package (`markdown_chunker`)
- ✅ API adapters for REST integration
- ✅ Configuration profiles
- ✅ Simplified API (`chunk_simple()`)
- ✅ Full JSON serialization
- ✅ Centralized error handling
- ✅ Backward compatibility with `stage1`/`stage2`

---

## See Also

- [README.md](README.md) - Quick start and overview
- [MIGRATION.md](MIGRATION.md) - Migration guide from old structure
- [examples/](examples/) - Usage examples

---

**Last Updated:** November 9, 2025  
**Version:** 1.0.0
