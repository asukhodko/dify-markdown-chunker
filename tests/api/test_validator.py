"""Tests for API validator refactored methods."""

from markdown_chunker.api import APIValidator


class TestAPIValidatorRefactored:
    """Test refactored validator methods for C901 compliance."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = APIValidator()

    def test_validate_chunk_sizes_valid_max_size(self):
        """Test validation accepts valid max_chunk_size."""
        config = {"max_chunk_size": 5000}
        errors = []

        self.validator._validate_chunk_sizes(config, errors)

        assert len(errors) == 0

    def test_validate_chunk_sizes_invalid_max_size_type(self):
        """Test validation rejects non-integer max_chunk_size."""
        config = {"max_chunk_size": "5000"}
        errors = []

        self.validator._validate_chunk_sizes(config, errors)

        assert len(errors) == 1
        assert "max_chunk_size" in errors[0].field
        assert "integer" in errors[0].message.lower()

    def test_validate_chunk_sizes_max_size_too_small(self):
        """Test validation rejects max_chunk_size below minimum."""
        config = {"max_chunk_size": 5}  # Below MIN_CHUNK_SIZE (10)
        errors = []

        self.validator._validate_chunk_sizes(config, errors)

        assert len(errors) == 1
        assert "max_chunk_size" in errors[0].field

    def test_validate_chunk_sizes_max_size_too_large(self):
        """Test validation rejects max_chunk_size above maximum."""
        config = {"max_chunk_size": 200000}  # Above MAX_CHUNK_SIZE (100000)
        errors = []

        self.validator._validate_chunk_sizes(config, errors)

        assert len(errors) == 1
        assert "max_chunk_size" in errors[0].field

    def test_validate_chunk_sizes_valid_min_size(self):
        """Test validation accepts valid min_chunk_size."""
        config = {"min_chunk_size": 100}
        errors = []

        self.validator._validate_chunk_sizes(config, errors)

        assert len(errors) == 0

    def test_validate_chunk_sizes_invalid_min_size_type(self):
        """Test validation rejects non-integer min_chunk_size."""
        config = {"min_chunk_size": "100"}
        errors = []

        self.validator._validate_chunk_sizes(config, errors)

        assert len(errors) == 1
        assert "min_chunk_size" in errors[0].field
        assert "integer" in errors[0].message.lower()

    def test_validate_chunk_sizes_min_size_too_small(self):
        """Test validation rejects min_chunk_size below minimum."""
        config = {"min_chunk_size": 5}  # Below MIN_CHUNK_SIZE (10)
        errors = []

        self.validator._validate_chunk_sizes(config, errors)

        assert len(errors) == 1
        assert "min_chunk_size" in errors[0].field

    def test_validate_chunk_sizes_min_greater_than_max(self):
        """Test validation rejects min_chunk_size > max_chunk_size."""
        config = {"min_chunk_size": 5000, "max_chunk_size": 1000}
        errors = []

        self.validator._validate_chunk_sizes(config, errors)

        assert len(errors) >= 1
        # Should have error about relationship
        assert any(
            "min_chunk_size" in err.message.lower()
            and "max_chunk_size" in err.message.lower()
            for err in errors
        )

    def test_validate_chunk_sizes_valid_relationship(self):
        """Test validation accepts valid min/max relationship."""
        config = {"min_chunk_size": 100, "max_chunk_size": 5000}
        errors = []

        self.validator._validate_chunk_sizes(config, errors)

        assert len(errors) == 0

    def test_validate_overlap_valid_size(self):
        """Test validation accepts valid overlap_size."""
        config = {"overlap_size": 100}
        errors = []

        self.validator._validate_overlap(config, errors)

        assert len(errors) == 0

    def test_validate_overlap_invalid_type(self):
        """Test validation rejects non-integer overlap_size."""
        config = {"overlap_size": "100"}
        errors = []

        self.validator._validate_overlap(config, errors)

        assert len(errors) == 1
        assert "overlap_size" in errors[0].field
        assert "integer" in errors[0].message.lower()

    def test_validate_overlap_negative_value(self):
        """Test validation rejects negative overlap_size."""
        config = {"overlap_size": -50}
        errors = []

        self.validator._validate_overlap(config, errors)

        assert len(errors) == 1
        assert "overlap_size" in errors[0].field
        assert "negative" in errors[0].message.lower()

    def test_validate_overlap_zero_value(self):
        """Test validation accepts zero overlap_size."""
        config = {"overlap_size": 0}
        errors = []

        self.validator._validate_overlap(config, errors)

        assert len(errors) == 0


class TestAPIValidatorIntegration:
    """Integration tests for validator with refactored methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = APIValidator()

    def test_validate_config_calls_chunk_sizes(self):
        """Test validate_config properly calls _validate_chunk_sizes."""
        config = {"max_chunk_size": 5000, "min_chunk_size": 100}

        errors = self.validator.validate_config(config)

        assert len(errors) == 0

    def test_validate_config_calls_overlap(self):
        """Test validate_config properly calls _validate_overlap."""
        config = {"overlap_size": 100}

        errors = self.validator.validate_config(config)

        assert len(errors) == 0

    def test_validate_config_accumulates_errors(self):
        """Test validate_config accumulates errors from all validators."""
        config = {
            "max_chunk_size": "invalid",  # Type error
            "min_chunk_size": 5,  # Too small
            "overlap_size": -10,  # Negative
        }

        errors = self.validator.validate_config(config)

        # Should have multiple errors
        assert len(errors) >= 3

    def test_validate_config_empty_config(self):
        """Test validate_config handles empty config."""
        config = {}

        errors = self.validator.validate_config(config)

        assert len(errors) == 0

    def test_validate_config_complex_invalid_config(self):
        """Test validate_config with multiple invalid fields."""
        config = {
            "max_chunk_size": 5,  # Too small
            "min_chunk_size": 10000,  # Greater than max
            "overlap_size": "not_a_number",  # Wrong type
        }

        errors = self.validator.validate_config(config)

        # Should catch all errors
        assert len(errors) >= 2
        assert any("max_chunk_size" in err.field for err in errors)
        assert any("overlap_size" in err.field for err in errors)


class TestValidatorComplexity:
    """Tests to ensure refactored methods maintain low complexity."""

    def test_validate_chunk_sizes_single_responsibility(self):
        """Test _validate_chunk_sizes focuses on chunk size validation only."""
        validator = APIValidator()
        config = {"max_chunk_size": 5000, "overlap_size": 100}
        errors = []

        # Should only validate chunk sizes, not overlap
        validator._validate_chunk_sizes(config, errors)

        # No errors for overlap_size (that's handled elsewhere)
        assert len(errors) == 0

    def test_validate_overlap_single_responsibility(self):
        """Test _validate_overlap focuses on overlap validation only."""
        validator = APIValidator()
        config = {"overlap_size": 100, "max_chunk_size": 5000}
        errors = []

        # Should only validate overlap, not chunk sizes
        validator._validate_overlap(config, errors)

        # No errors for max_chunk_size (that's handled elsewhere)
        assert len(errors) == 0

    def test_methods_are_independent(self):
        """Test refactored methods can be called independently."""
        validator = APIValidator()

        # Test chunk sizes independently
        errors1 = []
        validator._validate_chunk_sizes({"max_chunk_size": 5000}, errors1)
        assert len(errors1) == 0

        # Test overlap independently
        errors2 = []
        validator._validate_overlap({"overlap_size": 100}, errors2)
        assert len(errors2) == 0

        # Errors lists are independent
        assert errors1 is not errors2
