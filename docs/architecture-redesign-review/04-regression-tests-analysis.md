# Анализ Regression Тестов

## Обзор

Анализ regression тестов для понимания критических фиксов, которые должны быть сохранены в новом дизайне.

---

## test_critical_fixes.py

### Тесты

| Тест | Что проверяет | В новом дизайне |
|------|---------------|-----------------|
| `test_mixed_strategy_lists` | MixedStrategy работает со списками | ✅ CodeAwareStrategy |
| `test_mixed_strategy_tables` | MixedStrategy работает с таблицами | ✅ CodeAwareStrategy |
| `test_list_strategy_integration` | ListStrategy работает | ❌ ListStrategy удалена |
| `test_no_attribute_errors` | Нет AttributeError | ✅ Упрощённый код |

### Анализ

1. **MixedStrategy** → объединена в CodeAwareStrategy
   - Тесты должны работать, т.к. CodeAwareStrategy обрабатывает таблицы и смешанный контент
   
2. **ListStrategy** → удалена
   - Тест `test_list_strategy_integration` нужно обновить
   - Документы со списками будут обрабатываться StructuralStrategy или FallbackStrategy

3. **AttributeError** — проблема была в доступе к несуществующим атрибутам Stage1Results
   - В новом дизайне ContentAnalysis имеет чёткую структуру
   - Риск AttributeError минимален

### Рекомендации

- Обновить тесты для нового API
- Удалить тест `test_list_strategy_integration` или переписать для FallbackStrategy
- Добавить тесты для CodeAwareStrategy с таблицами и списками

---

## test_overlap_duplication.py

### Тесты

| Тест | Что проверяет | В новом дизайне |
|------|---------------|-----------------|
| `test_anti_fraud_phrase_no_duplication_metadata_mode` | Нет дублирования в metadata mode | ⚠️ Проверить |
| `test_anti_fraud_phrase_context_separation` | Разделение content/context | ⚠️ Проверить |
| `test_anti_fraud_phrase_legacy_mode_no_duplication` | Нет дублирования в legacy mode | ⚠️ Проверить |
| `test_no_content_duplication_at_boundaries` | Нет дублирования на границах | ⚠️ Проверить |
| `test_offset_based_verification` | Offsets соответствуют контенту | ⚠️ Проверить |
| `test_block_aligned_extraction_prevents_duplication` | Block-aligned overlap | ⚠️ Проверить |

### Анализ

Эти тесты проверяют критическую проблему — дублирование контента при overlap.

**Текущая реализация:**
- `block_overlap_manager.py` — block-based overlap
- Overlap содержит только полные блоки
- Не включает контент, который уже есть в чанке

**Новый дизайн:**
- Упрощённый `_apply_overlap()` в Chunker
- Character-based overlap с проверками

### Риски

1. **Дублирование контента** — упрощённый overlap может дублировать
2. **Разрезание code blocks** — проверка добавлена, но упрощена
3. **Metadata mode vs Legacy mode** — в новом дизайне только metadata mode

### Рекомендации

1. Сохранить эти тесты как regression suite
2. Убедиться, что `_apply_overlap()` не дублирует контент
3. Добавить проверку на дублирование в Validator

---

## Критические проверки для нового дизайна

### Из test_critical_fixes.py

```python
# Должны работать без AttributeError
def test_no_attribute_errors():
    chunker = MarkdownChunker()
    result = chunker.chunk("# Doc\n\n- List item")
    assert len(result.chunks) > 0
    assert result.strategy_used != "emergency"
```

### Из test_overlap_duplication.py

```python
# Контент не должен дублироваться
def test_no_content_duplication():
    config = ChunkConfig(max_chunk_size=200, overlap_size=50)
    chunker = MarkdownChunker(config)
    result = chunker.chunk(text)
    
    for chunk in result.chunks:
        # Фраза не должна появляться дважды в content
        assert chunk.content.count(phrase) <= 1
        
        # Если фраза в content, не должна быть в previous_content
        if phrase in chunk.content:
            prev = chunk.metadata.get("previous_content", "")
            assert phrase not in prev
```

---

## Сводка

### Тесты для сохранения

1. ✅ `test_no_attribute_errors` — базовая работоспособность
2. ✅ `test_anti_fraud_phrase_no_duplication_metadata_mode` — критичный
3. ✅ `test_no_content_duplication_at_boundaries` — критичный
4. ✅ `test_offset_based_verification` — если используем offsets

### Тесты для обновления

1. ⚠️ `test_mixed_strategy_lists` → тест для CodeAwareStrategy
2. ⚠️ `test_mixed_strategy_tables` → тест для CodeAwareStrategy
3. ❌ `test_list_strategy_integration` → удалить или переписать

### Тесты для добавления

1. Тест на oversize_tolerance (MC-001)
2. Тест на code fence balance (Phase 1.1)
3. Тест на 50% overlap limit (Phase 2.2)
