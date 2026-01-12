# Адаптивные уровни разбиения (Semantic Split Level Hierarchy)
## Метаинформация
- **Конкурентная ценность**: Очень высокая
- **Влияние на пользователей**: Высокое
- **Сложность реализации**: Высокая
- **Стратегический приоритет**: P1 — Дифференциация
- **Область**: Токен-семантическое чанкование
## Стратегический контекст
Текущие стратегии не имеют formal degradation model. Результаты inconsistent на documents с variable structure density. Нужна формализованная иерархия semantic boundaries с predictable degradation.
## Мотивация
Текущие стратегии не имеют formal degradation model:
- Structural strategy всегда режет по sections
- List strategy всегда режет по items
- Нет automatic adaptation когда preferred level doesn't fit
**Последствия**: Inconsistent boundaries, either large chunks или over-fragmentation.
## Описание возможности
Формализация chunking как multi-level decision process:
1. Try coarse boundaries first (sections)
2. If doesn't fit → degrade к finer boundaries (blocks)
3. Continue degrading до fit (lines, sentences, words)
**Ключевая идея**: Chunking = attempts на каждом level, degradation только when necessary.
## Ценность для пользователя
### Для predictability
- Clear hierarchy объясняет each boundary decision
- Deterministic behaviour across documents
- Stable chunk sizes with natural boundaries
### Для quality
- Maximize semantic coherence within size constraints
- Prefer large units, degrade only when forced
### Для debugging
- Metadata показывает degradation path
- Understand почему chunk закрылся на конкретном level
## Подход к дизайну
### Level hierarchy (от coarse к fine)
```
Level 1 - Section: Heading-delimited regions
Level 2 - Block: Paragraphs, list items, code, tables
Level 3 - Line: Line breaks внутри blocks
Level 4 - Sentence: Sentence boundaries
Level 5 - Word: Word boundaries
Level 6 - Character: Last resort
```
### Degradation algorithm
```
Chunking с degradation:
current_level = configured_start_level
WHILE есть content:
unit = get_next_unit(current_level)
IF current_chunk + unit fits:
Add unit
ELSE IF unit too large:
Degrade к next finer level
ELSE:
Emit current_chunk, start new
```
## Параметры конфигурации
```
split_levels: список строк
По умолчанию: ["section", "block", "line", "sentence", "word", "character"]
start_level: строка
По умолчанию: "section"
level_respect_atomic: словарь
Пример: {"line": false, "sentence": false}
```
## Схема метаданных
```
metadata.split_levels:
split_levels_used: ["section", "block"]
primary_split_level: "section"
degraded_to_level: "block"
degradation_reason: "section_exceeded_max_size"
```
## Инварианты
1. **Coarse-first**: Always attempt coarse levels перед fine
2. **Per-unit decisions**: Degradation per-unit, не globally
3. **Atomic respect**: Atomic blocks respected на всех levels
4. **No infinite loops**: Character level always works
## Дорожная карта реализации
### Фаза 1: Hierarchy Implementation (3 недели)
- Level abstraction
- Degradation algorithm
- BoundaryProvider interface
**Зависимости**: Нет
**Риски**: High — core algorithm change
## Критерии успеха
- Zero infinite loops на all inputs
- Boundary quality: >90% на section/block level
- Metadata accuracy: levels used reported correctly
## Оценка рисков
**Средний риск**: Complexity increases debugging difficulty
**Mitigation**: Extensive metadata logging, visual debugging tools
## Связанные фичи
- **Token-Aware Sizing**: Критично для принятия решений о размерах
- **Unicode Sentence/Word**: Предоставляют fine-grain уровни разбиения
## Ссылки
- [Индекс дорожной карты](../README.md)
- [Token-Aware Sizing](./token-aware-sizing.md)