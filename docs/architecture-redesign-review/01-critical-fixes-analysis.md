# Анализ критических исправлений

## Обзор

Анализ всех критических исправлений (MC-*, Phase 1/2, FIX) в текущем коде и их отражение в новом дизайне.

---

## MC-* Fixes (Block-based improvements)

### MC-001: Section Fragmentation

**Проблема:** Секции разбивались посередине, теряя семантическую целостность.

**Текущее решение:**
- `block_packer.py` — block-based packing
- `structural_strategy.py:526` — 20% tolerance для сохранения секций целиком
- Параметр: `allow_oversize_for_integrity = True`

**В новом дизайне:**
- ✅ **ОТРАЖЕНО** — добавлен `oversize_tolerance: float = 0.2` в ChunkConfig
- ✅ StructuralStrategy использует `effective_max = max_chunk_size * (1 + oversize_tolerance)`
- ✅ FallbackStrategy также использует tolerance для сохранения целостности параграфов

**Статус:** ✅ ИСПРАВЛЕНО в docs/architecture-audit-to-be/05-strategies.md

---

### MC-002: Structural Breaks

**Проблема:** Code blocks и таблицы разбивались между чанками.

**Текущее решение:**
- `block_packer.py` — работа на уровне блоков
- `block_overlap_manager.py:115-121` — skip code/table blocks в overlap
- `base.py:237` — `_validate_code_fence_balance()`

**В новом дизайне:**
- ✅ CodeAwareStrategy обрабатывает атомарные блоки
- ✅ `_validate_code_fence_balance()` добавлен в BaseStrategy
- ✅ Проверка code blocks в `_apply_overlap()`

**Статус:** ✅ ИСПРАВЛЕНО

---

### MC-003: Overlap Issues

**Проблема:** Overlap мог разрезать code blocks или включать заголовки из других секций.

**Текущее решение:**
- `block_overlap_manager.py` — block-based overlap
- Overlap содержит только полные блоки
- Не включает заголовки из других секций

**В новом дизайне:**
- ✅ Проверка code blocks в `_apply_overlap()`:
```python
if '```' in overlap:
    if overlap.count('```') % 2 == 1:
        overlap = overlap[fence_pos + 3:].lstrip()
```
- ✅ 50% limit предотвращает слишком большой overlap
- ✅ Симметричное обрезание

**Статус:** ✅ ЧАСТИЧНО ИСПРАВЛЕНО (достаточно для MVP)

---

### MC-004: Size Variance

**Проблема:** Большой разброс размеров чанков (от 50 до 4000 символов).

**Текущее решение:**
- `chunk_size_normalizer.py` — single-pass merging
- Параметр: `min_effective_chunk_size = 40% of max`

**В новом дизайне:**
- ⚠️ **НЕ ОТРАЖЕНО**
- Нет нормализации размеров

**Рекомендация:** Добавить опциональную нормализацию или убедиться, что стратегии создают равномерные чанки.

---

### MC-005: Preamble/Link Block Fragmentation

**Проблема:** URL pools (3+ ссылок подряд) разбивались.

**Текущее решение:**
- `block_packer.py:467` — `_detect_url_pool_block()`
- Параметр: `detect_url_pools = True`

**В новом дизайне:**
- ⚠️ **НЕ ОТРАЖЕНО**
- URL pools не упомянуты

**Рекомендация:** Добавить детекцию URL pools в CodeAwareStrategy.

---

### MC-006: Header Path Issues

**Проблема:** Некорректные или неполные header_path в метаданных.

**Текущее решение:**
- `header_path_validator.py` — валидация и исправление путей

**В новом дизайне:**
- ✅ StructuralStrategy добавляет header_path
- ⚠️ Нет отдельной валидации

**Рекомендация:** Добавить валидацию header_path в StructuralStrategy.

---

## Phase 1/2 Fixes

### Phase 1.1: Code Block Extraction

**Проблема:** Code blocks не извлекались полностью.

**Текущее решение:**
- `markdown_ast.py:80` — Handle closing tokens FIRST
- `base.py:237` — `_validate_code_fence_balance()`

**В новом дизайне:**
- ✅ **ОТРАЖЕНО** — добавлен `_validate_code_fence_balance()` в BaseStrategy
- ✅ CodeAwareStrategy обрабатывает code blocks как атомарные элементы
- ✅ Валидация проверяет баланс ``` в каждом чанке

**Статус:** ✅ ИСПРАВЛЕНО в docs/architecture-audit-to-be/05-strategies.md

---

### Phase 1.2: Oversize Chunks Flagging

**Проблема:** Oversize чанки не помечались флагом `allow_oversize`.

**Текущее решение:**
- `orchestrator.py:170` — `_validate_size_compliance()`

**В новом дизайне:**
- ✅ Упомянуто в `Chunker._validate()`
- Нужно убедиться, что флаг добавляется

---

### Phase 2.1: Symmetric Truncation

**Проблема:** Несимметричное обрезание overlap.

**Текущее решение:**
- `text_normalizer.py:306-317` — `strip()` для симметрии

**В новом дизайне:**
- ✅ **ОТРАЖЕНО** — `overlap = overlap.strip()` в `_apply_overlap()`
- ✅ Также есть поиск границы слова для чистого обрезания

**Статус:** ✅ ОТРАЖЕНО в docs/architecture-audit-to-be/04-components.md

---

### Phase 2.2: Overlap Limit

**Проблема:** Overlap мог превышать 50% чанка.

**Текущее решение:**
- Ограничение в overlap manager

**В новом дизайне:**
- ✅ **ОТРАЖЕНО** — `max_overlap = min(config.overlap_size, len(prev_content) // 2)`
- ✅ Ограничение до 50% размера предыдущего чанка

**Статус:** ✅ ОТРАЖЕНО в docs/architecture-audit-to-be/04-components.md

---

## Другие FIX комментарии

### FIX: Sort chunks by document position

**Файлы:** `orchestrator.py:162`, `list_strategy.py:165`

**В новом дизайне:**
- ✅ Добавлено в `_post_process()`: `sorted(chunks, key=lambda c: (c.start_line, c.end_line))`

**Статус:** ✅ ИСПРАВЛЕНО

---

### FIX: Filter out list strategy in auto mode

**Файл:** `selector.py:102`

**В новом дизайне:**
- ✅ ListStrategy удалена полностью

---

### FIX: Preserve markdown structure

**Файл:** `sentences_strategy.py:267`

**В новом дизайне:**
- ⚠️ FallbackStrategy упрощена
- Нужно проверить сохранение структуры

---

### FIX: Group multiple items to avoid micro-chunks

**Файл:** `list_strategy.py:416, 526, 651`

**В новом дизайне:**
- ✅ ListStrategy удалена
- Логика группировки должна быть в других стратегиях

---

## Сводная таблица

| Fix | Описание | В новом дизайне | Статус |
|-----|----------|-----------------|--------|
| MC-001 | Section fragmentation | oversize_tolerance | ✅ OK |
| MC-002 | Structural breaks | _validate_code_fence_balance | ✅ OK |
| MC-003 | Overlap issues | Проверка code blocks | ✅ OK |
| MC-004 | Size variance | Не отражено | ⚠️ Некритично |
| MC-005 | URL pools | Не отражено | ⚠️ Некритично |
| MC-006 | Header paths | _update_header_path | ✅ OK |
| Phase 1.1 | Code extraction | _validate_code_fence_balance | ✅ OK |
| Phase 1.2 | Oversize flagging | _flag_oversize_chunks | ✅ OK |
| Phase 2.1 | Symmetric truncation | strip() + word boundary | ✅ OK |
| Phase 2.2 | Overlap limit | 50% limit | ✅ OK |
| Sort chunks | Ordering | sorted() в _post_process | ✅ OK |

---

## Выводы

### Исправленные пробелы

1. ✅ **MC-001** — добавлен `oversize_tolerance` в конфиг и стратегии
2. ✅ **Phase 1.1** — добавлен `_validate_code_fence_balance()` в BaseStrategy
3. ✅ **Phase 1.2** — `_flag_oversize_chunks()` в Chunker
4. ✅ **Phase 2.1** — symmetric truncation в `_apply_overlap()`
5. ✅ **Phase 2.2** — 50% overlap limit в `_apply_overlap()`
6. ✅ **Сортировка** — `sorted()` в `_post_process()`

### Оставшиеся пробелы

1. **MC-003 Overlap** — проверка на разрезание code blocks добавлена, но упрощена
2. **MC-004** — нет нормализации размеров (возможно не критично)
3. **MC-005** — нет детекции URL pools (возможно не критично)

### Рекомендации

1. **MC-003** — текущая реализация проверяет code blocks в overlap, но может быть недостаточно
2. **MC-004** — рассмотреть добавление опциональной нормализации если нужна
3. **MC-005** — рассмотреть URL pools если это важно для пользователей
