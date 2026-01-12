# 📊 Типы данных Stage 1
## 🎯 Обзор
Stage 1 использует строго типизированные структуры данных для обеспечения надежности и удобства использования.
## 🧩 Базовые типы
### Position
Представляет позицию в тексте с информацией о строке, колонке и смещении.
```python
@dataclass
class Position:
line: int # Номер строки (начиная с 0)
column: int # Номер колонки (начиная с 0)
offset: int # Смещение от начала текста
# Пример использования
pos = Position(line=5, column=10, offset=150)
print(f"Строка {pos.line}, колонка {pos.column}")
```
**Валидация:**
- `line >= 0`
- `column >= 0`
- `offset >= 0`
### NodeType
Перечисление типов узлов AST.
```python
class NodeType(Enum):
DOCUMENT = "document"
PARAGRAPH = "paragraph"
HEADER = "header"
LIST = "list"
LIST_ITEM = "list_item"
CODE_BLOCK = "code_block"
FENCED_CODE = "fenced_code"
TABLE = "table"
TABLE_ROW = "table_row"
TABLE_CELL = "table_cell"
TEXT = "text"
EMPHASIS = "emphasis"
STRONG = "strong"
LINK = "link"
IMAGE = "image"
BLOCKQUOTE = "blockquote"
HORIZONTAL_RULE = "horizontal_rule"
HTML_BLOCK = "html_block"
INLINE_CODE = "inline_code"
```
## 🌳 AST структуры
### MarkdownNode
Базовый узел AST дерева.
```python
@dataclass
class MarkdownNode:
type: NodeType
content: str
start_pos: Position
end_pos: Position
children: List['MarkdownNode'] = field(default_factory=list)
metadata: Dict[str, Any] = field(default_factory=dict)
def get_line_range(self) -> Tuple[int, int]:
"""Возвращает диапазон строк узла."""
return (self.start_pos.line, self.end_pos.line)
def is_leaf(self) -> bool:
"""Проверяет, является ли узел листом."""
return len(self.children) == 0
def find_children(self, node_type: NodeType) -> List['MarkdownNode']:
"""Находит дочерние узлы указанного типа."""
return [child for child in self.children if child.type == node_type]
def get_text_content(self) -> str:
"""Извлекает текстовое содержимое узла."""
if self.type == NodeType.TEXT:
return self.content
return ''.join(child.get_text_content for child in self.children)
```
**Пример использования:**
```python
# Создание узла заголовка
header = MarkdownNode(
type=NodeType.HEADER,
content="# Заголовок",
start_pos=Position(0, 0, 0),
end_pos=Position(0, 11, 11),
metadata={'level': 1}
)
# Поиск всех заголовков в документе
headers = document.find_children(NodeType.HEADER)
```
## 🔒 Огражденные блоки
### FencedBlock
Представляет огражденный блок кода.
```python
@dataclass
class FencedBlock:
content: str # Содержимое блока
language: Optional[str] # Язык программирования
fence_char: str # Символ ограждения: '`' или '~'
fence_length: int # Длина ограждения (3, 4, 5 и т.д.)
start_line: int # Начальная строка
end_line: int # Конечная строка
start_pos: int # Начальное смещение в символах
end_pos: int # Конечное смещение в символах
is_closed: bool # Закрыт ли блок (есть ли закрывающее ограждение)
def get_size(self) -> int:
"""Возвращает размер содержимого в символах."""
return len(self.content)
def is_valid(self) -> bool:
"""Проверяет валидность блока."""
return self.is_closed and len(self.content.strip) > 0
def is_nested(self) -> bool:
"""Проверяет, содержит ли блок вложенные ограждения."""
# Блок считается вложенным, если fence_length > 3
return self.fence_length > 3
def extract_function_names(self) -> List[str]:
"""Извлекает имена функций из блока (для поддерживаемых языков)."""
# Реализация зависит от языка
def extract_class_names(self) -> List[str]:
"""Извлекает имена классов из блока (для поддерживаемых языков)."""
# Реализация зависит от языка
def get_hash(self) -> str:
"""Возвращает хеш блока для идентификации."""
return f"{self.language or 'text'}_{hash(self.content)}"
```
**Пример использования:**
```python
# Создание простого блока кода (тройные бэктики)
block = FencedBlock(
content="def hello:\n print('Hello!')",
language="python",
fence_char="`",
fence_length=3,
start_line=5,
end_line=8,
start_pos=100,
end_pos=150,
is_closed=True
)
# Создание вложенного блока (четверные бэктики)
nested_block = FencedBlock(
content="```python\ncode here\n```",
language="markdown",
fence_char="`",
fence_length=4,
start_line=10,
end_line=15,
start_pos=200,
end_pos=280,
is_closed=True
)
# Проверка вложенности
print(block.is_nested) # False (fence_length=3)
print(nested_block.is_nested) # True (fence_length=4)
# Работа с тильдами (~)
tilde_block = FencedBlock(
content="code content",
language="python",
fence_char="~",
fence_length=3,
start_line=20,
end_line=23,
start_pos=300,
end_pos=350,
is_closed=True
)
```
**Поддержка вложенных ограждений:**
Парсер корректно обрабатывает вложенные блоки кода:
- Тройные бэктики (```) — стандартные блоки
- Четверные бэктики (````) — для вложения тройных внутрь
- Пятерные бэктики (`````) — для глубокой вложенности
- Тильды (~~~, ~~~~, ~~~~~) — альтернативный синтаксис
Закрывающее ограждение должно иметь тот же символ (`fence_char`) и длину >= открывающего (`fence_length`).
```
## 📋 Структурные элементы
### Header
Представляет заголовок документа.
```python
@dataclass
class Header:
level: int # Уровень заголовка (1-6)
text: str # Текст заголовка
anchor: str # Якорь для ссылок
start_line: int # Начальная строка
end_line: int # Конечная строка
start_offset: int # Начальное смещение
end_offset: int # Конечное смещение
def get_hierarchy_path(self) -> str:
"""Возвращает путь в иерархии заголовков."""
return f"h{self.level}:{self.anchor}"
```
### MarkdownList
Представляет список (упорядоченный или неупорядоченный).
```python
@dataclass
class MarkdownList:
list_type: str # 'ordered', 'unordered', 'task'
items: List[ListItem] # Элементы списка
start_line: int # Начальная строка
end_line: int # Конечная строка
max_nesting_level: int # Максимальный уровень вложенности
def get_completed_count(self) -> int:
"""Возвращает количество выполненных задач (для task списков)."""
if self.list_type != 'task':
return 0
return sum(1 for item in self.items if item.is_completed)
```
### ListItem
Представляет элемент списка.
```python
@dataclass
class ListItem:
text: str # Текст элемента
nesting_level: int # Уровень вложенности
is_completed: Optional[bool] # Выполнен ли (для task списков)
start_line: int # Начальная строка
end_line: int # Конечная строка
```
### Table
Представляет таблицу.
```python
@dataclass
class Table:
headers: List[str] # Заголовки колонок
rows: List[List[str]] # Строки данных
alignment: List[str] # Выравнивание колонок
start_line: int # Начальная строка
end_line: int # Конечная строка
column_count: int # Количество колонок
def get_cell(self, row: int, col: int) -> str:
"""Получает содержимое ячейки."""
if 0 <= row < len(self.rows) and 0 <= col < len(self.rows[row]):
return self.rows[row][col]
return ""
```
## 📦 Коллекции
### ElementCollection
Коллекция всех структурных элементов документа.
```python
@dataclass
class ElementCollection:
headers: List[Header] # Заголовки
lists: List[MarkdownList] # Списки
tables: List[Table] # Таблицы
def get_element_count(self) -> int:
"""Возвращает общее количество элементов."""
return len(self.headers) + len(self.lists) + len(self.tables)
def get_headers_by_level(self, level: int) -> List[Header]:
"""Возвращает заголовки указанного уровня."""
return [h for h in self.headers if h.level == level]
```
## 📊 Анализ контента
### ContentAnalysis
Результаты анализа содержимого документа.
```python
@dataclass
class ContentAnalysis:
total_chars: int # Общее количество символов
total_lines: int # Общее количество строк
content_type: str # Тип контента: code_heavy, list_heavy, mixed, primary
complexity_score: float # Оценка сложности (0-1)
code_ratio: float # Доля кода в документе (0-1)
list_ratio: float # Доля списков в документе (0-1)
table_ratio: float # Доля таблиц в документе (0-1)
text_ratio: float # Доля обычного текста (0-1)
languages: List[str] # Найденные языки программирования
max_header_depth: int # Максимальная глубина заголовков
max_list_nesting: int # Максимальная вложенность списков
has_mixed_content: bool # Есть ли смешанный контент
def get_dominant_content_type(self) -> str:
"""Возвращает доминирующий тип контента."""
ratios = {
'code': self.code_ratio,
'lists': self.list_ratio,
'tables': self.table_ratio,
'text': self.text_ratio
}
return max(ratios.items, key=lambda x: x[1])[0]
def is_code_heavy(self) -> bool:
"""Проверяет, является ли документ кодо-ориентированным."""
return self.code_ratio > 0.5
def get_complexity_category(self) -> str:
"""Возвращает категорию сложности."""
if self.complexity_score < 0.3:
return "simple"
elif self.complexity_score < 0.7:
return "moderate"
else:
return "complex"
```
## 🎯 Результаты Stage 1
### Stage1Results
Полные результаты обработки документа Stage 1.
```python
@dataclass
class Stage1Results:
ast_root: MarkdownNode # Корень AST дерева
fenced_blocks: List[FencedBlock] # Огражденные блоки
elements: ElementCollection # Структурные элементы
analysis: ContentAnalysis # Анализ контента
processing_time: float # Время обработки в секундах
parser_used: str # Использованный парсер
errors: List[str] # Ошибки обработки
def get_summary(self) -> Dict[str, Any]:
"""Возвращает краткую сводку результатов."""
return {
'total_elements': (
len(self.fenced_blocks) +
self.elements.get_element_count
),
'content_type': self.analysis.content_type,
'processing_time': self.processing_time,
'parser': self.parser_used,
'has_errors': len(self.errors) > 0
}
def is_suitable_for_chunking(self) -> bool:
"""Проверяет, подходит ли документ для чанкования."""
return (
self.analysis.total_chars > 100 and
len(self.errors) == 0 and
self.elements.get_element_count > 0
)
```
## 🔧 Конфигурационные типы
### ParserConfig, ExtractorConfig, etc.
Подробные конфигурационные типы описаны в [документации по конфигурации](../reference/configuration.md).
## 🎨 Примеры использования типов
### Обход AST дерева
```python
def traverse_ast(node: MarkdownNode, depth: int = 0) -> None:
"""Рекурсивный обход AST дерева."""
indent = " " * depth
print(f"{indent}{node.type.value}: {node.content[:50]}...")
for child in node.children:
traverse_ast(child, depth + 1)
# Использование
traverse_ast(result.ast_root)
```
### Фильтрация блоков по языку
```python
def get_blocks_by_language(blocks: List[FencedBlock], language: str) -> List[FencedBlock]:
"""Возвращает блоки указанного языка."""
return [block for block in blocks if block.language == language]
# Использование
python_blocks = get_blocks_by_language(result.fenced_blocks, "python")
```
### Построение оглавления
```python
def build_toc(headers: List[Header]) -> str:
"""Строит оглавление из заголовков."""
toc_lines =
for header in headers:
indent = " " * (header.level - 1)
toc_lines.append(f"{indent}- [{header.text}](#{header.anchor})")
return "\n".join(toc_lines)
# Использование
toc = build_toc(result.elements.headers)
```
## 🏗️ Hierarchical Chunking Types
### HierarchicalChunkingResult
Result object for hierarchical chunking with navigation methods.
```python
@dataclass
class HierarchicalChunkingResult:
chunks: List[Chunk] # All chunks including root document chunk
root_id: str # ID of document-level chunk
strategy_used: str # Name of chunking strategy applied
_index: Dict[str, Chunk] # Internal O(1) lookup index
```
**Navigation Methods:**
```python
def get_chunk(chunk_id: str) -> Optional[Chunk]
"""Get chunk by ID with O(1) lookup."""
def get_children(chunk_id: str) -> List[Chunk]
"""Get all child chunks of given chunk."""
def get_parent(chunk_id: str) -> Optional[Chunk]
"""Get parent chunk of given chunk."""
def get_ancestors(chunk_id: str) -> List[Chunk]
"""Get all ancestor chunks from parent to root."""
def get_siblings(chunk_id: str) -> List[Chunk]
"""Get all sibling chunks (including self)."""
def get_flat_chunks -> List[Chunk]
"""Get only leaf chunks for backward-compatible retrieval."""
def get_by_level(level: int) -> List[Chunk]
"""Get all chunks at specific hierarchy level.
Levels: 0=document, 1=section, 2=subsection, 3=paragraph"""
def to_tree_dict -> Dict
"""Convert hierarchy to tree dictionary for serialization.
Uses IDs to avoid circular references. Safe for JSON."""
```
**Example Usage:**
```python
from markdown_chunker_v2 import MarkdownChunker
chunker = MarkdownChunker
result = chunker.chunk_hierarchical(markdown_text)
# Access document root
root = result.get_chunk(result.root_id)
print(f"Document: {root.content[:100]}...")
# Navigate hierarchy
sections = result.get_children(result.root_id)
for section in sections:
subsections = result.get_children(section.metadata['chunk_id'])
print(f"Section {section.metadata['header_path']}: {len(subsections)} subsections")
# Get breadcrumb for context
matched_chunk = sections[0]
breadcrumb = [a.metadata['header_path'] for a in result.get_ancestors(matched_chunk.metadata['chunk_id'])]
print(f"Path: {' > '.join(reversed(breadcrumb))}")
# Backward-compatible flat access
leaf_chunks = result.get_flat_chunks
print(f"Total leaf chunks: {len(leaf_chunks)}")
# Export as tree
tree = result.to_tree_dict
import json
print(json.dumps(tree, indent=2))
```
### Hierarchy Metadata Fields
Each chunk in hierarchical mode includes these additional metadata fields:
| Field | Type | Description |
|-------|------|-------------|
| `chunk_id` | str | Unique 8-char hash identifier |
| `parent_id` | str \| None | Parent chunk ID (None for root) |
| `children_ids` | List[str] | Child chunk IDs |
| `prev_sibling_id` | str \| None | Previous sibling ID |
| `next_sibling_id` | str \| None | Next sibling ID |
| `hierarchy_level` | int | 0=document, 1=section, 2=subsection, 3=paragraph |
| `is_leaf` | bool | Has no children |
| `is_root` | bool | Document-level chunk |
**Example metadata:**
```python
chunk.metadata = {
"chunk_id": "a3f9d21c",
"parent_id": "7b2e4f18",
"children_ids": ["c4e8f90d", "91d3a7f2"],
"prev_sibling_id": None,
"next_sibling_id": "e5a2b8d3",
"hierarchy_level": 2,
"is_leaf": False,
"is_root": False,
"header_path": "/Installation/Requirements"
}
```