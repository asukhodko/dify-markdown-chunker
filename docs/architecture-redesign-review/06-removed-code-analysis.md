# Анализ удаляемого кода

## Удаляемые стратегии

### ListStrategy

**Статус:** ❌ УДАЛЯЕТСЯ

**Причина:** Исключена из auto mode (selector.py:103-105):
```python
# FIX 2: Filter out list strategy in auto mode for safety
# List strategy can lose non-list content in mixed documents
safe_strategies = [s for s in self.strategies if s.name != "list"]
```

**Риск:** Низкий — стратегия уже не используется в auto mode.

**Миграция:** Документы со списками обрабатываются StructuralStrategy или FallbackStrategy.

---

### MixedStrategy

**Статус:** ✅ ОБЪЕДИНЕНА в CodeAwareStrategy

**Логика для переноса:**
- Обработка смешанного контента (код + текст + таблицы)
- Группировка связанных элементов
- Сохранение семантических границ

**В CodeAwareStrategy:**
- Атомарные блоки (code, tables) обрабатываются как единое целое
- Текст между блоками группируется
- Семантические границы сохраняются

---

### TableStrategy

**Статус:** ✅ ОБЪЕДИНЕНА в CodeAwareStrategy

**Логика для переноса:**
- Таблицы как атомарные блоки
- Не разрезать таблицы между чанками
- Метаданные таблиц

**В CodeAwareStrategy:**
- `table_count >= 1` → CodeAwareStrategy
- Таблицы извлекаются как атомарные блоки
- `preserve_atomic_blocks` сохраняет целостность

---

## Удаляемые компоненты

### overlap_manager.py (~400 строк)

**Статус:** ✅ УПРОЩЁН

**Текущая логика:**
- Block-based overlap
- Не разрезать code blocks
- Не включать заголовки из других секций
- 50% limit

**В новом дизайне:**
- `Chunker._apply_overlap()` (~30 строк)
- Проверка на code blocks
- 50% limit
- Симметричное обрезание

**Риск:** Средний — упрощённая логика может не покрыть все edge cases.

---

### metadata_enricher.py (~200 строк)

**Статус:** ✅ ИНТЕГРИРОВАН в стратегии

**Текущая логика:**
- Добавление метаданных по типу контента
- code_metadata, list_metadata, table_metadata

**В новом дизайне:**
- Метаданные добавляются в `_create_chunk()` каждой стратегии
- Базовые метаданные в BaseStrategy

---

### fallback_manager.py (~150 строк)

**Статус:** ✅ УДАЛЁН

**Текущая логика:**
- Цепочка fallback стратегий
- 3 уровня fallback

**В новом дизайне:**
- FallbackStrategy всегда работает (can_handle = True)
- Нет цепочки — один fallback

---

### block_packer.py (~600 строк)

**Статус:** ✅ ИНТЕГРИРОВАН в стратегии

**Текущая логика:**
- Упаковка блоков в чанки
- Обработка атомарных блоков
- URL pool detection

**В новом дизайне:**
- Логика в CodeAwareStrategy._extract_atomic_blocks()
- Логика в CodeAwareStrategy._split_around_atomic()

---

### section_builder.py (~300 строк)

**Статус:** ✅ ИНТЕГРИРОВАН в StructuralStrategy

**Текущая логика:**
- Построение секций из AST
- Иерархия заголовков

**В новом дизайне:**
- StructuralStrategy._split_by_headers()
- StructuralStrategy._update_header_path()

---

## Удаляемые параметры конфигурации

| Параметр | Причина | Новое поведение |
|----------|---------|-----------------|
| target_chunk_size | Избыточен | max/min |
| enable_overlap | Избыточен | overlap_size=0 |
| overlap_percentage | Избыточен | overlap_size |
| min_code_blocks | Упрощено | code_threshold |
| list_count_threshold | ListStrategy удалена | — |
| list_ratio_threshold | ListStrategy удалена | — |
| table_count_threshold | Упрощено | CodeAware |
| table_ratio_threshold | Упрощено | CodeAware |
| preserve_code_blocks | Объединён | preserve_atomic_blocks |
| preserve_tables | Объединён | preserve_atomic_blocks |
| enable_fallback | Всегда True | — |
| fallback_strategy | Всегда sentences | — |
| max_fallback_level | Не нужен | — |
| enable_streaming | Не реализовано | — |
| streaming_threshold | Не реализовано | — |
| detect_url_pools | Не критичен | — |

---

## Backward Compatibility

### Удаляемые алиасы

Нет критичных алиасов для удаления.

### Deprecated функции

| Функция | Замена |
|---------|--------|
| chunk_with_analysis() | chunk(include_analysis=True) |
| chunk_simple() | chunk() с конфигом |
| get_performance_stats() | Удалён |

### Влияние на пользователей

1. **Низкое влияние:** Большинство пользователей используют `chunk()` с defaults
2. **Среднее влияние:** Пользователи с кастомными конфигами — нужна миграция параметров
3. **Высокое влияние:** Пользователи ListStrategy — нужна проверка результатов

---

## Рекомендации

1. **Добавить deprecation warnings** перед удалением функций
2. **Документировать миграцию** параметров конфигурации
3. **Сохранить алиасы** для критичных функций на переходный период
4. **Тестировать** документы со списками после удаления ListStrategy
