# План Редизайна: Фаза 0 и 1 — Подготовка

## Фаза 0: Тестовый корпус (1-2 дня)

### 0.1 Создать тестовый корпус

```
tests/fixtures/corpus/
├── code_heavy/
│   ├── python_tutorial.md
│   ├── api_reference.md
│   └── code_snippets.md
├── structured/
│   ├── user_guide.md
│   ├── architecture_doc.md
│   └── faq.md
├── mixed/
│   ├── readme.md
│   ├── changelog.md
│   └── contributing.md
├── simple/
│   ├── notes.md
│   ├── todo.md
│   └── blog_post.md
└── edge_cases/
    ├── nested_code_blocks.md
    ├── large_tables.md
    ├── mixed_line_endings.md
    └── unicode_heavy.md
```

### 0.2 Сохранить baseline результаты

```bash
python scripts/save_baseline.py --corpus tests/fixtures/corpus --output baseline.json
```

### 0.3 Создать скрипт сравнения

```bash
python scripts/compare_results.py --baseline baseline.json --new new_results.json
```

### 0.4 Определить rollback критерии

| Метрика | Порог | Действие |
|---------|-------|----------|
| Chunk count difference | >5% | Review required |
| Content loss | >1% | Rollback |
| Property test failures | Any | Rollback |
| Table integrity errors | Any | Rollback |

---

## Фаза 1: Property-Based тесты (2-3 дня)

### 1.1 Создать структуру тестов

```
tests_v2/
├── conftest.py
├── test_properties.py      # 10 property-based тестов (PROP-1..10)
├── test_design_fixes.py    # 6 property-based тестов (design fixes)
├── test_integration.py     # 1 интеграционный тест
├── test_edge_cases.py      # ~10 edge cases
└── fixtures/
    └── corpus/             # Тестовый корпус
```

### 1.2 Написать property-based тесты

**Критические (PROP-1 через PROP-5):**

| # | Свойство | Описание |
|---|----------|----------|
| 1 | No Content Loss | Весь контент сохраняется |
| 2 | Size Bounds | Чанки в пределах лимитов |
| 3 | Monotonic Order | Чанки в порядке документа |
| 4 | No Empty Chunks | Нет пустых чанков |
| 5 | Valid Line Numbers | Корректные номера строк |

**Важные (PROP-6 через PROP-10):**

| # | Свойство | Описание |
|---|----------|----------|
| 6 | Code Block Integrity | Code blocks не разбиваются |
| 7 | Table Integrity | Таблицы не разбиваются |
| 8 | Serialization Round-Trip | Сериализация обратима |
| 9 | Idempotence | Повторный вызов даёт идентичный результат |
| 10 | Header Path Correctness | Путь заголовков корректен |

**Design Fixes (6 тестов):**

| # | Свойство | Описание |
|---|----------|----------|
| 1 | Overlap Integrity | Overlap content соответствует metadata |
| 2 | Code Fence Balance | Чётное количество ``` в каждом чанке |
| 3 | Table Integrity Validation | Таблицы валидируются |
| 4 | Oversize Metadata | Правильные причины oversize |
| 5 | Line Ending Normalization | Нет \r в результате |
| 6 | Idempotence | Повторный чанкинг идентичен |

### 1.3 Проверить текущий код

```bash
# Запустить новые тесты на текущем коде
pytest tests_v2/ -v

# Все тесты должны пройти
# Если не проходят — это баги в текущем коде, не в тестах
```

### 1.4 Настроить CI

```yaml
# .github/workflows/redesign.yml
name: Redesign Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -e ".[dev]"
      - run: pytest tests_v2/ -v --tb=short
```

## Критерии завершения

- [ ] Все 8 property-based тестов написаны
- [ ] Все тесты проходят на текущем коде
- [ ] CI настроен и работает
- [ ] Тестовые документы созданы

## Риски

| Риск | Вероятность | Митигация |
|------|-------------|-----------|
| Текущий код не проходит тесты | Средняя | Исправить баги или ослабить тесты |
| Hypothesis генерирует невалидный markdown | Высокая | Улучшить генератор |

## Результат

После завершения фазы 1:
- Есть надёжная "страховочная сетка" из тестов
- Можно безопасно начинать редизайн
- Любая регрессия будет обнаружена
