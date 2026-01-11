# Soft/Hard Лимиты Размера (Dual Threshold Size Control)

## Метаинформация

- **Конкурентная ценность**: Средняя
- **Влияние на пользователей**: Среднее
- **Сложность реализации**: Низкая
- **Стратегический приоритет**: P2 — Качество
- **Область**: Объяснимое чанкование

## Стратегический контекст

Единственный hard limit создаёт неестественные boundaries. Chunks часто close преждевременно или overflow slightly, оба случая снижают качество.

## Мотивация

Единственный hard limit создаёт неестественные границы:
- Преждевременное закрытие → мелкие чанки, фрагментация
- Slight overflow → непредсказуемый размер

**Проблема**: Нужен preferred target size с graceful overflow.

## Описание возможности

Введение **preferred target size** (soft limit) с **maximum ceiling** (hard limit). Чанкер закрывает чанки на естественных границах после достижения soft limit.

**Ключевая идея**: Soft limit = preferred, hard limit = absolute maximum.

## Ценность для пользователя

### Для разработчиков
- Более consistent размеры чанков
- Меньше "barely under" и "barely over" cases

### Для RAG-систем
- Boundaries aligned с document structure
- Более ровные чанки → optimal token utilization

## Подход к дизайну

### Operational model

```
1. Accumulate blocks в chunk
2. If size < min: continue
3. If size >= soft AND < hard: close на next good boundary
4. If size >= hard: close immediately
5. "Good boundary" = block/section/paragraph boundary
```

### Grace margin

Разрешается небольшой overflow за soft limit (10-15%) для завершения logical units.

## Параметры конфигурации

```
soft_max_chunk_size: целое или None
  По умолчанию: None (disabled)
  
soft_max_grace_ratio: вещественное
  По умолчанию: 0.15
  
hard_max_chunk_size: целое
  Existing parameter
```

## Схема метаданных

```
metadata.sizing_info:
  hit_soft_limit: true
  soft_limit_close_reason: "block_boundary"
  final_size: 1850
  soft_max_value: 1800
  grace_used: 50
```

## Инварианты

1. **Hard absolute**: final_size ≤ hard_max ВСЕГДА
2. **Atomic preservation**: Soft never splits atomic blocks
3. **Grace bounded**: Overflow ≤ grace_ratio
4. **Min priority**: min_chunk_size overrides soft

## Дорожная карта реализации

### Фаза 1: Soft Logic (1-2 недели)
- Soft limit checking
- Grace margin implementation
- Good boundary detection

**Зависимости**: Block Model recommended  
**Риски**: Low

## Критерии успеха

- Size variance reduction: ≥30%
- При soft=None baseline unchanged
- Atomic blocks never split

## Оценка рисков

**Низкий риск**: User confusion об exact sizes  
**Mitigation**: Clear documentation, metadata transparency

## Связанные фичи

- **Block Provenance**: Обеспечивает определение хороших границ
- **Token-Aware Sizing**: Работает в любых единицах измерения

## Ссылки

- [Индекс дорожной карты](../README.md)
- [Block Provenance](./block-provenance.md)
- [Token-Aware Sizing](./token-aware-sizing.md)
