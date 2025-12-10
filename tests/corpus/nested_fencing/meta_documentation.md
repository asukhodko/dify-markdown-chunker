# How to Write Technical Documentation

A comprehensive guide for creating effective markdown documentation.

## Getting Started

Technical documentation should be clear, concise, and well-structured.

## Including Code Examples

### Basic Code Blocks

Use triple backticks for simple code:

```python
def hello_world():
    print("Hello, World!")
```

### Showing Markdown Examples

When documenting markdown syntax itself, use quadruple backticks:

````markdown
To create a header:

# Main Title
## Subsection
### Detail Level
````

### Meta-Documentation Pattern

For tutorials about writing documentation:

`````markdown
# Documentation Best Practices

## Code Example Section

Show code with context:

````markdown
First explain the concept, then show:

```python
# Implementation
def process():
    return "result"
```
````
`````

## Real-World Tutorial Example

````markdown
# Python Tutorial: Functions

## Defining Functions

Use the `def` keyword:

```python
def greet(name):
    """Return a greeting message."""
    return f"Hello, {name}!"
```

## Calling Functions

```python
message = greet("Alice")
print(message)  # Output: Hello, Alice!
```
````

## README Template

Here's a template for README files:

`````markdown
# Project Name

## Installation

```bash
pip install project-name
```

## Quick Start

```python
import project

# Basic usage
result = project.run()
```

## Advanced Usage

For complex scenarios:

````markdown
### Custom Configuration

```python
config = {
    'option1': 'value1',
    'option2': 'value2'
}
project.run(config)
```
````
`````

## Style Guide

When creating style guides, use nested fences to show examples:

````markdown
### Code Documentation

All functions must have docstrings:

```python
def calculate(x, y):
    """
    Calculate the sum of two numbers.
    
    Args:
        x: First number
        y: Second number
    
    Returns:
        Sum of x and y
    """
    return x + y
```
````

## Conclusion

Nested fencing enables clear, unambiguous documentation about markdown syntax itself.
