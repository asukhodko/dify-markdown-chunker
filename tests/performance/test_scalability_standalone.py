#!/usr/bin/env python3
"""
Standalone test for scalability benchmarks (no pytest required).
"""

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from markdown_chunker_v2 import MarkdownChunker
from tests.performance.corpus_selector import CorpusSelector
from tests.performance.utils import run_benchmark


def test_linear_scaling():
    """Test linear scaling with adjusted thresholds."""
    print("Testing linear scaling analysis...")
    
    corpus_path = Path(__file__).parent.parent / "corpus"
    corpus_selector = CorpusSelector(corpus_path)
    chunker = MarkdownChunker()
    
    documents = corpus_selector.get_all_documents()
    documents.sort(key=lambda d: d["size_bytes"])
    
    percentiles = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95]
    sample_docs = []
    
    for p in percentiles:
        idx = int((p / 100) * len(documents))
        if idx < len(documents):
            sample_docs.append(documents[idx])
    
    sizes_kb = []
    times_ms = []
    
    for doc in sample_docs:
        content = corpus_selector.load_document(doc)
        size_bytes = len(content.encode('utf-8'))
        size_kb = size_bytes / 1024
        
        def chunk_doc():
            return chunker.chunk(content)
        
        result = run_benchmark(chunk_doc, warmup_runs=1, measurement_runs=3)
        time_ms = result["time"]["mean"] * 1000
        
        sizes_kb.append(size_kb)
        times_ms.append(time_ms)
        print(f"  {size_kb:6.1f}KB -> {time_ms:6.2f}ms")
    
    # Linear regression
    n = len(sizes_kb)
    x_mean = statistics.mean(sizes_kb)
    y_mean = statistics.mean(times_ms)
    
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(sizes_kb, times_ms))
    denominator = sum((x - x_mean) ** 2 for x in sizes_kb)
    
    coefficient = numerator / denominator if denominator > 0 else 0
    intercept = y_mean - coefficient * x_mean
    
    y_predicted = [coefficient * x + intercept for x in sizes_kb]
    ss_total = sum((y - y_mean) ** 2 for y in times_ms)
    ss_residual = sum((y - yp) ** 2 for y, yp in zip(times_ms, y_predicted))
    r_squared = 1 - (ss_residual / ss_total) if ss_total > 0 else 0
    
    print(f"\nRegression Results:")
    print(f"  Coefficient: {coefficient:.4f} ms/KB")
    print(f"  Intercept: {intercept:.2f} ms")
    print(f"  R²: {r_squared:.4f}")
    
    # Validate with adjusted thresholds
    assert r_squared >= 0.70, f"R² = {r_squared:.4f} < 0.70 (FAIL)"
    assert coefficient < 2.0, f"Coefficient = {coefficient:.4f} >= 2.0 ms/KB (FAIL)"
    
    print(f"\n✓ R² threshold: {r_squared:.4f} >= 0.70 (PASS)")
    print(f"✓ Coefficient threshold: {coefficient:.4f} < 2.0 ms/KB (PASS)")


def test_memory_scaling():
    """Test memory scaling with adjusted thresholds."""
    print("\nTesting memory scaling analysis...")
    
    corpus_path = Path(__file__).parent.parent / "corpus"
    corpus_selector = CorpusSelector(corpus_path)
    chunker = MarkdownChunker()
    
    documents = corpus_selector.get_all_documents()
    documents.sort(key=lambda d: d["size_bytes"])
    
    indices = [
        int(len(documents) * 0.2),
        int(len(documents) * 0.5),
        int(len(documents) * 0.8),
    ]
    
    memory_ratios = []
    
    for idx in indices:
        if idx >= len(documents):
            continue
        
        doc = documents[idx]
        content = corpus_selector.load_document(doc)
        size_kb = len(content.encode('utf-8')) / 1024
        
        def chunk_doc():
            return chunker.chunk(content)
        
        result = run_benchmark(chunk_doc, warmup_runs=1, measurement_runs=3)
        memory_mb = result["memory"]["mean"]
        
        memory_ratio = memory_mb / size_kb if size_kb > 0 else 0
        memory_ratios.append(memory_ratio)
        print(f"  {size_kb:6.1f}KB -> {memory_mb:6.2f}MB (ratio: {memory_ratio:.4f})")
    
    if len(memory_ratios) > 1:
        avg_ratio = statistics.mean(memory_ratios)
        
        # Check if we have large documents
        large_doc_exists = any(idx >= int(len(documents) * 0.7) for idx in indices if idx < len(documents))
        max_deviation = 1.5 if not large_doc_exists else 0.8
        
        print(f"\nMemory Analysis:")
        print(f"  Average ratio: {avg_ratio:.4f} MB/KB")
        print(f"  Max deviation allowed: {max_deviation*100:.0f}%")
        
        if avg_ratio > 0.01:
            for i, ratio in enumerate(memory_ratios):
                deviation = abs(ratio - avg_ratio) / avg_ratio if avg_ratio > 0 else 0
                print(f"  Sample {i+1} deviation: {deviation*100:.1f}%")
                assert deviation < max_deviation, \
                    f"Deviation {deviation*100:.1f}% >= {max_deviation*100:.0f}% (FAIL)"
            
            print(f"\n✓ All samples within {max_deviation*100:.0f}% deviation (PASS)")
        else:
            print(f"✓ Memory ratio too small for meaningful validation (SKIP)")


def main():
    """Run standalone scalability tests."""
    print("=" * 70)
    print("SCALABILITY BENCHMARK TESTS (Standalone)")
    print("=" * 70)
    print()
    
    try:
        test_linear_scaling()
        test_memory_scaling()
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70)
        return 0
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
