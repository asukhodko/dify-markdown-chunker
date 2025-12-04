# Configuration Analysis

## Обзор

Анализ системы конфигурации ChunkConfig с выявлением избыточных параметров и параметров для багфиксов.

**Общая статистика:**
- Всего параметров: **32**
- Параметров для багфиксов: **6** (MC-001 через MC-006)
- Параметров Phase 2: **3**
- Фабричных методов: **8+**

---

## Параметры ChunkConfig

### Группа 1: Размеры чанков (5 параметров)

| Параметр | Тип | Default | Назначение |
|----------|-----|---------|------------|
| `max_chunk_size` | int | 4096 | Максимальный размер чанка |
| `min_chunk_size` | int | 512 | Минимальный размер чанка |
| `target_chunk_size` | int | 2048 | Целевой размер чанка |
| `min_effective_chunk_size` | int | 0→40% | Минимальный эффективный размер (MC-004) |
| `min_content_per_chunk` | int | 50 | Минимум контента без заголовков (Phase 2) |

### Группа 2: Overlap (4 параметра)

| Параметр | Тип | Default | Назначение |
|----------|-----|---------|------------|
| `overlap_size` | int | 200 | Размер перекрытия в символах |
| `overlap_percentage` | float | 0.1 | Процент перекрытия |
| `enable_overlap` | bool | True | Включить перекрытие |
| `block_based_overlap` | bool | True | Block-based overlap (MC-003) |

### Группа 3: Пороги выбора стратегий (8 параметров)

| Параметр | Тип | Default | Документация | Реальное |
|----------|-----|---------|--------------|----------|
| `code_ratio_threshold` | float | 0.7 | ≥70% кода | **0.3** |
| `min_code_blocks` | int | 3 | ≥3 блоков | **1** |
| `min_complexity` | float | 0.3 | Для mixed | 0.3 |
| `list_count_threshold` | int | 5 | ≥5 списков | 5 |
| `list_ratio_threshold` | float | 0.6 | ≥60% списков | 0.6 |
| `table_count_threshold` | int | 3 | ≥3 таблиц | 3 |
| `table_ratio_threshold` | float | 0.4 | ≥40% таблиц | 0.4 |
| `header_count_threshold` | int | 3 | ≥3 заголовков | 3 |

### ⚠️ Проблема: Расхождение документации и кода

```python
# В docstring:
code_ratio_threshold: Threshold for code strategy selection (default: 0.7).
min_code_blocks: Minimum code blocks for code strategy (default: 3).

# В коде:
code_ratio_threshold: float = 0.3  # Lowered from 0.7 to handle real-world docs
min_code_blocks: int = 1  # Lowered from 3 to handle docs with few code blocks
```

### Группа 4: Поведение (4 параметра)

| Параметр | Тип | Default | Назначение |
|----------|-----|---------|------------|
| `allow_oversize` | bool | True | Разрешить oversize чанки |
| `preserve_code_blocks` | bool | True | Сохранять code blocks целиком |
| `preserve_tables` | bool | True | Сохранять таблицы целиком |
| `preserve_list_hierarchy` | bool | True | Сохранять иерархию списков |

### Группа 5: Fallback (3 параметра)

| Параметр | Тип | Default | Назначение |
|----------|-----|---------|------------|
| `enable_fallback` | bool | True | Включить fallback |
| `fallback_strategy` | str | "sentences" | Стратегия fallback |
| `max_fallback_level` | int | 4 | Максимальная глубина fallback |

### Группа 6: Preamble (3 параметра)

| Параметр | Тип | Default | Назначение |
|----------|-----|---------|------------|
| `extract_preamble` | bool | True | Извлекать преамбулу |
| `separate_preamble_chunk` | bool | False | Отдельный чанк для преамбулы |
| `preamble_min_size` | int | 10 | Минимальный размер преамбулы |

### Группа 7: Phase 2 (2 параметра)

| Параметр | Тип | Default | Назначение |
|----------|-----|---------|------------|
| `section_boundary_level` | int | 2 | Уровень заголовка для границ (H2) |
| `preserve_markdown_structure` | bool | True | Сохранять структуру markdown |

### Группа 8: Багфиксы MC-001 через MC-006 (5 параметров)

| Параметр | Тип | Default | Баг |
|----------|-----|---------|-----|
| `block_based_splitting` | bool | True | MC-001, MC-002, MC-005 |
| `allow_oversize_for_integrity` | bool | True | MC-001 (20% oversize) |
| `min_effective_chunk_size` | int | 0→40% | MC-004 |
| `block_based_overlap` | bool | True | MC-003 |
| `detect_url_pools` | bool | True | MC-005 |

### Группа 9: Прочее (3 параметра)

| Параметр | Тип | Default | Назначение |
|----------|-----|---------|------------|
| `enable_content_validation` | bool | True | Валидация полноты (Phase 1 Fix 3) |
| `enable_streaming` | bool | False | Streaming для больших документов |
| `streaming_threshold` | int | 10MB | Порог для streaming |

---

## Использование параметров

### Редко используемые параметры

| Параметр | Использований в коде | Статус |
|----------|---------------------|--------|
| `enable_streaming` | 0 | ⚠️ Не реализовано |
| `streaming_threshold` | 0 | ⚠️ Не реализовано |
| `max_fallback_level` | 1 | Только в FallbackManager |
| `fallback_strategy` | 0 | ⚠️ Не используется (hardcoded) |
| `preserve_list_hierarchy` | 1 | Только в ListStrategy |

### ⚠️ Проблема: Неиспользуемые параметры

```python
# fallback_strategy не используется - fallback hardcoded:
self._structural_strategy = StructuralStrategy()
self._sentences_strategy = SentencesStrategy()

# streaming не реализован:
enable_streaming: bool = False
streaming_threshold: int = 10 * 1024 * 1024  # 10MB
```

---

## Профили конфигурации

### Фабричные методы

| Метод | max_chunk | target | overlap | Особенности |
|-------|-----------|--------|---------|-------------|
| `default()` | 4096 | 2048 | 200 | Базовый |
| `for_code_heavy()` | 6144 | 3072 | 300 | code_ratio=0.5, min_blocks=2 |
| `for_structured_docs()` | 3072 | 1536 | 150 | header_threshold=2 |
| `for_large_documents()` | 8192 | 4096 | 400 | streaming=True |
| `for_dify_rag()` | ? | ? | ? | Для Dify RAG |
| `for_api_docs()` | ? | ? | ? | Для API документации |
| `for_code_docs()` | ? | ? | ? | Для документации кода |
| `for_search_indexing()` | ? | ? | ? | Для поискового индекса |
| `for_chat_context()` | ? | ? | ? | Для чат-контекста |

### ⚠️ Проблема: Много профилей

8+ фабричных методов с небольшими различиями. Сложно понять какой выбрать.

---

## Параметры для багфиксов

### MC-001: Section Fragmentation

```python
block_based_splitting: bool = True  # Use block-based packer for splitting
```

**Где используется:**
- `orchestrator.py`: `_apply_block_based_postprocessing()`
- `block_packer.py`: `BlockPacker`

### MC-002: Structural Breaks

```python
allow_oversize_for_integrity: bool = True  # Allow 20% oversize
```

**Где используется:**
- `block_packer.py`: При упаковке блоков

### MC-003: Overlap Issues

```python
block_based_overlap: bool = True  # Use block-based overlap calculation
```

**Где используется:**
- `orchestrator.py`: Условное переключение overlap
- `block_overlap_manager.py`: `BlockOverlapManager`

### MC-004: Size Variance

```python
min_effective_chunk_size: int = 0  # Minimum target size (0 = 40% of max)
```

**Где используется:**
- `chunk_size_normalizer.py`: `ChunkSizeNormalizer`
- `__post_init__`: Auto-adjust to 40% of max

### MC-005: Preamble/Link Block Fragmentation

```python
detect_url_pools: bool = True  # Detect and preserve URL pool blocks
```

**Где используется:**
- `block_packer.py`: `_detect_url_pool_block()`

### MC-006: Header Path Issues

Нет отдельного параметра — всегда применяется:
- `header_path_validator.py`: `HeaderPathValidator`

---

## Выводы

### Ключевые проблемы конфигурации

1. **Слишком много параметров**: 32 параметра — сложно понять и настроить
2. **Расхождение документации**: code_ratio 0.7 vs 0.3, min_blocks 3 vs 1
3. **Неиспользуемые параметры**: streaming, fallback_strategy
4. **Параметры для багфиксов**: 6 параметров добавлены для MC-* fixes
5. **Много профилей**: 8+ фабричных методов с небольшими различиями

### Рекомендации (предварительные)

1. **Удалить неиспользуемые**: streaming, fallback_strategy
2. **Объединить overlap**: enable_overlap + block_based_overlap → один механизм
3. **Упростить пороги**: Меньше параметров для выбора стратегий
4. **Удалить MC-* параметры**: После стабилизации сделать поведение по умолчанию
5. **Сократить профили**: 2-3 профиля вместо 8+
6. **Исправить документацию**: Синхронизировать docstrings с реальными defaults
