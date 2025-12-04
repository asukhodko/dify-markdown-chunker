# Data Flow Analysis

## Обзор

Анализ потока данных через систему чанкинга от входного markdown до выходных чанков.

---

## Основной поток данных

```mermaid
flowchart TD
    INPUT[/"md_text: str"/]
    
    subgraph Stage1["Stage 1: Parsing"]
        PARSER[ParserInterface.process_document]
        AST[AST Building]
        FENCED[Fenced Block Extraction]
        ELEMENTS[Element Detection]
        ANALYSIS[Content Analysis]
    end
    
    subgraph Stage2["Stage 2: Chunking"]
        ORCH[ChunkingOrchestrator]
        SELECTOR[StrategySelector]
        STRATEGY[Selected Strategy.apply]
        FALLBACK[FallbackManager]
    end
    
    subgraph PostProcess["Post-Processing"]
        BLOCK_POST[Block-based Post-processing]
        OVERLAP[OverlapManager]
        META[MetadataEnricher]
        VALID[DataCompletenessValidator]
        PREAMBLE[Preamble Processing]
    end
    
    subgraph Transform["Output Transform"]
        TRANS[OutputTransformer]
    end
    
    INPUT --> PARSER
    PARSER --> AST --> FENCED --> ELEMENTS --> ANALYSIS
    ANALYSIS --> |Stage1Results| ORCH
    
    ORCH --> SELECTOR
    SELECTOR --> |ContentAnalysis| STRATEGY
    STRATEGY --> |List[Chunk]| FALLBACK
    FALLBACK --> |ChunkingResult| BLOCK_POST
    
    BLOCK_POST --> OVERLAP
    OVERLAP --> META
    META --> VALID
    VALID --> PREAMBLE
    PREAMBLE --> |ChunkingResult| TRANS
    
    TRANS --> OUTPUT[/"List[Chunk] | ChunkingResult | dict"/]
```

### Детальный путь вызовов

```
MarkdownChunker.chunk(md_text)
├── _validate_chunk_params()
├── _orchestrator.chunk_with_strategy(md_text, strategy)
│   ├── _run_stage1_analysis(md_text)
│   │   └── ParserInterface.process_document(md_text)
│   │       ├── safe_parse_to_ast()
│   │       ├── safe_extract_fenced_blocks()
│   │       ├── safe_detect_elements()
│   │       └── safe_analyze_content()
│   │       └── → Stage1Results
│   ├── _select_and_apply_strategy()
│   │   ├── StrategySelector.select_strategy()
│   │   └── FallbackManager.execute_with_fallback()
│   │       └── Strategy.apply() → List[Chunk]
│   ├── _apply_block_based_postprocessing()
│   │   ├── BlockOverlapManager.apply_block_overlap()
│   │   ├── HeaderPathValidator.validate_and_fix_paths()
│   │   └── ChunkSizeNormalizer.normalize_chunk_sizes()
│   ├── _validate_content_completeness()
│   └── _validate_size_compliance()
│   └── → ChunkingResult
├── _post_process_chunks()
│   ├── OverlapManager.apply_overlap()
│   ├── MetadataEnricher.enrich_chunks()
│   ├── DataCompletenessValidator.validate_chunks()
│   └── _process_preamble()
└── OutputTransformer.transform()
    └── → List[Chunk] | ChunkingResult | dict
```

---

## Промежуточные структуры данных

### 1. Stage1Results (parser → chunker)

```python
@dataclass
class Stage1Results:
    ast: MarkdownNode              # AST дерево документа
    fenced_blocks: List[FencedBlock]  # Извлечённые code blocks
    elements: ElementsInfo         # Заголовки, списки, таблицы
    analysis: ContentAnalysis      # Метрики контента
    parser_name: str               # Какой парсер использован
    processing_time: float         # Время обработки
```

### 2. ContentAnalysis (для выбора стратегии)

```python
@dataclass
class ContentAnalysis:
    total_chars: int
    total_lines: int
    code_ratio: float              # Доля кода
    text_ratio: float              # Доля текста
    list_ratio: float              # Доля списков
    table_ratio: float             # Доля таблиц
    code_block_count: int
    list_count: int
    table_count: int
    header_count: int
    max_header_depth: int
    complexity_score: float
    content_type: str              # "code", "text", "mixed"
    has_mixed_content: bool
    languages: Set[str]            # Языки программирования
    preamble: Optional[PreambleInfo]
```

### 3. Chunk (результат стратегии)

```python
@dataclass
class Chunk:
    content: str                   # Содержимое чанка
    start_line: int                # Начальная строка (1-based)
    end_line: int                  # Конечная строка
    metadata: Dict[str, Any]       # Метаданные (strategy, content_type, etc.)
```

### 4. ChunkingResult (финальный результат)

```python
@dataclass
class ChunkingResult:
    chunks: List[Chunk]
    strategy_used: str
    processing_time: float
    fallback_used: bool
    fallback_level: int
    errors: List[str]
    warnings: List[str]
    total_chars: int
    total_lines: int
    content_type: str
    complexity_score: float
```

---

## Точки дублирования и множественных трансформаций

### ⚠️ Проблема 1: Двойной парсинг Stage 1

В `_post_process_chunks()`:
```python
if chunks and self.config.extract_preamble:
    try:
        stage1_results = self.stage1.process_document(md_text)  # ПОВТОРНЫЙ ВЫЗОВ!
        if stage1_results.analysis.preamble:
            chunks = self._process_preamble(chunks, stage1_results.analysis.preamble)
```

**Проблема**: Stage 1 вызывается дважды — в orchestrator и в post_process_chunks.

### ⚠️ Проблема 2: Двойная обработка overlap

Есть два механизма overlap:
1. `BlockOverlapManager.apply_block_overlap()` — в orchestrator (block-based)
2. `OverlapManager.apply_overlap()` — в post_process_chunks (legacy)

```python
# В orchestrator:
if self.config.block_based_overlap:
    chunks = self._block_overlap_manager.apply_block_overlap(chunks, blocks_by_chunk)

# В core.py _post_process_chunks:
if self.config.enable_overlap and not getattr(self.config, "block_based_overlap", False):
    chunks = self._overlap_manager.apply_overlap(chunks, include_metadata)
```

**Проблема**: Два разных механизма overlap с условной логикой переключения.

### ⚠️ Проблема 3: Множественные валидации

```python
# В orchestrator:
self._validate_content_completeness(md_text, result.chunks)
validate_no_excessive_duplication(result.chunks)
validate_overlap_accuracy(result.chunks)
result.chunks = self._validate_size_compliance(result.chunks)

# В core.py _post_process_chunks:
validation_result = self._validator.validate_chunks(md_text, chunks)
```

**Проблема**: Валидация происходит в нескольких местах с разной логикой.

### ⚠️ Проблема 4: Трансформация метаданных

Метаданные добавляются в нескольких местах:
1. В стратегии (`_create_chunk()`)
2. В `MetadataEnricher.enrich_chunks()`
3. В `FallbackManager._create_fallback_result()`
4. В `_validate_size_compliance()` (oversize flags)

---

## Этапы пост-обработки

### 1. Block-based Post-processing (в orchestrator)

**Цель**: Исправление багов MC-001 через MC-006

| Этап | Компонент | Назначение |
|------|-----------|------------|
| 1 | BlockOverlapManager | Block-based overlap (MC-003) |
| 2 | HeaderPathValidator | Валидация путей заголовков (MC-006) |
| 3 | ChunkSizeNormalizer | Нормализация размеров (MC-004) |
| 4 | normalize_line_breaks | Нормализация переносов (Fix #7) |

### 2. Legacy Post-processing (в core.py)

| Этап | Компонент | Назначение |
|------|-----------|------------|
| 1 | OverlapManager | Legacy overlap (если block_based выключен) |
| 2 | MetadataEnricher | Обогащение метаданных |
| 3 | DataCompletenessValidator | Проверка полноты данных |
| 4 | _process_preamble | Обработка преамбулы |

### ⚠️ Проблема: Дублирование пост-обработки

Два набора пост-обработки с частично пересекающейся функциональностью:
- Block-based (новый) vs Legacy (старый)
- Условное переключение через флаги конфигурации

---

## Выводы

### Ключевые проблемы потока данных

1. **Двойной парсинг**: Stage 1 вызывается дважды для preamble
2. **Два механизма overlap**: block-based и legacy с условным переключением
3. **Распределённая валидация**: проверки в 4+ местах
4. **Распределённое обогащение метаданных**: в 4+ местах
5. **Сложная условная логика**: много `if config.flag` переключений

### Рекомендации (предварительные)

1. Кэшировать Stage1Results, не вызывать повторно
2. Выбрать один механизм overlap, удалить второй
3. Консолидировать валидацию в одном месте
4. Консолидировать обогащение метаданных
5. Упростить пост-обработку до линейного pipeline
