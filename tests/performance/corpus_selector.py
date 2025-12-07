"""
Corpus selector for benchmark testing.

Selects representative test documents from the corpus for performance measurement.
"""

from pathlib import Path
from typing import Dict, List

# Meta-documentation files to exclude from benchmarks
EXCLUDED_FILES = {
    "README.md",
    "INDEX.md",
    "USAGE.md",
    "COMPLETION_SUMMARY.md",
    "COLLECTION_REPORT.md",
    "metadata.csv",
    "metadata_index.json",
}


class CorpusSelector:
    """Select appropriate documents from test corpus for benchmarking."""

    def __init__(self, corpus_root: Path):
        """
        Initialize corpus selector.

        Args:
            corpus_root: Path to corpus root directory
        """
        self.corpus_root = Path(corpus_root)
        if not self.corpus_root.exists():
            raise ValueError(f"Corpus root does not exist: {corpus_root}")

    def scan_corpus(self) -> List[Dict[str, any]]:
        """
        Scan corpus and collect document metadata.

        Returns:
            List of document metadata dictionaries
        """
        documents = []

        for md_file in self.corpus_root.rglob("*.md"):
            # Skip meta-documentation files
            if md_file.name in EXCLUDED_FILES:
                continue

            # Get file size
            size_bytes = md_file.stat().st_size

            # Determine category from path
            try:
                relative_path = md_file.relative_to(self.corpus_root)
                category = (
                    str(relative_path.parts[0])
                    if len(relative_path.parts) > 1
                    else "root"
                )
            except ValueError:
                category = "unknown"

            documents.append(
                {
                    "path": md_file,
                    "name": md_file.name,
                    "size_bytes": size_bytes,
                    "category": category,
                    "relative_path": str(md_file.relative_to(self.corpus_root)),
                }
            )

        return documents

    def categorize_by_size(self, documents: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize documents by size.

        Size categories:
        - Tiny: < 1KB
        - Small: 1-5KB
        - Medium: 5-20KB
        - Large: 20-100KB
        - Very Large: > 100KB

        Args:
            documents: List of document metadata

        Returns:
            Dictionary mapping size category to documents
        """
        categories = {
            "tiny": [],
            "small": [],
            "medium": [],
            "large": [],
            "very_large": [],
        }

        for doc in documents:
            size_kb = doc["size_bytes"] / 1024

            if size_kb < 1:
                categories["tiny"].append(doc)
            elif size_kb < 5:
                categories["small"].append(doc)
            elif size_kb < 20:
                categories["medium"].append(doc)
            elif size_kb < 100:
                categories["large"].append(doc)
            else:
                categories["very_large"].append(doc)

        return categories

    def select_by_size(
        self, target_counts: Dict[str, int] = None
    ) -> Dict[str, List[Dict]]:
        """
        Select representative documents by size category.

        Args:
            target_counts: Target number of documents per size category
                          Default: {"tiny": 10, "small": 15, "medium": 15,
                                   "large": 10, "very_large": 5}

        Returns:
            Dictionary mapping size category to selected documents
        """
        if target_counts is None:
            target_counts = {
                "tiny": 10,
                "small": 15,
                "medium": 15,
                "large": 10,
                "very_large": 5,
            }

        documents = self.scan_corpus()
        categorized = self.categorize_by_size(documents)

        selected = {}
        for category, target_count in target_counts.items():
            docs = categorized.get(category, [])
            # Sort by size for consistent selection
            docs.sort(key=lambda d: d["size_bytes"])
            # Select evenly distributed samples
            if len(docs) <= target_count:
                selected[category] = docs
            else:
                step = len(docs) / target_count
                indices = [int(i * step) for i in range(target_count)]
                selected[category] = [docs[i] for i in indices]

        return selected

    def select_by_category(
        self, categories: List[str] = None, samples_per_category: int = 10
    ) -> Dict[str, List[Dict]]:
        """
        Select documents by content category.

        Args:
            categories: List of category names to select from
                       If None, selects from all categories
            samples_per_category: Number of samples to select per category

        Returns:
            Dictionary mapping category to selected documents
        """
        documents = self.scan_corpus()

        # Group by category
        by_category = {}
        for doc in documents:
            cat = doc["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(doc)

        # Filter to requested categories if specified
        if categories:
            by_category = {k: v for k, v in by_category.items() if k in categories}

        # Sample from each category
        selected = {}
        for category, docs in by_category.items():
            docs.sort(key=lambda d: d["size_bytes"])
            if len(docs) <= samples_per_category:
                selected[category] = docs
            else:
                step = len(docs) / samples_per_category
                indices = [int(i * step) for i in range(samples_per_category)]
                selected[category] = [docs[i] for i in indices]

        return selected

    def get_all_documents(self) -> List[Dict]:
        """
        Get all valid documents from corpus.

        Returns:
            List of all document metadata
        """
        return self.scan_corpus()

    def load_document(self, doc_metadata: Dict) -> str:
        """
        Load document content.

        Args:
            doc_metadata: Document metadata dictionary with 'path' key

        Returns:
            Document content as string
        """
        path = doc_metadata["path"]
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
