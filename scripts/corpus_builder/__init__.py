"""Corpus builder package."""

from .base import BaseCollector, BaseGenerator, DocumentMetadata, CollectionResult
from .config import (
    CORPUS_ROOT,
    TARGETS,
    GITHUB_REPOS,
    DOCS_SOURCES,
    BLOG_SOURCES,
)

__all__ = [
    "BaseCollector",
    "BaseGenerator",
    "DocumentMetadata",
    "CollectionResult",
    "CORPUS_ROOT",
    "TARGETS",
    "GITHUB_REPOS",
    "DOCS_SOURCES",
    "BLOG_SOURCES",
]
