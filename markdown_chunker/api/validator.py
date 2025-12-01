"""
API validator for request validation.

Validates API requests before processing.
"""

from typing import Any, Dict, List

from markdown_chunker.api.types import APIError, APIRequest


class APIValidator:
    """
    Validator for API requests.

    Validates content, configuration, and strategy parameters.
    """

    # Validation limits
    MAX_CONTENT_SIZE = 10 * 1024 * 1024  # 10MB
    MIN_CONTENT_SIZE = 1
    MAX_CHUNK_SIZE = 100000
    MIN_CHUNK_SIZE = 10

    VALID_STRATEGIES = [
        "auto",
        "code",
        "mixed",
        "list",
        "table",
        "structural",
        "sentences",
    ]

    def __init__(
        self,
        max_content_size: int = MAX_CONTENT_SIZE,
        min_content_size: int = MIN_CONTENT_SIZE,
    ):
        """
        Initialize validator.

        Args:
            max_content_size: Maximum allowed content size in bytes
            min_content_size: Minimum allowed content size in bytes
        """
        self.max_content_size = max_content_size
        self.min_content_size = min_content_size

    def validate_request(self, request: APIRequest) -> List[APIError]:
        """
        Validate API request.

        Args:
            request: API request to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Validate content
        errors.extend(self.validate_content(request.content))

        # Validate config if provided
        if request.config:
            errors.extend(self.validate_config(request.config))

        # Validate strategy if provided
        if request.strategy:
            errors.extend(self.validate_strategy(request.strategy))

        return errors

    def validate_content(self, content: str) -> List[APIError]:
        """
        Validate content field.

        Args:
            content: Content to validate

        Returns:
            List of validation errors
        """
        errors = []

        # Check if content exists
        if content is None:
            errors.append(APIError.validation_error("content", "Content is required"))
            return errors

        # Check if content is string
        if not isinstance(content, str):
            errors.append(
                APIError.validation_error(
                    "content", f"Content must be a string, got {type(content).__name__}"
                )
            )
            return errors

        # Check content size
        content_size = len(content.encode("utf-8"))

        if content_size < self.min_content_size:
            errors.append(
                APIError.validation_error(
                    "content",
                    f"Content is too small (minimum {self.min_content_size} bytes)",
                )
            )

        if content_size > self.max_content_size:
            errors.append(
                APIError.validation_error(
                    "content",
                    f"Content is too large (maximum "
                    f"{self.max_content_size} bytes, got {content_size})",
                )
            )

        # Check if content is not just whitespace
        if not content.strip():
            errors.append(
                APIError.validation_error(
                    "content", "Content cannot be empty or whitespace-only"
                )
            )

        return errors

    def _validate_chunk_sizes(
        self, config: Dict[str, Any], errors: List[APIError]
    ) -> None:
        """Validate chunk size parameters."""
        # Validate max_chunk_size
        if "max_chunk_size" in config:
            max_size = config["max_chunk_size"]
            if not isinstance(max_size, int):
                errors.append(
                    APIError.validation_error(
                        "config.max_chunk_size",
                        f"max_chunk_size must be integer, "
                        f"got {type(max_size).__name__}",
                    )
                )
            elif max_size < self.MIN_CHUNK_SIZE or max_size > self.MAX_CHUNK_SIZE:
                errors.append(
                    APIError.validation_error(
                        "config.max_chunk_size",
                        f"max_chunk_size must be between "
                        f"{self.MIN_CHUNK_SIZE} and {self.MAX_CHUNK_SIZE}",
                    )
                )

        # Validate min_chunk_size
        if "min_chunk_size" in config:
            min_size = config["min_chunk_size"]
            if not isinstance(min_size, int):
                errors.append(
                    APIError.validation_error(
                        "config.min_chunk_size",
                        f"min_chunk_size must be integer, "
                        f"got {type(min_size).__name__}",
                    )
                )
            elif min_size < self.MIN_CHUNK_SIZE:
                errors.append(
                    APIError.validation_error(
                        "config.min_chunk_size",
                        f"min_chunk_size must be at least {self.MIN_CHUNK_SIZE}",
                    )
                )

        # Validate size relationship
        if "max_chunk_size" in config and "min_chunk_size" in config:
            if isinstance(config["max_chunk_size"], int) and isinstance(
                config["min_chunk_size"], int
            ):
                if config["min_chunk_size"] > config["max_chunk_size"]:
                    errors.append(
                        APIError.validation_error(
                            "config",
                            "min_chunk_size cannot be greater than max_chunk_size",
                        )
                    )

    def _validate_overlap(self, config: Dict[str, Any], errors: List[APIError]) -> None:
        """Validate overlap parameters."""
        if "overlap_size" in config:
            overlap = config["overlap_size"]
            if not isinstance(overlap, int):
                errors.append(
                    APIError.validation_error(
                        "config.overlap_size",
                        f"overlap_size must be integer, got {type(overlap).__name__}",
                    )
                )
            elif overlap < 0:
                errors.append(
                    APIError.validation_error(
                        "config.overlap_size", "overlap_size cannot be negative"
                    )
                )

    def _validate_boolean_fields(
        self, config: Dict[str, Any], errors: List[APIError]
    ) -> None:
        """Validate boolean configuration fields."""
        bool_fields = ["enable_overlap", "allow_oversize", "preserve_code_blocks"]
        for field in bool_fields:
            if field in config and not isinstance(config[field], bool):
                errors.append(
                    APIError.validation_error(
                        f"config.{field}",
                        f"{field} must be boolean, got {type(config[field]).__name__}",
                    )
                )

    def _validate_thresholds(
        self, config: Dict[str, Any], errors: List[APIError]
    ) -> None:
        """Validate threshold fields (0.0 to 1.0)."""
        threshold_fields = [
            "code_ratio_threshold",
            "list_ratio_threshold",
            "table_ratio_threshold",
        ]
        for field in threshold_fields:
            if field in config:
                value = config[field]
                if not isinstance(value, (int, float)):
                    errors.append(
                        APIError.validation_error(
                            f"config.{field}",
                            f"{field} must be number, got {type(value).__name__}",
                        )
                    )
                elif not (0.0 <= value <= 1.0):
                    errors.append(
                        APIError.validation_error(
                            f"config.{field}", f"{field} must be between 0.0 and 1.0"
                        )
                    )

    def validate_config(self, config: Dict[str, Any]) -> List[APIError]:
        """
        Validate configuration dictionary.

        Args:
            config: Configuration to validate

        Returns:
            List of validation errors
        """
        errors: List[APIError] = []

        # Check if config is dict
        if not isinstance(config, dict):
            errors.append(
                APIError.validation_error(
                    "config",
                    f"Config must be a dictionary, got {type(config).__name__}",
                )
            )
            return errors

        # Validate different aspects
        self._validate_chunk_sizes(config, errors)
        self._validate_overlap(config, errors)
        self._validate_boolean_fields(config, errors)
        self._validate_thresholds(config, errors)

        return errors

    def validate_strategy(self, strategy: str) -> List[APIError]:
        """
        Validate strategy parameter.

        Args:
            strategy: Strategy name to validate

        Returns:
            List of validation errors
        """
        errors: List[APIError] = []

        # Check if strategy is string
        if not isinstance(strategy, str):
            errors.append(
                APIError.validation_error(
                    "strategy",
                    f"Strategy must be a string, got {type(strategy).__name__}",
                )
            )
            return errors

        # Check if strategy is valid
        if strategy not in self.VALID_STRATEGIES:
            valid_list = ", ".join(self.VALID_STRATEGIES)
            errors.append(
                APIError.validation_error(
                    "strategy",
                    f'Invalid strategy "{strategy}". '
                    f"Valid strategies: {valid_list}",
                )
            )

        return errors

    def is_valid(self, request: APIRequest) -> bool:
        """
        Check if request is valid.

        Args:
            request: API request to check

        Returns:
            True if valid, False otherwise
        """
        return len(self.validate_request(request)) == 0
