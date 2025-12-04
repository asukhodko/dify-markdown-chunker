# Целевая Архитектура: Конфигурация

## Обзор

Конфигурация в одном файле `config.py` (~150 строк).
Вместо 32 параметров — 8-10 основных.

## ChunkConfig

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ChunkConfig:
    """
    Конфигурация чанкинга.
    
    Минимальный набор параметров для управления поведением.
    Все параметры имеют разумные defaults.
    """
    
    # === Размеры ===
    max_chunk_size: int = 4096
    """Максимальный размер чанка в символах."""
    
    min_chunk_size: int = 512
    """Минимальный размер чанка. Меньшие чанки объединяются."""
    
    overlap_size: int = 200
    """Размер перекрытия между чанками. 0 = без перекрытия."""
    
    # === Поведение ===
    preserve_atomic_blocks: bool = True
    """
    Сохранять атомарные блоки (code, tables) целиком.
    Если True, блоки не разбиваются даже если превышают max_chunk_size.
    """
    
    extract_preamble: bool = True
    """Извлекать преамбулу (YAML front matter, первый параграф)."""
    
    # === Пороги выбора стратегии ===
    code_threshold: float = 0.3
    """Порог code_ratio для выбора CodeAwareStrategy."""
    
    structure_threshold: int = 3
    """Минимум заголовков для выбора StructuralStrategy."""
    
    # === Tolerance (MC-001 fix) ===
    oversize_tolerance: float = 0.2
    """
    Допустимое превышение max_chunk_size для сохранения целостности секций.
    0.2 = 20% — секция размером до 4915 символов (при max=4096) 
    будет сохранена целиком вместо разбиения.
    """
    
    # === Опционально ===
    strategy_override: Optional[str] = None
    """Принудительный выбор стратегии (code, structural, fallback)."""
    
    def __post_init__(self):
        """Валидация параметров."""
        if self.max_chunk_size <= 0:
            raise ValueError("max_chunk_size must be positive")
        if self.min_chunk_size <= 0:
            raise ValueError("min_chunk_size must be positive")
        if self.min_chunk_size > self.max_chunk_size:
            raise ValueError("min_chunk_size must be <= max_chunk_size")
        if self.overlap_size < 0:
            raise ValueError("overlap_size must be non-negative")
        if self.overlap_size >= self.max_chunk_size:
            raise ValueError("overlap_size must be < max_chunk_size")
        if not 0.0 <= self.code_threshold <= 1.0:
            raise ValueError("code_threshold must be between 0.0 and 1.0")
        if self.structure_threshold < 0:
            raise ValueError("structure_threshold must be non-negative")
    
    # === Фабричные методы ===
    
    @classmethod
    def default(cls) -> "ChunkConfig":
        """Конфигурация по умолчанию."""
        return cls()
    
    @classmethod
    def for_code(cls) -> "ChunkConfig":
        """Для документов с кодом."""
        return cls(
            max_chunk_size=6144,
            overlap_size=300,
            code_threshold=0.2,
        )
    
    @classmethod
    def for_rag(cls) -> "ChunkConfig":
        """Для RAG систем (меньшие чанки)."""
        return cls(
            max_chunk_size=2048,
            min_chunk_size=256,
            overlap_size=100,
        )
    
    @classmethod
    def for_search(cls) -> "ChunkConfig":
        """Для поискового индекса (маленькие чанки)."""
        return cls(
            max_chunk_size=1024,
            min_chunk_size=128,
            overlap_size=50,
        )
    
    @classmethod
    def compact(cls) -> "ChunkConfig":
        """Компактные чанки без перекрытия."""
        return cls(
            max_chunk_size=2048,
            min_chunk_size=256,
            overlap_size=0,
        )
```

## Сравнение с текущей конфигурацией

### Удалённые параметры

| Параметр | Причина удаления |
|----------|------------------|
| `target_chunk_size` | Избыточен, используем max/min |
| `overlap_percentage` | Избыточен, используем overlap_size |
| `enable_overlap` | Заменён на overlap_size=0 |
| `min_code_blocks` | Упрощено до code_threshold |
| `min_complexity` | Не нужен |
| `list_count_threshold` | ListStrategy удалена |
| `list_ratio_threshold` | ListStrategy удалена |
| `table_count_threshold` | Таблицы в CodeAwareStrategy |
| `table_ratio_threshold` | Таблицы в CodeAwareStrategy |
| `header_count_threshold` | Переименован в structure_threshold |
| `allow_oversize` | Заменён на preserve_atomic_blocks |
| `preserve_code_blocks` | Объединён в preserve_atomic_blocks |
| `preserve_tables` | Объединён в preserve_atomic_blocks |
| `preserve_list_hierarchy` | Не нужен |
| `enable_fallback` | Всегда включён |
| `fallback_strategy` | Всегда sentences |
| `max_fallback_level` | Не нужен |
| `enable_streaming` | Не реализовано |
| `streaming_threshold` | Не реализовано |
| `separate_preamble_chunk` | Упрощено |
| `preamble_min_size` | Не нужен |
| `section_boundary_level` | Не нужен |
| `min_content_per_chunk` | Не нужен |
| `preserve_markdown_structure` | Всегда True |
| `block_based_splitting` | Всегда True |
| `allow_oversize_for_integrity` | Объединён в preserve_atomic_blocks |
| `min_effective_chunk_size` | Не нужен |
| `block_based_overlap` | Всегда True |
| `detect_url_pools` | Не нужен |
| `enable_content_validation` | Всегда True |

### Итого

| Аспект | Было | Стало |
|--------|------|-------|
| Параметров | 32 | 8 |
| Фабричных методов | 10+ | 4 |
| Строк кода | ~500 | ~150 |

## Использование

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

# Defaults
chunker = MarkdownChunker()

# Custom config
config = ChunkConfig(max_chunk_size=2048, overlap_size=100)
chunker = MarkdownChunker(config)

# Factory methods
chunker = MarkdownChunker(ChunkConfig.for_code())
chunker = MarkdownChunker(ChunkConfig.for_rag())

# Force strategy
config = ChunkConfig(strategy_override="structural")
chunker = MarkdownChunker(config)
```

## Принципы

1. **Минимализм** — только необходимые параметры
2. **Разумные defaults** — работает из коробки
3. **Валидация** — ошибки при неверных значениях
4. **Фабрики** — готовые профили для типичных сценариев
5. **Без флагов для багфиксов** — правильное поведение по умолчанию
