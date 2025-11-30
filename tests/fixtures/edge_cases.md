# Edge Cases Document

This document contains edge cases for testing robustness.

## Empty Sections

### Empty Subsection

### Another Empty Subsection

## Very Short Section

Hi.

## Section with Only Code

```python
print("Hello")
```

## Malformed Elements

This has a code block without closing:

```python
def incomplete():
    pass

And some text after.

## Multiple Blank Lines



Between paragraphs.

## Special Characters

Testing special chars: `~!@#$%^&*()_+-={}[]|:;"'<>,.?/

## Unicode Content

Testing unicode: 你好世界 🌍 Привет мир

## Very Long Line

This is a very long line that goes on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on and on.

## Nested Lists

- Level 1
  - Level 2
    - Level 3
      - Level 4
        - Level 5

## Mixed Formatting

**Bold** *italic* ***bold italic*** `code` ~~strikethrough~~

[Link](https://example.com) ![Image](image.png)
