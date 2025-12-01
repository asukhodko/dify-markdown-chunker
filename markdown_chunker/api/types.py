"""
API types for REST integration.

Defines request/response structures for the REST API.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class APIRequest:
    """
    API request structure for chunking operations.

    Attributes:
        content: Markdown content to chunk
        config: Optional configuration dictionary
        strategy: Optional strategy override
        metadata: Optional request metadata
    """

    content: str
    config: Optional[Dict[str, Any]] = None
    strategy: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary."""
        return {
            "content": self.content,
            "config": self.config,
            "strategy": self.strategy,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APIRequest":
        """Create request from dictionary."""
        return cls(
            content=data["content"],
            config=data.get("config"),
            strategy=data.get("strategy"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class APIResponse:
    """
    API response structure for chunking operations.

    Attributes:
        success: Whether operation succeeded
        chunks: List of chunk dictionaries
        metadata: Response metadata (strategy, timing, etc.)
        errors: List of error messages
        warnings: List of warning messages
    """

    success: bool
    chunks: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            "success": self.success,
            "chunks": self.chunks,
            "metadata": self.metadata,
            "errors": self.errors,
            "warnings": self.warnings,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APIResponse":
        """Create response from dictionary."""
        return cls(
            success=data["success"],
            chunks=data.get("chunks", []),
            metadata=data.get("metadata", {}),
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
        )

    @classmethod
    def success_response(
        cls,
        chunks: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        warnings: Optional[List[str]] = None,
    ) -> "APIResponse":
        """Create a successful response."""
        return cls(
            success=True, chunks=chunks, metadata=metadata, warnings=warnings or []
        )

    @classmethod
    def error_response(
        cls, errors: List[str], metadata: Optional[Dict[str, Any]] = None
    ) -> "APIResponse":
        """Create an error response."""
        return cls(success=False, errors=errors, metadata=metadata or {})


@dataclass
class APIError:
    """
    API error structure.

    Attributes:
        code: Error code
        message: Error message
        details: Optional error details
        field: Optional field that caused the error
    """

    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    field: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        result: Dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details:
            result["details"] = self.details
        if self.field:
            result["field"] = self.field
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APIError":
        """Create error from dictionary."""
        return cls(
            code=data["code"],
            message=data["message"],
            details=data.get("details"),
            field=data.get("field"),
        )

    @classmethod
    def validation_error(cls, field: str, message: str) -> "APIError":
        """Create a validation error."""
        return cls(code="VALIDATION_ERROR", message=message, field=field)

    @classmethod
    def processing_error(
        cls, message: str, details: Optional[Dict[str, Any]] = None
    ) -> "APIError":
        """Create a processing error."""
        return cls(code="PROCESSING_ERROR", message=message, details=details)

    @classmethod
    def configuration_error(
        cls, message: str, field: Optional[str] = None
    ) -> "APIError":
        """Create a configuration error."""
        return cls(code="CONFIGURATION_ERROR", message=message, field=field)
