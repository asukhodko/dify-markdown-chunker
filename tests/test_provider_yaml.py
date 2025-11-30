"""Property Tests 5, 6, 7: Provider YAML Completeness

Validates: Requirements 2.1, 2.2, 2.3
Ensures provider YAML contains all required fields and valid values.
"""

from pathlib import Path

import pytest
import yaml


class TestProviderYAML:
    """Property 5, 6, 7: Provider YAML Completeness"""

    @pytest.fixture
    def provider_data(self):
        """Load and parse provider YAML."""
        provider_path = (
            Path(__file__).parent.parent / "provider" / "markdown_chunker.yaml"
        )
        assert provider_path.exists(), "provider/markdown_chunker.yaml not found"

        with open(provider_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_identity_completeness(self, provider_data):
        """Property 5: Provider Identity Completeness - Test identity section."""
        assert "identity" in provider_data
        identity = provider_data["identity"]

        # Check required fields
        assert "author" in identity
        assert "name" in identity
        assert "label" in identity
        assert "description" in identity
        assert "icon" in identity

        # Check values
        assert identity["author"] == "asukhodko"
        assert identity["name"] == "markdown_chunker"
        assert (
            identity["icon"] == "icon.svg"
        ), "Icon should be 'icon.svg' (without _assets/ prefix)"

    def test_localization_completeness(self, provider_data):
        """Property 5: Provider Identity Completeness - Test localization."""
        identity = provider_data["identity"]
        required_languages = ["en_US", "zh_Hans", "ru_RU"]

        # Check labels
        for lang in required_languages:
            assert lang in identity["label"], f"Label missing for language {lang}"
            assert identity["label"][lang], f"Label empty for language {lang}"

        # Check descriptions
        for lang in required_languages:
            assert (
                lang in identity["description"]
            ), f"Description missing for language {lang}"
            assert identity["description"][
                lang
            ], f"Description empty for language {lang}"

    def test_tags_presence(self, provider_data):
        """Property 6: Provider Tags Presence - Test required tags."""
        assert "identity" in provider_data
        assert "tags" in provider_data["identity"]

        tags = provider_data["identity"]["tags"]
        assert isinstance(tags, list), "Tags must be a list"
        assert len(tags) > 0, "At least one tag should be present"

        # All tags should be strings (CLI validates against standard list)
        for tag in tags:
            assert isinstance(tag, str), f"Tag '{tag}' should be a string"

    def test_tool_reference(self, provider_data):
        """Property 7: Provider Tool Reference - Test tool reference."""
        assert "tools" in provider_data
        tools = provider_data["tools"]

        assert isinstance(tools, list), "Tools must be a list"
        assert len(tools) >= 1, "Should have at least one tool"
        assert "tools/markdown_chunk_tool.yaml" in tools, "Tool reference incorrect"

    def test_python_source_reference(self, provider_data):
        """Test Python source reference."""
        assert "extra" in provider_data
        assert "python" in provider_data["extra"]
        assert "source" in provider_data["extra"]["python"]

        source = provider_data["extra"]["python"]["source"]
        assert source == "provider/markdown_chunker.py", "Python source path incorrect"
