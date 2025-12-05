# Архитектурный Аудит: Рекомендации

## Общая рекомендация

**Полный редизайн** проекта с нуля, а не попытка рефакторинга существующего кода.

### Обоснование:

1. Код накопил слишком много слоёв исправлений (Phase 1, Phase 2, MC-001..MC-006)
2. Двойные механизмы (overlap, пост-обработка) сложно разделить
3. Тесты привязаны к реализации, а не к поведению
4. Проще написать заново с учётом всех требований

## Рекомендации по структуре

### R1: Сократить количество файлов

**Было:** 55 файлов
**Цель:** 12 файлов

```
markdown_chunker/
├── __init__.py          # Публичный API
├── types.py             # Все типы данных
├── config.py            # ChunkConfig (8-10 параметров)
├── chunker.py           # MarkdownChunker (main class)
├── parser.py            # Парсинг markdown
├── strategies/
│   ├── __init__.py
│   ├── base.py          # BaseStrategy
│   ├── code_aware.py    # Code + Mixed (объединены)
│   ├── structural.py    # Structural (упрощённая)
│   └── fallback.py      # Sentences (fallback)
└── utils.py             # Общие утилиты
```

### R2: Объединить types.py

**Было:** 
- `chunker/types.py` — 1079 строк
- `parser/types.py` — 931 строка

**Цель:** Один `types.py` ~500 строк

```python
# types.py
@dataclass
class Chunk:
    content: str
    start_line: int
    end_line: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChunkingResult:
    chunks: List[Chunk]
    strategy_used: str
    processing_time: float
    # Минимум полей

@dataclass
class ContentAnalysis:
    total_chars: int
    total_lines: int
    code_ratio: float
    header_count: int
    # Только необходимое
```

### R3: Упростить конфигурацию

**Было:** 32 параметра
**Цель:** 8-10 параметров

```python
@dataclass
class ChunkConfig:
    # Размеры
    max_chunk_size: int = 4096
    min_chunk_size: int = 512
    overlap_size: int = 200  # 0 = disabled
    
    # Поведение
    preserve_atomic_blocks: bool = True  # code, tables
    extract_preamble: bool = True
    
    # Пороги (опционально)
    code_threshold: float = 0.3
    structure_threshold: int = 3
    
    @classmethod
    def default(cls) -> "ChunkConfig":
        return cls()
    
    @classmethod
    def for_code(cls) -> "ChunkConfig":
        return cls(max_chunk_size=6144, code_threshold=0.2)
    
    @classmethod
    def for_rag(cls) -> "ChunkConfig":
        return cls(max_chunk_size=2048, overlap_size=100)
```

### R4: Консолидировать стратегии

**Было:** 6 стратегий (одна не используется)
**Цель:** 3-4 стратегии

| Было | Станет | Причина |
|------|--------|---------|
| CodeStrategy | CodeAwareStrategy | Объединить с Mixed |
| MixedStrategy | (объединена) | Дублирует Code |
| ListStrategy | (удалена) | Не используется |
| TableStrategy | (в CodeAware) | Редко нужна отдельно |
| StructuralStrategy | StructuralStrategy | Упростить |
| SentencesStrategy | FallbackStrategy | Переименовать |

```python
# Новые стратегии:
class CodeAwareStrategy(BaseStrategy):
    """Для документов с кодом, таблицами, смешанным контентом."""
    priority = 1

class StructuralStrategy(BaseStrategy):
    """Для документов с иерархией заголовков."""
    priority = 2

class FallbackStrategy(BaseStrategy):
    """Универсальный fallback по предложениям."""
    priority = 3
    
    def can_handle(self, analysis, config):
        return True  # Всегда может обработать
```

## Рекомендации по потоку данных

### R5: Линейный pipeline

**Было:** Двойная пост-обработка, двойной Stage 1

**Цель:** Один линейный pipeline

```python
def chunk(self, md_text: str) -> ChunkingResult:
    # 1. Parse (один раз)
    analysis = self._parse(md_text)
    
    # 2. Select strategy
    strategy = self._select_strategy(analysis)
    
    # 3. Apply strategy
    chunks = strategy.apply(md_text, analysis, self.config)
    
    # 4. Post-process (один раз)
    chunks = self._post_process(chunks, analysis)
    
    # 5. Return
    return ChunkingResult(chunks=chunks, strategy_used=strategy.name)
```

### R6: Удалить legacy overlap

**Было:** `OverlapManager` + `BlockOverlapManager`

**Цель:** Один механизм overlap

```python
def _apply_overlap(self, chunks: List[Chunk]) -> List[Chunk]:
    if self.config.overlap_size == 0:
        return chunks
    
    for i in range(1, len(chunks)):
        overlap_content = self._get_overlap(chunks[i-1], chunks[i])
        chunks[i].metadata["previous_content"] = overlap_content
    
    return chunks
```

### R7: Централизовать валидацию

**Было:** Валидация в 5+ местах

**Цель:** Один валидатор

```python
class ChunkValidator:
    def validate(self, chunks: List[Chunk], config: ChunkConfig) -> ValidationResult:
        errors = []
        
        # PROP-2: Size bounds
        for chunk in chunks:
            if len(chunk.content) > config.max_chunk_size:
                if not chunk.metadata.get("allow_oversize"):
                    errors.append(f"Chunk exceeds max size")
        
        # PROP-4: No empty
        for chunk in chunks:
            if not chunk.content.strip():
                errors.append(f"Empty chunk")
        
        # PROP-3: Ordering
        for i in range(len(chunks) - 1):
            if chunks[i].start_line > chunks[i+1].start_line:
                errors.append(f"Chunks out of order")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
```

## Рекомендации по тестам

### R8: Property-based тесты вместо тестов реализации

**Было:** 1853 теста, 45K строк
**Цель:** ~50-100 тестов, ~2K строк

```python
# tests/test_properties.py — один файл для всех свойств

class TestCriticalProperties:
    @given(markdown_documents())
    def test_no_content_loss(self, doc):
        # PROP-1
        
    @given(markdown_documents(), chunk_configs())
    def test_size_bounds(self, doc, config):
        # PROP-2
        
    @given(markdown_documents())
    def test_monotonic_ordering(self, doc):
        # PROP-3
        
    @given(markdown_documents())
    def test_no_empty_chunks(self, doc):
        # PROP-4
        
    @given(markdown_documents())
    def test_valid_line_numbers(self, doc):
        # PROP-5

class TestImportantProperties:
    @given(markdown_with_code())
    def test_code_block_integrity(self, doc):
        # PROP-6
        
    @given(markdown_with_tables())
    def test_table_integrity(self, doc):
        # PROP-7
        
    @given(chunking_results())
    def test_serialization_roundtrip(self, result):
        # PROP-8
```

### R9: Минимум unit тестов

```python
# tests/test_edge_cases.py — только edge cases

class TestEdgeCases:
    def test_empty_document(self):
        assert chunker.chunk("") == []
    
    def test_whitespace_only(self):
        assert chunker.chunk("   \n\n   ") == []
    
    def test_single_char(self):
        chunks = chunker.chunk("x")
        assert len(chunks) == 1
    
    def test_huge_code_block(self):
        doc = "```\n" + "x" * 10000 + "\n```"
        chunks = chunker.chunk(doc)
        assert len(chunks) == 1
        assert chunks[0].metadata.get("allow_oversize")
```

### R10: Один integration тест

```python
# tests/test_integration.py

def test_full_pipeline():
    doc = load_fixture("complex_document.md")
    result = chunker.chunk(doc, include_analysis=True)
    
    assert result.success
    assert result.chunks
    assert result.processing_time < 10.0
```

## Рекомендации по API

### R11: Минимальный публичный API

**Было:** 50+ символов из parser
**Цель:** ~10 символов

```python
# markdown_chunker/__init__.py

__all__ = [
    # Main
    "MarkdownChunker",
    "ChunkConfig",
    "Chunk",
    "ChunkingResult",
    
    # Convenience
    "chunk_text",
    "chunk_file",
]
```

### R12: Удалить deprecated код

- Удалить Simple API
- Удалить backward compatibility aliases
- Удалить try/except imports

## Приоритеты рекомендаций

| # | Рекомендация | Приоритет | Сложность |
|---|--------------|-----------|-----------|
| R1 | Сократить файлы | HIGH | HIGH |
| R2 | Объединить types | HIGH | MEDIUM |
| R3 | Упростить конфигурацию | HIGH | LOW |
| R4 | Консолидировать стратегии | HIGH | HIGH |
| R5 | Линейный pipeline | HIGH | MEDIUM |
| R6 | Удалить legacy overlap | MEDIUM | LOW |
| R7 | Централизовать валидацию | MEDIUM | LOW |
| R8 | Property-based тесты | HIGH | MEDIUM |
| R9 | Минимум unit тестов | MEDIUM | LOW |
| R10 | Один integration тест | LOW | LOW |
| R11 | Минимальный API | MEDIUM | LOW |
| R12 | Удалить deprecated | LOW | LOW |
