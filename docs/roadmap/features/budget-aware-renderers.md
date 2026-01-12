# Budget-Aware Renderers (Гарантированное соблюдение бюджета)
## Метаинформация
- **Конкурентная ценность**: Средняя
- **Влияние на пользователей**: Среднее
- **Сложность реализации**: Средняя
- **Стратегический приоритет**: P2 — Качество
- **Область**: LLM-нативная точность
## Стратегический контекст
Canonical content уже fits в budget (через adaptive sizing). Но при rendering: adding overlap может overflow, including metadata может overflow. Нужны renderers с guaranteed budget compliance.
## Мотивация
Canonical content + metadata overlap может exceed LLM context when combined. Нужна guaranteed budget compliance на rendering stage.
**Проблема**: Overlap + content может не fit в budget even если content alone fits.
## Описание возможности
Renderers которые accept budget parameter и guarantee output ≤ budget через intelligent trimming overlap while preserving core content.
**Ключевая идея**: Renderer — pure function, гарантирует size ≤ budget.
## Ценность для пользователя
### Для LLM integration
- Never exceed context window
- Automatic overlap adjustment
- Explicit signaling когда trimming
### Для
- Tight budget compliance для models
- Configurable prev/next balance
### Для monitoring
- Truncation flags для quality metrics
- Track когда budgets tight
## Подход к дизайну
### Renderer algorithm
```
render_with_budget(chunk, budget, sizer):
1. Measure core content
2. If core > budget: truncate content, flag
3. Calculate remaining budget
4. Allocate к prev/next overlap
5. Trim overlaps если не fit
6. Return view + flags
```
## Параметры конфигурации
```
budget: целое (обязательный)
Maximum output size в sizer units
overlap_allocation: строка
"symmetric" | "prev_priority" | "next_priority"
truncation_policy: строка
"trim_overlap" | "trim_content" | "error"
```
## Output schema
```
Rendered output:
rendered_text: "..."
actual_size: 480
budget: 512
trimmed_prev_overlap: true
trimmed_next_overlap: false
trimmed_content: false
```
## Инварианты
1. **No mutation**: Renderer never mutates Chunk
2. **Strict budget**: output ≤ budget (always)
3. **Content priority**: Content trimmed only if overlap eliminated
4. **Flag accuracy**: Truncation flags accurate
## Дорожная карта реализации
### Фаза 1: Core Renderer (2 недели)
- render_with_budget function
- Overlap allocation strategies
- Truncation handling
**Зависимости**: Sizer, split tracking
**Риски**: Low — isolated layer
## Критерии успеха
- Budget compliance: 100% (output ≤ budget)
- Content preserved: Trimmed only as last resort
- Token mode: Works correctly с tokenizers
## Оценка рисков
**Низкий риск**: Minimal — well-scoped functionality
**Mitigation**: Comprehensive tests
## Связанные фичи
- **Token-Aware Sizing**: Предоставляет sizer для измерения
- **Adaptive Sizing**: Гарантирует, что контент вмещается
## Ссылки
- [Индекс дорожной карты](../README.md)
- [Token-Aware Sizing](./token-aware-sizing.md)