# Nested Code Blocks Test

This document tests nested code blocks with 4+ backticks.

## Example 1: Markdown in Markdown

`````markdown
Here's how to write a code block:

````python
def hello():
    print("Hello")
````

And here's another:

```bash
echo "test"
```
`````

## Example 2: Simple Nesting

````python
# This is a code block
def example():
    """
    ```
    This looks like a code block but it's in a docstring
    ```
    """
    pass
````

## Regular Code Block

```python
def regular():
    return "This is a regular code block"
```

End of document.
