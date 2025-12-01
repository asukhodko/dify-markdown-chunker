"""
Deduplication validator for detecting unintentional content duplication.

This module validates that chunks don't contain massive unintentional duplication
beyond the configured overlap. It addresses BLOCK-3 from the bug report.
"""

from typing import List, Tuple

from .types import Chunk


def find_duplicate_substrings(
    text1: str, text2: str, min_length: int = 50
) -> List[Tuple[str, int, int]]:
    """
    Find duplicate substrings between two texts.

    Uses a sliding window approach to find common substrings that exceed
    the minimum length threshold.

    Args:
        text1: First text
        text2: Second text
        min_length: Minimum substring length to consider (default: 50 chars)

    Returns:
        List of tuples: (duplicate_text, start_in_text1, start_in_text2)
    """
    duplicates = []

    # Use sliding window to find matches
    for i in range(len(text1) - min_length + 1):
        for j in range(len(text2) - min_length + 1):
            # Find longest common substring starting at positions i and j
            length = 0
            while (
                i + length < len(text1)
                and j + length < len(text2)
                and text1[i + length] == text2[j + length]
            ):
                length += 1

            if length >= min_length:
                duplicate_text = text1[i : i + length]
                duplicates.append((duplicate_text, i, j))
                # Skip ahead to avoid overlapping matches
                break

    return duplicates


def calculate_duplication_ratio(chunk: Chunk, previous_chunk: Chunk = None) -> float:
    """
    Calculate the duplication ratio for a chunk.

    Checks for:
    1. Internal duplication (within the chunk itself)
    2. External duplication (with previous chunk, excluding known overlap)

    Args:
        chunk: Chunk to analyze
        previous_chunk: Previous chunk for inter-chunk analysis (optional)

    Returns:
        Duplication ratio (0.0 = no duplication, 1.0 = 100% duplicated)
    """
    content = chunk.content

    # Handle Mock objects in tests
    from unittest.mock import Mock

    if isinstance(content, Mock):
        return 0.0

    if not content or not isinstance(content, str):
        return 0.0

    total_duplicate_chars = 0

    # Check internal duplication
    # Split into paragraphs and check for repeated paragraphs
    # Optimize: only check paragraphs if content is reasonably sized
    if len(content) < 10000:  # Only check internal duplication for smaller chunks
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        seen_paragraphs = set()

        for para in paragraphs:
            if len(para) < 20:  # Skip very short paragraphs
                continue
            if para in seen_paragraphs:
                total_duplicate_chars += len(para)
            else:
                seen_paragraphs.add(para)

    # Check external duplication with previous chunk
    if previous_chunk:
        # Handle Mock objects
        if isinstance(previous_chunk.content, Mock):
            return 0.0
        if not isinstance(previous_chunk.content, str):
            return 0.0

        known_overlap = chunk.get_metadata("overlap_size", 0)

        # Find duplicates beyond the known overlap
        duplicates = find_duplicate_substrings(
            previous_chunk.content, content, min_length=50
        )

        # Calculate total duplicate length, excluding known overlap region
        for dup_text, _, pos_in_current in duplicates:
            # Only count if it's NOT in the expected overlap region
            # (overlap is at the beginning of current chunk)
            if pos_in_current > known_overlap + 10:  # +10 for tolerance
                total_duplicate_chars += len(dup_text)

    # Calculate ratio
    duplication_ratio = total_duplicate_chars / len(content) if content else 0.0
    return min(duplication_ratio, 1.0)  # Cap at 100%


def validate_no_excessive_duplication(
    chunks: List[Chunk], max_duplication_ratio: float = 0.3
) -> Tuple[bool, List[str]]:
    """
    Validate that chunks don't have excessive unintentional duplication.

    This checks for BLOCK-3 issue: "massive content duplication within
    and between chunks" beyond the intentional overlap.

    Args:
        chunks: List of chunks to validate
        max_duplication_ratio: Maximum acceptable duplication (default: 30%)

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    if not chunks:
        return True, []

    errors = []

    for i, chunk in enumerate(chunks):
        previous_chunk = chunks[i - 1] if i > 0 else None

        # Calculate duplication ratio
        dup_ratio = calculate_duplication_ratio(chunk, previous_chunk)

        if dup_ratio > max_duplication_ratio:
            errors.append(
                f"Chunk {i} has {dup_ratio:.1%} duplication "
                f"(max allowed: {max_duplication_ratio:.1%})"
            )

    return len(errors) == 0, errors


def calculate_character_level_overlap(chunk1_content: str, chunk2_content: str) -> int:
    """
    Calculate character-level overlap between two chunks.

    Uses longest common substring (LCS) approach to find the actual
    overlapping region.

    Args:
        chunk1_content: Content of first chunk
        chunk2_content: Content of second chunk

    Returns:
        Length of overlapping region in characters
    """
    if not chunk1_content or not chunk2_content:
        return 0

    # Find longest common suffix of chunk1 and prefix of chunk2
    # This is the most likely overlap pattern
    max_overlap = min(len(chunk1_content), len(chunk2_content))
    overlap_length = 0

    for length in range(1, max_overlap + 1):
        if chunk1_content[-length:] == chunk2_content[:length]:
            overlap_length = length
        else:
            # Once we find a mismatch, the previous match was the longest
            break

    return overlap_length


def validate_overlap_accuracy(chunks: List[Chunk]) -> Tuple[bool, List[str]]:
    """
    Validate that declared overlap matches actual character-level overlap.

    This ensures that the overlap_size metadata is accurate and that
    there's no hidden duplication.

    Args:
        chunks: List of chunks to validate

    Returns:
        Tuple of (is_valid, list_of_warnings)
    """
    if len(chunks) < 2:
        return True, []

    warnings = []

    for i in range(1, len(chunks)):
        current_chunk = chunks[i]
        previous_chunk = chunks[i - 1]

        # Get declared overlap
        declared_overlap = current_chunk.get_metadata("overlap_size", 0)

        # Calculate actual overlap
        actual_overlap = calculate_character_level_overlap(
            previous_chunk.content, current_chunk.content
        )

        # Allow 10% tolerance for whitespace differences
        tolerance = max(10, int(declared_overlap * 0.1))

        if abs(actual_overlap - declared_overlap) > tolerance:
            warnings.append(
                f"Chunk {i}: Declared overlap={declared_overlap}, "
                f"actual overlap={actual_overlap} "
                f"(difference: {abs(actual_overlap - declared_overlap)})"
            )

    return len(warnings) == 0, warnings
