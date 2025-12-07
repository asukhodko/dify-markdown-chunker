# Roadmap v2.1: Возможности для улучшения markdown_chunker_v2

## Краткое резюме

На основе комплексного исследования (анализ конкурентов, потребности пользователей, тестовый корпус) определены 15 ключевых возможностей для достижения статуса "top-1 candidate" в области markdown chunking для RAG-систем.

**Ключевые выводы:**
- Текущее состояние: markdown_chunker_v2 уже имеет конкурентные преимущества в code-aware chunking и automatic strategy selection
- Главный gap: Удаление List Strategy при переходе на v2.0 — затрагивает 20-25% документов
- Уникальная возможность: Nested fencing support — ни один конкурент не обрабатывает это корректно
- Путь к лидерству: 15 улучшений за 6 месяцев

---

## Обзор фаз

| Фаза | Период | Цель | Кол-во фич |
|------|--------|------|------------|
| 1 | Месяц 1-2 | Восстановление функциональности + уникальные возможности | 3 |
| 2 | Месяц 2-3 | Семантика и интеграция с LLM | 3 |
| 3 | Месяц 3-4 | Интеграция и adoption | 4 |
| 4 | Месяц 4-5 | Продвинутые возможности | 3 |
| 5 | Месяц 5-6 | Производительность и полировка | 2 |

---

## Фаза 1: Восстановление ядра и уникальные возможности (Месяц 1-2)

**Цель:** Восстановить потерянную функциональность и занять уникальную позицию на рынке

| # | Фича | Приоритет | Effort | Уникальность |
|---|------|-----------|--------|--------------|
| 1.1 | Smart List Strategy | CRITICAL | 5-7 дней | Partial |
| 1.2 | Nested Fencing Support | CRITICAL | 3-5 дней | **YES** |
| 1.3 | List Detection в Parser | HIGH | 2-3 дня | No |

### 1.1 Smart List Strategy
Восстановление стратегии для list-heavy документов (changelogs, feature lists, outlines).
- **Проблема:** List Strategy удалена в v2.0, затрагивает 20-25% документов
- **Польза:** SCS для list-heavy docs: +25%, CPS: +15%
- **Детали:** [01-smart-list-strategy.md](./features/01-smart-list-strategy.md)

### 1.2 Nested Fencing Support
Поддержка вложенных code blocks (````, ~~~~~).
- **Проблема:** Ни один конкурент не обрабатывает корректно
- **Польза:** Уникальный дифференциатор, критично для documentation templates
- **Детали:** [02-nested-fencing-support.md](./features/02-nested-fencing-support.md)

### 1.3 List Detection в Parser
Добавление извлечения информации о списках в парсер.
- **Проблема:** Парсер не извлекает list block информацию
- **Польза:** Необходимо для List Strategy, улучшает анализ контента
- **Детали:** [03-list-detection-parser.md](./features/03-list-detection-parser.md)

---

## Фаза 2: Семантические и Token-Aware возможности (Месяц 2-3)

**Цель:** Значительное улучшение качества для интеграции с LLM

| # | Фича | Приоритет | Effort | Уникальность |
|---|------|-----------|--------|--------------|
| 2.1 | Semantic Boundary Detection | HIGH | 5-7 дней | No |
| 2.2 | Token-Aware Sizing | HIGH | 2-3 дня | No |
| 2.3 | Enhanced Code-Context Binding | MEDIUM | 2-3 дня | **YES** |

### 2.1 Semantic Boundary Detection
Использование sentence embeddings для определения семантических границ.
- **Проблема:** Текущие границы структурные, не семантические
- **Польза:** SCS: +30-40%, общее качество: +10%
- **Детали:** [04-semantic-boundary-detection.md](./features/04-semantic-boundary-detection.md)

### 2.2 Token-Aware Sizing
Размер чанков на основе токенов для LLM context windows.
- **Проблема:** Character-based sizing не соответствует token limits LLM
- **Польза:** Точное соответствие context window моделей (GPT-4, Claude, etc.)
- **Детали:** [05-token-aware-sizing.md](./features/05-token-aware-sizing.md)

### 2.3 Enhanced Code-Context Binding
Улучшенная привязка кода к объяснениям.
- **Проблема:** Код теряет окружающий контекст (explanation → code → output)
- **Польза:** Лучший retrieval для вопросов о коде
- **Детали:** [06-enhanced-code-context-binding.md](./features/06-enhanced-code-context-binding.md)

---

## Фаза 3: Интеграция и Adoption (Месяц 3-4)

**Цель:** Расширить охват экосистемы и улучшить usability

| # | Фича | Приоритет | Effort | Уникальность |
|---|------|-----------|--------|--------------|
| 3.1 | LangChain Adapter | HIGH | 2-3 дня | No |
| 3.2 | LlamaIndex Adapter | HIGH | 3-5 дней | No |
| 3.3 | Adaptive Chunk Sizing | MEDIUM | 2-3 дня | No |
| 3.4 | Debug/Explain Mode | MEDIUM | 2-3 дня | No |

### 3.1 LangChain Adapter
Официальный адаптер для LangChain.
- **Проблема:** Отсутствие официальных адаптеров затрудняет adoption
- **Польза:** Seamless интеграция с LangChain pipelines, публикация в PyPI
- **Детали:** [07-langchain-adapter.md](./features/07-langchain-adapter.md)

### 3.2 LlamaIndex Adapter
Официальный адаптер для LlamaIndex.
- **Проблема:** Та же барьер adoption, что и для LangChain
- **Польза:** Поддержка hierarchical node model LlamaIndex
- **Детали:** [08-llamaindex-adapter.md](./features/08-llamaindex-adapter.md)

### 3.3 Adaptive Chunk Sizing
Автоматическая настройка размера чанка на основе сложности контента.
- **Проблема:** Фиксированный размер не оптимален для разного контента
- **Польза:** Code-heavy → larger chunks, Simple text → smaller chunks
- **Детали:** [09-adaptive-chunk-sizing.md](./features/09-adaptive-chunk-sizing.md)

### 3.4 Debug/Explain Mode
Режим объяснения решений chunker.
- **Проблема:** Пользователи не понимают, почему chunker принял определённые решения
- **Польза:** `explain=True` параметр, логирование решений, визуализация
- **Детали:** [10-debug-explain-mode.md](./features/10-debug-explain-mode.md)

---

## Фаза 4: Продвинутые возможности (Месяц 4-5)

**Цель:** Включить новые use cases и дифференциацию

| # | Фича | Приоритет | Effort | Уникальность |
|---|------|-----------|--------|--------------|
| 4.1 | Hierarchical Chunking | MEDIUM | 7-10 дней | No |
| 4.2 | LaTeX Formula Handling | LOW | 1-2 дня | No |
| 4.3 | Configurable Strategy Thresholds | LOW | 2-3 дня | No |

### 4.1 Hierarchical Chunking
Создание иерархии чанков (parent-child) для многоуровневого retrieval.
- **Проблема:** Flat chunk structure не поддерживает multi-level retrieval
- **Польза:** Document → Section → Subsection → Paragraph levels
- **Детали:** [11-hierarchical-chunking.md](./features/11-hierarchical-chunking.md)

### 4.2 LaTeX Formula Handling
Правильная обработка математических формул.
- **Проблема:** Математические формулы могут быть разорваны
- **Польза:** Распознавание `$...$` и `$$...$$`, сохранение как atomic blocks
- **Детали:** [12-latex-formula-handling.md](./features/12-latex-formula-handling.md)

### 4.3 Configurable Strategy Thresholds
Настраиваемые пороги для выбора стратегий.
- **Проблема:** Текущие пороги hardcoded, нет гибкости
- **Польза:** Fine-tuning для специфических use cases
- **Детали:** [13-configurable-strategy-thresholds.md](./features/13-configurable-strategy-thresholds.md)

---

## Фаза 5: Производительность и полировка (Месяц 5-6)

**Цель:** Production-ready для всех сценариев

| # | Фича | Приоритет | Effort | Уникальность |
|---|------|-----------|--------|--------------|
| 5.1 | Streaming Processing | LOW | 5-7 дней | No |
| 5.2 | Table Grouping Option | LOW | 2-3 дня | No |

### 5.1 Streaming Processing
Потоковая обработка больших файлов.
- **Проблема:** Файлы >10MB могут вызывать memory issues
- **Польза:** Streaming API, reduced memory footprint
- **Детали:** [14-streaming-processing.md](./features/14-streaming-processing.md)

### 5.2 Table Grouping Option
Группировка связанных таблиц.
- **Проблема:** Связанные таблицы могут быть разделены
- **Польза:** Лучше для API reference documentation
- **Детали:** [15-table-grouping-option.md](./features/15-table-grouping-option.md)

---

## Сводная матрица приоритетов

| # | Фича | Фаза | Приоритет | Impact | Effort | Уникальность |
|---|------|------|-----------|--------|--------|--------------|
| 1 | Smart List Strategy | 1 | CRITICAL | High | M | Partial |
| 2 | Nested Fencing Support | 1 | CRITICAL | High | M | **YES** |
| 3 | List Detection в Parser | 1 | HIGH | High | S | No |
| 4 | Semantic Boundary Detection | 2 | HIGH | Very High | M | No |
| 5 | Token-Aware Sizing | 2 | HIGH | High | S | No |
| 6 | Enhanced Code-Context Binding | 2 | MEDIUM | Medium | S | **YES** |
| 7 | LangChain Adapter | 3 | HIGH | High | S | No |
| 8 | LlamaIndex Adapter | 3 | HIGH | High | M | No |
| 9 | Adaptive Chunk Sizing | 3 | MEDIUM | Medium | S | No |
| 10 | Debug/Explain Mode | 3 | MEDIUM | Medium | S | No |
| 11 | Hierarchical Chunking | 4 | MEDIUM | High | L | No |
| 12 | LaTeX Formula Handling | 4 | LOW | Medium | S | No |
| 13 | Configurable Strategy Thresholds | 4 | LOW | Medium | S | No |
| 14 | Streaming Processing | 5 | LOW | Medium | M | No |
| 15 | Table Grouping Option | 5 | LOW | Low | S | No |

**Легенда Effort:** S = Small (1-3 дня), M = Medium (3-7 дней), L = Large (7-10 дней)

---

## Общие затраты

| Фаза | Effort (дни) |
|------|--------------|
| Фаза 1 | 10-15 |
| Фаза 2 | 9-13 |
| Фаза 3 | 9-14 |
| Фаза 4 | 10-15 |
| Фаза 5 | 7-10 |
| **Итого** | **40-55 дней** |

---

## Метрики успеха

| Метрика | Текущее | Цель |
|---------|---------|------|
| SCS (overall) | 1.3 | > 1.8 |
| CPS (overall) | 75% | > 90% |
| BQS (overall) | 0.88 | > 0.95 |
| OQS (overall) | 78 | > 88 |
| SCS (list-heavy docs) | 1.2 | > 1.6 |
| Скорость обработки | 45ms/100KB | < 40ms/100KB |

---

## Уникальные дифференциаторы после реализации

1. **Nested Fencing Support** — единственное решение с полной поддержкой
2. **Code-Context Binding** — уникальная привязка кода к объяснениям
3. **Smart List Strategy** — улучшенная обработка списков с иерархией
4. **Automatic Strategy Selection** — интеллектуальный выбор стратегии

---

## Критерии "Top-1 Candidate"

markdown_chunker_v2 будет считаться "top-1 candidate" когда:

1. **Quality:** OQS > 88 (лучше всех конкурентов)
2. **Features:** 3+ уникальных возможности
3. **Integration:** Официальные адаптеры для top-3 RAG frameworks
4. **Performance:** Конкурентная скорость (< 50ms/100KB)
5. **Adoption:** Рекомендация в документации Dify/LangChain/LlamaIndex

---

## Риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Semantic boundaries slow | Medium | Medium | Optional feature, caching |
| Breaking changes | Low | High | Semantic versioning, migration guide |
| Dependency bloat | Medium | Medium | Optional dependencies |
| Scope creep | High | Medium | Strict prioritization |

---

## Рекомендация

**Немедленно:** Фаза 1 — восстановить List Strategy и добавить Nested Fencing
**Краткосрочно:** Фаза 2 — добавить Semantic Boundaries и Token-Aware Sizing
**Среднесрочно:** Фазы 3-4 — адаптеры и Hierarchical Chunking

При реализации всех 15 фич за 6 месяцев, markdown_chunker_v2 станет бесспорным лидером с лучшим качеством chunking и уникальными возможностями.

## Приложение (SCS, CPS, BQS, OQS, SCS)

### Что такое каждая метрика по этим формулам

1. **Semantic Coherence Score (SCS)**
   Формула:

   ```text
   SCS = avg(intra_chunk_similarity) / avg(inter_chunk_similarity)
   ```

   * `intra_chunk_similarity` — насколько похожи друг на друга куски *внутри* одного чанка.
   * `inter_chunk_similarity` — насколько похожи куски *между разными* чанками.

   Интуиция:

   * Если внутри чанков всё «про одно и то же», а между чанками — про разное, то SCS > 1, и чем больше, тем лучше.
   * Если чанки неотличимы друг от друга (или внутри такой же шум, как и между), SCS ≈ 1 или меньше.

2. **Context Preservation Score (CPS)**
   Формула:

   ```text
   CPS = (code_blocks_with_context / total_code_blocks) * 100
   ```

   Это доля кодовых блоков, у которых **рядом с ними в чанках есть нужный контекст** (объяснение, описание, заголовок, связанный текст).

   * 75% ⇒ у 3 из 4 кусков кода есть читабельный контекст;
   * цель >90% ⇒ почти каждый кусок кода попадает в чанки вместе с объяснением.

3. **Boundary Quality Score (BQS)**
   Формула:

   ```text
   BQS = 1 - (bad_boundaries / total_boundaries)
   ```

   * `bad_boundaries` — границы чанков, которые режут посреди предложения/кода/таблицы и т.п.
   * `total_boundaries` — количество всех границ.

   Если каждый разрез проходит по «естественным» местам (между блоками/абзацами), то `bad_boundaries` → 0 и BQS → 1.

4. **Size Distribution Score (SDS)**
   Формула:

   ```text
   SDS = chunks_in_optimal_range / total_chunks
   ```

   Это доля чанков, у которых размер в «золотом диапазоне» 500–2000 символов:

   * слишком маленькие — теряем контекст,
   * слишком большие — плохо влезают в контекст модели и мешают точному матчинг-поиску.

5. **Overall Quality Score (OQS)**
   Формула (из черновика):

   ```text
   OQS = (SCS_norm * 0.25) + (CPS * 0.30) + (BQS * 0.30) + (SDS * 0.15)
   ```

   Это сводная оценка качества чанкования:

   * семантика внутри чанков (SCS_norm),
   * сохранение контекста кода (CPS),
   * аккуратность границ (BQS),
   * адекватный размер чанков (SDS).
