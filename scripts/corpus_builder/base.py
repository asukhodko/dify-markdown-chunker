"""Base classes for collectors and generators."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import json


@dataclass
class DocumentMetadata:
    """Metadata for a corpus document."""

    filename: str
    category: str
    subcategory: Optional[str] = None
    size_bytes: int = 0
    line_count: int = 0
    source: str = "synthetic"
    source_url: Optional[str] = None
    collection_date: str = ""
    
    # Content characteristics
    code_ratio: float = 0.0
    table_count: int = 0
    list_count: int = 0
    header_count: int = 0
    max_header_depth: int = 0
    code_block_count: int = 0
    nesting_level: int = 0
    
    # Expected behavior
    expected_strategy: Optional[str] = None
    
    # Hash for deduplication
    content_hash: str = ""
    
    # Additional metadata
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "filename": self.filename,
            "category": self.category,
            "subcategory": self.subcategory,
            "size_bytes": self.size_bytes,
            "line_count": self.line_count,
            "source": self.source,
            "source_url": self.source_url,
            "collection_date": self.collection_date,
            "code_ratio": self.code_ratio,
            "table_count": self.table_count,
            "list_count": self.list_count,
            "header_count": self.header_count,
            "max_header_depth": self.max_header_depth,
            "code_block_count": self.code_block_count,
            "nesting_level": self.nesting_level,
            "expected_strategy": self.expected_strategy,
            "content_hash": self.content_hash,
            "extra": self.extra,
        }


@dataclass
class CollectionResult:
    """Result from a collection operation."""

    success: bool
    content: str = ""
    metadata: Optional[DocumentMetadata] = None
    error: Optional[str] = None


class BaseCollector(ABC):
    """Base class for document collectors."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.collected_hashes = set()

    @abstractmethod
    def collect(self) -> List[CollectionResult]:
        """Collect documents and return results."""
        pass

    def _compute_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _is_duplicate(self, content: str) -> bool:
        """Check if content is duplicate."""
        content_hash = self._compute_hash(content)
        if content_hash in self.collected_hashes:
            return True
        self.collected_hashes.add(content_hash)
        return False

    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content characteristics."""
        lines = content.split("\n")
        line_count = len(lines)
        
        # Count headers
        header_count = sum(1 for line in lines if line.strip().startswith("#"))
        max_depth = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                depth = len(stripped) - len(stripped.lstrip("#"))
                max_depth = max(max_depth, depth)
        
        # Count code blocks
        code_block_count = content.count("```")  // 2
        
        # Count tables (simplified)
        table_count = sum(1 for line in lines if "|" in line and line.count("|") >= 2) // 3
        
        # Count lists
        list_count = sum(
            1
            for line in lines
            if line.strip().startswith(("-", "*", "+"))
            or (len(line.strip()) > 2 and line.strip()[0].isdigit() and line.strip()[1] == ".")
        )
        
        # Calculate code ratio
        code_lines = 0
        in_code_block = False
        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
            elif in_code_block:
                code_lines += 1
        
        code_ratio = code_lines / max(line_count, 1)
        
        # Detect nesting level (for fences)
        max_backticks = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("`") and not in_code_block:
                backtick_count = len(stripped) - len(stripped.lstrip("`"))
                max_backticks = max(max_backticks, backtick_count)
        
        nesting_level = max(0, (max_backticks - 3) // 3)
        
        return {
            "line_count": line_count,
            "header_count": header_count,
            "max_header_depth": max_depth,
            "code_block_count": code_block_count,
            "table_count": table_count,
            "list_count": list_count,
            "code_ratio": code_ratio,
            "nesting_level": nesting_level,
        }

    def _determine_expected_strategy(self, analysis: Dict[str, Any]) -> str:
        """Determine expected chunking strategy based on analysis."""
        code_ratio = analysis.get("code_ratio", 0)
        code_blocks = analysis.get("code_block_count", 0)
        headers = analysis.get("header_count", 0)
        
        # Based on v2 strategy selection logic
        if code_ratio >= 0.3 and code_blocks >= 1:
            return "code_aware"
        elif headers >= 3:
            return "structural"
        else:
            return "fallback"

    def save_document(
        self, content: str, filename: str, metadata: DocumentMetadata
    ) -> bool:
        """Save document and metadata to disk."""
        try:
            # Save content
            file_path = self.output_dir / filename
            file_path.write_text(content, encoding="utf-8")
            
            # Save metadata
            metadata_path = file_path.with_suffix(file_path.suffix + ".meta.json")
            metadata_path.write_text(
                json.dumps(metadata.to_dict(), indent=2), encoding="utf-8"
            )
            
            return True
        except Exception as e:
            print(f"Error saving {filename}: {e}")
            return False


class BaseGenerator(ABC):
    """Base class for document generators."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def generate(self, count: int) -> List[CollectionResult]:
        """Generate documents and return results."""
        pass

    def _compute_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content characteristics (same as collector)."""
        lines = content.split("\n")
        line_count = len(lines)
        
        header_count = sum(1 for line in lines if line.strip().startswith("#"))
        max_depth = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                depth = len(stripped) - len(stripped.lstrip("#"))
                max_depth = max(max_depth, depth)
        
        code_block_count = content.count("```") // 2
        table_count = sum(1 for line in lines if "|" in line and line.count("|") >= 2) // 3
        
        list_count = sum(
            1
            for line in lines
            if line.strip().startswith(("-", "*", "+"))
            or (len(line.strip()) > 2 and line.strip()[0].isdigit() and line.strip()[1] == ".")
        )
        
        code_lines = 0
        in_code_block = False
        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
            elif in_code_block:
                code_lines += 1
        
        code_ratio = code_lines / max(line_count, 1)
        
        max_backticks = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("`"):
                backtick_count = len(stripped) - len(stripped.lstrip("`"))
                max_backticks = max(max_backticks, backtick_count)
        
        nesting_level = max(0, (max_backticks - 3) // 3)
        
        return {
            "line_count": line_count,
            "header_count": header_count,
            "max_header_depth": max_depth,
            "code_block_count": code_block_count,
            "table_count": table_count,
            "list_count": list_count,
            "code_ratio": code_ratio,
            "nesting_level": nesting_level,
        }

    def _determine_expected_strategy(self, analysis: Dict[str, Any]) -> str:
        """Determine expected chunking strategy."""
        code_ratio = analysis.get("code_ratio", 0)
        code_blocks = analysis.get("code_block_count", 0)
        headers = analysis.get("header_count", 0)
        
        if code_ratio >= 0.3 and code_blocks >= 1:
            return "code_aware"
        elif headers >= 3:
            return "structural"
        else:
            return "fallback"

    def save_document(
        self, content: str, filename: str, metadata: DocumentMetadata
    ) -> bool:
        """Save document and metadata to disk."""
        try:
            file_path = self.output_dir / filename
            file_path.write_text(content, encoding="utf-8")
            
            metadata_path = file_path.with_suffix(file_path.suffix + ".meta.json")
            metadata_path.write_text(
                json.dumps(metadata.to_dict(), indent=2), encoding="utf-8"
            )
            
            return True
        except Exception as e:
            print(f"Error saving {filename}: {e}")
            return False
