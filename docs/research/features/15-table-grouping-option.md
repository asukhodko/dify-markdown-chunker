# Feature 15: Table Grouping Option

## Краткое описание

Опция группировки связанных таблиц в одном чанке для улучшения качества retrieval для table-heavy документов (API references, data reports).

---

## Метаданные

| Параметр | Значение |
|----------|----------|
| **Фаза** | 5 — Производительность и полировка |
| **Приоритет** | LOW |
| **Effort** | 2-3 дня |
| **Impact** | Low |
| **Уникальность** | No |

---

## Проблема

### Текущее состояние

Таблицы уже сохраняются как atomic units (не разрываются), но:
- Связанные таблицы могут оказаться в разных чанках
- Контекст между таблицами теряется
- API reference с несколькими таблицами разбивается

### Типичные примеры

#### API Reference

```markdown
## User Endpoints

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | yes | User ID |
| email | string | yes | Email address |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| user | object | User data |
| created_at | datetime | Creation time |

### Error Codes

| Code | Message |
|------|---------|
| 404 | User not found |
| 400 | Invalid input |
```

**Проблема:** Три связанные таблицы могут оказаться в трёх разных чанках.

---

## Решение

### Архитектура

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class TableGroupingConfig:
    """Конфигурация группировки таблиц."""
    enabled: bool = True
    max_distance_lines: int = 10      # Max lines between tables to group
    max_grouped_tables: int = 5       # Max tables in one group
    max_group_size: int = 5000        # Max chars for grouped tables
    require_same_section: bool = True # Only group within same header section

class TableGrouper:
    """
    Группировка связанных таблиц.
    """
    
    def __init__(self, config: TableGroupingConfig):
        self.config = config
    
    def group_tables(
        self,
        tables: list[TableBlock],
        text: str
    ) -> list[list[TableBlock]]:
        """
        Сгруппировать связанные таблицы.
        
        Returns:
            List of table groups
        """
        if not self.config.enabled or not tables:
            return [[t] for t in tables]
        
        groups = []
        current_group = [tables[0]]
        current_size = len(tables[0].content)
        
        for i in range(1, len(tables)):
            table = tables[i]
            prev_table = tables[i - 1]
            
            # Check if should group with previous
            if self._should_group(prev_table, table, text, current_size):
                current_group.append(table)
                current_size += len(table.content)
            else:
                # Start new group
                groups.append(current_group)
                current_group = [table]
                current_size = len(table.content)
        
        # Add last group
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _should_group(
        self,
        prev_table: TableBlock,
        table: TableBlock,
        text: str,
        current_group_size: int
    ) -> bool:
        """Проверить, нужно ли группировать с предыдущей таблицей."""
        
        # Check max tables
        if len(current_group_size) >= self.config.max_grouped_tables:
            return False
        
        # Check max size
        if current_group_size + len(table.content) > self.config.max_group_size:
            return False
        
        # Check distance
        distance = table.start_line - prev_table.end_line
        if distance > self.config.max_distance_lines:
            return False
        
        # Check same section
        if self.config.require_same_section:
            text_between = self._get_text_between(prev_table, table, text)
            if self._has_header(text_between):
                return False
        
        return True
    
    def _get_text_between(
        self,
        table1: TableBlock,
        table2: TableBlock,
        text: str
    ) -> str:
        """Получить текст между таблицами."""
        lines = text.split('\n')
        return '\n'.join(lines[table1.end_line:table2.start_line])
    
    def _has_header(self, text: str) -> bool:
        """Проверить, есть ли header в тексте."""
        for line in text.split('\n'):
            if line.strip().startswith('#'):
                return True
        return False
```

### Интеграция с ChunkConfig

```python
@dataclass
class ChunkConfig:
    # Existing fields...
    max_chunk_size: int = 2000
    preserve_tables: bool = True
    
    # Table grouping
    group_related_tables: bool = False
    table_grouping_config: Optional[TableGroupingConfig] = None
    
    def get_table_grouper(self) -> Optional[TableGrouper]:
        """Получить table grouper если enabled."""
        if not self.group_related_tables:
            return None
        config = self.table_grouping_config or TableGroupingConfig()
        return TableGrouper(config)
```

### Интеграция с Strategy

```python
class CodeAwareStrategy(BaseStrategy):
    def apply(
        self,
        text: str,
        analysis: ContentAnalysis,
        config: ChunkConfig
    ) -> list[Chunk]:
        # Group related tables if enabled
        table_grouper = config.get_table_grouper()
        
        if table_grouper and analysis.tables:
            table_groups = table_grouper.group_tables(
                analysis.tables, text
            )
            
            # Process groups as atomic units
            for group in table_groups:
                group_content = self._combine_table_group(group, text)
                # Create chunk for group...
        else:
            # Process tables individually
            pass
```

---

## Usage Examples

### Basic Usage

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

# Enable table grouping
config = ChunkConfig(
    group_related_tables=True
)

chunker = MarkdownChunker(config)
result = chunker.chunk(api_docs)

# Related tables will be in same chunk
```

### Custom Configuration

```python
from markdown_chunker import ChunkConfig, TableGroupingConfig

config = ChunkConfig(
    group_related_tables=True,
    table_grouping_config=TableGroupingConfig(
        max_distance_lines=15,       # Allow more space between tables
        max_grouped_tables=3,        # Max 3 tables per group
        max_group_size=8000,         # Larger groups OK
        require_same_section=True    # Must be in same section
    )
)

chunker = MarkdownChunker(config)
```

### For API Documentation

```python
# Optimized for API docs with many related tables
config = ChunkConfig.for_api_docs()
config.group_related_tables = True
config.table_grouping_config = TableGroupingConfig(
    max_distance_lines=20,
    max_grouped_tables=5,
)
```

---

## Примеры

### Before Grouping

```
Chunk 1: "## Parameters" + Parameters table
Chunk 2: "### Response Fields" + Response table  
Chunk 3: "### Error Codes" + Error codes table
```

### After Grouping

```
Chunk 1: "## Parameters" + Parameters table + Response table + Error codes table
```

Или (если слишком большой):

```
Chunk 1: "## Parameters" + Parameters table + Response table
Chunk 2: "### Error Codes" + Error codes table
```

---

## Тестирование

### Unit Tests

```python
def test_tables_grouped_when_close():
    """Близкие таблицы группируются"""
    text = """
| A | B |
|---|---|
| 1 | 2 |

Some text.

| C | D |
|---|---|
| 3 | 4 |
"""
    config = ChunkConfig(group_related_tables=True)
    result = MarkdownChunker(config).chunk(text)
    
    # Both tables should be in same chunk
    assert len(result.chunks) == 1

def test_tables_not_grouped_when_far():
    """Далёкие таблицы не группируются"""
    
def test_tables_not_grouped_across_headers():
    """Таблицы в разных секциях не группируются"""
    
def test_max_group_size_respected():
    """max_group_size соблюдается"""
    
def test_grouping_disabled_by_default():
    """Группировка выключена по умолчанию"""
```

---

## Ожидаемые улучшения

### Quality Impact

| Document Type | Before | After |
|---------------|--------|-------|
| API reference | 75% retrieval quality | 85% |
| Data reports | 70% | 82% |
| Comparison docs | 72% | 80% |

### Retrieval Scenarios

| Query | Before | After |
|-------|--------|-------|
| "What are the user endpoint parameters?" | Returns only Parameters table | Returns all related tables |
| "Show error codes for user API" | May miss context | Full context with related tables |

---

## Конфигурация

| Parameter | Default | Description |
|-----------|---------|-------------|
| enabled | true | Enable table grouping |
| max_distance_lines | 10 | Max lines between tables to group |
| max_grouped_tables | 5 | Max tables in one group |
| max_group_size | 5000 | Max chars for grouped content |
| require_same_section | true | Only group within same header section |

---

## Зависимости

### Изменяет

- `ChunkConfig` — новые поля
- `CodeAwareStrategy` — table group handling
- Chunk metadata — table_group info

---

## Риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Chunks too large | Medium | Low | max_group_size limit |
| Wrong grouping | Low | Low | require_same_section |
| Breaking existing behavior | Low | Low | Disabled by default |

---

## Acceptance Criteria

- [ ] TableGrouper class создан
- [ ] group_related_tables config option работает
- [ ] Близкие таблицы группируются
- [ ] Таблицы в разных секциях не группируются
- [ ] max_group_size соблюдается
- [ ] max_grouped_tables соблюдается
- [ ] По умолчанию выключено (backward compatible)
- [ ] Metadata содержит table group info
- [ ] Документация с примерами

---

## Примеры из тестового корпуса

### Файлы с множеством таблиц (10+ tables)

| Файл | Кол-во таблиц | Размер |
|------|---------------|--------|
| [webpack.md](../../../tests/corpus/github_readmes/javascript/webpack.md) | 13 | 80KB |
| [axios.md](../../../tests/corpus/github_readmes/javascript/axios.md) | 12 | 72KB |
| [spaCy.md](../../../tests/corpus/github_readmes/python/spaCy.md) | 12 | ~50KB |
| [gin.md](../../../tests/corpus/github_readmes/go/gin.md) | 11 | ~45KB |
| [scikit-learn.md](../../../tests/corpus/github_readmes/python/scikit-learn.md) | 10 | ~40KB |

### Файлы со средним кол-вом таблиц (5-9 tables)

| Файл | Кол-во таблиц |
|------|---------------|
| [tensorflow.md](../../../tests/corpus/github_readmes/python/tensorflow.md) | 8 |
| [kubernetes.md](../../../tests/corpus/technical_docs/kubernetes/kubernetes.md) | 7 |
| [cobra.md](../../../tests/corpus/github_readmes/go/cobra.md) | 6 |
| [express.md](../../../tests/corpus/github_readmes/javascript/express.md) | 5 |
| [flask.md](../../../tests/corpus/github_readmes/python/flask.md) | 5 |

### Рекомендации по тестированию

- **webpack.md, axios.md** — JavaScript docs с API tables
- **spaCy.md, scikit-learn.md** — ML libraries с parameter tables
- **gin.md** — Go web framework с routing tables
