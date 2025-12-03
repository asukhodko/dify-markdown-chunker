#!/usr/bin/env python3
"""Manual test to verify previous_content/next_content fields appear in metadata."""

from markdown_chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig
import json

# Create config with metadata-mode overlap
config = ChunkConfig(
    max_chunk_size=1000,
    overlap_size=200,
    enable_overlap=True,
    block_based_overlap=False  # Use new metadata-mode overlap
)

# Sample markdown text
markdown_text = """# Критерии грейдов

## Junior-, Младший разработчик

### Scope
Разработчик помогает разрабатывать отдельные компоненты продукта.  
Нет выделенной зоны ответственности, работает при полной поддержке наставника.  
Ответственен за конкретные задачи. Может делить зону ответственности в проекте с наставником.

### Impact (Delivery)
Основная задача Junior — учиться, понимать свой проект и процессы, набирать опыт.  
Выполняет несложные задачи (маленькие и нетребующие большой экспертизы или не горящие, которые смогут проревьюить менторы).  
Получает декомпозированную задачу от ментора/лида с проработанным путем решения задачи.  
Получает помощь ментора или команды в процессе решения задачи.

### Complexity
Решает простые технические задачи, с понятным описанием, требуемым результатом и планом действий.  
При необходимости обращается за помощью к ментору или команде.  
Большинство зависимостей дано, отсутствующие пропуски легко устранимы.  
Задачи стандартные, в команде есть опыт и готовые решения.

### Leadership
Работает под руководством ментора.  
В коммуникациях в основном принимает информацию, сообщает о статусе и блокерах.  
При возникновении трудностей не замыкается, обращается за помощью.  
Формирует привычку к прозрачной коммуникации и ответственности за выполнение взятых задач.
"""

# Chunk with metadata mode
chunker = MarkdownChunker(config)
result = chunker.chunk(
    markdown_text,
    strategy="structural",
    include_metadata=True,  # Enable metadata-mode overlap
    return_format="dict"
)

print("=" * 80)
print("CHUNKING RESULTS WITH METADATA-MODE OVERLAP")
print("=" * 80)
print(f"Total chunks: {len(result['chunks'])}")
print(f"Strategy used: {result.get('strategy_used', 'N/A')}")
print()

# Check each chunk for overlap fields
for i, chunk in enumerate(result['chunks']):
    print(f"\n{'=' * 80}")
    print(f"CHUNK {i}")
    print(f"{'=' * 80}")
    
    metadata = chunk.get('metadata', {})
    
    # Check for new overlap fields
    has_previous = 'previous_content' in metadata
    has_next = 'next_content' in metadata
    has_prev_idx = 'previous_chunk_index' in metadata
    has_next_idx = 'next_chunk_index' in metadata
    
    # Check for old block-based fields (should NOT be present)
    has_block_overlap = 'overlap_block_count' in metadata
    has_overlap_size = 'overlap_size' in metadata
    
    print(f"\nNew overlap fields:")
    print(f"  ✓ previous_content: {has_previous}")
    if has_previous:
        prev_len = len(metadata['previous_content'])
        print(f"    Length: {prev_len} chars")
        print(f"    Preview: {metadata['previous_content'][:100]}...")
    
    print(f"  ✓ next_content: {has_next}")
    if has_next:
        next_len = len(metadata['next_content'])
        print(f"    Length: {next_len} chars")
        print(f"    Preview: {metadata['next_content'][:100]}...")
    
    print(f"  ✓ previous_chunk_index: {has_prev_idx}")
    if has_prev_idx:
        print(f"    Value: {metadata['previous_chunk_index']}")
    
    print(f"  ✓ next_chunk_index: {has_next_idx}")
    if has_next_idx:
        print(f"    Value: {metadata['next_chunk_index']}")
    
    print(f"\nOld block-based fields (should be absent):")
    print(f"  ✗ overlap_block_count: {has_block_overlap}")
    print(f"  ✗ overlap_size: {has_overlap_size}")
    
    print(f"\nContent preview:")
    content = chunk.get('content', '')
    print(f"  Length: {len(content)} chars")
    print(f"  First 200 chars: {content[:200]}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
