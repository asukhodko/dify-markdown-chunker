# Архитектурный Аудит: Анализ Тестов

## Статистика тестов

| Метрика | Значение |
|---------|----------|
| Тестовых файлов | 162 |
| Всего тестов | 1,853 |
| Строк тестового кода | ~45,600 |
| Соотношение тесты/код | 1.9x |
| Property-based тестов | 20+ файлов |

## Проблема: Тестов почти в 2 раза больше кода

```
Код:   ~24,000 строк  ████████████
Тесты: ~45,600 строк  ███████████████████████
```

Это аномальное соотношение указывает на:
- Тесты реализации вместо тестов поведения
- Дублирование тестов
- Тесты для конкретных багфиксов

## Классификация тестов

### Property-based тесты (20 файлов) ✓

Тестируют доменные свойства:
```
test_data_preservation_properties.py    # PROP-1: No content loss
test_critical_properties.py             # PROP-2: Size bounds
test_monotonic_ordering_property.py     # PROP-3: Ordering
test_no_empty_chunks_property.py        # PROP-4: No empty
test_code_strategy_properties.py        # PROP-6: Code integrity
test_serialization_roundtrip_property.py # PROP-8: Round-trip
test_idempotence_property.py            # PROP-9: Idempotence
test_header_path_property.py            # PROP-10: Header paths
```

**Оценка:** Хорошо, но избыточно — многие свойства тестируются в нескольких файлах.

### Тесты реализации (~130 файлов) ⚠️

Тестируют КАК работает система:
```python
# test_chunker.py
def test_chunk_returns_list_of_chunks():
    # Тестирует конкретный тип возврата

# test_strategy_selector.py
def test_selector_prefers_code_strategy_for_high_code_ratio():
    # Тестирует внутреннюю логику выбора

# test_fallback_manager_integration.py
def test_fallback_to_structural_when_code_fails():
    # Тестирует конкретный fallback механизм
```

**Проблема:** При рефакторинге эти тесты сломаются, даже если поведение останется корректным.

### Тесты для багфиксов ⚠️

```
test_critical_fixes.py           # Phase 1 fixes
test_overlap_duplication.py      # MC-003
test_phase2_properties.py        # Phase 2
test_regression_prevention.py    # Regression
```

**Проблема:** Фиксируют конкретные исправления вместо общих свойств.

## Дублирование тестов

### Overlap тестируется в 5+ местах:

```
tests/chunker/test_overlap_properties.py
tests/chunker/test_overlap_properties_redesign.py
tests/integration/test_overlap_integration.py
tests/integration/test_overlap_redesign_integration.py
tests/regression/test_overlap_duplication.py
```

### Strategy тесты дублируются:

```
test_code_strategy_properties.py      # ~200 строк
test_list_strategy_properties.py      # ~200 строк
test_mixed_strategy_properties.py     # ~200 строк
test_sentences_strategy_properties.py # ~200 строк
test_structural_strategy_properties.py # ~200 строк
test_table_strategy_properties.py     # ~200 строк
```

Каждый файл содержит похожие тесты для разных стратегий.

### Integration тесты пересекаются:

```
test_full_pipeline.py
test_full_pipeline_real_docs.py
test_end_to_end.py
test_full_api_flow.py
```

## Покрытие доменных свойств

### Хорошо покрытые (избыточно):

| Свойство | Файлов | Оценка |
|----------|--------|--------|
| No Content Loss | 5+ | Избыточно |
| Size Bounds | 4+ | Избыточно |
| Code Integrity | 3+ | Избыточно |

### Слабо покрытые:

| Свойство | Покрытие |
|----------|----------|
| Semantic coherence | ✗ |
| Performance bounds | ✗ |
| Memory bounds | ✗ |
| Determinism | Частично |

## Минимальный набор тестов для редизайна

### Критические property-based тесты (5):

```python
# 1. No Content Loss (PROP-1)
@given(markdown_documents())
def test_no_content_loss(doc):
    chunks = chunker.chunk(doc)
    reconstructed = reconstruct(chunks)
    assert content_equivalent(doc, reconstructed)

# 2. Size Bounds (PROP-2)
@given(markdown_documents(), chunk_configs())
def test_size_bounds(doc, config):
    chunks = chunker.chunk(doc, config)
    for chunk in chunks:
        assert len(chunk.content) <= config.max_chunk_size or chunk.is_oversize

# 3. Monotonic Ordering (PROP-3)
@given(markdown_documents())
def test_monotonic_ordering(doc):
    chunks = chunker.chunk(doc)
    for i in range(len(chunks) - 1):
        assert chunks[i].start_line <= chunks[i+1].start_line

# 4. No Empty Chunks (PROP-4)
@given(markdown_documents())
def test_no_empty_chunks(doc):
    chunks = chunker.chunk(doc)
    for chunk in chunks:
        assert chunk.content.strip()

# 5. Valid Line Numbers (PROP-5)
@given(markdown_documents())
def test_valid_line_numbers(doc):
    chunks = chunker.chunk(doc)
    for chunk in chunks:
        assert chunk.start_line >= 1
        assert chunk.end_line >= chunk.start_line
```

### Важные property-based тесты (3):

```python
# 6. Code Block Integrity (PROP-6)
@given(markdown_with_code())
def test_code_block_integrity(doc):
    chunks = chunker.chunk(doc)
    for block in extract_code_blocks(doc):
        assert exactly_one_chunk_contains(chunks, block)

# 7. Table Integrity (PROP-7)
@given(markdown_with_tables())
def test_table_integrity(doc):
    chunks = chunker.chunk(doc)
    for table in extract_tables(doc):
        assert exactly_one_chunk_contains(chunks, table)

# 8. Serialization Round-Trip (PROP-8)
@given(chunking_results())
def test_serialization_roundtrip(result):
    serialized = result.to_dict()
    deserialized = ChunkingResult.from_dict(serialized)
    assert result == deserialized
```

### Unit тесты для edge cases (~20):

```python
# Пустой документ
def test_empty_document():
    assert chunker.chunk("") == []

# Только whitespace
def test_whitespace_only():
    assert chunker.chunk("   \n\n   ") == []

# Один символ
def test_single_char():
    chunks = chunker.chunk("x")
    assert len(chunks) == 1

# Очень большой code block
def test_huge_code_block():
    doc = "```\n" + "x" * 10000 + "\n```"
    chunks = chunker.chunk(doc)
    assert len(chunks) == 1
    assert chunks[0].is_oversize
```

### Integration тест (1):

```python
def test_full_pipeline():
    doc = load_real_document("complex_doc.md")
    result = chunker.chunk(doc, include_analysis=True)
    
    assert result.success
    assert result.chunks
    assert all(c.content.strip() for c in result.chunks)
    assert result.processing_time < 10.0  # Performance bound
```

## Целевые метрики тестов

| Метрика | Было | Цель |
|---------|------|------|
| Тестовых файлов | 162 | ~10 |
| Всего тестов | 1,853 | ~50-100 |
| Строк тестов | ~45,600 | ~2,000 |
| Соотношение | 1.9x | 0.4x |
| Property-based | 20 файлов | 1-2 файла |
| Unit тесты | ~130 файлов | 1-2 файла |
| Integration | 11 файлов | 1 файл |

## Рекомендации

1. **Удалить тесты реализации** — оставить только property-based
2. **Объединить property тесты** — один файл для всех свойств
3. **Параметризовать strategy тесты** — один тест для всех стратегий
4. **Удалить дублирование** — один файл для overlap
5. **Удалить тесты багфиксов** — заменить на общие свойства
