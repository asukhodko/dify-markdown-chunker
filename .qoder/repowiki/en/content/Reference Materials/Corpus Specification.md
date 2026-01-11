# Corpus Specification

<cite>
**Referenced Files in This Document**   
- [README.md](file://tests/corpus/README.md)
- [USAGE.md](file://tests/corpus/USAGE.md)
- [INDEX.md](file://tests/corpus/INDEX.md)
- [metadata.csv](file://tests/corpus/metadata.csv)
- [metadata_index.json](file://tests/corpus/metadata_index.json)
- [changelogs_003.md](file://tests/corpus/changelogs/changelogs_003.md)
- [changelogs_003.md.meta.json](file://tests/corpus/changelogs/changelogs_003.md.meta.json)
- [etcd.md](file://tests/corpus/github_readmes/go/etcd.md)
- [etcd.md.meta.json](file://tests/corpus/github_readmes/go/etcd.md.meta.json)
- [unstructured_000.md](file://tests/corpus/personal_notes/unstructured/unstructured_000.md)
- [deep_nesting.md](file://tests/corpus/nested_fencing/deep_nesting.md)
- [deep_nesting.md.meta.json](file://tests/corpus/nested_fencing/deep_nesting.md.meta.json)
- [mixed_content_004.md](file://tests/corpus/mixed_content/mixed_content_004.md)
- [mixed_content_004.md.meta.json](file://tests/corpus/mixed_content/mixed_content_004.md.meta.json)
- [research_notes_007.md](file://tests/corpus/research_notes/research_notes_007.md)
- [research_notes_007.md.meta.json](file://tests/corpus/research_notes/research_notes_007.md.meta.json)
- [calculus-analysis.md](file://tests/corpus/scientific/calculus-analysis.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Taxonomy of Document Types](#taxonomy-of-document-types)
3. [Metadata Schema](#metadata-schema)
4. [Corpus Composition and Statistics](#corpus-composition-and-statistics)
5. [Quality Metrics and Validation Procedures](#quality-metrics-and-validation-procedures)
6. [Usage for Testing and Benchmarking](#usage-for-testing-and-benchmarking)
7. [Extending the Corpus](#extending-the-corpus)
8. [Data Lifecycle Management](#data-lifecycle-management)
9. [Conclusion](#conclusion)

## Introduction

The test corpus specification for dify-markdown-chunker-1 defines a comprehensive collection of markdown documents designed to evaluate the performance, accuracy, and robustness of markdown chunking algorithms. The corpus contains over 470 documents organized into nine distinct categories, each representing different types of real-world markdown content. This documentation provides a detailed overview of the corpus structure, metadata schema, quality validation procedures, and usage guidelines for testing, benchmarking, and feature validation.

The corpus serves as a standardized benchmark for evaluating chunking strategies, measuring performance across diverse document types, and ensuring backward compatibility when introducing new features. It includes synthetic and real-world examples with comprehensive metadata to support systematic testing and analysis.

**Section sources**
- [README.md](file://tests/corpus/README.md#L1-L426)
- [INDEX.md](file://tests/corpus/INDEX.md#L1-L382)

## Taxonomy of Document Types

The corpus is organized into nine primary categories, each representing a distinct type of markdown document commonly encountered in software development and technical documentation. These categories are designed to test different aspects of the chunking algorithm, from basic parsing to complex edge cases.

### Changelogs

Changelogs represent version history documentation following standardized formats such as "Keep a Changelog." These documents are characterized by structured headers with version numbers and dates, categorized changes (Added, Changed, Fixed, Removed), and links to issues or pull requests. The changelog category contains 50 documents with an average size of 3-6KB, featuring high header density and extensive use of lists to enumerate changes across multiple versions.

**Section sources**
- [README.md](file://tests/corpus/README.md#L88-L107)
- [INDEX.md](file://tests/corpus/INDEX.md#L76-L87)
- [changelogs_003.md](file://tests/corpus/changelogs/changelogs_003.md#L1-L154)

### Engineering Blogs

Engineering blogs represent long-form technical content from technology companies and engineering teams. These documents typically range from 2,000 to 10,000 words and include code examples in multiple programming languages, architectural diagrams, performance data, and detailed technical explanations. The corpus includes 50 engineering blog posts from sources such as Netflix, Uber, Airbnb, and Stripe, featuring a mix of prose, code blocks, and tables for presenting technical information.

**Section sources**
- [README.md](file://tests/corpus/README.md#L110-L128)
- [INDEX.md](file://tests/corpus/INDEX.md#L88-L107)

### GitHub READMEs

GitHub READMEs represent project documentation from popular open-source repositories. The corpus includes 160 README files from top-starred projects across four programming languages: Python, JavaScript, Go, and Rust. These documents typically include badges, installation instructions, usage examples, API references, feature lists, and contributing guidelines. The selection criteria require repositories with more than 10,000 stars and README files larger than 1KB that contain code examples.

**Section sources**
- [README.md](file://tests/corpus/README.md#L62-L85)
- [INDEX.md](file://tests/corpus/INDEX.md#L57-L75)
- [etcd.md](file://tests/corpus/github_readmes/go/etcd.md#L1-L206)

### Mixed Content

Mixed content documents are designed to test edge cases and extreme scenarios by combining multiple content types within a single document. The 20 documents in this category include Unicode characters from multiple scripts, emoji, very wide tables (20+ columns), deeply nested lists (10+ levels), very long lines (300+ words), empty sections, and consecutive code blocks without intervening text. These documents represent the most challenging test cases for the chunking algorithm.

**Section sources**
- [README.md](file://tests/corpus/README.md#L341-L347)
- [INDEX.md](file://tests/corpus/INDEX.md#L187-L199)
- [mixed_content_004.md](file://tests/corpus/mixed_content/mixed_content_004.md#L1-L84)

### Nested Fencing

Nested fencing documents test the handling of meta-documentation with deeply nested code fences. These 20 documents demonstrate documentation about documentation, requiring triple, quadruple, and quintuple backtick nesting to properly render code examples that themselves contain fenced code blocks. The documents test nesting levels from 3 to 6 deep, with mixed fence types (backticks and tildes) and meta-documentation explaining how to write code examples.

**Section sources**
- [README.md](file://tests/corpus/README.md#L281-L328)
- [INDEX.md](file://tests/corpus/INDEX.md#L155-L165)
- [deep_nesting.md](file://tests/corpus/nested_fencing/deep_nesting.md#L1-L102)

### Personal Notes

Personal notes represent informal, unstructured markdown content such as journal entries, cheat sheets, and unstructured notes. This category contains 30 documents divided into three subcategories: unstructured notes (10 files), engineering journals (10 files), and cheat sheets (10 files). Unstructured notes lack clear organization and contain mixed topics, incomplete sentences, and personal abbreviations. Engineering journals follow a problem-solution structure with code snippets showing before-and-after implementations. Cheat sheets are dense information resources with minimal prose, featuring command reference tables and code snippets for common tasks.

**Section sources**
- [README.md](file://tests/corpus/README.md#L131-L224)
- [INDEX.md](file://tests/corpus/INDEX.md#L108-L137)
- [unstructured_000.md](file://tests/corpus/personal_notes/unstructured/unstructured_000.md#L1-L42)

### Research Notes

Research notes represent academic and research documentation with literature references, methodology sections, data tables, and analysis code. The 20 documents in this category follow a standard research paper structure with abstract, introduction, literature review, methodology, results, discussion, and conclusion sections. They include citations, statistical analysis, and code snippets for data processing and analysis, representing technical content with a formal structure.

**Section sources**
- [README.md](file://tests/corpus/README.md#L331-L338)
- [INDEX.md](file://tests/corpus/INDEX.md#L168-L186)
- [research_notes_007.md](file://tests/corpus/research_notes/research_notes_007.md#L1-L97)

### Scientific Documents

Scientific documents contain mathematical formulas, equations, and scientific notation using LaTeX syntax. These documents test the chunking algorithm's ability to handle complex mathematical expressions rendered with $$ delimiters. Examples include calculus formulas, linear algebra equations, machine learning algorithms, and physics equations. The documents require special handling to preserve the integrity of mathematical expressions during chunking.

**Section sources**
- [calculus-analysis.md](file://tests/corpus/scientific/calculus-analysis.md#L1-L314)

### Technical Documentation

Technical documentation represents official project documentation with well-structured content, API references, and configuration examples. The corpus includes 100 technical documentation files from popular projects such as Kubernetes, Docker, React, and AWS. These documents feature clear header hierarchies, code examples in multiple languages (Bash, YAML, Python, JavaScript), tables for API parameters and configuration options, and consistent formatting. They are typically 2-50KB in size and test both code-aware and structural chunking strategies.

**Section sources**
- [README.md](file://tests/corpus/README.md#L37-L59)
- [INDEX.md](file://tests/corpus/INDEX.md#L40-L56)

## Metadata Schema

Each document in the corpus is accompanied by metadata that describes its characteristics, source, and expected processing behavior. The metadata is stored in JSON format with a corresponding .meta.json file for each markdown document, as well as aggregated in metadata_index.json and metadata.csv files for bulk analysis.

### Core Metadata Fields

The metadata schema includes the following core fields for each document:

| Field | Type | Description |
|-------|------|-------------|
| filename | string | Name of the markdown file |
| category | string | Primary category (e.g., changelogs, github_readmes) |
| subcategory | string | Secondary category when applicable (e.g., go, python) |
| size_bytes | integer | File size in bytes |
| line_count | integer | Number of lines in the document |
| source | string | Source of the document (github, synthetic) |
| source_url | string | URL of the original document when applicable |
| collection_date | string | ISO timestamp when the document was collected |
| content_hash | string | SHA-256 hash of the content for deduplication |
| expected_strategy | string | Expected chunking strategy (code_aware, structural, fallback) |

**Section sources**
- [metadata_index.json](file://tests/corpus/metadata_index.json#L1-L800)
- [metadata.csv](file://tests/corpus/metadata.csv#L1-L110)

### Content Characteristic Metrics

The metadata includes quantitative metrics that describe the document's content characteristics:

| Metric | Description |
|--------|-------------|
| code_ratio | Proportion of content in code blocks (0.0 to 1.0) |
| table_count | Number of tables in the document |
| list_count | Number of list items |
| header_count | Number of headers |
| max_header_depth | Maximum header nesting level |
| code_block_count | Number of fenced code blocks |
| nesting_level | Fence nesting depth (for nested fencing documents) |

These metrics enable filtering and analysis of documents based on their structural and content properties, allowing targeted testing of specific chunking behaviors.

**Section sources**
- [metadata_index.json](file://tests/corpus/metadata_index.json#L1-L800)

## Corpus Composition and Statistics

The corpus contains 470+ documents with a total size of approximately 2.0 MB, providing comprehensive coverage of markdown document types and edge cases.

### Size Distribution

| Size Category | Range | Count | Percentage |
|---------------|-------|-------|------------|
| Tiny | < 1KB | ~20 | 4% |
| Small | 1-5KB | ~100 | 21% |
| Medium | 5-20KB | ~250 | 53% |
| Large | 20-100KB | ~90 | 19% |
| Very Large | > 100KB | ~10 | 2% |

### Category Distribution

| Category | Count | Percentage |
|---------|-------|------------|
| GitHub READMEs | 160 | 34% |
| Technical Documentation | 100 | 21% |
| Changelogs | 50 | 11% |
| Engineering Blogs | 50 | 11% |
| Mixed Content | 20 | 4% |
| Personal Notes | 30 | 6% |
| Research Notes | 20 | 4% |
| Nested Fencing | 20 | 4% |
| Debug Logs | 20 | 4% |
| **Total** | **470+** | **100%** |

### Content Characteristics

| Characteristic | High | Medium | Low |
|----------------|------|--------|-----|
| Code ratio | 100 | 150 | 210 |
| Table count | 80 | 120 | 260 |
| List ratio | 100 | 150 | 210 |
| Header depth | 150 | 180 | 130 |
| Nested fencing | 20 | 30 | 410 |

**Section sources**
- [INDEX.md](file://tests/corpus/INDEX.md#L212-L221)
- [README.md](file://tests/corpus/README.md#L348-L357)
- [metadata_index.json](file://tests/corpus/metadata_index.json#L1-L800)

## Quality Metrics and Validation Procedures

The corpus includes comprehensive validation procedures to ensure data integrity, consistency, and reliability for testing purposes.

### Validation Checklist

The corpus must pass the following validation criteria:
- Total files ≥ 400 (actual: 470+)
- All categories represented per specification
- Size distribution covers all ranges
- Content characteristics varied (code, tables, lists, structure)
- All files are valid markdown (parseable)
- Metadata complete for all files
- Expected strategies distributed across all types

**Section sources**
- [README.md](file://tests/corpus/README.md#L417-L425)
- [INDEX.md](file://tests/corpus/INDEX.md#L340-L351)

### Automated Validation

The corpus provides automated validation scripts to check chunk quality across all documents. The validation process checks for:
- Empty chunks
- Overlapping line numbers between consecutive chunks
- Missing metadata in chunks
- Strategy consistency with expected values
- Proper handling of edge cases

The validation script processes each document and reports any quality issues, saving results to a JSON file for further analysis.

```python
def validate_chunk_quality():
    """Validate chunk quality across corpus."""
    # Implementation details in USAGE.md
    pass
```

**Section sources**
- [USAGE.md](file://tests/corpus/USAGE.md#L147-L215)

## Usage for Testing and Benchmarking

The corpus supports various testing and benchmarking scenarios to evaluate the markdown chunker's performance and accuracy.

### Basic Testing

The corpus can be used for comprehensive testing of the chunking functionality across all document types:

```python
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
```

**Section sources**
- [USAGE.md](file://tests/corpus/USAGE.md#L8-L43)

### Strategy-Specific Tests

The metadata enables targeted testing of specific chunking strategies based on document characteristics:

```python
def test_code_aware_strategy():
    """Test code-aware strategy on appropriate documents."""
    # Find documents expected to use code_aware strategy
    code_docs = [
        doc for doc in metadata_index
        if doc.get("expected_strategy") == "code_aware"
    ]
    
    chunker = MarkdownChunker()
    
    for doc_meta in code_docs[:10]:  # Test subset
        # Construct file path and test chunking
        pass
```

**Section sources**
- [USAGE.md](file://tests/corpus/USAGE.md#L45-L82)

### Performance Benchmarking

The corpus supports performance benchmarking to measure chunking speed and efficiency:

```python
def benchmark_corpus():
    """Benchmark chunking performance on corpus."""
    results = []
    
    for md_file in corpus_root.rglob("*.md"):
        if md_file.name in ["README.md", "INDEX.md", "USAGE.md"]:
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
    
    # Analyze results by strategy and size
    return results
```

**Section sources**
- [USAGE.md](file://tests/corpus/USAGE.md#L84-L145)

### Regression Testing

The corpus supports regression testing to ensure backward compatibility when modifying the chunking algorithm:

```python
def test_regression():
    """Test that results match baseline."""
    if not baseline_path.exists():
        pytest.skip("No baseline results")
    
    with open(baseline_path) as f:
        baseline = json.load(f)
    
    chunker = MarkdownChunker()
    
    for doc_result in baseline:
        filename = doc_result["filename"]
        expected_chunks = doc_result["chunk_count"]
        expected_strategy = doc_result["strategy"]
        
        # Compare current results with baseline
        assert len(result.chunks) == expected_chunks
        assert result.strategy_used == expected_strategy
```

**Section sources**
- [USAGE.md](file://tests/corpus/USAGE.md#L303-L340)

## Extending the Corpus

The corpus can be extended with new document types while maintaining backward compatibility and data integrity.

### Adding New Document Types

To add a new document type:
1. Create a new subdirectory under `tests/corpus/`
2. Add markdown documents following the naming convention `category_XXX.md`
3. Generate corresponding `.meta.json` files with appropriate metadata
4. Update the `metadata_index.json` and `metadata.csv` files
5. Verify the document passes validation checks

### Maintaining Backward Compatibility

When extending the corpus:
- Preserve existing file names and directory structure
- Maintain consistent metadata schema
- Ensure new documents do not alter the behavior of existing tests
- Update baseline results when appropriate
- Document changes in the corpus version history

**Section sources**
- [INDEX.md](file://tests/corpus/INDEX.md#L353-L371)

## Data Lifecycle Management

The corpus follows a structured approach to versioning and maintenance.

### Versioning

Corpus releases are versioned to ensure reproducible testing results. Each release includes:
- Complete set of markdown documents
- Corresponding metadata files
- Baseline results for regression testing
- Collection report with statistics

### Maintenance

The corpus is maintained through automated scripts that can regenerate or extend the collection:
```bash
# Full regeneration
python3 scripts/build_full_corpus.py

# Generate additional documents
python3 -c "
from scripts.corpus_builder.synthetic_generator import SyntheticGenerator
gen = SyntheticGenerator(Path('tests/corpus/debug_logs'), category='debug_logs')
gen.generate(5)  # Generate 5 more debug logs
"
```

**Section sources**
- [INDEX.md](file://tests/corpus/INDEX.md#L353-L371)

## Conclusion

The dify-markdown-chunker-1 test corpus provides a comprehensive and standardized benchmark for evaluating markdown chunking algorithms. With over 470 documents across nine categories, detailed metadata, and automated validation procedures, the corpus enables thorough testing of chunking strategies, performance benchmarking, and regression testing. The structured taxonomy, quality metrics, and extension guidelines ensure the corpus remains a valuable resource for developing and validating markdown processing tools.