# Спецификация тестов для markdown_chunker_v2

## Обзор

Эта папка содержит полную спецификацию для создания новых тестов markdown_chunker_v2. 
Спецификация создана на основе анализа ~3200 legacy-тестов и определяет, какие тесты 
нужно написать с нуля для v2 API.

## Как пользоваться этой документацией

### Шаг 1: Понять контекст
Прочитайте [SUMMARY.md](./SUMMARY.md) для понимания общей картины:
- Сколько тестов было проанализировано
- Какие группы тестов выделены
- Какие спецификации созданы

### Шаг 2: Выбрать задачу для реализации
Откройте [implementation-roadmap.md](./implementation-roadmap.md):
- Найдите спецификации по приоритету (Critical → High → Medium → Low)
- Выберите спецификацию для реализации
- Посмотрите оценку времени

### Шаг 3: Изучить спецификацию теста
Откройте [v2-test-specification.md](./v2-test-specification.md):
- Найдите нужную спецификацию (SPEC-001, SPEC-002, ...)
- Изучите: Purpose, V2 API, Property Definition, Inputs, Expected Outputs, Edge Cases
- Посмотрите Legacy Reference для контекста

### Шаг 4: Написать тест
Используйте шаблон из спецификации:
```python
from hypothesis import given, settings, strategies as st
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig

class TestSPEC001ContentAnalysisMetrics:
    """
    SPEC-001: Content Analysis Metrics Accuracy
    
    **Feature: v2-test-specification, Property 1: Content metrics accuracy**
    **Validates: Requirements 3.1, 3.2**
    """
    
    @given(st.text(min_size=0, max_size=10000))
    @settings(max_examples=100)
    def test_metrics_accuracy(self, text: str):
        from markdown_chunker_v2.parser import Parser
        
        analysis = Parser().analyze(text)
        
        assert analysis.total_chars == len(text)
        assert analysis.total_lines == text.count('\n') + 1
        assert 0 <= analysis.code_ratio <= 1
```

### Шаг 5: Запустить тесты
```bash
# Запустить все тесты
make test

# Запустить конкретный файл
python -m pytest tests/test_v2_parser_properties.py -v
```

## Структура файлов

| Файл | Описание |
|------|----------|
| [README.md](./README.md) | Этот файл — точка входа |
| [SUMMARY.md](./SUMMARY.md) | Краткая сводка результатов анализа |
| [semantic-groups.md](./semantic-groups.md) | 26 смысловых групп тестов |
| [v2-test-specification.md](./v2-test-specification.md) | 52 спецификации новых тестов |
| [implementation-roadmap.md](./implementation-roadmap.md) | План реализации в 4 фазы |
| [test-intent-analysis.md](./test-intent-analysis.md) | Детальный анализ 3188 legacy-тестов |

## Связанные файлы

- **Скрипт анализа**: `scripts/analyze_p1_tests.py` — извлекает намерения из legacy-тестов
- **Property-тесты процесса**: `tests/test_p1_specification_properties.py` — валидирует спецификацию

## Ключевые числа

| Метрика | Значение |
|---------|----------|
| Legacy-тестов проанализировано | 3188 |
| Применимы к v2 | 2369 (74%) |
| Удалённая функциональность | 819 (26%) |
| Смысловых групп | 26 |
| Спецификаций новых тестов | 52 |
| Оценка времени реализации | 80-100 часов |

## V2 API Reference

```
markdown_chunker_v2/
├── __init__.py          # Exports: MarkdownChunker, ChunkConfig, Chunk, ContentAnalysis
├── parser.py            # Parser.analyze() → ContentAnalysis
├── chunker.py           # MarkdownChunker.chunk() → List[Chunk]
├── config.py            # ChunkConfig (8 параметров)
├── types.py             # Chunk, ContentAnalysis, FencedBlock, Header, TableBlock
├── validator.py         # Validator, validate_chunks()
└── strategies/
    ├── code_aware.py    # CodeAwareStrategy (code_ratio > 0.3)
    ├── structural.py    # StructuralStrategy (headers >= 3)
    └── fallback.py      # FallbackStrategy (default)
```

## Приоритеты реализации

1. **Critical** (12 спецификаций) — базовые инварианты, без которых система не работает
2. **High** (18 спецификаций) — важная функциональность стратегий и метаданных
3. **Medium** (16 спецификаций) — edge cases и обработка ошибок
4. **Low** (6 спецификаций) — производительность и документация

## Контакты

При возникновении вопросов по спецификации обращайтесь к:
- Исходной спецификации: `.kiro/specs/p1-test-specification/`
- Legacy-анализу: `docs/legacy-tests-analysis/`
