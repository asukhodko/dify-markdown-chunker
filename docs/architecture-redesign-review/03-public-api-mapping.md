# Маппинг публичного API

## Обзор

Анализ публичного API текущей реализации и его отображение на новый дизайн.

---

## Главный пакет (markdown_chunker)

### Экспортируемые классы

| Класс | Текущий | Новый дизайн | Статус |
|-------|---------|--------------|--------|
| `MarkdownChunker` | chunker/core.py | chunker.py | ✅ Сохранён |
| `ChunkConfig` | chunker/types.py | config.py | ✅ Сохранён (упрощён) |
| `Chunk` | chunker/types.py | types.py | ✅ Сохранён |
| `ChunkingResult` | chunker/types.py | types.py | ✅ Сохранён |
| `ParserInterface` | parser/core.py | parser.py | ✅ Сохранён (упрощён) |
| `ContentAnalysis` | parser/types.py | types.py | ✅ Сохранён |
| `PreambleExtractor` | parser/preamble.py | — | ⚠️ Удалён (интегрирован) |
| `PreambleInfo` | parser/preamble.py | — | ⚠️ Удалён |
| `PreambleType` | parser/preamble.py | — | ⚠️ Удалён |
| `MarkdownChunkerProvider` | provider/ | — | ✅ Без изменений |

### Экспортируемые функции

| Функция | Текущий | Новый дизайн | Статус |
|---------|---------|--------------|--------|
| `chunk_text()` | __init__.py | __init__.py | ✅ Сохранён |
| `chunk_file()` | __init__.py | __init__.py | ✅ Сохранён |
| `extract_preamble()` | parser/preamble.py | — | ⚠️ Удалён |

---

## MarkdownChunker API

### Публичные методы

| Метод | Текущий | Новый дизайн | Статус |
|-------|---------|--------------|--------|
| `chunk(md_text, include_analysis)` | core.py:155 | chunker.py | ✅ Сохранён |
| `chunk_with_analysis(md_text, strategy)` | core.py:423 | — | ⚠️ Удалён (объединён с chunk) |
| `chunk_simple(md_text, max_size)` | core.py:733 | — | ⚠️ Удалён |
| `get_available_strategies()` | core.py:617 | chunker.py | ✅ Сохранён |
| `get_performance_stats()` | core.py:675 | — | ⚠️ Удалён |

### Рекомендации

1. **chunk_with_analysis** — объединить с `chunk()`, добавив параметр `include_analysis=True`
2. **chunk_simple** — удалить, использовать `chunk()` с конфигом
3. **get_performance_stats** — удалить или сделать опциональным

---

## ChunkConfig API

### Текущие параметры (32)

```python
# Размеры
max_chunk_size: int = 4096
target_chunk_size: int = 3000  # УДАЛЁН
min_chunk_size: int = 100

# Overlap
enable_overlap: bool = True  # УДАЛЁН (overlap_size=0)
overlap_size: int = 200
overlap_percentage: float = 0.1  # УДАЛЁН

# Стратегии
strategy: str = "auto"  # ПЕРЕИМЕНОВАН в strategy_override
min_code_blocks: int = 1  # УДАЛЁН
min_complexity: float = 0.3  # УДАЛЁН
code_ratio_threshold: float = 0.7  # ПЕРЕИМЕНОВАН в code_threshold
list_count_threshold: int = 5  # УДАЛЁН
list_ratio_threshold: float = 0.3  # УДАЛЁН
table_count_threshold: int = 3  # УДАЛЁН
table_ratio_threshold: float = 0.2  # УДАЛЁН
header_count_threshold: int = 3  # ПЕРЕИМЕНОВАН в structure_threshold

# Поведение
allow_oversize: bool = True  # ПЕРЕИМЕНОВАН в preserve_atomic_blocks
preserve_code_blocks: bool = True  # ОБЪЕДИНЁН в preserve_atomic_blocks
preserve_tables: bool = True  # ОБЪЕДИНЁН в preserve_atomic_blocks
preserve_list_hierarchy: bool = True  # УДАЛЁН

# Fallback
enable_fallback: bool = True  # УДАЛЁН (всегда True)
fallback_strategy: str = "sentences"  # УДАЛЁН
max_fallback_level: int = 4  # УДАЛЁН

# Streaming (не реализовано)
enable_streaming: bool = False  # УДАЛЁН
streaming_threshold: int = 100000  # УДАЛЁН

# Preamble
extract_preamble: bool = True
separate_preamble_chunk: bool = True  # УДАЛЁН
preamble_min_size: int = 10  # УДАЛЁН

# Block-based
section_boundary_level: int = 2  # УДАЛЁН
min_content_per_chunk: int = 50  # УДАЛЁН
preserve_markdown_structure: bool = True  # УДАЛЁН (всегда True)
block_based_splitting: bool = True  # УДАЛЁН (всегда True)
allow_oversize_for_integrity: bool = True  # ОБЪЕДИНЁН в preserve_atomic_blocks
min_effective_chunk_size: int = 0  # УДАЛЁН
block_based_overlap: bool = True  # УДАЛЁН (всегда True)
detect_url_pools: bool = True  # УДАЛЁН

# Validation
enable_content_validation: bool = True  # УДАЛЁН (всегда True)
```

### Новые параметры (8)

```python
max_chunk_size: int = 4096
min_chunk_size: int = 512
overlap_size: int = 200
preserve_atomic_blocks: bool = True
extract_preamble: bool = True
code_threshold: float = 0.3
structure_threshold: int = 3
oversize_tolerance: float = 0.2
strategy_override: Optional[str] = None
```

---

## Chunk API

### Свойства

| Свойство | Текущий | Новый дизайн | Статус |
|----------|---------|--------------|--------|
| `content` | ✅ | ✅ | Сохранён |
| `start_line` | ✅ | ✅ | Сохранён |
| `end_line` | ✅ | ✅ | Сохранён |
| `metadata` | ✅ | ✅ | Сохранён |
| `size` | property | property | ✅ Сохранён |
| `line_count` | property | property | ✅ Сохранён |
| `content_type` | property | property | ✅ Сохранён |
| `strategy` | property | property | ✅ Сохранён |
| `language` | property | property | ✅ Сохранён |
| `is_oversize` | property | property | ✅ Сохранён |

### Методы

| Метод | Текущий | Новый дизайн | Статус |
|-------|---------|--------------|--------|
| `add_metadata(key, value)` | ✅ | ✅ | Сохранён |
| `to_dict()` | ✅ | ✅ | Сохранён |
| `from_dict(data)` | classmethod | classmethod | ✅ Сохранён |
| `get_section_path()` | ✅ | ✅ | Сохранён |
| `get_source_range()` | ✅ | ✅ | Сохранён |
| `get_section_id()` | ✅ | ✅ | Сохранён |

---

## Стратегии API

### Текущие стратегии (6)

| Стратегия | Новый дизайн | Статус |
|-----------|--------------|--------|
| `CodeStrategy` | CodeAwareStrategy | ✅ Объединён |
| `MixedStrategy` | CodeAwareStrategy | ✅ Объединён |
| `TableStrategy` | CodeAwareStrategy | ✅ Объединён |
| `ListStrategy` | — | ❌ Удалён |
| `StructuralStrategy` | StructuralStrategy | ✅ Упрощён |
| `SentencesStrategy` | FallbackStrategy | ✅ Переименован |

### Новые стратегии (3)

| Стратегия | Описание |
|-----------|----------|
| `CodeAwareStrategy` | Код, таблицы, смешанный контент |
| `StructuralStrategy` | Иерархия заголовков |
| `FallbackStrategy` | Универсальный fallback |

---

## Parser API

### Текущий API (большой)

```python
# Основные функции
extract_fenced_blocks()
parse_markdown()
parse_to_ast()
process_markdown()
analyze()

# Simple API
extract_code_blocks()
get_document_structure()
check_markdown_quality()
quick_analyze()
get_code()
get_structure()
check_quality()

# Классы
ParserInterface
Stage1Interface
FenceHandler
FencedBlockExtractor
ASTBuilder
EnhancedASTBuilder
# ... и много других
```

### Новый API (минимальный)

```python
# Один класс
class Parser:
    def parse(md_text: str) -> ContentAnalysis
```

### Backward Compatibility

Для обратной совместимости можно сохранить алиасы:

```python
# В __init__.py
def extract_fenced_blocks(md_text):
    """Deprecated: use Parser.parse()"""
    return Parser().parse(md_text).code_blocks
```

---

## Сводка изменений

### Сохранено без изменений
- `MarkdownChunker` (основной класс)
- `Chunk` (структура данных)
- `ChunkingResult` (результат)
- `chunk_text()`, `chunk_file()` (convenience функции)

### Упрощено
- `ChunkConfig` (32 → 8 параметров)
- `Parser` (много классов → 1 класс)
- Стратегии (6 → 3)

### Удалено
- `PreambleExtractor`, `PreambleInfo`, `PreambleType`
- `chunk_with_analysis()`, `chunk_simple()`
- `get_performance_stats()`
- `ListStrategy`
- Большинство parser функций

### Требует миграции
- Пользователи `chunk_with_analysis()` → `chunk(include_analysis=True)`
- Пользователи `ListStrategy` → `StructuralStrategy` или `FallbackStrategy`
- Пользователи preamble API → встроенная логика

---

## Риски обратной совместимости

1. **Низкий риск**: Удаление `chunk_simple()` — редко используется
2. **Средний риск**: Упрощение `ChunkConfig` — пользователи с кастомными конфигами
3. **Средний риск**: Удаление `ListStrategy` — пользователи с list-heavy документами
4. **Высокий риск**: Удаление preamble API — если есть пользователи

### Рекомендации

1. Добавить deprecation warnings перед удалением
2. Сохранить алиасы для критичных функций
3. Документировать миграционный путь


---

## Детальный маппинг удалённых функций

### chunk_with_analysis() → chunk()

**Причина:** Избыточность. `chunk()` уже поддерживает `include_analysis=True`.

**Миграция:**
```python
# Было
result = chunker.chunk_with_analysis(text, strategy="structural")

# Стало
result = chunker.chunk(text, include_analysis=True)
# strategy задаётся через config.strategy_override
```

### chunk_simple() → chunk()

**Причина:** Избыточность. Можно использовать `chunk()` с простым конфигом.

**Миграция:**
```python
# Было
chunks = chunker.chunk_simple(text, max_size=2000)

# Стало
config = ChunkConfig(max_chunk_size=2000)
chunker = MarkdownChunker(config)
result = chunker.chunk(text)
chunks = result.chunks
```

### get_performance_stats() → удалён

**Причина:** Не критичен для основной функциональности. Усложняет код.

**Миграция:** Если нужна статистика, использовать внешний профайлер или добавить опционально.

### ListStrategy → удалён

**Причина:** Была исключена из auto-mode (`selector.py:102`). Не используется.

**Миграция:**
```python
# Было
config = ChunkConfig(strategy="list")

# Стало
# Использовать structural или fallback
config = ChunkConfig(strategy_override="structural")
```

### PreambleExtractor → интегрирован

**Причина:** Логика встроена в Parser и стратегии.

**Миграция:**
```python
# Было
from markdown_chunker import PreambleExtractor, extract_preamble
preamble = extract_preamble(text)

# Стало
# Preamble извлекается автоматически при chunk()
result = chunker.chunk(text)
# Preamble в первом чанке если extract_preamble=True
```

---

## Удалённые параметры ChunkConfig

| Параметр | Причина удаления | Новое поведение |
|----------|------------------|-----------------|
| `target_chunk_size` | Избыточен | Используется max/min |
| `enable_overlap` | Избыточен | `overlap_size=0` отключает |
| `overlap_percentage` | Избыточен | Используется `overlap_size` |
| `min_code_blocks` | Упрощено | `code_threshold` |
| `min_complexity` | Не нужен | Удалён |
| `list_count_threshold` | ListStrategy удалена | Удалён |
| `list_ratio_threshold` | ListStrategy удалена | Удалён |
| `table_count_threshold` | Упрощено | CodeAware обрабатывает |
| `table_ratio_threshold` | Упрощено | CodeAware обрабатывает |
| `preserve_code_blocks` | Объединён | `preserve_atomic_blocks` |
| `preserve_tables` | Объединён | `preserve_atomic_blocks` |
| `preserve_list_hierarchy` | Не нужен | Удалён |
| `enable_fallback` | Всегда True | Удалён |
| `fallback_strategy` | Всегда sentences | Удалён |
| `max_fallback_level` | Не нужен | Удалён |
| `enable_streaming` | Не реализовано | Удалён |
| `streaming_threshold` | Не реализовано | Удалён |
| `separate_preamble_chunk` | Упрощено | Удалён |
| `preamble_min_size` | Не нужен | Удалён |
| `section_boundary_level` | Не нужен | Удалён |
| `min_content_per_chunk` | Не нужен | Удалён |
| `preserve_markdown_structure` | Всегда True | Удалён |
| `block_based_splitting` | Всегда True | Удалён |
| `allow_oversize_for_integrity` | Объединён | `preserve_atomic_blocks` |
| `min_effective_chunk_size` | Не нужен | Удалён |
| `block_based_overlap` | Всегда True | Удалён |
| `detect_url_pools` | Не критичен | Удалён |
| `enable_content_validation` | Всегда True | Удалён |
