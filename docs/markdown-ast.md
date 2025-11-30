# 🌳 Markdown AST - Парсинг в дерево

## 🎯 Обзор

Модуль `markdown_ast.py` предоставляет унифицированный интерфейс для парсинга Markdown в AST (Abstract Syntax Tree) с поддержкой разных библиотек парсинга.

## 🏗️ Архитектура

### Абстрактный парсер

```python
from abc import ABC, abstractmethod
from stage1.types import MarkdownNode

class MarkdownParser(ABC):
    """Абстрактный базовый класс для парсеров Markdown."""
    
    @abstractmethod
    def parse(self, text: str) -> MarkdownNode:
        """Парсит Markdown текст в AST дерево."""
        pass
    
    @abstractmethod
    def supports_positions(self) -> bool:
        """Возвращает True, если парсер поддерживает позиционную информацию."""
        pass
```

## 🔌 Адаптеры парсеров

### MarkdownItPyAdapter

Адаптер для библиотеки `markdown-it-py` (рекомендуемый).

```python
class MarkdownItPyAdapter(MarkdownParser):
    """Адаптер для markdown-it-py с полной поддержкой позиций."""
    
    def __init__(self):
        self._parser = None
        self._init_parser()
    
    def parse(self, text: str) -> MarkdownNode:
        """Парсит текст с полной поддержкой позиций."""
        # Реализация парсинга
        
    def supports_positions(self) -> bool:
        return True
```

**Особенности:**
- ✅ Полная поддержка позиций (line/column)
- ✅ Богатое AST дерево
- ✅ Соответствие CommonMark спецификации
- ✅ Расширяемость плагинами

### MistuneAdapter

Адаптер для библиотеки `mistune`.

```python
class MistuneAdapter(MarkdownParser):
    """Адаптер для mistune с базовой поддержкой позиций."""
    
    def supports_positions(self) -> bool:
        return True  # Частичная поддержка
```

**Особенности:**
- ⚡ Высокая производительность
- ⚠️ Ограниченная поддержка позиций
- ✅ Простота использования

### CommonMarkAdapter

Адаптер для библиотеки `commonmark`.

```python
class CommonMarkAdapter(MarkdownParser):
    """Адаптер для commonmark без поддержки позиций."""
    
    def supports_positions(self) -> bool:
        return False
```

**Особенности:**
- ✅ Строгое соответствие CommonMark
- ❌ Нет поддержки позиций
- ⚡ Хорошая производительность

## 🎯 Публичный API

### Основные функции

```python
def parse_to_ast(md_text: str, parser_name: Optional[str] = None) -> MarkdownNode:
    """
    Парсит Markdown текст в AST дерево.
    
    Args:
        md_text: Markdown текст для парсинга
        parser_name: Имя парсера ('markdown-it-py', 'mistune', 'commonmark', 'auto')
    
    Returns:
        MarkdownNode: Корневой узел AST дерева
    
    Raises:
        MarkdownParsingError: При ошибке парсинга
    """

def get_best_parser() -> MarkdownParser:
    """
    Возвращает лучший доступный парсер.
    
    Приоритет:
    1. markdown-it-py (лучшее качество)
    2. mistune (хорошая производительность)
    3. commonmark (fallback)
    """

def get_available_parsers() -> List[str]:
    """Возвращает список доступных парсеров."""

def get_parser_info(parser_name: str) -> Dict[str, Any]:
    """Возвращает информацию о парсере."""
```

## 💡 Примеры использования

### Базовое использование

```python
from stage1.markdown_ast import parse_to_ast

# Простой парсинг
markdown_text = """
# Заголовок

Параграф с **жирным** текстом.

```python
def hello():
    print("Hello, World!")
```

- Элемент списка
- Другой элемент
"""

# Парсинг с автовыбором парсера
ast = parse_to_ast(markdown_text)

print(f"Тип корня: {ast.type}")
print(f"Дочерних узлов: {len(ast.children)}")
print(f"Диапазон строк: {ast.get_line_range()}")
```

### Выбор конкретного парсера

```python
# Использование конкретного парсера
ast_markdown_it = parse_to_ast(markdown_text, "markdown-it-py")
ast_mistune = parse_to_ast(markdown_text, "mistune")

# Сравнение результатов
print(f"markdown-it-py узлов: {len(ast_markdown_it.children)}")
print(f"mistune узлов: {len(ast_mistune.children)}")
```

### Работа с позициями

```python
def print_positions(node: MarkdownNode, depth: int = 0):
    """Выводит позиции всех узлов."""
    indent = "  " * depth
    start = node.start_pos
    end = node.end_pos
    
    print(f"{indent}{node.type.value}:")
    print(f"{indent}  Позиция: ({start.line}:{start.column}) - ({end.line}:{end.column})")
    print(f"{indent}  Смещение: {start.offset} - {end.offset}")
    
    for child in node.children:
        print_positions(child, depth + 1)

# Использование
ast = parse_to_ast(markdown_text, "markdown-it-py")
print_positions(ast)
```

### Поиск узлов по типу

```python
from stage1.types import NodeType

def find_all_nodes(root: MarkdownNode, node_type: NodeType) -> List[MarkdownNode]:
    """Рекурсивно находит все узлы указанного типа."""
    result = []
    
    if root.type == node_type:
        result.append(root)
    
    for child in root.children:
        result.extend(find_all_nodes(child, node_type))
    
    return result

# Поиск всех заголовков
headers = find_all_nodes(ast, NodeType.HEADER)
for header in headers:
    level = header.metadata.get('level', 1)
    text = header.get_text_content()
    print(f"H{level}: {text}")

# Поиск всех блоков кода
code_blocks = find_all_nodes(ast, NodeType.FENCED_CODE)
for block in code_blocks:
    language = block.metadata.get('language', 'text')
    print(f"Блок {language}: {len(block.content)} символов")
```

### Извлечение текстового содержимого

```python
def extract_plain_text(node: MarkdownNode) -> str:
    """Извлекает только текстовое содержимое, игнорируя разметку."""
    if node.type == NodeType.TEXT:
        return node.content
    elif node.type in [NodeType.FENCED_CODE, NodeType.CODE_BLOCK]:
        return ""  # Игнорируем код
    else:
        return " ".join(extract_plain_text(child) for child in node.children)

# Использование
plain_text = extract_plain_text(ast)
print(f"Чистый текст: {plain_text[:100]}...")
```

## 🔧 Конфигурация парсеров

### Настройка markdown-it-py

```python
from stage1.markdown_ast import MarkdownItPyAdapter

# Создание адаптера с настройками
adapter = MarkdownItPyAdapter()

# Парсинг с расширенными возможностями
ast = adapter.parse(markdown_text)
```

### Обработка ошибок

```python
from stage1.errors import MarkdownParsingError

try:
    ast = parse_to_ast(malformed_markdown)
except MarkdownParsingError as e:
    print(f"Ошибка парсинга: {e}")
    
    # Попытка с другим парсером
    try:
        ast = parse_to_ast(malformed_markdown, "mistune")
    except MarkdownParsingError:
        # Используем fallback
        ast = parse_to_ast(malformed_markdown, "commonmark")
```

## 📊 Сравнение парсеров

### Получение информации о парсерах

```python
from stage1.markdown_ast import get_available_parsers, get_parser_info

# Список доступных парсеров
parsers = get_available_parsers()
print(f"Доступные парсеры: {parsers}")

# Информация о каждом парсере
for parser_name in parsers:
    info = get_parser_info(parser_name)
    print(f"{parser_name}:")
    print(f"  Доступен: {info['available']}")
    print(f"  Поддержка позиций: {info['supports_positions']}")
```

### Бенчмарк парсеров

```python
import time
from stage1.benchmark import benchmark_parsers

# Запуск бенчмарков
results = benchmark_parsers()

# Анализ результатов
for parser_name, metrics in results.items():
    if metrics.success:
        print(f"{parser_name}:")
        print(f"  Время парсинга: {metrics.parse_time:.4f}с")
        print(f"  Узлов в AST: {metrics.node_count}")
        print(f"  Поддержка позиций: {metrics.supports_positions}")
    else:
        print(f"{parser_name}: недоступен")
```

## 🎯 Интеграция с другими компонентами

### Передача AST в другие модули

```python
from stage1.markdown_ast import parse_to_ast
from stage1.element_detector import ElementDetector
from stage1.content_analyzer import ContentAnalyzer

# Парсинг
ast = parse_to_ast(markdown_text)

# Использование AST в других компонентах
detector = ElementDetector()
elements = detector.detect_from_ast(ast)

analyzer = ContentAnalyzer()
analysis = analyzer.analyze_from_ast(ast)
```

### Восстановление исходного текста

```python
def reconstruct_text(node: MarkdownNode, original_text: str) -> str:
    """Восстанавливает исходный текст узла по позициям."""
    start_offset = node.start_pos.offset
    end_offset = node.end_pos.offset
    return original_text[start_offset:end_offset]

# Использование
ast = parse_to_ast(markdown_text)
for child in ast.children:
    if child.type == NodeType.HEADER:
        original_header = reconstruct_text(child, markdown_text)
        print(f"Исходный заголовок: {repr(original_header)}")
```

## 🚀 Производительность

### Оптимизация для больших документов

```python
def parse_large_document(text: str) -> MarkdownNode:
    """Оптимизированный парсинг для больших документов."""
    # Выбираем самый быстрый доступный парсер
    if "mistune" in get_available_parsers():
        return parse_to_ast(text, "mistune")
    else:
        return parse_to_ast(text, "auto")

# Использование
large_text = "# Header\n" * 10000  # Большой документ
ast = parse_large_document(large_text)
```

### Кеширование результатов

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_parse(text_hash: str, text: str) -> MarkdownNode:
    """Кешированный парсинг для повторяющихся документов."""
    return parse_to_ast(text)

# Использование
text_hash = hash(markdown_text)
ast = cached_parse(text_hash, markdown_text)
```

## 🔮 Расширение функциональности

### Добавление нового парсера

```python
class MyCustomAdapter(MarkdownParser):
    """Пользовательский адаптер парсера."""
    
    def __init__(self):
        # Инициализация парсера
        pass
    
    def parse(self, text: str) -> MarkdownNode:
        # Реализация парсинга
        # Должна возвращать MarkdownNode с правильной структурой
        pass
    
    def supports_positions(self) -> bool:
        return True  # или False
```

### Постобработка AST

```python
def enhance_ast(node: MarkdownNode) -> MarkdownNode:
    """Добавляет дополнительные метаданные в AST."""
    # Добавление ID для заголовков
    if node.type == NodeType.HEADER:
        text = node.get_text_content()
        node.metadata['id'] = text.lower().replace(' ', '-')
    
    # Рекурсивная обработка дочерних узлов
    for child in node.children:
        enhance_ast(child)
    
    return node

# Использование
ast = parse_to_ast(markdown_text)
enhanced_ast = enhance_ast(ast)
```