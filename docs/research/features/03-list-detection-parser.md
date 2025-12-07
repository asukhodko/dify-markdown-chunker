# Feature 03: List Detection в Parser

## Краткое описание

Добавление извлечения информации о списках в парсер markdown. Необходимо для работы Smart List Strategy.

---

## Метаданные

| Параметр | Значение |
|----------|----------|
| **Фаза** | 1 — Восстановление ядра |
| **Приоритет** | HIGH |
| **Effort** | 2-3 дня |
| **Impact** | High (enables List Strategy) |
| **Уникальность** | No |

---

## Проблема

### Текущее состояние

Парсер `markdown_chunker_v2/parser.py` извлекает:
- Headers (заголовки)
- Fenced code blocks
- Tables
- Paragraphs

**Не извлекает:**
- List blocks
- List hierarchy (вложенность)
- List types (bullet, numbered, checkbox)
- List item counts

### Почему это критично

Без информации о списках невозможно:
1. Определить list-heavy документы
2. Выбрать List Strategy
3. Правильно группировать list items
4. Сохранять иерархию вложенных списков

---

## Решение

### Структуры данных

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class ListType(Enum):
    BULLET = "bullet"        # - item или * item
    NUMBERED = "numbered"    # 1. item, 2. item
    CHECKBOX = "checkbox"    # - [ ] item или - [x] item

@dataclass
class ListItem:
    content: str              # Текст пункта (без маркера)
    marker: str               # Маркер (-, *, 1., - [ ], etc.)
    depth: int                # Уровень вложенности (0 = top-level)
    line_number: int          # Номер строки
    list_type: ListType       # Тип списка
    is_checked: Optional[bool]  # Для checkbox: True/False/None

@dataclass
class ListBlock:
    items: list[ListItem]     # Пункты списка
    start_line: int           # Начальная строка
    end_line: int             # Конечная строка
    list_type: ListType       # Преобладающий тип
    max_depth: int            # Максимальная вложенность
    
    @property
    def item_count(self) -> int:
        return len(self.items)
    
    @property
    def has_nested(self) -> bool:
        return self.max_depth > 0
    
    @property
    def content(self) -> str:
        """Восстановленный markdown списка"""
        # Реконструкция с сохранением formatting
        pass
```

### Алгоритм парсинга списков

```python
class ListParser:
    # Regex patterns
    BULLET_PATTERN = r'^(\s*)([-*+])\s+(.+)$'
    NUMBERED_PATTERN = r'^(\s*)(\d+\.)\s+(.+)$'
    CHECKBOX_PATTERN = r'^(\s*)([-*+])\s+\[([ xX])\]\s+(.+)$'
    
    def parse_lists(self, text: str) -> list[ListBlock]:
        """Извлечение всех list blocks из текста."""
        blocks = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            # Проверка, начинается ли list
            item = self._try_parse_item(lines[i], i)
            if item:
                # Собрать весь list block
                block, end_idx = self._collect_list_block(lines, i)
                blocks.append(block)
                i = end_idx + 1
            else:
                i += 1
        
        return blocks
    
    def _try_parse_item(
        self, 
        line: str, 
        line_number: int
    ) -> Optional[ListItem]:
        """Попытка распарсить строку как list item."""
        
        # Checkbox (проверять первым, т.к. subset bullet)
        match = re.match(self.CHECKBOX_PATTERN, line)
        if match:
            indent, marker, checked, content = match.groups()
            return ListItem(
                content=content,
                marker=f"{marker} [{checked}]",
                depth=len(indent) // 2,  # 2 пробела = 1 уровень
                line_number=line_number,
                list_type=ListType.CHECKBOX,
                is_checked=(checked.lower() == 'x')
            )
        
        # Numbered
        match = re.match(self.NUMBERED_PATTERN, line)
        if match:
            indent, marker, content = match.groups()
            return ListItem(
                content=content,
                marker=marker,
                depth=len(indent) // 2,
                line_number=line_number,
                list_type=ListType.NUMBERED,
                is_checked=None
            )
        
        # Bullet
        match = re.match(self.BULLET_PATTERN, line)
        if match:
            indent, marker, content = match.groups()
            return ListItem(
                content=content,
                marker=marker,
                depth=len(indent) // 2,
                line_number=line_number,
                list_type=ListType.BULLET,
                is_checked=None
            )
        
        return None
    
    def _collect_list_block(
        self, 
        lines: list[str], 
        start_idx: int
    ) -> tuple[ListBlock, int]:
        """Собрать весь list block начиная с start_idx."""
        items = []
        max_depth = 0
        end_idx = start_idx
        
        for i in range(start_idx, len(lines)):
            line = lines[i]
            
            # Пустая строка может прервать список
            if not line.strip():
                # Проверить, продолжается ли список после пустой строки
                if i + 1 < len(lines):
                    next_item = self._try_parse_item(lines[i + 1], i + 1)
                    if next_item:
                        continue  # Список продолжается
                break
            
            item = self._try_parse_item(line, i)
            if item:
                items.append(item)
                max_depth = max(max_depth, item.depth)
                end_idx = i
            elif items:
                # Continuation line (wrapped content)
                # Добавить к последнему item
                items[-1].content += '\n' + line.strip()
            else:
                break
        
        # Определить преобладающий тип
        type_counts = {}
        for item in items:
            type_counts[item.list_type] = type_counts.get(item.list_type, 0) + 1
        primary_type = max(type_counts, key=type_counts.get)
        
        return ListBlock(
            items=items,
            start_line=start_idx,
            end_line=end_idx,
            list_type=primary_type,
            max_depth=max_depth
        ), end_idx
```

### Интеграция с ContentAnalysis

```python
@dataclass
class ContentAnalysis:
    # Existing fields
    code_ratio: float
    table_count: int
    header_count: int
    # ...
    
    # New fields for lists
    list_count: int          # Количество list blocks
    list_item_count: int     # Общее количество items
    list_ratio: float        # Доля текста в списках
    max_list_depth: int      # Максимальная вложенность
    has_checkbox_lists: bool # Есть ли checkbox списки
    
    def is_list_heavy(self) -> bool:
        """Определить, является ли документ list-heavy."""
        return self.list_ratio > 0.40 or self.list_count >= 5
```

---

## Тестирование

### Unit Tests

```python
def test_parse_bullet_list():
    """Parsing простого bullet list"""
    text = """
- Item 1
- Item 2
- Item 3
"""
    blocks = ListParser().parse_lists(text)
    assert len(blocks) == 1
    assert blocks[0].item_count == 3
    assert blocks[0].list_type == ListType.BULLET

def test_parse_nested_list():
    """Parsing вложенного списка"""
    text = """
- Parent
  - Child 1
  - Child 2
    - Grandchild
"""
    blocks = ListParser().parse_lists(text)
    assert blocks[0].max_depth == 2

def test_parse_checkbox_list():
    """Parsing checkbox списка"""
    text = """
- [ ] Unchecked
- [x] Checked
- [X] Also checked
"""
    blocks = ListParser().parse_lists(text)
    assert blocks[0].list_type == ListType.CHECKBOX
    assert blocks[0].items[0].is_checked == False
    assert blocks[0].items[1].is_checked == True

def test_parse_numbered_list():
    """Parsing нумерованного списка"""
    
def test_mixed_list_types():
    """Документ с разными типами списков"""
    
def test_list_with_continuation():
    """List item с многострочным контентом"""
```

---

## Ожидаемые улучшения

### Новые возможности

| Возможность | Статус до | Статус после |
|-------------|-----------|--------------|
| List detection | ❌ | ✅ |
| List ratio calculation | ❌ | ✅ |
| Nested list analysis | ❌ | ✅ |
| Checkbox list support | ❌ | ✅ |

### Enabled Features

- **Smart List Strategy** — основная зависимость
- **Improved strategy selection** — list_ratio как критерий
- **Better metadata** — информация о списках в chunk metadata

---

## Зависимости

### Блокирует

- **Feature 01: Smart List Strategy** — не может быть реализована без list detection

### Изменяет

- `markdown_chunker_v2/parser.py`
- `markdown_chunker_v2/types.py`

---

## Риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Performance overhead | Low | Low | Lazy parsing |
| Edge cases в markdown | Medium | Low | Comprehensive tests |
| Breaking changes | Low | Medium | Additive API changes |

---

## Acceptance Criteria

- [ ] Bullet lists (-, *, +) распознаются
- [ ] Numbered lists (1., 2., etc.) распознаются
- [ ] Checkbox lists (- [ ], - [x]) распознаются
- [ ] Вложенность до 5 уровней поддерживается
- [ ] list_ratio корректно вычисляется
- [ ] Многострочные items обрабатываются
- [ ] Производительность деградирует не более чем на 3%
- [ ] Все существующие тесты проходят

---

## Примеры из тестового корпуса

Следующие файлы подходят для тестирования List Detection:

### Разнообразные типы списков

| Файл | Списков | Описание |
|------|---------|----------|
| [changelogs_005.md](../../../tests/corpus/changelogs/changelogs_005.md) | 128 | Много bullet lists |
| [node.md](../../../tests/corpus/github_readmes/javascript/node.md) | 660 | Огромное количество списков |
| [fastapi.md](../../../tests/corpus/github_readmes/python/fastapi.md) | 99 | Смешанные типы списков |
| [pytorch.md](../../../tests/corpus/github_readmes/python/pytorch.md) | 81 | Технические списки |
| [webpack.md](../../../tests/corpus/github_readmes/javascript/webpack.md) | 62 | Feature lists |
| [eslint.md](../../../tests/corpus/github_readmes/javascript/eslint.md) | 52 | Configuration lists |

### Cheatsheets и Personal Notes

| Файл | Списков | Описание |
|------|---------|----------|
| [cheatsheets_003.md](../../../tests/corpus/personal_notes/cheatsheets/cheatsheets_003.md) | 9 | Cheatsheet со списками команд |
| [journals_003.md](../../../tests/corpus/personal_notes/journals/journals_003.md) | 10 | Журнал со списками задач |

### Mixed Content со списками

| Файл | Списков | Описание |
|------|---------|----------|
| [mixed_content_005.md](../../../tests/corpus/mixed_content/mixed_content_005.md) | 16 | Смешанный контент со списками |
| [mixed_content_006.md](../../../tests/corpus/mixed_content/mixed_content_006.md) | 16 | Mixed content |
| [mixed_content_007.md](../../../tests/corpus/mixed_content/mixed_content_007.md) | 16 | Mixed content |
| [mixed_content_018.md](../../../tests/corpus/mixed_content/mixed_content_018.md) | 16 | Mixed content |
