# Troubleshooting

<cite>
**Referenced Files in This Document**
- [docs/guides/troubleshooting.md](file://docs/guides/troubleshooting.md)
- [tests/test_error_handling.py](file://tests/test_error_handling.py)
- [tests/chunker/test_error_types.py](file://tests/chunker/test_error_types.py)
- [tests/chunker/test_strategy_error_handling.py](file://tests/chunker/test_strategy_error_handling.py)
- [tests/chunker/test_performance.py](file://tests/chunker/test_performance.py)
- [tests/integration/test_dify_plugin_integration.py](file://tests/integration/test_dify_plugin_integration.py)
- [markdown_chunker_legacy/chunker/errors.py](file://markdown_chunker_legacy/chunker/errors.py)
- [markdown_chunker_legacy/api/error_handler.py](file://markdown_chunker_legacy/api/error_handler.py)
- [markdown_chunker_legacy/parser/validation.py](file://markdown_chunker_legacy/parser/validation.py)
- [examples/dify_integration.py](file://examples/dify_integration.py)
- [tests/parser/fixtures/edge_cases/mixed_fence_lengths.md](file://tests/parser/fixtures/edge_cases/mixed_fence_lengths.md)
- [tests/parser/fixtures/edge_cases/deep_nested_list.md](file://tests/parser/fixtures/edge_cases/deep_nested_list.md)
- [tests/parser/fixtures/edge_cases/nested_fences.md](file://tests/parser/fixtures/edge_cases/nested_fences.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Common Error Scenarios](#common-error-scenarios)
3. [Configuration Issues](#configuration-issues)
4. [Strategy Selection Problems](#strategy-selection-problems)
5. [Malformed Markdown Input](#malformed-markdown-input)
6. [Performance and Memory Issues](#performance-and-memory-issues)
7. [Dify Integration Problems](#dify-integration-problems)
8. [Edge Cases and Limitations](#edge-cases-and-limitations)
9. [Debugging Tools and Techniques](#debugging-tools-and-techniques)
10. [Testing and Isolation](#testing-and-isolation)
11. [Best Practices](#best-practices)

## Introduction

This troubleshooting guide addresses common issues encountered when using the Markdown chunker, particularly in production environments with Dify and other RAG systems. The chunker provides robust error handling and fallback mechanisms, but understanding common failure modes helps prevent issues and enables quick resolution.

## Common Error Scenarios

### Import and Setup Errors

**Problem**: `ModuleNotFoundError: No module named 'markdown_chunker'`

**Solution**:
- Verify virtual environment activation: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Check Python path configuration

### Empty Input Handling

**Problem**: Processing empty or whitespace-only content

**Solution**: The chunker handles empty input gracefully, but expects valid string input. Use validation before processing:

```python
# Validate input before chunking
if not input_text or not input_text.strip():
    # Handle empty input case
    return []
```

### Encoding Issues

**Problem**: Invalid character encoding in input text

**Solution**: Ensure input is properly encoded UTF-8. The chunker validates encoding automatically:

```python
# Automatic encoding validation
try:
    chunker.chunk(input_text)
except InvalidEncodingError as e:
    # Handle encoding issues
    logger.error(f"Encoding error: {e}")
```

**Section sources**
- [docs/guides/troubleshooting.md](file://docs/guides/troubleshooting.md#L1-L31)
- [markdown_chunker_legacy/chunker/errors.py](file://markdown_chunker_legacy/chunker/errors.py#L34-L46)

## Configuration Issues

### Invalid Configuration Values

**Problem**: Configuration parameters outside acceptable ranges

**Common Issues**:
- Negative chunk sizes
- Zero or negative overlap values
- Invalid strategy names
- Malformed configuration objects

**Solution**: Use the ChunkConfig class with validation:

```python
from markdown_chunker import ChunkConfig

# Valid configuration
config = ChunkConfig(
    max_chunk_size=1000,
    min_chunk_size=100,
    overlap_size=100,
    enable_overlap=True
)

# Invalid configuration will raise ValidationError
try:
    config = ChunkConfig(max_chunk_size=-100)
except ValidationError as e:
    logger.error(f"Configuration error: {e}")
```

### Strategy Configuration Problems

**Problem**: Incorrect strategy selection or configuration

**Solution**: Validate strategy names and configurations:

```python
# Check available strategies
chunker = MarkdownChunker()
available_strategies = chunker.get_available_strategies()

# Validate strategy before use
if strategy_name not in available_strategies:
    raise StrategyNotFoundError(strategy_name, available_strategies)
```

**Section sources**
- [tests/chunker/test_error_types.py](file://tests/chunker/test_error_types.py#L230-L272)
- [tests/chunker/test_strategy_error_handling.py](file://tests/chunker/test_strategy_error_handling.py#L19-L51)

## Strategy Selection Problems

### Strategy Not Found Errors

**Problem**: Requested strategy doesn't exist

**Error Pattern**: `StrategyNotFoundError: Strategy 'invalid_name' not found. Available strategies: code, mixed, list, table, structural, sentences`

**Solution**: 
1. Check available strategies: `chunker.get_available_strategies()`
2. Use case-sensitive strategy names
3. Validate strategy names before processing

```python
# Safe strategy selection
def safe_strategy_selection(chunker, strategy_name):
    available = chunker.get_available_strategies()
    if strategy_name not in available:
        raise StrategyNotFoundError(strategy_name, available)
    return strategy_name
```

### Strategy Execution Failures

**Problem**: Strategy fails during processing

**Error Types**:
- `StrategyFailedError`: Strategy execution failed with original exception
- `NoStrategyCanHandleError`: No strategy can handle the content type

**Solution**: The chunker automatically falls back to alternative strategies:

```python
# Automatic fallback handling
try:
    result = chunker.chunk_with_analysis(content, strategy="code")
    if result.fallback_used:
        logger.warning(f"Used fallback strategy: {result.strategy_used}")
        logger.warning(f"Fallback level: {result.fallback_level}")
except StrategyFailedError as e:
    logger.error(f"Strategy failed: {e}")
    # Handle specific strategy failure
```

**Section sources**
- [tests/chunker/test_strategy_error_handling.py](file://tests/chunker/test_strategy_error_handling.py#L19-L175)
- [markdown_chunker_legacy/chunker/errors.py](file://markdown_chunker_legacy/chunker/errors.py#L72-L108)

## Malformed Markdown Input

### Unclosed Code Blocks

**Problem**: Markdown with unclosed code fences

**Error Pattern**: Parser detects unclosed fences and may fail to process

**Solution**: The parser attempts to recover from malformed input:

```python
# Test input before processing
from markdown_chunker.parser.validation import validate_and_normalize_input

try:
    validated_input = validate_and_normalize_input(raw_markdown)
    result = chunker.chunk(validated_input)
except Exception as e:
    logger.error(f"Input validation failed: {e}")
    # Handle malformed input
```

### Mixed Fence Lengths

**Problem**: Conflicting fence lengths (e.g., ``` vs ~~~)

**Known Issue**: Mixed fence lengths can cause parsing confusion

**Workaround**: Standardize fence lengths before processing:

```python
# Normalize fence lengths
def standardize_fences(markdown):
    # Replace all ~~~ with ```
    markdown = markdown.replace('~~~', '```')
    return markdown
```

**Section sources**
- [tests/parser/fixtures/edge_cases/mixed_fence_lengths.md](file://tests/parser/fixtures/edge_cases/mixed_fence_lengths.md#L1-L19)
- [markdown_chunker_legacy/parser/validation.py](file://markdown_chunker_legacy/parser/validation.py#L36-L89)

## Performance and Memory Issues

### Large Document Processing

**Problem**: Memory usage and processing time with large documents

**Performance Monitoring**: Enable performance monitoring to track metrics:

```python
# Enable performance monitoring
chunker = MarkdownChunker(enable_performance_monitoring=True)

# Process large document
result = chunker.chunk_with_analysis(large_document)

# Check performance metrics
stats = chunker.get_performance_stats()
logger.info(f"Processing time: {stats.get('total_time', 0):.2f}s")
logger.info(f"Strategy used: {result.strategy_used}")
```

### Memory Optimization Strategies

**Problem**: High memory usage with large documents

**Solutions**:
1. Use streaming processing for very large documents
2. Adjust chunk sizes to balance memory and context
3. Enable caching judiciously

```python
# Optimized configuration for large documents
config = ChunkConfig(
    max_chunk_size=2000,  # Smaller chunks reduce memory usage
    min_chunk_size=500,
    overlap_size=200,     # Reasonable overlap
    enable_overlap=True
)

# Monitor memory usage
import psutil
memory_before = psutil.Process().memory_info().rss / 1024 / 1024
result = chunker.chunk_with_analysis(large_document)
memory_after = psutil.Process().memory_info().rss / 1024 / 1024
logger.info(f"Memory delta: {memory_after - memory_before:.2f} MB")
```

### Timeout and Resource Limits

**Problem**: Processing timeouts or resource exhaustion

**Monitoring and Limits**:
```python
import signal
import time

def timeout_handler(signum, frame):
    raise TimeoutError("Chunking operation timed out")

# Set timeout for processing
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout

try:
    result = chunker.chunk_with_analysis(document)
except TimeoutError as e:
    logger.error(f"Processing timeout: {e}")
finally:
    signal.alarm(0)  # Cancel timeout
```

**Section sources**
- [tests/chunker/test_performance.py](file://tests/chunker/test_performance.py#L295-L448)

## Dify Integration Problems

### Plugin Registration Issues

**Problem**: Plugin not appearing in Dify interface

**Solution**:
1. Verify plugin installation in Dify settings → Plugins
2. Check plugin status is "Active"
3. Restart Dify server if needed
4. Verify plugin configuration in `manifest.yaml`

### API Compatibility Issues

**Problem**: Dify API format mismatches

**Common Issues**:
- Unexpected parameter formats
- Missing required fields
- Metadata format inconsistencies

**Solution**: Use the API adapter for compatibility:

```python
from markdown_chunker.api import APIAdapter, APIRequest

# Create compatible request
request = APIRequest(
    content=document_content,
    config={
        "max_chunk_size": 1536,
        "strategy": "auto",
        "include_metadata": True
    }
)

# Process through adapter
adapter = APIAdapter()
response = adapter.process_request(request)

if response.success:
    # Process chunks for Dify
    for chunk in response.chunks:
        # Format for Dify output
        formatted_chunk = {
            "content": chunk.content,
            "metadata": {
                "chunk_id": f"chunk_{chunk.start_line}_{chunk.end_line}",
                "lines": f"{chunk.start_line}-{chunk.end_line}",
                "size": chunk.size,
                "type": chunk.content_type
            }
        }
        # Send to Dify
```

### Metadata Filtering Problems

**Problem**: Excessive metadata in Dify output

**Solution**: Configure metadata filtering:

```python
# Filter metadata for Dify
filtered_metadata = {
    k: v for k, v in chunk.metadata.items()
    if not k.startswith(('char_count', 'line_count', 'word_count'))
}

# Remove boolean fields that should be True
filtered_metadata = {
    k: v for k, v in filtered_metadata.items()
    if not (k.startswith(('is_', 'has_')) and v is False)
}
```

**Section sources**
- [tests/integration/test_dify_plugin_integration.py](file://tests/integration/test_dify_plugin_integration.py#L1-L398)
- [examples/dify_integration.py](file://examples/dify_integration.py#L1-L487)

## Edge Cases and Limitations

### Deeply Nested Structures

**Problem**: Deeply nested lists or code blocks

**Limitation**: Maximum nesting depth may be limited

**Workaround**: Process nested content separately or adjust nesting limits:

```python
# Test for deep nesting
def detect_deep_nesting(markdown):
    lines = markdown.split('\n')
    max_depth = 0
    current_depth = 0
    
    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        
        if stripped.startswith('- ') or stripped.startswith('* ') or stripped.startswith('+ '):
            current_depth = indent // 2 + 1
            max_depth = max(max_depth, current_depth)
    
    return max_depth > 10  # Threshold for deep nesting

# Handle deep nesting specially
if detect_deep_nesting(content):
    # Split into smaller sections
    sections = split_into_sections(content)
    for section in sections:
        result = chunker.chunk(section)
        # Process each section
```

### Mixed Fence Lengths

**Problem**: Conflicting fence lengths in code blocks

**Known Issue**: The parser may struggle with inconsistent fence lengths

**Workaround**: Standardize fence lengths:

```python
def standardize_fences(markdown):
    """Convert all fence types to triple backticks"""
    # Replace ~~~ with ```
    markdown = re.sub(r'^\s*~~~', '```', markdown, flags=re.MULTILINE)
    
    # Replace ```lang with ```
    markdown = re.sub(r'^\s*```(\w+)', '```', markdown, flags=re.MULTILINE)
    
    return markdown
```

### Unclosed Code Blocks

**Problem**: Code blocks without closing fences

**Parser Behavior**: The parser attempts to recover but may produce unexpected results

**Detection and Workaround**:
```python
def detect_unclosed_blocks(markdown):
    """Detect potential unclosed code blocks"""
    fences = []
    for line in markdown.split('\n'):
        if line.strip().startswith('```'):
            if line.strip() in fences:
                fences.remove(line.strip())
            else:
                fences.append(line.strip())
    
    return len(fences) > 0

# Handle unclosed blocks
if detect_unclosed_blocks(content):
    # Try to close blocks manually or warn user
    logger.warning("Potential unclosed code blocks detected")
```

**Section sources**
- [tests/parser/fixtures/edge_cases/deep_nested_list.md](file://tests/parser/fixtures/edge_cases/deep_nested_list.md#L1-L9)
- [tests/parser/fixtures/edge_cases/nested_fences.md](file://tests/parser/fixtures/edge_cases/nested_fences.md#L1-L9)

## Debugging Tools and Techniques

### Verbose Logging Configuration

**Enable Debug Logging**:
```python
import logging
from markdown_chunker.logging_config import setup_logging

# Configure debug logging
logger = setup_logging(level="DEBUG")

# Enable chunker-specific logging
chunker = MarkdownChunker()
chunker.logger.setLevel(logging.DEBUG)
```

### Error Message Analysis

**Understanding Error Messages**: The chunker provides detailed error information:

```python
try:
    result = chunker.chunk(content, strategy="code")
except StrategyFailedError as e:
    # Analyze error details
    logger.error(f"Strategy: {e.strategy_name}")
    logger.error(f"Reason: {e.reason}")
    logger.error(f"Content preview: {e.content_preview}")
    
    # Check original exception
    if hasattr(e, 'original_error'):
        logger.error(f"Original error: {e.original_error}")
```

### Performance Profiling

**Monitor Performance Metrics**:
```python
# Enable performance monitoring
chunker = MarkdownChunker(enable_performance_monitoring=True)

# Process document
result = chunker.chunk_with_analysis(document)

# Analyze performance
stats = chunker.get_performance_stats()
logger.info(f"Total time: {stats.get('total_time', 0):.3f}s")
logger.info(f"Strategy: {result.strategy_used}")
logger.info(f"Chunks: {len(result.chunks)}")

# Check strategy-specific metrics
strategy_stats = stats.get('strategy_execution', {})
for strategy, timing in strategy_stats.items():
    logger.info(f"Strategy {strategy}: {timing['time']:.3f}s")
```

### Error Handler Integration

**Standardized Error Handling**:
```python
from markdown_chunker.api.error_handler import APIErrorHandler

# Create error handler
error_handler = APIErrorHandler(include_traceback=True)

try:
    result = chunker.chunk(content)
except Exception as e:
    # Handle through error handler
    response = error_handler.handle_exception(e, context={"document_id": "123"})
    logger.error(f"Error response: {response}")
```

**Section sources**
- [markdown_chunker_legacy/api/error_handler.py](file://markdown_chunker_legacy/api/error_handler.py#L1-L235)
- [tests/test_error_handling.py](file://tests/test_error_handling.py#L1-L111)

## Testing and Isolation

### Test Suite Usage

**Run Specific Test Categories**:
```bash
# Run error handling tests
pytest tests/test_error_handling.py -v

# Run strategy error handling tests
pytest tests/chunker/test_strategy_error_handling.py -v

# Run performance tests
pytest tests/chunker/test_performance.py -v

# Run Dify integration tests
pytest tests/integration/test_dify_plugin_integration.py -v
```

### Isolating Problematic Documents

**Document Type Testing**:
```python
# Test different document types
test_documents = {
    "simple": "# Simple\nContent",
    "code_heavy": "# Code\n```python\ndef func():\n    pass\n```",
    "list_heavy": "# Lists\n- Item 1\n- Item 2\n- Item 3",
    "table_heavy": "# Tables\n| Col1 | Col2 |\n|------|------|\n| A    | B    |",
    "edge_case": "# Edge Case\nNested ```code``` blocks"
}

for name, content in test_documents.items():
    try:
        result = chunker.chunk(content)
        logger.info(f"{name}: {len(result)} chunks")
    except Exception as e:
        logger.error(f"{name} failed: {e}")
```

### Regression Testing

**Validate Fix Results**:
```python
# Test edge cases after fixes
edge_cases = [
    "tests/parser/fixtures/edge_cases/mixed_fence_lengths.md",
    "tests/parser/fixtures/edge_cases/deep_nested_list.md",
    "tests/parser/fixtures/edge_cases/nested_fences.md"
]

for case_file in edge_cases:
    with open(case_file, 'r') as f:
        content = f.read()
    
    try:
        result = chunker.chunk(content)
        logger.info(f"{case_file}: SUCCESS - {len(result)} chunks")
    except Exception as e:
        logger.error(f"{case_file}: FAILED - {e}")
```

**Section sources**
- [tests/test_error_handling.py](file://tests/test_error_handling.py#L1-L111)
- [tests/chunker/test_performance.py](file://tests/chunker/test_performance.py#L1-L448)

## Best Practices

### Error Handling Patterns

**Robust Error Handling**:
```python
from markdown_chunker.chunker.errors import (
    StrategyError, 
    InputValidationError, 
    ChunkingError
)

def safe_chunking(chunker, content, strategy=None):
    """Safe chunking with comprehensive error handling"""
    try:
        # Validate input
        if not content or not content.strip():
            return [], "Empty input"
        
        # Try primary strategy
        result = chunker.chunk_with_analysis(content, strategy=strategy)
        
        if result.fallback_used:
            logger.warning(f"Fallback used: {result.strategy_used}")
            logger.warning(f"Fallback level: {result.fallback_level}")
        
        return result.chunks, None
        
    except StrategyNotFoundError as e:
        logger.error(f"Invalid strategy: {e}")
        # Fall back to automatic selection
        return safe_chunking(chunker, content, strategy=None)
        
    except StrategyFailedError as e:
        logger.error(f"Strategy failed: {e}")
        # Try alternative strategy
        if strategy != "sentences":
            return safe_chunking(chunker, content, strategy="sentences")
        return [], f"Chunking failed: {e}"
        
    except InputValidationError as e:
        logger.error(f"Invalid input: {e}")
        return [], f"Invalid input: {e}"
        
    except ChunkingError as e:
        logger.error(f"Chunking error: {e}")
        return [], f"Chunking error: {e}"
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return [], f"Unexpected error: {e}"
```

### Configuration Best Practices

**Production Configuration**:
```python
# Production-ready configuration
production_config = ChunkConfig(
    max_chunk_size=1536,  # Optimal for embeddings
    min_chunk_size=200,
    overlap_size=200,     # Preserve context
    enable_overlap=True,
    enable_performance_monitoring=True
)

# Environment-specific configurations
configs = {
    "development": ChunkConfig(max_chunk_size=500, enable_overlap=False),
    "production": production_config,
    "testing": ChunkConfig(max_chunk_size=1000, enable_overlap=True)
}

# Select configuration based on environment
environment = os.getenv("ENVIRONMENT", "development")
config = configs[environment]
chunker = MarkdownChunker(config)
```

### Monitoring and Alerting

**Implementation Monitoring**:
```python
class ChunkingMonitor:
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.performance_stats = []
    
    def log_error(self, error_type, context=None):
        self.error_counts[error_type] += 1
        if self.error_counts[error_type] > 10:  # Threshold
            self.send_alert(f"High error rate: {error_type}")
    
    def log_performance(self, processing_time, chunk_count):
        self.performance_stats.append({
            "time": processing_time,
            "chunks": chunk_count,
            "timestamp": time.time()
        })
        
        # Alert on performance degradation
        if processing_time > 5.0 and chunk_count > 10:
            self.send_alert(f"Slow processing: {processing_time:.2f}s for {chunk_count} chunks")
    
    def send_alert(self, message):
        # Implement alerting (email, Slack, etc.)
        logger.error(f"ALERT: {message}")

# Usage
monitor = ChunkingMonitor()

try:
    result = chunker.chunk_with_analysis(content)
    monitor.log_performance(result.processing_time, len(result.chunks))
except Exception as e:
    monitor.log_error(type(e).__name__)
    raise
```

### Documentation and Maintenance

**Keep Documentation Updated**:
- Document known limitations and workarounds
- Maintain error handling patterns
- Update troubleshooting guides with new issues
- Monitor error rates and fix recurring problems

**Regular Testing**:
- Run comprehensive test suites periodically
- Test edge cases regularly
- Validate performance metrics
- Update configurations based on usage patterns

This comprehensive troubleshooting guide provides solutions for the most common issues encountered with the Markdown chunker, along with debugging techniques and best practices for reliable operation in production environments.