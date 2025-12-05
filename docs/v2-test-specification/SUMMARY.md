# Сводка: Спецификация тестов V2

## Результаты анализа

### Исходные данные
- **Проанализировано legacy-тестов**: 3188 тестов из 126 файлов
- **Применимы к v2**: 2369 тестов (74%)
- **Удалённая функциональность**: 819 тестов (26%)

### Созданные артефакты
- **Смысловых групп**: 26 (7 Parser + 7 Chunker + 4 Strategy + 4 Integration + 4 Property)
- **Спецификаций тестов**: 52 (24 property + 20 unit + 8 integration)
- **Архивных групп**: 5 (удалённые стратегии и архитектура)

## Распределение по приоритетам

| Приоритет | Количество | Описание |
|-----------|------------|----------|
| Critical | 12 | Базовые инварианты системы |
| High | 18 | Стратегии и метаданные |
| Medium | 16 | Edge cases и ошибки |
| Low | 6 | Производительность |

## Распределение по компонентам V2

| Компонент | Спецификации | Приоритет |
|-----------|--------------|-----------|
| Parser.analyze() | SPEC-001, 006, 007 | Critical |
| ContentAnalysis | SPEC-001 to 006 | Critical/High |
| MarkdownChunker | SPEC-008 to 014, 020 | Critical/High |
| ChunkConfig | SPEC-009, 010, 015 | High/Medium |
| Chunk | SPEC-008, 013, 021 | Critical/High |
| CodeAwareStrategy | SPEC-016 | High |
| StructuralStrategy | SPEC-017 | High |
| FallbackStrategy | SPEC-018 | Medium |

## Фазы реализации

| Фаза | Фокус | Время | Спецификации |
|------|-------|-------|--------------|
| Phase 1 | Critical Foundation | 25-30h | SPEC-001, 002, 006, 008, 009, 012, 020, 021, 023-025 |
| Phase 2 | High Priority | 25-30h | SPEC-003, 005, 007, 010, 011, 013, 014, 016, 017, 026 |
| Phase 3 | Medium Priority | 20-25h | SPEC-004, 015, 018, 019, 022, 027-029 |
| Phase 4 | Low Priority | 10-15h | SPEC-030 to 052 |

**Общая оценка**: 80-100 часов

## Что НЕ тестируется (удалённая функциональность)

- ListStrategy → merged into FallbackStrategy
- TableStrategy → merged into FallbackStrategy  
- SentencesStrategy → merged into FallbackStrategy
- MixedStrategy → merged into FallbackStrategy
- Stage-based architecture → replaced with linear pipeline
- 32 параметра конфигурации → упрощено до 8

## Существующие тесты V2

Уже работают и покрывают базовую функциональность:
- `tests/test_domain_properties.py` — PROP-1 to PROP-9
- `tests/test_v2_properties.py` — PROP-10 to PROP-16
- `tests/test_p1_specification_properties.py` — валидация спецификации

## Следующие шаги

1. Начать с Phase 1 (Critical)
2. Создать файлы тестов по шаблону из спецификации
3. Добавить в `make test`
4. Достичь 90% покрытия кода
