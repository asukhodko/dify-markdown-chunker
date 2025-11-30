"""
Test data for Stage 1 tests.

This module contains various Markdown samples for testing different components.
"""

# Simple Markdown for basic tests
SIMPLE_MARKDOWN = """# Simple Header

This is a simple paragraph with some text.

```python
def hello():
    print("Hello, World!")
```

- List item 1
- List item 2
  - Nested item

| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
"""

# Complex Markdown with various elements
COMPLEX_MARKDOWN = """# API Documentation

## Introduction

This API provides access to data processing services.

### Authentication

```bash
curl -H "Authorization: Bearer TOKEN" https://api.example.com
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| token | string | Access token |
| format | string | Response format |

### Examples

1. Get data:
   ```python
   import requests

   response=requests.get('https://api.example.com/data')
   print(response.json())
   ```

2. Send data:
   - Prepare JSON payload
   - Send POST request
   - Handle response

> **Note**: Always check response status.

## Error Handling

```javascript
try {
    const data=await fetch('/api/data');
    return data.json();
} catch (error) {
    console.error('Failed to fetch data:', error);
}
```

### Task List

- [x] Implement authentication
- [ ] Add rate limiting
- [ ] Write documentation
  - [x] API reference
  - [ ] Examples
"""

# Nested blocks for testing nesting support
NESTED_BLOCKS = """# Nested Blocks Example

Here's a markdown example with nested code blocks:

```markdown
# Example Documentation

```python
def example():
    return "nested code"
```

Text after the nested code block.
```

End of document.

```text
Another block with ~~~ inside:

~~~bash
echo "Hello from nested tilde block"
~~~
```
"""

# Edge cases for robustness testing
EDGE_CASES = {
    "empty": "",
    "whitespace_only": "   \n\n   ",
    "unclosed_block": (
        "```python\ndef unclosed():\n    print('This block is not closed')"
    ),
    "mixed_fences": """```python
print("Backtick block")
```

~~~bash
echo "Tilde block"
~~~""",
    "malformed_table": """| Header 1 | Header 2
|----------|
| Cell 1 | Cell 2 | Extra cell
| Missing cell |""",
    "empty_headers": """### Empty H3

## Empty H2

# Empty H1""",
    "very_long_line": "This is a very long line " + "that goes on and on " * 50,
    "special_chars": "Here are some special characters: `<>&\"'` and unicode: 🚀 ✨ 🎉",
    "multiple_consecutive_headers": """### Header 1
### Header 2
### Header 3""",
}

# Lists with various nesting levels
COMPLEX_LISTS = """# Lists

## Unordered list
- Item 1
  - Subitem 1.1
  - Subitem 1.2
    - Sub-subitem 1.2.1
- Item 2

## Ordered list
1. First item
2. Second item
   1. Subitem 2.1
   2. Subitem 2.2
      1. Sub-subitem 2.2.1
3. Third item

## Task list
- [x] Completed task
- [ ] Incomplete task
  - [x] Completed subtask
  - [ ] Incomplete subtask
"""

# Tables with different alignments
TABLES_MARKDOWN = """# Tables

## Simple table
| Name | Age | City |
|------|-----|------|
| John | 25  | NYC  |
| Jane | 30  | LA   |

## Aligned table
| Left | Center | Right |
|:-----|:------:|------:|
| L1   |   C1   |    R1 |
| L2   |   C2   |    R2 |

## Complex table
| Feature | Status | Notes |
|---------|--------|-------|
| Parser  | ✅     | Working |
| Extractor | ⚠️   | In progress |
| Analyzer | ❌    | Not started |
"""

# Code blocks with different languages
CODE_BLOCKS = """# Code Examples

## Python
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

## JavaScript
```javascript
function factorial(n) {
    return n <= 1 ? 1: n * factorial(n - 1);
}
```

## Go
```go
func main() {
    fmt.Println("Hello, World!")
}
```

## Bash
```bash
#!/bin/bash
echo "Script started"
for i in {1..5}; do
    echo "Iteration $i"
done
```

## No language specified
```
This is a code block without language specification.
It should still be detected and processed correctly.
```
"""
