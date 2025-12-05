#!/usr/bin/env python3
"""
Скрипт сохранения baseline результатов чанкинга.

Используется для сохранения результатов текущей реализации
перед редизайном для последующего сравнения.

Usage:
    python scripts/save_baseline.py --corpus tests/fixtures/corpus --output baseline.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from markdown_chunker import MarkdownChunker, ChunkConfig


def save_baseline(corpus_dir: Path, output_file: Path, config: ChunkConfig = None) -> Dict[str, Any]:
    """
    Сохранить baseline результаты для всех документов корпуса.
    
    Args:
        corpus_dir: Путь к директории с тестовыми документами
        output_file: Путь для сохранения результатов
        config: Конфигурация чанкинга (опционально)
    
    Returns:
        dict с результатами для каждого документа
    """
    chunker = MarkdownChunker(config or ChunkConfig())
    results = {}
    
    # Find all markdown files
    md_files = list(corpus_dir.rglob("*.md"))
    
    print(f"Found {len(md_files)} markdown files in {corpus_dir}")
    
    for doc_path in md_files:
        # Skip .gitkeep and README
        if doc_path.name.startswith('.') or doc_path.name == 'README.md':
            continue
        
        try:
            content = doc_path.read_text(encoding='utf-8')
            chunks = chunker.chunk(content)
            
            relative_path = str(doc_path.relative_to(corpus_dir))
            
            results[relative_path] = {
                'input_size': len(content),
                'input_lines': content.count('\n') + 1,
                'chunk_count': len(chunks),
                'chunks': [
                    {
                        'content': chunk.content,
                        'start_line': chunk.start_line,
                        'end_line': chunk.end_line,
                        'size': len(chunk.content),
                        'strategy': chunk.metadata.get('strategy', 'unknown'),
                    }
                    for chunk in chunks
                ],
                'total_output_size': sum(len(c.content) for c in chunks),
            }
            
            print(f"  ✓ {relative_path}: {len(chunks)} chunks")
            
        except Exception as e:
            print(f"  ✗ {relative_path}: {e}")
            results[str(doc_path.relative_to(corpus_dir))] = {
                'error': str(e)
            }
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nBaseline saved to {output_file}")
    print(f"Total documents: {len(results)}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Save baseline chunking results')
    parser.add_argument('--corpus', required=True, help='Path to test corpus directory')
    parser.add_argument('--output', required=True, help='Path to save baseline JSON')
    parser.add_argument('--max-chunk-size', type=int, default=4096, help='Max chunk size')
    
    args = parser.parse_args()
    
    corpus_dir = Path(args.corpus)
    output_file = Path(args.output)
    
    if not corpus_dir.exists():
        print(f"Error: Corpus directory not found: {corpus_dir}")
        sys.exit(1)
    
    config = ChunkConfig(max_chunk_size=args.max_chunk_size)
    
    save_baseline(corpus_dir, output_file, config)


if __name__ == '__main__':
    main()
