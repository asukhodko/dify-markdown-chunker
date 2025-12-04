# Domain Properties

## Обзор

Формализованные доменные свойства системы чанкинга для использования в редизайне.

---

## Инварианты

### PROP-1: No Content Loss (CRITICAL)

**Формулировка:** Для любого валидного markdown-документа, конкатенация содержимого всех чанков (за вычетом overlap) должна быть эквивалентна исходному документу.

```
∀ doc ∈ ValidMarkdown:
  concat(chunks) - overlaps ≡ doc
```

**Текущие тесты:**
- `test_data_preservation_properties.py`
- `test_critical_properties.py`

**Статус:** ✓ Покрыто

### PROP-2: Chunk Size Bounds (CRITICAL)

**Формулировка:** Для любого чанка, его размер должен быть ≤ max_chunk_size, ИЛИ чанк должен быть помечен как allow_oversize=True.

```
∀ chunk ∈ Chunks:
  len(chunk.content) ≤ config.max_chunk_size 
  ∨ chunk.metadata["allow_oversize"] = True
```

**Текущие тесты:**
- `test_critical_properties.py`

**Статус:** ✓ Покрыто

### PROP-3: Monotonic Ordering (CRITICAL)

**Формулировка:** Для любой последовательности чанков, значения start_line должны быть монотонно возрастающими.

```
∀ i < j:
  chunks[i].start_line ≤ chunks[j].start_line
```

**Текущие тесты:**
- `test_monotonic_ordering_property.py`

**Статус:** ✓ Покрыто

### PROP-4: No Empty Chunks (CRITICAL)

**Формулировка:** Для любого чанка, его содержимое не должно быть пустым или состоять только из whitespace.

```
∀ chunk ∈ Chunks:
  chunk.content.strip() ≠ ""
```

**Текущие тесты:**
- `test_no_empty_chunks_property.py`

**Статус:** ✓ Покрыто

### PROP-5: Valid Line Numbers (CRITICAL)

**Формулировка:** Для любого чанка, start_line ≥ 1 и end_line ≥ start_line.

```
∀ chunk ∈ Chunks:
  chunk.start_line ≥ 1 ∧ chunk.end_line ≥ chunk.start_line
```

**Текущие тесты:**
- `test_types.py` (в __post_init__)

**Статус:** ✓ Покрыто (валидация в конструкторе)

---

## Семантические свойства

### PROP-6: Code Block Integrity (HIGH)

**Формулировка:** Для любого code block в исходном документе, он должен появиться целиком в ровно одном чанке (не разбит между чанками).

```
∀ code_block ∈ doc.code_blocks:
  ∃! chunk ∈ Chunks: code_block ⊆ chunk.content
```

**Текущие тесты:**
- `test_code_strategy_properties.py`
- `test_critical_properties.py`

**Статус:** ✓ Покрыто

### PROP-7: Table Integrity (HIGH)

**Формулировка:** Для любой таблицы в исходном документе, она должна появиться целиком в ровно одном чанке.

```
∀ table ∈ doc.tables:
  ∃! chunk ∈ Chunks: table ⊆ chunk.content
```

**Текущие тесты:**
- `test_table_strategy_properties.py`

**Статус:** ✓ Покрыто

### PROP-8: Serialization Round-Trip (HIGH)

**Формулировка:** Для любого ChunkingResult, сериализация в dict и обратно должна давать эквивалентный результат.

```
∀ result ∈ ChunkingResult:
  ChunkingResult.from_dict(result.to_dict()) ≡ result
```

**Текущие тесты:**
- `test_serialization_roundtrip_property.py`

**Статус:** ✓ Покрыто

### PROP-9: Idempotence (MEDIUM)

**Формулировка:** Повторный чанкинг того же документа с той же конфигурацией должен давать идентичный результат.

```
∀ doc, config:
  chunk(doc, config) ≡ chunk(doc, config)
```

**Текущие тесты:**
- `test_idempotence_property.py`

**Статус:** ✓ Покрыто

### PROP-10: Header Path Correctness (MEDIUM)

**Формулировка:** Для любого чанка с header_path, путь должен соответствовать реальной иерархии заголовков в документе.

```
∀ chunk with header_path:
  header_path reflects actual document hierarchy
```

**Текущие тесты:**
- `test_header_path_property.py`

**Статус:** ✓ Покрыто

---

## Сопоставление с тестами

### Матрица покрытия

| Свойство | Property Test | Unit Test | Integration Test |
|----------|---------------|-----------|------------------|
| PROP-1 No Content Loss | ✓ | ✓ | ✓ |
| PROP-2 Size Bounds | ✓ | ✓ | ✓ |
| PROP-3 Monotonic Order | ✓ | - | ✓ |
| PROP-4 No Empty | ✓ | ✓ | - |
| PROP-5 Valid Lines | - | ✓ | - |
| PROP-6 Code Integrity | ✓ | ✓ | ✓ |
| PROP-7 Table Integrity | ✓ | ✓ | - |
| PROP-8 Round-Trip | ✓ | - | - |
| PROP-9 Idempotence | ✓ | - | - |
| PROP-10 Header Path | ✓ | ✓ | - |

### Избыточное покрытие

Многие свойства тестируются в нескольких местах:
- PROP-1 тестируется в 5+ файлах
- PROP-2 тестируется в 4+ файлах
- PROP-6 тестируется в 3+ файлах

---

## Минимальный набор свойств для нового дизайна

### Критические (MUST HAVE)

| # | Свойство | Описание |
|---|----------|----------|
| 1 | No Content Loss | Весь контент сохраняется |
| 2 | Size Bounds | Чанки в пределах лимитов |
| 3 | Monotonic Order | Чанки в порядке документа |
| 4 | No Empty Chunks | Нет пустых чанков |
| 5 | Valid Line Numbers | Корректные номера строк |

### Важные (SHOULD HAVE)

| # | Свойство | Описание |
|---|----------|----------|
| 6 | Code Block Integrity | Code blocks не разбиваются |
| 7 | Table Integrity | Таблицы не разбиваются |
| 8 | Serialization Round-Trip | Сериализация обратима |

### Желательные (NICE TO HAVE)

| # | Свойство | Описание |
|---|----------|----------|
| 9 | Idempotence | Детерминированный результат |
| 10 | Header Path | Корректные пути заголовков |

---

## Предложение для нового дизайна

### Минимальный контракт

```python
@dataclass
class ChunkingContract:
    """Контракт, который должна выполнять любая реализация чанкера."""
    
    # CRITICAL
    no_content_loss: bool = True      # PROP-1
    size_bounds: bool = True          # PROP-2
    monotonic_order: bool = True      # PROP-3
    no_empty_chunks: bool = True      # PROP-4
    valid_line_numbers: bool = True   # PROP-5
    
    # HIGH
    code_block_integrity: bool = True # PROP-6
    table_integrity: bool = True      # PROP-7
    serialization_roundtrip: bool = True  # PROP-8
```

### Тестовая стратегия

1. **5 критических property-based тестов** для PROP-1 через PROP-5
2. **3 важных property-based теста** для PROP-6 через PROP-8
3. **Минимум unit тестов** только для edge cases
4. **1 integration тест** для full pipeline

**Целевое количество тестов:** ~50 (вместо 1853)
