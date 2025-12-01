"""
Strategy selector for choosing optimal chunking strategy.

This module implements the logic for automatically selecting the best
chunking strategy based on content analysis from Stage 1.
"""

import logging
from typing import List, Optional, Tuple

from markdown_chunker.parser.types import ContentAnalysis

from .strategies.base import BaseStrategy
from .types import ChunkConfig, StrategyMetrics

logger = logging.getLogger(__name__)


class StrategySelectionError(Exception):
    """Raised when strategy selection fails."""


class StrategySelector:
    """
    Selects optimal chunking strategy based on content analysis.

    The selector uses a priority-based system with quality scoring to
    determine the best strategy for a given document. Strategies are
    evaluated in priority order, and the first applicable strategy with
    sufficient quality is selected.

    Selection modes:
    - strict: Select first applicable strategy by priority
    - weighted: Select best strategy by combined priority + quality score
    """

    def __init__(self, strategies: List[BaseStrategy], mode: str = "strict"):
        """
        Initialize strategy selector.

        Args:
            strategies: List of available strategies
            mode: Selection mode ("strict" or "weighted")
        """
        self.strategies = sorted(strategies, key=lambda s: s.priority)
        self.mode = mode

        if mode not in ["strict", "weighted"]:
            raise ValueError(
                f"Invalid selection mode: {mode}. Must be 'strict' or 'weighted'"
            )

        logger.info(
            f"StrategySelector initialized with {len(strategies)} "
            f"strategies in {mode} mode"
        )

    def select_strategy(
        self, analysis: ContentAnalysis, config: ChunkConfig
    ) -> BaseStrategy:
        """
        Select best strategy for content.

        Args:
            analysis: Content analysis from Stage 1
            config: Chunking configuration

        Returns:
            Selected strategy

        Raises:
            StrategySelectionError: If no strategy can handle the content
        """
        if self.mode == "strict":
            return self._select_strict(analysis, config)
        else:
            return self._select_weighted(analysis, config)

    def _select_strict(  # noqa: C901
        self, analysis: ContentAnalysis, config: ChunkConfig
    ) -> BaseStrategy:
        """
        Select strategy using strict priority-based selection.

        Returns the first strategy (by priority) that can handle the content.

        Content density rules (Requirements 6.1-6.3):
        - >50% list elements -> prefer list strategy
        - >3 tables -> prefer table strategy
        - >3 headers with hierarchy -> prefer structural strategy

        Note: List strategy is excluded from auto-selection for safety.
        It can still be used via explicit strategy override.
        """
        logger.debug("Using strict strategy selection")

        # Check content density for strategy preference
        preferred_strategy = self._get_preferred_strategy_by_density(analysis)
        if preferred_strategy:
            logger.info(f"Content density suggests: {preferred_strategy} strategy")

        # FIX 2: Filter out list strategy in auto mode for safety
        # List strategy can lose non-list content in mixed documents
        safe_strategies = [s for s in self.strategies if s.name != "list"]

        logger.info("Auto mode: list strategy excluded for safety (mixed-content risk)")

        # If we have a preferred strategy, try it first
        if preferred_strategy:
            for strategy in safe_strategies:
                if strategy.name == preferred_strategy:
                    if strategy.can_handle(analysis, config):
                        self._log_selection_reason(
                            strategy.name,
                            f"Content density match: {preferred_strategy}",
                            analysis,
                        )
                        return strategy
                    break

        for strategy in safe_strategies:
            if strategy.can_handle(analysis, config):
                self._log_selection_reason(
                    strategy.name,
                    f"Priority-based selection (priority {strategy.priority})",
                    analysis,
                )
                return strategy

        # Fallback to structural strategy if no safe strategy can handle
        # This should rarely happen since sentences strategy handles everything
        for strategy in safe_strategies:
            if strategy.name == "structural":
                self._log_selection_reason(
                    "structural",
                    "Fallback: no strategy matched",
                    analysis,
                )
                return strategy

        # Emergency fallback: return first safe strategy
        if safe_strategies:
            self._log_selection_reason(
                safe_strategies[0].name,
                "Emergency fallback",
                analysis,
            )
            return safe_strategies[0]

        raise StrategySelectionError("No safe strategy available")

    def _log_selection_reason(
        self, strategy_name: str, reason: str, analysis: ContentAnalysis
    ) -> None:
        """
        Log the reason for strategy selection (Requirement 6.4).

        Args:
            strategy_name: Name of selected strategy
            reason: Reason for selection
            analysis: Content analysis
        """
        total_headers = analysis.get_total_header_count()
        logger.info(
            f"Strategy selected: {strategy_name} | "
            f"Reason: {reason} | "
            f"Content: headers={total_headers}, "
            f"tables={analysis.table_count}, "
            f"lists={analysis.list_count}, "
            f"code_ratio={analysis.code_ratio:.2f}"
        )

    def _select_weighted(
        self, analysis: ContentAnalysis, config: ChunkConfig
    ) -> BaseStrategy:
        """
        Select strategy using weighted scoring (priority + quality).

        Evaluates all applicable strategies and selects the one with
        the highest combined score.

        Content density rules (Requirements 6.1-6.3):
        - >50% list elements -> prefer list strategy
        - >3 tables -> prefer table strategy
        - >3 headers with hierarchy -> prefer structural strategy

        Note: List strategy is excluded from auto-selection for safety.
        It can still be used via explicit strategy override.
        """
        logger.debug("Using weighted strategy selection")

        # Check content density for strategy preference
        preferred_strategy = self._get_preferred_strategy_by_density(analysis)
        if preferred_strategy:
            logger.info(f"Content density suggests: {preferred_strategy} strategy")

        # FIX 2: Filter out list strategy in auto mode for safety
        safe_strategies = [s for s in self.strategies if s.name != "list"]

        logger.info("Auto mode: list strategy excluded for safety (mixed-content risk)")

        candidates = []

        for strategy in safe_strategies:
            if strategy.can_handle(analysis, config):
                metrics = strategy.get_metrics(analysis, config)
                # Boost score for preferred strategy
                final_score = metrics.final_score
                if preferred_strategy and strategy.name == preferred_strategy:
                    final_score += 0.2  # Boost preferred strategy
                    logger.debug(
                        f"Strategy {strategy.name}: boosted by content density"
                    )
                candidates.append((strategy, metrics, final_score))
                logger.debug(
                    f"Strategy {strategy.name}: quality={metrics.quality_score:.3f}, "
                    f"final_score={final_score:.3f}"
                )

        if not candidates:
            # Fallback to structural
            for strategy in safe_strategies:
                if strategy.name == "structural":
                    logger.warning("No strategy matched, using structural as fallback")
                    return strategy
            raise StrategySelectionError("No safe strategy can handle the content")

        # Select strategy with highest final score (including boost)
        best_strategy, best_metrics, best_score = max(candidates, key=lambda x: x[2])

        logger.info(
            f"Selected strategy: {best_strategy.name} " f"(score={best_score:.3f})"
        )

        return best_strategy

    def _get_preferred_strategy_by_density(
        self, analysis: ContentAnalysis
    ) -> Optional[str]:
        """
        Determine preferred strategy based on content density.

        Requirements 6.1-6.3:
        - >50% list elements -> prefer list strategy
        - >3 tables -> prefer table strategy
        - >3 headers with hierarchy -> prefer structural strategy

        Priority: structural > table > list (Requirement 6.5)

        Args:
            analysis: Content analysis from Stage 1

        Returns:
            Preferred strategy name or None
        """
        # Check for structural preference first (highest priority)
        total_headers = analysis.get_total_header_count()
        if total_headers > 3 and analysis.max_header_depth > 1:
            logger.debug(
                f"Structural preferred: {total_headers} headers, "
                f"depth {analysis.max_header_depth}"
            )
            return "structural"

        # Check for table preference
        if analysis.table_count > 3:
            logger.debug(f"Table preferred: {analysis.table_count} tables")
            return "table"

        # Check for list preference (>50% list content)
        # Note: list strategy is excluded from auto mode, but we still log
        if analysis.list_ratio > 0.5:
            logger.debug(f"List content detected: {analysis.list_ratio:.1%}")
            # Return mixed instead since list is excluded from auto
            return "mixed"

        return None

    def get_applicable_strategies(
        self, analysis: ContentAnalysis, config: ChunkConfig
    ) -> List[Tuple[BaseStrategy, float]]:
        """
        Get all applicable strategies with quality scores.

        Args:
            analysis: Content analysis from Stage 1
            config: Chunking configuration

        Returns:
            List of (strategy, quality_score) tuples, sorted by final score descending
        """
        applicable = []

        for strategy in self.strategies:
            if strategy.can_handle(analysis, config):
                metrics = strategy.get_metrics(analysis, config)
                applicable.append((strategy, metrics.final_score))

        # Sort by final score (descending)
        applicable.sort(key=lambda x: x[1], reverse=True)

        return applicable

    def get_strategy_metrics(
        self, analysis: ContentAnalysis, config: ChunkConfig
    ) -> List[StrategyMetrics]:
        """
        Get detailed metrics for all strategies.

        Args:
            analysis: Content analysis from Stage 1
            config: Chunking configuration

        Returns:
            List of StrategyMetrics for all strategies
        """
        metrics = []

        for strategy in self.strategies:
            strategy_metrics = strategy.get_metrics(analysis, config)
            metrics.append(strategy_metrics)

        return metrics

    def explain_selection(self, analysis: ContentAnalysis, config: ChunkConfig) -> dict:
        """
        Explain why a particular strategy was selected.

        Args:
            analysis: Content analysis from Stage 1
            config: Chunking configuration

        Returns:
            Dictionary with selection explanation
        """
        selected_strategy = self.select_strategy(analysis, config)
        all_metrics = self.get_strategy_metrics(analysis, config)

        explanation: dict = {
            "selected_strategy": selected_strategy.name,
            "selection_mode": self.mode,
            "content_analysis": {
                "content_type": analysis.content_type,
                "code_ratio": analysis.code_ratio,
                "code_blocks": analysis.code_block_count,
                "list_count": analysis.list_count,
                "table_count": analysis.table_count,
                "header_count": analysis.header_count,
                "complexity_score": analysis.complexity_score,
                "has_mixed_content": analysis.has_mixed_content,
            },
            "strategy_evaluation": [],
        }

        for metrics in all_metrics:
            strategy_info = {
                "name": metrics.strategy_name,
                "priority": metrics.priority,
                "can_handle": metrics.can_handle,
                "quality_score": metrics.quality_score,
                "final_score": metrics.final_score,
                "reason": metrics.reason,
                "selected": metrics.strategy_name == selected_strategy.name,
            }
            explanation["strategy_evaluation"].append(strategy_info)

        return explanation

    def validate_strategies(self) -> List[str]:
        """
        Validate that the strategy configuration is correct.

        Returns:
            List of validation issues (empty if valid)
        """
        issues: List[str] = []

        if not self.strategies:
            issues.append("No strategies configured")
            return issues

        # Check for duplicate priorities
        priorities = [s.priority for s in self.strategies]
        if len(priorities) != len(set(priorities)):
            issues.append("Duplicate strategy priorities detected")

        # Check for fallback strategy (should have lowest priority)
        fallback_strategies = [s for s in self.strategies if s.name == "sentences"]
        if not fallback_strategies:
            issues.append("No fallback strategy (SentencesStrategy) configured")
        elif fallback_strategies[0].priority != max(priorities):
            issues.append(
                "Fallback strategy should have lowest priority (highest number)"
            )

        # Check strategy names are unique
        names = [s.name for s in self.strategies]
        if len(names) != len(set(names)):
            issues.append("Duplicate strategy names detected")

        return issues

    def get_strategy_by_name(self, name: str) -> Optional[BaseStrategy]:
        """
        Get strategy by name.

        Args:
            name: Strategy name

        Returns:
            Strategy instance or None if not found
        """
        for strategy in self.strategies:
            if strategy.name == name:
                return strategy
        return None

    def add_strategy(self, strategy: BaseStrategy) -> None:
        """
        Add a new strategy to the selector.

        Args:
            strategy: Strategy to add
        """
        # Check for duplicate name
        if self.get_strategy_by_name(strategy.name):
            raise ValueError(f"Strategy with name '{strategy.name}' already exists")

        self.strategies.append(strategy)
        # Re-sort by priority
        self.strategies.sort(key=lambda s: s.priority)

        logger.info(f"Added strategy: {strategy.name} (priority {strategy.priority})")

    def remove_strategy(self, name: str) -> bool:
        """
        Remove strategy by name.

        Args:
            name: Name of strategy to remove

        Returns:
            True if strategy was removed, False if not found
        """
        for i, strategy in enumerate(self.strategies):
            if strategy.name == name:
                removed_strategy = self.strategies.pop(i)
                logger.info(f"Removed strategy: {removed_strategy.name}")
                return True
        return False

    def get_strategy_names(self) -> List[str]:
        """Get list of all strategy names."""
        return [s.name for s in self.strategies]

    def __str__(self) -> str:
        """String representation of the selector."""
        strategy_names = ", ".join(self.get_strategy_names())
        return f"StrategySelector({self.mode} mode, strategies: {strategy_names})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"StrategySelector(mode='{self.mode}', strategies={len(self.strategies)})"
        )
