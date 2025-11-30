# Mixed Fence Types

Testing different combinations of ``` and ~~~ fences.

## Backticks inside tildes

~~~markdown
# Documentation

```python
def function_in_tilde():
    return "backticks inside tildes"
```

More documentation.
~~~

## Tildes inside backticks

```markdown
# Another document

~~~bash
echo "tildes inside backticks"
~~~

End of inner document.
```

## Multiple nesting

~~~text
Outer text block

```markdown
# Inner markdown

~~~python
print("deeply nested")
~~~

Back to markdown.
```

Back to text.
~~~