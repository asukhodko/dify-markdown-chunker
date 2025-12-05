# Migration Guide: v1.x → v2.0

## Overview

Версия 2.0.0 — это полный редизайн архитектуры с фокусом на упрощение:
- **Модуль**: `markdown_chunker` → `markdown_chunker_v2`
- **Стратегии**: 6 → 3 (code_aware, structural, fallback)
- **Конфигурация**: 32 → 8 параметров
- **Тесты**: 1366+ → 445 (фокус на property-based тестах)

## Quick Start

```python
# v1.x
from markdown_chunker import MarkdownChunker
chunker = MarkdownChunker()
chunks = chunker.chunk(text)

# v2.0 - новый импорт
from markdown_chunker_v2 import MarkdownChunker
chunker = MarkdownChunker()
chunks = chunker.chunk(text)
```

Для совместимости можно использовать alias:
```python
# В вашем коде
from markdown_chunker_v2 import MarkdownChunker as MarkdownChunker
```

## Breaking Changes

### 1. ChunkConfig Parameters

**Removed parameters (24 → 8):**

| Removed Parameter | Replacement |
|-------------------|-------------|
| `enable_overlap` | Используйте `overlap_size > 0` |
| `block_based_splitting` | Всегда включено |
| `preserve_code_blocks` | Всегда включено |
| `preserve_tables` | Всегда включено |
| `enable_deduplication` | Удалено |
| `enable_regression_validation` | Удалено |
| `enable_header_path_validation` | Удалено |
| `use_enhanced_parser` | Всегда включено |
| `use_legacy_overlap` | Удалено |
| `enable_block_overlap` | Используйте `overlap_size > 0` |
| `enable_sentence_splitting` | Удалено |
| `enable_paragraph_merging` | Удалено |
| `enable_list_preservation` | Всегда включено |
| `enable_metadata_enrichment` | Всегда включено |
| `enable_size_normalization` | Удалено |
| `enable_fallback_strategy` | Всегда включено |

**Renamed parameters:**

| v1.x | v2.0 |
|------|------|
| `max_size` | `max_chunk_size` |
| `min_size` | `min_chunk_size` |

**New parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `preserve_atomic_blocks` | `True` | Сохранять целостность code blocks и tables |
| `strategy_override` | `None` | Принудительный выбор стратегии |

**Migration example:**

```python
# v1.x
config = ChunkConfig(
    max_size=1000,
    enable_overlap=True,
    overlap_size=100,
    block_based_splitting=True,
    preserve_code_blocks=True,
    enable_deduplication=False
)

# v2.0
config = ChunkConfig(
    max_chunk_size=1000,
    overlap_size=100,
    preserve_atomic_blocks=True
)
```

### 2. Removed Methods

**Removed:**

| Method | Replacement |
|--------|-------------|
| `chunk_with_analysis()` | Используйте `chunk()` |
| `chunk_simple()` | Используйте `chunk_text()` |
| `get_strategy_info()` | Используйте `chunk.metadata['strategy']` |

**Migration example:**

```python
# v1.x
result = chunker.chunk_with_analysis(text)
chunks = result.chunks
strategy = result.strategy_used

# v2.0
chunks = chunker.chunk(text)
strategy = chunks[0].metadata.get('strategy') if chunks else None
```

### 3. Strategy Selection Changes

**v1.x behavior:**
- Документы с кодом И заголовками → `StructuralStrategy`
- Только код → `CodeStrategy`
- Только таблицы → `TableStrategy`
- Смешанный контент → `MixedStrategy`

**v2.0 behavior:**
- Любой code block ИЛИ таблица → `CodeAwareStrategy`
- Только заголовки → `StructuralStrategy`
- Остальное → `FallbackStrategy`

**Impact:**
- Документы с кодом теперь обрабатываются `CodeAwareStrategy`, что обеспечивает лучшую целостность code blocks
- Количество чанков может измениться (обычно уменьшается)

**Migration:**

```python
# Для принудительного выбора стратегии (если нужно старое поведение):
config = ChunkConfig(strategy_override="structural")
chunks = chunker.chunk(text, config)
```

### 4. Removed Classes

**Consolidated strategies (6 → 3):**

| v1.x | v2.0 |
|------|------|
| `CodeStrategy` | `CodeAwareStrategy` |
| `TableStrategy` | `CodeAwareStrategy` |
| `MixedStrategy` | `CodeAwareStrategy` |
| `ListStrategy` | `CodeAwareStrategy` |
| `StructuralStrategy` | `StructuralStrategy` |
| `SentencesStrategy` | `FallbackStrategy` |

**Removed modules:**
- `markdown_chunker/api/` — REST API adapters removed
- `markdown_chunker/chunker/strategies/` — consolidated into `markdown_chunker_v2/strategies/`
- `markdown_chunker/parser/` — consolidated into `markdown_chunker_v2/parser.py`

### 5. Metadata Changes

**New metadata fields:**

| Field | Description |
|-------|-------------|
| `allow_oversize` | `True` если чанк превышает `max_chunk_size` намеренно |
| `oversize_reason` | Причина: `code_block_integrity`, `table_integrity`, `section_integrity` |
| `fence_balance_error` | `True` если не удалось сбалансировать code fences |

**Removed metadata fields:**

| Field | Notes |
|-------|-------|
| `dedup_hash` | Дедупликация удалена |
| `regression_score` | Regression validation удалена |

## FAQ

### Q: Мой код использует `chunk_with_analysis()`, что делать?

A: Замените на `chunk()`. Метаданные теперь доступны в каждом чанке:

```python
# v1.x
result = chunker.chunk_with_analysis(text)
print(f"Strategy: {result.strategy_used}")

# v2.0
chunks = chunker.chunk(text)
print(f"Strategy: {chunks[0].metadata.get('strategy')}")
```

### Q: Как получить старое поведение выбора стратегии?

A: Используйте `strategy_override`:

```python
config = ChunkConfig(strategy_override="structural")
```

### Q: Почему удалены параметры для багфиксов?

A: Все багфиксы теперь включены по умолчанию. Параметры были нужны только для backward compatibility во время тестирования.

### Q: Изменится ли результат чанкинга моих документов?

A: Возможно. Основные изменения:
- Code blocks и tables теперь всегда сохраняют целостность
- Выбор стратегии изменился (см. раздел 3)
- Overlap теперь применяется более консистентно

Рекомендуем протестировать на вашем корпусе документов перед обновлением.

### Q: Как проверить совместимость?

A: Используйте скрипт сравнения:

```bash
# Сохранить baseline с v1.x
python scripts/save_baseline.py --output baseline.json

# После обновления на v2.0
python scripts/compare_results.py --baseline baseline.json
```

## Deprecation Timeline

| Version | Changes |
|---------|---------|
| v1.9.0 | Deprecation warnings для удаляемых методов |
| v2.0.0 | Breaking changes (этот релиз) |
| v2.1.0 | Удаление deprecated shims |

## Support

Если у вас возникли проблемы с миграцией:
1. Проверьте этот документ
2. Посмотрите [CHANGELOG.md](./CHANGELOG.md)
3. Создайте issue в репозитории
