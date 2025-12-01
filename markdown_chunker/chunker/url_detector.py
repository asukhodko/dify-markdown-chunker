"""
URL detector for Phase 2 semantic quality improvements.

This module detects URLs and Markdown links in content to ensure they
are not broken during chunking. URLs are treated as atomic elements.
"""

import re
from typing import List, Tuple


class URLDetector:
    """
    Detects and validates URLs/links in markdown content.

    This detector identifies various URL formats including HTTP(S), www,
    email addresses, Markdown links, wiki links, and git repository URLs.
    It's used to ensure URLs remain intact during chunking.

    Examples:
        >>> detector = URLDetector()
        >>> urls = detector.detect_urls("Visit https://example.com for info")
        >>> print(urls)
        [(6, 25, 'https://example.com')]
        >>>
        >>> has_urls = detector.has_urls("Plain text without links")
        >>> print(has_urls)
        False
    """

    # URL patterns for detection
    URL_PATTERNS = [
        # HTTP(S) URLs
        (r'https?://[^\s<>"{}|\\^`\[\]]+', "http"),
        # www URLs
        (r'www\.[^\s<>"{}|\\^`\[\]]+', "www"),
        # Email addresses
        (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "email"),
        # Markdown links [text](url)
        (r"\[([^\]]+)\]\(([^)]+)\)", "markdown_link"),
        # Wiki links (Confluence style) [[Page Name]]
        (r"\[\[([^\]]+)\]\]", "wiki_link"),
        # Git repository URLs (GitHub, GitLab, etc.)
        (r"git@[a-zA-Z0-9.-]+:[a-zA-Z0-9/_-]+\.git", "git_ssh"),
    ]

    def __init__(self):
        """Initialize URL detector with compiled patterns."""
        self.compiled_patterns = [
            (re.compile(pattern), url_type) for pattern, url_type in self.URL_PATTERNS
        ]

    def detect_urls(self, text: str) -> List[Tuple[int, int, str]]:
        """
        Detect all URLs in text.

        Args:
            text: Text to search for URLs

        Returns:
            List of (start_pos, end_pos, url_text) tuples sorted by position

        Examples:
            >>> detector = URLDetector()
            >>> text = "Check https://example.com and www.test.org"
            >>> urls = detector.detect_urls(text)
            >>> for start, end, url in urls:
            ...     print(f"{start}-{end}: {url}")
            6-25: https://example.com
            30-42: www.test.org
        """
        urls = []

        for pattern, url_type in self.compiled_patterns:
            for match in pattern.finditer(text):
                # For markdown links, extract the URL part
                if url_type == "markdown_link":
                    # Match group 2 is the URL in [text](url)
                    url_text = match.group(0)  # Keep full markdown link
                else:
                    url_text = match.group(0)

                urls.append((match.start(), match.end(), url_text))

        # Sort by position and remove duplicates
        urls = sorted(set(urls), key=lambda x: x[0])
        return urls

    def has_urls(self, text: str) -> bool:
        """
        Check if text contains any URLs.

        Args:
            text: Text to check

        Returns:
            True if text contains at least one URL, False otherwise

        Examples:
            >>> detector = URLDetector()
            >>> detector.has_urls("Visit https://example.com")
            True
            >>> detector.has_urls("Plain text")
            False
        """
        for pattern, _ in self.compiled_patterns:
            if pattern.search(text):
                return True
        return False

    def is_split_safe(self, text: str, split_pos: int) -> bool:
        """
        Check if splitting at position would break a URL.

        Args:
            text: Text to split
            split_pos: Proposed split position

        Returns:
            True if safe to split (no URL would be broken), False otherwise

        Examples:
            >>> detector = URLDetector()
            >>> text = "Visit https://example.com for info"
            >>> detector.is_split_safe(text, 5)  # Before URL
            True
            >>> detector.is_split_safe(text, 15)  # Inside URL
            False
            >>> detector.is_split_safe(text, 26)  # After URL
            True
        """
        urls = self.detect_urls(text)

        for start, end, _ in urls:
            if start < split_pos < end:
                return False  # Split would break URL

        return True

    def find_safe_split(
        self, text: str, target_pos: int, direction: str = "left"
    ) -> int:
        """
        Find nearest safe split position that doesn't break URLs.

        Args:
            text: Text to split
            target_pos: Desired split position
            direction: "left" or "right" - which way to search for safe position

        Returns:
            Safe split position (may be same as target_pos if already safe)

        Examples:
            >>> detector = URLDetector()
            >>> text = "Visit https://example.com for more info"
            >>> # Target is inside URL, find safe position to the left
            >>> safe_pos = detector.find_safe_split(text, 15, "left")
            >>> print(safe_pos)  # Position before URL starts
            6
        """
        if self.is_split_safe(text, target_pos):
            return target_pos

        urls = self.detect_urls(text)

        if direction == "left":
            # Find nearest URL boundary to the left
            for start, end, _ in reversed(urls):
                if end <= target_pos:
                    return end
                if start < target_pos:
                    return start
        else:
            # Find nearest URL boundary to the right
            for start, end, _ in urls:
                if start >= target_pos:
                    return start
                if end > target_pos:
                    return end

        return target_pos  # Fallback to original position

    def get_url_types(self, text: str) -> List[str]:
        """
        Get types of URLs present in text.

        Args:
            text: Text to analyze

        Returns:
            List of URL types found (e.g., ['http', 'email', 'markdown_link'])

        Examples:
            >>> detector = URLDetector()
            >>> text = "Email me@test.com or visit https://example.com"
            >>> types = detector.get_url_types(text)
            >>> print(sorted(types))
            ['email', 'http']
        """
        types = set()

        for pattern, url_type in self.compiled_patterns:
            if pattern.search(text):
                types.add(url_type)

        return list(types)
