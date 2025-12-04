#!/usr/bin/env python3
"""
Скрипт сравнения результатов чанкинга.

Используется для валидации редизайна путём сравнения результатов
новой реализации с baseline результатами текущей реализации.

Usage:
    python scripts/compare_results.py --baseline baseline.json --new new_results.json
    python scripts/compare_results.py --corpus tests/fixtures/corpus --baseline baseline.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List


# Rollback thresholds
CHUNK_COUNT_DIFF_THRESHOLD = 5.0  # >5% requires review
CONTENT_LOSS_THRESHOLD = 1.0  # >1% triggers rollback


def load_json(path: Path) -> Dict[str, Any]:
    """Загрузить JSON файл."""
    with open(path) as f:
        return json.load(f)


def save_json(data: Dict[str, Any], path: Path) -> None:
    """Сохранить JSON файл."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def compare_results(baseline: Dict[str, Any], new_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Сравнить результаты чанкинга.
    
    Returns:
        dict с метриками различий и вердиктом
    """
    differences = {
        'total_docs': len(baseline),
        'docs_compared': 0,
        'docs_with_differences': 0,
        'chunk_count_diffs': [],
        'content_loss_docs': [],
        'missing_docs': [],
        'new_docs': [],
        'verdict': 'PASS',
        'requires_review': False,
    }
    
    # Найти отсутствующие и новые документы
    baseline_docs = set(baseline.keys())
    new_docs = set(new_results.keys())
    
    differences['missing_docs'] = list(baseline_docs - new_docs)
    differences['new_docs'] = list(new_docs - baseline_docs)
    
    # Сравнить общие документы
    common_docs = baseline_docs & new_docs
    
    for doc_name in common_docs:
        old = baseline[doc_name]
        new = new_results[doc_name]
        differences['docs_compared'] += 1
        
        old_count = len(old.get('chunks', []))
        new_count = len(new.get('chunks', []))
        
        if old_count != new_count:
            diff_pct = abs(old_count - new_count) / max(old_count, 1) * 100
            
            differences['chunk_count_diffs'].append({
                'doc': doc_name,
                'old_count': old_count,
                'new_count': new_count,
                'diff_percent': round(diff_pct, 2),
            })
            
            if diff_pct > CHUNK_COUNT_DIFF_THRESHOLD:
                differences['docs_with_differences'] += 1
                differences['requires_review'] = True
        
        # Проверка content loss
        old_content = ''.join(c.get('content', '') for c in old.get('chunks', []))
        new_content = ''.join(c.get('content', '') for c in new.get('chunks', []))
        
        if len(old_content) > 0:
            content_diff_pct = (len(old_content) - len(new_content)) / len(old_content) * 100
            
            if content_diff_pct > CONTENT_LOSS_THRESHOLD:
                differences['content_loss_docs'].append({
                    'doc': doc_name,
                    'old_size': len(old_content),
                    'new_size': len(new_content),
                    'loss_percent': round(content_diff_pct, 2),
                })
                differences['verdict'] = 'ROLLBACK'
    
    # Определить финальный вердикт
    if differences['missing_docs']:
        differences['verdict'] = 'ROLLBACK'
    elif differences['content_loss_docs']:
        differences['verdict'] = 'ROLLBACK'
    elif differences['requires_review']:
        differences['verdict'] = 'REVIEW_REQUIRED'
    
    return differences


def print_report(differences: Dict[str, Any]) -> None:
    """Вывести отчёт о сравнении."""
    print("\n" + "=" * 60)
    print("COMPARISON REPORT")
    print("=" * 60)
    
    print(f"\nTotal documents: {differences['total_docs']}")
    print(f"Documents compared: {differences['docs_compared']}")
    print(f"Documents with significant differences: {differences['docs_with_differences']}")
    
    if differences['missing_docs']:
        print(f"\n⚠️  Missing documents: {len(differences['missing_docs'])}")
        for doc in differences['missing_docs'][:5]:
            print(f"   - {doc}")
    
    if differences['chunk_count_diffs']:
        print(f"\n📊 Chunk count differences:")
        for diff in sorted(differences['chunk_count_diffs'], 
                          key=lambda x: x['diff_percent'], reverse=True)[:10]:
            status = "⚠️" if diff['diff_percent'] > CHUNK_COUNT_DIFF_THRESHOLD else "✓"
            print(f"   {status} {diff['doc']}: {diff['old_count']} → {diff['new_count']} "
                  f"({diff['diff_percent']:+.1f}%)")
    
    if differences['content_loss_docs']:
        print(f"\n🚨 Content loss detected:")
        for doc in differences['content_loss_docs']:
            print(f"   - {doc['doc']}: {doc['loss_percent']:.1f}% loss")
    
    print("\n" + "-" * 60)
    verdict = differences['verdict']
    if verdict == 'PASS':
        print("✅ VERDICT: PASS - No significant differences")
    elif verdict == 'REVIEW_REQUIRED':
        print("⚠️  VERDICT: REVIEW REQUIRED - Some differences exceed thresholds")
    else:
        print("🚨 VERDICT: ROLLBACK - Critical differences detected")
    print("-" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Compare chunking results')
    parser.add_argument('--baseline', required=True, help='Path to baseline results JSON')
    parser.add_argument('--new', required=True, help='Path to new results JSON')
    parser.add_argument('--output', help='Path to save comparison report JSON')
    
    args = parser.parse_args()
    
    baseline = load_json(Path(args.baseline))
    new_results = load_json(Path(args.new))
    
    differences = compare_results(baseline, new_results)
    print_report(differences)
    
    if args.output:
        save_json(differences, Path(args.output))
        print(f"Report saved to {args.output}")
    
    # Exit code based on verdict
    if differences['verdict'] == 'ROLLBACK':
        sys.exit(2)
    elif differences['verdict'] == 'REVIEW_REQUIRED':
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
