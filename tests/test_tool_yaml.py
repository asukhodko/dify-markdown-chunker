"""Property Tests 10, 11, 12: Tool YAML Validation

Validates: Requirements 3.1-3.7
Ensures tool YAML contains all required fields and valid parameter definitions.
"""

from pathlib import Path

import pytest
import yaml


class TestToolYAML:
    """Property 10, 11, 12: Tool YAML Validation"""

    @pytest.fixture
    def tool_data(self):
        """Load and parse tool YAML."""
        tool_path = Path(__file__).parent.parent / "tools" / "markdown_chunk_tool.yaml"
        assert tool_path.exists(), "tools/markdown_chunk_tool.yaml not found"

        with open(tool_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_identity_present(self, tool_data):
        """Test identity section is present."""
        assert "identity" in tool_data
        identity = tool_data["identity"]

        assert "name" in identity
        assert "author" in identity
        assert "label" in identity
        assert "icon" in identity

        assert identity["name"] == "markdown_chunk_tool"
        assert identity["author"] == "asukhodko"

    def test_description_present(self, tool_data):
        """Test description section is present."""
        assert "description" in tool_data
        description = tool_data["description"]

        assert "human" in description
        assert "llm" in description

    def test_parameter_definitions_completeness(self, tool_data):
        """Property 10: Parameter Definitions Completeness - Test all required parameters."""
        assert "parameters" in tool_data
        parameters = tool_data["parameters"]

        # Get parameter names
        param_names = [p["name"] for p in parameters]

        # Check required parameters
        required_params = [
            "input_text",
            "max_chunk_size",
            "chunk_overlap",
            "strategy",
            "include_metadata",
        ]
        for param in required_params:
            assert param in param_names, f"Required parameter '{param}' missing"

    def test_input_text_parameter(self, tool_data):
        """Property 10: Parameter Definitions Completeness - Test input_text parameter."""
        parameters = tool_data["parameters"]
        input_text = next(p for p in parameters if p["name"] == "input_text")

        assert input_text["type"] == "string"
        assert input_text["required"] is True
        assert input_text["form"] == "llm"

    def test_max_chunk_size_parameter(self, tool_data):
        """Property 10: Parameter Definitions Completeness - Test max_chunk_size parameter."""
        parameters = tool_data["parameters"]
        max_chunk_size = next(p for p in parameters if p["name"] == "max_chunk_size")

        assert max_chunk_size["type"] == "number"
        assert max_chunk_size["required"] is False
        assert max_chunk_size["default"] == 4096

    def test_chunk_overlap_parameter(self, tool_data):
        """Property 10: Parameter Definitions Completeness - Test chunk_overlap parameter."""
        parameters = tool_data["parameters"]
        chunk_overlap = next(p for p in parameters if p["name"] == "chunk_overlap")

        assert chunk_overlap["type"] == "number"
        assert chunk_overlap["required"] is False
        assert chunk_overlap["default"] == 200

    def test_strategy_parameter(self, tool_data):
        """Property 10: Parameter Definitions Completeness - Test strategy parameter."""
        parameters = tool_data["parameters"]
        strategy = next(p for p in parameters if p["name"] == "strategy")

        assert strategy["type"] == "select"
        assert strategy["required"] is False
        assert strategy["default"] == "auto"
        assert "options" in strategy

        # Check options
        option_values = [opt["value"] for opt in strategy["options"]]
        assert "auto" in option_values
        assert "code_aware" in option_values
        assert "structural" in option_values
        assert "fallback" in option_values

    def test_include_metadata_parameter(self, tool_data):
        """Property 10: Parameter Definitions Completeness - Test include_metadata parameter."""
        parameters = tool_data["parameters"]
        include_metadata = next(
            p for p in parameters if p["name"] == "include_metadata"
        )

        assert include_metadata["type"] == "boolean"
        assert include_metadata["required"] is False
        assert include_metadata["default"] is True

    def test_localization_completeness(self, tool_data):
        """Property 12: Localization Completeness - Test all parameters have localization."""
        parameters = tool_data["parameters"]
        required_languages = ["en_US", "zh_Hans", "ru_RU"]

        for param in parameters:
            param_name = param["name"]

            # Check label
            assert "label" in param, f"Parameter '{param_name}' missing label"
            for lang in required_languages:
                assert (
                    lang in param["label"]
                ), f"Parameter '{param_name}' missing label for {lang}"
                assert param["label"][
                    lang
                ], f"Parameter '{param_name}' has empty label for {lang}"

            # Check human_description
            assert (
                "human_description" in param
            ), f"Parameter '{param_name}' missing human_description"
            for lang in required_languages:
                assert (
                    lang in param["human_description"]
                ), f"Parameter '{param_name}' missing human_description for {lang}"
                assert param["human_description"][
                    lang
                ], f"Parameter '{param_name}' has empty human_description for {lang}"

    def test_strategy_options_localization(self, tool_data):
        """Property 12: Localization Completeness - Test strategy options have localization."""
        parameters = tool_data["parameters"]
        strategy = next(p for p in parameters if p["name"] == "strategy")
        required_languages = ["en_US", "zh_Hans", "ru_RU"]

        for option in strategy["options"]:
            option_value = option["value"]
            assert "label" in option, f"Strategy option '{option_value}' missing label"

            for lang in required_languages:
                assert (
                    lang in option["label"]
                ), f"Strategy option '{option_value}' missing label for {lang}"
                assert option["label"][
                    lang
                ], f"Strategy option '{option_value}' has empty label for {lang}"

    def test_output_schema_reference(self, tool_data):
        """Property 11: Output Schema Reference - Test output schema."""
        assert "output_schema" in tool_data
        output_schema = tool_data["output_schema"]

        assert output_schema["type"] == "object"
        assert "properties" in output_schema
        assert "result" in output_schema["properties"]
        assert "$ref" in output_schema["properties"]["result"]
        assert (
            output_schema["properties"]["result"]["$ref"]
            == "https://dify.ai/schemas/v1/general_structure.json"
        )

    def test_python_source_reference(self, tool_data):
        """Test Python source reference."""
        assert "extra" in tool_data
        assert "python" in tool_data["extra"]
        assert "source" in tool_data["extra"]["python"]
        assert tool_data["extra"]["python"]["source"] == "tools/markdown_chunk_tool.py"
