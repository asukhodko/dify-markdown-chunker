# Architecture Smells

## Обзор

Выявленные архитектурные проблемы с приоритизацией и рекомендациями.

---

## Переусложнение

### SMELL-1: Слишком много файлов (HIGH)

**Проблема:** 55 Python-файлов для относительно простой задачи (разбиение markdown на чанки).

**Примеры:**
- `chunker/` содержит 26 файлов
- `parser/` содержит 15 файлов
- Отдельные файлы для каждой стратегии (6 файлов)
- Отдельные файлы для каждого компонента (overlap, metadata, fallback)

**Рекомендация:** Объединить в 5-10 файлов.

### SMELL-2: Раздутые файлы (HIGH)

**Проблема:** Несколько файлов превышают 700 строк.

| Файл | Строк | Проблема |
|------|-------|----------|
| `structural_strategy.py` | 1720 | Слишком много логики в одной стратегии |
| `types.py` (chunker) | 1079 | Слишком много типов |
| `types.py` (parser) | 931 | Дублирование с chunker/types.py |
| `overlap_manager.py` | 926 | Сложная логика overlap |

**Рекомендация:** Разбить или упростить.

### SMELL-3: 32 параметра конфигурации (HIGH)

**Проблема:** ChunkConfig содержит 32 параметра — сложно понять и настроить.

**Категории:**
- 5 параметров размеров
- 4 параметра overlap
- 8 порогов стратегий
- 4 поведенческих флага
- 6 параметров для багфиксов
- 5 прочих

**Рекомендация:** Сократить до 10-15 параметров.

### SMELL-4: 6 стратегий с дублированием (MEDIUM)

**Проблема:** 6 стратегий с похожим кодом, одна из которых (List) исключена из auto-mode.

**Дублирование:**
- Header extraction в Structural и Mixed
- Code block handling в Code, Structural, Mixed
- Paragraph splitting в Structural, Mixed, Sentences

**Рекомендация:** Объединить в 2-3 стратегии.

---

## Избыточные абстракции

### SMELL-5: Двойной механизм overlap (HIGH)

**Проблема:** Два механизма overlap с условным переключением.

```python
# В orchestrator:
if self.config.block_based_overlap:
    chunks = self._block_overlap_manager.apply_block_overlap(...)

# В core.py:
if self.config.enable_overlap and not self.config.block_based_overlap:
    chunks = self._overlap_manager.apply_overlap(...)
```

**Рекомендация:** Выбрать один механизм, удалить второй.

### SMELL-6: Двойная пост-обработка (HIGH)

**Проблема:** Пост-обработка в двух местах.

```
orchestrator._apply_block_based_postprocessing()
├── BlockOverlapManager
├── HeaderPathValidator
├── ChunkSizeNormalizer
└── normalize_line_breaks

core._post_process_chunks()
├── OverlapManager
├── MetadataEnricher
├── DataCompletenessValidator
└── _process_preamble
```

**Рекомендация:** Объединить в один pipeline.

### SMELL-7: Множественные валидаторы (MEDIUM)

**Проблема:** Валидация в 4+ местах.

```python
# orchestrator.py:
self._validate_content_completeness(md_text, result.chunks)
validate_no_excessive_duplication(result.chunks)
validate_overlap_accuracy(result.chunks)
result.chunks = self._validate_size_compliance(result.chunks)

# core.py:
validation_result = self._validator.validate_chunks(md_text, chunks)
```

**Рекомендация:** Один валидатор в одном месте.

### SMELL-8: Раздутый публичный API parser (MEDIUM)

**Проблема:** `parser/__init__.py` экспортирует 50+ символов.

```python
__all__ = [
    # 7 функций
    # 8 Simple API (deprecated)
    # 4 Core classes
    # 4 Nesting resolver (backward compatibility)
    # 3 AST classes
    # 8 Validation classes
    # 6 Error classes
    # 3 Utility classes
    # 4 Preamble
    # 5 Data types
    # 4 Validation functions
    # 1 Error function
    # 5 Utility functions
]
```

**Рекомендация:** Сократить до 10-15 символов.

---

## Код обратной совместимости

### SMELL-9: Deprecated Simple API (LOW)

**Проблема:** Deprecated код не удалён.

```python
# parser/__init__.py
try:
    from .simple_api import (
        analyze, check_markdown_quality, ...
    )
except ImportError:
    def analyze(*args, **kwargs):
        raise NotImplementedError("simple_api has been removed")
```

**Рекомендация:** Удалить deprecated код.

### SMELL-10: Backward compatibility aliases (LOW)

**Проблема:** Много алиасов для совместимости.

```python
# parser/__init__.py
ParserInterface = Stage1Interface  # Alias
ValidationError = MarkdownParsingError  # Alias
APIValidationError = ValidationError  # Alias
```

**Рекомендация:** Удалить алиасы, использовать новые имена.

### SMELL-11: Try/except imports (LOW)

**Проблема:** Много try/except для импортов.

```python
try:
    from .nesting_resolver import ...
except ImportError:
    class BlockCandidate:
        pass
    class NestingResolver:
        pass
```

**Рекомендация:** Удалить fallback-определения.

---

## Паттерны "фикс на фикс"

### SMELL-12: Phase 1, Phase 2, MC-* fixes (HIGH)

**Проблема:** Код содержит множество слоёв исправлений.

**Хронология:**
1. **Phase 1**: Базовая реализация
2. **Phase 1.1**: CRITICAL FIX для code blocks
3. **Phase 1.2**: CRITICAL FIX для oversize chunks
4. **Phase 2**: Semantic quality improvements
5. **Phase 2.2**: CRITICAL FIX для overlap limit
6. **MC-001**: Section fragmentation fix
7. **MC-002**: Structural breaks fix
8. **MC-003**: Overlap issues fix
9. **MC-004**: Size variance fix
10. **MC-005**: Preamble/link block fix
11. **MC-006**: Header path fix
12. **Fix #3, Fix #7**: Дополнительные исправления

**Примеры в коде:**
```python
# CRITICAL FIX (Phase 1.1): Ensures complete code block extraction
# CRITICAL FIX (Phase 1.2): Ensure all oversize chunks are flagged
# CRITICAL FIX (Phase 2.2): Enforce 50% total overlap limit
# FIX 3: Validate content completeness
# FIX: Sort chunks by document position (Requirements 2.1, 2.2)
```

**Рекомендация:** Переписать с нуля с учётом всех требований.

### SMELL-13: Условные флаги для fixes (MEDIUM)

**Проблема:** Параметры конфигурации для включения/выключения fixes.

```python
block_based_splitting: bool = True  # MC-001, MC-002, MC-005
allow_oversize_for_integrity: bool = True  # MC-001
min_effective_chunk_size: int = 0  # MC-004
block_based_overlap: bool = True  # MC-003
detect_url_pools: bool = True  # MC-005
enable_content_validation: bool = True  # Phase 1 Fix 3
```

**Рекомендация:** Сделать fixes поведением по умолчанию, удалить флаги.

---

## Сводная таблица проблем

| ID | Проблема | Severity | Effort | Priority |
|----|----------|----------|--------|----------|
| SMELL-1 | Слишком много файлов | HIGH | HIGH | 1 |
| SMELL-2 | Раздутые файлы | HIGH | MEDIUM | 2 |
| SMELL-3 | 32 параметра конфигурации | HIGH | MEDIUM | 3 |
| SMELL-12 | Phase/MC fixes | HIGH | HIGH | 4 |
| SMELL-5 | Двойной overlap | HIGH | LOW | 5 |
| SMELL-6 | Двойная пост-обработка | HIGH | MEDIUM | 6 |
| SMELL-4 | 6 стратегий | MEDIUM | MEDIUM | 7 |
| SMELL-7 | Множественные валидаторы | MEDIUM | LOW | 8 |
| SMELL-8 | Раздутый API | MEDIUM | LOW | 9 |
| SMELL-13 | Флаги для fixes | MEDIUM | LOW | 10 |
| SMELL-9 | Deprecated API | LOW | LOW | 11 |
| SMELL-10 | Backward aliases | LOW | LOW | 12 |
| SMELL-11 | Try/except imports | LOW | LOW | 13 |

---

## Выводы

### Корневая причина

Проект развивался итеративно с добавлением fixes поверх fixes. Каждый новый баг приводил к добавлению нового слоя кода вместо рефакторинга.

### Рекомендация

**Полный редизайн** с учётом всех выявленных требований, а не попытка исправить существующий код.
