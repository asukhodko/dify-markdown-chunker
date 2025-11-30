# Deep Nesting Test

This tests multiple levels of nesting.

~~~markdown
# Level 1 Document

This is a markdown document with nested code.

```python
# Level 2 Python code
def outer_function():
    """This function contains nested examples."""
    
    # Example of nested markdown in docstring
    example = '''
    ~~~text
    Level 3 nested text block
    ~~~
    '''
    
    return example
```

More level 1 content.
~~~

End of document.