"""
Regression prevention validator for ensuring bug fixes don't regress.

This module provides validation functions that check for the specific bug
patterns identified in the design document. It should be run as part of
CI/CD to prevent regression of critical fixes.
"""

import re
from typing import Dict, List, Tuple

from .types import Chunk


class RegressionCheck:
    """Base class for regression checks."""

    def __init__(self, bug_id: str, description: str):
        self.bug_id = bug_id
        self.description = description

    def check(self, chunks: List[Chunk], original_text: str) -> Tuple[bool, str]:
        """
        Check for regression.

        Args:
            chunks: Generated chunks
            original_text: Original markdown text

        Returns:
            Tuple of (passed, message)
        """
        raise NotImplementedError


class BLOCK1_WhitespaceCheck(RegressionCheck):
    """Check for BLOCK-1: Text concatenation without whitespace preservation."""

    def __init__(self):
        super().__init__(
            "BLOCK-1", "Text concatenation without whitespace preservation"
        )

    def check(self, chunks: List[Chunk], original_text: str) -> Tuple[bool, str]:
        """Check that no tokens are adjacent without whitespace."""
        issues = []

        # Pattern: punctuation directly followed by letter/cyrillic
        # Example: "продукта.Нет" or "Достижения:мы"
        pattern = r"([.!?:;,])([А-Яа-яA-Za-z])"

        for i, chunk in enumerate(chunks):
            matches = re.findall(pattern, chunk.content)
            if matches:
                for match in matches:
                    # Check if this is intentional (like URLs or abbreviations)
                    context = match[0] + match[1]
                    if context not in ["http:", "https:", "ftp:"]:  # Allow URLs
                        msg = f"Chunk {i}: Found '{context}'"
                        issues.append(f"{msg} - missing space after punctuation")

        if issues:
            return False, "BLOCK-1 regression detected:\n" + "\n".join(issues[:5])

        return True, "BLOCK-1: No whitespace issues detected"


class BLOCK2_WordFragmentCheck(RegressionCheck):
    """Check for BLOCK-2: Word splitting at chunk boundaries."""

    def __init__(self):
        super().__init__("BLOCK-2", "Word splitting at chunk boundaries")

    def check(self, chunks: List[Chunk], original_text: str) -> Tuple[bool, str]:
        """Check that chunks don't start/end with word fragments."""
        issues = []

        # Common fragment patterns (lowercase, 1-3 chars, not complete words)
        fragment_pattern = r"^[a-z]{1,3}[.,!?]?\s"

        common_words = {
            "a",
            "an",
            "at",
            "be",
            "by",
            "do",
            "go",
            "he",
            "i",
            "if",
            "in",
            "is",
            "it",
            "me",
            "my",
            "no",
            "of",
            "on",
            "or",
            "so",
            "to",
            "up",
            "us",
            "we",
        }

        for i, chunk in enumerate(chunks):
            content = chunk.content.strip()
            if not content:
                continue

            # Check start of chunk
            first_word = content.split()[0] if content.split() else ""
            first_word_clean = re.sub(r"[^a-zA-Z]", "", first_word).lower()

            if first_word_clean and len(first_word_clean) <= 3:
                if first_word_clean not in common_words:
                    # Might be a fragment
                    if re.match(fragment_pattern, content):
                        issues.append(
                            f"Chunk {i} starts with possible fragment: '{first_word}'"
                        )

        if issues:
            return False, "BLOCK-2 regression detected:\n" + "\n".join(issues[:5])

        return True, "BLOCK-2: No word fragments detected"


class BLOCK3_DuplicationCheck(RegressionCheck):
    """Check for BLOCK-3: Massive content duplication."""

    def __init__(self):
        super().__init__(
            "BLOCK-3", "Massive content duplication within and between chunks"
        )

    def check(self, chunks: List[Chunk], original_text: str) -> Tuple[bool, str]:
        """Check for excessive duplication."""
        from .dedup_validator import validate_no_excessive_duplication

        # Allow higher threshold for overlap scenarios
        is_valid, errors = validate_no_excessive_duplication(
            chunks, max_duplication_ratio=0.6
        )

        if not is_valid:
            return False, "BLOCK-3 regression detected:\n" + "\n".join(errors[:3])

        return True, "BLOCK-3: No excessive duplication detected"


class CRIT1_SizeViolationCheck(RegressionCheck):
    """Check for CRIT-1: Max chunk size constraint violations."""

    def __init__(self):
        super().__init__("CRIT-1", "Max chunk size constraint violations")

    def check(self, chunks: List[Chunk], original_text: str) -> Tuple[bool, str]:
        """Check that non-atomic chunks respect size limits."""
        from .size_enforcer import is_atomic_content

        issues = []

        for i, chunk in enumerate(chunks):
            # Get the max size from chunk metadata or assume 4096
            max_size = 4096  # Default

            if len(chunk.content) > max_size:
                # Check if it's allowed to be oversize
                if not chunk.is_oversize:
                    # Not marked as oversize - this is a violation
                    if not is_atomic_content(chunk.content):
                        issues.append(
                            f"Chunk {i}: {len(chunk.content)} chars exceeds {max_size} "
                            f"(non-atomic, not marked oversize)"
                        )

        if issues:
            return False, "CRIT-1 regression detected:\n" + "\n".join(issues[:5])

        return True, "CRIT-1: All chunks respect size limits"


class CRIT2_ListStructureCheck(RegressionCheck):
    """Check for CRIT-2: Complete loss of list structure formatting."""

    def __init__(self):
        super().__init__("CRIT-2", "Complete loss of list structure formatting")

    def check(self, chunks: List[Chunk], original_text: str) -> Tuple[bool, str]:
        """Check that list structures are preserved."""
        # Find lists in original text
        has_unordered_list = bool(
            re.search(r"^\s*[-*+]\s+", original_text, re.MULTILINE)
        )
        has_ordered_list = bool(re.search(r"^\s*\d+\.\s+", original_text, re.MULTILINE))
        has_task_list = bool(
            re.search(r"^\s*[-*+]\s*\[[x ]\]", original_text, re.MULTILINE)
        )

        if not (has_unordered_list or has_ordered_list or has_task_list):
            return True, "CRIT-2: No lists in original text"

        # Check that lists appear in chunks
        combined_chunks = "\n".join(c.content for c in chunks)

        issues = []

        if has_unordered_list:
            if not re.search(r"^\s*[-*+]\s+", combined_chunks, re.MULTILINE):
                issues.append("Unordered list markers lost")

        if has_ordered_list:
            if not re.search(r"^\s*\d+\.\s+", combined_chunks, re.MULTILINE):
                issues.append("Ordered list markers lost")

        if has_task_list:
            if not re.search(r"\[[x ]\]", combined_chunks):
                issues.append("Task list checkboxes lost")

        if issues:
            return False, "CRIT-2 regression detected:\n" + "\n".join(issues)

        return True, "CRIT-2: List structures preserved"


class RegressionValidator:
    """Main validator for running all regression checks."""

    def __init__(self):
        self.checks = [
            BLOCK1_WhitespaceCheck(),
            BLOCK2_WordFragmentCheck(),
            BLOCK3_DuplicationCheck(),
            CRIT1_SizeViolationCheck(),
            CRIT2_ListStructureCheck(),
        ]

    def validate(
        self, chunks: List[Chunk], original_text: str
    ) -> Dict[str, Tuple[bool, str]]:
        """
        Run all regression checks.

        Args:
            chunks: Generated chunks
            original_text: Original markdown text

        Returns:
            Dictionary mapping bug_id to (passed, message)
        """
        results = {}

        for check in self.checks:
            passed, message = check.check(chunks, original_text)
            results[check.bug_id] = (passed, message)

        return results

    def validate_and_report(self, chunks: List[Chunk], original_text: str) -> bool:
        """
        Run all checks and print report.

        Args:
            chunks: Generated chunks
            original_text: Original markdown text

        Returns:
            True if all checks passed, False otherwise
        """
        results = self.validate(chunks, original_text)

        all_passed = True

        print("=" * 70)
        print("REGRESSION VALIDATION REPORT")
        print("=" * 70)

        for bug_id, (passed, message) in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"\n{status} - {bug_id}")
            print(f"  {message}")

            if not passed:
                all_passed = False

        print("\n" + "=" * 70)
        if all_passed:
            print("ALL CHECKS PASSED - No regressions detected")
        else:
            print("SOME CHECKS FAILED - Regressions detected!")
        print("=" * 70)

        return all_passed


def validate_no_regression(chunks: List[Chunk], original_text: str) -> bool:
    """
    Convenience function to validate no regressions.

    Args:
        chunks: Generated chunks
        original_text: Original markdown text

    Returns:
        True if no regressions detected, False otherwise
    """
    validator = RegressionValidator()
    results = validator.validate(chunks, original_text)

    return all(passed for passed, _ in results.values())
