#!/usr/bin/env python3
"""Test overlap with data structure similar to user's real SDE grades document."""

from markdown_chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig

# Create config with 200-char overlap
config = ChunkConfig(
    max_chunk_size=1000,
    overlap_size=200,
    enable_overlap=True,
    block_based_overlap=False
)

# Realistic test data matching user's structure
markdown_text = """# Критерии грейдов SDE

## SDE 16 (Senior I, Ведущий разработчик)

### Scope

Ведущий разработчик оказывает влияние на несколько команд и продуктов.
Отвечает за архитектурные решения и технологическое развитие направления.
Влияет на стратегию развития продуктов, платформ и инструментов в своём домене.
Понимает контекст бизнеса и учитывает его при принятии инженерных решений.

### Impact (Delivery)

Проектирует, разрабатывает и поставляет критически важные решения.
Влияет на несколько проектов или команд, участвует в масштабных инициативах.
Реализует архитектурные улучшения, устраняет технические ограничения.
Инициирует Proof-of-Concept, оценивает риски и доказывает реализуемость подходов.
Вносит вклад в стратегические цели и эффективность всего направления.

## SDE 16 (Senior I, Ведущий разработчик)

### Complexity

Решает задачи высокой сложности и неопределённости, где нет готовых решений.
Работает с системами, влияющими на масштаб и производительность бизнеса.
Учитывает баланс между архитектурной чистотой, скоростью поставки и рисками.
Разрабатывает решения, применимые в разных командах и сервисах.
Способен упрощать существующие системы, улучшая надёжность и стабильность.

## SDE 16 (Senior I, Ведущий разработчик)

### Leadership

Является техническим лидером для нескольких команд.
Аргументирует технические решения, выстраивает диалог со смежными командами.
Вдохновляет и направляет инженеров, развивает культуру ответственности.
Наставляет мидлов и лидов, проводит ревью архитектурных решений.
Может выступать архитектором или руководителем временной проектной группы.
"""

# Create chunker and chunk the text
chunker = MarkdownChunker(config)
result = chunker.chunk(
    markdown_text,
    strategy="structural",
    include_metadata=True,
    return_format="objects"
)

# Display results focusing on overlap quality
print("\n" + "="*80)
print("OVERLAP QUALITY TEST - Real Data Structure")
print("="*80)

for i, chunk in enumerate(result):
    print(f"\n{'='*80}")
    print(f"CHUNK {i}")
    print(f"{'='*80}")
    
    # Show content preview (first 150 chars)
    content = chunk.content
    print(f"\nContent ({len(content)} chars):")
    lines = content.split('\n')[:3]
    print('\n'.join(lines))
    if len(content) > 200:
        print("...")
    
    # Show overlap fields with FULL content to verify quality
    metadata = chunk.metadata
    
    if 'previous_content' in metadata:
        prev = metadata['previous_content']
        print(f"\n✓ previous_content ({len(prev)} chars):")
        print(f"   First 150 chars: {prev[:150]}")
        print(f"   Last 50 chars: ...{prev[-50:]}")
        # Check if it's just headers
        has_paragraphs = any(line and not line.strip().startswith('#') 
                            for line in prev.split('\n'))
        print(f"   Contains paragraphs: {'YES' if has_paragraphs else 'NO (headers only!)'}")
    else:
        print("\n✗ previous_content: Not present")
    
    if 'next_content' in metadata:
        next_ctx = metadata['next_content']
        print(f"\n✓ next_content ({len(next_ctx)} chars):")
        print(f"   First 150 chars: {next_ctx[:150]}")
        # Check if it's just headers
        has_paragraphs = any(line and not line.strip().startswith('#') 
                            for line in next_ctx.split('\n'))
        print(f"   Contains paragraphs: {'YES' if has_paragraphs else 'NO (headers only!)'}")
    else:
        print("\n✗ next_content: Not present")

print("\n" + "="*80)
print("EXPECTED BEHAVIOR:")
print("- previous_content should include paragraph text from previous chunk")
print("- next_content should include paragraph text from next chunk")
print("- NOT just headers!")
print("="*80)
