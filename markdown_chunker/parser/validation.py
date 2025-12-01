"""
Validation logic for markdown parsing.

This module consolidates all validation functionality into a single location
with consistent error handling.

Consolidates:
- input_validator.py::InputValidator
- api_validator.py::Stage1APIValidator (as APIValidator)
- ast_validator.py::ASTValidator

Classes:
    InputValidator: Validate and normalize markdown input
    Stage1APIValidator: Validate Stage 1 API results (alias: APIValidator)
    ASTValidator: Validate AST structure

Functions:
    validate_and_normalize_input: Convenience function for input validation
    normalize_line_endings: Convenience function for line ending normalization
    validate_stage1_result: Convenience function for Stage 1 result validation
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class InputValidator:
    """
    Validate and normalize markdown input.

    Ensures input text meets requirements before processing.
    Migrated from input_validator.py.
    """

    @staticmethod
    def validate_and_normalize(md_text: Any) -> str:
        """
        Validate and normalize markdown input.

        Args:
            md_text: Markdown text to validate (can be None or str)

        Returns:
            Normalized text (empty string if None)

        Raises:
            TypeError: If input is not a string or None
        """
        if md_text is None:
            return ""

        if not isinstance(md_text, str):
            raise TypeError(f"Input must be a string, got {type(md_text)}")

        # Normalize line endings to Unix style (\n)
        normalized = InputValidator.normalize_line_endings(md_text)

        return normalized

    @staticmethod
    def normalize_line_endings(text: str) -> str:
        """
        Normalize line endings to Unix style (\\n).

        Args:
            text: Text with potentially mixed line endings

        Returns:
            Text with normalized line endings
        """
        # Replace Windows CRLF (\r\n) with LF (\n)
        text = text.replace("\r\n", "\n")

        # Replace old Mac CR (\r) with LF (\n)
        text = text.replace("\r", "\n")

        return text

    @staticmethod
    def validate_non_empty(text: str) -> bool:
        """
        Check if text is non-empty after stripping whitespace.

        Args:
            text: Text to check

        Returns:
            True if text has non-whitespace content
        """
        return bool(text.strip())

    @staticmethod
    def get_line_count(text: str) -> int:
        """
        Get the number of lines in the text.

        Args:
            text: Text to count lines in

        Returns:
            Number of lines (0 if empty)
        """
        if not text:
            return 0
        return len(text.split("\n"))

    @staticmethod
    def validate_encoding(text: str) -> bool:
        """
        Validate that text is properly encoded UTF-8.

        Args:
            text: Text to validate

        Returns:
            True if text is valid UTF-8
        """
        try:
            # Try to encode and decode to validate UTF-8
            text.encode("utf-8").decode("utf-8")
            return True
        except UnicodeError:
            return False


# APIValidator classes and dataclasses migrated from api_validator.py


@dataclass
class APIValidationError(Exception):
    """Exception raised when API validation fails."""

    errors: List[str]

    def __str__(self):
        return (
            f"API validation failed with {len(self.errors)} errors: "
            f"{'; '.join(self.errors)}"
        )


@dataclass
class ElementCountValidation:
    """Validation result for element count consistency."""

    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)


# Note: APIValidator is now Stage1APIValidator (migrated from api_validator.py)
# Keeping APIValidator as alias for backward compatibility
class Stage1APIValidator:
    """
    Validator for Stage 1 API results.

    Migrated from api_validator.py::Stage1APIValidator.
    Provides comprehensive validation for Stage 1 processing results.
    """

    def __init__(self):
        import logging

        self.logger = logging.getLogger(__name__)

    def validate_process_document_result(  # noqa: C901
        self, result
    ):  # result: Stage1Results -> APIValidationResult
        """Validate complete Stage 1 processing result."""
        # Complexity justified: Comprehensive validation of all Stage 1 components
        # Import here to avoid circular dependency
        # Note: ValidationResult and validate_ast_structure are now in this module

        @dataclass
        class APIValidationResult:
            """Complete API validation result."""

            is_valid: bool = True
            ast_validation: Any = None
            element_count_validation: Any = None
            content_validation: Any = None
            blocks_validation: Any = None
            errors: List[str] = field(default_factory=list)
            warnings: List[str] = field(default_factory=list)

            def add_validation(self, validation):
                """Add a validation result."""
                if hasattr(validation, "is_valid") and not validation.is_valid:
                    self.is_valid = False
                if hasattr(validation, "errors"):
                    self.errors.extend(validation.errors)
                if hasattr(validation, "warnings"):
                    self.warnings.extend(validation.warnings)

            def get_all_errors(self) -> List[str]:
                """Get all errors from all validations."""
                all_errors = self.errors.copy()
                if self.ast_validation:
                    all_errors.extend(
                        [issue.message for issue in self.ast_validation.get_errors()]
                    )
                if self.element_count_validation:
                    all_errors.extend(self.element_count_validation.errors)
                if self.content_validation:
                    all_errors.extend(self.content_validation.errors)
                if self.blocks_validation:
                    all_errors.extend(self.blocks_validation.errors)
                return all_errors

        validation_result = APIValidationResult()

        try:
            # Validate AST structure
            ast_validation = self._validate_ast_structure(result.ast)
            validation_result.ast_validation = ast_validation
            validation_result.add_validation(ast_validation)

            # Validate element counts
            count_validation = self._validate_element_counts(result)
            validation_result.element_count_validation = count_validation
            validation_result.add_validation(count_validation)

            # Validate ContentAnalysis
            content_validation = self._validate_content_analysis(result.analysis)
            validation_result.content_validation = content_validation
            validation_result.add_validation(content_validation)

            # Validate fenced blocks
            blocks_validation = self._validate_fenced_blocks(result.fenced_blocks)
            validation_result.blocks_validation = blocks_validation
            validation_result.add_validation(blocks_validation)

            # Cross-validation between components
            self._cross_validate_components(result, validation_result)

            if not validation_result.is_valid:
                self.logger.error(
                    f"API validation failed: {validation_result.get_all_errors()}"
                )
            else:
                self.logger.debug("API validation passed successfully")

        except Exception as e:
            validation_result.is_valid = False
            validation_result.errors.append(f"Validation exception: {str(e)}")
            self.logger.error(f"API validation exception: {e}")

        return validation_result

    def _validate_ast_structure(self, ast):  # ast: MarkdownNode -> ValidationResult
        """Validate AST structure."""
        # Note: ValidationResult and validate_ast_structure are defined in this module

        if ast is None:
            result = ValidationResult(is_valid=False)
            result.add_issue("error", "AST is None")
            return result
        return validate_ast_structure(ast)

    def _validate_element_counts(self, result) -> ElementCountValidation:
        """Validate consistency of element counts."""
        validation = ElementCountValidation()
        try:
            ast_counts = self._count_ast_elements(result.ast)
            # P1-005: header_count is now Dict[int, int], get total
            analysis_header_count = result.analysis.get_total_header_count()
            analysis_counts = {
                "code_blocks": result.analysis.code_block_count,
                "headers": analysis_header_count,
            }
            elements_counts = result.elements.get_element_count()
            actual_blocks_count = len(result.fenced_blocks)

            if ast_counts.get("code_blocks", 0) != analysis_counts["code_blocks"]:
                validation.add_error(
                    f"Code block count mismatch: AST={ast_counts.get('code_blocks', 0)}, "  # noqa: E501
                    f"Analysis={analysis_counts['code_blocks']}"
                )
            if ast_counts.get("headers", 0) != analysis_counts["headers"]:
                validation.add_error(
                    f"Header count mismatch: AST={ast_counts.get('headers', 0)}, "
                    f"Analysis={analysis_counts['headers']}"
                )
            if analysis_counts["headers"] != elements_counts["headers"]:
                validation.add_error(
                    f"Header count mismatch: Analysis={analysis_counts['headers']}, "
                    f"Elements={elements_counts['headers']}"
                )
            if analysis_counts["code_blocks"] != actual_blocks_count:
                validation.add_error(
                    f"Fenced block count mismatch: Analysis={analysis_counts['code_blocks']}, "  # noqa: E501
                    f"Actual={actual_blocks_count}"
                )
            self._validate_ratios_consistency(result.analysis, validation)
        except Exception as e:
            validation.add_error(f"Element count validation failed: {str(e)}")
        return validation

    def _count_ast_elements(self, ast) -> Dict[str, int]:
        """Count elements in AST."""
        from .types import NodeType

        counts = {
            "code_blocks": 0,
            "headers": 0,
            "paragraphs": 0,
            "lists": 0,
            "tables": 0,
            "links": 0,
            "images": 0,
        }

        def count_recursive(node):
            if node.type == NodeType.CODE_BLOCK:
                counts["code_blocks"] += 1
            elif node.type == NodeType.HEADER:
                counts["headers"] += 1
            elif node.type == NodeType.PARAGRAPH:
                counts["paragraphs"] += 1
            elif node.type == NodeType.LIST:
                counts["lists"] += 1
            elif node.type == NodeType.TABLE:
                counts["tables"] += 1
            elif node.type == NodeType.LINK:
                counts["links"] += 1
            elif node.type == NodeType.IMAGE:
                counts["images"] += 1
            for child in node.children:
                count_recursive(child)

        count_recursive(ast)
        return counts

    def _validate_ratios_consistency(
        self, analysis, validation: ElementCountValidation
    ):
        """Validate that content ratios are consistent."""
        total_ratio = analysis.code_ratio + analysis.text_ratio
        if abs(total_ratio - 1.0) > 0.1:
            validation.add_warning(
                f"Content ratios don't sum to 1.0: code={analysis.code_ratio}, "
                f"text={analysis.text_ratio}, total={total_ratio}"
            )
        if not (0.0 <= analysis.code_ratio <= 1.0):
            validation.add_error(f"Code ratio out of bounds: {analysis.code_ratio}")
        if not (0.0 <= analysis.text_ratio <= 1.0):
            validation.add_error(f"Text ratio out of bounds: {analysis.text_ratio}")

    def _validate_content_analysis(self, analysis) -> ElementCountValidation:
        """Validate ContentAnalysis structure and values."""
        validation = ElementCountValidation()
        try:
            self._validate_analysis_numeric_fields(analysis, validation)
            self._validate_analysis_ratio_fields(analysis, validation)
            self._validate_analysis_type_fields(analysis, validation)
        except Exception as e:
            validation.add_error(f"ContentAnalysis validation failed: {str(e)}")
        return validation

    def _validate_analysis_numeric_fields(  # noqa: C901
        self, analysis, validation: ElementCountValidation
    ) -> None:
        """Validate numeric fields in ContentAnalysis."""
        if not hasattr(analysis, "total_chars"):
            validation.add_error("ContentAnalysis missing total_chars")
        elif analysis.total_chars < 0:
            validation.add_error(f"Invalid total_chars: {analysis.total_chars}")
        if not hasattr(analysis, "total_lines"):
            validation.add_error("ContentAnalysis missing total_lines")
        elif analysis.total_lines < 0:
            validation.add_error(f"Invalid total_lines: {analysis.total_lines}")
        if not hasattr(analysis, "code_block_count"):
            validation.add_error("ContentAnalysis missing code_block_count")
        elif analysis.code_block_count < 0:
            validation.add_error(
                f"Invalid code_block_count: {analysis.code_block_count}"
            )
        if not hasattr(analysis, "header_count"):
            validation.add_error("ContentAnalysis missing header_count")
        elif isinstance(analysis.header_count, dict):
            # P1-005: header_count is now Dict[int, int]
            for level, count in analysis.header_count.items():
                if count < 0:
                    validation.add_error(f"Invalid header_count[{level}]: {count}")
        elif isinstance(analysis.header_count, int) and analysis.header_count < 0:
            validation.add_error(f"Invalid header_count: {analysis.header_count}")

    def _validate_analysis_ratio_fields(
        self, analysis, validation: ElementCountValidation
    ) -> None:
        """Validate ratio fields in ContentAnalysis."""
        if not hasattr(analysis, "code_ratio"):
            validation.add_error("ContentAnalysis missing code_ratio")
        if not hasattr(analysis, "text_ratio"):
            validation.add_error("ContentAnalysis missing text_ratio")

    def _validate_analysis_type_fields(
        self, analysis, validation: ElementCountValidation
    ) -> None:
        """Validate type and collection fields in ContentAnalysis."""
        if not hasattr(analysis, "content_type"):
            validation.add_error("ContentAnalysis missing content_type")
        elif analysis.content_type not in ["code_heavy", "mixed", "text_heavy"]:
            validation.add_warning(f"Unexpected content_type: {analysis.content_type}")
        if not hasattr(analysis, "languages"):
            validation.add_error("ContentAnalysis missing languages")
        # P1-006: languages is now Dict[str, int]
        elif not isinstance(analysis.languages, dict):
            validation.add_error("ContentAnalysis.languages must be a dict")

    def _validate_fenced_blocks(self, blocks: List) -> ElementCountValidation:
        """Validate fenced blocks structure and consistency."""
        from .types import FencedBlock

        validation = ElementCountValidation()
        try:
            if not isinstance(blocks, list):
                validation.add_error("Fenced blocks must be a list")
                return validation
            for i, block in enumerate(blocks):
                if not isinstance(block, FencedBlock):
                    validation.add_error(f"Block {i} is not a FencedBlock instance")
                    continue
                self._validate_single_block(block, i, validation)
            self._validate_block_positions(blocks, validation)
        except Exception as e:
            validation.add_error(f"Fenced blocks validation failed: {str(e)}")
        return validation

    def _validate_single_block(
        self, block, index: int, validation: ElementCountValidation
    ) -> None:
        """Validate a single fenced block structure."""
        if not hasattr(block, "start_line") or block.start_line < 1:
            validation.add_error(
                f"Block {index} has invalid start_line: "
                f"{getattr(block, 'start_line', 'missing')}"
            )
        if not hasattr(block, "end_line") or block.end_line < 1:
            validation.add_error(
                f"Block {index} has invalid end_line: "
                f"{getattr(block, 'end_line', 'missing')}"
            )
        if (
            hasattr(block, "start_line")
            and hasattr(block, "end_line")
            and block.end_line <= block.start_line
        ):
            validation.add_error(
                f"Block {index} end_line <= start_line: "
                f"{block.end_line} <= {block.start_line}"
            )
        if not hasattr(block, "content"):
            validation.add_error(f"Block {index} missing content")
        elif not isinstance(block.content, str):
            validation.add_error(f"Block {index} content must be string")
        if not hasattr(block, "language"):
            validation.add_error(f"Block {index} missing language")
        if not hasattr(block, "nesting_level") or block.nesting_level < 0:
            validation.add_error(
                f"Block {index} has invalid nesting_level: "
                f"{getattr(block, 'nesting_level', 'missing')}"
            )
        if not hasattr(block, "is_closed"):
            validation.add_error(f"Block {index} missing is_closed")
        elif not isinstance(block.is_closed, bool):
            validation.add_error(f"Block {index} is_closed must be boolean")

    def _validate_block_positions(
        self, blocks: List, validation: ElementCountValidation
    ):
        """Validate that blocks don't have invalid overlaps."""
        for i, block1 in enumerate(blocks):
            for j, block2 in enumerate(blocks[i + 1 :], i + 1):
                if (
                    block1.nesting_level == block2.nesting_level
                    and self._blocks_overlap_improperly(block1, block2)
                ):
                    validation.add_warning(
                        f"Blocks {i} and {j} overlap improperly at same nesting level: "
                        f"Block {i}: lines {block1.start_line}-{block1.end_line}, "
                        f"Block {j}: lines {block2.start_line}-{block2.end_line}"
                    )

    def _blocks_overlap_improperly(self, block1, block2) -> bool:
        """Check if two blocks overlap improperly."""
        overlap = not (
            block1.end_line < block2.start_line or block2.end_line < block1.start_line
        )
        if not overlap:
            return False
        block1_contains_block2 = (
            block1.start_line <= block2.start_line
            and block1.end_line >= block2.end_line
        )
        block2_contains_block1 = (
            block2.start_line <= block1.start_line
            and block2.end_line >= block1.end_line
        )
        return overlap and not (block1_contains_block2 or block2_contains_block1)

    def _cross_validate_components(self, result, validation_result):
        """Cross-validate consistency between different components."""
        try:
            if result.analysis.total_chars == 0 and result.ast.get_text_content():
                validation_result.errors.append(
                    "Analysis reports 0 chars but AST has content"
                )
            strategy = result.analysis.recommend_strategy()
            if strategy == "code" and result.analysis.code_ratio < 0.5:
                validation_result.warnings.append(
                    f"Strategy 'code' recommended but code_ratio is "
                    f"{result.analysis.code_ratio}"
                )
            if result.processing_time < 0:
                validation_result.errors.append(
                    f"Invalid processing time: {result.processing_time}"
                )
            elif result.processing_time > 60:
                validation_result.warnings.append(
                    f"Very long processing time: {result.processing_time}s"
                )
        except Exception as e:
            validation_result.errors.append(f"Cross-validation failed: {str(e)}")


# Backward compatibility alias
APIValidator = Stage1APIValidator


# Convenience functions for backward compatibility
def validate_and_normalize_input(md_text: Any) -> str:
    """
    Validate and normalize input (convenience function).

    Backward compatibility wrapper for InputValidator.validate_and_normalize().

    Args:
        md_text: Input text (can be None or str)

    Returns:
        Normalized text

    Raises:
        TypeError: If input is not a string or None
    """
    return InputValidator.validate_and_normalize(md_text)


def normalize_line_endings(text: str) -> str:
    """
    Normalize line endings (convenience function).

    Backward compatibility wrapper for InputValidator.normalize_line_endings().

    Args:
        text: Text with potentially mixed line endings

    Returns:
        Text with normalized line endings
    """
    return InputValidator.normalize_line_endings(text)


def validate_stage1_result(result):  # result: Stage1Results -> APIValidationResult
    """
    Validate Stage1Results (convenience function).

    Backward compatibility wrapper for Stage1APIValidator.

    Args:
        result: Stage1Results to validate

    Returns:
        APIValidationResult with validation status and errors
    """
    validator = Stage1APIValidator()
    return validator.validate_process_document_result(result)


# ASTValidator classes and dataclasses migrated from ast_validator.py


@dataclass
class ValidationIssue:
    """Represents a validation issue found in the AST."""

    severity: str  # "error", "warning", "info"
    message: str
    node_type: Optional[Any] = None
    position: Optional[Any] = None
    details: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of AST validation."""

    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    node_count: int = 0
    max_depth: int = 0

    def add_issue(
        self,
        severity: str,
        message: str,
        node_type: Optional[Any] = None,
        position: Optional[Any] = None,
        details: Optional[str] = None,
    ):
        """Add a validation issue."""
        issue = ValidationIssue(
            severity=severity,
            message=message,
            node_type=node_type,
            position=position,
            details=details,
        )
        self.issues.append(issue)

        # Mark as invalid if we have errors
        if severity == "error":
            self.is_valid = False

    def get_errors(self) -> List[ValidationIssue]:
        """Get all error-level issues."""
        return [issue for issue in self.issues if issue.severity == "error"]

    def get_warnings(self) -> List[ValidationIssue]:
        """Get all warning-level issues."""
        return [issue for issue in self.issues if issue.severity == "warning"]

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.get_errors()) > 0

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.get_warnings()) > 0


class ASTValidator:
    """
    Validator for AST structures.

    Migrated from ast_validator.py.
    Provides comprehensive validation for AST structures.
    """

    def __init__(self):
        import logging

        self.logger = logging.getLogger(__name__)

    def validate_ast(self, ast) -> ValidationResult:  # ast: MarkdownNode
        """Validate complete AST structure."""
        result = ValidationResult(is_valid=True)

        try:
            # Basic structure validation
            self._validate_basic_structure(ast, result)

            # Position validation (if positions exist)
            if hasattr(ast, "start_pos") and hasattr(ast, "end_pos"):
                self._validate_positions(ast, result)

            # Hierarchy validation
            if hasattr(ast, "children"):
                self._validate_hierarchy(ast, result)

            # Content validation
            self._validate_content(ast, result)

            # Calculate statistics (if methods exist)
            if hasattr(ast, "count_nodes"):
                result.node_count = ast.count_nodes()
            if hasattr(ast, "get_depth"):
                result.max_depth = ast.get_depth()

            self.logger.debug(
                f"AST validation completed: {len(result.issues)} issues found"
            )

        except Exception as e:
            result.add_issue(
                "error", f"Validation failed with exception: {str(e)}", details=str(e)
            )
            self.logger.error(f"AST validation failed: {e}")

        return result

    def _validate_basic_structure(self, ast, result: ValidationResult):
        """Validate basic AST structure."""
        # Check for required attributes
        if not hasattr(ast, "children"):
            result.add_issue("error", "Node missing children attribute")

        if not hasattr(ast, "metadata"):
            result.add_issue("error", "Node missing metadata attribute")

        # Recursively validate children
        if hasattr(ast, "children"):
            self._validate_children_structure(ast, result)

    def _validate_children_structure(self, node, result: ValidationResult):
        """Validate structure of child nodes."""
        if not isinstance(node.children, list):
            result.add_issue("error", "Node children must be a list")
            return

        for i, child in enumerate(node.children):
            # Recursively validate child
            if hasattr(child, "children"):
                self._validate_children_structure(child, result)

    def _validate_positions(self, node, result: ValidationResult):
        """Validate position information in nodes."""
        # Check position validity
        if hasattr(node, "start_pos") and node.start_pos:
            if hasattr(node.start_pos, "line") and node.start_pos.line < 0:
                result.add_issue(
                    "error", f"Invalid start position: line={node.start_pos.line}"
                )

        # Recursively validate children
        if hasattr(node, "children"):
            for child in node.children:
                if hasattr(child, "start_pos"):
                    self._validate_positions(child, result)

    def _validate_hierarchy(self, node, result: ValidationResult):
        """Validate node hierarchy relationships."""
        # Check for overlapping siblings
        if hasattr(node, "children"):
            for i, child in enumerate(node.children):
                # Recursively validate children
                if hasattr(child, "children"):
                    self._validate_hierarchy(child, result)

    def _validate_content(self, node, result: ValidationResult):
        """Validate node content consistency."""
        # Check content type
        if hasattr(node, "content") and node.content is not None:
            if not isinstance(node.content, str):
                result.add_issue(
                    "error", f"Node content must be string, got {type(node.content)}"
                )

        # Check metadata type
        if hasattr(node, "metadata") and not isinstance(node.metadata, dict):
            result.add_issue(
                "error", f"Node metadata must be dict, got {type(node.metadata)}"
            )

        # Recursively validate children
        if hasattr(node, "children"):
            for child in node.children:
                self._validate_content(child, result)


def validate_ast_structure(ast) -> ValidationResult:
    """
    Convenience function to validate AST structure.

    Backward compatibility wrapper for ASTValidator.validate_ast().

    Args:
        ast: MarkdownNode to validate

    Returns:
        ValidationResult with validation status and issues
    """
    validator = ASTValidator()
    return validator.validate_ast(ast)
