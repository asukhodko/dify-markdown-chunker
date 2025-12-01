"""
Main MarkdownChunker class for Stage 2.

This module provides the primary interface for chunking Markdown documents
using adaptive strategies based on content analysis.

Algorithm Documentation:
    - Main Pipeline: docs/markdown-extractor/02-algorithm-core/pipeline.md
    - Extractor (Orchestrator): docs/markdown-extractor/01-overview/architecture.md
    - Chunking Process: docs/markdown-extractor/02-algorithm-core/chunk-creation.md
"""

import logging
import warnings
from typing import List, Literal, Optional, Union

from markdown_chunker.parser import ParserInterface

from .components import FallbackManager, MetadataEnricher, OverlapManager
from .errors import ChunkingError
from .orchestrator import ChunkingOrchestrator
from .performance import PerformanceOptimizer
from .selector import StrategySelectionError, StrategySelector
from .strategies import (
    CodeStrategy,
    ListStrategy,
    MixedStrategy,
    SentencesStrategy,
    StructuralStrategy,
    TableStrategy,
)
from .strategies.base import BaseStrategy
from .transformer import OutputTransformer
from .types import Chunk, ChunkConfig, ChunkingResult
from .validator import DataCompletenessValidator

# Initialize logger for this module
logger = logging.getLogger(__name__)


class MarkdownChunker:
    """
    Main interface for Stage 2 chunking operations.

    This class orchestrates the entire chunking process:
    1. Uses Stage 1 for content analysis and element detection
    2. Selects optimal chunking strategy based on content
    3. Applies strategy to create semantically meaningful chunks
    4. Adds overlap and enriches metadata
    5. Handles errors with fallback strategies

    Usage:
        chunker=MarkdownChunker()
        chunks=chunker.chunk(markdown_text)

        # Or with custom configuration
        config=ChunkConfig.for_code_heavy()
        chunker=MarkdownChunker(config)
        result=chunker.chunk_with_analysis(markdown_text)
    """

    def __init__(
        self,
        config: Optional[ChunkConfig] = None,
        enable_performance_monitoring: bool = False,
    ):
        """
        Initialize MarkdownChunker with configuration.

        Creates a new chunker instance with the specified configuration.
        The chunker automatically initializes all necessary components:
        parser, strategies, fallback manager, and performance optimizer.

        Args:
            config: Configuration for chunking behavior. If None, uses default
                configuration with max_chunk_size=4096, min_chunk_size=512,
                enable_overlap=True. See ChunkConfig for all options.
            enable_performance_monitoring: Enable performance monitoring and
                optimization. When True, tracks timing metrics for all operations.
                Defaults to False for minimal overhead.

        Examples:
            >>> # Basic usage with defaults
            >>> chunker=MarkdownChunker()
            >>> chunks=chunker.chunk("# Hello\nWorld")

            >>> # Custom configuration
            >>> from markdown_chunker import ChunkConfig
            >>> config=ChunkConfig(
            ...     max_chunk_size=2048,
            ...     min_chunk_size=256,
            ...     enable_overlap=True
            ... )
            >>> chunker=MarkdownChunker(config)
            >>> result=chunker.chunk("# Test", include_analysis=True)

            >>> # Using configuration profiles
            >>> config=ChunkConfig.for_code_heavy()
            >>> chunker=MarkdownChunker(config)
            >>> chunks=chunker.chunk(code_document)

            >>> # With performance monitoring
            >>> chunker=MarkdownChunker(enable_performance_monitoring=True)
            >>> chunks=chunker.chunk("# Test")
            >>> stats=chunker.get_performance_stats()
            >>> print(stats['chunk']['avg_time'])

        See Also:
            - ChunkConfig: Configuration options and factory methods
            - chunk(): Main method for processing markdown
            - get_performance_stats(): Get performance metrics

        Notes:
            - The chunker is thread-safe for read operations
            - Strategies are initialized once and reused
            - Performance optimizer tracks metrics automatically when enabled
            - All 6 strategies are loaded at initialization
        """
        self.config = config or ChunkConfig.default()
        self.stage1 = ParserInterface()

        # Initialize performance optimizer
        self._performance_optimizer = PerformanceOptimizer()
        self._performance_optimizer.monitor.enabled = enable_performance_monitoring
        self._performance_monitor = self._performance_optimizer.monitor

        # Initialize all strategies (lazy loading via cache)
        self._strategies: List[BaseStrategy] = [
            CodeStrategy(),
            MixedStrategy(),
            ListStrategy(),
            TableStrategy(),
            StructuralStrategy(),
            SentencesStrategy(),
        ]

        # Initialize components
        self._strategy_selector = StrategySelector(self._strategies, mode="strict")
        self._overlap_manager = OverlapManager(self.config)
        self._metadata_enricher = MetadataEnricher(self.config)
        self._fallback_manager = FallbackManager(self.config)
        self._validator = DataCompletenessValidator(tolerance=0.05)

        # Initialize orchestrator
        self._orchestrator = ChunkingOrchestrator(
            config=self.config,
            strategy_selector=self._strategy_selector,
            fallback_manager=self._fallback_manager,
            parser=self.stage1,
        )

        # Initialize transformer
        self._transformer = OutputTransformer()

    def chunk(
        self,
        md_text: str,
        strategy: Optional[str] = None,
        include_analysis: bool = False,
        return_format: Literal["objects", "dict"] = "objects",
    ) -> Union[List[Chunk], ChunkingResult, dict]:
        """
        Unified chunking method supporting multiple return formats.

        This is the primary method for chunking markdown documents. It automatically
        selects the optimal chunking strategy based on content analysis, or uses
        a specified strategy if provided.

        Args:
            md_text: Markdown content to process. Must be valid UTF-8 text.
            strategy: Optional strategy override. Valid values:
                - None: Auto-select based on content (default)
                - "code": For code-heavy documents (≥70% code)
                - "mixed": For mixed content with diverse elements
                - "list": For list-heavy documents (≥5 lists)
                - "table": For table-heavy documents (≥3 tables)
                - "structural": For well-structured documents with headers
                - "sentences": For simple text documents
            include_analysis: Include detailed analysis metadata in result.
                - False: Returns List[Chunk] (default, backward compatible)
                - True: Returns ChunkingResult with full metadata
            return_format: Output format for the result.
                - "objects": Return Python objects (Chunk/ChunkingResult)
                - "dict": Return dictionary representation (JSON-serializable)

        Returns:
            The return type depends on parameters:
            - List[Chunk]: When include_analysis=False, return_format="objects" (default)  # noqa: E501
            - ChunkingResult: When include_analysis=True, return_format="objects"
            - dict: When return_format="dict" (regardless of include_analysis)

        Raises:
            ValueError: If md_text is empty or invalid
            StrategySelectionError: If specified strategy is not found
            ChunkingError: If chunking fails completely

        Examples:
            >>> # Basic usage (backward compatible)
            >>> chunker=MarkdownChunker()
            >>> chunks=chunker.chunk("# Hello\\n\\nWorld")
            >>> print(len(chunks))
            1
            >>> print(chunks[0].content)
            '# Hello\\n\\nWorld'

            >>> # With detailed analysis
            >>> result=chunker.chunk("# Hello\\n\\nWorld", include_analysis=True)
            >>> print(result.strategy_used)
            'structural'
            >>> print(result.processing_time)
            0.123
            >>> print(len(result.chunks))
            1

            >>> # As dictionary (for JSON APIs)
            >>> data=chunker.chunk("# Hello\\n\\nWorld", return_format="dict")
            >>> print(data['chunks'][0]['content'])
            '# Hello\\n\\nWorld'
            >>> print(data['strategy_used'])
            'structural'

            >>> # Force specific strategy
            >>> chunks=chunker.chunk(code_doc, strategy="code")
            >>> print(chunks[0].metadata['strategy'])
            'code'

            >>> # Combine parameters
            >>> data=chunker.chunk(
            ...     "# Test",
            ...     strategy="structural",
            ...     include_analysis=True,
            ...     return_format="dict"
            ... )
            >>> print(data['metadata']['strategy_used'])
            'structural'

        See Also:
            - chunk_with_analysis(): Deprecated, use chunk(include_analysis=True)
            - chunk_simple(): Deprecated, use chunk(return_format="dict")
            - ChunkConfig: Configuration options for chunking behavior

        Notes:
            - The method always performs full analysis internally for optimal results
            - Performance overhead of include_analysis=True is minimal (<5%)
            - Dictionary format is fully JSON-serializable
            - All chunks respect configured size limits (unless allow_oversize=True)
        """
        # Validate parameters
        self._validate_chunk_params(
            md_text=md_text,
            strategy=strategy,
            include_analysis=include_analysis,
            return_format=return_format,
        )

        # Get result from orchestrator
        result = self._orchestrator.chunk_with_strategy(md_text, strategy)

        # Apply post-processing (overlap, metadata, validation, preamble)
        result = self._post_process_chunks(result, md_text)

        # Transform output based on parameters
        return self._transformer.transform(result, include_analysis, return_format)

    def _post_process_chunks(  # noqa: C901
        self, result: ChunkingResult, md_text: str
    ) -> ChunkingResult:
        """
        Apply post-processing to chunks (overlap, metadata, validation, preamble).

        Args:
            result: Chunking result from orchestrator
            md_text: Original markdown text

        Returns:
            Updated ChunkingResult with post-processing applied
        """
        chunks = result.chunks

        # Stage 3: Apply overlap if enabled
        if self.config.enable_overlap and chunks:
            try:
                chunks = self._overlap_manager.apply_overlap(chunks)
            except Exception as e:
                result.errors.append(f"Overlap processing failed: {str(e)}")

        # Stage 4: Enrich metadata
        if chunks:
            try:
                # Pass fallback information to metadata enricher
                fallback_metadata = {
                    "fallback_used": result.fallback_used,
                    "fallback_level": result.fallback_level,
                    "strategy_used": result.strategy_used,
                }
                chunks = self._metadata_enricher.enrich_chunks(
                    chunks, fallback_info=fallback_metadata
                )
            except Exception as e:
                result.errors.append(f"Metadata enrichment failed: {str(e)}")

        # Stage 4.5: Validate data completeness
        if chunks:
            try:
                validation_result = self._validator.validate_chunks(md_text, chunks)

                # Add validation warnings to result
                if validation_result.warnings:
                    result.warnings.extend(validation_result.warnings)

                # Log validation results
                if not validation_result.is_valid:
                    summary = validation_result.get_summary()
                    logger.warning(f"Data completeness validation failed: {summary}")
                    # Add validation info to warnings but don't fail
                    coverage = validation_result.char_coverage
                    result.warnings.append(
                        f"Data completeness check: {coverage:.1%} coverage"
                    )
                else:
                    summary = validation_result.get_summary()
                    logger.debug(f"Data completeness validation passed: {summary}")
            except Exception as e:
                # Don't fail chunking if validation fails
                logger.error(f"Data completeness validation error: {str(e)}")
                result.warnings.append(f"Validation error: {str(e)}")

        # Stage 5: Process preamble (if available from Stage 1)
        # Note: We need to get preamble from Stage 1 results
        # We'll need to pass stage1_results through the orchestrator
        # For now, we'll re-run Stage 1 if preamble extraction is enabled
        if chunks and self.config.extract_preamble:
            try:
                stage1_results = self.stage1.process_document(md_text)
                if stage1_results.analysis.preamble:
                    chunks = self._process_preamble(
                        chunks, stage1_results.analysis.preamble
                    )
            except Exception as e:
                result.errors.append(f"Preamble processing failed: {str(e)}")

        # Update chunks in result
        result.chunks = chunks

        return result

    def _validate_chunk_params(
        self,
        md_text: str,
        strategy: Optional[str],
        include_analysis: bool,
        return_format: str,
    ) -> None:
        """
        Validate chunk() method parameters.

        Args:
            md_text: Markdown content
            strategy: Strategy name
            include_analysis: Analysis flag
            return_format: Return format

        Raises:
            ValueError: If parameters are invalid
            TypeError: If parameters have wrong type
        """
        # Validate md_text
        if not isinstance(md_text, str):
            raise TypeError(f"md_text must be a string, got {type(md_text).__name__}")
        # Note: We allow empty/whitespace content for backward compatibility
        # It will return empty chunks list

        # Validate strategy
        if strategy is not None:
            if not isinstance(strategy, str):
                raise TypeError(
                    f"strategy must be a string or None, got {type(strategy).__name__}"
                )
            if strategy == "":
                raise StrategySelectionError(
                    "strategy cannot be empty. "
                    f"Available strategies: {self.get_available_strategies()}"
                )
            valid_strategies = self.get_available_strategies()
            if strategy not in valid_strategies:
                raise StrategySelectionError(
                    f"Invalid strategy '{strategy}'. "
                    f"Available strategies: {valid_strategies}"
                )

        # Validate include_analysis
        if not isinstance(include_analysis, bool):
            raise TypeError(
                f"include_analysis must be a boolean, "
                f"got {type(include_analysis).__name__}"
            )

        # Validate return_format
        if not isinstance(return_format, str):
            raise TypeError(
                f"return_format must be a string, got {type(return_format).__name__}"
            )
        valid_formats = ["objects", "dict"]
        if return_format not in valid_formats:
            raise ValueError(
                f"Invalid return_format '{return_format}'. "
                f"Valid formats: {valid_formats}"
            )

    def chunk_with_analysis(
        self, md_text: str, strategy: Optional[str] = None
    ) -> ChunkingResult:
        """
                Chunk with detailed analysis information.

                .. deprecated:: 1.1.0
                    Use:meth:`chunk` with ``include_analysis=True`` instead.
                    This method will be removed in version 2.0.0.

                Args:
                    md_text: Markdown content to chunk
                    strategy: Optional strategy override

                Returns:
                    ChunkingResult with chunks, strategy used, analysis, etc.

                Raises:
                    ChunkingError: If chunking fails completely

                Examples:
                    >>> # Old way (deprecated)
                    >>> result=chunker.chunk_with_analysis("# Test")

                    >>> # New way (recommended)
                    >>> result=chunker.chunk("# Test", include_analysis=True)

                See Also:
        :meth:`chunk`: Unified chunking method
        """
        warnings.warn(
            "chunk_with_analysis() is deprecated and will be removed in version 2.0.0. "
            "Use chunk(include_analysis=True) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        result = self.chunk(md_text, strategy=strategy, include_analysis=True)
        return result  # type: ignore[return-value]

    def _get_strategy_by_name(self, name: str) -> Optional[BaseStrategy]:
        """
        Get strategy by name.

        Args:
            name: Strategy name

        Returns:
            Strategy instance or None if not found
        """
        for strategy in self._strategies:
            if strategy.name == name:
                return strategy
        return None

    def _process_preamble(self, chunks: List[Chunk], preamble) -> List[Chunk]:
        """
        Process preamble and add to chunks.

        Args:
            chunks: List of chunks
            preamble: PreambleInfo from analysis

        Returns:
            Updated list of chunks with preamble information
        """
        if not chunks or not preamble:
            return chunks

        # Add preamble to first chunk metadata (default behavior)
        if not self.config.separate_preamble_chunk:
            chunks[0].add_metadata("preamble", preamble.to_dict())
            chunks[0].add_metadata("has_preamble", True)
            chunks[0].add_metadata("preamble_type", preamble.type)
        else:
            # Create separate preamble chunk (optional behavior)
            preamble_chunk = Chunk(
                content=preamble.content,
                start_line=1,
                end_line=preamble.line_count,
                metadata={
                    "strategy": "preamble",
                    "content_type": "preamble",
                    "preamble_type": preamble.type,
                    "has_metadata": preamble.has_metadata,
                    "metadata_fields": preamble.metadata_fields,
                    "is_preamble_chunk": True,
                },
            )
            # Insert at beginning
            chunks.insert(0, preamble_chunk)

        return chunks

    def add_strategy(self, strategy: BaseStrategy) -> None:
        """
        Add a custom strategy to the chunker.

        Allows extending the chunker with custom chunking strategies.
        The new strategy will be available for automatic selection and
        manual override via the strategy parameter.

        Args:
            strategy: Custom strategy instance implementing BaseStrategy.
                Must have unique name and implement can_handle() and apply() methods.

        Examples:
            >>> from markdown_chunker.chunker.strategies.base import BaseStrategy
            >>>
            >>> class CustomStrategy(BaseStrategy):
            ...     def __init__(self):
            ...         super().__init__()
            ...         self.name="custom"
            ...         self.priority=50
            ...
            ...     def can_handle(self, analysis, config):
            ...         return analysis.complexity_score > 0.5
            ...
            ...     def apply(self, text, stage1_results, config):
            ...         # Custom chunking logic
            ...         return [Chunk(text, 1, 1, {})]
            >>>
            >>> chunker=MarkdownChunker()
            >>> chunker.add_strategy(CustomStrategy())
            >>> print("custom" in chunker.get_available_strategies())
            True
            >>> chunks=chunker.chunk(text, strategy="custom")

        See Also:
            - remove_strategy(): Remove a strategy
            - get_available_strategies(): List all strategies
            - BaseStrategy: Base class for custom strategies

        Notes:
            - Strategy selector is recreated after adding
            - Duplicate strategy names will override existing ones
            - Custom strategies participate in automatic selection
        """
        self._strategies.append(strategy)
        # Recreate selector with updated strategies
        current_mode = getattr(self._strategy_selector, "_mode", "strict")
        self._strategy_selector = StrategySelector(self._strategies, mode=current_mode)

        # Update orchestrator with new selector
        self._orchestrator._strategy_selector = self._strategy_selector

    def remove_strategy(self, strategy_name: str) -> None:
        """
        Remove a strategy from the chunker.

        Removes a strategy by name, making it unavailable for both
        automatic selection and manual override. Useful for disabling
        strategies that don't fit your use case.

        Args:
            strategy_name: Name of strategy to remove. Must match exactly
                one of the available strategy names (case-sensitive).

        Examples:
            >>> chunker=MarkdownChunker()
            >>> print(len(chunker.get_available_strategies()))
            6
            >>>
            >>> # Remove table strategy if you never process tables
            >>> chunker.remove_strategy("table")
            >>> print(len(chunker.get_available_strategies()))
            5
            >>> print("table" in chunker.get_available_strategies())
            False
            >>>
            >>> # Trying to use removed strategy will raise error
            >>> try:
            ...     chunker.chunk(text, strategy="table")
            ... except StrategySelectionError as e:
            ...     print("Strategy not found")

        See Also:
            - add_strategy(): Add a custom strategy
            - get_available_strategies(): List all strategies

        Notes:
            - Strategy selector is recreated after removal
            - Removing all strategies will cause chunking to fail
            - Built-in strategies can be removed but not restored
            - No error if strategy name doesn't exist
        """
        self._strategies = [s for s in self._strategies if s.name != strategy_name]

        # Recreate selector with updated strategies
        current_mode = getattr(self._strategy_selector, "_mode", "strict")
        self._strategy_selector = StrategySelector(self._strategies, mode=current_mode)

        # Update orchestrator with new selector
        self._orchestrator._strategy_selector = self._strategy_selector

    def get_available_strategies(self) -> List[str]:
        """
        Get list of available strategy names.

        Returns all strategy names that can be used with the chunk()
        method's strategy parameter. Includes both built-in and custom
        strategies.

        Returns:
            List of strategy names (strings) that can be passed to
            chunk(strategy=...). Default strategies: "code", "mixed",
            "list", "table", "structural", "sentences".

        Examples:
            >>> chunker=MarkdownChunker()
            >>> strategies=chunker.get_available_strategies()
            >>> print(strategies)
            ['code', 'mixed', 'list', 'table', 'structural', 'sentences']
            >>>
            >>> # Check if specific strategy is available
            >>> if "code" in chunker.get_available_strategies():
            ...     chunks=chunker.chunk(code_doc, strategy="code")
            >>>
            >>> # After adding custom strategy
            >>> chunker.add_strategy(CustomStrategy())
            >>> print("custom" in chunker.get_available_strategies())
            True

        See Also:
            - chunk(): Main chunking method that accepts strategy parameter
            - add_strategy(): Add custom strategies
            - remove_strategy(): Remove strategies

        Notes:
            - Order of strategies in list is not guaranteed
            - Strategy names are case-sensitive
            - Empty list means no strategies available (will cause errors)
        """
        return [strategy.name for strategy in self._strategies]

    def validate_config(self) -> List[str]:
        """
        Validate current configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        try:
            # Basic validation is done in ChunkConfig.__post_init__
            # Additional validation can be added here
            pass
        except ValueError as e:
            errors.append(str(e))

        return errors

    def get_performance_stats(self) -> dict:
        """
        Get performance statistics for all operations.

        Returns detailed timing metrics for chunking operations when
        performance monitoring is enabled. Useful for profiling and
        optimization.

        Returns:
            Dictionary with performance metrics including:
            - 'chunk': Stats for chunk() method (count, total_time, avg_time)
            - 'strategy_selection': Stats for strategy selection
            - 'overlap': Stats for overlap processing
            - 'metadata': Stats for metadata enrichment
            Each stat includes: count, total_time, avg_time, min_time, max_time

        Examples:
            >>> # Enable monitoring first
            >>> chunker=MarkdownChunker(enable_performance_monitoring=True)
            >>>
            >>> # Process some documents
            >>> for doc in documents:
            ...     chunker.chunk(doc)
            >>>
            >>> # Get statistics
            >>> stats=chunker.get_performance_stats()
            >>> print(f"Average chunk time: {stats['chunk']['avg_time']:.3f}s")
            >>> print(f"Total operations: {stats['chunk']['count']}")
            >>>
            >>> # Check for performance issues
            >>> if stats['chunk']['max_time'] > 1.0:
            ...     print("Warning: Slow chunking detected")

        See Also:
            - enable_performance_monitoring(): Enable monitoring
            - disable_performance_monitoring(): Disable monitoring
            - clear_caches(): Clear performance caches

        Notes:
            - Returns empty dict if monitoring is disabled
            - Stats are cumulative since chunker creation
            - Use clear_caches() to reset statistics
            - Minimal overhead when monitoring is enabled (<5%)
        """
        return self._performance_optimizer.monitor.get_all_stats()

    def clear_caches(self):
        """Clear all performance caches."""
        self._performance_optimizer.clear_all_caches()

    def enable_performance_monitoring(self):
        """Enable performance monitoring."""
        self._performance_optimizer.monitor.enabled = True

    def disable_performance_monitoring(self):
        """Disable performance monitoring."""
        self._performance_optimizer.monitor.enabled = False

    def chunk_simple(
        self,
        md_text: str,
        config: Optional[dict] = None,
        strategy: Optional[str] = None,
    ) -> dict:  # noqa: E501
        """
                      Simplified chunking interface that returns dictionaries instead of objects.

                      .. deprecated:: 1.1.0
                          Use:meth:`chunk` with ``return_format='dict'`` instead.
                          This method will be removed in version 2.0.0.

                      Args:
                          md_text: Markdown content to chunk
                          config: Optional configuration as dictionary
                          strategy: Optional strategy override

                      Returns:
                          Dictionary with chunks and metadata

                      Examples:
                          >>> # Old way (deprecated)
                          >>> result=chunker.chunk_simple("# Test")

                          >>> # New way (recommended)
                          >>> result=chunker.chunk("# Test", return_format="dict")
        # noqa: E501
                          >>> # With custom config (old way)
                          >>> result=chunker.chunk_simple("# Test", config={'max_chunk_size': 2048})

                          >>> # With custom config (new way)
                          >>> chunker=MarkdownChunker(ChunkConfig(max_chunk_size=2048))
                          >>> result=chunker.chunk("# Test", return_format="dict")

                      See Also:
              :meth:`chunk`: Unified chunking method
        """
        warnings.warn(
            "chunk_simple() is deprecated and will be removed in version 2.0.0. "
            "Use chunk(return_format='dict') instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Handle config parameter
        if config:
            chunk_config = ChunkConfig.from_dict(config)
            # Temporarily update config
            old_config = self.config
            self.config = chunk_config
            try:
                result = self.chunk(md_text, strategy=strategy, return_format="dict")
                return result  # type: ignore[return-value]
            finally:
                self.config = old_config
        else:
            result = self.chunk(md_text, strategy=strategy, return_format="dict")
            return result  # type: ignore[return-value]


class ConfigurationError(ChunkingError):
    """Exception raised for configuration errors."""
