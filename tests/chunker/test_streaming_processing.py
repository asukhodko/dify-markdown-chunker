"""
Unit tests for streaming processing components.

Tests buffer management, fence tracking, and split detection.
"""

import io

from markdown_chunker_v2.streaming import StreamingConfig
from markdown_chunker_v2.streaming.buffer_manager import BufferManager
from markdown_chunker_v2.streaming.fence_tracker import FenceTracker
from markdown_chunker_v2.streaming.split_detector import SplitDetector


class TestFenceTracker:
    """Test fence tracking across lines."""

    def test_no_fence(self):
        """Test with no fences."""
        tracker = FenceTracker()
        tracker.track_line("regular text")
        assert not tracker.is_inside_fence()

    def test_opening_fence(self):
        """Test fence opening detection."""
        tracker = FenceTracker()
        tracker.track_line("```python")
        assert tracker.is_inside_fence()
        info = tracker.get_fence_info()
        assert info == ("`", 3)

    def test_fence_pair(self):
        """Test matched fence pair."""
        tracker = FenceTracker()
        tracker.track_line("```python")
        assert tracker.is_inside_fence()
        tracker.track_line("```")
        assert not tracker.is_inside_fence()

    def test_tilde_fence(self):
        """Test tilde fencing."""
        tracker = FenceTracker()
        tracker.track_line("~~~")
        assert tracker.is_inside_fence()
        tracker.track_line("~~~")
        assert not tracker.is_inside_fence()

    def test_nested_fence_longer(self):
        """Test nested fence with longer closing."""
        tracker = FenceTracker()
        tracker.track_line("```")
        assert tracker.is_inside_fence()
        tracker.track_line("````")
        assert not tracker.is_inside_fence()

    def test_reset(self):
        """Test fence state reset."""
        tracker = FenceTracker()
        tracker.track_line("```")
        tracker.reset()
        assert not tracker.is_inside_fence()


class TestSplitDetector:
    """Test safe split point detection."""

    def test_split_at_header(self):
        """Test split before header."""
        detector = SplitDetector(threshold=0.5)
        tracker = FenceTracker()
        buffer = ["line1\n", "line2\n", "line3\n", "# Header\n", "line5\n"]
        idx = detector.find_split_point(buffer, tracker)
        assert idx == 3  # Before header

    def test_split_at_paragraph(self):
        """Test split at paragraph boundary."""
        detector = SplitDetector(threshold=0.5)
        tracker = FenceTracker()
        buffer = ["line1\n", "line2\n", "\n", "line4\n", "line5\n"]
        idx = detector.find_split_point(buffer, tracker)
        assert idx == 3  # After empty line

    def test_fallback_split(self):
        """Test fallback split when no boundary found."""
        detector = SplitDetector(threshold=0.8)
        tracker = FenceTracker()
        buffer = ["line\n"] * 10
        idx = detector.find_split_point(buffer, tracker)
        assert idx == 8  # 80% of 10


class TestBufferManager:
    """Test buffer window management."""

    def test_single_window(self):
        """Test single small buffer."""
        config = StreamingConfig(buffer_size=100)
        manager = BufferManager(config)
        stream = io.StringIO("line1\nline2\nline3\n")

        windows = list(manager.read_windows(stream))
        assert len(windows) == 1
        buffer, overlap, _ = windows[0]
        assert len(buffer) == 3
        assert len(overlap) == 0

    def test_multiple_windows(self):
        """Test multiple buffer windows."""
        config = StreamingConfig(buffer_size=20, overlap_lines=1)
        manager = BufferManager(config)
        # Each line is ~10 chars, so 20 bytes = ~2 lines per window
        stream = io.StringIO("line1\n" * 10)

        windows = list(manager.read_windows(stream))
        assert len(windows) > 1

    def test_overlap_preserved(self):
        """Test overlap between windows."""
        config = StreamingConfig(buffer_size=20, overlap_lines=2)
        manager = BufferManager(config)
        stream = io.StringIO("line1\nline2\nline3\nline4\n")

        windows = list(manager.read_windows(stream))
        if len(windows) > 1:
            _, overlap, _ = windows[1]
            assert len(overlap) > 0


class TestStreamingIntegration:
    """Integration tests for streaming components."""

    def test_fence_not_split(self):
        """Verify fences prevent splits."""
        tracker = FenceTracker()

        buffer = ["text\n", "```\n", "code\n", "more code\n", "```\n", "text\n"]

        # Track all lines
        for line in buffer:
            tracker.track_line(line)

        # Fence should be closed
        assert not tracker.is_inside_fence()
