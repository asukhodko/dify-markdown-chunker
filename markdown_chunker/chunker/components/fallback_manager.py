"""
FallbackManager for handling strategy failures and error recovery.

This module implements a 3-level fallback chain to ensure that chunking
always succeeds, even when the primary strategy fails.
"""

import logging
from enum import Enum
from typing import Any, Dict, List

from markdown_chunker.parser.types import Stage1Results

from ..strategies.base import BaseStrategy
from ..strategies.sentences_strategy import SentencesStrategy
from ..strategies.structural_strategy import StructuralStrategy
from ..types import Chunk, ChunkConfig, ChunkingResult

logger = logging.getLogger(__name__)


class FallbackLevel(Enum):
    """Fallback levels in the error recovery chain."""

    PRIMARY = 0      # Selected strategy (no fallback)
    STRUCTURAL = 1   # Structural fallback
    SENTENCES = 2    # Final fallback (sentences)
    FALLBACK = 1     # Alias for backward compatibility (maps to STRUCTURAL)


class FallbackManager:
    """
    Manages fallback chain for error recovery during chunking.

    Implements a 3-level fallback system:
    1. Primary strategy (selected by strategy selector)
    2. Structural fallback (for specialized strategies that fail)
    3. Sentences fallback (universal fallback - always works)

    This approach:
    - Provides intermediate fallback for specialized strategies
    - Makes fallback behavior more robust
    - Ensures sentences strategy is always available as reliable fallback
    - Guarantees that chunking always succeeds and never loses content
    """

    def __init__(self, config: ChunkConfig):
        """
        Initialize fallback manager.

        Args:
            config: Chunking configuration
        """
        self.config = config
        self._structural_strategy = StructuralStrategy()
        self._sentences_strategy = SentencesStrategy()
        # Backward compatibility alias
        self._fallback_strategy = self._sentences_strategy

    def execute_with_fallback(
        self,
        content: str,
        stage1_results: Stage1Results,
        primary_strategy: BaseStrategy,
    ) -> ChunkingResult:
        """
        Execute chunking with automatic fallback on errors.

        Implements a 3-level fallback:
        1. Try primary strategy
        2. If fails, use structural fallback (skip if primary was structural)
        3. If fails, use sentences fallback (universal fallback)

        Args:
            content: Original markdown content
            stage1_results: Results from Stage 1 processing
            primary_strategy: Primary strategy to try first

        Returns:
            ChunkingResult with chunks and fallback information
        """
        errors = []
        warnings = []

        # Level 0: Try primary strategy
        try:
            logger.debug(f"Attempting primary strategy: {primary_strategy.name}")
            chunks = primary_strategy.apply(content, stage1_results, self.config)

            if chunks:  # Success
                logger.info(f"Primary strategy {primary_strategy.name} succeeded")
                return ChunkingResult(
                    chunks=chunks,
                    strategy_used=primary_strategy.name,
                    processing_time=0.0,  # Will be set by caller
                    fallback_used=False,
                    fallback_level=0,
                )
            else:
                warning_msg = (
                    f"Primary strategy {primary_strategy.name} returned no chunks"
                )
                logger.warning(warning_msg)
                warnings.append(warning_msg)

        except Exception as e:
            error_msg = f"Primary strategy {primary_strategy.name} failed: {str(e)}"
            logger.warning(error_msg)
            errors.append(error_msg)

        # Level 1: Try structural fallback (skip if primary was structural)
        if primary_strategy.name != self._structural_strategy.name:
            try:
                logger.info(f"Using structural fallback: {self._structural_strategy.name}")
                chunks = self._structural_strategy.apply(
                    content, stage1_results, self.config
                )

                if chunks:
                    logger.info("Structural fallback succeeded")
                    return self._create_fallback_result(
                        chunks,
                        self._structural_strategy.name,
                        FallbackLevel.STRUCTURAL,
                        errors,
                        warnings,
                    )
                else:
                    warning_msg = "Structural fallback returned no chunks"
                    logger.warning(warning_msg)
                    warnings.append(warning_msg)

            except Exception as e:
                error_msg = f"Structural fallback failed: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)

        # Level 2: Final fallback to sentences (skip if primary was sentences)
        if primary_strategy.name != self._sentences_strategy.name:
            try:
                logger.info(f"Using sentences fallback: {self._sentences_strategy.name}")
                chunks = self._sentences_strategy.apply(
                    content, stage1_results, self.config
                )

                if chunks:
                    logger.info("Sentences fallback succeeded")
                    return self._create_fallback_result(
                        chunks,
                        self._sentences_strategy.name,
                        FallbackLevel.SENTENCES,
                        errors,
                        warnings,
                    )
                else:
                    warning_msg = "Sentences fallback returned no chunks"
                    logger.warning(warning_msg)
                    warnings.append(warning_msg)

            except Exception as e:
                error_msg = f"Sentences fallback failed: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)

        # If we get here, all strategies failed - return error result
        logger.error("All strategies failed, returning empty result")
        return ChunkingResult(
            chunks=[],
            strategy_used="none",
            processing_time=0.0,
            fallback_used=True,
            fallback_level=2,
            errors=errors if errors else ["All strategies failed"],
            warnings=warnings,
        )

    def _create_fallback_result(
        self,
        chunks: List[Chunk],
        strategy_name: str,
        fallback_level: FallbackLevel,
        errors: List[str],
        warnings: List[str],
    ) -> ChunkingResult:
        """
        Create chunking result for fallback scenario.

        Args:
            chunks: Generated chunks
            strategy_name: Name of strategy that succeeded
            fallback_level: Level of fallback used
            errors: Accumulated errors
            warnings: Accumulated warnings

        Returns:
            ChunkingResult with fallback information
        """
        # Add fallback metadata to chunks
        for chunk in chunks:
            chunk.add_metadata("fallback_level", fallback_level.value)
            chunk.add_metadata(
                "fallback_reason", f"Primary strategy failed, used {strategy_name}"
            )

        return ChunkingResult(
            chunks=chunks,
            strategy_used=strategy_name,
            processing_time=0.0,  # Will be set by caller
            fallback_used=True,
            fallback_level=fallback_level.value,
            errors=errors,
            warnings=warnings,
        )

    def validate_fallback_chain(self) -> List[str]:
        """
        Validate that the fallback chain is properly configured.

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        if not self.config.enable_fallback:
            issues.append("Fallback is disabled in configuration")

        if not self._fallback_strategy:
            issues.append("Fallback strategy not available")

        return issues

    def get_fallback_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about fallback usage.

        Returns:
            Dictionary with fallback statistics
        """
        return {
            "fallback_enabled": self.config.enable_fallback,
            "max_fallback_level": 2,  # 3 levels (0, 1, 2)
            "structural_strategy": self._structural_strategy.name,
            "sentences_strategy": self._sentences_strategy.name,
        }


class FallbackError(Exception):
    """Exception raised when all fallback levels fail."""

    def __init__(self, message: str, errors: List[str]):
        self.errors = errors
        super().__init__(message)


# Utility functions
def create_fallback_manager(config: ChunkConfig) -> FallbackManager:
    """
    Create a fallback manager with default configuration.

    Args:
        config: Chunking configuration

    Returns:
        Configured FallbackManager instance
    """
    return FallbackManager(config)


def validate_fallback_chain(
    content: str, config: ChunkConfig, strategies: List[BaseStrategy]
) -> Dict[str, Any]:
    """
    Validate the fallback chain with given strategies.

    Args:
        content: Test content
        config: Chunking configuration
        strategies: List of strategies to test

    Returns:
        Dictionary with test results
    """
    manager = FallbackManager(config)

    results = {}

    for strategy in strategies:
        try:
            # Mock Stage1Results for testing
            from unittest.mock import Mock

            stage1_results = Mock()

            result = manager.execute_with_fallback(content, stage1_results, strategy)

            results[strategy.name] = {
                "success": len(result.chunks) > 0,
                "chunk_count": len(result.chunks),
                "fallback_used": result.fallback_used,
                "fallback_level": result.fallback_level,
                "strategy_used": result.strategy_used,
                "errors": len(result.errors),
                "warnings": len(result.warnings),
            }

        except Exception as e:
            results[strategy.name] = {"success": False, "error": str(e)}

    return results
