#!/usr/bin/env python
"""Test overlap extraction after v3 fix (empty check moved after content detection)."""

import logging
from markdown_chunker.chunker.components.overlap_manager import OverlapManager
from markdown_chunker.chunker.types import Chunk, ChunkConfig

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

# Test case: chunks with structure like user's data
# Each chunk has headers followed by paragraph

chunk1_content = """## SDE 14 (Middle I, Разработчик)

### Complexity

Решает задачи средней сложности.
Понимает систему и архитектуру своего продукта.
Способен предложить несколько вариантов решения и обосновать выбор.
Может разобраться в соседних сервисах и использовать их интерфейсы.
Работает с частично определёнными требованиями, умеет уточнять их у аналитиков или заказчиков.
Задачи могут требовать координации с другими командами.
Соблюдает нефункциональные требования: надёжность, производительность, безопасность."""

chunk2_content = """## SDE 14 (Middle I, Разработчик)

### Leadership

Коммуницирует эффективно с командой и смежными командами.
Дает конструктивный фидбек коллегам, умеет слушать и учитывать обратную связь.
Отвечает за выполнение своих задач и информирует о рисках и задержках заранее.
Может участвовать в код-ревью, помогать младшим разработчикам советом.
Понимает, как донести сложные технические идеи простым языком."""

chunk3_content = """## SDE 14 (Middle I, Разработчик)

### Improvement

Следует процессам команды и помогает улучшать их.
Понимает, зачем используются инструменты и практики.
Предлагает точечные улучшения, которые повышают эффективность и качество.
Самостоятельно поддерживает свой план развития, согласуя его с лидом.
Участвует в обучающих мероприятиях, делится опытом внутри команды."""

# Create chunks
chunks = [
    Chunk(content=chunk1_content, start_line=1, end_line=10, metadata={}),
    Chunk(content=chunk2_content, start_line=11, end_line=20, metadata={}),
    Chunk(content=chunk3_content, start_line=21, end_line=30, metadata={}),
]

# Test overlap extraction
config = ChunkConfig(
    max_chunk_size=4096,
    enable_overlap=True,
    overlap_size=200,
    overlap_percentage=0.0
)
manager = OverlapManager(config=config)

# Process chunks with metadata mode
result_chunks = manager.apply_overlap(chunks, include_metadata=True)

print("\n" + "="*80)
print("OVERLAP EXTRACTION TEST - V3 FIX")
print("="*80 + "\n")

for i, chunk in enumerate(result_chunks):
    prev_content = chunk.get_metadata("previous_content", "")
    next_content = chunk.get_metadata("next_content", "")
    
    print(f"Chunk {i}:")
    print(f"  Core content length: {len(chunk.content)} chars")
    
    if prev_content:
        print(f"\n  ✓ previous_content ({len(prev_content)} chars):")
        print(f"    First 150 chars: {prev_content[:150]}")
        # Check for paragraph keywords (verbs, content words, not just header markers)
        has_para = any(word in prev_content.lower() for word in ["решает", "коммуницирует", "следует", "понимает", "работает", "дает", "отвечает", "может", "участвует", "предлагает"])
        print(f"    Contains paragraphs: {'YES' if has_para else 'NO (headers only!)'}")
    else:
        print(f"\n  ✗ previous_content: MISSING")
    
    if next_content:
        print(f"\n  ✓ next_content ({len(next_content)} chars):")
        print(f"    First 150 chars: {next_content[:150]}")
        has_para = any(word in next_content.lower() for word in ["решает", "коммуницирует", "следует", "понимает", "работает", "дает", "отвечает", "может", "участвует", "предлагает"])
        print(f"    Contains paragraphs: {'YES' if has_para else 'NO (headers only!)'}")
    else:
        print(f"\n  ✗ next_content: MISSING")
    
    print("\n" + "-"*80 + "\n")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

# Check if overlap fields are present
chunks_with_prev = sum(1 for c in result_chunks if c.get_metadata("previous_content", ""))
chunks_with_next = sum(1 for c in result_chunks if c.get_metadata("next_content", ""))

print(f"\nChunks with previous_content: {chunks_with_prev}/{len(result_chunks)}")
print(f"Chunks with next_content: {chunks_with_next}/{len(result_chunks)}")

# Check content quality
prev_contents = [c.get_metadata("previous_content", "") for c in result_chunks if c.get_metadata("previous_content", "")]
next_contents = [c.get_metadata("next_content", "") for c in result_chunks if c.get_metadata("next_content", "")]

has_para_in_prev = sum(1 for p in prev_contents if any(word in p.lower() for word in ["решает", "коммуницирует", "следует", "понимает", "работает", "дает", "отвечает", "может", "участвует", "предлагает"]))
has_para_in_next = sum(1 for n in next_contents if any(word in n.lower() for word in ["решает", "коммуницирует", "следует", "понимает", "работает", "дает", "отвечает", "может", "участвует", "предлагает"]))

print(f"\nPrevious contexts with paragraph content: {has_para_in_prev}/{len(prev_contents)}")
print(f"Next contexts with paragraph content: {has_para_in_next}/{len(next_contents)}")

if chunks_with_prev > 0 and chunks_with_next > 0:
    print("\n✅ PASS: Overlap fields are present")
    if has_para_in_prev == len(prev_contents) and has_para_in_next == len(next_contents):
        print("✅ PASS: All overlap content contains paragraphs (not just headers)")
    else:
        print("⚠️  WARNING: Some overlap content still contains only headers")
else:
    print("\n❌ FAIL: Overlap fields are missing")

print("")
