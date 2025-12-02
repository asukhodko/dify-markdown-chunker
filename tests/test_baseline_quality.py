"""Baseline tests for current chunking behavior.

These tests capture the current output for regression detection
during the block-based chunking improvements.
"""

import json
import pathlib
from typing import Any, List

import pytest

from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig
from tests.quality_metrics import MetricsCalculator

# Test fixtures directory
FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures" / "real_documents"


class TestBaseline:
    """Baseline tests to capture current behavior."""

    def setup_method(self):
        """Set up test configuration."""
        self.config = ChunkConfig(max_chunk_size=1000, overlap_size=200)
        self.chunker = MarkdownChunker(self.config)
        self.metrics_calc = MetricsCalculator(max_chunk_size=1000)

    def _load_fixture(self, filename: str) -> str:
        """Load test fixture content."""
        filepath = FIXTURES_DIR / filename
        return filepath.read_text()

    def _extract_chunks_list(self, result: Any) -> List:
        """Extract chunks from result."""
        if isinstance(result, dict) and "chunks" in result:
            return result["chunks"]
        elif isinstance(result, list):
            return result
        return []

    def test_baseline_career_matrix(self):
        """Baseline test for career matrix document (MC-001 primary test doc).

        This test captures the current chunking behavior for the career matrix
        document that was used in manual testing. Results provide baseline
        for measuring improvements.
        """
        content = self._load_fixture("career_matrix.md")

        # Chunk with current implementation
        result = self.chunker.chunk(
            content,
            strategy=None,  # Auto-select
            include_analysis=True,
            return_format="dict",
        )

        chunks = self._extract_chunks_list(result)

        # Capture baseline metrics
        metrics = self.metrics_calc.calculate_metrics(chunks, content)

        # Document baseline metrics
        baseline_data = {
            "document": "career_matrix.md",
            "config": {
                "max_chunk_size": self.config.max_chunk_size,
                "overlap_size": self.config.overlap_size,
            },
            "metrics": metrics.to_dict(),
            "chunk_count": len(chunks),
        }

        # Print baseline for documentation
        print("\n=== Baseline Metrics: Career Matrix ===")
        print(json.dumps(baseline_data, indent=2))

        # Basic assertions (should pass with current code)
        assert len(chunks) > 0, "Should produce chunks"
        assert all(
            len(self._get_content(c)) <= 1200 for c in chunks
        ), "Chunks should respect size limits (with 20% tolerance)"

    def test_baseline_api_documentation(self):
        """Baseline test for API documentation (MC-002 test: code blocks, tables).

        Tests structural element handling in current implementation.
        """
        content = self._load_fixture("api_documentation.md")

        result = self.chunker.chunk(
            content, strategy=None, include_analysis=True, return_format="dict"
        )

        chunks = self._extract_chunks_list(result)
        metrics = self.metrics_calc.calculate_metrics(chunks, content)

        baseline_data = {
            "document": "api_documentation.md",
            "config": {
                "max_chunk_size": self.config.max_chunk_size,
                "overlap_size": self.config.overlap_size,
            },
            "metrics": metrics.to_dict(),
            "chunk_count": len(chunks),
        }

        print("\n=== Baseline Metrics: API Documentation ===")
        print(json.dumps(baseline_data, indent=2))

        assert len(chunks) > 0

    def test_baseline_technical_spec(self):
        """Baseline test for technical specification (MC-006 test: hierarchy).

        Tests header path metadata in current implementation.
        """
        content = self._load_fixture("technical_spec.md")

        result = self.chunker.chunk(
            content, strategy=None, include_analysis=True, return_format="dict"
        )

        chunks = self._extract_chunks_list(result)
        metrics = self.metrics_calc.calculate_metrics(chunks, content)

        baseline_data = {
            "document": "technical_spec.md",
            "config": {
                "max_chunk_size": self.config.max_chunk_size,
                "overlap_size": self.config.overlap_size,
            },
            "metrics": metrics.to_dict(),
            "chunk_count": len(chunks),
        }

        print("\n=== Baseline Metrics: Technical Specification ===")
        print(json.dumps(baseline_data, indent=2))

        assert len(chunks) > 0

    def test_baseline_metrics_documented(self):
        """Test that baseline metrics can be calculated for all fixtures.

        This ensures the metrics calculation infrastructure works correctly.
        """
        fixtures = ["career_matrix.md", "api_documentation.md", "technical_spec.md"]

        all_metrics = {}

        for fixture in fixtures:
            try:
                content = self._load_fixture(fixture)
                result = self.chunker.chunk(
                    content, strategy=None, include_analysis=True, return_format="dict"
                )

                chunks = self._extract_chunks_list(result)
                metrics = self.metrics_calc.calculate_metrics(chunks, content)

                all_metrics[fixture] = metrics.to_dict()

            except Exception as e:
                pytest.fail(f"Failed to calculate metrics for {fixture}: {e}")

        # Verify all metrics calculated
        assert len(all_metrics) == len(fixtures)

        # Print summary
        print("\n=== Baseline Metrics Summary ===")
        for fixture, metrics in all_metrics.items():
            print(f"\n{fixture}:")
            print(f"  Section completeness: {metrics['section_completeness_rate']:.2%}")
            print(
                f"  Structural integrity: {metrics['structural_element_integrity']:.2%}"
            )
            print(f"  Overlap integrity: {metrics['overlap_block_integrity']:.2%}")
            print(f"  Size CV: {metrics['chunk_size_cv']:.3f}")
            print(f"  URL pool preservation: {metrics['url_pool_preservation']:.2%}")
            print(
                f"  Header path completeness: {metrics['header_path_completeness']:.2%}"
            )

    def _get_content(self, chunk: Any) -> str:
        """Extract content from chunk."""
        if isinstance(chunk, dict):
            return chunk.get("content", "")
        return getattr(chunk, "content", "")


class TestBaselineSnapshot:
    """Snapshot tests to detect unexpected changes."""

    def setup_method(self):
        """Set up test configuration."""
        self.config = ChunkConfig(max_chunk_size=1000, overlap_size=200)
        self.chunker = MarkdownChunker(self.config)

    def test_simple_document_structure_preserved(self):
        """Test that simple document structure is preserved.

        This test ensures basic chunking behavior doesn't regress.
        """
        content = """# Main Header

## Section 1

This is section 1 content with some text.

## Section 2

This is section 2 content with more text.

### Subsection 2.1

Subsection content here.
"""

        result = self.chunker.chunk(
            content, strategy=None, include_analysis=True, return_format="dict"
        )

        chunks = result.get("chunks", []) if isinstance(result, dict) else result

        # Basic structure checks
        assert len(chunks) > 0, "Should produce chunks"

        # Check that headers appear in chunks
        all_content = "\n".join(
            c.get("content", "") if isinstance(c, dict) else c.content for c in chunks
        )
        assert "# Main Header" in all_content or "Main Header" in all_content
        assert "Section 1" in all_content
        assert "Section 2" in all_content

    def test_code_block_detection(self):
        """Test that code blocks are detected.

        Baseline for MC-002 fix.
        """
        content = """# Code Example

Here's some code:

```python
def hello():
    print("Hello, world!")
```

More text after code.
"""

        result = self.chunker.chunk(
            content, strategy=None, include_analysis=True, return_format="dict"
        )

        chunks = result.get("chunks", []) if isinstance(result, dict) else result

        assert len(chunks) > 0

        # Check if code appears somewhere
        all_content = "\n".join(
            c.get("content", "") if isinstance(c, dict) else c.content for c in chunks
        )
        assert "def hello" in all_content or "print" in all_content

    def test_list_detection(self):
        """Test that lists are detected.

        Baseline for MC-002 fix.
        """
        content = """# Lists

Here are some items:

- Item 1
- Item 2
- Item 3

End of list.
"""

        result = self.chunker.chunk(
            content, strategy=None, include_analysis=True, return_format="dict"
        )

        chunks = result.get("chunks", []) if isinstance(result, dict) else result

        assert len(chunks) > 0

        all_content = "\n".join(
            c.get("content", "") if isinstance(c, dict) else c.content for c in chunks
        )
        assert "Item 1" in all_content
        assert "Item 2" in all_content
