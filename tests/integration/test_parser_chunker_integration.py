#!/usr/bin/env python3
"""
Validation script to ensure Stage1Interface works correctly with Stage 2.
"""

import logging

from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.parser import Stage1Interface

# Set up logging to see our new error handling
logging.basicConfig(
    level=logging.WARNING, format="%(name)s - %(levelname)s - %(message)s"
)


def test_stage1_interface_integration():
    """Test that Stage1Interface produces valid data for Stage 2."""

    # Test content with lists and tables
    content = """# Test Document

This is a test document with mixed content.

## Lists

- Item 1
- Item 2
  - Nested item
- Item 3

## Tables

| Column A | Column B |
|----------|----------|
| Data 1   | Data 2   |
| Data 3   | Data 4   |

## Task List

- [x] Completed task
- [ ] Pending task

That's all!
"""

    print("🔍 Testing Stage1Interface integration...")

    # Test Stage 1 processing
    try:
        stage1 = Stage1Interface()
        stage1_results = stage1.process_document(content)

        print("✅ Stage 1 processing successful")
        print(f"   - Elements: {stage1_results.elements}")
        print(
            f"   - Lists: {len(stage1_results.elements.lists) if stage1_results.elements.lists else 0}"
        )
        print(
            f"   - Tables: {len(stage1_results.elements.tables) if stage1_results.elements.tables else 0}"
        )

        # Test Stage 2 processing
        chunker = MarkdownChunker()
        result = chunker.chunk_with_analysis(content)

        print("✅ Stage 2 processing successful")
        print(f"   - Strategy: {result.strategy_used}")
        print(f"   - Chunks: {len(result.chunks)}")
        print(f"   - Processing time: {result.processing_time:.3f}s")

        # Monitor Stage 1 usage rate
        stage1_usage_count = 0
        total_chunks = len(result.chunks)

        for chunk in result.chunks:
            # Check if chunk metadata indicates Stage 1 usage
            if chunk.get_metadata("source") == "stage1_analysis":
                stage1_usage_count += 1

        stage1_usage_rate = (
            (stage1_usage_count / total_chunks * 100) if total_chunks > 0 else 0
        )

        print("📊 Stage 1 Usage Monitoring:")
        print(f"   - Stage 1 chunks: {stage1_usage_count}/{total_chunks}")
        print(f"   - Usage rate: {stage1_usage_rate:.1f}%")

        if stage1_usage_rate >= 80:
            print("✅ Stage 1 usage rate meets target (≥80%)")
        elif stage1_usage_rate >= 50:
            print("⚠️ Stage 1 usage rate moderate (50-79%)")
        else:
            print("❌ Stage 1 usage rate low (<50%)")

        # Verify chunks contain expected content
        all_content = " ".join(chunk.content for chunk in result.chunks)

        # Check for task lists (our recent fix)
        if "- [x] Completed task" in all_content:
            print("✅ Task lists formatted correctly")
        else:
            print("❌ Task list formatting issue detected")
            print(f"   Content: {all_content}")

        # Check for tables
        if "| Column A |" in all_content:
            print("✅ Tables preserved correctly")
        else:
            print("❌ Table preservation issue detected")

        # Check for regular lists
        if "- Item 1" in all_content:
            print("✅ Regular lists preserved correctly")
        else:
            print("❌ Regular list preservation issue detected")
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_fallback_rate_monitoring():
    """Test fallback rate monitoring to ensure it stays below 10%."""

    print("\n🔍 Testing fallback rate monitoring...")

    test_documents = [
        # Document with lists (should use list or mixed strategy)
        """# Lists Document

- Item 1
- Item 2
- Item 3

More content here.
""",
        # Document with tables (should use table or mixed strategy)
        """# Tables Document

| A | B |
|---|---|
| 1 | 2 |
| 3 | 4 |

More content here.
""",
        # Document with code (should use code strategy)
        """# Code Document

```python
def example():
    return "code"
```

```javascript
function test() {
    return true;
}
```

More content here.
""",
        # Mixed content document
        """# Mixed Document

Some text content.

## Code Section

```python
def mixed_example():
    return "mixed"
```

## List Section

- Mixed item 1
- Mixed item 2

## Table Section

| Mixed | Content |
|-------|---------|
| A     | B       |

Final text.
""",
        # Simple text document (should use structural or sentences)
        """# Simple Document

This is just a simple text document with multiple paragraphs.

## Section 1

Some content in section 1.

## Section 2

Some content in section 2.

## Conclusion

Final thoughts.
""",
    ]

    chunker = MarkdownChunker()
    fallback_count = 0
    total_documents = len(test_documents)

    for i, content in enumerate(test_documents):
        try:
            result = chunker.chunk_with_analysis(content)

            # Check if emergency fallback was used (fallback_level >= 4)
            fallback_level = getattr(result, "fallback_level", 0)
            if fallback_level >= 4:
                fallback_count += 1
                print(
                    f"⚠️ Document {i+1}: Emergency fallback used (level {fallback_level})"
                )
            else:
                print(
                    f"✅ Document {i+1}: Normal processing (strategy: {result.strategy_used})"
                )

        except Exception as e:
            fallback_count += 1
            print(f"❌ Document {i+1}: Processing failed: {e}")

    fallback_rate = (
        (fallback_count / total_documents * 100) if total_documents > 0 else 0
    )

    print("\n📊 Fallback Rate Monitoring:")
    print(f"   - Emergency fallbacks: {fallback_count}/{total_documents}")
    print(f"   - Fallback rate: {fallback_rate:.1f}%")

    if fallback_rate < 10:
        print("✅ Fallback rate meets target (<10%)")
    else:
        print("❌ Fallback rate exceeds target (≥10%)")
        return False


if __name__ == "__main__":
    print("🔍 Running comprehensive Stage 1/Stage 2 validation...")

    # Test integration
    integration_success = test_stage1_interface_integration()

    # Test fallback rate monitoring
    fallback_success = test_fallback_rate_monitoring()

    # Overall result
    if integration_success and fallback_success:
        print("\n🎉 All validation tests successful!")
        print("   ✅ Stage1Interface integration working")
        print("   ✅ Fallback rate within acceptable limits")
        print("   ✅ Stage 1 usage rate monitoring active")
    else:
        print("\n💥 Some validation tests failed!")
        if not integration_success:
            print("   ❌ Stage1Interface integration issues")
        if not fallback_success:
            print("   ❌ Fallback rate too high")
        exit(1)
