# Разбиение Oversize Кода (Semantic Code Splitting)
## Метаинформация
- **Конкурентная ценность**: Средняя
- **Влияние на пользователей**: Высокое
- **Сложность реализации**: Средняя
- **Стратегический приоритет**: P1 — Практичность
- **Область**: Токен-семантическое чанкование
## Стратегический контекст
Atomic code blocks часто oversized в token mode. Binary choice (allow oversize vs break atomicity) insufficient. Нужен structure-aware splitting для code blocks.
## Мотивация
Atomic code blocks часто oversized в token mode. Текущие опции:
- **Allow oversize**: Один гигантский chunk → unusable для retrieval
- **Line splitting**: Breaks syntax → invalid code fragments
**Проблема**: Нужен semantic splitting preserving validity.
## Описание возможности
Optionally split large code blocks по semantic units (functions, classes, top-level statements) вместо arbitrary lines. Preserves syntactic validity и semantic coherence.
**Ключевая идея**: Split code по function/class boundaries, не по lines.
## Ценность для пользователя
### Для code retrieval
- Function-level granularity → better relevance
- Syntactically valid chunks → можно execute/analyze
### Для code understanding
- Split по логическим единицам → easier comprehension
- Language context в metadata → syntax highlighting
## Подход к дизайну
### Pluggable splitter interface
```
Интерфейс CodeBlockSplitter:
Метод split(language, code, max_size, sizer) -> список CodePart
```
### Built-in splitters
**HeuristicSplitter**:
- Empty lines (functions separated)
- Comment blocks (section markers)
- Indentation changes
**TreeSitterSplitter** (optional):
- Parse code в AST
- Split на function/class boundaries
- Graceful fallback
## Параметры конфигурации
```
split_oversize_atomic_blocks: булево
По умолчанию: False
code_block_splitter: объект CodeBlockSplitter
По умолчанию: None
code_split_fallback: строка
Значения: "lines" | "hard" | "keep_oversize"
```
## Схема метаданных
```
metadata.code_split:
code_language: "python"
code_split_method: "tree_sitter"
code_split_kind: "function"
needs_fence_open: true
needs_fence_close: true
```
## Инварианты
1. **Default disabled**: Feature off by default
2. **Syntactic validity**: Split parts remain valid code
3. **No fence duplication**: Fences только в renderer
4. **Valid line ranges**: Accurate и non-overlapping
## Дорожная карта реализации
### Фаза 1: Heuristic Splitter (1 неделя)
- Empty line detection
- Comment block detection
- Basic splitting logic
**Зависимости**: Adaptive sizing
**Риски**: Low
### Фаза 2: Tree-sitter (1 неделя)
- AST parsing integration
- Function/class detection
- Fallback logic
**Зависимости**: Фаза 1
**Риски**: Medium — external dependency
## Критерии успеха
- Syntactically valid parts: >90% cases
- Function boundaries: Detected correctly
- Token limit: All parts fit budget
## Оценка рисков
**Средний риск**: Invalid syntax в edge cases
**Mitigation**: Validity checking, fallback, warnings
## Связанные фичи
- **Adaptive Sizing**: Обеспечивает обработку oversize блоков
- **Token-Aware Sizing**: Корректно измеряет размеры частей
## Ссылки
- [Индекс дорожной карты](../README.md)
- [Token-Aware Sizing](./token-aware-sizing.md)