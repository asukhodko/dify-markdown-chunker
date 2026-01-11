# Позиционные оффсеты (Character и Byte Ranges)

## Метаинформация

- **Конкурентная ценность**: Высокая
- **Влияние на пользователей**: Высокое
- **Сложность реализации**: Низкая
- **Стратегический приоритет**: P0 — Фундамент
- **Область**: LLM-нативная точность

## Стратегический контекст

Line numbers недостаточно для многих производственных сценариев. Требуется точная позиционная информация для UI highlighting, deduplication, source attribution и обработки нормализованного текста.

### Проблема line-only addressing

**Ограничения line numbers**:
- Нет pixel-perfect highlighting в editors
- Невозможность deduplication по byte ranges
- Проблемы с CRLF→LF normalization
- Нет exact position для deep linking

**Последствия**:
- UI highlighting приблизительный
- Deduplication требует re-parsing
- Source attribution неточный
- Version tracking затруднён

## Мотивация

Line numbers недостаточно для точной атрибуции источников. Современные сценарии требуют:
- **UI highlighting**: Pixel-perfect подсветка в editors
- **Deduplication**: Byte ranges для detect duplicates
- **Normalization handling**: Корректная работа с CRLF↔LF
- **Source attribution**: Exact position для citations

## Описание возможности

Emit character (Unicode code point) и byte (UTF-8) offsets для каждого chunk как half-open ranges `[start, end)`. Offsets позволяют точно восстановить chunk из original text через slicing.

**Ключевая идея**: Дополнить line numbers точными offsets для character и byte позиций.

## Ценность для пользователя

### Для UI/visualization
- Pixel-perfect highlighting в editors
- Scroll-to-chunk functionality
- Visual diff между versions

### Для data processing
- Deduplication based на byte ranges
- Incremental updates (re-chunk только changed ranges)
- Content-addressable storage

### Для source attribution
- Exact citations с character-level precision
- Deep linking в documents
- Audit trails для compliance

## Подход к дизайну

### Precomputation strategy

```
Алгоритм вычисления оффсетов:
  1. Parse документа: build line_start_offsets tables
     - line_start_char: массив character offsets для начала каждой строки
     - line_start_byte: массив byte offsets для начала каждой строки
     
  2. При формировании chunk:
     - Lookup start_line в tables → получить start offsets
     - Lookup end_line в tables → получить end offsets
     - Записать в metadata
     
  3. Время: O(n) для parsing, O(1) для каждого chunk
```

### Normalization handling

- Документировать какой text является reference (pre/post normalization)
- Offsets относятся к тому text, который реально chunked
- Optional metadata: какая normalization applied

### Invariant guarantee

```
Гарантия восстановления:
  text[chunk.start_char : chunk.end_char] == chunk.content
  text.encode('utf-8')[chunk.start_byte : chunk.end_byte].decode('utf-8') == chunk.content
```

## Параметры конфигурации

```
Конфигурация offsets:
  include_char_offsets: булево (по умолчанию False)
    Описание: Emit character offsets в metadata
    
  include_byte_offsets: булево (по умолчанию False)
    Описание: Emit byte offsets в metadata
    
  offset_normalization: строка ("none" | "crlf_to_lf")
    Описание: Declare какая normalization applied к source text
    По умолчанию: "none"
```

## Схема метаданных

```
metadata.offsets:
  start_char: целое число
    Описание: Character offset начала chunk (0-indexed, inclusive)
    
  end_char: целое число
    Описание: Character offset конца chunk (0-indexed, exclusive)
    
  start_byte: целое число
    Описание: Byte offset начала chunk (0-indexed, inclusive)
    
  end_byte: целое число
    Описание: Byte offset конца chunk (0-indexed, exclusive)
    
  offset_base: строка
    Описание: Reference text для offsets
    Значения: "original" | "crlf_normalized" | "custom"

Пример:
  start_char: 1250
  end_char: 2890
  start_byte: 1340
  end_byte: 3120
  offset_base: "crlf_normalized"
```

## Инварианты

1. **Roundtrip correctness**: Text slicing восстанавливает chunk content
2. **Monotonicity**: Offsets монотонно возрастают across chunks
3. **No gaps**: Chunks exhaustively покрывают document (no gaps в offsets)
4. **No overlaps**: Offset ranges не overlap (except metadata overlap)

## Стратегия тестирования

### Unicode tests
- Emoji (multi-byte, multi-codepoint)
- Combining characters
- CJK text
- Right-to-left scripts

### Normalization tests
- CRLF input: offsets valid after LF normalization
- Mixed line endings: handled correctly
- Trailing whitespace: preserved или stripped correctly

### Roundtrip tests
- Recover all chunks via offsets
- Verify no gaps, no overlaps
- Edge cases: empty chunks, single-char chunks

## Дорожная карта реализации

### Фаза 1: Offset Tables (1 неделя)
**Deliverables**:
- Line-start offset computation
- Character и byte tables
- Integration в parsing
- Unit tests

**Зависимости**: Нет

**Риски**: Low — straightforward computation

### Фаза 2: Metadata Integration (1 неделя)
**Deliverables**:
- Offset fields в metadata
- Configuration options
- Normalization handling
- Documentation

**Зависимости**: Фаза 1

**Риски**: Low — metadata extension

## Критерии успеха

### Функциональные метрики
- Roundtrip accuracy: 100% text recovery от offsets
- Unicode correctness: All scripts handled
- Normalization: CRLF handling correct

### Performance метрики
- Offset computation overhead: ≤5% vs current
- Memory overhead: O(n) для tables (acceptable)
- Lookup time: O(1) per chunk

### Совместимость
- Optional feature (disabled by default)
- No impact when disabled
- Backward compatible metadata

## Оценка рисков

### Низкий риск: Unicode Edge Cases

**Описание**: Редкие Unicode sequences могут вызвать проблемы

**Severity**: Low

**Mitigation**:
- Comprehensive Unicode test suite
- Fuzzing с random Unicode
- Clear documentation edge cases

## Связанные фичи

- **Token-Aware Sizing**: Compatible с любыми units измерения
- **Split Tracking**: Offsets критичны для parent-child relationships при разбиении
- **Deduplication**: Byte ranges обеспечивают эффективную дедупликацию

## Ссылки

- [Индекс дорожной карты](../README.md)
- [Token-Aware Sizing](./token-aware-sizing.md)
