# 🚀 Быстрый старт

## 📦 Установка

```bash
# Клонирование репозитория
git clone <repository-url>
cd dify-markdown-chunker

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -e ".[dev]"
```

## ✅ Проверка установки

```bash
# Запуск тестов
make test

# Демонстрация возможностей
make demo

# Проверка качества кода
make lint
```

## 🎯 Основное использование

### Простая обработка документа

```python
from stage1 import process_markdown

# Обработка Markdown текста
markdown_text = """
# Документация API

## Введение

Это пример документации с кодом:

```python
def hello_world():
    print("Hello, World!")
    return "success"
```

### Особенности

- Поддержка множественных языков
- Автоматическое определение типа контента
- Извлечение метаданных

| Параметр | Тип | Описание |
|----------|-----|----------|
| name | str | Имя функции |
| result | any | Результат выполнения |
"""

# Полная обработка документа
result = process_markdown(markdown_text)

# Результаты обработки
print(f"📄 Обработан документ размером {result.analysis.total_chars} символов")
print(f"🔍 Найдено элементов:")
print(f"  - Заголовков: {len(result.elements.headers)}")
print(f"  - Блоков кода: {len(result.fenced_blocks)}")
print(f"  - Списков: {len(result.elements.lists)}")
print(f"  - Таблиц: {len(result.elements.tables)}")
print(f"📊 Тип контента: {result.analysis.content_type}")
print(f"⚡ Время обработки: {result.processing_time:.3f}с")
```

### Работа с отдельными компонентами

```python
from stage1 import (
    parse_to_ast,
    extract_fenced_blocks,
    detect_elements,
    analyze_content
)

markdown_text = "# Заголовок\n\n```python\nprint('hello')\n```"

# Парсинг в AST
ast = parse_to_ast(markdown_text)
print(f"AST корень: {ast.type}, дочерних узлов: {len(ast.children)}")

# Извлечение блоков кода
blocks = extract_fenced_blocks(markdown_text)
for block in blocks:
    print(f"Блок {block.language}: {len(block.content)} символов")

# Обнаружение структурных элементов
elements = detect_elements(markdown_text)
for header in elements.headers:
    print(f"H{header.level}: {header.text}")

# Анализ контента
analysis = analyze_content(markdown_text)
print(f"Сложность: {analysis.complexity_score:.2f}")
print(f"Соотношение кода: {analysis.code_ratio:.2f}")
```

## ⚙️ Конфигурация

### Базовая конфигурация

```python
from stage1 import Stage1Interface, Stage1Config

# Создание конфигурации
config = Stage1Config(
    parser=ParserConfig(
        preferred_parser="markdown-it-py",
        enable_positions=True
    ),
    analyzer=AnalyzerConfig(
        code_ratio_threshold=0.7,
        enable_language_detection=True
    )
)

# Использование с конфигурацией
interface = Stage1Interface(config)
result = interface.process_document(markdown_text)
```

### Готовые конфигурации

```python
from stage1.config import get_default_config, get_fast_config, get_detailed_config

# Конфигурация по умолчанию (баланс скорости и качества)
config = get_default_config()

# Быстрая конфигурация (максимальная скорость)
config = get_fast_config()

# Детальная конфигурация (максимальное качество)
config = get_detailed_config()
```

## 🔍 Работа с результатами

### Структура результатов

```python
result = process_markdown(markdown_text)

# AST дерево
ast_root = result.ast_root
print(f"Тип корня: {ast_root.type}")
print(f"Позиция: строки {ast_root.start_pos.line}-{ast_root.end_pos.line}")

# Огражденные блоки
for i, block in enumerate(result.fenced_blocks):
    print(f"Блок {i+1}:")
    print(f"  Язык: {block.language or 'не указан'}")
    print(f"  Размер: {len(block.content)} символов")
    print(f"  Строки: {block.start_line}-{block.end_line}")
    print(f"  Закрыт: {'✅' if block.is_closed else '❌'}")
    
    # Извлечение функций и классов
    if block.language == 'python':
        functions = block.extract_function_names()
        classes = block.extract_class_names()
        print(f"  Функции: {functions}")
        print(f"  Классы: {classes}")

# Структурные элементы
elements = result.elements

# Заголовки с иерархией
for header in elements.headers:
    indent = "  " * (header.level - 1)
    print(f"{indent}H{header.level}: {header.text}")
    print(f"{indent}Якорь: {header.anchor}")

# Списки с анализом
for i, lst in enumerate(elements.lists):
    print(f"Список {i+1} ({lst.list_type}):")
    print(f"  Элементов: {len(lst.items)}")
    print(f"  Макс. вложенность: {lst.max_nesting_level}")
    if lst.list_type == 'task':
        completed = sum(1 for item in lst.items if item.is_completed)
        print(f"  Выполнено: {completed}/{len(lst.items)}")

# Таблицы
for i, table in enumerate(elements.tables):
    print(f"Таблица {i+1}:")
    print(f"  Размер: {table.column_count}x{len(table.rows)}")
    print(f"  Заголовки: {', '.join(table.headers)}")
    print(f"  Выравнивание: {table.alignment}")

# Анализ контента
analysis = result.analysis
print(f"\n📊 Анализ контента:")
print(f"Тип: {analysis.content_type}")
print(f"Сложность: {analysis.complexity_score:.2f}")
print(f"Соотношения:")
print(f"  Код: {analysis.code_ratio:.1%}")
print(f"  Списки: {analysis.list_ratio:.1%}")
print(f"  Таблицы: {analysis.table_ratio:.1%}")
```

## 🛠️ Обработка ошибок

```python
from stage1 import process_markdown
from stage1.errors import MarkdownParsingError, Stage1Error

try:
    result = process_markdown(malformed_markdown)
except MarkdownParsingError as e:
    print(f"Ошибка парсинга: {e}")
    # Используем fallback парсер
    result = process_markdown(malformed_markdown, use_fallback=True)
except Stage1Error as e:
    print(f"Общая ошибка Stage 1: {e}")
    # Обработка ошибки
```

## 📈 Бенчмарки и производительность

```python
from stage1.benchmark import benchmark_parsers, print_benchmark_results

# Запуск бенчмарков
results = benchmark_parsers()

# Вывод результатов
print_benchmark_results(results)

# Получение лучшего парсера
best_parser = max(results.items(), key=lambda x: x[1].parse_time)
print(f"Самый быстрый парсер: {best_parser[0]}")
```

## 🎯 Подготовка к Stage 2

```python
# Получение данных для чанкования
result = process_markdown(markdown_text)

# Подготовка для Stage 2
chunking_data = {
    'ast': result.ast_root,
    'blocks': result.fenced_blocks,
    'elements': result.elements,
    'analysis': result.analysis,
    'strategy_hint': result.analysis.content_type  # code_heavy, list_heavy, etc.
}

# Рекомендуемая стратегия чанкования
if result.analysis.content_type == 'code_heavy':
    print("Рекомендуется CodeChunkStrategy")
elif result.analysis.content_type == 'list_heavy':
    print("Рекомендуется ListChunkStrategy")
else:
    print("Рекомендуется StructuralStrategy")
```

## 🔧 Отладка и диагностика

```bash
# Включение подробного логирования
export STAGE1_LOG_LEVEL=DEBUG

# Запуск с профилированием
python -m cProfile -o profile.stats your_script.py

# Анализ производительности
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(10)
"
```

## 📚 Следующие шаги

1. Изучите [примеры использования](examples.md) для более сложных сценариев
2. Ознакомьтесь с [архитектурой](architecture.md) для понимания внутреннего устройства
3. Прочитайте документацию по [интеграции с Stage 2](stage2-integration.md)
4. Изучите [API отдельных компонентов](markdown-ast.md) для тонкой настройки