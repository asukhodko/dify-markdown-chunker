"""
Test processing components for the cleanup system.
"""

import ast
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from .config import CleanupConfig
from .logging_setup import LoggerMixin
from .models import (
    AdaptationPlan,
    AdaptationReport,
    CodeChange,
    DuplicateReport,
    RemovalReport,
    TestFile,
)


class TestProcessor(LoggerMixin):
    """Main processor for test file operations."""

    def __init__(self, config: CleanupConfig):
        self.config = config
        self.redundancy_detector = RedundancyDetector(config)
        self.test_adapter = TestAdapter(config)
        self.file_manager = FileManager(config)

    def remove_redundant_tests(self, duplicates: DuplicateReport) -> RemovalReport:
        """
        Remove redundant tests identified by duplicate detection.

        Args:
            duplicates: Report of duplicate tests to remove

        Returns:
            RemovalReport with details of removed tests
        """
        self.logger.info(
            f"Removing {len(duplicates.redundant_files)} redundant test files"
        )

        removed_files = []
        preserved_assertions = {}
        makefile_updates = []
        errors = []

        for file_path in duplicates.redundant_files:
            try:
                # Extract unique assertions before removal
                unique_assertions = self.redundancy_detector.extract_unique_assertions(
                    file_path
                )
                if unique_assertions:
                    preserved_assertions[file_path] = unique_assertions
                    self.logger.info(
                        f"Preserved {len(unique_assertions)} unique assertions "
                        f"from {file_path}"
                    )

                # Remove the file
                if self.file_manager.remove_file(file_path):
                    removed_files.append(file_path)

                    # Update Makefile references
                    makefile_changes = self.file_manager.update_makefile_references(
                        file_path
                    )
                    makefile_updates.extend(makefile_changes)

                    self.logger.info(
                        f"Successfully removed redundant test: {file_path}"
                    )
                else:
                    errors.append(f"Failed to remove file: {file_path}")

            except Exception as e:
                error_msg = f"Error processing {file_path}: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)

        report = RemovalReport(
            removed_files=removed_files,
            preserved_assertions=preserved_assertions,
            makefile_updates=makefile_updates,
            errors=errors,
        )

        self.logger.info(
            f"Removal complete: {len(removed_files)} files removed, "
            f"{len(errors)} errors"
        )

        return report

    def adapt_valuable_tests(self, valuable_tests: List[TestFile]) -> AdaptationReport:
        """
        Adapt valuable legacy tests to work with new architecture.

        Args:
            valuable_tests: List of test files to adapt

        Returns:
            AdaptationReport with details of adaptations
        """
        self.logger.info(f"Adapting {len(valuable_tests)} valuable test files")

        adapted_files = []
        adaptation_plans = []
        successful_adaptations = []
        failed_adaptations = []
        errors = []

        for test_file in valuable_tests:
            try:
                # Create adaptation plan
                plan = self.test_adapter.create_adaptation_plan(test_file)
                adaptation_plans.append(plan)

                # Execute adaptation
                if self.test_adapter.execute_adaptation(plan):
                    adapted_files.append(plan.adapted_file)
                    successful_adaptations.append(test_file.path)
                    self.logger.info(f"Successfully adapted: {test_file.path}")
                else:
                    failed_adaptations.append(test_file.path)
                    errors.append(f"Failed to execute adaptation for: {test_file.path}")

            except Exception as e:
                error_msg = f"Error adapting {test_file.path}: {str(e)}"
                errors.append(error_msg)
                failed_adaptations.append(test_file.path)
                self.logger.error(error_msg)

        report = AdaptationReport(
            adapted_files=adapted_files,
            adaptation_plans=adaptation_plans,
            successful_adaptations=successful_adaptations,
            failed_adaptations=failed_adaptations,
            errors=errors,
        )

        self.logger.info(
            f"Adaptation complete: {len(successful_adaptations)} successful, "
            f"{len(failed_adaptations)} failed"
        )

        return report

    def preserve_unique_assertions(self, test_file: TestFile) -> List[str]:
        """
        Extract and preserve unique assertions from a test file.

        Args:
            test_file: Test file to analyze

        Returns:
            List of unique assertion strings
        """
        return self.redundancy_detector.extract_unique_assertions(test_file.path)


class RedundancyDetector(LoggerMixin):
    """Detects and handles redundant test removal."""

    def __init__(self, config: CleanupConfig):
        self.config = config

    def extract_unique_assertions(self, file_path: str) -> List[str]:
        """
        Extract unique assertions from a test file that should be preserved.

        Args:
            file_path: Path to the test file

        Returns:
            List of unique assertion strings
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            unique_assertions = []

            # Extract assertions from the AST
            for node in ast.walk(tree):
                if isinstance(node, ast.Assert):
                    assertion_text = self._extract_assertion_text(node, content)
                    if assertion_text and self._is_unique_assertion(assertion_text):
                        unique_assertions.append(assertion_text)

            return unique_assertions

        except Exception as e:
            self.logger.warning(f"Could not extract assertions from {file_path}: {e}")
            return []

    def _extract_assertion_text(
        self, assert_node: ast.Assert, content: str
    ) -> Optional[str]:
        """Extract the text of an assertion from the AST node."""
        try:
            # Get the line number and extract the assertion text
            line_num = assert_node.lineno - 1  # AST uses 1-based line numbers
            lines = content.splitlines()

            if 0 <= line_num < len(lines):
                line = lines[line_num].strip()
                if line.startswith("assert"):
                    return line

            return None
        except Exception:
            return None

    def _is_unique_assertion(self, assertion_text: str) -> bool:
        """
        Determine if an assertion is unique and worth preserving.

        Args:
            assertion_text: The assertion text to evaluate

        Returns:
            True if the assertion should be preserved
        """
        # Skip very basic assertions
        basic_patterns = [
            r"assert True",
            r"assert False",
            r"assert \w+ is not None",
            r"assert len\(\w+\) > 0",
            r"assert len\(\w+\) == \d+",
        ]

        for pattern in basic_patterns:
            if re.match(pattern, assertion_text):
                return False

        # Preserve complex assertions
        complex_indicators = [
            "isinstance",
            "hasattr",
            "startswith",
            "endswith",
            "in ",
            "not in",
            "raises",
            ">=",
            "<=",
            "!=",
            "and ",
            "or ",
        ]

        return any(indicator in assertion_text for indicator in complex_indicators)


class TestAdapter(LoggerMixin):
    """Adapts legacy tests to work with new architecture."""

    def __init__(self, config: CleanupConfig):
        self.config = config

    def create_adaptation_plan(self, test_file: TestFile) -> AdaptationPlan:
        """
        Create a plan for adapting a legacy test file.

        Args:
            test_file: Test file to adapt

        Returns:
            AdaptationPlan with all necessary changes
        """
        original_path = test_file.path
        adapted_path = self._generate_adapted_path(original_path)

        # Analyze the file content
        with open(original_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        # Plan import changes
        import_changes = self._plan_import_changes(test_file.analysis.imports)

        # Plan code changes
        code_changes = self._plan_code_changes(tree, content)

        # Extract assertions to preserve
        preserved_assertions = self._extract_assertions_to_preserve(tree, content)

        plan = AdaptationPlan(
            original_file=original_path,
            adapted_file=adapted_path,
            import_changes=import_changes,
            code_changes=code_changes,
            preserved_assertions=preserved_assertions,
            adaptation_notes=[
                f"Adapted from legacy test: {original_path}",
                f"Replaced {len(import_changes)} import statements",
                f"Modified {len(code_changes)} code sections",
            ],
        )

        self.logger.debug(
            f"Created adaptation plan for {original_path}: "
            f"{len(import_changes)} imports, {len(code_changes)} changes"
        )

        return plan

    def execute_adaptation(self, plan: AdaptationPlan) -> bool:
        """
        Execute an adaptation plan to create the adapted test file.

        Args:
            plan: AdaptationPlan to execute

        Returns:
            True if adaptation was successful
        """
        try:
            # Read original content
            with open(plan.original_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST to get exact import locations
            tree = ast.parse(content)
            lines = content.splitlines()

            # Apply import changes using AST-based replacement
            content = self._apply_import_changes_ast(content, tree, plan.import_changes)

            # Apply code changes
            lines = content.splitlines()
            for change in sorted(
                plan.code_changes, key=lambda x: x.line_number, reverse=True
            ):
                if 0 <= change.line_number - 1 < len(lines):
                    old_line = lines[change.line_number - 1]
                    if change.old_code in old_line:
                        new_line = old_line.replace(change.old_code, change.new_code)
                        lines[change.line_number - 1] = new_line
                        self.logger.debug(
                            f"Applied change at line {change.line_number}: "
                            f"{old_line.strip()} -> {new_line.strip()}"
                        )
                    else:
                        self.logger.warning(
                            f"Could not find '{change.old_code}' in line "
                            f"{change.line_number}: {old_line.strip()}"
                        )

            adapted_content = "\n".join(lines)

            # Add adaptation header comment
            header = f'''"""
Adapted test file - migrated from legacy implementation.
Original: {plan.original_file}
Adapted: {plan.adapted_file}

This test has been adapted to use the migration adapter instead of
the legacy markdown_chunker_v2/markdown_chunker modules.
"""

'''
            adapted_content = header + adapted_content

            # Write adapted file
            os.makedirs(os.path.dirname(plan.adapted_file), exist_ok=True)
            with open(plan.adapted_file, "w", encoding="utf-8") as f:
                f.write(adapted_content)

            self.logger.info(f"Successfully created adapted test: {plan.adapted_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to execute adaptation plan: {e}")
            return False

    def _apply_import_changes_ast(
        self, content: str, tree: ast.AST, import_changes: Dict[str, str]
    ) -> str:
        """Apply import changes using AST-based replacement."""
        lines = content.splitlines()

        # Find all import nodes and their line ranges
        import_replacements = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                start_line = node.lineno - 1  # Convert to 0-based
                end_line = node.end_lineno - 1 if node.end_lineno else start_line

                # Get the original import text

                # Check if this import needs replacement
                replacement = self._get_import_replacement(node, import_changes)
                if replacement:
                    import_replacements.append((start_line, end_line, replacement))

        # Apply replacements in reverse order to maintain line numbers
        for start_line, end_line, replacement in sorted(
            import_replacements, reverse=True
        ):
            # Replace the import lines
            lines[start_line : end_line + 1] = replacement.split("\n")

        return "\n".join(lines)

    def _get_import_replacement(
        self, node: ast.AST, import_changes: Dict[str, str]
    ) -> Optional[str]:
        """Get replacement text for an import node."""
        if isinstance(node, ast.ImportFrom):
            return self._handle_import_from(node)
        elif isinstance(node, ast.Import):
            return self._handle_import(node)
        return None

    def _handle_import_from(self, node: ast.ImportFrom) -> Optional[str]:
        """Handle ImportFrom nodes."""
        module = node.module or ""

        if not ("markdown_chunker_v2" in module or "markdown_chunker" in module):
            return None

        imported_names = [alias.name for alias in node.names]
        return self._get_replacement_for_names(imported_names)

    def _handle_import(self, node: ast.Import) -> Optional[str]:
        """Handle Import nodes."""
        for alias in node.names:
            if "markdown_chunker" in alias.name:
                return "from adapter import MarkdownChunker"
        return None

    def _get_replacement_for_names(self, imported_names: List[str]) -> str:
        """Get replacement import for specific imported names."""
        if "MarkdownChunker" in imported_names and "ChunkConfig" in imported_names:
            return (
                "from adapter import MarkdownChunker\n"
                "from chunkana import ChunkerConfig as ChunkConfig"
            )
        elif "MarkdownChunker" in imported_names:
            return "from adapter import MarkdownChunker"
        elif "ChunkConfig" in imported_names:
            return "from chunkana import ChunkerConfig as ChunkConfig"
        elif "Chunk" in imported_names:
            return "from chunkana import Chunk"
        elif any(
            name in ["AdaptiveSizeCalculator", "AdaptiveSizeConfig"]
            for name in imported_names
        ):
            return (
                "# Legacy adaptive sizing imports - "
                "functionality moved to chunkana core"
            )
        elif any(
            name in ["Parser", "StreamingConfig", "HierarchyBuilder"]
            for name in imported_names
        ):
            return "# Legacy imports - functionality moved to chunkana core"
        else:
            return "from adapter import MarkdownChunker"

    def _generate_adapted_path(self, original_path: str) -> str:
        """Generate path for adapted test file."""
        path = Path(original_path)
        stem = path.stem

        # Add _adapted suffix if not already present
        if not stem.endswith("_adapted"):
            stem += "_adapted"

        return str(path.parent / f"{stem}{path.suffix}")

    def _plan_import_changes(self, imports: List[str]) -> Dict[str, str]:
        """Plan import statement changes."""
        import_changes = {}

        for import_stmt in imports:
            original_stmt = import_stmt.strip()

            # Handle different import patterns
            if (
                "markdown_chunker_v2" in original_stmt
                or "markdown_chunker" in original_stmt
            ):
                # Replace with adapter import - keep MarkdownChunker as alias
                if (
                    "MarkdownChunker" in original_stmt
                    and "ChunkConfig" in original_stmt
                ):
                    # Multiple imports: from module import MarkdownChunker, ChunkConfig
                    import_changes[original_stmt] = (
                        "from adapter import MarkdownChunker\n"
                        "from chunkana import ChunkerConfig as ChunkConfig"
                    )
                elif "MarkdownChunker" in original_stmt:
                    # Single MarkdownChunker import
                    import_changes[original_stmt] = (
                        "from adapter import MarkdownChunker"
                    )
                elif "ChunkConfig" in original_stmt:
                    # ChunkConfig import
                    import_changes[original_stmt] = (
                        "from chunkana import ChunkerConfig as ChunkConfig"
                    )
                elif "Chunk," in original_stmt or "Chunk " in original_stmt:
                    # Chunk import
                    import_changes[original_stmt] = "from chunkana import Chunk"
                else:
                    # Generic module imports - replace with adapter
                    import_changes[original_stmt] = (
                        "from adapter import MarkdownChunker"
                    )

        return import_changes

    def _plan_code_changes(self, tree: ast.AST, content: str) -> List[CodeChange]:
        """Plan code changes needed for adaptation."""
        code_changes = []
        lines = content.splitlines()

        # Find patterns that need to be changed
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()

            # Replace MarkdownChunker instantiation - keep as MarkdownChunker (alias)
            if "MarkdownChunker(" in line:
                # No change needed - MarkdownChunker is now an alias to MigrationAdapter
                pass

            # Replace ChunkConfig with ChunkerConfig
            elif "ChunkConfig(" in line and "ChunkerConfig(" not in line:
                old_code = line_stripped
                new_code = line_stripped.replace("ChunkConfig(", "ChunkerConfig(")
                code_changes.append(
                    CodeChange(
                        line_number=i,
                        old_code=old_code,
                        new_code=new_code,
                        change_type="config_class",
                    )
                )

            # Replace .chunk( method calls with .run_chunking(
            elif ".chunk(" in line and ".run_chunking(" not in line:
                old_code = line_stripped
                new_code = line_stripped.replace(".chunk(", ".run_chunking(")
                code_changes.append(
                    CodeChange(
                        line_number=i,
                        old_code=old_code,
                        new_code=new_code,
                        change_type="method_call",
                    )
                )

        return code_changes

    def _extract_assertions_to_preserve(self, tree: ast.AST, content: str) -> List[str]:
        """Extract important assertions that should be preserved."""
        assertions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                try:
                    line_num = node.lineno - 1
                    lines = content.splitlines()
                    if 0 <= line_num < len(lines):
                        assertion = lines[line_num].strip()
                        assertions.append(assertion)
                except Exception:
                    continue

        return assertions


class FileManager(LoggerMixin):
    """Manages file operations for test cleanup."""

    def __init__(self, config: CleanupConfig):
        self.config = config

    def remove_file(self, file_path: str) -> bool:
        """
        Safely remove a test file with optional backup.

        Args:
            file_path: Path to file to remove

        Returns:
            True if removal was successful
        """
        try:
            if not os.path.exists(file_path):
                self.logger.warning(f"File does not exist: {file_path}")
                return False

            # Create backup if configured
            if self.config.create_backups:
                self._create_backup(file_path)

            # Remove the file
            if not self.config.dry_run:
                os.remove(file_path)
                self.logger.info(f"Removed file: {file_path}")
            else:
                self.logger.info(f"DRY RUN: Would remove file: {file_path}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to remove {file_path}: {e}")
            return False

    def update_makefile_references(self, removed_file: str) -> List[str]:
        """
        Update Makefile to remove references to deleted test files.

        Args:
            removed_file: Path to the removed file

        Returns:
            List of changes made to Makefile
        """
        makefile_path = os.path.join(self.config.project_root, "Makefile")
        changes: List[str] = []

        if not os.path.exists(makefile_path):
            self.logger.warning("Makefile not found")
            return changes

        try:
            with open(makefile_path, "r") as f:
                content = f.read()

            # Find references to the removed file
            file_name = os.path.basename(removed_file)
            file_stem = os.path.splitext(file_name)[0]

            # Remove file references from test targets
            lines = content.splitlines()
            modified_lines = []

            for line in lines:
                original_line = line

                # Remove direct file references
                if file_name in line or file_stem in line:
                    # Remove the file from test target lists
                    line = re.sub(rf"\s*{re.escape(file_name)}\s*", " ", line)
                    line = re.sub(rf"\s*{re.escape(file_stem)}\s*", " ", line)
                    line = re.sub(r"\s+", " ", line).strip()  # Clean up whitespace

                    if line != original_line:
                        changes.append(f"Updated line: {original_line} -> {line}")

                modified_lines.append(line)

            # Write updated Makefile
            if changes and not self.config.dry_run:
                with open(makefile_path, "w") as f:
                    f.write("\n".join(modified_lines))
                self.logger.info(f"Updated Makefile: {len(changes)} changes")
            elif changes:
                self.logger.info(
                    f"DRY RUN: Would update Makefile with {len(changes)} changes"
                )

            return changes

        except Exception as e:
            self.logger.error(f"Failed to update Makefile: {e}")
            return []

    def _create_backup(self, file_path: str) -> None:
        """Create a backup of the file before removal."""
        try:
            backup_dir = Path(self.config.backup_directory)
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Create backup path maintaining directory structure
            rel_path = os.path.relpath(file_path, self.config.project_root)
            backup_path = backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(file_path, backup_path)
            self.logger.debug(f"Created backup: {backup_path}")

        except Exception as e:
            self.logger.warning(f"Failed to create backup for {file_path}: {e}")
