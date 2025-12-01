"""
Size enforcement module for ensuring chunks respect max_chunk_size limits.

This module addresses CRIT-1: "chunks violating max_chunk_size"
for non-atomic blocks. Atomic blocks (code, tables) are allowed to be
oversize, but regular text should be split.
"""

import re
from typing import List

from .text_normalizer import truncate_at_word_boundary
from .types import Chunk, ChunkConfig


def is_atomic_content(content: str) -> bool:
    """
    Check if content is atomic (indivisible).

    Atomic content includes:
    - Code blocks (fenced with ```)
    - Tables (with | separators)
    - Single very long lines (likely formatted data)

    Args:
        content: Content to check

    Returns:
        True if content should not be split
    """
    # Check for code blocks
    if "```" in content:
        return True

    # Check for tables (multiple lines with pipes)
    lines_with_pipes = sum(1 for line in content.split("\n") if "|" in line)
    if lines_with_pipes >= 3:  # Likely a table
        return True

    # Check for single very long line (likely formatted data)
    # Only consider it atomic if it's VERY long and has no spaces (likely data)
    lines = [line for line in content.split("\n") if line.strip()]
    if len(lines) == 1 and len(lines[0]) > 1000:
        # Very long single line - check if it looks like data (low space ratio)
        space_ratio = lines[0].count(" ") / len(lines[0])
        if space_ratio < 0.1:  # Less than 10% spaces = likely data
            return True

    return False


def split_oversized_chunk(chunk: Chunk, config: ChunkConfig) -> List[Chunk]:
    """
    Split an oversized non-atomic chunk into multiple chunks.

    This function enforces hard size limits for chunks that exceed max_chunk_size
    but don't contain atomic elements. It splits at paragraph or sentence boundaries
    to maintain readability.

    Args:
        chunk: Oversized chunk to split
        config: Chunking configuration with max_chunk_size

    Returns:
        List of chunks (may be single chunk if atomic or within limits)
    """
    # If chunk is within limits, return as-is
    if len(chunk.content) <= config.max_chunk_size:
        return [chunk]

    # If chunk is atomic, mark as oversize and return
    if is_atomic_content(chunk.content):
        chunk.add_metadata("allow_oversize", True)
        chunk.add_metadata("oversize_reason", "atomic_content")
        return [chunk]

    # Split the chunk
    return _split_at_boundaries(chunk, config)


def _split_at_boundaries(chunk: Chunk, config: ChunkConfig) -> List[Chunk]:
    """
    Split chunk at paragraph or sentence boundaries.

    Tries to split at:
    1. Double newlines (paragraph breaks)
    2. Sentence boundaries (. ! ?)
    3. Word boundaries (as last resort)

    Args:
        chunk: Chunk to split
        config: Configuration with size limits

    Returns:
        List of smaller chunks
    """
    content = chunk.content
    max_size = config.max_chunk_size

    # Try splitting at paragraph boundaries first
    paragraphs = content.split("\n\n")

    if len(paragraphs) > 1:
        # We have multiple paragraphs
        sub_chunks: List[Chunk] = []
        current_parts: List[str] = []
        current_size = 0

        for para in paragraphs:
            para_size = len(para)

            # If single paragraph exceeds max, need to split it further
            if para_size > max_size:
                # Flush current parts first
                if current_parts:
                    sub_chunks.append(
                        _create_sub_chunk(
                            "\n\n".join(current_parts), chunk, len(sub_chunks)
                        )
                    )
                    current_parts = []
                    current_size = 0

                # Split this large paragraph
                split_para = _split_large_paragraph(
                    para, max_size, chunk, len(sub_chunks)
                )
                sub_chunks.extend(split_para)

            elif current_size + para_size + 2 <= max_size:  # +2 for \n\n
                current_parts.append(para)
                current_size += para_size + 2

            else:
                # Flush current parts
                if current_parts:
                    sub_chunks.append(
                        _create_sub_chunk(
                            "\n\n".join(current_parts), chunk, len(sub_chunks)
                        )
                    )

                # Start new chunk with this paragraph
                current_parts = [para]
                current_size = para_size

        # Flush remaining parts
        if current_parts:
            sub_chunks.append(
                _create_sub_chunk("\n\n".join(current_parts), chunk, len(sub_chunks))
            )

        return sub_chunks if sub_chunks else [chunk]

    else:
        # Single paragraph - split at sentence boundaries
        return _split_large_paragraph(content, max_size, chunk, 0)


def _split_large_paragraph(
    para: str, max_size: int, original_chunk: Chunk, start_index: int
) -> List[Chunk]:
    """
    Split a large paragraph at sentence boundaries.

    Args:
        para: Paragraph content
        max_size: Maximum size per chunk
        original_chunk: Original chunk for metadata
        start_index: Starting index for sub-chunks

    Returns:
        List of sub-chunks
    """
    # Split into sentences
    sentence_pattern = r"([.!?]+\s+)"
    parts = re.split(sentence_pattern, para)

    # Reconstruct sentences with their punctuation
    sentences = []
    i = 0
    while i < len(parts):
        if i + 1 < len(parts) and re.match(sentence_pattern, parts[i + 1]):
            sentences.append(parts[i] + parts[i + 1])
            i += 2
        else:
            if parts[i].strip():
                sentences.append(parts[i])
            i += 1

    if not sentences:
        # No sentence boundaries found - split at word boundaries
        return _split_at_word_boundaries(para, max_size, original_chunk, start_index)

    # Group sentences into chunks
    sub_chunks: List[Chunk] = []
    current_sentences: List[str] = []
    current_size = 0

    for sentence in sentences:
        sentence_size = len(sentence)

        if sentence_size > max_size:
            # Single sentence exceeds max - need to split it
            if current_sentences:
                sub_chunks.append(
                    _create_sub_chunk(
                        " ".join(current_sentences),
                        original_chunk,
                        start_index + len(sub_chunks),
                    )
                )
                current_sentences = []
                current_size = 0

            # Split at word boundary
            word_splits = _split_at_word_boundaries(
                sentence, max_size, original_chunk, start_index + len(sub_chunks)
            )
            sub_chunks.extend(word_splits)

        elif current_size + sentence_size + 1 <= max_size:  # +1 for space
            current_sentences.append(sentence.strip())
            current_size += sentence_size + 1

        else:
            # Flush current sentences
            if current_sentences:
                sub_chunks.append(
                    _create_sub_chunk(
                        " ".join(current_sentences),
                        original_chunk,
                        start_index + len(sub_chunks),
                    )
                )

            # Start new chunk with this sentence
            current_sentences = [sentence.strip()]
            current_size = sentence_size

    # Flush remaining sentences
    if current_sentences:
        sub_chunks.append(
            _create_sub_chunk(
                " ".join(current_sentences),
                original_chunk,
                start_index + len(sub_chunks),
            )
        )

    return sub_chunks if sub_chunks else [original_chunk]


def _split_at_word_boundaries(
    text: str, max_size: int, original_chunk: Chunk, start_index: int
) -> List[Chunk]:
    """
    Split text at word boundaries (last resort).

    Args:
        text: Text to split
        max_size: Maximum size per chunk
        original_chunk: Original chunk for metadata
        start_index: Starting index for sub-chunks

    Returns:
        List of sub-chunks
    """
    sub_chunks = []
    remaining = text
    chunk_index = 0

    while len(remaining) > max_size:
        # Truncate at word boundary
        truncated = truncate_at_word_boundary(remaining, max_size, from_end=False)

        if not truncated or len(truncated) == len(remaining):
            # Couldn't truncate - force split
            truncated = remaining[:max_size]
            remaining = remaining[max_size:]
        else:
            remaining = remaining[len(truncated) :].lstrip()

        sub_chunks.append(
            _create_sub_chunk(truncated, original_chunk, start_index + chunk_index)
        )
        chunk_index += 1

    # Add remaining content
    if remaining.strip():
        sub_chunks.append(
            _create_sub_chunk(remaining, original_chunk, start_index + chunk_index)
        )

    return sub_chunks if sub_chunks else [original_chunk]


def _create_sub_chunk(content: str, original_chunk: Chunk, sub_index: int) -> Chunk:
    """
    Create a sub-chunk from split content.

    Args:
        content: Content for the sub-chunk
        original_chunk: Original chunk for metadata inheritance
        sub_index: Index of this sub-chunk

    Returns:
        New Chunk object
    """
    # Inherit metadata from original
    metadata = original_chunk.metadata.copy()
    metadata["is_split"] = True
    metadata["split_from"] = original_chunk.get_metadata("id", "unknown")
    metadata["split_index"] = sub_index

    # Create new chunk
    return Chunk(
        content=content.strip(),
        start_line=original_chunk.start_line,
        end_line=original_chunk.end_line,
        metadata=metadata,
    )


def enforce_size_limits(chunks: List[Chunk], config: ChunkConfig) -> List[Chunk]:
    """
    Enforce size limits on all chunks, splitting oversized non-atomic chunks.

    This is the main entry point for size enforcement. It processes all chunks
    and splits any that exceed max_chunk_size (unless they're atomic).

    Args:
        chunks: List of chunks to process
        config: Configuration with size limits

    Returns:
        List of chunks with size limits enforced
    """
    if config.allow_oversize:
        # If oversize is allowed, just mark them but don't split
        return chunks

    result = []
    for chunk in chunks:
        if len(chunk.content) > config.max_chunk_size:
            # Try to split
            split_chunks = split_oversized_chunk(chunk, config)
            result.extend(split_chunks)
        else:
            result.append(chunk)

    return result
