# План Редизайна: Фаза 1 — Подготовка

## Цель

Создать "страховочную сетку" из property-based тестов перед началом редизайна.

## Длительность: 2-3 дня

## Задачи

### 1.1 Создать структуру тестов

```
tests_v2/
├── conftest.py
├── test_properties.py      # 8 property-based тестов
├── test_integration.py     # 1 интеграционный тест
├── test_edge_cases.py      # ~10 edge cases
└── fixtures/
    └── sample_docs/
        ├── code_heavy.md
        ├── structured.md
        ├── mixed.md
        └── simple.md
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

**Важные (PROP-6 через PROP-8):**

| # | Свойство | Описание |
|---|----------|----------|
| 6 | Code Block Integrity | Code blocks не разбиваются |
| 7 | Table Integrity | Таблицы не разбиваются |
| 8 | Serialization Round-Trip | Сериализация обратима |

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
