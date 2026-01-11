# Metrics Definition

<cite>
**Referenced Files in This Document**   
- [04_metrics_definition.md](file://docs/research/04_metrics_definition.md)
</cite>

## Table of Contents
1. [Overview](#overview)
2. [Automatic Metrics](#automatic-metrics)
3. [Manual Metrics](#manual-metrics)
4. [Baseline Measurements](#baseline-measurements)
5. [Comparison Protocol](#comparison-protocol)
6. [Tools Implementation](#tools-implementation)

## Overview

The metrics framework for dify-markdown-chunker-1 is designed to objectively evaluate the quality of markdown chunking. The framework includes both automatic metrics (computed programmatically) and manual metrics (requiring expert evaluation). These metrics assess various aspects of chunking quality, including semantic coherence, context preservation, structural integrity, and processing efficiency. The metrics are used to validate chunking accuracy and ensure optimal performance for Retrieval-Augmented Generation (RAG) systems.

**Section sources**
- [04_metrics_definition.md](file://docs/research/04_metrics_definition.md#L1-L6)

## Automatic Metrics

### 1. Semantic Coherence Score (SCS)

**Purpose:** Measures how semantically related the content within chunks is compared to the content between chunks.

**Formula:**
```
SCS = avg(intra_chunk_similarity) / avg(inter_chunk_similarity)
```

**Implementation Details:**
- Uses the SentenceTransformer model 'all-MiniLM-L6-v2' to generate embeddings
- Calculates intra-chunk similarity by averaging pairwise cosine similarities between sentence embeddings within each chunk
- Calculates inter-chunk similarity by averaging cosine similarities between chunk embeddings
- Returns the ratio of average intra-chunk similarity to average inter-chunk similarity

**Interpretation:**
| SCS Value | Quality |
|-----------|---------|
| < 0.8 | Poor - chunks not coherent |
| 0.8 - 1.0 | Fair - similar to random |
| 1.0 - 1.5 | Good - some semantic separation |
| 1.5 - 2.0 | Very Good - clear semantic boundaries |
| > 2.0 | Excellent - strong semantic coherence |

**Section sources**
- [04_metrics_definition.md](file://docs/research/04_metrics_definition.md#L9-L69)

### 2. Context Preservation Score (CPS)

**Purpose:** Measures how well context is preserved between related elements, particularly code blocks and their explanatory text.

**Formula:**
```
CPS = (code_blocks_with_context / total_code_blocks) * 100
```

**Implementation Details:**
- Identifies code blocks in the original text using regex pattern matching
- For each code block, checks if it appears in a chunk with sufficient explanatory text (at least 50 characters)
- Calculates the percentage of code blocks that have their context preserved

**Interpretation:**
| CPS Value | Quality |
|-----------|---------|
| < 50% | Poor - most code lacks context |
| 50-70% | Fair - some context preserved |
| 70-85% | Good - most code has context |
| 85-95% | Very Good - nearly all code has context |
| > 95% | Excellent - all code has context |

**Section sources**
- [04_metrics_definition.md](file://docs/research/04_metrics_definition.md#L72-L125)

### 3. Boundary Quality Score (BQS)

**Purpose:** Measures the quality of chunk boundaries, specifically whether sentences, code blocks, tables, or lists are inappropriately split.

**Formula:**
```
BQS = 1 - (bad_boundaries / total_boundaries)
```

**Bad Boundary Types:**
1. Mid-sentence split (sentence continues in next chunk)
2. Mid-code-block split (code block is split)
3. Mid-table split (table is split)
4. Mid-list split (list item continues in next chunk)

**Implementation Details:**
- Evaluates each boundary between consecutive chunks
- Checks for mid-sentence splits by examining sentence terminators and capitalization patterns
- Detects mid-code-block splits by counting opening and closing code fences
- Identifies mid-table splits by checking if both chunks contain table rows
- Assigns different weights to different types of bad boundaries (mid-list splits are less severe)

**Interpretation:**
| BQS Value | Quality |
|-----------|---------|
| < 0.7 | Poor - many bad boundaries |
| 0.7 - 0.85 | Fair - some issues |
| 0.85 - 0.95 | Good - few issues |
| 0.95 - 0.99 | Very Good - rare issues |
| 1.0 | Excellent - perfect boundaries |

**Section sources**
- [04_metrics_definition.md](file://docs/research/04_metrics_definition.md#L128-L235)

### 4. Size Distribution Score (SDS)

**Purpose:** Measures how well chunk sizes align with the optimal range for RAG retrieval.

**Formula:**
```
SDS = chunks_in_optimal_range / total_chunks
```

**Optimal Range:** 500-2000 characters (configurable based on use case)

**Implementation Details:**
- Calculates the percentage of chunks that fall within the optimal size range
- Provides detailed size distribution statistics including min, max, mean, median, and standard deviation
- Categorizes chunks into size categories: tiny (<200), small (200-500), optimal (500-2000), large (2000-4000), and very large (>4000)

**Interpretation:**
| SDS Value | Quality |
|-----------|---------|
| < 0.5 | Poor - most chunks suboptimal |
| 0.5 - 0.7 | Fair - half optimal |
| 0.7 - 0.85 | Good - most optimal |
| 0.85 - 0.95 | Very Good - nearly all optimal |
| > 0.95 | Excellent - all optimal |

**Section sources**
- [04_metrics_definition.md](file://docs/research/04_metrics_definition.md#L238-L297)

### 5. Overall Quality Score (OQS)

**Purpose:** Combined metric that provides an overall assessment of chunking quality.

**Formula:**
```
OQS = (SCS_norm * 0.25) + (CPS * 0.30) + (BQS * 0.30) + (SDS * 0.15)
```

**Weights Rationale:**
- CPS (30%): Context preservation is critical for RAG
- BQS (30%): Clean boundaries prevent information loss
- SCS (25%): Semantic coherence improves retrieval
- SDS (15%): Size optimization is important but secondary

**Implementation Details:**
- Normalizes SCS to a 0-100 scale (capped at 2.0 = 100)
- Combines normalized SCS, CPS, BQS, and SDS using weighted sum
- Returns a comprehensive quality assessment with individual component scores

**Section sources**
- [04_metrics_definition.md](file://docs/research/04_metrics_definition.md#L300-L337)

## Manual Metrics

### Expert Rating (1-5 Scale)

**Criteria:**
| Score | Description |
|-------|-------------|
| 1 | Poor: Major issues, unusable for RAG |
| 2 | Fair: Significant issues, limited usefulness |
| 3 | Good: Some issues, generally usable |
| 4 | Very Good: Minor issues, high quality |
| 5 | Excellent: No issues, optimal chunking |

**Evaluation Checklist:**
- [ ] Code blocks intact?
- [ ] Tables intact?
- [ ] Lists preserved?
- [ ] Context maintained?
- [ ] Sizes appropriate?
- [ ] Headers with content?

**Section sources**
- [04_metrics_definition.md](file://docs/research/04_metrics_definition.md#L343-L361)

### Bad Split Count

**Definition:** Number of boundaries that cause information loss or confusion.

**Categories:**
1. **Critical:** Code block split, table split
2. **Major:** Context separation, mid-sentence
3. **Minor:** Suboptimal size, list item separation

**Section sources**
- [04_metrics_definition.md](file://docs/research/04_metrics_definition.md#L362-L370)

## Baseline Measurements (v2.0)

### Test Configuration
```python
config = ChunkConfig(
    max_chunk_size=2000,
    min_chunk_size=200,
    overlap_size=100,
    preserve_atomic_blocks=True
)
```

### Expected Baseline (to be measured)
| Metric | Expected Range | Target |
|--------|----------------|--------|
| SCS | 1.2 - 1.8 | > 1.5 |
| CPS | 70% - 90% | > 85% |
| BQS | 0.85 - 0.95 | > 0.90 |
| SDS | 0.60 - 0.80 | > 0.75 |
| OQS | 70 - 85 | > 80 |

### Measurement Protocol
1. Run chunker on entire corpus (410 documents)
2. Calculate metrics for each document
3. Aggregate by category
4. Report mean, median, std for each metric
5. Identify outliers and failure cases

**Section sources**
- [04_metrics_definition.md](file://docs/research/04_metrics_definition.md#L373-L402)

## Comparison Protocol

### vs Competitors
1. Select 50 representative documents from corpus
2. Run each chunker with comparable settings
3. Calculate all metrics
4. Statistical comparison (t-test for significance)
5. Document qualitative differences

### Settings Normalization
| Parameter | Our Setting | LangChain | LlamaIndex |
|-----------|-------------|-----------|------------|
| Max size | 2000 | chunk_size=2000 | - |
| Min size | 200 | - | - |
| Overlap | 100 | chunk_overlap=100 | - |

**Section sources**
- [04_metrics_definition.md](file://docs/research/04_metrics_definition.md#L405-L422)

## Tools Implementation

### Metrics Calculator

```python
# tools/metrics/calculator.py

class ChunkingMetricsCalculator:
    """Calculate all chunking quality metrics."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def calculate_all(
        self,
        chunks: list[str],
        original_text: str
    ) -> dict:
        """Calculate all metrics for a chunking result."""
        return {
            'scs': self.calculate_scs(chunks),
            'cps': self.calculate_cps(chunks, original_text),
            'bqs': self.calculate_bqs(chunks),
            'sds': self.calculate_sds(chunks),
            'oqs': self.calculate_oqs(chunks, original_text),
            'size_distribution': self.get_size_distribution(chunks),
            'chunk_count': len(chunks),
        }
    
    def compare(
        self,
        results_a: dict,
        results_b: dict,
        name_a: str = 'A',
        name_b: str = 'B'
    ) -> dict:
        """Compare two chunking results."""
        comparison = {}
        for metric in ['scs', 'cps', 'bqs', 'sds', 'oqs']:
            comparison[metric] = {
                name_a: results_a[metric],
                name_b: results_b[metric],
                'difference': results_a[metric] - results_b[metric],
                'winner': name_a if results_a[metric] > results_b[metric] else name_b
            }
        return comparison
```

**Section sources**
- [04_metrics_definition.md](file://docs/research/04_metrics_definition.md#L425-L471)

### Batch Evaluation

```python
# tools/metrics/batch.py

def evaluate_corpus(
    chunker,
    corpus_dir: str,
    output_file: str
) -> pd.DataFrame:
    """Evaluate chunker on entire corpus."""
    calculator = ChunkingMetricsCalculator()
    results = []
    
    for filepath in Path(corpus_dir).rglob('*.md'):
        text = filepath.read_text()
        chunks = chunker.chunk(text)
        
        metrics = calculator.calculate_all(
            [c.content for c in chunks],
            text
        )
        metrics['file'] = str(filepath)
        metrics['category'] = filepath.parent.name
        results.append(metrics)
    
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    return df
```

**Section sources**
- [04_metrics_definition.md](file://docs/research/04_metrics_definition.md#L473-L502)