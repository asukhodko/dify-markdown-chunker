# Провенанс блоков (Block-Level Provenance Tracking)
## Метаинформация
- **Конкурентная ценность**: Высокая
- **Влияние на пользователей**: Среднее
- **Сложность реализации**: Средняя
- **Стратегический приоритет**: P1 — Дифференциация
- **Область**: Объяснимое чанкование
## Стратегический контекст
Chunks expose line ranges, но не структурный состав. Operators не могут ответить "какие Markdown-элементы сформировали этот chunk?" без manual inspection. Это создаёт проблемы debugging и quality assurance.
## Мотивация
Chunks в текущей реализации экспонируют line ranges, но не структурный состав. Операторы не могут ответить на вопрос "какие Markdown-элементы сформировали этот чанк?" без ручной инспекции исходного документа.
**Проблемы**:
- Невозможность быстрого дебага решений чанкера
- Отсутствие метрик по распределению типов блоков
- Сложность построения structure-aware retrieval scoring
- Нет поддержки для UI-инструментов chunk inspection
## Описание возможности
Отслеживание типов Markdown-блоков (headings, paragraphs, lists, code fences, tables, blockquotes), которые составляют каждый чанк. Информация о провенансе сохраняется в metadata и доступна для анализа и визуализации.
**Ключевая идея**: Чанк знает из каких block-level units Markdown он собран.
## Ценность для пользователя
### Для разработчиков
- Дебаг решений чанкера: "Этот чанк = 3 параграфа + 1 code block + 1 таблица"
- Метрики качества: распределение типов блоков по чанкам
- Валидация стратегий: проверка, что код не разрывается
### Для операторов RAG-систем
- Quality dashboards с block type distribution
- Быстрая диагностика проблем retrieval
- Мониторинг изменений в распределении типов контента
### Для интеграторов
- Structure-aware retrieval scoring (бустинг чанков с кодом, таблицами)
- UI-driven chunk inspection tools
- Automatic quality checks на провенансе
## Подход к дизайну
### Block Model Layer
Вводится слой анализа Markdown в последовательность типизированных сегментов перед чанкованием.
**Структура Block**:
```
Блок Markdown:
block_index: целое число (0..n-1, порядковый номер в документе)
block_type: строка (Heading | Paragraph | List | CodeFence | Table | Blockquote)
start_line: целое число (1-indexed, inclusive)
end_line: целое число (1-indexed, inclusive)
header_path: строка (формат "/H1/H2")
atomic: булево (можно ли разрывать блок)
```
### Модели провенанса
**Span mode** (компактный):
- Хранит только индексы начального и конечного блока
- Минимальный overhead в metadata
**Full mode** (детальный):
- Хранит полный список блоков с их атрибутами
- Максимальная observability
## Параметры конфигурации
```
Конфигурация провенанса:
extract_blocks: булево (по умолчанию False)
Описание: Включить ли извлечение блочной структуры
include_block_provenance: булево (по умолчанию False)
Описание: Присоединять ли провенанс к metadata чанков
block_provenance_mode: строка ("span" | "full", по умолчанию "span")
Описание: Уровень детализации провенанса
```
## Схема метаданных
**Span mode**:
```
metadata.block_provenance:
block_start: 12
block_end: 18
block_types_summary:
Paragraph: 3
CodeFence: 1
List: 2
```
## Инварианты
1. **Полное покрытие**: Блоки exhaustively покрывают документ без gaps
2. **Отсутствие пересечений**: Блоки никогда не overlap
3. **Alignment границ**: Границы чанков align с block boundaries when possible
4. **Canonical content**: Принцип канонического контента сохраняется
## Дорожная карта реализации
### Фаза 1: Block Model (2-3 недели)
- Block extraction layer
- Provenance metadata (span/full modes)
- Unit tests для block parsing
**Зависимости**: Нет
**Риски**: Medium — parsing complexity
## Критерии успеха
- Block provenance accuracy: 100% на test corpus
- При extract_blocks=False baseline не меняется
- Zero atomic boundary violations с provenance
## Оценка рисков
**Средний риск**: Block model complexity increases maintenance burden
**Mitigation**: Comprehensive oracle tests, gradual rollout
## Связанные фичи
- **Soft/Hard Limits**: Работают лучше с block model для определения естественных границ
- **Parser Backend**: Предоставляет authoritative blocks из парсера
## Ссылки
- [Индекс дорожной карты](../README.md)
- [Soft/Hard Limits](./soft-hard-limits.md)
- [Parser Backend](./parser-backend.md)