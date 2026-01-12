# Token-Aware Sizing (Токен-осознанное измерение размера)
## Метаинформация
- **Конкурентная ценность**: Критическая
- **Влияние на пользователей**: Высокое
- **Сложность реализации**: Средняя
- **Стратегический приоритет**: P0 — Фундамент
- **Область**: LLM-нативная точность
## Стратегический контекст
Текущий подход к определению размера на основе символов не соответствует реальности работы LLM: модели потребляют токены, а не символы. Это создаёт production-проблемы: чанки кажутся подходящими по размеру, но переполняют context windows или тратят capacity впустую.
### Проблема несоответствия единиц измерения
**Символы vs токены**: Разница может быть драматической:
- Код: `function calculateTotal` = 25 символов, но ~5-7 токенов
- CJK текст: 中文文本 = 4 символа, но ~8-12 токенов
- Unicode: emoji и спецсимволы имеют непредсказуемое соотношение
**Последствия**:
- Чанки "влезают" по символам, но overflow по токенам → runtime errors
- Чанки слишком малы по токенам → неэффективное использование context window
- Невозможность гарантировать budget compliance
### Конкурентное позиционирование
Token-aware sizing делает Chunkana первым Markdown-чанкером, который:
- Treat token budgets как first-class concern
- Гарантирует budget compliance через pluggable sizing
- Обеспечивает измерение в любых units (chars, bytes, tokens, custom)
## Мотивация
Все размерные решения (max/min/overlap) в текущей реализации используют character count. Это создаёт фундаментальное несоответствие:
- Token counts радикально отличаются от character counts
- Разница зависит от language, content type, encoding
- Пользователи либо "угадывают" размеры, либо пишут external wrappers
## Описание возможности
Абстракция измерения размера за pluggable interface. Поддержка characters, bytes, tokens и custom metrics через единый механизм.
**Ключевая идея**: Все code paths используют один и тот же "размеромер" (sizer), который может измерять в любых units.
## Ценность для пользователя
### Для workflows
- Guarantee chunks ≤ 512 tokens (или любой model limit)
- No trial-and-error с размерами
- Predictable index size
### Для LLM context management
- Accurate utilization context window
- No overflow errors
- Stable batch sizes
### Для custom scenarios
- Cost-per-chunk metrics (based on pricing)
- Semantic density scoring
- Domain-specific measurements
## Подход к дизайну
### Sizer Protocol
```
Интерфейс Sizer:
Метод size(text: строка) -> целое число
Описание: Возвращает размер text в единицах данного sizer
Инвариант: Детерминированный результат для одинакового text
```
### Встроенные реализации
**CharSizer**:
- Текущее поведение: `len(text)`
- Default для backward compatibility
- Zero overhead
**ByteSizer**:
- UTF-8 byte length
- Useful для storage/network constraints
- Slight overhead для encoding
**TokenSizer** (wrapper):
- Обёртка над tokenizer (tiktoken, HuggingFace)
- Измеряет в токенах specific модели
- Требует external tokenizer
**MemoizedSizer** (decorator):
- Кэширует результаты size(text)
- Configurable cache size/eviction
- Critical для performance в token mode
### Интеграция в chunking
```
Механика интеграции:
1. Configuration определяет active sizer
2. Все size comparisons маршрутизируются через sizer
3. Metadata записывает measurement unit и sizer type
4. Validation использует тот же sizer
```
## Параметры конфигурации
```
Конфигурация sizer:
sizer: объект Sizer (runtime-only, не сериализуется)
Описание: Активный измеритель размера
По умолчанию: CharSizer
size_unit: строка ("chars" | "bytes" | "tokens")
Описание: Serializable индикатор единицы измерения
По умолчанию: "chars"
tokenizer_model: строка или None
Описание: Идентификатор модели для token sizing
Примеры: "cl100k_base" (OpenAI), "gpt2", "bert-base"
По умолчанию: None
```
## Схема метаданных
```
metadata.sizing:
content_size: целое число
Описание: Размер canonical content в единицах sizer
size_unit: строка
Описание: Единица измерения ("chars" | "bytes" | "tokens")
sizer_type: строка
Описание: Тип использованного sizer
Примеры: "char", "byte", "tiktoken_cl100k_base", "custom"
prev_overlap_size: целое число
Описание: Размер previous overlap (если есть)
next_overlap_size: целое число
Описание: Размер next overlap (если есть)
Пример (token mode):
content_size: 487
size_unit: "tokens"
sizer_type: "tiktoken_cl100k_base"
prev_overlap_size: 45
next_overlap_size: 50
```
## Инварианты
1. **Default preservation**: CharSizer preserves exact current behaviour
2. **Consistent units**: All code paths используют same sizer (no mixed units)
3. **Determinism**: size(text) детерминирован для same text
4. **No network calls**: Sizing никогда не делает сетевых вызовов
5. **Validation consistency**: Все validations используют configured sizer
## Стратегия тестирования
### Baseline tests
- CharSizer produces identical output к текущему behaviour
- Golden outputs unchanged с default config
### Token mode tests
- Validate chunks stay under token limit
- Test с different tokenizers (tiktoken, HF)
- Stress test: длинный код, CJK text, mixed content
### Performance tests
- Tokenization overhead ≤20% с memoization
- Cache hit rate ≥80% на typical documents
- Memory usage bounded
### Correctness tests
- Unicode handling (emoji, combining characters)
- Edge cases (empty chunks, single-token chunks)
- Boundary conditions (exactly at limit)
## Дорожная карта реализации
### Фаза 1: Core Sizer Architecture (1 неделя)
**Deliverables**:
- ChunkSizer Protocol definition
- CharSizer, ByteSizer implementations
- Configuration integration
- Unit tests
**Зависимости**: Нет
**Риски**: Low — interface definition
### Фаза 2: Token Support (1 неделя)
**Deliverables**:
- TokenSizer wrapper (tiktoken, HF)
- MemoizedSizer decorator
- Token mode integration tests
- Documentation
**Зависимости**: Фаза 1
**Риски**: Medium — external tokenizer integration
### Фаза 3: Performance Optimization (1 неделя)
**Deliverables**:
- Memoization tuning
- Lazy evaluation
- Performance benchmarks
- Optimization documentation
**Зависимости**: Фаза 2
**Риски**: Low — optimization work
## Критерии успеха
### Функциональные метрики
- Token mode: 99.9% chunks within budget
- Default mode (chars): 100% baseline compatibility
- Custom sizer: User-provided callables work correctly
### Performance метрики
- Tokenization overhead: ≤20% с memoization
- Cache hit rate: ≥80% на typical documents
- Memory overhead: ≤10% для cache
### Совместимость
- Default behaviour unchanged
- Golden outputs identical в chars mode
- No breaking changes в public API
## Оценка рисков
### Высокий риск: Tokenization Performance
**Описание**: Tokenization может быть медленной на больших документах
**Severity**: High
**Mitigation**:
- Aggressive memoization (cache результаты)
- Lazy evaluation (tokenize только when needed)
- Batching (tokenize blocks вместе)
- Benchmarking и performance budgets
### Низкий риск: Cache Memory Usage
**Описание**: Memoization cache может consume significant memory
**Severity**: Low
**Mitigation**:
- Configurable cache size limits
- LRU eviction policy
- Per-document cache lifetime
- Memory monitoring
## Связанные фичи
- **Позиционные оффсеты**: Требует consistent size measurement для корректного определения размеров
- **Адаптивное разбиение**: Зависит от sizer для принятия решений о разбиении
- **Budget-Aware Renderers**: Использует sizer для гарантии соответствия бюджету
## Ссылки
- [Индекс дорожной карты](../README.md)
- [Позиционные оффсеты](./positional-offsets.md)
- [Budget-Aware Renderers](./budget-aware-renderers.md)