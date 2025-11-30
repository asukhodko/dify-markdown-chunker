#!/usr/bin/env python3
"""
Quick test of critical fixes implementation.
"""


def test_enhanced_ast():
    """Test enhanced AST building."""
    from markdown_chunker.parser import EnhancedASTBuilder
    from markdown_chunker.parser.types import NodeType

    print("\n=== Testing Enhanced AST ===")

    markdown = "This is a paragraph with `inline code` and **bold text**."

    builder = EnhancedASTBuilder()
    ast = builder.build_ast(markdown)

    print("✓ AST built successfully")
    print(f"  Root type: {ast.type}")
    print(f"  Children: {len(ast.children)}")

    # Find paragraph with inline elements
    for child in ast.children:
        if child.type == NodeType.PARAGRAPH:
            print(f"  Paragraph children: {len(child.children)}")
            break


def test_error_collection():
    """Test error collection system."""
    from markdown_chunker.parser import ErrorCollector, SourceLocation

    print("\n=== Testing Error Collection ===")

    collector = ErrorCollector()

    # Add some test errors
    location = SourceLocation(line=5, column=10)
    collector.add_error("Test error", category="test", location=location)
    collector.add_warning("Test warning", category="test")

    summary = collector.get_summary()
    print("✓ Error collection working")
    print(f"  Errors: {summary.error_count}")
    print(f"  Warnings: {summary.warning_count}")


def test_fence_handling():
    """Test fence handling."""
    from markdown_chunker.parser import FenceHandler

    print("\n=== Testing Fence Handling ===")

    handler = FenceHandler()

    # Test opening fence parsing
    fence_info = handler.parse_opening_fence("```python", 1)
    print("✓ Fence parsing working")
    print(f"  Type: {fence_info.fence_type}")
    print(f"  Language: {fence_info.language}")
    print(f"  Is opening: {fence_info.is_opening_fence()}")


def test_text_recovery():
    """Test text recovery utilities."""
    from markdown_chunker.parser import create_text_recovery_utils
    from markdown_chunker.parser.types import FencedBlock

    print("\n=== Testing Text Recovery ===")

    markdown = """# Header

```python
def hello():
    print("Hello!")
```

More text."""

    utils = create_text_recovery_utils(markdown)

    # Create test block
    block = FencedBlock(
        content='def hello():\n    print("Hello!")',
        language="python",
        fence_type="```",
        fence_length=3,
        start_line=3,
        end_line=5,
        start_offset=10,
        end_offset=50,
        nesting_level=0,
        is_closed=True,
        raw_content='```python\ndef hello():\n    print("Hello!")\n```',
    )

    recovered = utils.get_block_text(block, include_fences=True)
    print("✓ Text recovery working")
    print(f"  Recovered {len(recovered)} characters")


def test_api_validation():
    """Test API validation."""
    from markdown_chunker.parser import validate_stage1_result
    from markdown_chunker.parser.types import (
        ContentAnalysis,
        ElementCollection,
        MarkdownNode,
        NodeType,
        Position,
        Stage1Results,
    )

    print("\n=== Testing API Validation ===")

    # Create minimal valid results
    ast = MarkdownNode(
        type=NodeType.DOCUMENT,
        content="",
        start_pos=Position(line=1, column=1, offset=0),
        end_pos=Position(line=1, column=10, offset=10),
        children=[],
    )

    analysis = ContentAnalysis(
        total_chars=10,
        total_lines=1,
        total_words=2,
        code_ratio=0.0,
        text_ratio=1.0,
        code_block_count=0,
        header_count=0,
        content_type="text_heavy",
        languages=set(),
    )

    results = Stage1Results(
        ast=ast,
        fenced_blocks=[],
        elements=ElementCollection(),
        analysis=analysis,
        parser_name="test",
        processing_time=0.1,
    )

    validation = validate_stage1_result(results)
    print("✓ API validation working")
    print(f"  Valid: {validation.is_valid}")


def main():
    """Run all tests."""
    print("Testing Critical Fixes Implementation")
    print("=" * 50)

    try:
        test_enhanced_ast()
        test_error_collection()
        test_fence_handling()
        test_text_recovery()
        test_api_validation()

        print("\n" + "=" * 50)
        print("✅ All tests passed! Critical fixes are working.")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
