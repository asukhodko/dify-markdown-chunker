"""
Tests for CodeStrategy.

This module tests the code-heavy document chunking strategy that preserves
code block atomicity while maintaining context with surrounding text.
"""

from unittest.mock import Mock

from markdown_chunker.chunker.strategies.code_strategy import CodeSegment, CodeStrategy
from markdown_chunker.chunker.types import ChunkConfig
from markdown_chunker.parser.types import ContentAnalysis, FencedBlock, Stage1Results


class TestCodeStrategy:
    """Test cases for CodeStrategy."""

    def test_strategy_properties(self):
        """Test basic strategy properties."""
        strategy = CodeStrategy()

        assert strategy.name == "code"
        assert strategy.priority == 1  # Highest priority

    def test_can_handle_sufficient_code(self):
        """Test can_handle with sufficient code ratio and blocks."""
        strategy = CodeStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.code_ratio = 0.75
        analysis.code_block_count = 5

        config = ChunkConfig(code_ratio_threshold=0.7, min_code_blocks=3)

        assert strategy.can_handle(analysis, config) is True

    def test_can_handle_insufficient_code_ratio(self):
        """Test can_handle with insufficient code ratio."""
        strategy = CodeStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.code_ratio = 0.5  # Below threshold
        analysis.code_block_count = 5

        config = ChunkConfig(code_ratio_threshold=0.7, min_code_blocks=3)

        assert strategy.can_handle(analysis, config) is False

    def test_can_handle_insufficient_code_blocks(self):
        """Test can_handle with insufficient code blocks."""
        strategy = CodeStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.code_ratio = 0.8
        analysis.code_block_count = 2  # Below threshold

        config = ChunkConfig(code_ratio_threshold=0.7, min_code_blocks=3)

        assert strategy.can_handle(analysis, config) is False

    def test_calculate_quality_high_code_ratio(self):
        """Test quality calculation for high code ratio."""
        strategy = CodeStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.code_ratio = 0.9
        analysis.code_block_count = 15
        analysis.languages = {"python", "javascript"}

        quality = strategy.calculate_quality(analysis)

        # Should be very high quality
        assert quality > 0.9

    def test_calculate_quality_moderate_code(self):
        """Test quality calculation for moderate code content."""
        strategy = CodeStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.code_ratio = 0.6
        analysis.code_block_count = 4
        analysis.languages = {"python"}

        quality = strategy.calculate_quality(analysis)

        # Should be moderate quality
        assert 0.3 < quality < 0.7

    def test_detect_language_python(self):
        """Test language detection for Python code."""
        strategy = CodeStrategy()

        python_code = """
def hello_world():
    print("Hello, World!")

class MyClass:
    pass
"""

        language = strategy._detect_language(python_code)
        assert language == "python"

    def test_detect_language_javascript(self):
        """Test language detection for JavaScript code."""
        strategy = CodeStrategy()

        js_code = """
function greet(name) {
    console.log("Hello, " + name);
}

const myVar=42;
"""

        language = strategy._detect_language(js_code)
        assert language == "javascript"

    def test_detect_language_unknown(self):
        """Test language detection for unknown code."""
        strategy = CodeStrategy()

        unknown_code = "some random text without language markers"

        language = strategy._detect_language(unknown_code)
        assert language is None

    def test_extract_function_names_python(self):
        """Test function name extraction for Python."""
        strategy = CodeStrategy()

        python_code = """
def first_function():
    pass

def second_function(arg1, arg2):
    return arg1 + arg2
"""

        functions = strategy._extract_function_names(python_code, "python")

        assert len(functions) == 2
        assert "first_function" in functions
        assert "second_function" in functions

    def test_extract_class_names_python(self):
        """Test class name extraction for Python."""
        strategy = CodeStrategy()

        python_code = """
class FirstClass:
    pass

class SecondClass(BaseClass):
    def method(self):
        pass
"""

        classes = strategy._extract_class_names(python_code, "python")

        assert len(classes) == 2
        assert "FirstClass" in classes
        assert "SecondClass" in classes

    def test_extract_function_names_javascript(self):
        """Test function name extraction for JavaScript."""
        strategy = CodeStrategy()

        js_code = """
function myFunction() {
    return true;
}

function anotherFunction(param) {
    console.log(param);
}
"""

        functions = strategy._extract_function_names(js_code, "javascript")

        assert len(functions) == 2
        assert "myFunction" in functions
        assert "anotherFunction" in functions

    def test_calculate_line_number(self):
        """Test line number calculation from position."""
        strategy = CodeStrategy()

        content = "Line 1\nLine 2\nLine 3\nLine 4"

        # Position at start of Line 1
        assert strategy._calculate_line_number(content, 0) == 1

        # Position at start of Line 2
        assert strategy._calculate_line_number(content, 7) == 2

        # Position at start of Line 3
        assert strategy._calculate_line_number(content, 14) == 3

    def test_apply_empty_content(self):
        """Test applying strategy to empty content."""
        strategy = CodeStrategy()
        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig.default()

        chunks = strategy.apply("", stage1_results, config)

        assert chunks == []

    def test_apply_no_code_blocks(self):
        """Test applying strategy to content without code blocks."""
        strategy = CodeStrategy()

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.fenced_blocks = []

        config = ChunkConfig.default()
        content = "Just some plain text without any code blocks."

        chunks = strategy.apply(content, stage1_results, config)

        assert chunks == []

    def test_apply_simple_code_document(self):
        """Test applying strategy to simple code document."""
        strategy = CodeStrategy()

        # Mock code blocks
        code_block = Mock(spec=FencedBlock)
        code_block.content = "def hello():\n    print('Hello')"
        code_block.raw_content = "```python\ndef hello():\n    print('Hello')\n```"
        code_block.language = "python"
        code_block.fence_type = "```"  # Add missing fence_type attribute
        code_block.start_line = 3
        code_block.end_line = 5
        code_block.start_offset = 20
        code_block.end_offset = 60

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.fenced_blocks = [code_block]

        config = ChunkConfig.default()
        content = """# Code Example

Here's a simple function:

```python
def hello():
    print('Hello')
```

That's it!"""

        chunks = strategy.apply(content, stage1_results, config)

        assert len(chunks) >= 1

        # Should have at least one code chunk
        code_chunks = [c for c in chunks if c.metadata.get("content_type") == "code"]
        assert len(code_chunks) >= 1

        # Code chunk should have proper metadata
        code_chunk = code_chunks[0]
        assert code_chunk.metadata["language"] == "python"
        assert code_chunk.metadata["is_fenced"] is True
        assert (
            "function_names" in code_chunk.metadata
            or "function_name" in code_chunk.metadata
        )

    def test_segment_around_code_blocks(self):
        """Test segmentation around code blocks."""
        strategy = CodeStrategy()

        content = """Introduction text.

```python
def example():
    pass
```

Explanation text.

```python
result=example()
```

Conclusion."""

        # Mock code blocks
        code_blocks = [
            Mock(
                content="def example():\n    pass",
                raw_content="```python\ndef example():\n    pass\n```",
                language="python",
                start_line=3,
                end_line=5,
                start_offset=20,
                end_offset=60,
            ),
            Mock(
                content="result=example()",
                raw_content="```python\nresult=example()\n```",
                language="python",
                start_line=9,
                end_line=11,
                start_offset=100,
                end_offset=130,
            ),
        ]

        segments = strategy._segment_around_code_blocks(content, code_blocks)

        # Should have alternating text-code-text-code-text segments
        assert len(segments) >= 3

        # Check segment types
        segment_types = [s.type for s in segments]
        assert "text" in segment_types
        assert "code" in segment_types

        # Code segments should have language information
        code_segments = [s for s in segments if s.type == "code"]
        for code_segment in code_segments:
            assert code_segment.language == "python"
            assert code_segment.is_fenced is True

    def test_get_selection_reason(self):
        """Test selection reason generation."""
        strategy = CodeStrategy()

        # Can handle
        analysis = Mock(spec=ContentAnalysis)
        analysis.code_ratio = 0.8
        analysis.code_block_count = 5

        reason = strategy._get_selection_reason(analysis, True)
        assert "80.0%" in reason
        assert "5 code blocks" in reason

        # Cannot handle - low ratio
        analysis.code_ratio = 0.5
        reason = strategy._get_selection_reason(analysis, False)
        assert "50.0%" in reason
        assert "below threshold" in reason

        # Cannot handle - few blocks
        analysis.code_ratio = 0.8
        analysis.code_block_count = 2
        reason = strategy._get_selection_reason(analysis, False)
        assert "Too few code blocks" in reason


class TestCodeSegment:
    """Test cases for CodeSegment data structure."""

    def test_code_segment_creation(self):
        """Test creating CodeSegment."""
        segment = CodeSegment(
            type="code",
            content="def test(): pass",
            start_line=5,
            end_line=5,
            language="python",
            is_fenced=True,
        )

        assert segment.type == "code"
        assert segment.content == "def test(): pass"
        assert segment.language == "python"
        assert segment.is_fenced is True
        assert segment.function_names == []
        assert segment.class_names == []

    def test_code_segment_with_metadata(self):
        """Test CodeSegment with function and class names."""
        segment = CodeSegment(
            type="code",
            content="class Test:\n    def method(self): pass",
            start_line=1,
            end_line=2,
            language="python",
            function_names=["method"],
            class_names=["Test"],
        )

        assert segment.function_names == ["method"]
        assert segment.class_names == ["Test"]


class TestCodeStrategyIntegration:
    """Integration tests for CodeStrategy."""

    def test_realistic_tutorial_chunking(self):
        """Test chunking realistic tutorial with code examples."""
        strategy = CodeStrategy()

        content = """# Python Tutorial

## Functions

Functions are reusable blocks of code:

```python
def greet(name):
    return f"Hello, {name}!"
```

You can call functions like this:

```python
message=greet("Alice")
print(message)
```

## Classes

Classes define objects:

```python
class Person:
    def __init__(self, name):
        self.name=name

    def introduce(self):
        return f"I'm {self.name}"
```

Create instances like this:

```python
person=Person("Bob")
print(person.introduce())
```"""

        # Mock code blocks
        code_blocks = [
            Mock(
                content='def greet(name):\n    return f"Hello, {name}!"',
                raw_content='```python\ndef greet(name):\n    return f"Hello, {name}!"\n```',
                language="python",
                start_line=7,
                end_line=9,
                start_offset=100,
                end_offset=150,
            ),
            Mock(
                content='message=greet("Alice")\nprint(message)',
                raw_content='```python\nmessage=greet("Alice")\nprint(message)\n```',
                language="python",
                start_line=13,
                end_line=15,
                start_offset=200,
                end_offset=250,
            ),
            Mock(
                content='class Person:\n    def __init__(self, name):\n        self.name=name\n    \n    def introduce(self):\n        return f"I\'m {self.name}"',
                raw_content='```python\nclass Person:\n    def __init__(self, name):\n        self.name=name\n    \n    def introduce(self):\n        return f"I\'m {self.name}"\n```',
                language="python",
                start_line=21,
                end_line=27,
                start_offset=350,
                end_offset=450,
            ),
            Mock(
                content='person=Person("Bob")\nprint(person.introduce())',
                raw_content='```python\nperson=Person("Bob")\nprint(person.introduce())\n```',
                language="python",
                start_line=31,
                end_line=33,
                start_offset=500,
                end_offset=550,
            ),
        ]

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.fenced_blocks = code_blocks

        config = ChunkConfig(max_chunk_size=800, min_chunk_size=200)

        chunks = strategy.apply(content, stage1_results, config)

        # Should create multiple chunks
        assert len(chunks) > 1

        # Should have both code and text chunks
        code_chunks = [c for c in chunks if c.metadata.get("content_type") == "code"]
        text_chunks = [c for c in chunks if c.metadata.get("content_type") == "text"]

        assert len(code_chunks) > 0
        assert len(text_chunks) > 0

        # Code chunks should have proper metadata
        for code_chunk in code_chunks:
            assert code_chunk.metadata["language"] == "python"
            assert code_chunk.metadata["is_fenced"] is True
            # Should have function or class names (at least some chunks should have them)

        # Check that at least some code chunks have function or class metadata
        has_any_functions = any(
            "function_names" in chunk.metadata or "function_name" in chunk.metadata
            for chunk in code_chunks
        )
        has_any_classes = any(
            "class_names" in chunk.metadata or "class_name" in chunk.metadata
            for chunk in code_chunks
        )
        assert has_any_functions or has_any_classes

        # Text chunks should have context metadata
        for text_chunk in text_chunks:
            assert text_chunk.metadata["context"] == "code_explanation"

    def test_oversize_code_block_handling(self):
        """Test handling of oversized code blocks."""
        strategy = CodeStrategy()

        # Create a large code block
        large_code_content = (
            "def large_function():\n" + "    # comment\n" * 100 + "    pass"
        )

        code_block = Mock(spec=FencedBlock)
        code_block.content = large_code_content
        code_block.raw_content = f"```python\n{large_code_content}\n```"
        code_block.language = "python"
        code_block.fence_type = "```"  # Add missing fence_type attribute
        code_block.start_line = 1
        code_block.end_line = 102
        code_block.start_offset = 0
        code_block.end_offset = len(code_block.raw_content)

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.fenced_blocks = [code_block]

        config = ChunkConfig(max_chunk_size=500, min_chunk_size=100)  # Small limit
        content = code_block.raw_content

        chunks = strategy.apply(content, stage1_results, config)

        assert len(chunks) == 1  # Should create one oversized chunk

        code_chunk = chunks[0]
        assert code_chunk.metadata["content_type"] == "code"
        assert code_chunk.metadata["allow_oversize"] is True
        assert code_chunk.metadata["oversize_reason"] == "code_block_atomicity"
        assert code_chunk.size > config.max_chunk_size

    def test_multiple_languages_detection(self):
        """Test handling documents with multiple programming languages."""
        strategy = CodeStrategy()

        # Mock code blocks with different languages
        code_blocks = [
            Mock(
                content="def python_func(): pass",
                raw_content="```python\ndef python_func(): pass\n```",
                language="python",
                start_line=1,
                end_line=3,
                start_offset=0,
                end_offset=40,
            ),
            Mock(
                content="function jsFunc() { return true; }",
                raw_content="```javascript\nfunction jsFunc() { return true; }\n```",
                language="javascript",
                start_line=5,
                end_line=7,
                start_offset=50,
                end_offset=100,
            ),
        ]

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.fenced_blocks = code_blocks

        config = ChunkConfig.default()
        content = """```python
def python_func(): pass
```

```javascript
function jsFunc() { return true; }
```"""

        chunks = strategy.apply(content, stage1_results, config)

        # Should create chunks for both languages
        code_chunks = [c for c in chunks if c.metadata.get("content_type") == "code"]
        assert len(code_chunks) == 2

        languages = [c.metadata["language"] for c in code_chunks]
        assert "python" in languages
        assert "javascript" in languages
