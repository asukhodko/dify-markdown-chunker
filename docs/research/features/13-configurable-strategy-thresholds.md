# Feature 13: Configurable Strategy Thresholds

## Краткое описание

Настраиваемые пороги для выбора стратегий chunking — возможность fine-tuning для специфических типов документов.

---

## Метаданные

| Параметр | Значение |
|----------|----------|
| **Фаза** | 4 — Продвинутые возможности |
| **Приоритет** | LOW |
| **Effort** | 2-3 дня |
| **Impact** | Medium |
| **Уникальность** | No |

---

## Проблема

### Текущее состояние

Пороги для выбора стратегий hardcoded:

```python
# В strategy selector
if analysis.code_ratio >= 0.30:  # Hardcoded
    return CodeAwareStrategy()
elif analysis.header_count >= 3:  # Hardcoded
    return StructuralStrategy()
else:
    return FallbackStrategy()
```

### Ограничения

1. **Нет гибкости:**
   - Для code-heavy проектов 30% может быть слишком высоким
   - Для text-heavy проектов 30% может быть слишком низким

2. **Разные use cases:**
   - API documentation: больше code tolerance
   - User guides: меньше code tolerance
   - Changelogs: нужен list threshold

3. **При добавлении List Strategy:**
   - Нужен list_ratio threshold
   - Нужен list_count threshold

---

## Решение

### Расширение ChunkConfig

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class StrategyThresholds:
    """Пороги для выбора стратегий."""
    
    # CodeAware thresholds
    code_ratio_threshold: float = 0.30
    code_block_min_count: int = 1
    
    # List thresholds (для Smart List Strategy)
    list_ratio_threshold: float = 0.40
    list_count_threshold: int = 5
    
    # Structural thresholds
    header_count_threshold: int = 3
    header_depth_threshold: int = 2
    
    # Table thresholds
    table_count_threshold: int = 3
    table_ratio_threshold: float = 0.40
    
    def validate(self) -> list[str]:
        """Валидация порогов."""
        errors = []
        
        if not 0 <= self.code_ratio_threshold <= 1:
            errors.append("code_ratio_threshold must be 0-1")
        if not 0 <= self.list_ratio_threshold <= 1:
            errors.append("list_ratio_threshold must be 0-1")
        if self.header_count_threshold < 1:
            errors.append("header_count_threshold must be >= 1")
        
        return errors

@dataclass
class ChunkConfig:
    # Size configuration
    max_chunk_size: int = 2000
    min_chunk_size: int = 200
    overlap_size: int = 100
    
    # Strategy thresholds
    thresholds: StrategyThresholds = field(
        default_factory=StrategyThresholds
    )
    
    # Existing fields...
    preserve_code_blocks: bool = True
    preserve_tables: bool = True
    strategy_override: Optional[str] = None
```

### Strategy Selector с Thresholds

```python
class StrategySelector:
    """
    Выбор стратегии на основе конфигурируемых порогов.
    """
    
    def __init__(self, config: ChunkConfig):
        self.config = config
        self.thresholds = config.thresholds
    
    def select(self, analysis: ContentAnalysis) -> BaseStrategy:
        """Выбрать оптимальную стратегию."""
        
        # 1. Check CodeAware conditions
        if self._should_use_code_aware(analysis):
            return CodeAwareStrategy(self.config)
        
        # 2. Check List conditions (when implemented)
        if self._should_use_list(analysis):
            return ListAwareStrategy(self.config)
        
        # 3. Check Structural conditions
        if self._should_use_structural(analysis):
            return StructuralStrategy(self.config)
        
        # 4. Fallback
        return FallbackStrategy(self.config)
    
    def _should_use_code_aware(self, analysis: ContentAnalysis) -> bool:
        """Проверить условия для CodeAware."""
        return (
            analysis.code_ratio >= self.thresholds.code_ratio_threshold or
            analysis.code_block_count >= self.thresholds.code_block_min_count
        )
    
    def _should_use_list(self, analysis: ContentAnalysis) -> bool:
        """Проверить условия для List strategy."""
        return (
            analysis.list_ratio >= self.thresholds.list_ratio_threshold or
            analysis.list_count >= self.thresholds.list_count_threshold
        )
    
    def _should_use_structural(self, analysis: ContentAnalysis) -> bool:
        """Проверить условия для Structural."""
        return (
            analysis.header_count >= self.thresholds.header_count_threshold and
            analysis.header_depth >= self.thresholds.header_depth_threshold
        )
```

### Preset Profiles

```python
@dataclass
class ChunkConfig:
    # ... existing fields ...
    
    @classmethod
    def for_api_docs(cls) -> "ChunkConfig":
        """Оптимизировано для API документации."""
        return cls(
            max_chunk_size=2500,
            thresholds=StrategyThresholds(
                code_ratio_threshold=0.20,  # Lower threshold
                code_block_min_count=1,
                table_count_threshold=2,    # API docs have many tables
            )
        )
    
    @classmethod
    def for_user_guides(cls) -> "ChunkConfig":
        """Оптимизировано для user guides."""
        return cls(
            max_chunk_size=1500,
            thresholds=StrategyThresholds(
                code_ratio_threshold=0.40,  # Higher threshold
                header_count_threshold=2,   # Lower header requirement
                list_ratio_threshold=0.30,  # Lists important in guides
            )
        )
    
    @classmethod
    def for_changelogs(cls) -> "ChunkConfig":
        """Оптимизировано для changelogs."""
        return cls(
            max_chunk_size=2000,
            thresholds=StrategyThresholds(
                list_ratio_threshold=0.25,  # Much lower
                list_count_threshold=3,     # Fewer lists trigger
            )
        )
    
    @classmethod
    def for_mixed_content(cls) -> "ChunkConfig":
        """Для смешанного контента."""
        return cls(
            thresholds=StrategyThresholds(
                code_ratio_threshold=0.35,
                list_ratio_threshold=0.35,
                header_count_threshold=4,
            )
        )
```

---

## Usage Examples

### Custom Thresholds

```python
from markdown_chunker import ChunkConfig, StrategyThresholds

# Custom thresholds for code-light documentation
config = ChunkConfig(
    thresholds=StrategyThresholds(
        code_ratio_threshold=0.50,  # Only heavy code triggers CodeAware
        header_count_threshold=2,   # Fewer headers for Structural
    )
)

chunker = MarkdownChunker(config)
result = chunker.chunk(text)
```

### Using Presets

```python
# For API documentation
config = ChunkConfig.for_api_docs()
chunker = MarkdownChunker(config)

# For changelogs
config = ChunkConfig.for_changelogs()
chunker = MarkdownChunker(config)
```

### YAML Configuration

```yaml
# config.yaml
chunk_config:
  max_chunk_size: 2000
  thresholds:
    code_ratio_threshold: 0.25
    list_ratio_threshold: 0.35
    header_count_threshold: 3
```

```python
import yaml

with open("config.yaml") as f:
    data = yaml.safe_load(f)

thresholds = StrategyThresholds(**data["chunk_config"]["thresholds"])
config = ChunkConfig(
    max_chunk_size=data["chunk_config"]["max_chunk_size"],
    thresholds=thresholds
)
```

---

## Тестирование

### Unit Tests

```python
def test_custom_code_threshold():
    """Custom code threshold работает"""
    config = ChunkConfig(
        thresholds=StrategyThresholds(code_ratio_threshold=0.50)
    )
    chunker = MarkdownChunker(config)
    
    # 40% code - should NOT trigger CodeAware with 50% threshold
    text = "```python\ncode\n```\n\nText text text text"
    result = chunker.chunk(text)
    assert result.strategy_used != "CodeAware"

def test_custom_list_threshold():
    """Custom list threshold работает"""
    
def test_preset_for_api_docs():
    """Preset for_api_docs имеет правильные thresholds"""
    config = ChunkConfig.for_api_docs()
    assert config.thresholds.code_ratio_threshold == 0.20
    
def test_threshold_validation():
    """Invalid thresholds вызывают ошибки"""
    thresholds = StrategyThresholds(code_ratio_threshold=1.5)
    errors = thresholds.validate()
    assert len(errors) > 0
```

---

## Ожидаемые улучшения

### Flexibility

| Scenario | До | После |
|----------|-----|-------|
| API docs с 20% code | Structural | CodeAware (configurable) |
| Guide с 35% code | CodeAware | Structural (configurable) |
| Changelog с 3 lists | Fallback | List (configurable) |

---

## Конфигурация

### Все доступные thresholds

| Threshold | Default | Range | Description |
|-----------|---------|-------|-------------|
| code_ratio_threshold | 0.30 | 0.0-1.0 | Min code ratio for CodeAware |
| code_block_min_count | 1 | 0+ | Min code blocks for CodeAware |
| list_ratio_threshold | 0.40 | 0.0-1.0 | Min list ratio for List strategy |
| list_count_threshold | 5 | 0+ | Min list count for List strategy |
| header_count_threshold | 3 | 1+ | Min headers for Structural |
| header_depth_threshold | 2 | 1+ | Min header depth for Structural |
| table_count_threshold | 3 | 0+ | Min tables for Table handling |
| table_ratio_threshold | 0.40 | 0.0-1.0 | Min table ratio |

---

## Риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| User confusion | Medium | Low | Good documentation, presets |
| Breaking changes | Low | Low | Defaults match current behavior |

---

## Acceptance Criteria

- [ ] StrategyThresholds dataclass создана
- [ ] ChunkConfig использует thresholds
- [ ] Strategy selector использует configurable thresholds
- [ ] Preset profiles созданы (api_docs, user_guides, changelogs)
- [ ] Validation для thresholds
- [ ] YAML configuration поддерживается
- [ ] Документация с примерами
- [ ] Backward compatibility (defaults = current behavior)

---

## Примеры из тестового корпуса

Следующие файлы демонстрируют разные пороги и подходят для тестирования Configurable Thresholds:

### Файлы на границе code_ratio threshold (30%)

| Файл | Code Ratio | Strategy при 30% | Strategy при 40% |
|------|------------|---------------|---------------|
| [go_007.md](../../../tests/corpus/github_readmes/go/go_007.md) | 31% | CodeAware | Structural |
| [journals_003.md](../../../tests/corpus/personal_notes/journals/journals_003.md) | 30% | CodeAware | Structural |
| [click.md](../../../tests/corpus/github_readmes/python/click.md) | 27% | Structural | Structural |
| [research_notes_007.md](../../../tests/corpus/research_notes/research_notes_007.md) | 23% | Structural | Structural |

### Файлы для тестирования list threshold

| Файл | Lists | Strategy при list>=5 | Strategy при list>=10 |
|------|-------|------------------|-------------------|
| [changelogs_043.md](../../../tests/corpus/changelogs/changelogs_043.md) | 34 | List | List |
| [node.md](../../../tests/corpus/github_readmes/javascript/node.md) | 660 | List | List |
| [cheatsheets_003.md](../../../tests/corpus/personal_notes/cheatsheets/cheatsheets_003.md) | 9 | List | Structural |
| [mixed_content_004.md](../../../tests/corpus/mixed_content/mixed_content_004.md) | 4 | Structural | Structural |

### Файлы для тестирования header threshold

| Файл | Headers | Strategy при header>=3 | Strategy при header>=5 |
|------|---------|---------------------|---------------------|
| [unstructured_004.md](../../../tests/corpus/personal_notes/unstructured/unstructured_004.md) | 1 | Fallback | Fallback |
| [unstructured_001.md](../../../tests/corpus/personal_notes/unstructured/unstructured_001.md) | 3 | Structural | Fallback |
| [cheatsheets_003.md](../../../tests/corpus/personal_notes/cheatsheets/cheatsheets_003.md) | 11 | Structural | Structural |
