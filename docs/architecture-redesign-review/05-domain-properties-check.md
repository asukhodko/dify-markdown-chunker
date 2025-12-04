# Проверка доменных свойств в новом дизайне

## Сводка

| Свойство | Текущая реализация | Новая реализация | Статус |
|----------|-------------------|------------------|--------|
| PROP-1: No Content Loss | orchestrator._validate_content_completeness | Validator._validate_content_completeness | ✅ |
| PROP-2: Chunk Size Bounds | _validate_size_compliance | Validator.validate + _flag_oversize_chunks | ✅ |
| PROP-3: Monotonic Ordering | sorted() в orchestrator | sorted() в _post_process | ✅ |
| PROP-4: No Empty Chunks | Chunk.__post_init__ | Chunk.__post_init__ + Validator | ✅ |
| PROP-5: Valid Line Numbers | Chunk.__post_init__ | Chunk.__post_init__ + Validator | ✅ |
| PROP-6: Code Block Integrity | _validate_code_fence_balance | BaseStrategy._validate_code_fence_balance | ✅ |
| PROP-7: Table Integrity | preserve_tables, TableStrategy | CodeAwareStrategy (атомарные блоки) | ✅ |
| PROP-8: Serialization Round-Trip | to_dict/from_dict | to_dict/from_dict | ✅ |

---

## PROP-1: No Content Loss

**Определение:** Весь контент исходного документа должен присутствовать в чанках.

**Текущая реализация:**
- `orchestrator._validate_content_completeness()` — подсчёт символов

**Новая реализация:**
- `Validator._validate_content_completeness()` — подсчёт символов с учётом overlap
- Вызывается из `Validator.validate(chunks, config, original_text)`

**Файл:** `docs/architecture-audit-to-be/04-components.md`

---

## PROP-2: Chunk Size Bounds

**Определение:** Размер чанка <= max_chunk_size (или помечен allow_oversize).

**Текущая реализация:**
- `orchestrator._validate_size_compliance()` — пометка oversize чанков

**Новая реализация:**
- `Validator.validate()` — проверка размеров
- `Chunker._flag_oversize_chunks()` — пометка oversize

**Файл:** `docs/architecture-audit-to-be/04-components.md`

---

## PROP-3: Monotonic Ordering

**Определение:** Чанки отсортированы по start_line.

**Текущая реализация:**
- `orchestrator:162-168` — sorted()

**Новая реализация:**
- `Chunker._post_process()` — sorted(chunks, key=lambda c: (c.start_line, c.end_line))
- `Validator.validate()` — проверка порядка

**Файл:** `docs/architecture-audit-to-be/04-components.md`

---

## PROP-4: No Empty Chunks

**Определение:** Каждый чанк имеет непустой content.

**Текущая реализация:**
- `Chunk.__post_init__` — ValueError если content пустой

**Новая реализация:**
- `Chunk.__post_init__` — ValueError если content пустой
- `Validator.validate()` — дополнительная проверка

**Файл:** `docs/architecture-audit-to-be/02-types.md`, `04-components.md`

---

## PROP-5: Valid Line Numbers

**Определение:** start_line >= 1, end_line >= start_line.

**Текущая реализация:**
- `Chunk.__post_init__` — ValueError при нарушении

**Новая реализация:**
- `Chunk.__post_init__` — ValueError при нарушении
- `Validator.validate()` — дополнительная проверка

**Файл:** `docs/architecture-audit-to-be/02-types.md`, `04-components.md`

---

## PROP-6: Code Block Integrity

**Определение:** Code blocks не разрезаются между чанками.

**Текущая реализация:**
- `base.py:_validate_code_fence_balance()` — проверка чётности ```
- `preserve_code_blocks` параметр

**Новая реализация:**
- `BaseStrategy._validate_code_fence_balance()` — проверка чётности ```
- `CodeAwareStrategy` — обработка code blocks как атомарных
- `preserve_atomic_blocks` параметр

**Файл:** `docs/architecture-audit-to-be/05-strategies.md`

---

## PROP-7: Table Integrity

**Определение:** Таблицы не разрезаются между чанками.

**Текущая реализация:**
- `TableStrategy` — отдельная стратегия
- `preserve_tables` параметр

**Новая реализация:**
- `CodeAwareStrategy` — таблицы как атомарные блоки
- `preserve_atomic_blocks` параметр (объединяет code + tables)

**Файл:** `docs/architecture-audit-to-be/05-strategies.md`

---

## PROP-8: Serialization Round-Trip

**Определение:** Chunk.from_dict(chunk.to_dict()) == chunk.

**Текущая реализация:**
- `Chunk.to_dict()`, `Chunk.from_dict()`

**Новая реализация:**
- `Chunk.to_dict()`, `Chunk.from_dict()` — без изменений

**Файл:** `docs/architecture-audit-to-be/02-types.md`

---

## Тестовое покрытие

Все свойства покрыты property-based тестами в `docs/architecture-audit-to-be/06-testing.md`:

```python
def test_prop1_no_content_loss(self, md_text: str)
def test_prop2_size_bounds(self, md_text: str)
def test_prop3_monotonic_ordering(self, md_text: str)
def test_prop4_no_empty_chunks(self, md_text: str)
def test_prop5_valid_line_numbers(self, md_text: str)
def test_prop6_code_block_integrity(self, md_text: str)
def test_prop7_table_integrity(self, md_text: str)
def test_prop8_serialization_roundtrip(self, chunk: Chunk)
```

---

## Вывод

Все 8 доменных свойств отражены в новом дизайне:
- ✅ Валидация в Validator
- ✅ Инварианты в Chunk.__post_init__
- ✅ Логика в стратегиях
- ✅ Property-based тесты
