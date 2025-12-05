# How to Write Technical Documentation

## Including Code Examples

When documenting code, you need to show examples in markdown.

### Basic Code Block

Use triple backticks:

```markdown
Here's how to show Python:

```python
def hello():
    print('Hello, World!')
```
```

### Nested Examples

For meta-documentation:

````markdown
To show markdown within markdown:

```markdown
# Example
```python
code here
```
```
````

## Best Practices

1. Use appropriate fence depth
2. Specify language for syntax highlighting
3. Keep examples concise
4. Test all code examples

## Alternatives

You can also use tilde fences:

~~~python
def alternative():
    return True
~~~
