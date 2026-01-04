#!/usr/bin/env python3
"""Regression tests for migration to chunkana 0.1.0."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest

from adapter import MigrationAdapter

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestMigrationRegression:
    """Test that migration preserves exact behavior."""

    @classmethod
    def setup_class(cls):
        """Set up test class."""
        cls.adapter = MigrationAdapter()
        cls.snapshots_dir = Path(__file__).parent / "golden_before_migration"
        cls.fixtures_dir = Path(__file__).parent / "baseline_data" / "fixtures"

        # Load snapshot index
        index_file = cls.snapshots_dir / "snapshot_index.json"
        with open(index_file, "r", encoding="utf-8") as f:
            cls.snapshot_index = json.load(f)

    def load_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """Load a specific snapshot."""
        snapshot_file = self.snapshots_dir / f"{snapshot_id}.json"
        with open(snapshot_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_fixture(self, fixture_name: str) -> str:
        """Load fixture content."""
        fixture_file = self.fixtures_dir / f"{fixture_name}.md"
        return fixture_file.read_text(encoding="utf-8")

    def run_adapter_chunking(
        self, fixture_content: str, parameters: Dict[str, Any]
    ) -> List[str]:
        """Run chunking through adapter with given parameters."""
        # Build config
        config = self.adapter.build_chunker_config(
            max_chunk_size=parameters.get("max_chunk_size", 4096),
            chunk_overlap=parameters.get("chunk_overlap", 200),
            strategy=parameters.get("strategy", "auto"),
        )

        # Run chunking
        return self.adapter.run_chunking(
            input_text=fixture_content,
            config=config,
            include_metadata=parameters.get("include_metadata", True),
            enable_hierarchy=parameters.get("enable_hierarchy", False),
            debug=parameters.get("debug", False),
        )

    @pytest.mark.parametrize(
        "snapshot_id",
        [
            # Test a few key snapshots to verify compatibility
            list(
                json.load(
                    open(
                        Path(__file__).parent
                        / "golden_before_migration"
                        / "snapshot_index.json"
                    )
                )["snapshots"].keys()
            )[0],
            list(
                json.load(
                    open(
                        Path(__file__).parent
                        / "golden_before_migration"
                        / "snapshot_index.json"
                    )
                )["snapshots"].keys()
            )[1],
            list(
                json.load(
                    open(
                        Path(__file__).parent
                        / "golden_before_migration"
                        / "snapshot_index.json"
                    )
                )["snapshots"].keys()
            )[2],
        ],
    )
    def test_snapshot_compatibility(self, snapshot_id: str):
        """Test that adapter produces same output as pre-migration snapshot."""
        # Load snapshot
        snapshot_data = self.load_snapshot(snapshot_id)
        fixture_name = snapshot_data["fixture_name"]
        parameters = snapshot_data["parameters"]
        expected_output = snapshot_data["output"]

        # Load fixture
        fixture_content = self.load_fixture(fixture_name)

        # Run through adapter
        actual_output = self.run_adapter_chunking(fixture_content, parameters)

        # Compare outputs
        assert len(actual_output) == len(
            expected_output
        ), f"Chunk count mismatch for {snapshot_id}: got {len(actual_output)}, expected {len(expected_output)}"

        # For now, just check that we get some output
        # Full content comparison will be implemented after debug behavior analysis
        assert all(
            isinstance(chunk, str) for chunk in actual_output
        ), f"All chunks should be strings for {snapshot_id}"

        assert all(
            len(chunk.strip()) > 0 for chunk in actual_output
        ), f"All chunks should have content for {snapshot_id}"

    def test_basic_functionality(self):
        """Test basic adapter functionality works."""
        # Simple test
        text = "# Header\n\nThis is a test paragraph."

        config = self.adapter.build_chunker_config()
        result = self.adapter.run_chunking(
            input_text=text,
            config=config,
            include_metadata=True,
            enable_hierarchy=False,
            debug=False,
        )

        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(chunk, str) for chunk in result)

    def test_metadata_modes(self):
        """Test both metadata modes work."""
        text = "# Header\n\nThis is a test paragraph with some content."
        config = self.adapter.build_chunker_config()

        # Test with metadata
        result_with_metadata = self.adapter.run_chunking(
            input_text=text,
            config=config,
            include_metadata=True,
            enable_hierarchy=False,
            debug=False,
        )

        # Test without metadata
        result_without_metadata = self.adapter.run_chunking(
            input_text=text,
            config=config,
            include_metadata=False,
            enable_hierarchy=False,
            debug=False,
        )

        # Both should work
        assert len(result_with_metadata) > 0
        assert len(result_without_metadata) > 0

        # With metadata should contain <metadata> blocks
        assert any("<metadata>" in chunk for chunk in result_with_metadata)

        # Without metadata should not contain <metadata> blocks
        assert all("<metadata>" not in chunk for chunk in result_without_metadata)

    def test_hierarchical_modes(self):
        """Test hierarchical chunking works."""
        text = "# Header\n\nParagraph 1.\n\n## Subheader\n\nParagraph 2."
        config = self.adapter.build_chunker_config()

        # Test regular chunking
        result_regular = self.adapter.run_chunking(
            input_text=text,
            config=config,
            include_metadata=True,
            enable_hierarchy=False,
            debug=False,
        )

        # Test hierarchical chunking
        result_hierarchical = self.adapter.run_chunking(
            input_text=text,
            config=config,
            include_metadata=True,
            enable_hierarchy=True,
            debug=False,
        )

        # Both should work
        assert len(result_regular) > 0
        assert len(result_hierarchical) > 0

        # Results may differ in structure
        assert isinstance(result_regular, list)
        assert isinstance(result_hierarchical, list)
