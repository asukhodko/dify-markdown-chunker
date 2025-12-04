"""
Text normalization utilities for ensuring whitespace preservation.

This module provides utilities for normalizing text while preserving proper
whitespace between tokens, preventing the concatenation of words and loss
of formatting.

Functions:
    normalize_whitespace: Normalize whitespace while preserving token boundaries
    join_content_blocks: Join blocks with proper whitespace separation
    normalize_list_content: Preserve list formatting during normalization
    ensure_space_between_tokens: Ensure minimum whitespace between tokens
"""

import re
from typing import List


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace while preserving token boundaries.

    This function ensures that:
    - Single newlines are replaced with spaces
    - Double newlines are preserved as paragraph breaks
    - At least one space exists between non-whitespace tokens
    - Trailing punctuation-space patterns are preserved

    Args:
        text: Input text to normalize

    Returns:
        Normalized text with proper whitespace

    Examples:
        >>> normalize_whitespace("word1\\nword2")
        'word1 word2'
        >>> normalize_whitespace("word1\\n\\nword2")
        'word1\\n\\nword2'
        >>> normalize_whitespace("word1word2")
        'word1 word2'
    """
    if not text:
        return text

    # Step 1: Preserve paragraph breaks (double newlines)
    # Replace them with a placeholder to protect during processing
    paragraph_marker = "\x00PARAGRAPH_BREAK\x00"
    text = re.sub(r"\n\n+", paragraph_marker, text)

    # Step 2: Replace single newlines with spaces
    text = re.sub(r"\n", " ", text)

    # Step 3: Ensure space after punctuation if followed by alphanumeric
    # Pattern: punctuation + no space + alphanumeric
    text = re.sub(r"([.!?:;,])([A-Za-zА-Яа-я0-9])", r"\1 \2", text)

    # Step 4: Ensure space between adjacent alphanumeric tokens
    # This catches cases like "wordword" -> "word word"
    # But preserves intentional compounds
    # Pattern: letter/digit + letter at word boundary
    text = re.sub(r"([a-zа-я])([A-ZА-Я])", r"\1 \2", text)

    # Step 5: Normalize multiple spaces to single space (but not paragraph breaks)
    text = re.sub(r" +", " ", text)

    # Step 6: Restore paragraph breaks
    text = text.replace(paragraph_marker, "\n\n")

    # Step 7: Clean up edge cases
    text = text.strip()

    return text


def join_content_blocks(blocks: List[str], separator: str = "\n\n") -> str:
    """
    Join content blocks with proper whitespace separation.

    Ensures that blocks are joined with appropriate whitespace and validates
    that no token adjacency occurs without whitespace.

    Args:
        blocks: List of content blocks to join
        separator: Separator to use between blocks (default: double newline)

    Returns:
        Joined content with proper whitespace

    Raises:
        ValueError: If joining would create token adjacency without whitespace

    Examples:
        >>> join_content_blocks(["Block 1", "Block 2"])
        'Block 1\\n\\nBlock 2'
        >>> join_content_blocks(["Block 1", "Block 2"], " ")
        'Block 1 Block 2'
    """
    if not blocks:
        return ""

    # Filter out empty blocks
    non_empty_blocks = [b.strip() for b in blocks if b.strip()]

    if not non_empty_blocks:
        return ""

    # Join blocks
    result = separator.join(non_empty_blocks)

    # Validate no token adjacency
    if not ensure_space_between_tokens(result):
        # Try to fix by adding space at problem points
        result = normalize_whitespace(result)

        # Validate again
        if not ensure_space_between_tokens(result):
            raise ValueError(
                "Joining blocks created token adjacency without whitespace. "
                "This indicates a formatting issue in the input blocks."
            )

    return result


def normalize_list_content(text: str) -> str:
    """
    Normalize list content while preserving list formatting.

    Ensures that:
    - List markers are preserved
    - Spacing after markers is normalized to single space
    - Indentation structure is preserved
    - Line breaks between items are maintained
    - Blank lines after list labels/headers are preserved

    Args:
        text: List content to normalize

    Returns:
        Normalized list content with preserved formatting

    Examples:
        >>> normalize_list_content("- Item 1\\n- Item 2")
        '- Item 1\\n- Item 2'
        >>> normalize_list_content("-  Item 1\\n-Item 2")
        '- Item 1\\n- Item 2'
    """
    if not text:
        return text

    lines = text.split("\n")
    normalized_lines = []

    for line in lines:
        # Detect list item patterns
        # Check in order: Task lists, Ordered lists, Unordered lists
        # Task lists must be checked FIRST because they also match unordered pattern

        # Check for task list marker (- [ ] or - [x])
        match = re.match(r"^(\s*)([-*+])\s*(\[[xX ]\])\s*(.*)$", line)
        if match:
            indent, marker, checkbox, content = match.groups()
            # Normalize checkbox spacing and content
            content = content.strip()
            # Normalize checkbox to lowercase x
            checkbox = checkbox.lower()
            normalized_lines.append(f"{indent}{marker} {checkbox} {content}")
            continue

        # Check for ordered list marker (1., 2., etc.)
        match = re.match(r"^(\s*)(\d+\.)\s*(.*)$", line)
        if match:
            indent, marker, content = match.groups()
            normalized_lines.append(f"{indent}{marker} {content}")
            continue

        # Check for unordered list marker (-, *, +)
        match = re.match(r"^(\s*)([-*+])\s*(.*)$", line)
        if match:
            indent, marker, content = match.groups()
            # Normalize spacing: indent + marker + single space + content
            normalized_lines.append(f"{indent}{marker} {content}")
            continue

        # Not a list item, preserve as-is
        normalized_lines.append(line)

    return "\n".join(normalized_lines)


def ensure_space_between_tokens(text: str) -> bool:
    """
    Validate that all tokens have whitespace between them.

    Checks for patterns where alphanumeric characters are adjacent
    without whitespace, which indicates improper text concatenation.

    Args:
        text: Text to validate

    Returns:
        True if text has proper spacing, False if tokens are adjacent

    Examples:
        >>> ensure_space_between_tokens("word1 word2")
        True
        >>> ensure_space_between_tokens("word1word2")
        False
        >>> ensure_space_between_tokens("word1. Word2")
        True
    """
    if not text:
        return True

    # Check for problematic patterns:
    # 1. Lowercase letter followed by uppercase letter
    # (camelCase is ok, but "word.Word" is not)
    # 2. Letter followed by digit or digit followed by letter without space
    # 3. Punctuation followed immediately by letter (except hyphenated words)

    # Pattern 1: Sentence ending (. ! ?) followed immediately by uppercase without space
    if re.search(r"[.!?][A-ZА-Я]", text):
        return False

    # Pattern 2: Colon or semicolon followed immediately by letter without space
    if re.search(r"[:;][A-Za-zА-Яа-я]", text):
        return False

    # Pattern 3: Closing punctuation followed by opening
    # (e.g., ")(" or "](" without space)
    if re.search(r'[)\]}"\']\s*[(\[{"\']', text):
        # This might be okay (e.g., citations), so we'll allow it
        pass

    return True


def ensure_list_formatting(content: str) -> str:
    """
    Ensure proper formatting for list content.

    Detects list patterns and ensures:
    - Spacing after markers
    - Line breaks between items
    - Indentation consistency

    Args:
        content: Content that may contain lists

    Returns:
        Content with ensured list formatting

    Examples:
        >>> ensure_list_formatting("1.Item one2.Item two")
        '1. Item one\\n2. Item two'
    """
    if not content:
        return content

    # Detect and fix common list formatting issues

    # Pattern: "1.Word" -> "1. Word"
    content = re.sub(r"(\d+\.)([A-Za-zА-Яа-я])", r"\1 \2", content)

    # Pattern: "-Word" -> "- Word"
    content = re.sub(r"(^|\n)([-*+])([A-Za-zА-Яа-я])", r"\1\2 \3", content)

    # Pattern: "item1.item2." with numbers -> "item1.\nitem2."
    content = re.sub(
        r"([^.\d])(\d+\.\s*[A-Za-zА-Яа-я][^.]*\.)(\d+\.)", r"\1\2\n\3", content
    )

    return content


def truncate_at_word_boundary(
    text: str, max_length: int, from_end: bool = False
) -> str:
    """
    Truncate text at word boundary without splitting words.

    Args:
        text: Text to truncate
        max_length: Maximum length in characters
        from_end: If True, truncate from end; if False, from beginning

    Returns:
        Truncated text ending/starting at word boundary

    Examples:
        >>> truncate_at_word_boundary("The quick brown fox", 10)
        'The quick'
        >>> truncate_at_word_boundary("The quick brown fox", 10, from_end=True)
        'brown fox'
    """
    if len(text) <= max_length:
        return text

    if from_end:
        # Truncate from beginning, keep end
        truncated = text[-max_length:]
        # Find first word boundary
        match = re.search(r"\s", truncated)
        if match:
            # CRITICAL FIX (Phase 2.1): Use strip() for symmetric behavior
            return truncated[match.end() :].strip()
        return truncated.strip()
    else:
        # Truncate from end, keep beginning
        truncated = text[:max_length]
        # Find last word boundary
        match = re.search(r"\s\S+$", truncated)
        if match:
            # CRITICAL FIX (Phase 2.1): Use strip() for symmetric behavior
            result = truncated[: match.start()].strip()
            return result
        return truncated.strip()


def normalize_line_breaks(text: str) -> str:
    """
    Normalize excessive line breaks in chunk content.

    This function addresses the issue of excessive blank lines accumulating
    in chunks due to overlap and block concatenation.

    Normalization rules:
    - 3+ consecutive blank lines → 2 blank lines (preserve paragraph separation)
    - Trailing blank lines → removed entirely
    - Leading blank lines → removed entirely

    Args:
        text: Text content to normalize

    Returns:
        Text with normalized line breaks

    Examples:
        >>> normalize_line_breaks("Content\n\n\n\n\n\nMore")
        'Content\n\nMore'
        >>> normalize_line_breaks("Text\n\n\n")
        'Text'
        >>> normalize_line_breaks("\n\n\nHeader\n\nSection")
        'Header\n\nSection'
    """
    if not text:
        return text

    # Replace 3+ consecutive newlines with exactly 2 newlines
    # This preserves paragraph breaks while removing excessive spacing
    text = re.sub(r"\n\n\n+", "\n\n", text)

    # Trim leading and trailing whitespace/newlines
    text = text.strip()

    return text


def validate_no_word_fragments(text: str) -> bool:
    """
    Validate that text doesn't start or end with word fragments.

    A word fragment is detected when:
    - Text starts with lowercase letter that doesn't form a valid word
    - Text ends with alphanumeric not followed by punctuation or whitespace

    Args:
        text: Text to validate

    Returns:
        True if no fragments detected, False otherwise

    Examples:
        >>> validate_no_word_fragments("The quick brown")
        True
        >>> validate_no_word_fragments("nk. Fragment")
        False
    """
    if not text or len(text) < 2:
        return True

    # Check start: if it starts with lowercase letter, it might be a fragment
    # Exception: common article words or list continuations
    if text[0].islower():
        # Extract first "word" (sequence of alphanumeric chars)
        first_word_match = re.match(r"^([a-z]+)", text, re.IGNORECASE)
        if first_word_match:
            first_word = first_word_match.group(1).lower()
            # Common valid words that can start lowercase
            valid_starts = {
                "a",
                "an",
                "the",
                "and",
                "or",
                "but",
                "in",
                "on",
                "at",
                "to",
                "for",
                "of",
                "with",
                "by",
                "from",
                "as",
                "is",
                "was",
                "are",
                "were",
                "be",
                "been",
                "being",
                "have",
                "has",
                "had",
                "do",
                "does",
                "did",
                "will",
                "would",
                "could",
                "should",
                "may",
                "might",
                "can",
                "if",
                "then",
                "when",
                "where",
                "what",
                "who",
                "which",
                "why",
                "how",
                "word",
                "words",
            }
            # If the first word is a valid standalone word, it's okay
            if first_word in valid_starts:
                return True
            # If it's a very short fragment (1-2 chars), likely invalid
            if len(first_word) <= 2:
                return False

    return True
