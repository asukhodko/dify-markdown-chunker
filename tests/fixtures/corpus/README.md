# Test Corpus

Этот каталог содержит тестовый корпус из реальных markdown документов для валидации редизайна markdown_chunker.

## Структура

```
corpus/
├── code_heavy/      # Документы с большим количеством кода
├── structured/      # Документы со структурой (заголовки, списки)
├── mixed/           # Смешанный контент
├── simple/          # Простые документы
└── edge_cases/      # Граничные случаи
```

## Использование

### Сохранение baseline

```bash
python scripts/save_baseline.py --corpus tests/fixtures/corpus --output baseline.json
```

### Сравнение результатов

```bash
python scripts/compare_results.py --baseline baseline.json --corpus tests/fixtures/corpus
```

## Критерии выбора документов

1. **code_heavy/** — документы с >50% кода
   - API reference
   - Tutorials с примерами кода
   - Code snippets collections

2. **structured/** — документы с иерархией заголовков
   - User guides
   - Architecture docs
   - FAQ

3. **mixed/** — типичные README и документация
   - README.md
   - CHANGELOG.md
   - CONTRIBUTING.md

4. **simple/** — минимальная структура
   - Notes
   - Todo lists
   - Blog posts

5. **edge_cases/** — граничные случаи
   - Nested code blocks (4+ backticks)
   - Large tables (>50 rows)
   - Mixed line endings
   - Unicode heavy content
