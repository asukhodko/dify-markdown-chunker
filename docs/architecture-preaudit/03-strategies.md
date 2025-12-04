# Strategies Catalog

## Обзор

Каталог всех 6 стратегий чанкинга с анализом критериев выбора, алгоритмов и дублирования кода.

---

## Обзор стратегий

| Стратегия | Приоритет | Назначение | Строк кода |
|-----------|-----------|------------|------------|
| Code | 1 | Документы с преобладанием кода (≥30% кода, ≥1 блок) | 624 |
| Structural | 2 | Документы с иерархией заголовков (≥3 заголовков) | 1720 |
| Mixed | 3 | Смешанный контент с высокой сложностью | 848 |
| List | 4 | Документы с преобладанием списков (≥5 списков) | 856 |
| Table | 5 | Документы с таблицами (≥3 таблиц) | 465 |
| Sentences | 6 | Универсальный fallback (всегда работает) | 525 |

### ⚠️ Проблема: Размер стратегий

`structural_strategy.py` содержит **1720 строк** — это в 3 раза больше других стратегий. Указывает на переусложнение.

---

## Критерии выбора

### CodeStrategy (priority=1)

```python
def can_handle(self, analysis, config):
    return (
        analysis.code_ratio >= config.code_ratio_threshold  # default: 0.3
        and analysis.code_block_count >= config.min_code_blocks  # default: 1
    )
```

**Quality scoring:**
- Base: code_ratio ≥85% → 0.8, ≥70% → 0.6, ≥50% → 0.3
- Bonus: ≥10 blocks → +0.2, ≥5 → +0.15, ≥3 → +0.1
- Bonus: multiple languages → +0.1

### StructuralStrategy (priority=2)

```python
def can_handle(self, analysis, config):
    return (
        analysis.get_total_header_count() >= config.header_count_threshold  # default: 3
        and analysis.max_header_depth > 1
    )
```

**Quality scoring:**
- Base: header_count ≥10 → 0.8, ≥5 → 0.6, ≥3 → 0.4
- Bonus: deep hierarchy (depth ≥3) → +0.1
- Penalty: high code ratio → -0.1

### MixedStrategy (priority=3)

```python
def can_handle(self, analysis, config):
    return (
        analysis.has_mixed_content
        and analysis.complexity_score >= config.min_complexity  # default: 0.3
    )
```

**Quality scoring:**
- Base: complexity ≥0.7 → 0.7, ≥0.5 → 0.5, ≥0.3 → 0.3
- Bonus: balanced content types → +0.2
- Penalty: single dominant type → -0.1

### ListStrategy (priority=4)

```python
def can_handle(self, analysis, config):
    return (
        analysis.list_count >= config.list_count_threshold  # default: 5
        or analysis.list_ratio >= config.list_ratio_threshold  # default: 0.6
    )
```

**⚠️ ВАЖНО**: ListStrategy исключена из автоматического выбора!

```python
# В StrategySelector._select_strict():
safe_strategies = [s for s in self.strategies if s.name != "list"]
logger.info("Auto mode: list strategy excluded for safety (mixed-content risk)")
```

### TableStrategy (priority=5)

```python
def can_handle(self, analysis, config):
    return (
        analysis.table_count >= config.table_count_threshold  # default: 3
        or analysis.table_ratio >= config.table_ratio_threshold  # default: 0.4
    )
```

### SentencesStrategy (priority=6)

```python
def can_handle(self, analysis, config):
    return True  # Всегда может обработать любой контент
```

**Quality scoring:**
- Base: 0.3 (universal applicability)
- Penalties: code (-0.1), headers (-0.1), lists (-0.05), tables (-0.05)
- Bonuses: high text ratio (+0.2), low complexity (+0.1)

---

## Алгоритмы стратегий

### CodeStrategy

1. Извлечь fenced blocks из Stage1Results
2. Создать CodeSegments (code/text)
3. Для каждого code block:
   - Определить язык (из fence или эвристически)
   - Извлечь имена функций/классов
4. Группировать segments в chunks:
   - Code block + surrounding text
   - Не разбивать code blocks
   - Разрешить oversize для больших блоков

### StructuralStrategy

1. Извлечь заголовки и построить иерархию
2. Разбить документ на секции по заголовкам
3. Для каждой секции:
   - Если размер ≤ max_chunk_size → один chunk
   - Если размер > max_chunk_size → разбить по подзаголовкам или параграфам
4. Добавить header_path в метаданные
5. **Phase 2**: Использовать SectionBuilder для семантического качества
6. **Block-based**: Использовать BlockPacker для MC-001, MC-002, MC-005

### MixedStrategy

1. Классифицировать контент по типам (code, text, list, table)
2. Создать ContentBlocks с типами
3. Группировать блоки по типу:
   - Сохранять code blocks целиком
   - Группировать текст с ближайшим кодом
4. Применить size limits

### ListStrategy

1. Извлечь списки из Stage1Results
2. Для каждого списка:
   - Сохранить иерархию (nested lists)
   - Группировать items до max_chunk_size
3. Добавить контекст (текст до/после списка)

### TableStrategy

1. Извлечь таблицы из Stage1Results
2. Для каждой таблицы:
   - Сохранить целиком (atomic)
   - Разрешить oversize для больших таблиц
3. Добавить контекст (заголовок, описание)

### SentencesStrategy

1. Разбить на параграфы (по двойным newlines)
2. Разбить параграфы на предложения (regex)
3. Группировать предложения до max_chunk_size
4. Сохранять границы параграфов где возможно

---

## Дублирование кода между стратегиями

### Общий код в BaseStrategy

```python
class BaseStrategy(ABC):
    # Все стратегии наследуют:
    - _create_chunk()           # Создание chunk с метаданными
    - _validate_chunks()        # Валидация размеров
    - _contains_atomic_element() # Проверка code/table
    - _validate_code_fence_balance()  # Проверка баланса ```
    - _split_at_boundary()      # Разбиение по границам
    - _find_paragraph_boundary()
    - _find_sentence_boundary()
    - _find_word_boundary()
```

### Дублирование между стратегиями

| Функциональность | Code | Structural | Mixed | List | Table | Sentences |
|-----------------|------|------------|-------|------|-------|-----------|
| Извлечение заголовков | - | ✓ | ✓ | - | - | - |
| Обработка code blocks | ✓ | ✓ | ✓ | - | - | - |
| Разбиение по параграфам | - | ✓ | ✓ | - | - | ✓ |
| Разбиение по предложениям | - | ✓ | - | - | - | ✓ |
| Определение языка кода | ✓ | - | ✓ | - | - | - |

### ⚠️ Проблемы дублирования

1. **Header extraction**: Дублируется в Structural и Mixed
2. **Code block handling**: Дублируется в Code, Structural, Mixed
3. **Paragraph splitting**: Дублируется в Structural, Mixed, Sentences
4. **Language detection**: Дублируется в Code и Mixed

---

## Fallback-цепочка

```mermaid
flowchart TD
    START[Выбранная стратегия]
    
    START --> |apply()| PRIMARY{Успех?}
    PRIMARY --> |Да| DONE[ChunkingResult]
    PRIMARY --> |Нет/Exception| STRUCT{Structural?}
    
    STRUCT --> |Не structural| STRUCT_TRY[StructuralStrategy.apply]
    STRUCT --> |Уже structural| SENT_TRY
    
    STRUCT_TRY --> |Успех| DONE_FB1[ChunkingResult + fallback_level=1]
    STRUCT_TRY --> |Нет| SENT_TRY[SentencesStrategy.apply]
    
    SENT_TRY --> |Успех| DONE_FB2[ChunkingResult + fallback_level=2]
    SENT_TRY --> |Нет| ERROR[Empty result + errors]
```

### Уровни fallback

| Level | Стратегия | Когда используется |
|-------|-----------|-------------------|
| 0 | Primary | Выбранная стратегия успешна |
| 1 | Structural | Primary failed, не была structural |
| 2 | Sentences | Structural failed или primary была structural |

### Метаданные fallback

```python
chunk.add_metadata("fallback_level", fallback_level.value)
chunk.add_metadata("fallback_reason", f"Primary strategy failed, used {strategy_name}")
```

---

## Выводы

### Ключевые проблемы стратегий

1. **Переусложнение Structural**: 1720 строк — слишком много для одной стратегии
2. **ListStrategy исключена**: Не используется в auto-mode из-за "mixed-content risk"
3. **Дублирование кода**: Header extraction, code handling, paragraph splitting
4. **Сложная инициализация**: Structural имеет try/except для Phase 2 и block-based
5. **Неочевидные пороги**: code_ratio_threshold=0.3 (было 0.7), min_code_blocks=1 (было 3)

### Рекомендации (предварительные)

1. **Объединить стратегии**: Code + Mixed → одна стратегия для кода
2. **Удалить ListStrategy**: Если исключена из auto-mode, зачем она?
3. **Упростить Structural**: Разбить на части или упростить алгоритм
4. **Вынести общий код**: Header extraction, paragraph splitting → utils
5. **Пересмотреть пороги**: Документировать почему изменены defaults
