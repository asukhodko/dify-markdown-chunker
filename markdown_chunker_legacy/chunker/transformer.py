"""
Output transformer for converting ChunkingResult to different formats.

This module handles transformation of chunking results into various output
formats, extracted from core.py to improve modularity.
"""

from typing import List, Literal, Union

from .types import Chunk, ChunkingResult


class OutputTransformer:
    """
    Transforms ChunkingResult into different output formats.

    Supports:
    - List[Chunk]: Simple list of chunks (backward compatible)
    - ChunkingResult: Full result with metadata
    - dict: JSON-serializable dictionary format
    """

    @staticmethod
    def transform(
        result: ChunkingResult,
        include_analysis: bool,
        return_format: Literal["objects", "dict"],
    ) -> Union[List[Chunk], ChunkingResult, dict]:
        """
        Transform ChunkingResult to requested output format.

        Args:
            result: Full chunking result
            include_analysis: Whether to include analysis metadata
            return_format: Output format ("objects" or "dict")

        Returns:
            Transformed output based on parameters:
            - List[Chunk]: When include_analysis=False, return_format="objects"
            - ChunkingResult: When include_analysis=True, return_format="objects"
            - dict: When return_format="dict"
        """
        if return_format == "dict":
            return OutputTransformer._transform_to_dict(result, include_analysis)
        else:
            return OutputTransformer._transform_to_objects(result, include_analysis)

    @staticmethod
    def _transform_to_dict(result: ChunkingResult, include_analysis: bool) -> dict:
        """
        Transform to dictionary format.

        Args:
            result: Chunking result
            include_analysis: Whether to include full analysis

        Returns:
            Dictionary representation
        """
        result_dict = result.to_dict()

        if include_analysis:
            # Full dictionary with all metadata
            return result_dict
        else:
            # Simplified dictionary (backward compatible)
            return {
                "success": result.success,
                "chunks": result_dict["chunks"],
                "metadata": {
                    "strategy_used": result_dict["strategy_used"],
                    "processing_time": result_dict["processing_time"],
                    "fallback_used": result_dict["fallback_used"],
                    "fallback_level": result_dict["fallback_level"],
                    "statistics": result_dict["statistics"],
                },
                "errors": result_dict["errors"],
                "warnings": result_dict["warnings"],
            }

    @staticmethod
    def _transform_to_objects(
        result: ChunkingResult, include_analysis: bool
    ) -> Union[List[Chunk], ChunkingResult]:
        """
        Transform to Python objects format.

        Args:
            result: Chunking result
            include_analysis: Whether to include full analysis

        Returns:
            Either List[Chunk] or ChunkingResult
        """
        if include_analysis:
            # Full ChunkingResult object
            return result
        else:
            # Just the chunks list (backward compatible)
            return result.chunks
