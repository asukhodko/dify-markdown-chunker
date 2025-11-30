# 🔒 Извлечение огражденных блоков

## 🎯 Обзор

Модуль `fenced_block_extractor.py` предоставляет функциональность для извлечения огражденных блоков кода из Markdown документов с поддержкой вложенности и различных типов ограждений.

## 🚀 Основной API

### Функция extract_fenced_blocks

```python
def extract_fenced_blocks(md_text: str) -> List[FencedBlock]:
    """
    Извлекает все огражденные блоки из Markdown текста.
    
    Args:
        md_text: Markdown текст для обработки
    
    Returns:
        List[FencedBlock]: Список найденных блоков
    
    Example:
        blocks = extract_fenced_blocks(markdown_text)
        for block in blocks:
            print(f"{block.language}: {len(block.content)} chars")
    """
```

## 🏗️ Класс FencedBlockExtractor

### Инициализация

```python
from stage1.fenced_block_extractor import FencedBlockExtractor

# Создание экстрактора
extractor = FencedBlockExtractor()

# Извлечение блоков
blocks = extractor.extract_fenced_blocks(markdown_text)
```

### Поддерживаемые типы ограждений

```python
# Поддерживаемые паттерны
fence_patterns = {
    'backtick': r'^(`{3,})\s*([a-zA-Z0-9_+-]*)\s*$',  # ```python
    'tilde': r'^(~{3,})\s*([a-zA-Z0-9_+-]*)\s*$'      # ~~~bash
}
```

**Примеры поддерживаемых блоков:**

```markdown
# Блоки с обратными кавычками
```python
def hello():
    print("Hello!")
```

# Блоки с тильдами
~~~bash
echo "Hello from bash"
~~~

# Блоки без языка
```
Простой текстовый блок
```

# Блоки с дополнительными символами
````markdown
```python
# Вложенный блок
```
````
```

## 🔍 Извлечение метаданных

### Функции и классы

```python
# Извлечение имен функций
block = blocks[0]  # Python блок
functions = block.extract_function_names()
print(f"Найденные функции: {functions}")

# Извлечение имен классов
classes = block.extract_class_names()
print(f"Найденные классы: {classes}")
```

**Поддерживаемые языки для извлечения:**
- Python: `def function_name`, `class ClassName`
- JavaScript: `function functionName`, `class ClassName`
- Go: `func functionName`, `type StructName struct`
- Java: `public/private class ClassName`, `method methodName`
- C/C++: `type functionName`, `class ClassName`
- Rust: `fn function_name`, `struct StructName`
- PHP: `function functionName`, `class ClassName`

### Позиционная информация

```python
for block in blocks:
    print(f"Блок {block.language or 'text'}:")
    print(f"  Строки: {block.start_line} - {block.end_line}")
    print(f"  Смещения: {block.start_offset} - {block.end_offset}")
    print(f"  Размер: {block.get_size()} символов")
    print(f"  Вложенность: уровень {block.nesting_level}")
    print(f"  Закрыт: {'✅' if block.is_closed else '❌'}")
```

## 🎯 Обработка вложенности

### Простая вложенность

```python
markdown_with_nesting = """
# Документация

Пример с вложенными блоками:

```markdown
# Заголовок в блоке

```python
def nested_function():
    return "nested"
```

Текст после вложенного блока.
```

Конец документа.
"""

blocks = extract_fenced_blocks(markdown_with_nesting)

# Анализ вложенности
for block in blocks:
    level = block.nesting_level
    indent = "  " * level
    print(f"{indent}Блок уровня {level}: {block.language}")
```

### Сложная вложенность

```python
# Обработка сложных случаев вложенности
complex_nesting = """
````markdown
# Внешний блок

```python
def outer():
    '''
    Docstring с блоком:
    ```
    example code
    ```
    '''
    pass
```

Текст между блоками.

~~~bash
echo "Тильды внутри markdown"
~~~
````
"""

blocks = extract_fenced_blocks(complex_nesting)

# Построение дерева вложенности
def build_nesting_tree(blocks: List[FencedBlock]) -> Dict:
    """Строит дерево вложенности блоков."""
    tree = {}
    for block in blocks:
        level = block.nesting_level
        if level not in tree:
            tree[level] = []
        tree[level].append(block)
    return tree

nesting_tree = build_nesting_tree(blocks)
for level, level_blocks in nesting_tree.items():
    print(f"Уровень {level}: {len(level_blocks)} блоков")
```

## 🛠️ Продвинутое использование

### Фильтрация блоков

```python
def filter_blocks(blocks: List[FencedBlock], **criteria) -> List[FencedBlock]:
    """Фильтрует блоки по критериям."""
    result = blocks
    
    if 'language' in criteria:
        result = [b for b in result if b.language == criteria['language']]
    
    if 'min_size' in criteria:
        result = [b for b in result if len(b.content) >= criteria['min_size']]
    
    if 'is_closed' in criteria:
        result = [b for b in result if b.is_closed == criteria['is_closed']]
    
    if 'max_nesting' in criteria:
        result = [b for b in result if b.nesting_level <= criteria['max_nesting']]
    
    return result

# Примеры фильтрации
python_blocks = filter_blocks(blocks, language='python')
large_blocks = filter_blocks(blocks, min_size=100)
closed_blocks = filter_blocks(blocks, is_closed=True)
top_level_blocks = filter_blocks(blocks, max_nesting=0)
```

### Группировка блоков

```python
from collections import defaultdict

def group_blocks_by_language(blocks: List[FencedBlock]) -> Dict[str, List[FencedBlock]]:
    """Группирует блоки по языкам программирования."""
    groups = defaultdict(list)
    
    for block in blocks:
        language = block.language or 'text'
        groups[language].append(block)
    
    return dict(groups)

# Использование
grouped = group_blocks_by_language(blocks)
for language, lang_blocks in grouped.items():
    print(f"{language}: {len(lang_blocks)} блоков")
    
    # Статистика по языку
    total_size = sum(len(b.content) for b in lang_blocks)
    avg_size = total_size / len(lang_blocks)
    print(f"  Общий размер: {total_size} символов")
    print(f"  Средний размер: {avg_size:.1f} символов")
```

### Валидация блоков

```python
def validate_blocks(blocks: List[FencedBlock]) -> Dict[str, Any]:
    """Валидирует корректность извлеченных блоков."""
    stats = {
        'total': len(blocks),
        'valid': 0,
        'closed': 0,
        'with_language': 0,
        'with_functions': 0,
        'errors': []
    }
    
    for i, block in enumerate(blocks):
        if block.is_valid():
            stats['valid'] += 1
        
        if block.is_closed:
            stats['closed'] += 1
        
        if block.language:
            stats['with_language'] += 1
        
        # Проверка на наличие функций
        if block.language in ['python', 'javascript', 'go']:
            functions = block.extract_function_names()
            if functions:
                stats['with_functions'] += 1
        
        # Проверка корректности позиций
        if block.start_line > block.end_line:
            stats['errors'].append(f"Блок {i}: некорректные позиции строк")
        
        if block.start_offset > block.end_offset:
            stats['errors'].append(f"Блок {i}: некорректные смещения")
    
    return stats

# Использование
validation = validate_blocks(blocks)
print(f"Валидация блоков:")
print(f"  Всего: {validation['total']}")
print(f"  Валидных: {validation['valid']}")
print(f"  Закрытых: {validation['closed']}")
print(f"  С языком: {validation['with_language']}")
print(f"  С функциями: {validation['with_functions']}")

if validation['errors']:
    print(f"  Ошибки: {len(validation['errors'])}")
    for error in validation['errors']:
        print(f"    - {error}")
```

## 🔧 Настройка и конфигурация

### ExtractorConfig

```python
from stage1.config import ExtractorConfig

config = ExtractorConfig(
    enable_nesting=True,           # Поддержка вложенности
    enable_function_extraction=True, # Извлечение имен функций
    enable_class_extraction=True,   # Извлечение имен классов
    max_nesting_depth=5,           # Максимальная глубина вложенности
    min_block_size=10              # Минимальный размер блока
)

# Использование с конфигурацией
extractor = FencedBlockExtractor(config)
blocks = extractor.extract_fenced_blocks(markdown_text)
```

## 🧪 Тестирование

### Тестовые сценарии

```python
# Тестирование различных сценариев
test_cases = [
    # Простой блок
    "```python\nprint('hello')\n```",
    
    # Блок без языка
    "```\nplain text\n```",
    
    # Незакрытый блок
    "```python\nprint('unclosed')",
    
    # Смешанные ограждения
    "```python\ncode\n```\n\n~~~bash\necho 'hi'\n~~~",
    
    # Вложенные блоки
    "````markdown\n```python\ncode\n```\n````"
]

for i, test_case in enumerate(test_cases):
    print(f"Тест {i+1}:")
    blocks = extract_fenced_blocks(test_case)
    print(f"  Найдено блоков: {len(blocks)}")
    for block in blocks:
        print(f"    {block.language or 'text'}: {block.is_closed}")
```

## 🎯 Интеграция с Stage 2

Результаты извлечения блоков готовы для использования в Stage 2:

```python
# Подготовка данных для чанкования
def prepare_blocks_for_chunking(blocks: List[FencedBlock]) -> Dict[str, Any]:
    """Подготавливает блоки для Stage 2."""
    return {
        'code_blocks': [b for b in blocks if b.language],
        'text_blocks': [b for b in blocks if not b.language],
        'large_blocks': [b for b in blocks if len(b.content) > 500],
        'functions': sum([b.extract_function_names() for b in blocks], []),
        'languages': list(set(b.language for b in blocks if b.language))
    }

# Использование
chunking_data = prepare_blocks_for_chunking(blocks)
```