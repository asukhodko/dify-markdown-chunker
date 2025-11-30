#!/usr/bin/env python3
"""
Test script for ContentAnalysis validation functionality.

This script tests the validation features added for task 4.3:
- Structure integrity validation
- Cross-component consistency validation
- Serialization compatibility validation
"""

import logging

from markdown_chunker.parser.types import (
    ContentAnalysis,
    ElementCollection,
    FencedBlock,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def test_content_analysis_validation():
    """Test ContentAnalysis validation functionality."""

    print("🔍 Testing ContentAnalysis Validation...")

    # Test 1: Valid ContentAnalysis
    print("\n1. Testing valid ContentAnalysis...")

    valid_analysis = ContentAnalysis(
        total_chars=1000,
        total_lines=50,
        total_words=200,
        code_ratio=0.3,
        text_ratio=0.7,
        code_block_count=2,
        header_count=3,
        content_type="mixed",
        languages={"python", "javascript"},
        list_count=1,
        table_count=0,
        list_ratio=0.0,
        table_ratio=0.0,
    )

    # Test consistency validation
    consistency_issues = valid_analysis.validate_consistency()
    print(f"✅ Consistency validation: {len(consistency_issues)} issues")
    if consistency_issues:
        for issue in consistency_issues:
            print(f"   - {issue}")

    # Test structure validation
    structure_issues = valid_analysis.validate_structure_integrity()
    print(f"✅ Structure validation: {len(structure_issues)} issues")
    if structure_issues:
        for issue in structure_issues:
            print(f"   - {issue}")

    # Test serialization validation
    serialization_issues = valid_analysis.validate_serialization_compatibility()
    print(f"✅ Serialization validation: {len(serialization_issues)} issues")
    if serialization_issues:
        for issue in serialization_issues:
            print(f"   - {issue}")

    # Test full validation
    is_valid = valid_analysis.is_valid()
    print(f"✅ Overall validity: {is_valid}")

    # Test 2: Invalid ContentAnalysis (should fail at creation)
    print("\n2. Testing invalid ContentAnalysis creation...")

    try:
        ContentAnalysis(
            total_chars=-100,  # Invalid: negative
            total_lines=50,
            total_words=200,
            code_ratio=1.5,  # Invalid: out of bounds
            text_ratio=0.7,  # Invalid: ratios sum > 1
            code_block_count=-1,  # Invalid: negative
            header_count=3,
            content_type="invalid_type",  # Invalid: not in allowed types
            languages={"python"},
            complexity_score=2.0,  # Invalid: out of bounds
        )
        print("❌ Invalid analysis was created (should have failed)")
    except ValueError as e:
        print(f"✅ Correctly rejected invalid analysis: {e}")

    # Test 3: Create analysis with borderline invalid values that pass __post_init__
    print("\n3. Testing analysis with validation issues...")

    # Create analysis that passes initial validation but has consistency issues
    problematic_analysis = ContentAnalysis(
        total_chars=100,
        total_lines=10,
        total_words=20,
        code_ratio=0.8,  # High code ratio
        text_ratio=0.2,
        code_block_count=0,  # But no code blocks - inconsistent!
        header_count=0,
        content_type="code_heavy",  # Says code heavy but no blocks
        languages=set(),
    )

    # Manually set some problematic values after creation
    problematic_analysis.max_header_depth = 3  # But header_count is 0

    consistency_issues = problematic_analysis.validate_consistency()
    print(f"❌ Consistency issues detected: {len(consistency_issues)}")
    for issue in consistency_issues:
        print(f"   - {issue}")

    is_valid = problematic_analysis.is_valid()
    print(f"❌ Overall validity: {is_valid}")

    print("\n🎉 ContentAnalysis validation testing completed!")


def test_cross_component_validation():
    """Test cross-component validation."""

    print("\n🔍 Testing Cross-Component Validation...")

    # Create test components
    analysis = ContentAnalysis(
        total_chars=500,
        total_lines=25,
        total_words=100,
        code_ratio=0.4,
        text_ratio=0.6,
        code_block_count=2,
        header_count=2,
        content_type="mixed",
        languages={"python"},
    )

    # Test 1: Consistent components
    print("\n1. Testing with consistent components...")

    # Create mock fenced blocks
    fenced_blocks = [
        FencedBlock(
            content="print('hello')",
            language="python",
            fence_type="```",
            fence_length=3,
            start_line=1,
            end_line=3,
            start_offset=0,
            end_offset=20,
            nesting_level=0,
            is_closed=True,
            raw_content="```python\nprint('hello')\n```",
        ),
        FencedBlock(
            content="console.log('world')",
            language="javascript",
            fence_type="```",
            fence_length=3,
            start_line=5,
            end_line=7,
            start_offset=50,
            end_offset=80,
            nesting_level=0,
            is_closed=True,
            raw_content="```javascript\nconsole.log('world')\n```",
        ),
    ]

    # Create mock elements
    elements = ElementCollection()
    # Add mock headers (would normally be populated by element detector)

    components = {"fenced_blocks": fenced_blocks, "elements": elements}

    cross_issues = analysis.validate_cross_component_consistency(components)
    print(f"✅ Cross-component validation: {len(cross_issues)} issues")
    for issue in cross_issues:
        print(f"   - {issue}")

    # Test 2: Inconsistent components
    print("\n2. Testing with inconsistent components...")

    # Create inconsistent analysis
    inconsistent_analysis = ContentAnalysis(
        total_chars=500,
        total_lines=25,
        total_words=100,
        code_ratio=0.4,
        text_ratio=0.6,
        code_block_count=5,  # Mismatch: says 5 but only 2 blocks
        header_count=10,  # Mismatch: says 10 but elements has 0
        content_type="mixed",
        languages={"python"},
    )

    cross_issues = inconsistent_analysis.validate_cross_component_consistency(
        components
    )
    print(f"❌ Cross-component issues detected: {len(cross_issues)}")
    for issue in cross_issues:
        print(f"   - {issue}")

    print("\n🎉 Cross-component validation testing completed!")


def test_serialization_validation():
    """Test serialization validation specifically."""

    print("\n🔍 Testing Serialization Validation...")

    # Test 1: Valid serialization
    print("\n1. Testing valid serialization...")

    analysis = ContentAnalysis(
        total_chars=100,
        total_lines=10,
        total_words=20,
        code_ratio=0.2,
        text_ratio=0.8,
        code_block_count=1,
        header_count=1,
        content_type="text_heavy",
        languages={"python", "javascript"},  # Set should be serializable
    )

    serialization_issues = analysis.validate_serialization_compatibility()
    print(f"✅ Serialization validation: {len(serialization_issues)} issues")
    for issue in serialization_issues:
        print(f"   - {issue}")

    # Test actual serialization
    try:
        import json

        summary = analysis.get_summary()
        json_str = json.dumps(summary, indent=2)
        print("✅ JSON serialization successful")
        print(f"   - JSON length: {len(json_str)} characters")
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")

    print("\n🎉 Serialization validation testing completed!")


if __name__ == "__main__":
    test_content_analysis_validation()
    test_cross_component_validation()
    test_serialization_validation()
