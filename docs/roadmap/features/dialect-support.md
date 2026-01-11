# Поддержка Диалектов Markdown (Dialect Support)

## Метаинформация

- **Конкурентная ценность**: Высокая
- **Влияние на пользователей**: Среднее
- **Сложность реализации**: Средняя
- **Стратегический приоритет**: P2 — Расширяемость
- **Область**: Парсер как источник истины

## Стратегический контекст

Markdown диалекты расширяют syntax (GFM: tables, MyST: directives, front-matter). Heuristics не справляются с расширениями → broken chunks.

## Мотивация

Markdown dialects extend syntax:
- **GFM**: Tables, task lists, strikethrough
- **MyST**: Directives, roles, front-matter
- **Custom**: Enterprise-specific extensions

**Проблема**: Heuristics miss расширения, causing corruption.

## Описание возможности

Configurable dialect presets которые activate appropriate parser plugins и classify новые constructs как atomic or structural.

**Ключевая идея**: Dialect как profile (parser + plugins + rules).

## Ценность для пользователя

### Для GitHub documentation
- GFM tables handled correctly
- Task lists preserved

### Для Sphinx/MyST documentation
- Directives (admonitions) как atomic units
- Front-matter не разрывается

### Для custom platforms
- Pluggable dialect configuration
- No core code changes

## Подход к дизайну

### DialectProfile structure

```
DialectProfile:
  name: строка
  parser_backend: строка
  plugins: список строк
  atomic_block_types: множество строк
```

### Built-in profiles

**commonmark**: Minimal spec-compliant  
**gfm**: Tables, strikethrough, task lists  
**myst**: Directives, roles, front-matter, math  
**custom**: User-provided

## Параметры конфигурации

```
dialect: строка
  "commonmark" | "gfm" | "myst" | "custom"
  По умолчанию: "commonmark"
  
dialect_profile: DialectProfile | None
  Для dialect="custom"
  
dialect_strict_mode: булево
  Error на unsupported constructs
```

## Схема метаданных

```
metadata.dialect:
  dialect: "myst"
  dialect_features_used: ["front_matter", "directive_admonition"]
  atomic_types_preserved: ["code_fence", "myst_directive"]
```

## Инварианты

1. **Default works**: CommonMark без extra dependencies
2. **Algorithm unchanged**: Selection не меняет core
3. **Graceful degradation**: Unsupported features don't crash

## Дорожная карта реализации

### Фаза 1: Profile System (2 недели)
- DialectProfile model
- Built-in profiles (CommonMark, GFM, MyST)
- Plugin integration

**Зависимости**: Markdown-it backend  
**Риски**: Low — configuration-driven

## Критерии успеха

- GFM: Tables не split
- MyST: Directives recognized
- Custom: User rules respected

## Оценка рисков

**Средний риск**: Plugin ecosystem fragmentation  
**Mitigation**: Standardize profile format, version matrix

## Связанные фичи

- **Parser Backend**: Предоставляет механизм для поддержки диалектов
- **Block Provenance**: Получает преимущества от dialect awareness

## Ссылки

- [Индекс дорожной карты](../README.md)
- [Parser Backend](./parser-backend.md)
- [Block Provenance](./block-provenance.md)
