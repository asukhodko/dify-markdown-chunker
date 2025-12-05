# Quality Metrics Definition

## Overview

Определение объективных метрик для оценки качества markdown chunking. Метрики разделены на автоматические (вычисляемые программно) и ручные (требующие экспертной оценки).

## Automatic Metrics

### 1. Semantic Coherence Score (SCS)

**Purpose:** Измерить, насколько семантически связан контент внутри чанков по сравнению с контентом между чанками.

**Formula:**
```
SCS = avg(intra_chunk_similarity) / avg(inter_chunk_similarity)
```

**Implementation:**
```python
from sentence_transformers import SentenceTransformer
import numpy as np

def calculate_scs(chunks: list[str]) -> float:
    """
    Calculate Semantic Coherence Score.
    
    Higher score = better semantic separation.
    Score > 1.0 means chunks are more coherent internally than externally.
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Calculate intra-chunk similarity
    intra_similarities = []
    for chunk in chunks:
        sentences = split_into_sentences(chunk)
        if len(sentences) < 2:
            continue
        embeddings = model.encode(sentences)
        # Average pairwise similarity within chunk
        sim = np.mean([
            cosine_similarity(embeddings[i], embeddings[j])
            for i in range(len(embeddings))
            for j in range(i+1, len(embeddings))
        ])
        intra_similarities.append(sim)
    
    # Calculate inter-chunk similarity
    chunk_embeddings = model.encode(chunks)
    inter_similarities = [
        cosine_similarity(chunk_embeddings[i], chunk_embeddings[j])
        for i in range(len(chunk_embeddings))
        for j in range(i+1, len(chunk_embeddings))
    ]
    
    avg_intra = np.mean(intra_similarities) if intra_similarities else 0
    avg_inter = np.mean(inter_similarities) if inter_similarities else 1
    
    return avg_intra / avg_inter if avg_inter > 0 else float('inf')
```

**Interpretation:**
| SCS Value | Quality |
|-----------|---------|
| < 0.8 | Poor - chunks not coherent |
| 0.8 - 1.0 | Fair - similar to random |
| 1.0 - 1.5 | Good - some semantic separation |
| 1.5 - 2.0 | Very Good - clear semantic boundaries |
| > 2.0 | Excellent - strong semantic coherence |

---

### 2. Context Preservation Score (CPS)

**Purpose:** Измерить, насколько хорошо сохраняется контекст между связанными элементами (код + объяснение).

**Formula:**
```
CPS = (code_blocks_with_context / total_code_blocks) * 100
```

**Implementation:**
```python
import re

def calculate_cps(chunks: list[str], original_text: str) -> float:
    """
    Calculate Context Preservation Score.
    
    Measures how many code blocks have their explanatory context preserved.
    """
    # Find all code blocks in original
    code_block_pattern = r'```[\w]*\n.*?\n```'
    original_blocks = re.findall(code_block_pattern, original_text, re.DOTALL)
    
    if not original_blocks:
        return 100.0  # No code blocks = perfect score
    
    blocks_with_context = 0
    
    for block in original_blocks:
        # Find which chunk contains this block
        for chunk in chunks:
            if block in chunk:
                # Check if chunk has explanatory text
                # (text before or after the code block)
                chunk_without_code = chunk.replace(block, '')
                text_content = chunk_without_code.strip()
                
                # Context is preserved if there's meaningful text
                if len(text_content) > 50:  # At least 50 chars of context
                    blocks_with_context += 1
                break
    
    return (blocks_with_context / len(original_blocks)) * 100
```

**Interpretation:**
| CPS Value | Quality |
|-----------|---------|
| < 50% | Poor - most code lacks context |
| 50-70% | Fair - some context preserved |
| 70-85% | Good - most code has context |
| 85-95% | Very Good - nearly all code has context |
| > 95% | Excellent - all code has context |

---

### 3. Boundary Quality Score (BQS)

**Purpose:** Измерить качество границ чанков — не разрываются ли предложения, блоки кода, таблицы.

**Formula:**
```
BQS = 1 - (bad_boundaries / total_boundaries)
```

**Bad Boundary Types:**
1. Mid-sentence split (sentence continues in next chunk)
2. Mid-code-block split (code block is split)
3. Mid-table split (table is split)
4. Mid-list split (list item continues in next chunk)

**Implementation:**
```python
def calculate_bqs(chunks: list[str]) -> float:
    """
    Calculate Boundary Quality Score.
    
    Measures how clean the chunk boundaries are.
    """
    if len(chunks) <= 1:
        return 1.0
    
    bad_boundaries = 0
    total_boundaries = len(chunks) - 1
    
    for i in range(len(chunks) - 1):
        current = chunks[i]
        next_chunk = chunks[i + 1]
        
        # Check for mid-sentence split
        if is_mid_sentence(current, next_chunk):
            bad_boundaries += 1
            continue
        
        # Check for mid-code-block split
        if is_mid_code_block(current, next_chunk):
            bad_boundaries += 1
            continue
        
        # Check for mid-table split
        if is_mid_table(current, next_chunk):
            bad_boundaries += 1
            continue
        
        # Check for mid-list split
        if is_mid_list(current, next_chunk):
            bad_boundaries += 0.5  # Less severe
    
    return 1 - (bad_boundaries / total_boundaries)

def is_mid_sentence(current: str, next_chunk: str) -> bool:
    """Check if boundary splits a sentence."""
    # Current chunk doesn't end with sentence terminator
    current_stripped = current.rstrip()
    if not current_stripped:
        return False
    
    last_char = current_stripped[-1]
    sentence_terminators = '.!?:"\''
    
    # If ends with code block or list, it's OK
    if current_stripped.endswith('```') or current_stripped.endswith('~~~'):
        return False
    
    # Check if next chunk starts with lowercase (continuation)
    next_stripped = next_chunk.lstrip()
    if next_stripped and next_stripped[0].islower():
        return True
    
    return last_char not in sentence_terminators

def is_mid_code_block(current: str, next_chunk: str) -> bool:
    """Check if boundary splits a code block."""
    # Count opening and closing fences in current chunk
    open_fences = len(re.findall(r'^```', current, re.MULTILINE))
    close_fences = len(re.findall(r'^```$', current, re.MULTILINE))
    
    # If unbalanced, we're in the middle of a code block
    return open_fences > close_fences

def is_mid_table(current: str, next_chunk: str) -> bool:
    """Check if boundary splits a table."""
    # Check if current ends with table row and next starts with table row
    current_lines = current.strip().split('\n')
    next_lines = next_chunk.strip().split('\n')
    
    if not current_lines or not next_lines:
        return False
    
    current_ends_table = '|' in current_lines[-1]
    next_starts_table = '|' in next_lines[0]
    
    return current_ends_table and next_starts_table
```

**Interpretation:**
| BQS Value | Quality |
|-----------|---------|
| < 0.7 | Poor - many bad boundaries |
| 0.7 - 0.85 | Fair - some issues |
| 0.85 - 0.95 | Good - few issues |
| 0.95 - 0.99 | Very Good - rare issues |
| 1.0 | Excellent - perfect boundaries |

---

### 4. Size Distribution Score (SDS)

**Purpose:** Измерить, насколько размеры чанков оптимальны для RAG retrieval.

**Formula:**
```
SDS = chunks_in_optimal_range / total_chunks
```

**Optimal Range:** 500-2000 characters (configurable based on use case)

**Implementation:**
```python
def calculate_sds(
    chunks: list[str],
    min_optimal: int = 500,
    max_optimal: int = 2000
) -> float:
    """
    Calculate Size Distribution Score.
    
    Measures what percentage of chunks are in the optimal size range.
    """
    if not chunks:
        return 0.0
    
    optimal_count = sum(
        1 for chunk in chunks
        if min_optimal <= len(chunk) <= max_optimal
    )
    
    return optimal_count / len(chunks)

def get_size_distribution(chunks: list[str]) -> dict:
    """Get detailed size distribution."""
    sizes = [len(chunk) for chunk in chunks]
    
    return {
        'min': min(sizes),
        'max': max(sizes),
        'mean': np.mean(sizes),
        'median': np.median(sizes),
        'std': np.std(sizes),
        'tiny': sum(1 for s in sizes if s < 200),
        'small': sum(1 for s in sizes if 200 <= s < 500),
        'optimal': sum(1 for s in sizes if 500 <= s <= 2000),
        'large': sum(1 for s in sizes if 2000 < s <= 4000),
        'very_large': sum(1 for s in sizes if s > 4000),
    }
```

**Interpretation:**
| SDS Value | Quality |
|-----------|---------|
| < 0.5 | Poor - most chunks suboptimal |
| 0.5 - 0.7 | Fair - half optimal |
| 0.7 - 0.85 | Good - most optimal |
| 0.85 - 0.95 | Very Good - nearly all optimal |
| > 0.95 | Excellent - all optimal |

---

### 5. Overall Quality Score (OQS)

**Purpose:** Комбинированная метрика качества.

**Formula:**
```
OQS = (SCS_norm * 0.25) + (CPS * 0.30) + (BQS * 0.30) + (SDS * 0.15)
```

**Weights Rationale:**
- CPS (30%): Context preservation is critical for RAG
- BQS (30%): Clean boundaries prevent information loss
- SCS (25%): Semantic coherence improves retrieval
- SDS (15%): Size optimization is important but secondary

**Implementation:**
```python
def calculate_oqs(chunks: list[str], original_text: str) -> dict:
    """Calculate Overall Quality Score with all components."""
    scs = calculate_scs(chunks)
    cps = calculate_cps(chunks, original_text)
    bqs = calculate_bqs(chunks)
    sds = calculate_sds(chunks)
    
    # Normalize SCS to 0-100 scale (cap at 2.0 = 100)
    scs_norm = min(scs / 2.0, 1.0) * 100
    
    oqs = (scs_norm * 0.25) + (cps * 0.30) + (bqs * 100 * 0.30) + (sds * 100 * 0.15)
    
    return {
        'scs': scs,
        'scs_normalized': scs_norm,
        'cps': cps,
        'bqs': bqs,
        'sds': sds,
        'oqs': oqs
    }
```

---

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

### Bad Split Count

**Definition:** Number of boundaries that cause information loss or confusion.

**Categories:**
1. **Critical:** Code block split, table split
2. **Major:** Context separation, mid-sentence
3. **Minor:** Suboptimal size, list item separation

---

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

---

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

---

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
