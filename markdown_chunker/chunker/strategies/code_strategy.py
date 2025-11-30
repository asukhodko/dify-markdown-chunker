"""
CodeStrategy - Code-heavy document chunking strategy.

This strategy specializes in handling documents with large amounts of code,
preserving code block atomicity while maintaining context with surrounding text.

Algorithm Documentation:
    - Code Strategy: docs/markdown-extractor/03-strategies/code-strategy.md
    - Strategy Selection: docs/markdown-extractor/02-algorithm-core/strategy-selection.md  # noqa: E501
"""

import re
from dataclasses import dataclass
from typing import List, Optional

from markdown_chunker.parser.types import ContentAnalysis, FencedBlock, Stage1Results

from ..types import Chunk, ChunkConfig
from .base import BaseStrategy


@dataclass
class CodeSegment:
    """A segment of content that is either code or text."""

    type: str  # "code" or "text"
    content: str
    start_line: int
    end_line: int
    language: Optional[str] = None
    is_fenced: bool = False
    function_names: Optional[List[str]] = None
    class_names: Optional[List[str]] = None

    def __post_init__(self):
        if self.function_names is None:
            self.function_names = []
        if self.class_names is None:
            self.class_names = []


class CodeStrategy(BaseStrategy):
    """
    Strategy for code-heavy documents (≥70% code, ≥3 blocks).

    This strategy:
    - Preserves code blocks atomically (never splits functions/classes)
    - Extracts code metadata (language, functions, classes)
    - Groups related text with code blocks
    - Allows oversize chunks for large code blocks
    - Maintains context between code and explanations

    Priority: 1 (highest)
    """

    # Language detection patterns
    LANGUAGE_PATTERNS = {
        "python": [
            r"\bdef\s+\w+",
            r"\bclass\s+\w+",
            r"\bimport\s+\w+",
            r"\bfrom\s+\w+",
        ],
        "javascript": [
            r"\bfunction\s+\w+",
            r"\bconst\s+\w+",
            r"\blet\s+\w+",
            r"\bvar\s+\w+",
        ],
        "java": [r"\bpublic\s+class", r"\bprivate\s+\w+", r"\bpublic\s+static"],
        "go": [r"\bfunc\s+\w+", r"\bpackage\s+\w+", r"\btype\s+\w+"],
        "rust": [r"\bfn\s+\w+", r"\bstruct\s+\w+", r"\bimpl\s+\w+"],
        "cpp": [r"\bclass\s+\w+", r"\bstruct\s+\w+", r"#include"],
        "c": [r"#include", r"\bstruct\s+\w+", r"\bint\s+main"],
    }

    # Function extraction patterns by language
    FUNCTION_PATTERNS = {
        "python": r"\bdef\s+(\w+)\s*\(",
        "javascript": r"\bfunction\s+(\w+)\s*\(",
        "java": r"\b(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(",
        "go": r"\bfunc\s+(\w+)\s*\(",
        "rust": r"\bfn\s+(\w+)\s*\(",
        "cpp": r"\b(?:inline\s+)?\w+\s+(\w+)\s*\(",
        "c": r"\b\w+\s+(\w+)\s*\(",
    }

    # Class extraction patterns by language
    CLASS_PATTERNS = {
        "python": r"\bclass\s+(\w+)",
        "javascript": r"\bclass\s+(\w+)",
        "java": r"\b(?:public|private)?\s*class\s+(\w+)",
        "go": r"\btype\s+(\w+)\s+struct",
        "rust": r"\bstruct\s+(\w+)",
        "cpp": r"\bclass\s+(\w+)",
        "c": r"\bstruct\s+(\w+)",
    }

    @property
    def name(self) -> str:
        """Strategy name."""
        return "code"

    @property
    def priority(self) -> int:
        """Highest priority."""
        return 1

    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        """
        Check if strategy can handle the content.

        Requires:
        - High code ratio (≥70% by default, configurable via code_ratio_threshold)
        - Sufficient code blocks (≥3 by default, configurable via min_code_blocks)

        Args:
            analysis: Content analysis from Stage 1
            config: Chunking configuration with thresholds

        Returns:
            True if content is code-heavy enough for this strategy

        Examples:
            >>> analysis=ContentAnalysis(code_ratio=0.75, code_block_count=5, ...)
            >>> config=ChunkConfig(code_ratio_threshold=0.7, min_code_blocks=3)
            >>> strategy=CodeStrategy()
            >>> print(strategy.can_handle(analysis, config))
            True
        """
        return (
            analysis.code_ratio >= config.code_ratio_threshold
            and analysis.code_block_count >= config.min_code_blocks
        )

    def calculate_quality(self, analysis: ContentAnalysis) -> float:
        """
        Calculate quality score for code strategy.

        Higher quality for:
        - Higher code ratio (≥85%: 0.8, ≥70%: 0.6, ≥50%: 0.3)
        - More code blocks (≥10: +0.2, ≥5: +0.15, ≥3: +0.1)
        - Multiple programming languages (+0.1 bonus)

        Args:
            analysis: Content analysis from Stage 1

        Returns:
            Quality score between 0.0 and 1.0 (higher=better fit)

        Examples:
            >>> analysis=ContentAnalysis(
            ...     code_ratio=0.85,
            ...     code_block_count=10,
            ...     languages={'python', 'javascript'},
            ...     ...
            ... )
            >>> strategy=CodeStrategy()
            >>> score=strategy.calculate_quality(analysis)
            >>> print(f"{score:.2f}")  # 0.8 + 0.2 + 0.1=1.0
            1.00
        """
        score = 0.0

        # Code ratio contribution
        if analysis.code_ratio >= 0.85:
            score += 0.8
        elif analysis.code_ratio >= 0.7:
            score += 0.6
        elif analysis.code_ratio >= 0.5:
            score += 0.3

        # Code block count contribution
        if analysis.code_block_count >= 10:
            score += 0.2
        elif analysis.code_block_count >= 5:
            score += 0.15
        elif analysis.code_block_count >= 3:
            score += 0.1

        # Multiple languages bonus
        if len(analysis.languages) > 1:
            score += 0.1

        return min(score, 1.0)

    def apply(
        self, content: str, stage1_results: Stage1Results, config: ChunkConfig
    ) -> List[Chunk]:
        """
        Apply code strategy to create chunks.

        Args:
            content: Original markdown content
            stage1_results: Results from Stage 1 processing
            config: Chunking configuration

        Returns:
            List of chunks created by code-aware splitting
        """
        if not content.strip():
            return []

        # Extract code blocks from Stage 1 results
        code_blocks = self._extract_code_blocks(stage1_results)

        if not code_blocks:
            # No code blocks found - cannot use code strategy
            return []

        # Segment content around code blocks
        segments = self._segment_around_code_blocks(content, code_blocks)

        # Process segments into chunks
        chunks = self._process_segments(segments, config)

        return self._validate_chunks(chunks, config)

    def _extract_code_blocks(self, stage1_results: Stage1Results) -> List[FencedBlock]:
        """
        Extract code blocks from Stage 1 results.

        Args:
            stage1_results: Stage 1 processing results

        Returns:
            List of FencedBlock objects
        """
        if hasattr(stage1_results, "fenced_blocks") and stage1_results.fenced_blocks:
            return stage1_results.fenced_blocks
        else:
            return []

    def _segment_around_code_blocks(
        self, content: str, code_blocks: List[FencedBlock]
    ) -> List[CodeSegment]:
        """
        Segment content around code blocks.

        Args:
            content: Original content
            code_blocks: List of code blocks

        Returns:
            List of CodeSegment objects alternating between text and code
        """
        segments = []
        current_pos = 0
        content_lines = content.split("\n")

        for code_block in code_blocks:
            # Get the actual code block content with fences
            # Ensure we capture the complete code block including closing fence
            raw_content = code_block.raw_content
            
            # Verify the raw_content has balanced fences
            fence_count = raw_content.count("```")
            if fence_count < 2:
                # Try to find the complete code block in content
                raw_content = self._extract_complete_code_block(
                    content, code_block.start_offset
                )
            
            # Calculate actual end offset based on raw_content
            # Add 1 to include the newline after closing fence
            actual_end_offset = code_block.start_offset + len(raw_content)
            # Check if there's a newline after the code block and include it
            if actual_end_offset < len(content) and content[actual_end_offset] == '\n':
                actual_end_offset += 1
            
            # Text before code block
            if code_block.start_offset > current_pos:
                text_content = content[current_pos : code_block.start_offset].strip()
                if text_content:
                    text_start_line = self._calculate_line_number(content, current_pos)
                    text_end_line = max(text_start_line, code_block.start_line - 1)

                    segments.append(
                        CodeSegment(
                            type="text",
                            content=text_content,
                            start_line=text_start_line,
                            end_line=text_end_line,
                        )
                    )

            # Code block
            # Extract metadata from code block
            language = code_block.language or self._detect_language(code_block.content)
            function_names = self._extract_function_names(code_block.content, language)
            class_names = self._extract_class_names(code_block.content, language)

            segments.append(
                CodeSegment(
                    type="code",
                    content=raw_content,  # Include fences
                    start_line=code_block.start_line,
                    end_line=code_block.end_line,
                    language=language,
                    is_fenced=True,
                    function_names=function_names,
                    class_names=class_names,
                )
            )

            current_pos = actual_end_offset

        # Text after last code block
        if current_pos < len(content):
            text_content = content[current_pos:].strip()
            if text_content:
                text_start_line = self._calculate_line_number(content, current_pos)
                text_end_line = max(text_start_line, len(content_lines))

                segments.append(
                    CodeSegment(
                        type="text",
                        content=text_content,
                        start_line=text_start_line,
                        end_line=text_end_line,
                    )
                )

        return segments

    def _extract_complete_code_block(self, content: str, start_offset: int) -> str:
        """
        Extract complete code block from content starting at offset.
        
        Ensures both opening and closing fences are included.
        
        Args:
            content: Full content
            start_offset: Starting position of code block
            
        Returns:
            Complete code block with both fences
        """
        # Find the opening fence
        remaining = content[start_offset:]
        
        # Find opening fence
        if not remaining.lstrip().startswith("```"):
            # Not a valid code block start
            return remaining.split("\n\n")[0]  # Return first paragraph
        
        # Find closing fence
        lines = remaining.split("\n")
        in_block = False
        block_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                if not in_block:
                    # Opening fence
                    in_block = True
                    block_lines.append(line)
                else:
                    # Closing fence
                    block_lines.append(line)
                    break
            elif in_block:
                block_lines.append(line)
        
        return "\n".join(block_lines)

    def _process_segments(
        self, segments: List[CodeSegment], config: ChunkConfig
    ) -> List[Chunk]:
        """
        Process segments into chunks.

        Args:
            segments: List of code and text segments
            config: Chunking configuration

        Returns:
            List of chunks
        """
        chunks = []

        for segment in segments:
            if segment.type == "code":
                # Code segments are always kept atomic
                chunk = self._create_code_chunk(segment, config)
                chunks.append(chunk)
            else:
                # Text segments may be split if too large
                if len(segment.content) <= config.max_chunk_size:
                    chunk = self._create_text_chunk(segment, config)
                    chunks.append(chunk)
                else:
                    # Split large text segments
                    text_chunks = self._split_text_segment(segment, config)
                    chunks.extend(text_chunks)

        return chunks

    def _create_code_chunk(self, segment: CodeSegment, config: ChunkConfig) -> Chunk:
        """
        Create a chunk from a code segment.

        Args:
            segment: Code segment
            config: Chunking configuration

        Returns:
            Chunk with code content and metadata
        """
        metadata = {
            "language": segment.language or "unknown",
            "is_fenced": segment.is_fenced,
        }

        # Add function names if found
        if segment.function_names:
            metadata["function_names"] = segment.function_names
            if len(segment.function_names) == 1:
                metadata["function_name"] = segment.function_names[0]

        # Add class names if found
        if segment.class_names:
            metadata["class_names"] = segment.class_names
            if len(segment.class_names) == 1:
                metadata["class_name"] = segment.class_names[0]

        # Handle oversize chunks
        if len(segment.content) > config.max_chunk_size:
            metadata["allow_oversize"] = True
            metadata["oversize_reason"] = "code_block_atomicity"

        return self._create_chunk(
            content=segment.content,
            start_line=segment.start_line,
            end_line=segment.end_line,
            content_type="code",
            **metadata,
        )

    def _create_text_chunk(self, segment: CodeSegment, config: ChunkConfig) -> Chunk:
        """
        Create a chunk from a text segment.

        Args:
            segment: Text segment
            config: Chunking configuration

        Returns:
            Chunk with text content and metadata
        """
        metadata = {"context": "code_explanation"}

        return self._create_chunk(
            content=segment.content,
            start_line=segment.start_line,
            end_line=segment.end_line,
            content_type="text",
            **metadata,
        )

    def _split_text_segment(
        self, segment: CodeSegment, config: ChunkConfig
    ) -> List[Chunk]:
        """
        Split a large text segment into multiple chunks.

        Args:
            segment: Large text segment
            config: Chunking configuration

        Returns:
            List of text chunks
        """
        chunks = []

        # Split by sentences (simple approach)
        sentences = re.split(r"[.!?]+\s+", segment.content)
        current_content = ""
        current_start_line = segment.start_line

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Check if adding this sentence would exceed size
            potential_content = current_content
            if potential_content:
                potential_content += " " + sentence
            else:
                potential_content = sentence

            if len(potential_content) > config.max_chunk_size and current_content:
                # Create chunk with current content
                chunk = self._create_text_chunk(
                    CodeSegment(
                        type="text",
                        content=current_content,
                        start_line=current_start_line,
                        end_line=current_start_line + current_content.count("\n"),
                    ),
                    config,
                )
                chunks.append(chunk)

                # Start new chunk
                current_content = sentence
                current_start_line += current_content.count("\n") + 1
            else:
                # Add sentence to current chunk
                if current_content:
                    current_content += " " + sentence
                else:
                    current_content = sentence

        # Add final chunk if there's remaining content
        if current_content:
            chunk = self._create_text_chunk(
                CodeSegment(
                    type="text",
                    content=current_content,
                    start_line=current_start_line,
                    end_line=segment.end_line,
                ),
                config,
            )
            chunks.append(chunk)

        return chunks

    def _detect_language(self, code_content: str) -> Optional[str]:
        """
        Detect programming language from code content.

        Args:
            code_content: Code content to analyze

        Returns:
            Detected language or None
        """
        for language, patterns in self.LANGUAGE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, code_content, re.IGNORECASE):
                    return language

        return None

    def _extract_function_names(
        self, code_content: str, language: Optional[str]
    ) -> List[str]:
        """
        Extract function names from code content.

        Args:
            code_content: Code content to analyze
            language: Programming language

        Returns:
            List of function names
        """
        if not language or language not in self.FUNCTION_PATTERNS:
            return []

        pattern = self.FUNCTION_PATTERNS[language]
        matches = re.findall(pattern, code_content, re.MULTILINE)

        return matches

    def _extract_class_names(
        self, code_content: str, language: Optional[str]
    ) -> List[str]:
        """
        Extract class names from code content.

        Args:
            code_content: Code content to analyze
            language: Programming language

        Returns:
            List of class names
        """
        if not language or language not in self.CLASS_PATTERNS:
            return []

        pattern = self.CLASS_PATTERNS[language]
        matches = re.findall(pattern, code_content, re.MULTILINE)

        return matches

    def _calculate_line_number(self, content: str, position: int) -> int:
        """
        Calculate line number for a character position.

        Args:
            content: Full content
            position: Character position

        Returns:
            Line number (1-based)
        """
        return content[:position].count("\n") + 1

    def _get_selection_reason(self, analysis: ContentAnalysis, can_handle: bool) -> str:
        """Get reason for strategy selection."""
        if can_handle:
            return (
                f"High code ratio ({analysis.code_ratio:.1%}) with "
                f"{analysis.code_block_count} code blocks - "
                f"ideal for code strategy"
            )
        else:
            if analysis.code_ratio < 0.7:
                return (
                    f"Code ratio ({analysis.code_ratio:.1%}) below threshold "
                    f"(70%) for code strategy"
                )
            elif analysis.code_block_count < 3:
                return (
                    f"Too few code blocks ({analysis.code_block_count}) "
                    f"for code strategy"
                )
            else:
                return "Content not suitable for code strategy"
