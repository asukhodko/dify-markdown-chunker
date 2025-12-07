# Performance Benchmark Suite

Comprehensive performance testing infrastructure for markdown_chunker_v2.

## Overview

This benchmark suite provides automated performance measurement across multiple dimensions:

- **Size-based benchmarks**: Performance across document size categories
- **Content-type benchmarks**: Performance across different content types
- **Strategy benchmarks**: Individual strategy performance analysis
- **Configuration benchmarks**: Impact of different configurations
- **Scalability analysis**: Regression analysis and scaling characteristics

## Quick Start

### Run All Benchmarks

```bash
# From project root
python tests/performance/run_all_benchmarks.py
```

### Run Specific Benchmark Category

```bash
# Size benchmarks
pytest tests/performance/test_benchmark_size.py -v

# Content type benchmarks
pytest tests/performance/test_benchmark_content_type.py -v

# Strategy benchmarks
pytest tests/performance/test_benchmark_strategy.py -v

# Configuration benchmarks
pytest tests/performance/test_benchmark_config.py -v

# Scalability analysis
pytest tests/performance/test_benchmark_scalability.py -v
```

## Benchmark Categories

### 1. Size-Based Benchmarks (`test_benchmark_size.py`)

Tests processing performance across document size categories:

- Tiny (< 1KB)
- Small (1-5KB)
- Medium (5-20KB)
- Large (20-100KB)
- Very Large (> 100KB)

**Metrics Measured**:
- Processing time (mean, min, max, stddev)
- Throughput (KB/s)
- Memory usage
- Chunk statistics

### 2. Content-Type Benchmarks (`test_benchmark_content_type.py`)

Tests performance across different content categories:

- Technical documentation
- GitHub READMEs
- Changelogs
- Engineering blogs
- Personal notes
- Debug logs
- Mixed content

**Metrics Measured**:
- Processing time per category
- Strategy selection patterns
- Chunk quality metrics

### 3. Strategy Benchmarks (`test_benchmark_strategy.py`)

Tests individual strategy performance:

- CodeAware strategy
- Structural strategy
- Fallback strategy

**Metrics Measured**:
- Strategy-specific processing time
- Overhead analysis
- Strategy comparison

### 4. Configuration Benchmarks (`test_benchmark_config.py`)

Tests impact of different configurations:

- Default configuration
- Code-heavy profile
- Structured profile
- Minimal profile
- No-overlap configuration

**Metrics Measured**:
- Configuration impact on performance
- Overlap processing overhead
- Chunk size impact

### 5. Scalability Analysis (`test_benchmark_scalability.py`)

Performs regression analysis:

- Linear regression on time vs. size
- Memory scaling analysis
- Performance projections

**Metrics Measured**:
- Regression coefficients
- R-squared values
- Projected performance for larger documents

## Output Files

Results are saved to `tests/performance/results/`:

| File | Description |
|------|-------------|
| `latest_run.json` | Complete benchmark results (JSON) |
| `performance_report.md` | Human-readable report |
| `results_all.csv` | Tabular results (CSV) |
| `baseline.json` | Baseline for regression detection |

## Infrastructure Components

### Measurement Utilities (`utils.py`)

Core measurement functions:

- `measure_time()`: Precise timing measurement
- `measure_memory()`: Peak memory tracking
- `measure_all()`: Combined timing and memory
- `run_benchmark()`: Multi-run benchmarking with warm-up
- `calculate_throughput()`: Throughput metrics
- `aggregate_results()`: Statistical aggregation

### Corpus Selector (`corpus_selector.py`)

Test document selection:

- Scans test corpus (`tests/corpus/`)
- Categorizes by size and content type
- Filters meta-documentation
- Provides representative sampling

### Results Manager (`results_manager.py`)

Results collection and reporting:

- Collects benchmark data
- Generates markdown reports
- Exports to JSON and CSV
- Tracks baselines for regression detection

## Benchmark Methodology

### Measurement Approach

Each benchmark:

1. **Warm-up runs**: 1-2 iterations to eliminate cold-start effects
2. **Measurement runs**: 3-5 iterations for statistical validity
3. **Statistical aggregation**: Mean, min, max, standard deviation
4. **Validation**: Performance threshold checks

### Test Data

- **Source**: `tests/corpus/` (470+ documents)
- **Diversity**: 9 content categories
- **Size range**: <1KB to >100KB
- **Filtering**: Excludes meta-documentation files

### Environment

Benchmarks capture environment metadata:

- Python version
- Platform information
- Timestamp
- System specs

## Performance Thresholds

Benchmarks validate against acceptance criteria:

| Metric | Threshold | Context |
|--------|-----------|---------|
| Processing time | < 100ms per 100KB | Medium documents |
| Throughput | > 1000 KB/s | Standard processing |
| Memory efficiency | < 0.2 MB per KB | Excluding base memory |
| Scaling linearity | R² > 0.95 | Up to 1MB documents |

## Adding New Benchmarks

### 1. Create Test File

```python
# tests/performance/test_benchmark_custom.py
import pytest
from .utils import run_benchmark
from .corpus_selector import CorpusSelector
from .results_manager import ResultsManager

@pytest.fixture(scope="module")
def corpus_selector():
    corpus_path = Path(__file__).parent.parent / "corpus"
    return CorpusSelector(corpus_path)

@pytest.fixture(scope="module")
def results_manager():
    results_path = Path(__file__).parent / "results"
    return ResultsManager(results_path)

class TestCustomBenchmark:
    def test_custom_metric(self, corpus_selector, results_manager):
        # Your benchmark implementation
        pass
```

### 2. Add to Runner

Update `run_all_benchmarks.py`:

```python
test_files = [
    # ... existing tests
    "tests/performance/test_benchmark_custom.py",
]
```

### 3. Document Results

Update report formatting in `results_manager.py` if needed.

## Interpreting Results

### Time Metrics

- **Mean**: Average performance (primary metric)
- **Min**: Best case performance
- **Max**: Worst case performance
- **Stddev**: Consistency indicator (lower is better)

### Throughput

- **KB/s**: Kilobytes processed per second
- **Chunks/s**: Chunks generated per second

### Memory

- **Peak MB**: Maximum memory during processing
- **MB per KB**: Memory efficiency ratio

### Regression Analysis

- **Coefficient**: Time (ms) per KB of input
- **Intercept**: Base overhead (ms)
- **R²**: Linear fit quality (1.0 = perfect linear)

## Troubleshooting

### Benchmarks Too Slow

- Reduce sample sizes in corpus selector
- Run specific categories instead of full suite
- Use smaller measurement_runs count

### Inconsistent Results

- Ensure system is idle during benchmarking
- Increase warm-up runs
- Increase measurement runs for better averaging

### Out of Memory

- Test on smaller documents
- Adjust corpus selector sampling
- Run categories separately

## CI Integration

For continuous integration:

```yaml
# Example GitHub Actions
- name: Run performance benchmarks
  run: |
    python tests/performance/run_all_benchmarks.py
    
- name: Check for regressions
  run: |
    python -m pytest tests/performance/ --benchmark-only
```

## Related Documentation

- [Performance Guide](../../docs/guides/performance.md) - Performance documentation
- [Testing Guide](../../docs/guides/testing-guide.md) - General testing approach
- [Developer Guide](../../docs/guides/developer-guide.md) - Development practices

---

**For Latest Results**: Check `tests/performance/results/performance_report.md` after running benchmarks.
