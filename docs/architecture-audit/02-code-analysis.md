# Архитектурный Аудит: Анализ Кода

## Структура модулей

### Текущая структура (55 файлов)

```
markdown_chunker/
├── __init__.py                    # 130 строк - динамический импорт провайдера
├── logging_config.py              # ~50 строк
├── api/                           # 5 файлов, ~900 строк
│   ├── __init__.py
│   ├── adapter.py
│   ├── error_handler.py
│   ├── types.py
│   └── validator.py
├── chunker/                       # 26 файлов, ~13,500 строк
│   ├── __init__.py
│   ├── core.py                    # 795 строк - главный класс
│   ├── orchestrator.py            # 665 строк - оркестрация
│   ├── types.py                   # 1079 строк - типы данных
│   ├── selector.py                # ~300 строк
│   ├── transformer.py             # ~200 строк
│   ├── validator.py               # ~300 строк
│   ├── block_packer.py            # 671 строк
│   ├── block_overlap_manager.py   # 263 строки
│   ├── chunk_size_normalizer.py   # ~200 строк
│   ├── dedup_validator.py         # ~150 строк
│   ├── header_path_validator.py   # ~150 строк
│   ├── logical_blocks.py          # ~200 строк
│   ├── performance.py             # ~200 строк
│   ├── regression_validator.py    # ~100 строк
│   ├── section_builder.py         # 607 строк
│   ├── size_enforcer.py           # ~150 строк
│   ├── text_normalizer.py         # ~100 строк
│   ├── url_detector.py            # ~100 строк
│   ├── errors.py                  # ~100 строк
│   ├── components/                # 5 файлов
│   │   ├── __init__.py
│   │   ├── fallback_manager.py    # ~400 строк
│   │   ├── metadata_enricher.py   # 712 строк
│   │   └── overlap_manager.py     # 926 строк (legacy)
│   └── strategies/                # 8 файлов
│       ├── __init__.py
│       ├── base.py                # ~350 строк
│       ├── code_strategy.py       # 624 строки
│       ├── list_strategy.py       # 856 строк (НЕ ИСПОЛЬЗУЕТСЯ)
│       ├── mixed_strategy.py      # 848 строк
│       ├── sentences_strategy.py  # 525 строк
│       ├── structural_strategy.py # 1720 строк (!)
│       └── table_strategy.py      # 465 строк
└── parser/                        # 15 файлов, ~8,500 строк
    ├── __init__.py                # 240 строк (!)
    ├── core.py                    # 653 строки
    ├── types.py                   # 931 строка
    ├── analyzer.py                # 500 строк
    ├── ast.py                     # ~300 строк
    ├── config.py                  # ~100 строк
    ├── elements.py                # ~300 строк
    ├── enhanced_ast_builder.py    # 653 строки
    ├── errors.py                  # 630 строк
    ├── fence_handler.py           # ~300 строк
    ├── markdown_ast.py            # 699 строк
    ├── nesting_resolver.py        # ~300 строк
    ├── preamble.py                # ~200 строк
    ├── utils.py                   # 523 строки
    └── validation.py              # 784 строки
```

## Анализ ключевых файлов

### 1. `chunker/core.py` — MarkdownChunker

**Проблемы:**
- Создаёт 10+ компонентов в `__init__`
- Двойной вызов Stage 1 (в orchestrator и в `_post_process_chunks`)
- Deprecated методы не удалены (`chunk_with_analysis`, `chunk_simple`)
- Сложная логика пост-обработки

```python
# Пример избыточности в __init__:
self._strategies: List[BaseStrategy] = [
    CodeStrategy(),
    MixedStrategy(),
    ListStrategy(),      # НЕ ИСПОЛЬЗУЕТСЯ в auto-mode!
    TableStrategy(),
    StructuralStrategy(),
    SentencesStrategy(),
]
```

### 2. `chunker/orchestrator.py` — ChunkingOrchestrator

**Проблемы:**
- Условная логика для block-based компонентов
- Множественные валидации
- Сложная пост-обработка

```python
# Пример условной логики:
if BLOCK_BASED_AVAILABLE:
    self._block_overlap_manager = BlockOverlapManager(config)
    self._header_path_validator = HeaderPathValidator()
    self._chunk_size_normalizer = ChunkSizeNormalizer(config)
else:
    self._block_overlap_manager = None
    # ...
```

### 3. `chunker/types.py` — ChunkConfig

**Проблемы:**
- 32 параметра конфигурации
- Расхождение документации и defaults
- Параметры для багфиксов

```python
# Группы параметров:
# Размеры: 5 параметров
# Overlap: 4 параметра
# Пороги стратегий: 8 параметров
# Поведение: 4 параметра
# Fallback: 3 параметра
# Preamble: 3 параметра
# Phase 2: 2 параметра
# MC-* fixes: 5 параметров
# Прочее: 3 параметра (streaming не реализован)
```

### 4. `chunker/strategies/structural_strategy.py` — 1720 строк

**Проблемы:**
- В 3x больше других стратегий
- Содержит Phase 2 логику
- Содержит block-based логику
- Дублирует код из других стратегий

### 5. `parser/__init__.py` — 240 строк импортов

**Проблемы:**
- 50+ экспортируемых символов
- Deprecated Simple API
- Backward compatibility aliases
- Try/except для импортов

```python
# Пример backward compatibility:
try:
    from .simple_api import (
        analyze, check_markdown_quality, ...
    )
except ImportError:
    def analyze(*args, **kwargs):
        raise NotImplementedError("simple_api has been removed")
```

## Дублирование кода

### Между стратегиями

| Функциональность | Code | Structural | Mixed | List | Sentences |
|-----------------|------|------------|-------|------|-----------|
| Header extraction | - | ✓ | ✓ | - | - |
| Code block handling | ✓ | ✓ | ✓ | - | - |
| Paragraph splitting | - | ✓ | ✓ | - | ✓ |
| Language detection | ✓ | - | ✓ | - | - |

### Между модулями

- `chunker/types.py` и `parser/types.py` — похожие структуры
- `OverlapManager` и `BlockOverlapManager` — два механизма overlap
- Валидация в `orchestrator.py`, `core.py`, `validator.py`, `dedup_validator.py`

## Неиспользуемый код

### ListStrategy (856 строк)

```python
# В StrategySelector._select_strict():
safe_strategies = [s for s in self.strategies if s.name != "list"]
logger.info("Auto mode: list strategy excluded for safety (mixed-content risk)")
```

### Streaming (не реализовано)

```python
# В ChunkConfig:
enable_streaming: bool = False
streaming_threshold: int = 10 * 1024 * 1024  # 10MB
# Нигде не используется!
```

### fallback_strategy (hardcoded)

```python
# В ChunkConfig:
fallback_strategy: str = "sentences"
# Но в FallbackManager:
self._structural_strategy = StructuralStrategy()  # hardcoded
self._sentences_strategy = SentencesStrategy()    # hardcoded
```

## Слои исправлений в коде

```python
# Примеры комментариев в коде:

# CRITICAL FIX (Phase 1.1): Ensures complete code block extraction
# CRITICAL FIX (Phase 1.2): Ensure all oversize chunks are flagged
# CRITICAL FIX (Phase 2.2): Enforce 50% total overlap limit
# FIX 3: Validate content completeness
# FIX: Sort chunks by document position (Requirements 2.1, 2.2)
# MC-001 through MC-006 fixes
```

## Выводы

1. **Код накопил технический долг** через итеративные исправления
2. **Дублирование** между стратегиями и модулями
3. **Неиспользуемый код** не удаляется
4. **Сложная инициализация** с множеством компонентов
5. **Условная логика** для разных режимов работы
