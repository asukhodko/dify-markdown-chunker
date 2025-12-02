"""Quality metrics for chunking evaluation.

This module defines metrics to measure chunking quality for the
block-based chunking improvements (MC-001 through MC-006).
"""

import re
import statistics
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class QualityMetrics:
    """Container for all quality metrics."""

    # MC-001: Section completeness
    section_completeness_rate: float

    # MC-002: Structural element integrity
    structural_element_integrity: float

    # MC-003: Overlap block integrity
    overlap_block_integrity: float

    # MC-004: Chunk size distribution
    chunk_size_cv: float  # Coefficient of variation

    # MC-005: URL pool preservation
    url_pool_preservation: float

    # MC-006: Header path completeness
    header_path_completeness: float

    # Additional metrics
    avg_chunk_size: float
    min_chunk_size: int
    max_chunk_size: int
    total_chunks: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "section_completeness_rate": self.section_completeness_rate,
            "structural_element_integrity": self.structural_element_integrity,
            "overlap_block_integrity": self.overlap_block_integrity,
            "chunk_size_cv": self.chunk_size_cv,
            "url_pool_preservation": self.url_pool_preservation,
            "header_path_completeness": self.header_path_completeness,
            "avg_chunk_size": self.avg_chunk_size,
            "min_chunk_size": self.min_chunk_size,
            "max_chunk_size": self.max_chunk_size,
            "total_chunks": self.total_chunks,
        }

    def meets_targets(self) -> bool:
        """Check if metrics meet target thresholds."""
        return (
            self.section_completeness_rate >= 0.80
            and self.structural_element_integrity >= 0.95
            and self.overlap_block_integrity >= 0.90
            and self.chunk_size_cv < 0.5
            and self.url_pool_preservation >= 0.95
            and self.header_path_completeness >= 1.0
        )


class MetricsCalculator:
    """Calculate quality metrics from chunks."""

    def __init__(self, max_chunk_size: int = 1000):
        """Initialize calculator.

        Args:
            max_chunk_size: Configured maximum chunk size
        """
        self.max_chunk_size = max_chunk_size

    def calculate_metrics(
        self, chunks: List[Any], original_content: str
    ) -> QualityMetrics:
        """Calculate all quality metrics.

        Args:
            chunks: List of chunk objects or dicts
            original_content: Original markdown content

        Returns:
            QualityMetrics object with all calculated metrics
        """
        # Extract chunk data
        chunk_data = [self._extract_chunk_data(c) for c in chunks]

        # Calculate each metric
        section_completeness = self._calc_section_completeness(chunk_data)
        structural_integrity = self._calc_structural_integrity(chunk_data)
        overlap_integrity = self._calc_overlap_integrity(chunk_data)
        size_cv = self._calc_size_cv(chunk_data)
        url_preservation = self._calc_url_pool_preservation(
            chunk_data, original_content
        )
        path_completeness = self._calc_header_path_completeness(chunk_data)

        # Calculate size statistics
        sizes = [cd["size"] for cd in chunk_data]
        avg_size = statistics.mean(sizes) if sizes else 0
        min_size = min(sizes) if sizes else 0
        max_size = max(sizes) if sizes else 0

        return QualityMetrics(
            section_completeness_rate=section_completeness,
            structural_element_integrity=structural_integrity,
            overlap_block_integrity=overlap_integrity,
            chunk_size_cv=size_cv,
            url_pool_preservation=url_preservation,
            header_path_completeness=path_completeness,
            avg_chunk_size=avg_size,
            min_chunk_size=min_size,
            max_chunk_size=max_size,
            total_chunks=len(chunks),
        )

    def _extract_chunk_data(self, chunk: Any) -> Dict[str, Any]:
        """Extract data from chunk object or dict."""
        if isinstance(chunk, dict):
            content = chunk.get("content", "")
            metadata = chunk.get("metadata", {})
        else:
            content = getattr(chunk, "content", "")
            metadata = getattr(chunk, "metadata", {})

        return {"content": content, "metadata": metadata, "size": len(content)}

    def _calc_section_completeness(self, chunk_data: List[Dict]) -> float:
        """Calculate section completeness rate (MC-001).

        Measures % of H2 sections that remain intact when size permits.
        A section is complete if size <= max * 1.2 and not split.
        """
        # Group chunks by section_path
        sections = {}
        for cd in chunk_data:
            section_path = cd["metadata"].get("section_path", [])
            if not section_path or len(section_path) < 2:
                continue

            # Use H2 level (second element in path)
            h2_section = tuple(section_path[:2])
            if h2_section not in sections:
                sections[h2_section] = []
            sections[h2_section].append(cd)

        if not sections:
            return 1.0  # No sections to evaluate

        # Check each section
        complete_count = 0
        for section_chunks in sections.values():
            total_size = sum(cd["size"] for cd in section_chunks)
            is_single_chunk = len(section_chunks) == 1
            size_permits = total_size <= self.max_chunk_size * 1.2

            if is_single_chunk or not size_permits:
                complete_count += 1

        return complete_count / len(sections)

    def _calc_structural_integrity(self, chunk_data: List[Dict]) -> float:
        """Calculate structural element integrity (MC-002).

        Measures % of structural elements (lists, tables, code) that don't
        split mid-element.
        """
        total_elements = 0
        intact_elements = 0

        # Patterns for structural elements
        list_start = re.compile(r"^\s*[-*+]\s+|\d+\.\s+", re.MULTILINE)
        table_row = re.compile(r"^\s*\|", re.MULTILINE)
        code_fence = re.compile(r"^```", re.MULTILINE)

        for cd in chunk_data:
            content = cd["content"]

            # Check for incomplete lists (starts with list but doesn't end with one)
            list_matches = list_start.findall(content)
            if list_matches:
                total_elements += 1
                # Consider intact if ends with list item or blank line
                if content.rstrip().endswith(("\n", "-", "*", "+", ".")):
                    intact_elements += 1

            # Check for incomplete tables
            table_matches = table_row.findall(content)
            if table_matches:
                total_elements += 1
                lines = content.strip().split("\n")
                # Table intact if last line is table row or separator
                if lines and (lines[-1].strip().startswith("|") or "---" in lines[-1]):
                    intact_elements += 1

            # Check for incomplete code blocks
            code_fences = code_fence.findall(content)
            if code_fences:
                total_elements += 1
                # Code block intact if even number of fences
                if len(code_fences) % 2 == 0:
                    intact_elements += 1

        if total_elements == 0:
            return 1.0  # No structural elements

        return intact_elements / total_elements

    def _calc_overlap_integrity(self, chunk_data: List[Dict]) -> float:
        """Calculate overlap block integrity (MC-003).

        Measures % of overlaps that contain only complete blocks
        (no mid-block splits).
        """
        overlap_count = 0
        block_intact_count = 0

        for cd in chunk_data:
            has_overlap = cd["metadata"].get("has_overlap", False)
            if not has_overlap:
                continue

            overlap_count += 1

            # Check if overlap metadata indicates block-based overlap
            # For now, assume integrity if overlap exists without mid-sentence splits
            overlap_size = cd["metadata"].get("overlap_size", 0)
            if overlap_size > 0:
                # Heuristic: Check if content starts mid-sentence
                content = cd["content"].lstrip()
                if content and content[0].isupper():
                    block_intact_count += 1

        if overlap_count == 0:
            return 1.0  # No overlaps to check

        return block_intact_count / overlap_count

    def _calc_size_cv(self, chunk_data: List[Dict]) -> float:
        """Calculate chunk size coefficient of variation (MC-004).

        Measures size distribution stability.
        CV = StdDev / Mean
        """
        sizes = [cd["size"] for cd in chunk_data]
        if len(sizes) < 2:
            return 0.0

        mean = statistics.mean(sizes)
        if mean == 0:
            return 0.0

        stdev = statistics.stdev(sizes)
        return stdev / mean

    def _calc_url_pool_preservation(
        self, chunk_data: List[Dict], original_content: str
    ) -> float:
        """Calculate URL pool preservation rate (MC-005).

        Measures % of URL pool blocks (3+ consecutive URLs) that remain intact.
        """
        # Find URL pools in original content
        url_pattern = re.compile(r"https?://[^\s]+")
        lines = original_content.split("\n")

        url_pools = []
        current_pool = []
        for i, line in enumerate(lines):
            if url_pattern.search(line):
                current_pool.append(i)
            else:
                if len(current_pool) >= 3:
                    url_pools.append(current_pool)
                current_pool = []

        if len(current_pool) >= 3:
            url_pools.append(current_pool)

        if not url_pools:
            return 1.0  # No URL pools to preserve

        # Check if each pool appears intact in a single chunk
        preserved_count = 0
        for pool in url_pools:
            pool_lines = [lines[i] for i in pool]
            pool_text = "\n".join(pool_lines)

            # Check if any chunk contains entire pool
            for cd in chunk_data:
                if pool_text in cd["content"]:
                    preserved_count += 1
                    break

        return preserved_count / len(url_pools)

    def _calc_header_path_completeness(self, chunk_data: List[Dict]) -> float:
        """Calculate header path completeness (MC-006).

        Measures % of chunks with complete hierarchical paths (no missing levels).
        """
        complete_count = 0

        for cd in chunk_data:
            section_path = cd["metadata"].get("section_path", [])
            header_path = cd["metadata"].get("header_path", "")

            # Check if path exists
            if not section_path and not header_path:
                # Preamble or special case - check for is_preamble flag
                if cd["metadata"].get("is_preamble", False):
                    complete_count += 1
                continue

            # Check for complete path (no None or empty strings)
            if section_path and all(p for p in section_path):
                complete_count += 1

        if not chunk_data:
            return 1.0

        return complete_count / len(chunk_data)
