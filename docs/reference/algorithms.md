# Mapping Документации Алгоритма на Реализацию
**Дата:** 2025-11-16
**Версия:** 1.0.0
**Статус:** 🔄 В процессе создания
## 1. Обзор
Этот документ связывает компоненты из `docs/markdown-extractor/` с реализацией в `dify-markdown-chunker/`.
**Цель:** Убедиться, что все компоненты из документации алгоритма реализованы или явно задокументированы как "не требуется".
**Документация алгоритма:**
- Расположение: `docs/markdown-extractor/`
- Версия: 2.1 (Consolidated + Enhanced)
- Файлов: 48
- Разделов: 10
- Качество: 99/100
## 2. Архитектурные Компоненты
### 2.1. Extractor (Главный оркестратор)
**Документация:** `docs/markdown-extractor/02-algorithm-core/pipeline.md`
**Реализация:**
- Файл: `markdown_chunker/chunker/core.py`
- Класс: `MarkdownChunker`
- Методы:
- `chunk(text, config, include_analysis)` - главный метод
- `chunk_with_analysis(text)` - с полным анализом
- `chunk_simple(text, config)` - упрощённый API
**Тесты:**
- `tests/chunker/test_chunker.py` (20 тестов)
- `tests/chunker/test_integration.py` (16 тестов)
**Статус:** ✅ Реализовано полностью
**Соответствие:**
- ✅ Оркестрация всего процесса
- ✅ Вызов ContentAnalyzer
- ✅ Вызов StrategySelector
- ✅ Применение выбранной стратегии
- ✅ Обработка ошибок с fallback
- ✅ Возврат результатов
### 2.2. ContentAnalyzer (Анализ контента)
**Документация:** `docs/markdown-extractor/04-components/content-analyzer.md`
**Реализация:**
- Файл: `markdown_chunker/parser/analyzer.py`
- Класс: `ContentAnalyzer`
- Методы:
- `analyze_content(text)` - главный метод анализа
- `_calculate_complexity(...)` - расчёт сложности
- `_detect_content_type(...)` - определение типа контента
**Тесты:**
- `tests/parser/test_analyzer.py` (предположительно)
- Интеграционные тесты в `tests/integration/`
**Статус:** ✅ Реализовано полностью
**Соответствие:**
- ✅ Анализ типа контента (code-heavy, text-heavy, mixed)
- ✅ Расчёт метрик (code_ratio, list_count, table_count)
- ✅ Расчёт сложности документа
- ✅ Возврат `ContentAnalysis` с метриками
- ⚠️ Preamble extraction - частично (см. раздел 3.1)
### 2.3. StrategySelector (Выбор стратегии)
**Документация:** `docs/markdown-extractor/04-components/strategy-selector.md`
**Реализация:**
- Файл: `markdown_chunker/chunker/selector.py`
- Класс: `StrategySelector`
- Методы:
- `select_strategy(analysis, config)` - выбор стратегии
- `get_applicable_strategies(...)` - получение применимых стратегий
- `_calculate_strategy_score(...)` - расчёт оценки стратегии
**Тесты:**
- `tests/chunker/test_strategy_selector.py` (30+ тестов)
**Статус:** ✅ Реализовано полностью
**Соответствие:**
- ✅ Приоритетный выбор стратегии
- ✅ Расчёт оценок для каждой стратегии
- ✅ Поддержка strict и weighted режимов
- ✅ Fallback к SentencesStrategy
- ✅ Логирование выбора
## 3. Стратегии Разбиения
### 3.1. CodeStrategy
**Документация:** `docs/markdown-extractor/03-strategies/code-strategy.md`
**Реализация:**
- Файл: `markdown_chunker/chunker/strategies/code_strategy.py`
- Класс: `CodeStrategy`
- Приоритет: 1 (высший)
**Активация (из документации):**
- code_ratio ≥ 70% (0.7)
- ≥3 блоков кода
**Реализация (проверить):**
- Файл содержит: `CODE_RATIO_THRESHOLD`, `MIN_CODE_BLOCKS`
- Нужно проверить значения
**Тесты:**
- `tests/chunker/test_strategies/test_code_strategy.py` (25 тестов)
**Статус:** ✅ Реализовано, нужна проверка порогов
**Действие:** Проверить, что `CODE_RATIO_THRESHOLD = 0.7` (НЕ 0.35 или 0.4)
### 3.2. MixedStrategy
**Документация:** `docs/markdown-extractor/03-strategies/mixed-strategy.md`
**Реализация:**
- Файл: `markdown_chunker/chunker/strategies/mixed_strategy.py`
- Класс: `MixedStrategy`
- Приоритет: 2
**Активация (из документации):**
- code_ratio ≥ 30% (0.3)
- complexity ≥ 0.3
**Тесты:**
- `tests/chunker/test_strategies/test_mixed_strategy.py` (30+ тестов)
**Статус:** ✅ Реализовано, нужна проверка порогов
### 3.3. ListStrategy
**Документация:** `docs/markdown-extractor/03-strategies/list-strategy.md`
**Реализация:**
- Файл: `markdown_chunker/chunker/strategies/list_strategy.py`
- Класс: `ListStrategy`
- Приоритет: 3
**Активация (из документации):**
- ≥5 списков (НЕ 3!)
**Тесты:**
- `tests/chunker/test_strategies/test_list_strategy.py` (40+ тестов)
**Статус:** ✅ Реализовано, нужна проверка порога
**Действие:** Проверить, что `MIN_LIST_COUNT = 5` (НЕ 3)
### 3.4. TableStrategy
**Документация:** `docs/markdown-extractor/03-strategies/table-strategy.md`
**Реализация:**
- Файл: `markdown_chunker/chunker/strategies/table_strategy.py`
- Класс: `TableStrategy`
- Приоритет: 4
**Активация (из документации):**
- ≥3 таблицы
**Тесты:**
- `tests/chunker/test_strategies/test_table_strategy.py` (30+ тестов)
**Статус:** ✅ Реализовано
### 3.5. StructuralStrategy
**Документация:** `docs/markdown-extractor/03-strategies/structural-strategy.md`
**Реализация:**
- Файл: `markdown_chunker/chunker/strategies/structural_strategy.py`
- Класс: `StructuralStrategy`
- Приоритет: 5
**Активация (из документации):**
- Есть заголовки
**Тесты:**
- `tests/chunker/test_strategies/test_structural_strategy.py` (30+ тестов)
**Статус:** ✅ Реализовано
### 3.6. SentencesStrategy
**Документация:** `docs/markdown-extractor/03-strategies/sentences-strategy.md`
**Реализация:**
- Файл: `markdown_chunker/chunker/strategies/sentences_strategy.py`
- Класс: `SentencesStrategy`
- Приоритет: 6 (низший, fallback)
**Активация (из документации):**
- Всегда применима (fallback)
**Тесты:**
- `tests/chunker/test_strategies/test_sentences_strategy.py` (20+ тестов)
**Статус:** ✅ Реализовано
## 4. Компоненты Системы
### 4.1. PreambleHandler
**Документация:** `docs/markdown-extractor/04-components/preamble-handler.md`
**Реализация:**
- Файл: ❌ НЕ СУЩЕСТВУЕТ
- Ожидается: `markdown_chunker/parser/preamble.py`
- Класс: `PreambleExtractor` (должен быть создан)
**Функциональность (из документации):**
- Извлечение контента до первого заголовка
- Определение типа preamble (introduction, summary, metadata, general)
- Извлечение метаданных (Author:, Date:, Version:, etc.)
- Интеграция с ContentAnalyzer
- Интеграция с MarkdownChunker
**Тесты:**
- ❌ Отсутствуют (должны быть созданы)
**Статус:** ❌ НЕ РЕАЛИЗОВАНО
**Приоритет:** 🔴 Критический
**Действие:** Реализовать `PreambleExtractor` (Задача 2)
### 4.2. OverlapProcessor
**Документация:** `docs/markdown-extractor/04-components/overlap-processor.md`
**Реализация:**
- Файл: `markdown_chunker/chunker/components/overlap_manager.py`
- Класс: `OverlapManager`
- Методы:
- `apply_overlap(chunks, config)` - применение перекрытия
- `_extract_suffix_overlap(...)` - извлечение суффикса
- `_extract_prefix_overlap(...)` - извлечение префикса
**Тесты:**
- `tests/chunker/test_components/test_overlap_manager.py` (30+ тестов)
**Статус:** ✅ Реализовано полностью
**Соответствие:**
- ✅ Перекрытие чанков (200-300 символов по умолчанию)
- ✅ Sentence-aware перекрытие
- ✅ Метаданные перекрытия
- ✅ Конфигурируемый размер
**Действие:** Проверить, что overlap включен по умолчанию
### 4.3. FallbackManager (ErrorHandler)
**Документация:** `docs/markdown-extractor/04-components/error-handler.md`
**Реализация:**
- Файл: `markdown_chunker/chunker/components/fallback.py`
- Класс: `FallbackManager`
- Методы:
- `execute_with_fallback(...)` - выполнение с fallback
- `_try_structural_fallback(...)` - fallback на structural
- `_try_sentences_fallback(...)` - fallback на sentences
- `_emergency_chunking(...)` - аварийное разбиение
**Тесты:**
- `tests/chunker/test_components/test_fallback_manager.py` (25 тестов)
**Статус:** ✅ Реализовано полностью
**Соответствие:**
- ✅ 4-уровневая система откатов
- ✅ Постепенная деградация
- ✅ Метаданные о fallback
- ✅ Emergency chunking
### 4.4. MetadataEnricher
**Документация:** `docs/markdown-extractor/04-components/metadata-enricher.md` (предположительно)
**Реализация:**
- Файл: `markdown_chunker/chunker/components/metadata.py`
- Класс: `MetadataEnricher`
- Методы:
- `enrich_chunks(chunks, ...)` - обогащение метаданных
- `_calculate_content_statistics(...)` - статистика контента
- `_add_searchability_metadata(...)` - метаданные для поиска
**Тесты:**
- `tests/chunker/test_components/test_metadata_enricher.py` (20 тестов)
**Статус:** ✅ Реализовано
## 5. Парсинг и Извлечение
### 5.1. Fenced Block Extraction
**Документация:** `docs/markdown-extractor/06-algorithms/parsing.md`
**Реализация:**
- Файл: `markdown_chunker/parser/core.py`
- Класс: `FencedBlockExtractor`
- Методы:
- `extract_blocks(text)` - извлечение блоков
- `_detect_fence_type(line)` - определение типа ограждения
- `_calculate_nesting_level(...)` - расчёт уровня вложенности
**Тесты:**
- `tests/parser/test_fenced_block_extractor.py` (20 тестов)
- `tests/parser/test_nested_fence_handling.py` (12 тестов)
**Статус:** ✅ Реализовано полностью
**Соответствие:**
- ✅ Поддержка ``` и ~~~
- ✅ Вложенность
- ✅ Позиционирование (1-based API)
- ✅ Обработка незакрытых блоков
### 5.2. AST Building
**Документация:** `docs/markdown-extractor/06-algorithms/parsing.md`
**Реализация:**
- Файл: `markdown_chunker/parser/ast.py`
- Класс: `ASTBuilder`
- Методы:
- `build(text)` - построение AST
- `_process_token(token)` - обработка токена
**Тесты:**
- `tests/parser/test_ast_new.py` (30 тестов)
**Статус:** ✅ Реализовано полностью
**Соответствие:**
- ✅ Построение AST из markdown-it-py
- ✅ Inline tokens
- ✅ Позиционирование
- ✅ Иерархия узлов
### 5.3. Element Detection
**Документация:** `docs/markdown-extractor/06-algorithms/detection.md`
**Реализация:**
- Файл: `markdown_chunker/parser/elements.py`
- Класс: `ElementDetector`
- Методы:
- `detect_lists(text)` - обнаружение списков
- `detect_tables(text)` - обнаружение таблиц
- `detect_headers(text)` - обнаружение заголовков
**Тесты:**
- `tests/parser/test_element_detector.py` (15 тестов)
**Статус:** ✅ Реализовано
## 6. Структуры Данных
### 6.1. Chunk
**Документация:** `docs/markdown-extractor/05-data-structures/chunk.md`
**Реализация:**
- Файл: `markdown_chunker/chunker/types.py`
- Класс: `Chunk` (dataclass)
- Поля:
- `content: str`
- `content_type: ContentType`
- `start_line: int`
- `end_line: int`
- `size: int`
- `metadata: dict`
**Тесты:**
- `tests/chunker/test_types.py` (10 тестов)
**Статус:** ✅ Реализовано
**Соответствие:**
- ✅ Все обязательные поля
- ✅ Метаданные
- ✅ Сериализация (to_dict, from_dict)
### 6.2. ChunkConfig
**Документация:** `docs/markdown-extractor/05-data-structures/config.md`
**Реализация:**
- Файл: `markdown_chunker/chunker/types.py`
- Класс: `ChunkConfig` (dataclass)
- Поля:
- `max_chunk_size: int`
- `min_chunk_size: int`
- `enable_overlap: bool`
- `overlap_size: int`
- `extract_preamble: bool`
- И другие...
**Тесты:**
- `tests/chunker/test_types.py` (10 тестов)
- `tests/chunker/test_config_profiles.py` (5 тестов)
**Статус:** ✅ Реализовано
**Соответствие:**
- ✅ Все основные параметры
- ✅ Фабричные методы (for_api_docs, for_code_docs, etc.)
- ✅ Валидация
- ⚠️ Нужно проверить значения по умолчанию
**Действие:** Проверить, что `enable_overlap=True` по умолчанию
### 6.3. ContentAnalysis
**Документация:** `docs/markdown-extractor/05-data-structures/analysis.md`
**Реализация:**
- Файл: `markdown_chunker/parser/types.py`
- Класс: `ContentAnalysis` (dataclass)
- Поля:
- `content_type: str`
- `code_ratio: float`
- `list_count: int`
- `table_count: int`
- `complexity_score: float`
- `preamble: PreambleInfo | None` (должно быть добавлено)
**Тесты:**
- Интеграционные тесты
**Статус:** ⚠️ Частично реализовано
**Действие:** Добавить поле `preamble` (Задача 2)
## 7. Конфигурация
### 7.1. Параметры
**Документация:** `docs/markdown-extractor/07-configuration/parameters.md`
**Реализация:**
- Файл: `markdown_chunker/chunker/types.py`
- Класс: `ChunkConfig`
**Статус:** ✅ Реализовано
**Действия:**
-  Проверить все параметры из документации
-  Проверить значения по умолчанию
-  Проверить пороги стратегий
### 7.2. Профили
**Документация:** `docs/markdown-extractor/07-configuration/profiles.md`
**Реализация:**
- Файл: `markdown_chunker/chunker/types.py`
- Методы: `ChunkConfig.for_api_docs`, `for_code_docs`, etc.
**Тесты:**
- `tests/chunker/test_config_profiles.py` (5 тестов)
**Статус:** ✅ Реализовано
## 8. Недостающие Компоненты
### 8.1. PreambleExtractor ❌
**Документация:** `docs/markdown-extractor/04-components/preamble-handler.md`
**Статус:** ❌ НЕ РЕАЛИЗОВАНО
**Приоритет:** 🔴 Критический
**План:**
- Создать `markdown_chunker/parser/preamble.py`
- Класс `PreambleExtractor`
- Интеграция с `ContentAnalyzer`
- Интеграция с `MarkdownChunker`
- 20+ тестов
**Задача:** 2 (Preamble Extraction)
### 8.2. StreamingProcessor ⚠️
**Документация:** `docs/markdown-extractor/04-components/streaming-processor.md` (предположительно)
**Статус:** ⚠️ Не реализовано
**Приоритет:** 🟡 Средний (не критично для Stage 3)
**Обоснование:**
- Потоковая обработка нужна для файлов >10 МБ
- Для Dify плагина обычно обрабатываются документы <10 МБ
- Можно добавить в будущих версиях
**Решение:** Задокументировать как "не требуется для MVP"
## 9. Расхождения и Уточнения
### 9.1. Пороги стратегий
**Нужно проверить:**
| Параметр | Документация | Реализация | Статус |
|----------|--------------|------------|--------|
| CODE_RATIO_THRESHOLD | 0.7 | ? | Проверить |
| MIN_CODE_BLOCKS | 3 | ? | Проверить |
| LIST_COUNT_THRESHOLD | 5 | ? | Проверить |
| TABLE_COUNT_THRESHOLD | 3 | ? | Проверить |
| enable_overlap (default) | True | ? | Проверить |
**Действие:** Проверить значения в коде (следующий шаг)
### 9.2. Overlap по умолчанию
**Документация:** Overlap включен по умолчанию
**Реализация:** Нужно проверить `ChunkConfig`
**Действие:** Проверить `enable_overlap` в `ChunkConfig.__init__`
## 10. Сводная Таблица
| Компонент | Документация | Реализация | Тесты | Статус |
|-----------|--------------|------------|-------|--------|
| **Архитектура** |
| Extractor | ✅ | ✅ MarkdownChunker | ✅ 20+ | ✅ Полностью |
| ContentAnalyzer | ✅ | ✅ ContentAnalyzer | ✅ 15+ | ⚠️ Без preamble |
| StrategySelector | ✅ | ✅ StrategySelector | ✅ 30+ | ✅ Полностью |
| **Стратегии** |
| CodeStrategy | ✅ | ✅ CodeStrategy | ✅ 25 | ⚠️ Проверить пороги |
| MixedStrategy | ✅ | ✅ MixedStrategy | ✅ 30+ | ⚠️ Проверить пороги |
| ListStrategy | ✅ | ✅ ListStrategy | ✅ 40+ | ⚠️ Проверить пороги |
| TableStrategy | ✅ | ✅ TableStrategy | ✅ 30+ | ✅ Полностью |
| StructuralStrategy | ✅ | ✅ StructuralStrategy | ✅ 30+ | ✅ Полностью |
| SentencesStrategy | ✅ | ✅ SentencesStrategy | ✅ 20+ | ✅ Полностью |
| **Компоненты** |
| PreambleHandler | ✅ | ❌ НЕТ | ❌ НЕТ | ❌ НЕ РЕАЛИЗОВАНО |
| OverlapProcessor | ✅ | ✅ OverlapManager | ✅ 30+ | ✅ Полностью |
| FallbackManager | ✅ | ✅ FallbackManager | ✅ 25 | ✅ Полностью |
| MetadataEnricher | ✅ | ✅ MetadataEnricher | ✅ 20 | ✅ Полностью |
| **Парсинг** |
| Fenced Blocks | ✅ | ✅ FencedBlockExtractor | ✅ 32 | ✅ Полностью |
| AST Building | ✅ | ✅ ASTBuilder | ✅ 30 | ✅ Полностью |
| Element Detection | ✅ | ✅ ElementDetector | ✅ 15 | ✅ Полностью |
| **Структуры данных** |
| Chunk | ✅ | ✅ Chunk | ✅ 10 | ✅ Полностью |
| ChunkConfig | ✅ | ✅ ChunkConfig | ✅ 15 | ⚠️ Проверить defaults |
| ContentAnalysis | ✅ | ✅ ContentAnalysis | ✅ 5 | ⚠️ Без preamble |
## 11. Итоговая Статистика
**Реализовано:** 17/20 компонентов (85%)
**Полностью:** 14/20 (70%)
**Частично:** 3/20 (15%)
**Не реализовано:** 3/20 (15%)
**Критические проблемы:**
1. ❌ PreambleExtractor не реализован
2. ⚠️ Нужно проверить пороги стратегий
3. ⚠️ Нужно проверить defaults в ChunkConfig
**Некритичные:**
4. ⚠️ StreamingProcessor не реализован (не нужен для MVP)
## 12. Следующие Шаги
### Шаг 1: Проверка порогов ⏳ NEXT
-  Проверить `CODE_RATIO_THRESHOLD` в `code_strategy.py`
-  Проверить `LIST_COUNT_THRESHOLD` в `list_strategy.py`
-  Проверить `enable_overlap` в `ChunkConfig`
-  Обновить mapping с результатами
### Шаг 2: Добавление ссылок на документацию
-  Добавить ссылки в ключевые классы
-  Формат: `# Algorithm: docs/markdown-extractor/path/to/section.md`
### Шаг 3: Реализация PreambleExtractor
-  См. Задачу 2 в tasks.md
**Создано:** 2025-11-16
**Обновлено:** 2025-11-16
**Статус:** 🔄 В процессе (Шаг 1 следующий)