"""Property Test 1: Manifest Completeness

Validates: Requirements 1.2
Ensures manifest.yaml contains all required fields and valid values.
"""

from datetime import datetime
from pathlib import Path

import pytest
import yaml


class TestManifestCompleteness:
    """Property 1: Manifest Completeness"""

    @pytest.fixture
    def manifest_data(self):
        """Load and parse manifest.yaml."""
        manifest_path = Path(__file__).parent.parent / "manifest.yaml"
        assert manifest_path.exists(), "manifest.yaml not found"

        with open(manifest_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_required_fields_present(self, manifest_data):
        """Test that all required fields are present."""
        required_fields = [
            "version",
            "type",
            "author",
            "name",
            "label",
            "description",
            "icon",
            "resource",
            "permission",
            "plugins",
            "meta",
            "minimum_dify_version",
            "tags",
            "created_at",
        ]

        for field in required_fields:
            assert (
                field in manifest_data
            ), f"Required field '{field}' missing from manifest"

    def test_plugin_metadata(self, manifest_data):
        """Test plugin metadata fields."""
        assert manifest_data["type"] == "plugin", "Type must be 'plugin'"
        assert manifest_data["author"] == "asukhodko", "Author should be 'asukhodko'"
        assert (
            manifest_data["name"] == "markdown_chunker"
        ), "Name should be 'markdown_chunker'"

        # Version should start with 2.0.0 (allow pre-release suffixes like -a1, -beta, etc)
        version = manifest_data["version"]
        assert version.startswith(
            "2.0.0"
        ), f"Version should start with '2.0.0', got '{version}'"

    def test_localization_completeness(self, manifest_data):
        """Test that all required languages are present."""
        required_languages = ["en_US", "zh_Hans", "ru_RU"]

        # Check labels
        assert "label" in manifest_data
        for lang in required_languages:
            assert lang in manifest_data["label"], f"Label missing for language {lang}"
            assert manifest_data["label"][lang], f"Label empty for language {lang}"

        # Check descriptions
        assert "description" in manifest_data
        for lang in required_languages:
            assert (
                lang in manifest_data["description"]
            ), f"Description missing for language {lang}"
            assert manifest_data["description"][
                lang
            ], f"Description empty for language {lang}"

    def test_resource_allocation(self, manifest_data):
        """Test resource allocation settings."""
        assert "resource" in manifest_data
        assert "memory" in manifest_data["resource"]

        memory = manifest_data["resource"]["memory"]
        assert isinstance(memory, int), "Memory must be an integer"
        assert memory == 536870912, "Memory should be 512MB (536870912 bytes)"

    def test_runner_configuration(self, manifest_data):
        """Test runner configuration."""
        assert "runner" in manifest_data["meta"]
        runner = manifest_data["meta"]["runner"]

        assert runner["language"] == "python", "Language must be 'python'"
        assert runner["version"] == "3.12", "Python version must be '3.12'"
        assert runner["entrypoint"] == "main", "Entrypoint must be 'main'"

    def test_required_tags(self, manifest_data):
        """Test that tags are present and valid."""
        assert "tags" in manifest_data
        tags = manifest_data["tags"]

        # Tags must be a list with at least one tag
        assert isinstance(tags, list), "Tags should be a list"
        assert len(tags) > 0, "At least one tag should be present"

        # All tags should be strings (CLI validates against standard list)
        for tag in tags:
            assert isinstance(tag, str), f"Tag '{tag}' should be a string"

    def test_provider_reference(self, manifest_data):
        """Test that provider is correctly referenced."""
        assert "plugins" in manifest_data
        assert "tools" in manifest_data["plugins"]

        tools = manifest_data["plugins"]["tools"]
        assert isinstance(tools, list), "Tools must be a list"
        assert len(tools) == 1, "Should have exactly one tool provider"
        assert tools[0] == "provider/markdown_chunker.yaml", "Provider path incorrect"

    def test_architecture_support(self, manifest_data):
        """Test architecture support."""
        assert "meta" in manifest_data
        assert "arch" in manifest_data["meta"]

        arch = manifest_data["meta"]["arch"]
        assert isinstance(arch, list), "Architecture must be a list"
        assert "amd64" in arch, "Must support amd64 architecture"
        assert "arm64" in arch, "Must support arm64 architecture"

    def test_dify_version_requirement(self, manifest_data):
        """Test minimum Dify version requirement."""
        assert "minimum_dify_version" in manifest_data
        min_version = manifest_data["minimum_dify_version"]
        assert min_version == "1.9.0", "Minimum Dify version should be 1.9.0"

    def test_created_at_format(self, manifest_data):
        """Test that created_at is in valid RFC3339 format."""
        assert "created_at" in manifest_data
        created_at = manifest_data["created_at"]

        # created_at can be either string or datetime object from YAML
        if isinstance(created_at, datetime):
            # Already parsed by YAML, that's fine
            return

        # If it's a string, try to parse as ISO format
        assert isinstance(
            created_at, str
        ), f"created_at must be string or datetime, got {type(created_at)}"
        try:
            datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except ValueError as e:
            pytest.fail(
                f"created_at '{created_at}' is not in valid RFC3339 format: {e}"
            )

    def test_icon_reference(self, manifest_data):
        """Test icon reference.

        Note: Icon path should be just the filename (icon.svg), not the full path.
        Dify/CLI automatically looks for icons in _assets/ directory.
        """
        assert "icon" in manifest_data
        assert (
            manifest_data["icon"] == "icon.svg"
        ), "Icon should be 'icon.svg' (without _assets/ prefix)"

    def test_permissions_configuration(self, manifest_data):
        """Test permissions are correctly configured."""
        assert "permission" in manifest_data
        permission = manifest_data["permission"]

        # Tool permission should be disabled (we're a tool provider, not consumer)
        assert "tool" in permission
        assert permission["tool"]["enabled"] is False

        # Model permission should be disabled (we don't use models)
        assert "model" in permission
        assert permission["model"]["enabled"] is False
