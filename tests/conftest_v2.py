"""
V2 Test Implementation: Shared Test Configuration

Provides shared fixtures and hypothesis strategies for v2 tests.
"""

import pytest
from hypothesis import strategies as st, settings, Verbosity

# Configure hypothesis defaults for v2 tests
settings.register_profile(
    "v2_default",
    max_examples=100,
    deadline=5000,
    verbosity=Verbosity.normal,
)

settings.register_profile(
    "v2_ci",
    max_examples=50,
    deadline=10000,
    verbosity=Verbosity.quiet,
)

settings.register_profile(
    "v2_debug",
    max_examples=10,
    deadline=None,
    verbosity=Verbosity.verbose,
)


# =============================================================================
# Hypothesis Strategies for Markdown Generation
# =============================================================================

# Basic text without special markdown characters
plain_text = st.text(
    alphabet=st.characters(
        whitelist_categories=['Lu', 'Ll', 'Nd', 'Zs'],
        whitelist_characters=' .,!?'
    ),
    min_size=1,
    max_size=500
)

# Header text (no newlines)
header_text = st.text(
    alphabet=st.characters(whitelist_categories=['Lu', 'Ll', 'Nd', 'Zs']),
    min_size=1,
    max_size=50
).filter(lambda x: x.strip())

# Code content
code_content = st.text(
    alphabet=st.characters(
        whitelist_categories=['Lu', 'Ll', 'Nd', 'Po', 'Zs'],
        whitelist_characters=' =()[]{}:;,.\n\t'
    ),
    min_size=0,
    max_size=200
)

# Language identifiers
language_id = st.sampled_from([
    'python', 'javascript', 'typescript', 'java', 'go', 
    'rust', 'c', 'cpp', 'ruby', 'php', '', None
])


@st.composite
def markdown_header(draw, level=None):
    """Generate a markdown header."""
    if level is None:
        level = draw(st.integers(min_value=1, max_value=6))
    text = draw(header_text)
    return f"{'#' * level} {text}"


@st.composite
def markdown_code_block(draw):
    """Generate a markdown code block."""
    lang = draw(language_id)
    content = draw(code_content)
    lang_str = lang if lang else ''
    return f"```{lang_str}\n{content}\n```"


@st.composite
def markdown_paragraph(draw):
    """Generate a markdown paragraph."""
    return draw(plain_text)


@st.composite
def markdown_table(draw, rows=None, cols=None):
    """Generate a markdown table."""
    if rows is None:
        rows = draw(st.integers(min_value=1, max_value=5))
    if cols is None:
        cols = draw(st.integers(min_value=2, max_value=4))
    
    # Header row
    header = "| " + " | ".join(f"Col{i}" for i in range(cols)) + " |"
    # Separator
    separator = "| " + " | ".join("---" for _ in range(cols)) + " |"
    # Data rows
    data_rows = []
    for r in range(rows):
        row = "| " + " | ".join(f"R{r}C{c}" for c in range(cols)) + " |"
        data_rows.append(row)
    
    return "\n".join([header, separator] + data_rows)


@st.composite
def simple_markdown_document(draw):
    """Generate a simple markdown document."""
    parts = []
    
    # Optional preamble
    if draw(st.booleans()):
        parts.append(draw(markdown_paragraph()))
    
    # 1-3 sections
    num_sections = draw(st.integers(min_value=1, max_value=3))
    for i in range(num_sections):
        parts.append(draw(markdown_header(level=i+1)))
        parts.append(draw(markdown_paragraph()))
    
    return "\n\n".join(parts)


@st.composite
def code_heavy_markdown_document(draw):
    """Generate a code-heavy markdown document."""
    parts = []
    
    parts.append(draw(markdown_header(level=1)))
    parts.append(draw(markdown_paragraph()))
    
    # 2-4 code blocks
    num_blocks = draw(st.integers(min_value=2, max_value=4))
    for _ in range(num_blocks):
        parts.append(draw(markdown_code_block()))
        if draw(st.booleans()):
            parts.append(draw(markdown_paragraph()))
    
    return "\n\n".join(parts)


@st.composite
def structured_markdown_document(draw):
    """Generate a structured markdown document with headers."""
    parts = []
    
    # H1
    parts.append(draw(markdown_header(level=1)))
    parts.append(draw(markdown_paragraph()))
    
    # 2-3 H2 sections
    num_h2 = draw(st.integers(min_value=2, max_value=3))
    for _ in range(num_h2):
        parts.append(draw(markdown_header(level=2)))
        parts.append(draw(markdown_paragraph()))
        
        # Optional H3
        if draw(st.booleans()):
            parts.append(draw(markdown_header(level=3)))
            parts.append(draw(markdown_paragraph()))
    
    return "\n\n".join(parts)


# =============================================================================
# Pytest Fixtures
# =============================================================================

@pytest.fixture
def default_chunker():
    """Provide a default MarkdownChunker instance."""
    from markdown_chunker_v2.chunker import MarkdownChunker
    return MarkdownChunker()


@pytest.fixture
def small_chunk_config():
    """Provide a config with small chunk sizes for testing."""
    from markdown_chunker_v2.config import ChunkConfig
    return ChunkConfig(
        max_chunk_size=500,
        min_chunk_size=50,
        overlap_size=50
    )


@pytest.fixture
def no_overlap_config():
    """Provide a config with no overlap."""
    from markdown_chunker_v2.config import ChunkConfig
    return ChunkConfig(
        max_chunk_size=1000,
        min_chunk_size=100,
        overlap_size=0
    )


@pytest.fixture
def parser():
    """Provide a Parser instance."""
    from markdown_chunker_v2.parser import Parser
    return Parser()


@pytest.fixture
def sample_markdown():
    """Provide a sample markdown document."""
    return """# Sample Document

This is a sample markdown document for testing.

## Section 1

Some content in section 1.

```python
def example():
    return "Hello"
```

## Section 2

| Col1 | Col2 |
|------|------|
| A    | B    |

## Conclusion

Final thoughts.
"""


@pytest.fixture
def code_heavy_markdown():
    """Provide a code-heavy markdown document."""
    return """# Code Examples

```python
class Example:
    def __init__(self):
        self.value = 0
```

More code:

```javascript
function hello() {
    console.log("Hello");
}
```

And more:

```go
func main() {
    fmt.Println("Hello")
}
```
"""


@pytest.fixture
def structured_markdown():
    """Provide a structured markdown document."""
    return """# Main Title

Introduction paragraph.

## Chapter 1

Content for chapter 1.

### Section 1.1

Details for section 1.1.

### Section 1.2

Details for section 1.2.

## Chapter 2

Content for chapter 2.

### Section 2.1

Details for section 2.1.

## Conclusion

Final summary.
"""
