"""
Tests for StrategySelector class.

This module tests the strategy selection logic including priority-based
and weighted selection modes.
"""

from unittest.mock import Mock

import pytest

from markdown_chunker.chunker.selector import StrategySelectionError, StrategySelector
from markdown_chunker.chunker.strategies.base import BaseStrategy
from markdown_chunker.chunker.types import ChunkConfig
from markdown_chunker.parser.types import ContentAnalysis


class MockStrategy(BaseStrategy):
    """Mock strategy for testing."""

    def __init__(
        self,
        name: str,
        priority: int,
        can_handle_result: bool = True,
        quality_score: float = 0.8,
    ):
        self._name = name
        self._priority = priority
        self._can_handle_result = can_handle_result
        self._quality_score = quality_score

    @property
    def name(self) -> str:
        return self._name

    @property
    def priority(self) -> int:
        return self._priority

    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        return self._can_handle_result

    def calculate_quality(self, analysis: ContentAnalysis) -> float:
        return self._quality_score

    def apply(self, content: str, stage1_results, config: ChunkConfig):
        return []


class TestStrategySelector:
    """Test cases for StrategySelector."""

    def test_selector_creation_strict_mode(self):
        """Test creating selector in strict mode."""
        strategies = [
            MockStrategy("high_priority", 1),
            MockStrategy("low_priority", 3),
            MockStrategy("medium_priority", 2),
        ]

        selector = StrategySelector(strategies, mode="strict")

        assert selector.mode == "strict"
        assert len(selector.strategies) == 3
        # Should be sorted by priority
        assert selector.strategies[0].name == "high_priority"
        assert selector.strategies[1].name == "medium_priority"
        assert selector.strategies[2].name == "low_priority"

    def test_selector_creation_weighted_mode(self):
        """Test creating selector in weighted mode."""
        strategies = [MockStrategy("test", 1)]
        selector = StrategySelector(strategies, mode="weighted")

        assert selector.mode == "weighted"

    def test_selector_invalid_mode(self):
        """Test creating selector with invalid mode."""
        strategies = [MockStrategy("test", 1)]

        with pytest.raises(ValueError, match="Invalid selection mode"):
            StrategySelector(strategies, mode="invalid")

    def test_strict_selection_first_applicable(self):
        """Test strict mode selects first applicable strategy by priority."""
        strategies = [
            MockStrategy("high_priority", 1, can_handle_result=False),
            MockStrategy("medium_priority", 2, can_handle_result=True),
            MockStrategy("low_priority", 3, can_handle_result=True),
        ]

        selector = StrategySelector(strategies, mode="strict")
        analysis = Mock(spec=ContentAnalysis)
        config = ChunkConfig.default()

        selected = selector.select_strategy(analysis, config)

        assert selected.name == "medium_priority"

    def test_strict_selection_no_applicable(self):
        """Test strict mode uses emergency fallback when no strategy can handle."""
        strategies = [
            MockStrategy("strategy1", 1, can_handle_result=False),
            MockStrategy("strategy2", 2, can_handle_result=False),
        ]

        selector = StrategySelector(strategies, mode="strict")
        analysis = Mock(spec=ContentAnalysis)
        config = ChunkConfig.default()

        # Emergency fallback should activate instead of raising
        selected = selector.select_strategy(analysis, config)
        assert selected is not None, "Emergency fallback should select a strategy"

    def test_weighted_selection_best_score(self):
        """Test weighted mode selects strategy with best combined score."""
        strategies = [
            MockStrategy(
                "high_priority_low_quality", 1, True, 0.3
            ),  # final_score ≈ 0.65
            MockStrategy(
                "low_priority_high_quality", 3, True, 0.9
            ),  # final_score ≈ 0.62
            MockStrategy("medium_both", 2, True, 0.6),  # final_score ≈ 0.55
        ]

        selector = StrategySelector(strategies, mode="weighted")
        analysis = Mock(spec=ContentAnalysis)
        config = ChunkConfig.default()

        selected = selector.select_strategy(analysis, config)

        # High priority should win despite lower quality
        assert selected.name == "high_priority_low_quality"

    def test_weighted_selection_no_applicable(self):
        """Test weighted mode raises error when no strategy can handle."""
        strategies = [
            MockStrategy("strategy1", 1, can_handle_result=False),
            MockStrategy("strategy2", 2, can_handle_result=False),
        ]

        selector = StrategySelector(strategies, mode="weighted")
        analysis = Mock(spec=ContentAnalysis)
        config = ChunkConfig.default()

        with pytest.raises(StrategySelectionError):
            selector.select_strategy(analysis, config)

    def test_get_applicable_strategies(self):
        """Test getting all applicable strategies with scores."""
        strategies = [
            MockStrategy("high_quality", 2, True, 0.9),
            MockStrategy("medium_quality", 1, True, 0.6),
            MockStrategy("cannot_handle", 3, False, 0.8),
        ]

        selector = StrategySelector(strategies)
        analysis = Mock(spec=ContentAnalysis)
        config = ChunkConfig.default()

        applicable = selector.get_applicable_strategies(analysis, config)

        assert len(applicable) == 2  # Only 2 can handle
        # Should be sorted by final score (descending)
        assert applicable[0][0].name == "medium_quality"  # Higher priority wins
        assert applicable[1][0].name == "high_quality"

    def test_get_strategy_metrics(self):
        """Test getting detailed metrics for all strategies."""
        strategies = [
            MockStrategy("strategy1", 1, True, 0.8),
            MockStrategy("strategy2", 2, False, 0.6),
        ]

        selector = StrategySelector(strategies)
        analysis = Mock(spec=ContentAnalysis)
        config = ChunkConfig.default()

        metrics = selector.get_strategy_metrics(analysis, config)

        assert len(metrics) == 2
        assert metrics[0].strategy_name == "strategy1"
        assert metrics[0].can_handle is True
        assert metrics[1].strategy_name == "strategy2"
        assert metrics[1].can_handle is False

    def test_explain_selection(self):
        """Test selection explanation functionality."""
        strategies = [
            MockStrategy("selected", 1, True, 0.8),
            MockStrategy("not_selected", 2, True, 0.6),
        ]

        selector = StrategySelector(strategies, mode="strict")

        # Mock analysis with required attributes
        analysis = Mock(spec=ContentAnalysis)
        analysis.content_type = "mixed"
        analysis.code_ratio = 0.4
        analysis.code_block_count = 5
        analysis.list_count = 3
        analysis.table_count = 1
        analysis.header_count = 8
        analysis.complexity_score = 0.6
        analysis.has_mixed_content = True

        config = ChunkConfig.default()

        explanation = selector.explain_selection(analysis, config)

        assert explanation["selected_strategy"] == "selected"
        assert explanation["selection_mode"] == "strict"
        assert "content_analysis" in explanation
        assert "strategy_evaluation" in explanation
        assert len(explanation["strategy_evaluation"]) == 2

        # Check that selected strategy is marked
        selected_eval = next(
            s for s in explanation["strategy_evaluation"] if s["selected"]
        )
        assert selected_eval["name"] == "selected"

    def test_validate_strategies_valid(self):
        """Test strategy validation with valid configuration."""
        strategies = [
            MockStrategy("code", 1),
            MockStrategy("mixed", 2),
            MockStrategy("sentences", 3),  # Fallback
        ]

        selector = StrategySelector(strategies)
        issues = selector.validate_strategies()

        assert len(issues) == 0

    def test_validate_strategies_no_strategies(self):
        """Test validation with no strategies."""
        selector = StrategySelector([])
        issues = selector.validate_strategies()

        assert "No strategies configured" in issues

    def test_validate_strategies_duplicate_priorities(self):
        """Test validation with duplicate priorities."""
        strategies = [
            MockStrategy("strategy1", 1),
            MockStrategy("strategy2", 1),  # Duplicate priority
        ]

        selector = StrategySelector(strategies)
        issues = selector.validate_strategies()

        assert any("Duplicate strategy priorities" in issue for issue in issues)

    def test_validate_strategies_no_fallback(self):
        """Test validation without fallback strategy."""
        strategies = [MockStrategy("code", 1), MockStrategy("mixed", 2)]

        selector = StrategySelector(strategies)
        issues = selector.validate_strategies()

        assert any("No fallback strategy" in issue for issue in issues)

    def test_validate_strategies_duplicate_names(self):
        """Test validation with duplicate strategy names."""
        strategies = [
            MockStrategy("duplicate", 1),
            MockStrategy("duplicate", 2),  # Duplicate name
        ]

        selector = StrategySelector(strategies)
        issues = selector.validate_strategies()

        assert any("Duplicate strategy names" in issue for issue in issues)

    def test_get_strategy_by_name(self):
        """Test getting strategy by name."""
        strategies = [MockStrategy("target", 1), MockStrategy("other", 2)]

        selector = StrategySelector(strategies)

        found = selector.get_strategy_by_name("target")
        assert found is not None
        assert found.name == "target"

        not_found = selector.get_strategy_by_name("nonexistent")
        assert not_found is None

    def test_add_strategy(self):
        """Test adding strategy to selector."""
        strategies = [MockStrategy("existing", 2)]
        selector = StrategySelector(strategies)

        new_strategy = MockStrategy("new", 1)
        selector.add_strategy(new_strategy)

        assert len(selector.strategies) == 2
        # Should be re-sorted by priority
        assert selector.strategies[0].name == "new"
        assert selector.strategies[1].name == "existing"

    def test_add_strategy_duplicate_name(self):
        """Test adding strategy with duplicate name."""
        strategies = [MockStrategy("existing", 1)]
        selector = StrategySelector(strategies)

        duplicate = MockStrategy("existing", 2)

        with pytest.raises(ValueError, match="already exists"):
            selector.add_strategy(duplicate)

    def test_remove_strategy(self):
        """Test removing strategy from selector."""
        strategies = [MockStrategy("keep", 1), MockStrategy("remove", 2)]
        selector = StrategySelector(strategies)

        removed = selector.remove_strategy("remove")
        assert removed is True
        assert len(selector.strategies) == 1
        assert selector.strategies[0].name == "keep"

        not_removed = selector.remove_strategy("nonexistent")
        assert not_removed is False

    def test_get_strategy_names(self):
        """Test getting list of strategy names."""
        strategies = [MockStrategy("first", 1), MockStrategy("second", 2)]
        selector = StrategySelector(strategies)

        names = selector.get_strategy_names()
        assert names == ["first", "second"]

    def test_string_representations(self):
        """Test string representations of selector."""
        strategies = [MockStrategy("test", 1)]
        selector = StrategySelector(strategies, mode="weighted")

        str_repr = str(selector)
        assert "weighted mode" in str_repr
        assert "test" in str_repr

        repr_str = repr(selector)
        assert "StrategySelector" in repr_str
        assert "weighted" in repr_str
        assert "1" in repr_str  # Number of strategies


class TestStrategySelectionIntegration:
    """Integration tests for strategy selection."""

    def test_realistic_strategy_selection(self):
        """Test strategy selection with realistic scenarios."""
        # Create strategies mimicking real ones
        strategies = [
            MockStrategy("code", 1, can_handle_result=False, quality_score=0.9),
            MockStrategy("mixed", 2, can_handle_result=True, quality_score=0.7),
            MockStrategy("list", 3, can_handle_result=False, quality_score=0.6),
            MockStrategy("structural", 4, can_handle_result=True, quality_score=0.5),
            MockStrategy("sentences", 5, can_handle_result=True, quality_score=0.3),
        ]

        selector = StrategySelector(strategies, mode="strict")
        analysis = Mock(spec=ContentAnalysis)
        config = ChunkConfig.default()

        # Should select "mixed" (first applicable by priority)
        selected = selector.select_strategy(analysis, config)
        assert selected.name == "mixed"

    def test_weighted_vs_strict_comparison(self):
        """Test difference between weighted and strict selection."""
        strategies = [
            MockStrategy("high_priority_low_quality", 1, True, 0.2),
            MockStrategy("low_priority_high_quality", 3, True, 0.9),
        ]

        analysis = Mock(spec=ContentAnalysis)
        config = ChunkConfig.default()

        # Strict mode: select by priority
        strict_selector = StrategySelector(strategies, mode="strict")
        strict_selected = strict_selector.select_strategy(analysis, config)
        assert strict_selected.name == "high_priority_low_quality"

        # Weighted mode: might select different strategy based on combined score
        weighted_selector = StrategySelector(strategies, mode="weighted")
        weighted_selected = weighted_selector.select_strategy(analysis, config)

        # Calculate expected scores:
        # high_priority_low_quality: priority_weight=1.0, quality=0.2 -> final_score=(1.0*0.5) + (0.2*0.5) = 0.6
        # low_priority_high_quality: priority_weight=1/3≈0.33, quality=0.9 -> final_score=(0.33*0.5) + (0.9*0.5) = 0.615
        # So high quality should actually win
        assert weighted_selected.name == "low_priority_high_quality"
