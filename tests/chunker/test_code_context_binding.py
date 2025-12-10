"""
Unit tests for code-context binding functionality.

Tests pattern recognition, context extraction, and relationship detection
for the enhanced code-context binding feature.
"""

from markdown_chunker_v2.code_context import (
    CodeBlockRole,
    CodeContext,
    CodeContextBinder,
)
from markdown_chunker_v2.types import FencedBlock


class TestRoleDetection:
    """Test code block role detection."""

    def test_detect_output_blocks_by_language(self):
        """Output blocks recognized by language tag."""
        binder = CodeContextBinder()

        # Test various output language tags
        for lang in ["output", "console", "stdout", "result"]:
            block = FencedBlock(
                language=lang,
                content="Hello, World!",
                start_line=5,
                end_line=7,
            )

            role = binder._determine_role(block, "")
            assert role == CodeBlockRole.OUTPUT, f"Failed for language: {lang}"

    def test_detect_output_blocks_by_text_pattern(self):
        """'Output:' text pattern recognized."""
        binder = CodeContextBinder()

        md_text = """Some code here.

Output:

```
Hello, World!
```
"""

        block = FencedBlock(
            language="",
            content="Hello, World!",
            start_line=5,
            end_line=7,
        )

        role = binder._determine_role(block, md_text)
        assert role == CodeBlockRole.OUTPUT

    def test_detect_setup_blocks(self):
        """Setup blocks recognized by pattern."""
        binder = CodeContextBinder()

        md_text = """First, you need to install the package:

```bash
pip install mypackage
```
"""

        block = FencedBlock(
            language="bash",
            content="pip install mypackage",
            start_line=3,
            end_line=5,
        )

        role = binder._determine_role(block, md_text)
        assert role == CodeBlockRole.SETUP

    def test_detect_before_after_pairs(self):
        """Before/After patterns recognized."""
        binder = CodeContextBinder()

        # Test BEFORE
        md_text_before = """Before (problematic code):

```python
def bad():
    pass
```
"""

        block_before = FencedBlock(
            language="python",
            content="def bad():\n    pass",
            start_line=3,
            end_line=5,
        )

        role = binder._determine_role(block_before, md_text_before)
        assert role == CodeBlockRole.BEFORE

        # Test AFTER
        md_text_after = """After (fixed code):

```python
def good():
    pass
```
"""

        block_after = FencedBlock(
            language="python",
            content="def good():\n    pass",
            start_line=3,
            end_line=5,
        )

        role = binder._determine_role(block_after, md_text_after)
        assert role == CodeBlockRole.AFTER

    def test_detect_error_blocks(self):
        """Error blocks recognized by language tag."""
        binder = CodeContextBinder()

        for lang in ["error", "traceback"]:
            block = FencedBlock(
                language=lang,
                content="Traceback...",
                start_line=5,
                end_line=7,
            )

            role = binder._determine_role(block, "")
            assert role == CodeBlockRole.ERROR, f"Failed for language: {lang}"

    def test_default_to_example(self):
        """Unmatched patterns default to EXAMPLE."""
        binder = CodeContextBinder()

        block = FencedBlock(
            language="python",
            content="print('hello')",
            start_line=1,
            end_line=3,
        )

        role = binder._determine_role(block, "Regular text before code.")
        assert role == CodeBlockRole.EXAMPLE


class TestContextExtraction:
    """Test context extraction before and after code blocks."""

    def test_extract_explanation_before(self):
        """Backward search finds explanation."""
        binder = CodeContextBinder()

        md_text = """# Example

This function demonstrates basic usage.
It takes a parameter and returns a result.

```python
def example(x):
    return x * 2
```
"""

        block = FencedBlock(
            language="python",
            content="def example(x):\n    return x * 2",
            start_line=6,
            end_line=8,
        )

        explanation = binder._extract_explanation_before(block, md_text, 500)

        assert explanation is not None
        assert "demonstrates basic usage" in explanation
        assert "takes a parameter" in explanation

    def test_extract_explanation_after(self):
        """Forward search finds explanation."""
        binder = CodeContextBinder()

        md_text = """```python
def example(x):
    return x * 2
```

This example shows how to double a number.
The function is simple and efficient.
"""

        block = FencedBlock(
            language="python",
            content="def example(x):\n    return x * 2",
            start_line=1,
            end_line=3,
        )

        explanation = binder._extract_explanation_after(block, md_text, 500)

        assert explanation is not None
        assert "shows how to double" in explanation

    def test_explanation_respects_max_chars(self):
        """Explanation trimmed to max_chars."""
        binder = CodeContextBinder()

        long_text = "A" * 1000
        md_text = f"""{long_text}

```python
code
```
"""

        block = FencedBlock(
            language="python",
            content="code",
            start_line=3,
            end_line=5,
        )

        explanation = binder._extract_explanation_before(block, md_text, 100)

        assert explanation is not None
        assert len(explanation) <= 100

    def test_no_explanation_returns_none(self):
        """Returns None when no explanation found."""
        binder = CodeContextBinder()

        md_text = """```python
code
```
"""

        block = FencedBlock(
            language="python",
            content="code",
            start_line=1,
            end_line=3,
        )

        explanation = binder._extract_explanation_before(block, md_text, 500)
        assert explanation is None


class TestRelatedBlockDetection:
    """Test detection of related code blocks."""

    def test_find_related_blocks_by_proximity(self):
        """Adjacent blocks with same language detected."""
        binder = CodeContextBinder()

        block1 = FencedBlock(
            language="python",
            content="code1",
            start_line=1,
            end_line=3,
        )

        block2 = FencedBlock(
            language="python",
            content="code2",
            start_line=5,
            end_line=7,
        )

        all_blocks = [block1, block2]
        md_text = ""

        related = binder._find_related_blocks(block1, all_blocks, md_text)

        assert len(related) == 1
        assert related[0] == block2

    def test_find_related_blocks_by_language(self):
        """Same-language blocks grouped."""
        binder = CodeContextBinder()

        block1 = FencedBlock(
            language="javascript",
            content="code1",
            start_line=1,
            end_line=3,
        )

        block2 = FencedBlock(
            language="javascript",
            content="code2",
            start_line=5,
            end_line=7,
        )

        block3 = FencedBlock(
            language="python",
            content="code3",
            start_line=9,
            end_line=11,
        )

        all_blocks = [block1, block2, block3]
        md_text = ""

        related = binder._find_related_blocks(block1, all_blocks, md_text)

        assert len(related) == 1
        assert related[0] == block2
        assert block3 not in related

    def test_before_after_pairing(self):
        """Before/After blocks detected as related."""
        binder = CodeContextBinder()

        md_text_combined = """Before:

```python
old_code
```

After:

```python
new_code
```
"""

        block1 = FencedBlock(
            language="python",
            content="old_code",
            start_line=3,
            end_line=5,
        )

        block2 = FencedBlock(
            language="python",
            content="new_code",
            start_line=9,
            end_line=11,
        )

        all_blocks = [block1, block2]

        related = binder._find_related_blocks(block1, all_blocks, md_text_combined)

        assert len(related) == 1
        assert related[0] == block2

    def test_code_output_pairing(self):
        """Code+Output blocks detected as related."""
        binder = CodeContextBinder()

        # Actual line count: 9 lines total
        md_text = """```python
print("hello")
```

Output:

```
hello
```"""

        # Line 1-3: code block
        code_block = FencedBlock(
            language="python",
            content='print("hello")',
            start_line=1,
            end_line=3,
        )

        # Line 7-9: output block
        output_block = FencedBlock(
            language="",
            content="hello",
            start_line=7,
            end_line=9,
        )

        all_blocks = [code_block, output_block]

        # Test both directions
        related_from_code = binder._find_related_blocks(code_block, all_blocks, md_text)

        assert len(related_from_code) == 1
        assert related_from_code[0] == output_block

    def test_distant_blocks_not_related(self):
        """Blocks too far apart not related."""
        binder = CodeContextBinder(related_block_max_gap=5)

        block1 = FencedBlock(
            language="python",
            content="code1",
            start_line=1,
            end_line=3,
        )

        block2 = FencedBlock(
            language="python",
            content="code2",
            start_line=20,  # Far away
            end_line=22,
        )

        all_blocks = [block1, block2]
        md_text = ""

        related = binder._find_related_blocks(block1, all_blocks, md_text)

        assert len(related) == 0


class TestOutputBlockFinding:
    """Test finding output blocks for code blocks."""

    def test_find_output_block(self):
        """Output block found for code block."""
        binder = CodeContextBinder()

        # Actual line count: 9 lines
        md_text = """```python
print("test")
```

Output:

```
test
```"""

        # Line 1-3: code block
        code_block = FencedBlock(
            language="python",
            content='print("test")',
            start_line=1,
            end_line=3,
        )

        # Line 7-9: output block (empty language indicates output)
        output_block = FencedBlock(
            language="",
            content="test",
            start_line=7,
            end_line=9,
        )

        all_blocks = [code_block, output_block]

        found_output = binder._find_output_block(code_block, all_blocks, md_text)

        assert found_output is not None
        assert found_output == output_block

    def test_no_output_block_for_output(self):
        """Output blocks don't look for their own output."""
        binder = CodeContextBinder()

        md_text = "Output:\n\n```\nresult\n```"

        output_block = FencedBlock(
            language="",
            content="result",
            start_line=3,
            end_line=5,
        )

        all_blocks = [output_block]

        found_output = binder._find_output_block(output_block, all_blocks, md_text)

        assert found_output is None


class TestBindContext:
    """Test full context binding."""

    def test_bind_context_complete(self):
        """Complete context binding works."""
        binder = CodeContextBinder()

        # Line count: 11 lines total
        md_text = """Here's an example of printing:

```python
print("Hello")
```

Output:

```
Hello
```"""

        # Line 3-5: code block
        code_block = FencedBlock(
            language="python",
            content='print("Hello")',
            start_line=3,
            end_line=5,
        )

        # Line 9-11: output block
        output_block = FencedBlock(
            language="",
            content="Hello",
            start_line=9,
            end_line=11,
        )

        all_blocks = [code_block, output_block]

        context = binder.bind_context(code_block, md_text, all_blocks)

        assert isinstance(context, CodeContext)
        assert context.code_block == code_block
        assert context.role == CodeBlockRole.EXAMPLE
        assert context.explanation_before is not None
        assert "example of printing" in context.explanation_before
        assert context.output_block == output_block
        assert len(context.related_blocks) == 1

    def test_cached_role_used(self):
        """Cached role in FencedBlock is used."""
        binder = CodeContextBinder()

        block = FencedBlock(
            language="python",
            content="code",
            start_line=1,
            end_line=3,
            context_role="setup",  # Cached role
        )

        context = binder.bind_context(block, "", [block])

        assert context.role == CodeBlockRole.SETUP


class TestConfigurableParameters:
    """Test configurable parameters work correctly."""

    def test_custom_max_context_chars_before(self):
        """Custom max_context_chars_before is respected."""
        binder = CodeContextBinder(max_context_chars_before=50)

        long_text = "A" * 200
        md_text = f"""{long_text}

```python
code
```
"""

        block = FencedBlock(
            language="python",
            content="code",
            start_line=3,
            end_line=5,
        )

        explanation = binder._extract_explanation_before(
            block, md_text, binder.max_context_chars_before
        )

        assert explanation is not None
        assert len(explanation) <= 50

    def test_custom_related_block_max_gap(self):
        """Custom related_block_max_gap is respected."""
        binder = CodeContextBinder(related_block_max_gap=2)

        block1 = FencedBlock(
            language="python",
            content="code1",
            start_line=1,
            end_line=3,
        )

        block2 = FencedBlock(
            language="python",
            content="code2",
            start_line=10,  # Gap = 7, > max_gap
            end_line=12,
        )

        all_blocks = [block1, block2]

        related = binder._find_related_blocks(block1, all_blocks, "")

        assert len(related) == 0  # Too far apart
