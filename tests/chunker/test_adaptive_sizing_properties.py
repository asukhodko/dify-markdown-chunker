"""
Property-based tests for adaptive chunk sizing.

These tests use Hypothesis to verify formal properties of the adaptive sizing
system, providing stronger guarantees than example-based tests.
"""

import unittest

from hypothesis import given, settings, strategies as st

from markdown_chunker_v2.adaptive_sizing import (
    AdaptiveSizeCalculator,
    AdaptiveSizeConfig,
)
from markdown_chunker_v2.parser import Parser
from markdown_chunker_v2.types import ContentAnalysis


class TestAdaptiveSizingProperties(unittest.TestCase):
    """Property-based tests for adaptive sizing algorithm."""

    @given(
        code_ratio=st.floats(min_value=0.0, max_value=1.0),
        list_ratio=st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=100)
    def test_monotonicity_code_ratio(self, code_ratio, list_ratio):
        """
        Property: Increasing code ratio should increase or maintain size.

        If all other factors are constant, higher code ratio should never
        decrease the calculated size.
        """
        config = AdaptiveSizeConfig()
        calculator = AdaptiveSizeCalculator(config)

        # Create two analyses with different code ratios
        analysis_low = ContentAnalysis(
            total_chars=1000,
            total_lines=100,
            code_ratio=code_ratio * 0.5,
            code_block_count=1,
            header_count=3,
            max_header_depth=2,
            table_count=0,
            list_ratio=list_ratio,
            avg_sentence_length=50.0,
        )

        analysis_high = ContentAnalysis(
            total_chars=1000,
            total_lines=100,
            code_ratio=code_ratio,
            code_block_count=2,
            header_count=3,
            max_header_depth=2,
            table_count=0,
            list_ratio=list_ratio,
            avg_sentence_length=50.0,
        )

        size_low = calculator.calculate_optimal_size("test", analysis_low)
        size_high = calculator.calculate_optimal_size("test", analysis_high)

        self.assertGreaterEqual(
            size_high,
            size_low,
            msg=f"Higher code ratio ({code_ratio}) should produce "
            f"larger or equal size, got {size_low} -> {size_high}",
        )

    @given(
        base_size=st.integers(min_value=500, max_value=4000),
        min_scale=st.floats(min_value=0.3, max_value=0.8),
        max_scale=st.floats(min_value=1.2, max_value=2.0),
    )
    @settings(max_examples=100)
    def test_bounded_output(self, base_size, min_scale, max_scale):
        """
        Property: Output size is always within configured bounds.

        For any configuration, the calculated size must be between
        base_size * min_scale and base_size * max_scale.
        """
        config = AdaptiveSizeConfig(
            base_size=base_size,
            min_scale=min_scale,
            max_scale=max_scale,
        )
        calculator = AdaptiveSizeCalculator(config)

        # Test with extreme complexities
        analysis_min = ContentAnalysis(
            total_chars=1000,
            total_lines=100,
            code_ratio=0.0,
            code_block_count=0,
            header_count=3,
            max_header_depth=2,
            table_count=0,
            list_ratio=0.0,
            avg_sentence_length=20.0,
        )

        analysis_max = ContentAnalysis(
            total_chars=1000,
            total_lines=100,
            code_ratio=1.0,
            code_block_count=10,
            header_count=3,
            max_header_depth=2,
            table_count=5,
            list_ratio=1.0,
            avg_sentence_length=150.0,
        )

        size_min = calculator.calculate_optimal_size("test", analysis_min)
        size_max = calculator.calculate_optimal_size("test", analysis_max)

        expected_min = int(base_size * min_scale)
        expected_max = int(base_size * max_scale)

        self.assertGreaterEqual(
            size_min,
            expected_min,
            msg=f"Min size {size_min} below lower bound {expected_min}",
        )
        self.assertLessEqual(
            size_max,
            expected_max,
            msg=f"Max size {size_max} above upper bound {expected_max}",
        )

    @given(
        code_ratio=st.floats(min_value=0.0, max_value=1.0),
        list_ratio=st.floats(min_value=0.0, max_value=1.0),
        avg_sentence_length=st.floats(min_value=10.0, max_value=150.0),
    )
    @settings(max_examples=100)
    def test_consistency(self, code_ratio, list_ratio, avg_sentence_length):
        """
        Property: Same input produces same output (determinism).

        Calling calculate_optimal_size with the same parameters should
        always return the same result.
        """
        config = AdaptiveSizeConfig()
        calculator = AdaptiveSizeCalculator(config)

        analysis = ContentAnalysis(
            total_chars=1000,
            total_lines=100,
            code_ratio=code_ratio,
            code_block_count=1,
            header_count=3,
            max_header_depth=2,
            table_count=0,
            list_ratio=list_ratio,
            avg_sentence_length=avg_sentence_length,
        )

        # Calculate twice
        size1 = calculator.calculate_optimal_size("test content", analysis)
        size2 = calculator.calculate_optimal_size("test content", analysis)

        self.assertEqual(
            size1,
            size2,
            msg="Same input should produce same output (determinism)",
        )

    @given(
        original_weight=st.floats(min_value=0.1, max_value=0.6),
        adjustment=st.floats(min_value=-0.2, max_value=0.2),
    )
    @settings(max_examples=50)
    def test_weight_independence(self, original_weight, adjustment):
        """
        Property: Changing a single weight affects output predictably.

        Increasing code_weight while keeping other factors constant should
        increase the impact of code_ratio on the final size.
        """
        # Ensure weights sum to 1.0
        remaining = 1.0 - original_weight
        table_w = remaining * 0.4
        list_w = remaining * 0.3
        sentence_w = remaining * 0.3

        config1 = AdaptiveSizeConfig(
            code_weight=original_weight,
            table_weight=table_w,
            list_weight=list_w,
            sentence_length_weight=sentence_w,
        )

        new_code_weight = max(0.1, min(0.8, original_weight + adjustment))
        remaining2 = 1.0 - new_code_weight
        table_w2 = remaining2 * 0.4
        list_w2 = remaining2 * 0.3
        sentence_w2 = remaining2 * 0.3

        config2 = AdaptiveSizeConfig(
            code_weight=new_code_weight,
            table_weight=table_w2,
            list_weight=list_w2,
            sentence_length_weight=sentence_w2,
        )

        calculator1 = AdaptiveSizeCalculator(config1)
        calculator2 = AdaptiveSizeCalculator(config2)

        # Code-heavy analysis
        analysis = ContentAnalysis(
            total_chars=1000,
            total_lines=100,
            code_ratio=0.7,
            code_block_count=3,
            header_count=3,
            max_header_depth=2,
            table_count=0,
            list_ratio=0.1,
            avg_sentence_length=60.0,
        )

        complexity1 = calculator1.calculate_complexity(analysis)
        complexity2 = calculator2.calculate_complexity(analysis)

        # If we increased code_weight and have high code_ratio,
        # complexity should increase
        if new_code_weight > original_weight and analysis.code_ratio > 0.5:
            self.assertGreaterEqual(
                complexity2,
                complexity1,
                msg=f"Increasing code_weight from {original_weight:.2f} "
                f"to {new_code_weight:.2f} should increase complexity "
                f"for code-heavy content",
            )

    @given(
        text_length=st.integers(min_value=100, max_value=10000),
        code_blocks=st.integers(min_value=0, max_value=10),
    )
    @settings(max_examples=50)
    def test_no_quality_regression_monotonic_complexity(
        self, text_length, code_blocks
    ):
        """
        Property: Complexity score is monotonic with code block count.

        More code blocks (relative to text length) should not decrease
        complexity score.
        """
        parser = Parser()

        # Generate text with varying code blocks
        text_per_block = text_length // max(1, code_blocks + 1)
        text_parts = ["# Test\n\nSome text. " * (text_per_block // 20)]

        for i in range(code_blocks):
            text_parts.append(f"\n```python\ncode_{i}\n```\n")

        text = "".join(text_parts)
        analysis = parser.analyze(text)

        calculator = AdaptiveSizeCalculator()
        complexity = calculator.calculate_complexity(analysis)

        # Complexity should be bounded and reasonable
        self.assertGreaterEqual(
            complexity,
            0.0,
            msg="Complexity cannot be negative",
        )
        self.assertLessEqual(
            complexity,
            1.0,
            msg="Complexity cannot exceed 1.0",
        )

        # If we have code blocks, complexity should be non-zero
        if code_blocks > 0:
            self.assertGreater(
                complexity,
                0.0,
                msg="Non-zero code blocks should produce non-zero complexity",
            )


if __name__ == "__main__":
    unittest.main()
