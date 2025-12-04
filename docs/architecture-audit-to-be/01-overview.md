# Целевая Архитектура: Обзор

## Цели редизайна

1. **Простота** — минимум компонентов для решения задачи
2. **Понятность** — линейный поток данных без условной логики
3. **Тестируемость** — property-based тесты вместо тестов реализации
4. **Производительность** — один проход парсинга, минимум аллокаций

## Ключевые метрики

| Метрика | Было | Цель | Изменение |
|---------|------|------|-----------|
| Файлов | 55 | 12 | -78% |
| Строк кода | ~24,000 | ~5,000 | -79% |
| Параметров конфигурации | 32 | 8-10 | -70% |
| Стратегий | 6 | 3 | -50% |
| Тестов | 1,853 | ~50-100 | -95% |
| Строк тестов | ~45,600 | ~2,000 | -96% |
| Публичных символов | 50+ | ~10 | -80% |

## Архитектурные принципы

### 1. Single Responsibility

Каждый модуль решает одну задачу:
- `parser.py` — парсинг markdown
- `chunker.py` — разбиение на чанки
- `strategies/*.py` — алгоритмы разбиения

### 2. No Duplication

- Один механизм overlap
- Одна точка валидации
- Одно место обогащения метаданных

### 3. Linear Pipeline

```
Input → Parse → Select Strategy → Apply → Post-process → Output
```

Без:
- Двойного парсинга
- Условных веток
- Параметров для багфиксов

### 4. Contract-First

Доменные свойства (PROP-1..PROP-10) определяют контракт.
Реализация должна удовлетворять контракту.
Тесты проверяют контракт, а не реализацию.

## Структура проекта

```
markdown_chunker/
├── __init__.py          # Публичный API (~50 строк)
├── types.py             # Типы данных (~300 строк)
├── config.py            # Конфигурация (~150 строк)
├── parser.py            # Парсинг (~500 строк)
├── chunker.py           # Главный класс (~400 строк)
├── validator.py         # Валидация (~150 строк)
├── strategies/
│   ├── __init__.py      # Экспорт (~20 строк)
│   ├── base.py          # Базовый класс (~200 строк)
│   ├── code_aware.py    # Для кода (~400 строк)
│   ├── structural.py    # Для структуры (~400 строк)
│   └── fallback.py      # Fallback (~200 строк)
└── utils.py             # Утилиты (~200 строк)

tests/
├── conftest.py          # Фикстуры и генераторы (~200 строк)
├── test_properties.py   # Property-based тесты (~500 строк)
├── test_edge_cases.py   # Edge cases (~200 строк)
└── test_integration.py  # Integration (~100 строк)
```

**Итого:** ~3,000 строк кода + ~1,000 строк тестов

## Диаграмма компонентов

```
┌─────────────────────────────────────────────────────────────┐
│                     markdown_chunker                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  MarkdownChunker                     │   │
│  │                    (chunker.py)                      │   │
│  │                                                      │   │
│  │  chunk(md_text, config) → ChunkingResult            │   │
│  └─────────────────────────────────────────────────────┘   │
│           │                                                 │
│           │ uses                                            │
│           ▼                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Parser    │  │  Selector   │  │  Validator  │        │
│  │ (parser.py) │  │ (chunker.py)│  │(validator.py)│        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│           │              │                                  │
│           │              ▼                                  │
│           │     ┌─────────────────────────────────┐        │
│           │     │          Strategies              │        │
│           │     ├─────────────────────────────────┤        │
│           │     │ CodeAwareStrategy (priority=1)  │        │
│           │     │ StructuralStrategy (priority=2) │        │
│           │     │ FallbackStrategy (priority=3)   │        │
│           │     └─────────────────────────────────┘        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    types.py                          │   │
│  │  Chunk, ChunkingResult, ChunkConfig, ContentAnalysis │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Поток данных

```
┌──────────┐
│ md_text  │
└────┬─────┘
     │
     ▼
┌──────────────────────────────────────┐
│ 1. Parse                              │
│    Parser.parse(md_text)              │
│    → ContentAnalysis                  │
└────┬─────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│ 2. Select Strategy                    │
│    Selector.select(analysis, config)  │
│    → Strategy                         │
└────┬─────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│ 3. Apply Strategy                     │
│    strategy.apply(md_text, analysis)  │
│    → List[Chunk]                      │
└────┬─────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│ 4. Post-process                       │
│    - Apply overlap                    │
│    - Enrich metadata                  │
│    - Validate                         │
│    → List[Chunk]                      │
└────┬─────────────────────────────────┘
     │
     ▼
┌──────────────────────────────────────┐
│ 5. Return                             │
│    ChunkingResult(chunks, strategy)   │
└──────────────────────────────────────┘
```

## Публичный API

```python
# markdown_chunker/__init__.py

from .chunker import MarkdownChunker
from .config import ChunkConfig
from .types import Chunk, ChunkingResult

def chunk_text(text: str, config: ChunkConfig = None) -> List[Chunk]:
    """Convenience function."""
    return MarkdownChunker(config).chunk(text).chunks

def chunk_file(path: str, config: ChunkConfig = None) -> List[Chunk]:
    """Convenience function."""
    with open(path) as f:
        return chunk_text(f.read(), config)

__all__ = [
    "MarkdownChunker",
    "ChunkConfig", 
    "Chunk",
    "ChunkingResult",
    "chunk_text",
    "chunk_file",
]
```

## Контракт (доменные свойства)

Любая реализация должна удовлетворять:

| # | Свойство | Критичность |
|---|----------|-------------|
| 1 | No Content Loss | CRITICAL |
| 2 | Size Bounds | CRITICAL |
| 3 | Monotonic Ordering | CRITICAL |
| 4 | No Empty Chunks | CRITICAL |
| 5 | Valid Line Numbers | CRITICAL |
| 6 | Code Block Integrity | HIGH |
| 7 | Table Integrity | HIGH |
| 8 | Serialization Round-Trip | HIGH |
| 9 | Idempotence | MEDIUM |
| 10 | Header Path Correctness | MEDIUM |
