# Oracle Тестирование (Oracle Testing Framework)
## Метаинформация
- **Конкурентная ценность**: Средняя
- **Влияние на пользователей**: Низкое
- **Сложность реализации**: Средняя
- **Стратегический приоритет**: P2 — Качество
- **Область**: Парсер как источник истины
## Стратегический контекст
С multiple backends и dialects, manual testing недостаточен. Нужны automated correctness proofs: "Chunkana не режет внутри atomic blocks", "Boundaries на block boundaries".
## Мотивация
С multiple backends, dialects и strategies, manual testing insufficient. Нужна automated verification формальных свойств chunking.
**Проблема**: Regression testing только через golden outputs insufficient.
## Описание возможности
Oracle tests которые verify atomic boundary invariants hold across all configurations и inputs. Automated verification формальных свойств.
**Ключевая идея**: Independent verification что boundaries correct.
## Ценность для пользователя
### Для quality assurance
- Guaranteed correctness
- Formal proof boundaries respected
### Для compliance
- Auditable correctness
- Formal verification reports
### Для development
- Catch bugs early
- Safe refactoring
## Подход к дизайну
### Oracle test algorithm
```
Oracle test:
1. Chunk document
2. Parse с StructureBackend
3. FOR каждой boundary:
Verify не inside atomic block
4. Report violations (expect 0)
```
### Property-based testing
Generate random Markdown, apply oracle test, expect zero violations.
## Параметры конфигурации
```
enable_oracle_checks: булево
По умолчанию: False (только в tests)
oracle_error_mode: строка
"error" | "warn" | "silent"
```
## Output schema
```
Oracle report:
oracle_test_passed: true
chunks_validated: 45
boundaries_checked: 44
atomic_blocks_checked: 12
violations_found: 0
```
## Инварианты
1. **No mutations**: Oracle не мутирует chunking
2. **Performance bounded**: Overhead ≤10%
3. **Detailed reporting**: Violations с context
## Дорожная карта реализации
### Фаза 1: Framework (2 недели)
- Oracle test implementation
- Property-based tests
- CI integration
**Зависимости**: All backends
**Риски**: Low — testing infrastructure
## Критерии успеха
- Pass rate: 100% на test corpus
- Zero false positives
- CI integrated
## Оценка рисков
**Низкий риск**: False positives на edge cases
**Mitigation**: Allowlist legitimate splits, clear docs
## Связанные фичи
- **Parser Backend**: Предоставляет authoritative структуру для валидации
- **All features**: Oracle валидирует корректность всех фич
## Ссылки
- [Индекс дорожной карты](../README.md)
- [Parser Backend](./parser-backend.md)