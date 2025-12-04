# План Редизайна: Фаза 4 и 5 — Интеграция и Очистка

## Фаза 4: Интеграция (3-4 дня)

### Цель

Собрать все компоненты вместе, удалить дублирование обработки.

### 4.1 Переработать MarkdownChunker (2 дня)

**Текущие проблемы:**
- Двойной парсинг (в orchestrator и в _post_process_chunks)
- Двойной overlap (block-based и legacy)
- Множественные валидации (4+ мест)
- Сложная пост-обработка

**Целевая структура:**

```python
# markdown_chunker/chunker.py

class MarkdownChunker:
    """
    Главный класс для чанкинга markdown.
    
    Упрощённый pipeline:
    1. Parse → ContentAnalysis
    2. Select strategy
    3. Apply strategy → chunks
    4. Apply overlap (если включён)
    5. Validate
    """
    
    def __init__(self, config: ChunkConfig = None):
        self.config = config or ChunkConfig()
        self.parser = Parser()
        self.selector = StrategySelector()
    
    def chunk(
        self, 
        md_text: str, 
        strategy: str = None,
        include_analysis: bool = False
    ) -> Union[List[Chunk], ChunkingResult]:
        """Разбить документ на чанки."""
        
        # 1. Парсинг (ОДИН РАЗ)
        analysis = self.parser.analyze(md_text)
        
        # 2. Выбор стратегии
        if strategy:
            selected = self.selector.get_by_name(strategy)
        else:
            selected = self.selector.select(analysis, self.config)
        
        # 3. Применение стратегии
        chunks = selected.apply(md_text, analysis, self.config)
        
        # 4. Overlap (если включён)
        if self.config.overlap_size > 0:
            chunks = self._apply_overlap(chunks)
        
        # 5. Валидация
        self._validate(chunks, md_text)
        
        # 6. Результат
        if include_analysis:
            return ChunkingResult(
                chunks=chunks,
                strategy_used=selected.name,
                processing_time=0.0,  # TODO: измерить
                total_chars=analysis.total_chars,
                total_lines=analysis.total_lines,
            )
        return chunks
    
    def _apply_overlap(self, chunks: List[Chunk]) -> List[Chunk]:
        """Применить overlap между чанками."""
        if len(chunks) <= 1:
            return chunks
        
        for i in range(1, len(chunks)):
            prev_content = chunks[i - 1].content
            overlap_text = prev_content[-self.config.overlap_size:]
            
            # Найти границу слова
            space_pos = overlap_text.find(' ')
            if space_pos > 0:
                overlap_text = overlap_text[space_pos + 1:]
            
            chunks[i].metadata['overlap_text'] = overlap_text
            chunks[i].metadata['overlap_size'] = len(overlap_text)
        
        return chunks
    
    def _validate(self, chunks: List[Chunk], original: str) -> None:
        """Валидация результата."""
        # PROP-1: No content loss
        total_content = sum(len(c.content) for c in chunks)
        if total_content < len(original) * 0.95:
            raise ValueError("Content loss detected")
        
        # PROP-2: Size bounds
        for chunk in chunks:
            if chunk.size > self.config.max_chunk_size:
                if not chunk.metadata.get('allow_oversize'):
                    raise ValueError(f"Chunk exceeds max size: {chunk.size}")
        
        # PROP-3: Monotonic ordering
        for i in range(len(chunks) - 1):
            if chunks[i].start_line > chunks[i + 1].start_line:
                raise ValueError("Chunks not in order")
```

### 4.2 Удалить дублирование (1-2 дня)

**Удалить:**
- `orchestrator.py` — логика перенесена в `chunker.py`
- `components/overlap_manager.py` — упрощённый overlap в `chunker.py`
- `components/metadata_enricher.py` — метаданные добавляются в стратегиях
- `block_overlap_manager.py` — один механизм overlap
- `validator.py`, `dedup_validator.py` — одна валидация

**Оставить:**
- `chunker.py` — главный класс
- `parser.py` — парсер
- `config.py` — конфигурация
- `types.py` — типы данных
- `strategies/` — стратегии

---

## Фаза 5: Очистка (2-3 дня)

### Цель

Удалить весь legacy-код, обновить документацию.

### 5.1 Удалить deprecated код (1 день)

**Файлы для удаления:**

```
# Parser
parser/simple_api.py          # Deprecated Simple API
parser/nesting_resolver.py    # Backward compatibility
parser/fence_handler.py       # Устаревший
parser/enhanced_ast_builder.py # Не используется
parser/markdown_ast.py        # Заменён на parser.py

# Chunker
chunker/orchestrator.py       # Заменён на chunker.py
chunker/selector.py           # Заменён на StrategySelector
chunker/transformer.py        # Не нужен
chunker/performance.py        # Не нужен
chunker/text_normalizer.py    # Встроен в стратегии
chunker/size_enforcer.py      # Встроен в стратегии
chunker/block_packer.py       # Удалён
chunker/section_builder.py    # Удалён

# Components
chunker/components/overlap_manager.py
chunker/components/metadata_enricher.py
chunker/components/fallback_manager.py
chunker/block_overlap_manager.py
chunker/chunk_size_normalizer.py
chunker/header_path_validator.py
chunker/dedup_validator.py
chunker/regression_validator.py

# Strategies
chunker/strategies/code_strategy.py    # → CodeAwareStrategy
chunker/strategies/mixed_strategy.py   # → CodeAwareStrategy
chunker/strategies/table_strategy.py   # → CodeAwareStrategy
chunker/strategies/list_strategy.py    # Удалена
chunker/strategies/sentences_strategy.py # → FallbackStrategy
```

### 5.2 Удалить backward compatibility (0.5 дня)

**В `parser/__init__.py`:**
```python
# УДАЛИТЬ:
# - Алиасы (ParserInterface = Stage1Interface)
# - Try/except imports
# - Fallback-определения классов
# - Deprecated функции
```

**В `chunker/__init__.py`:**
```python
# УДАЛИТЬ:
# - Закомментированные экспорты
# - Deprecated методы (chunk_with_analysis, chunk_simple)
```

### 5.3 Удалить старые тесты (1 день)

**Удалить:**
```
tests/chunker/test_*_strategy_properties.py  # 6 файлов → 1
tests/chunker/test_overlap_*.py              # 2 файла → 0
tests/chunker/test_phase2_*.py               # Phase 2 тесты
tests/integration/test_overlap_*.py          # 2 файла → 0
tests/regression/                            # Все
```

**Оставить:**
```
tests_v2/                                    # Новые тесты
```

### 5.4 Обновить документацию (0.5 дня)

**Обновить:**
- `README.md` — новый API
- `docs/quickstart.md` — примеры
- `docs/usage.md` — полное руководство

**Удалить:**
- `docs/architecture/` — устаревшая архитектура
- `docs/architecture-preaudit/` — после завершения

---

## Критерии завершения фазы 4

- [ ] `MarkdownChunker` переработан
- [ ] Один механизм overlap
- [ ] Одна точка валидации
- [ ] Все property-based тесты проходят

## Критерии завершения фазы 5

- [ ] Все deprecated файлы удалены
- [ ] Backward compatibility удалён
- [ ] Старые тесты удалены
- [ ] Документация обновлена
- [ ] CI проходит

## Финальная структура

```
markdown_chunker/
├── __init__.py          # Публичный API
├── types.py             # Chunk, ChunkingResult, ContentAnalysis
├── config.py            # ChunkConfig
├── chunker.py           # MarkdownChunker
├── parser.py            # Parser
└── strategies/
    ├── __init__.py      # StrategySelector
    ├── base.py          # BaseStrategy
    ├── code_aware.py    # CodeAwareStrategy
    ├── structural.py    # StructuralStrategy
    └── fallback.py      # FallbackStrategy

tests/
├── conftest.py
├── test_properties.py   # 8 property-based тестов
├── test_integration.py  # 1 интеграционный тест
├── test_edge_cases.py   # ~10 edge cases
└── fixtures/
```

**Итого: 10 файлов кода, ~5000 строк**
