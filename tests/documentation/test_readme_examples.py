#!/usr/bin/env python3
"""
Validate all documentation examples from README.md
"""


def test_basic_stage2_example():
    """Test the basic Stage 2 example from README"""
    print("Testing basic Stage 2 example...")

    from markdown_chunker.chunker import MarkdownChunker

    chunker = MarkdownChunker()
    result = chunker.chunk_with_analysis("# Test\n\nHello world!")

    assert len(result.chunks) > 0
    assert result.strategy_used is not None
    print(
        f"✅ Success: Created {len(result.chunks)} chunks using {result.strategy_used} strategy"
    )


def test_stage1_basic_example():
    """Test the basic Stage 1 example from README"""
    print("Testing basic Stage 1 example...")

    from markdown_chunker.parser import extract_fenced_blocks

    blocks = extract_fenced_blocks('```python\nprint("hello")\n```')

    assert len(blocks) == 1
    assert blocks[0].language == "python"
    print(f"✅ Stage 1: Found {len(blocks)} code blocks")


def test_comprehensive_stage2_example():
    """Test the comprehensive Stage 2 example from README"""
    print("Testing comprehensive Stage 2 example...")

    from markdown_chunker.chunker import MarkdownChunker

    # Create chunker with default configuration
    chunker = MarkdownChunker()

    # Chunk markdown content
    markdown = """# API Documentation

## Authentication
Use API keys for authentication.

```python
import requests

def authenticate(api_key):
    headers={"Authorization": f"Bearer {api_key}"}
    return headers
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /users   | List users  |
| POST   | /users   | Create user |

### Rate Limits
- 1000 requests per hour
- 10 requests per second
"""

    # Get chunks with analysis
    result = chunker.chunk_with_analysis(markdown)

    assert len(result.chunks) > 0
    assert result.strategy_used is not None
    assert result.processing_time > 0

    print(f"Strategy used: {result.strategy_used}")
    print(f"Created {len(result.chunks)} chunks")
    print(f"Processing time: {result.processing_time:.3f}s")

    # Access individual chunks
    for i, chunk in enumerate(result.chunks):
        assert chunk.content_type is not None
        assert chunk.start_line > 0
        assert chunk.end_line >= chunk.start_line
        assert chunk.size > 0
        print(
            f"Chunk {i+1} ({chunk.content_type}): Lines {chunk.start_line}-{chunk.end_line}, Size: {chunk.size} characters"
        )


def test_stage1_interface_example():
    """Test the Stage 1 interface example from README"""
    print("Testing Stage 1 interface example...")

    from markdown_chunker.parser import Stage1Interface

    markdown = """# API Documentation

## Authentication
Use API keys for authentication.

```python
import requests

def authenticate(api_key):
    headers={"Authorization": f"Bearer {api_key}"}
    return headers
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /users   | List users  |
| POST   | /users   | Create user |
"""

    # Analyze document structure
    stage1 = Stage1Interface()
    results = stage1.process_document(markdown)

    assert results.analysis.content_type is not None
    assert results.analysis.complexity_score >= 0
    assert len(results.fenced_blocks) > 0
    assert len(results.elements.tables) > 0

    print(f"Content type: {results.analysis.content_type}")
    print(f"Complexity: {results.analysis.complexity_score:.2f}")
    print(f"Code blocks: {len(results.fenced_blocks)}")
    print(f"Lists: {len(results.elements.lists)}")
    print(f"Tables: {len(results.elements.tables)}")


def test_advanced_stage1_example():
    """Test the advanced Stage 1 example from README"""
    print("Testing advanced Stage 1 example...")

    from markdown_chunker.parser import (
        LineNumberConverter,
        extract_fenced_blocks,
        validate_and_normalize_input,
    )

    # Normalize input with different line endings
    raw_markdown = "```python\r\nprint('hello')\r\n```"
    normalized = validate_and_normalize_input(raw_markdown)
    blocks = extract_fenced_blocks(normalized)

    assert len(blocks) == 1
    assert blocks[0].language == "python"

    # Work with line numbers
    for block in blocks:
        # API uses 1-based line numbers
        assert block.start_line >= 1
        assert block.end_line >= block.start_line
        print(f"Block at lines {block.start_line}-{block.end_line}")

        # Convert to 0-based for internal processing if needed
        internal_start = LineNumberConverter.from_api_line_number(block.start_line)
        assert internal_start >= 0
        print(f"Internal start line: {internal_start}")

    # Handle nested blocks
    nested_markdown = """~~~markdown
# Documentation

```python
def example():
    return "nested code"
```
~~~"""

    blocks = extract_fenced_blocks(nested_markdown)
    assert len(blocks) == 1  # Should be 1 outer block containing nested content

    for block in blocks:
        print(f"Language: {block.language}, Nesting level: {block.nesting_level}")


def test_block_data_example():
    """Test the working with block data example from README"""
    print("Testing block data example...")

    from markdown_chunker.parser import extract_fenced_blocks

    markdown = """```python
def hello():
    print("Hello, World!")
```

~~~javascript
function greet() {
    console.log("Hello!");
}
~~~"""

    blocks = extract_fenced_blocks(markdown)
    assert len(blocks) == 2

    for block in blocks:
        # Basic properties
        assert block.language in ["python", "javascript"]
        assert len(block.content) > 0
        assert block.fence_type in ["```", "~~~"]

        # Position information (1-based)
        assert block.start_line >= 1
        assert block.end_line >= block.start_line

        # Nesting information
        assert block.nesting_level >= 0
        assert isinstance(block.is_closed, bool)

        print(f"Language: {block.language}")
        print(f"Content: {block.content[:50]}...")
        print(f"Fence type: {block.fence_type}")
        print(f"Start line: {block.start_line}")
        print(f"End line: {block.end_line}")
        print(f"Nesting level: {block.nesting_level}")
        print(f"Is closed: {block.is_closed}")
        print("---")


def test_verification_steps():
    """Test the verification steps from README"""
    print("Testing verification steps...")

    # Test Stage 1
    from markdown_chunker.parser import extract_fenced_blocks

    blocks = extract_fenced_blocks('```python\nprint("hello")\n```')
    assert len(blocks) == 1
    print(f"✅ Stage 1: Found {len(blocks)} code blocks")

    # Test Stage 2
    from markdown_chunker.chunker import MarkdownChunker

    chunker = MarkdownChunker()
    result = chunker.chunk_with_analysis("# Test\n\nContent here.")
    assert len(result.chunks) > 0
    print(f"✅ Stage 2: Created {len(result.chunks)} chunks")
    print("🎉 Setup complete!")


def main():
    """Run all documentation example validations"""
    print("🧪 Validating all README.md examples...\n")

    tests = [
        test_basic_stage2_example,
        test_stage1_basic_example,
        test_comprehensive_stage2_example,
        test_stage1_interface_example,
        test_advanced_stage1_example,
        test_block_data_example,
        test_verification_steps,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__} passed\n")
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}\n")
            failed += 1

    print(f"📊 Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All documentation examples are working correctly!")
        return True
    else:
        print("⚠️ Some documentation examples need fixing.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
