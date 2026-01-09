"""Tests for URL detection in hierarchy builder.

Tests the _is_url_line() method used to prevent URL duplication
in root node summaries.
"""

from markdown_chunker_v2.hierarchy import HierarchyBuilder


class TestURLDetection:
    """Test URL line detection."""

    def setup_method(self):
        """Setup test fixtures."""
        self.builder = HierarchyBuilder()

    def test_direct_url_start_http(self):
        """Lines starting with http:// are detected as URLs."""
        assert self.builder._is_url_line("http://example.com")
        assert self.builder._is_url_line("http://example.com/path")
        assert self.builder._is_url_line("  http://example.com  ")

    def test_direct_url_start_https(self):
        """Lines starting with https:// are detected as URLs."""
        assert self.builder._is_url_line("https://example.com")
        assert self.builder._is_url_line("https://example.com/path?query=1")

    def test_label_colon_url_pattern(self):
        """Label: URL pattern is detected."""
        assert self.builder._is_url_line("Documentation: https://example.com")
        assert self.builder._is_url_line("Source: http://github.com/repo")
        assert self.builder._is_url_line(
            "Основная матрица: https://wiki.example.com/pages/viewpage.action"
        )

    def test_url_dominance_check(self):
        """Lines where URL takes >60% are detected."""
        # URL takes majority of line
        assert self.builder._is_url_line(
            "See https://example.com/very/long/path/to/resource"
        )

    def test_non_url_lines(self):
        """Non-URL lines are not detected as URLs."""
        assert not self.builder._is_url_line("This is regular text")
        assert not self.builder._is_url_line("No URL here at all")
        assert not self.builder._is_url_line("")
        assert not self.builder._is_url_line("   ")

    def test_url_in_middle_short_text(self):
        """URL in middle of text with more non-URL content is not detected."""
        # URL exists but is <60% of content
        line = "This is a long sentence with http://example.com embedded in middle"
        assert not self.builder._is_url_line(line)

    def test_multiple_words_before_url(self):
        """Lines with substantial text before URL are not detected."""
        line = "Here is some meaningful content and then https://example.com"
        # This should not be detected as URL-dominant if text is substantial
        assert not self.builder._is_url_line(line)

    def test_edge_case_just_url_text(self):
        """URLs without protocol are not detected."""
        assert not self.builder._is_url_line("example.com")
        assert not self.builder._is_url_line("www.example.com")

    def test_colon_without_url(self):
        """Colon pattern without actual URL is not detected."""
        assert not self.builder._is_url_line("Label: some text")
        assert not self.builder._is_url_line("Title: Description")

    def test_url_at_end_with_text(self):
        """Mixed content with URL at end, if URL dominates."""
        # URL takes >60%
        short_url_line = "See https://example.com/path"
        # URL portion: 27 chars, total: 31 chars = 87% > 60%
        assert self.builder._is_url_line(short_url_line)

    def test_russian_text_with_url(self):
        """Russian text label with URL is detected."""
        assert self.builder._is_url_line(
            "Матрица для Тимлидов: https://wiki.example.com/display/ITCAREER/IT+Manager"
        )

    def test_url_with_hash_fragment(self):
        """URLs with hash fragments are detected."""
        assert self.builder._is_url_line(
            "https://wiki.example.com/pages/viewpage.action?pageId=759187309#section"
        )

    def test_empty_line(self):
        """Empty lines are not detected as URLs."""
        assert not self.builder._is_url_line("")
        assert not self.builder._is_url_line("  ")
        assert not self.builder._is_url_line("\t")
