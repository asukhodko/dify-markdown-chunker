# Parser Backend (Structural Backend Abstraction)
## Метаинформация
- **Конкурентная ценность**: Высокая
- **Влияние на пользователей**: Среднее
- **Сложность реализации**: Высокая
- **Стратегический приоритет**: P1 — Дифференциация
- **Область**: Парсер как источник истины
## Стратегический контекст
Hardcoded эвристики ограничивают extensibility и корректность. Heuristic line-based analysis работает для clean Markdown, но fails на complex structures: nested lists, blockquotes, dialect extensions.
## Мотивация
Hardcoded эвристики ограничивают extensibility. Нужен pluggable механизм boundary detection для поддержки both heuristic (fast) и parser-based (correct) modes.
**Проблемы**:
- Эвристики вшиты в core
- Нет способа добавить alternative backend
- Нет formal correctness guarantees
## Описание возможности
Абстрагировать "как мы определяем Markdown structure" за interface. Поддержка heuristic (current) и parser-based (new) backends через единый механизм.
**Ключевая идея**: Chunking работает с DocumentStructure (blocks + headings), не с raw lines.
## Ценность для пользователя
### Для разработчиков
- Choose correctness (parser) vs speed (heuristic)
- A/B test backend performance/quality
### Для platforms
- Eliminate false boundaries в complex Markdown
- Support dialect-specific extensions
### Для quality assurance
- Formal correctness guarantees
- Oracle tests для automated verification
## Подход к дизайну
### StructureBackend Protocol
```
Интерфейс StructureBackend:
Метод analyze(text) -> DocumentStructure
Возвращает: blocks, headings, metadata
```
### Backend implementations
**NativeBackend**:
- Wraps текущие heuristics
- Preserves exact current behaviour
**MarkdownItBackend**:
- Uses markdown-it-py token stream
- Provides formal correctness
## Параметры конфигурации
```
structure_backend: строка
Значения: "native" | "markdown_it" | "custom"
По умолчанию: "native"
fallback_on_backend_error: булево
По умолчанию: True
```
## Схема метаданных
```
metadata.structure_backend:
backend: "markdown_it"
backend_version: "3.0.0"
parse_time_ms: 45
block_count: 127
fallback_used: false
```
## Инварианты
1. **Full coverage**: Blocks exhaustively cover document
2. **No overlaps**: Blocks never overlap
3. **Native preservation**: NativeBackend = current behaviour
4. **Fallback safety**: Parser errors don't crash
## Дорожная карта реализации
### Фаза 1: Abstraction (2 недели)
- StructureBackend Protocol
- NativeBackend wrapper
- Integration
**Зависимости**: Нет
**Риски**: Low — refactoring
### Фаза 2: Markdown-it (3 недели)
- MarkdownItBackend implementation
- Token-to-block mapping
- Fallback logic
**Зависимости**: Фаза 1
**Риски**: Medium — external library
## Критерии успеха
- Native backend: 100% baseline match
- Parser mode: Zero atomic violations
- Fallback: Graceful на parser errors
## Оценка рисков
**Средний риск**: Parser performance на large documents
**Mitigation**: Performance budgets, timeout mechanism
## Связанные фичи
- **Dialect Support**: Использует parser plugins для поддержки разных диалектов
- **Oracle Testing**: Валидирует корректность границ
## Ссылки
- [Индекс дорожной карты](../README.md)
- [Dialect Support](./dialect-support.md)
- [Oracle Testing](./oracle-testing.md)