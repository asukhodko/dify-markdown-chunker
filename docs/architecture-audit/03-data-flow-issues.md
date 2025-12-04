# Архитектурный Аудит: Проблемы Потока Данных

## Основной поток данных

```
Input: md_text (string)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Stage 1: Parsing (ParserInterface.process_document)         │
│   ├── AST Building                                          │
│   ├── Fenced Block Extraction                               │
│   ├── Element Detection                                     │
│   └── Content Analysis                                      │
│   Output: Stage1Results                                     │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Stage 2: Chunking (ChunkingOrchestrator)                    │
│   ├── Strategy Selection                                    │
│   ├── Strategy Application                                  │
│   └── Fallback (if needed)                                  │
│   Output: ChunkingResult                                    │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Post-Processing #1 (orchestrator._apply_block_based_...)    │
│   ├── BlockOverlapManager (MC-003)                          │
│   ├── HeaderPathValidator (MC-006)                          │
│   ├── ChunkSizeNormalizer (MC-004)                          │
│   └── normalize_line_breaks (Fix #7)                        │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Post-Processing #2 (core._post_process_chunks)              │
│   ├── OverlapManager (legacy, if block_based=False)         │
│   ├── MetadataEnricher                                      │
│   ├── DataCompletenessValidator                             │
│   └── Preamble Processing (ПОВТОРНЫЙ Stage 1!)              │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Output Transform (OutputTransformer.transform)              │
│   Output: List[Chunk] | ChunkingResult | dict               │
└─────────────────────────────────────────────────────────────┘
```

## Проблема 1: Двойной вызов Stage 1

**Где происходит:**
1. `orchestrator._run_stage1_analysis()` — основной анализ
2. `core._post_process_chunks()` — для preamble

```python
# В core.py _post_process_chunks():
if chunks and self.config.extract_preamble:
    try:
        stage1_results = self.stage1.process_document(md_text)  # ПОВТОРНЫЙ ВЫЗОВ!
        if stage1_results.analysis.preamble:
            chunks = self._process_preamble(chunks, stage1_results.analysis.preamble)
```

**Влияние:**
- Удвоение времени парсинга
- Лишнее использование памяти
- Потенциальные расхождения результатов

**Решение:** Передавать `stage1_results` через весь pipeline.

## Проблема 2: Два механизма Overlap

**Legacy механизм:**
```python
# components/overlap_manager.py — 926 строк
class OverlapManager:
    def apply_overlap(self, chunks, include_metadata):
        # Старая логика overlap
```

**Новый механизм:**
```python
# block_overlap_manager.py — 263 строки
class BlockOverlapManager:
    def apply_block_overlap(self, chunks, blocks_by_chunk):
        # Новая block-based логика
```

**Условное переключение:**
```python
# В orchestrator:
if self.config.block_based_overlap and self._block_overlap_manager:
    chunks = self._block_overlap_manager.apply_block_overlap(...)

# В core.py:
if self.config.enable_overlap and not self.config.block_based_overlap:
    chunks = self._overlap_manager.apply_overlap(...)
```

**Влияние:**
- Сложность понимания какой механизм используется
- Два набора тестов
- Потенциальные баги при переключении

**Решение:** Удалить legacy механизм, оставить только block-based.

## Проблема 3: Двойная пост-обработка

**В orchestrator (block-based):**
```python
def _apply_block_based_postprocessing(self, result, stage1_results):
    # Step 1: Block-based overlap (MC-003)
    # Step 2: Header path validation (MC-006)
    # Step 3: Chunk size normalization (MC-004)
    # Step 4: Line break normalization (Fix #7)
```

**В core (legacy):**
```python
def _post_process_chunks(self, result, md_text, include_metadata):
    # Stage 3: Apply overlap (legacy)
    # Stage 4: Enrich metadata
    # Stage 4.5: Validate data completeness
    # Stage 5: Process preamble
```

**Влияние:**
- Непонятно какие шаги выполняются
- Дублирование логики
- Сложность отладки

**Решение:** Объединить в единый линейный pipeline.

## Проблема 4: Распределённая валидация

**Места валидации:**

1. `orchestrator._validate_content_completeness()`
2. `orchestrator.validate_no_excessive_duplication()`
3. `orchestrator.validate_overlap_accuracy()`
4. `orchestrator._validate_size_compliance()`
5. `core._post_process_chunks()` → `validator.validate_chunks()`

**Влияние:**
- Сложно понять полный набор проверок
- Дублирование проверок
- Разная обработка ошибок

**Решение:** Один валидатор в одном месте.

## Проблема 5: Распределённое обогащение метаданных

**Места добавления метаданных:**

1. В стратегии (`_create_chunk()`)
2. В `MetadataEnricher.enrich_chunks()`
3. В `FallbackManager._create_fallback_result()`
4. В `_validate_size_compliance()` (oversize flags)
5. В `_process_preamble()`

**Влияние:**
- Непредсказуемый набор метаданных
- Сложность документирования
- Потенциальные конфликты

**Решение:** Централизованное обогащение метаданных.

## Проблема 6: Сложная условная логика

```python
# Примеры условий в коде:

# В orchestrator:
if BLOCK_BASED_AVAILABLE:
    # ...

if self.config.block_based_overlap and self._block_overlap_manager:
    # ...

if self.config.min_effective_chunk_size > 0 and self._chunk_size_normalizer:
    # ...

if self.config.enable_content_validation:
    # ...

# В core:
if self.config.enable_overlap and not self.config.block_based_overlap:
    # ...

if chunks and self.config.extract_preamble:
    # ...
```

**Влияние:**
- Сложность понимания поведения
- Комбинаторный взрыв тестовых сценариев
- Потенциальные баги в редких комбинациях

**Решение:** Упростить конфигурацию, убрать условные флаги.

## Диаграмма проблем

```
┌─────────────────────────────────────────────────────────────┐
│                    ПРОБЛЕМЫ ПОТОКА ДАННЫХ                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────┐     ┌─────────┐                               │
│  │ Stage 1 │────▶│ Stage 1 │  ❌ Двойной вызов             │
│  └─────────┘     └─────────┘                               │
│       │               │                                     │
│       ▼               ▼                                     │
│  ┌─────────┐     ┌─────────┐                               │
│  │ Overlap │     │ Overlap │  ❌ Два механизма             │
│  │ (block) │     │ (legacy)│                               │
│  └─────────┘     └─────────┘                               │
│       │               │                                     │
│       ▼               ▼                                     │
│  ┌─────────┐     ┌─────────┐                               │
│  │PostProc │     │PostProc │  ❌ Двойная обработка         │
│  │   #1    │     │   #2    │                               │
│  └─────────┘     └─────────┘                               │
│       │               │                                     │
│       ▼               ▼                                     │
│  ┌─────────────────────────┐                               │
│  │ Валидация в 5+ местах   │  ❌ Распределённая            │
│  └─────────────────────────┘                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Рекомендации

1. **Кэшировать Stage1Results** — не вызывать повторно
2. **Удалить legacy overlap** — оставить только block-based
3. **Объединить пост-обработку** — один линейный pipeline
4. **Централизовать валидацию** — один валидатор
5. **Централизовать метаданные** — одно место обогащения
6. **Упростить конфигурацию** — убрать условные флаги
