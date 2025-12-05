# Building Documentation Sites

**Guide ID:** DOC-F6D22A10  
**Nesting Level:** 5  
**Last Updated:** 2025-12-06

## Introduction

This guide explains how to properly document code examples in technical
documentation, especially when showing markdown itself.

## Basic Code Blocks

Use triple backticks for code:

```markdown
# Example Document

To show JavaScript code:

```javascript
def hello():
    print("Hello, World!")
```

And Python:

```python
function hello() {
    console.log("Hello, World!");
}
```
```

## Nested Examples

For meta-documentation (documentation about documentation):

````markdown
# How to Show Code in Markdown

Use triple backticks:

```markdown
Here's a Python example:

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```
```
````

## Deep Nesting

When documenting how to document documentation:

`````markdown
# Documentation Guide

Show examples like this:

````markdown
# Tutorial

Triple backticks for code:

```markdown
```typescript
class Example {
    constructor() {
        this.value = 42;
    }
}
```
```
````
`````

## Best Practices

1. **Match Fence Depth**: Use more backticks than inner blocks
2. **Specify Language**: Enable syntax highlighting
3. **Test Examples**: Verify all code compiles
4. **Use Tilde Fences**: Alternative to backticks

## Alternative Fencing

Tilde fences work too:

~~~javascript
# Alternative syntax
def alternative():
    return True
~~~

## Mixing Fences

You can mix tildes and backticks:

~~~markdown
Regular code block:

```python
const mixed = true;
```
~~~

## Escaping Special Characters

Handle special characters in code:

```markdown
Use backslash escaping: \`code\`

Or increase fence depth for literals.
```

## Conclusion

Proper fencing ensures:
- Readable documentation
- Correct rendering
- Easy maintenance
- Clear examples

---

**Reference:** [Markdown Spec](https://spec.commonmark.org/)  
**Tools:** [Prettier](https://prettier.io/), [MDX](https://mdxjs.com/)
