# Writing Technical Tutorials

**Guide ID:** DOC-294C5F47  
**Nesting Level:** 3  
**Last Updated:** 2025-12-06

## Introduction

This guide explains how to properly document code examples in technical
documentation, especially when showing markdown itself.

## Basic Code Blocks

Use triple backticks for code:

```markdown
# Example Document

To show Python code:

```python
def hello():
    print("Hello, World!")
```

And TypeScript:

```typescript
function hello() {
    console.log("Hello, World!");
}
```
```

## Best Practices

1. **Match Fence Depth**: Use more backticks than inner blocks
2. **Specify Language**: Enable syntax highlighting
3. **Test Examples**: Verify all code compiles
4. **Use Tilde Fences**: Alternative to backticks

## Alternative Fencing

Tilde fences work too:

~~~python
# Alternative syntax
def alternative():
    return True
~~~

## Mixing Fences

You can mix tildes and backticks:

~~~markdown
Regular code block:

```typescript
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
