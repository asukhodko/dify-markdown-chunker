# Test Corpus Usage Guide

## Overview

The test corpus contains 470+ markdown documents designed to test the Advanced Markdown Chunker across diverse content types, structures, and edge cases.

## Quick Start

### Running Tests with Corpus

```python
import pytest
from pathlib import Path
from markdown_chunker_v2 import MarkdownChunker

corpus_root = Path("tests/corpus")

@pytest.mark.parametrize(
    "md_file",
    list(corpus_root.rglob("*.md"))
)
def test_chunking_corpus(md_file):
    """Test chunking on entire corpus."""
    # Skip metadata files
    if md_file.name in ["README.md", "INDEX.md", "USAGE.md", "COLLECTION_REPORT.md"]:
        pytest.skip()
    
    chunker = MarkdownChunker()
    content = md_file.read_text()
    
    # Test basic chunking
    result = chunker.chunk(content, include_analysis=True)
    
    # Validate results
    assert len(result.chunks) > 0, f"No chunks created for {md_file}"
    assert result.strategy_used in ["code_aware", "structural", "fallback"]
    
    # Validate chunks
    for chunk in result.chunks:
        assert chunk.content.strip(), f"Empty chunk in {md_file}"
        assert chunk.start_line > 0
        assert chunk.end_line >= chunk.start_line
```

### Strategy-Specific Tests

```python
import json
from pathlib import Path

def test_code_aware_strategy():
    """Test code-aware strategy on appropriate documents."""
    corpus_root = Path("tests/corpus")
    metadata_index = json.loads(
        (corpus_root / "metadata_index.json").read_text()
    )
    
    # Find documents expected to use code_aware strategy
    code_docs = [
        doc for doc in metadata_index
        if doc.get("expected_strategy") == "code_aware"
    ]
    
    chunker = MarkdownChunker()
    
    for doc_meta in code_docs[:10]:  # Test subset
        # Construct file path
        category = doc_meta["category"]
        subcategory = doc_meta.get("subcategory")
        filename = doc_meta["filename"]
        
        if subcategory:
            file_path = corpus_root / category / subcategory / filename
        else:
            file_path = corpus_root / category / filename
        
        content = file_path.read_text()
        result = chunker.chunk(content, include_analysis=True)
        
        assert result.strategy_used == "code_aware", \
            f"Expected code_aware for {filename}, got {result.strategy_used}"
```

### Performance Benchmarking

```python
import time
import json
from pathlib import Path
from markdown_chunker_v2 import MarkdownChunker

def benchmark_corpus():
    """Benchmark chunking performance on corpus."""
    corpus_root = Path("tests/corpus")
    chunker = MarkdownChunker()
    
    results = []
    
    for md_file in corpus_root.rglob("*.md"):
        if md_file.name in ["README.md", "INDEX.md", "USAGE.md", "COLLECTION_REPORT.md"]:
            continue
        
        content = md_file.read_text()
        
        start = time.perf_counter()
        result = chunker.chunk(content, include_analysis=True)
        elapsed = time.perf_counter() - start
        
        results.append({
            "file": str(md_file.relative_to(corpus_root)),
            "size_bytes": len(content.encode("utf-8")),
            "chunks": len(result.chunks),
            "strategy": result.strategy_used,
            "time_ms": elapsed * 1000,
        })
    
    # Analyze results
    import pandas as pd
    df = pd.DataFrame(results)
    
    print("\n=== Performance by Strategy ===")
    print(df.groupby("strategy").agg({
        "time_ms": ["mean", "median", "max"],
        "chunks": "mean",
        "size_bytes": "mean",
    }).round(2))
    
    print("\n=== Performance by Size ===")
    df["size_category"] = pd.cut(
        df["size_bytes"],
        bins=[0, 1024, 5120, 20480, float("inf")],
        labels=["tiny", "small", "medium", "large+"]
    )
    print(df.groupby("size_category").agg({
        "time_ms": ["mean", "median", "max"],
    }).round(2))
    
    return df

# Run benchmark
if __name__ == "__main__":
    results_df = benchmark_corpus()
    results_df.to_csv("benchmark_results.csv", index=False)
    print("\nResults saved to benchmark_results.csv")
```

### Quality Validation

```python
import json
from pathlib import Path
from markdown_chunker_v2 import MarkdownChunker

def validate_chunk_quality():
    """Validate chunk quality across corpus."""
    corpus_root = Path("tests/corpus")
    chunker = MarkdownChunker()
    
    issues = []
    
    for md_file in corpus_root.rglob("*.md"):
        if md_file.name in ["README.md", "INDEX.md", "USAGE.md", "COLLECTION_REPORT.md"]:
            continue
        
        content = md_file.read_text()
        result = chunker.chunk(content, include_analysis=True)
        
        # Check for empty chunks
        empty_chunks = [i for i, c in enumerate(result.chunks) if not c.content.strip()]
        if empty_chunks:
            issues.append({
                "file": str(md_file.relative_to(corpus_root)),
                "issue": "empty_chunks",
                "details": f"Chunks {empty_chunks}"
            })
        
        # Check for overlapping line numbers
        for i in range(len(result.chunks) - 1):
            current = result.chunks[i]
            next_chunk = result.chunks[i + 1]
            if current.end_line >= next_chunk.start_line:
                issues.append({
                    "file": str(md_file.relative_to(corpus_root)),
                    "issue": "overlapping_lines",
                    "details": f"Chunk {i}: {current.end_line} >= Chunk {i+1}: {next_chunk.start_line}"
                })
        
        # Check for missing metadata
        for i, chunk in enumerate(result.chunks):
            if not chunk.metadata.get("strategy"):
                issues.append({
                    "file": str(md_file.relative_to(corpus_root)),
                    "issue": "missing_metadata",
                    "details": f"Chunk {i} missing strategy"
                })
    
    # Report
    if issues:
        print(f"\n❌ Found {len(issues)} quality issues:")
        for issue in issues[:10]:
            print(f"  - {issue['file']}: {issue['issue']} ({issue['details']})")
    else:
        print("\n✓ All chunks passed quality validation")
    
    return issues

# Run validation
if __name__ == "__main__":
    issues = validate_chunk_quality()
    if issues:
        import json
        with open("quality_issues.json", "w") as f:
            json.dump(issues, f, indent=2)
        print(f"\nIssues saved to quality_issues.json")
```

## Corpus Categories

### By Content Type

```python
import json
from pathlib import Path

corpus_root = Path("tests/corpus")
metadata = json.loads((corpus_root / "metadata_index.json").read_text())

# Code-heavy documents
code_heavy = [d for d in metadata if d.get("code_ratio", 0) >= 0.5]
print(f"Code-heavy: {len(code_heavy)} documents")

# Structural documents
structural = [d for d in metadata if d.get("header_count", 0) >= 5]
print(f"Highly structural: {len(structural)} documents")

# Table-rich documents
table_rich = [d for d in metadata if d.get("table_count", 0) >= 5]
print(f"Table-rich: {len(table_rich)} documents")

# Edge cases
edge_cases = [d for d in metadata if d.get("category") == "mixed_content"]
print(f"Edge cases: {len(edge_cases)} documents")
```

### By Expected Strategy

```python
import json
from pathlib import Path
from collections import Counter

corpus_root = Path("tests/corpus")
metadata = json.loads((corpus_root / "metadata_index.json").read_text())

strategies = Counter(d.get("expected_strategy") for d in metadata)
print("\nExpected strategy distribution:")
for strategy, count in strategies.most_common():
    print(f"  {strategy}: {count}")
```

## Advanced Usage

### Custom Test Scenarios

```python
def test_large_documents():
    """Test performance on large documents."""
    corpus_root = Path("tests/corpus")
    metadata = json.loads((corpus_root / "metadata_index.json").read_text())
    
    # Find large documents (> 50KB)
    large_docs = [d for d in metadata if d.get("size_bytes", 0) > 50000]
    
    chunker = MarkdownChunker()
    
    for doc_meta in large_docs:
        # Load document
        category = doc_meta["category"]
        subcategory = doc_meta.get("subcategory")
        filename = doc_meta["filename"]
        
        if subcategory:
            file_path = corpus_root / category / subcategory / filename
        else:
            file_path = corpus_root / category / filename
        
        content = file_path.read_text()
        
        # Test with timeout
        import signal
        signal.alarm(10)  # 10 second timeout
        try:
            result = chunker.chunk(content)
            signal.alarm(0)
            
            assert len(result.chunks) > 0
            print(f"✓ {filename}: {len(result.chunks)} chunks")
        except:
            signal.alarm(0)
            pytest.fail(f"Timeout or error processing {filename}")
```

### Regression Testing

```python
import json
from pathlib import Path

def test_regression():
    """Test that results match baseline."""
    corpus_root = Path("tests/corpus")
    baseline_path = corpus_root / "baseline_results.json"
    
    if not baseline_path.exists():
        pytest.skip("No baseline results")
    
    with open(baseline_path) as f:
        baseline = json.load(f)
    
    chunker = MarkdownChunker()
    
    for doc_result in baseline:
        filename = doc_result["filename"]
        expected_chunks = doc_result["chunk_count"]
        expected_strategy = doc_result["strategy"]
        
        # Find file
        file_path = corpus_root / filename
        if not file_path.exists():
            continue
        
        content = file_path.read_text()
        result = chunker.chunk(content, include_analysis=True)
        
        # Compare
        assert len(result.chunks) == expected_chunks, \
            f"Chunk count mismatch for {filename}"
        assert result.strategy_used == expected_strategy, \
            f"Strategy mismatch for {filename}"
```

## Utilities

### Generate Test Baseline

```python
import json
from pathlib import Path
from markdown_chunker_v2 import MarkdownChunker

def generate_baseline():
    """Generate baseline results for regression testing."""
    corpus_root = Path("tests/corpus")
    chunker = MarkdownChunker()
    
    baseline = []
    
    for md_file in corpus_root.rglob("*.md"):
        if md_file.name in ["README.md", "INDEX.md", "USAGE.md", "COLLECTION_REPORT.md"]:
            continue
        
        content = md_file.read_text()
        result = chunker.chunk(content, include_analysis=True)
        
        baseline.append({
            "filename": str(md_file.relative_to(corpus_root)),
            "chunk_count": len(result.chunks),
            "strategy": result.strategy_used,
            "size_bytes": len(content.encode("utf-8")),
        })
    
    with open(corpus_root / "baseline_results.json", "w") as f:
        json.dump(baseline, f, indent=2)
    
    print(f"Baseline generated for {len(baseline)} documents")

if __name__ == "__main__":
    generate_baseline()
```

### Find Problematic Documents

```python
import json
from pathlib import Path
from markdown_chunker_v2 import MarkdownChunker

def find_problematic_documents():
    """Find documents that cause issues."""
    corpus_root = Path("tests/corpus")
    chunker = MarkdownChunker()
    
    problematic = []
    
    for md_file in corpus_root.rglob("*.md"):
        if md_file.name in ["README.md", "INDEX.md", "USAGE.md", "COLLECTION_REPORT.md"]:
            continue
        
        content = md_file.read_text()
        
        try:
            result = chunker.chunk(content, include_analysis=True)
            
            # Check for fallback usage
            if result.fallback_used:
                problematic.append({
                    "file": str(md_file.relative_to(corpus_root)),
                    "issue": "fallback_used",
                    "fallback_level": result.fallback_level,
                })
            
            # Check for errors
            if result.errors:
                problematic.append({
                    "file": str(md_file.relative_to(corpus_root)),
                    "issue": "errors",
                    "errors": result.errors,
                })
        
        except Exception as e:
            problematic.append({
                "file": str(md_file.relative_to(corpus_root)),
                "issue": "exception",
                "error": str(e),
            })
    
    return problematic

if __name__ == "__main__":
    issues = find_problematic_documents()
    if issues:
        print(f"Found {len(issues)} problematic documents:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("No problematic documents found")
```

## Maintenance

### Corpus Management

Корпус является частью тестового набора и обновляется автоматически при необходимости.

## See Also

- [INDEX.md](INDEX.md) - Complete corpus documentation
- [README.md](README.md) - Original specification
- [metadata.csv](metadata.csv) - Corpus metadata in CSV format
- [metadata_index.json](metadata_index.json) - Full metadata in JSON
