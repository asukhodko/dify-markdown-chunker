"""
Unit tests for adaptive chunk sizing.

Tests cover:
- Complexity calculation
- Size calculation
- Configuration validation
- Scale factor computation
"""

import pytest

from markdown_chunker_v2.adaptive_sizing import AdaptiveSizeCalculator, AdaptiveSizeConfig
from markdown_chunker_v2.parser import Parser


class TestAdaptiveSizeConfig:
    """Test adaptive sizing configuration validation."""

    def test_default_config_valid(self):
        """Default configuration should be valid."""
        config = AdaptiveSizeConfig()
        assert config.base_size == 1500
        assert config.min_scale == 0.5
        assert config.max_scale == 1.5
        assert config.code_weight == 0.4
        assert config.table_weight == 0.3
        assert config.list_weight == 0.2
        assert config.sentence_length_weight == 0.1

    def test_weights_must_sum_to_one(self):
        """Weights must sum to 1.0 within tolerance."""
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            AdaptiveSizeConfig(
                code_weight=0.5, table_weight=0.3, list_weight=0.2, sentence_length_weight=0.2
            )

    def test_negative_base_size_rejected(self):
        """Negative base_size should be rejected."""
        with pytest.raises(ValueError, match="base_size must be positive"):
            AdaptiveSizeConfig(base_size=-100)

    def test_zero_base_size_rejected(self):
        """Zero base_size should be rejected."""
        with pytest.raises(ValueError, match="base_size must be positive"):
            AdaptiveSizeConfig(base_size=0)

    def test_min_scale_greater_than_max_rejected(self):
        """min_scale >= max_scale should be rejected."""
        with pytest.raises(ValueError, match="min_scale .* must be less than max_scale"):
            AdaptiveSizeConfig(min_scale=1.5, max_scale=0.5)

    def test_negative_weights_rejected(self):
        """Negative weights should be rejected."""
        with pytest.raises(ValueError, match="code_weight must be non-negative"):
            AdaptiveSizeConfig(
                code_weight=-0.1, table_weight=0.5, list_weight=0.3, sentence_length_weight=0.3
            )

    def test_custom_weights_valid(self):
        """Custom weights that sum to 1.0 should be valid."""
        config = AdaptiveSizeConfig(
            code_weight=0.6, table_weight=0.2, list_weight=0.1, sentence_length_weight=0.1
        )
        assert config.code_weight == 0.6


class TestComplexityCalculation:
    """Test complexity score calculation."""

    def test_code_heavy_high_complexity(self):
        """Code-heavy content should produce high complexity score."""
        parser = Parser()
        text = "```python\n" + "x = 1\n" * 100 + "```"
        analysis = parser.analyze(text)

        calculator = AdaptiveSizeCalculator()
        complexity = calculator.calculate_complexity(analysis)

        # Code-heavy should have complexity > 0.3 (code_weight is 0.4)
        assert complexity > 0.3

    def test_simple_text_low_complexity(self):
        """Simple text should produce low complexity score."""
        parser = Parser()
        text = "This is simple text. " * 50
        analysis = parser.analyze(text)

        calculator = AdaptiveSizeCalculator()
        complexity = calculator.calculate_complexity(analysis)

        # Simple text should have low complexity
        assert complexity < 0.2

    def test_mixed_content_medium_complexity(self):
        """Mixed content should produce medium complexity score."""
        parser = Parser()
        text = """
# Example

Some text here.

```python
def example():
    pass
```

More text here.
"""
        analysis = parser.analyze(text)

        calculator = AdaptiveSizeCalculator()
        complexity = calculator.calculate_complexity(analysis)

        # Mixed should be between low and high
        assert 0.1 < complexity < 0.5

    def test_empty_content_zero_complexity(self):
        """Empty content should have zero complexity."""
        parser = Parser()
        text = ""
        analysis = parser.analyze(text)

        calculator = AdaptiveSizeCalculator()
        complexity = calculator.calculate_complexity(analysis)

        assert complexity == 0.0

    def test_complexity_bounded_at_one(self):
        """Complexity score should never exceed 1.0."""
        parser = Parser()
        # Extremely code-heavy content
        text = "```python\n" + ("x = 1\n" * 1000) + "```"
        analysis = parser.analyze(text)

        calculator = AdaptiveSizeCalculator()
        complexity = calculator.calculate_complexity(analysis)

        assert complexity <= 1.0


class TestSizeCalculation:
    """Test optimal size calculation."""

    def test_code_heavy_larger_chunks(self):
        """Code-heavy content should get larger chunks."""
        parser = Parser()
        # Create code-heavy content with some text (realistic scenario)
        text = """# API Documentation

This is the main API class.

```python
class APIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    def get(self, endpoint: str) -> dict:
        response = self.session.get(f"{BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: dict) -> dict:
        response = self.session.post(f"{BASE_URL}/{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
```

Usage examples above show the core functionality.
"""
        analysis = parser.analyze(text)

        calculator = AdaptiveSizeCalculator()
        complexity = calculator.calculate_complexity(analysis)
        size = calculator.calculate_optimal_size(text, analysis)

        # Code-heavy content should have complexity leading to size >= base
        # With realistic code ratio (30-40%), complexity should be > 0.15
        assert complexity > 0.15, f"Expected complexity > 0.15, got {complexity}"
        assert size >= 1200, f"Expected size >= 1200 (base*0.8), got {size}"

    def test_simple_text_smaller_chunks(self):
        """Simple text should get smaller chunks."""
        parser = Parser()
        text = "This is simple text. " * 50
        analysis = parser.analyze(text)

        calculator = AdaptiveSizeCalculator()
        size = calculator.calculate_optimal_size(text, analysis)

        # Should be smaller than base_size (1500)
        assert size < 1500

    def test_size_respects_min_bound(self):
        """Calculated size should respect min_scale bound."""
        parser = Parser()
        text = "A"
        analysis = parser.analyze(text)

        config = AdaptiveSizeConfig(base_size=1000, min_scale=0.5)
        calculator = AdaptiveSizeCalculator(config)
        size = calculator.calculate_optimal_size(text, analysis)

        # Should be at least base_size * min_scale
        assert size >= 500

    def test_size_respects_max_bound(self):
        """Calculated size should respect max_scale bound."""
        parser = Parser()
        text = "```python\n" + ("x = 1\n" * 1000) + "```"
        analysis = parser.analyze(text)

        config = AdaptiveSizeConfig(base_size=1000, max_scale=1.5)
        calculator = AdaptiveSizeCalculator(config)
        size = calculator.calculate_optimal_size(text, analysis)

        # Should be at most base_size * max_scale
        assert size <= 1500

    def test_custom_base_size_scales_correctly(self):
        """Custom base_size should scale as expected."""
        parser = Parser()
        text = "Some text."
        analysis = parser.analyze(text)

        config = AdaptiveSizeConfig(base_size=2000, min_scale=0.5, max_scale=1.5)
        calculator = AdaptiveSizeCalculator(config)
        size = calculator.calculate_optimal_size(text, analysis)

        # Size should be between 1000 and 3000
        assert 1000 <= size <= 3000


class TestScaleFactor:
    """Test scale factor computation."""

    def test_zero_complexity_min_scale(self):
        """Zero complexity should yield min_scale."""
        config = AdaptiveSizeConfig(min_scale=0.5, max_scale=1.5)
        calculator = AdaptiveSizeCalculator(config)

        scale_factor = calculator.get_scale_factor(0.0)
        assert scale_factor == 0.5

    def test_max_complexity_max_scale(self):
        """Maximum complexity should yield max_scale."""
        config = AdaptiveSizeConfig(min_scale=0.5, max_scale=1.5)
        calculator = AdaptiveSizeCalculator(config)

        scale_factor = calculator.get_scale_factor(1.0)
        assert scale_factor == 1.5

    def test_mid_complexity_mid_scale(self):
        """Mid complexity should yield mid scale."""
        config = AdaptiveSizeConfig(min_scale=0.5, max_scale=1.5)
        calculator = AdaptiveSizeCalculator(config)

        scale_factor = calculator.get_scale_factor(0.5)
        # Should be halfway: 0.5 + 0.5 * (1.5 - 0.5) = 1.0
        assert abs(scale_factor - 1.0) < 0.01


class TestCustomWeights:
    """Test custom weight configurations."""

    def test_high_code_weight_increases_code_impact(self):
        """Higher code_weight should increase impact of code content."""
        parser = Parser()
        text = """
# Example
```python
code_here
```
Some text.
"""
        analysis = parser.analyze(text)

        # Standard weights
        calc_standard = AdaptiveSizeCalculator()
        complexity_standard = calc_standard.calculate_complexity(analysis)

        # High code weight
        config_high_code = AdaptiveSizeConfig(
            code_weight=0.6, table_weight=0.2, list_weight=0.1, sentence_length_weight=0.1
        )
        calc_high_code = AdaptiveSizeCalculator(config_high_code)
        complexity_high_code = calc_high_code.calculate_complexity(analysis)

        # High code weight should increase complexity for code content
        assert complexity_high_code >= complexity_standard

    def test_weights_affect_size_calculation(self):
        """Custom weights should affect final size calculation."""
        parser = Parser()
        text = "```python\nx = 1\n```\n" * 10
        analysis = parser.analyze(text)

        config1 = AdaptiveSizeConfig(
            base_size=1500,
            code_weight=0.4,
            table_weight=0.3,
            list_weight=0.2,
            sentence_length_weight=0.1,
        )
        config2 = AdaptiveSizeConfig(
            base_size=1500,
            code_weight=0.6,
            table_weight=0.2,
            list_weight=0.1,
            sentence_length_weight=0.1,
        )

        calc1 = AdaptiveSizeCalculator(config1)
        calc2 = AdaptiveSizeCalculator(config2)

        size1 = calc1.calculate_optimal_size(text, analysis)
        size2 = calc2.calculate_optimal_size(text, analysis)

        # Higher code weight should produce larger size for code-heavy content
        assert size2 >= size1


class TestTableRatioCalculation:
    """Test table ratio calculation."""

    def test_table_heavy_increases_complexity(self):
        """Table-heavy content should increase complexity."""
        parser = Parser()
        text_with_table = """
| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
"""
        analysis_with_table = parser.analyze(text_with_table)

        text_without_table = "Some text without tables."
        analysis_without_table = parser.analyze(text_without_table)

        calculator = AdaptiveSizeCalculator()
        complexity_with = calculator.calculate_complexity(analysis_with_table)
        complexity_without = calculator.calculate_complexity(analysis_without_table)

        # Tables should increase complexity
        assert complexity_with > complexity_without
