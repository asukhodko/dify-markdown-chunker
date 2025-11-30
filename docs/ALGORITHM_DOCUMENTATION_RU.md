# Техническая документация: Алгоритм чанкования Markdown документов

## Оглавление

1. [Введение и обзор системы](#1-введение-и-обзор-системы)
2. [Архитектура и компоненты](#2-архитектура-и-компоненты)
3. [Анализ контента (ContentAnalyzer)](#3-анализ-контента-contentanalyzer)
4. [Стратегии разбиения](#4-стратегии-разбиения)
5. [Выбор стратегии (StrategySelector)](#5-выбор-стратегии-strategyselector)
6. [Обработка специальных случаев](#6-обработка-специальных-случаев)
7. [Структуры данных](#7-структуры-данных)
8. [Алгоритмы и формулы](#8-алгоритмы-и-формулы)
9. [Примеры и тестовые случаи](#9-примеры-и-тестовые-случаи)
10. [Справочная информация](#10-справочная-информация)

---

## 1. Введение и обзор системы

### 1.1 Назначение

Алгоритм чанкования Markdown документов предназначен для интеллектуального разбиения больших Markdown файлов на семантически связные фрагменты (чанки). Основная цель - подготовка документов для систем Retrieval-Augmented Generation (RAG), где важно сохранить смысловую целостность и контекст каждого фрагмента.

### 1.2 Проблема

При работе с большими документами возникают следующие проблемы:
- **Ограничения контекста**: LLM модели имеют ограничение на размер входного контекста
- **Потеря семантики**: Простое разбиение по размеру разрывает связанные части
- **Разнородность контента**: Markdown содержит код, таблицы, списки, текст - каждый требует своего подхода
- **Потеря структуры**: Важно сохранить иерархию заголовков и связи между секциями

### 1.3 Решение

Система использует **адаптивный подход** к разбиению:
1. **Анализ документа**: Определение типа и структуры контента
2. **Выбор стратегии**: Автоматический выбор оптимального алгоритма разбиения
3. **Умное разбиение**: Сохранение семантических границ и контекста
4. **Обогащение метаданными**: Добавление информации для последующего поиска

### 1.4 Ключевые принципы

**Адаптивность к типу контента:**
- Разные типы контента (код, списки, таблицы, текст) обрабатываются специализированными стратегиями
- Автоматическое определение оптимальной стратегии на основе анализа

**Сохранение семантических границ:**
- Разбиение происходит по естественным границам (заголовки, параграфы, предложения)
- Блоки кода, таблицы и списки сохраняются атомарно когда возможно
- Избегание разрыва связанных частей

**Оптимизация для RAG:**
- Размер чанков оптимизирован для embedding моделей
- Перекрытие между чанками для сохранения контекста
- Богатые метаданные для точного поиска

**Производительность и масштабируемость:**
- Потоковая обработка для больших файлов (>10MB)
- Параллельная обработка множества файлов
- Оптимизации: кеширование, memory pooling

### 1.5 Ключевые концепции

**Chunk (Чанк):**
- Семантически связный фрагмент документа
- Имеет определенный размер (обычно 1000-8000 символов)
- Содержит метаданные о своем происхождении и типе

**Strategy (Стратегия):**
- Специализированный алгоритм разбиения для определенного типа контента
- 6 стратегий: Code, List, Table, Mixed, Structural, Sentences
- Каждая оптимизирована для своего типа контента

**Analysis (Анализ):**
- Процесс определения характеристик документа
- Вычисление метрик: соотношения типов контента, сложность, структура
- Результат используется для выбора стратегии

**Metadata (Метаданные):**
- Информация о чанке: тип, стратегия, позиция, структура
- Используется для поиска и восстановления контекста
- Включает специфичные для типа данные (язык кода, уровень заголовка, и т.д.)



### 1.6 Общая схема работы

```
┌─────────────────────────────────────────────────────────────────┐
│                      Входной Markdown документ                   │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Нормализация контента                         │
│  • Преобразование кодировки в UTF-8                             │
│  • Нормализация переносов строк (\r\n → \n)                     │
│  • Удаление BOM (Byte Order Mark)                               │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ContentAnalyzer                               │
│  • Обнаружение структурных элементов                            │
│  • Вычисление метрик контента                                   │
│  • Классификация типа документа                                 │
│  • Оценка сложности                                             │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    StrategySelector                              │
│  • Оценка подходящести каждой стратегии                         │
│  • Выбор оптимальной стратегии                                  │
│  • Учет приоритетов и качества                                  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ChunkingStrategy                              │
│  • Применение выбранной стратегии                               │
│  • Разбиение на семантические фрагменты                         │
│  • Сохранение структуры и границ                                │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PreambleHandler                               │
│  • Обработка контента до первого заголовка                      │
│  • Разбиение больших преамбул                                   │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OverlapProcessor                              │
│  • Создание перекрытия между чанками                            │
│  • Определение границ для перекрытия                            │
│  • Сохранение контекста                                         │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Обогащение метаданными                        │
│  • Добавление информации о стратегии                            │
│  • Добавление структурных метаданных                            │
│  • Добавление метрик анализа                                    │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Валидация чанков                              │
│  • Проверка размеров                                            │
│  • Проверка метаданных                                          │
│  • Проверка целостности                                         │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Результат: Массив чанков                      │
│  • Каждый чанк с контентом и метаданными                        │
│  • Готов для индексации и поиска                                │
└─────────────────────────────────────────────────────────────────┘
```

### 1.7 Пример разбиения документа

**Входной документ:**
```markdown
# Руководство по API

Это введение в наш API.

## Аутентификация

Для использования API нужен токен:

```python
import requests

headers = {"Authorization": "Bearer YOUR_TOKEN"}
response = requests.get("https://api.example.com", headers=headers)
```

## Endpoints

Доступные endpoints:

- GET /users - список пользователей
- POST /users - создание пользователя
- GET /users/{id} - получение пользователя
```

**Результат разбиения:**

```
Chunk 1 (Preamble):
  "# Руководство по API\n\nЭто введение в наш API."
  Metadata: {type: "preamble", header_level: "1"}

Chunk 2 (Header + Text):
  "## Аутентификация\n\nДля использования API нужен токен:"
  Metadata: {type: "header_with_content", header_level: "2"}

Chunk 3 (Code):
  "```python\nimport requests\n...\n```"
  Metadata: {type: "code", language: "python", strategy: "code"}

Chunk 4 (Header + List):
  "## Endpoints\n\nДоступные endpoints:\n\n- GET /users..."
  Metadata: {type: "mixed", has_lists: "true", strategy: "mixed"}
```

---

## 2. Архитектура и компоненты

### 2.1 Обзор архитектуры

Система построена по модульному принципу с четким разделением ответственности:

```
┌─────────────────────────────────────────────────────────────────┐
│                         Extractor                                │
│                   (Главный оркестратор)                          │
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │
│  │ ErrorHandler   │  │ FallbackChain  │  │ StreamingProc    │  │
│  └────────────────┘  └────────────────┘  └──────────────────┘  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ContentAnalyzer│  │StrategySelector  │  │PreambleHandler   │
│               │  │                  │  │                  │
│• Анализ       │  │• Выбор стратегии │  │• Обработка       │
│  структуры    │  │• Оценка          │  │  преамбулы       │
│• Метрики      │  │  подходящести    │  └──────────────────┘
│• Классификация│  │• Приоритеты      │
└───────────────┘  └────────┬─────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ChunkingStrategy │
                   │   (Interface)   │
                   └────────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│CodeStrategy  │  │ListStrategy  │  │TableStrategy │
└──────────────┘  └──────────────┘  └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│MixedStrategy │  │Structural    │  │Sentences     │
│              │  │Strategy      │  │Strategy      │
└──────────────┘  └──────────────┘  └──────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │OverlapProcessor │
                   │                 │
                   │• Создание       │
                   │  перекрытия     │
                   │• Определение    │
                   │  границ         │
                   └─────────────────┘
```



### 2.2 Описание компонентов

#### 2.2.1 Extractor (Главный оркестратор)

**Ответственность:**
- Координация всего процесса извлечения чанков
- Управление потоком данных между компонентами
- Обработка ошибок и применение fallback стратегий
- Выбор между обычной и потоковой обработкой

**Основные методы:**
```
Extract(context, file) -> (chunks, error)
  - Главный метод извлечения чанков
  
shouldUseStreaming(file) -> bool
  - Определяет нужна ли потоковая обработка
  
validateInput(file) -> error
  - Валидация входных данных
  
normalizeNewlines(content) -> string
  - Нормализация переносов строк
```

**Алгоритм работы:**
```
1. Проверить размер файла
2. IF размер > StreamingThreshold THEN
     Использовать StreamingProcessor
   ELSE
     Продолжить обычную обработку
3. Валидировать входные данные
4. Нормализовать контент (UTF-8, переносы строк)
5. Передать ContentAnalyzer для анализа
6. Получить результат анализа
7. Передать StrategySelector для выбора стратегии
8. Применить выбранную стратегию
9. Обработать преамбулу (PreambleHandler)
10. Добавить перекрытие (OverlapProcessor)
11. Обогатить метаданными
12. Валидировать результат
13. Вернуть чанки
```

#### 2.2.2 ContentAnalyzer (Анализатор контента)

**Ответственность:**
- Анализ структуры Markdown документа
- Обнаружение всех типов элементов (код, списки, таблицы, заголовки)
- Вычисление метрик контента
- Классификация типа документа
- Оценка сложности

**Основные методы:**
```
AnalyzeContent(content) -> DocumentAnalysis
  - Полный анализ документа
  
DetectCodeBlocks(content) -> []CodeBlock
  - Обнаружение блоков кода
  
DetectLists(content) -> []ListElement
  - Обнаружение списков
  
DetectTables(content) -> []Table
  - Обнаружение таблиц
  
AnalyzeHeaders(content) -> HeaderStructure
  - Анализ структуры заголовков
  
CalculateMetrics(content) -> ContentMetrics
  - Вычисление метрик
```

**Процесс анализа:**
```
1. Вычислить базовые метрики (размер, строки, слова)
2. Обнаружить все заголовки и построить иерархию
3. Обнаружить все блоки кода (fenced и indented)
4. Обнаружить все списки с вложенностью
5. Обнаружить все таблицы
6. Вычислить соотношения типов контента:
   - CodeRatio = размер_кода / общий_размер
   - TextRatio = размер_текста / общий_размер
   - ListRatio = размер_списков / общий_размер
   - TableRatio = размер_таблиц / общий_размер
7. Определить языки программирования
8. Классифицировать тип контента
9. Вычислить ComplexityScore
10. Вернуть DocumentAnalysis
```

#### 2.2.3 StrategySelector (Селектор стратегий)

**Ответственность:**
- Выбор оптимальной стратегии разбиения
- Оценка подходящести каждой стратегии
- Управление приоритетами стратегий
- Поддержка разных режимов выбора (strict/weighted)

**Основные методы:**
```
SelectStrategy(analysis, config) -> (strategy, error)
  - Выбор оптимальной стратегии
  
RegisterStrategy(strategy) -> error
  - Регистрация новой стратегии
  
EvaluateStrategy(strategy, analysis) -> float64
  - Оценка подходящести стратегии (0.0-1.0)
  
GetAvailableStrategies() -> []Strategy
  - Получение списка доступных стратегий
```

**Алгоритм выбора:**
```
1. Создать список кандидатов
2. FOR EACH зарегистрированная стратегия:
   a. Проверить CanHandle(analysis, config)
   b. IF может обработать THEN
      - Вычислить QualityScore
      - Получить Priority
      - Добавить в кандидаты
3. IF нет кандидатов THEN
   RETURN error
4. IF режим = "strict" THEN
   Сортировать по Priority
   RETURN первую
5. ELSE IF режим = "weighted" THEN
   FOR EACH кандидат:
     WeightedScore = (1.0/Priority)*0.5 + QualityScore*0.5
   Сортировать по WeightedScore
   RETURN первую
```

#### 2.2.4 ChunkingStrategy (Интерфейс стратегий)

**Ответственность:**
- Определение интерфейса для всех стратегий
- Обеспечение единообразия реализаций

**Методы интерфейса:**
```
GetName() -> string
  - Имя стратегии
  
GetDescription() -> string
  - Описание стратегии
  
GetPriority() -> int
  - Приоритет (1 = высший)
  
CanHandle(analysis, config) -> bool
  - Может ли обработать документ
  
Apply(content, file, analysis, config) -> (chunks, error)
  - Применение стратегии
  
EstimateChunkCount(analysis, config) -> int
  - Оценка количества чанков
  
GetStrategyMetadata(analysis, config) -> map[string]string
  - Метаданные стратегии
```

#### 2.2.5 PreambleHandler (Обработчик преамбулы)

**Ответственность:**
- Обработка контента до первого заголовка
- Разбиение больших преамбул
- Классификация типа преамбулы (введение/метаданные)

**Основные методы:**
```
ProcessPreamble(content, config) -> (result, error)
  - Обработка преамбулы
  
IsPreamble(content) -> bool
  - Проверка наличия преамбулы
  
GetPreambleMetrics(content) -> metrics
  - Метрики преамбулы
```

#### 2.2.6 OverlapProcessor (Процессор перекрытия)

**Ответственность:**
- Создание перекрытия между соседними чанками
- Определение оптимальных границ для перекрытия
- Сохранение контекста между чанками

**Основные методы:**
```
ProcessChunks(chunks, config) -> result
  - Обработка всех чанков
  
CalculateOverlap(chunk1, chunk2, config) -> info
  - Вычисление перекрытия между двумя чанками
  
DetectBoundaries(content, config) -> []boundary
  - Обнаружение границ для перекрытия
```

#### 2.2.7 ErrorHandler (Обработчик ошибок)

**Ответственность:**
- Обработка ошибок с возможностью восстановления
- Применение стратегий восстановления
- Сбор статистики ошибок

**Категории ошибок:**
- Input Validation - невалидный вход
- Processing Errors - ошибки обработки
- Strategy Failures - ошибки стратегии
- Resource Limits - превышение лимитов

**Стратегии восстановления:**
- CleanAndRetry - очистить и повторить
- FallbackStrategy - использовать более простую стратегию
- PartialResults - вернуть частичные результаты
- EmergencyFallback - базовое разбиение

#### 2.2.8 StreamingProcessor (Потоковый процессор)

**Ответственность:**
- Обработка больших файлов (>10MB) потоково
- Управление памятью
- Разбиение на окна обработки
- Объединение результатов

**Основные методы:**
```
ProcessLargeFile(context, reader, file, config) -> (chunks, error)
  - Потоковая обработка файла
  
ProcessFileChunks(context, content, file, config) -> (chunks, error)
  - Обработка чанков файла
  
EstimateMemoryUsage(fileSize, config) -> int64
  - Оценка использования памяти
```

### 2.3 Взаимодействие компонентов

**Последовательность вызовов:**

```
1. Extractor.Extract()
   ↓
2. Extractor.shouldUseStreaming()
   ↓ (если нужен streaming)
3. StreamingProcessor.ProcessLargeFile()
   ↓ (иначе обычная обработка)
4. Extractor.validateInput()
   ↓
5. Extractor.normalizeNewlines()
   ↓
6. ContentAnalyzer.AnalyzeContent()
   ├─ DetectCodeBlocks()
   ├─ DetectLists()
   ├─ DetectTables()
   ├─ AnalyzeHeaders()
   └─ CalculateMetrics()
   ↓
7. StrategySelector.SelectStrategy()
   ├─ FOR EACH strategy:
   │   ├─ strategy.CanHandle()
   │   └─ EvaluateStrategy()
   └─ Выбор лучшей
   ↓
8. Strategy.Apply()
   ↓
9. PreambleHandler.ProcessPreamble()
   ↓
10. OverlapProcessor.ProcessChunks()
    ↓
11. Обогащение метаданными
    ↓
12. Валидация
    ↓
13. RETURN chunks
```

**Обработка ошибок:**

```
TRY:
  Основная обработка
CATCH error:
  ↓
  ErrorHandler.HandleError()
  ↓
  Определить категорию ошибки
  ↓
  Выбрать стратегию восстановления
  ↓
  IF CleanAndRetry THEN
    Очистить контент
    Повторить обработку
  ELSE IF FallbackStrategy THEN
    Использовать более простую стратегию
  ELSE IF PartialResults THEN
    Вернуть частичные результаты
  ELSE IF EmergencyFallback THEN
    Базовое разбиение по размеру
  ELSE
    RETURN error
```


## 3. Анализ контента (ContentAnalyzer)

### 3.1 Назначение и принципы работы

ContentAnalyzer - это ключевой компонент системы, который выполняет глубокий анализ Markdown документа перед его разбиением на чанки. Результаты анализа используются для выбора оптимальной стратегии разбиения.

**Основные задачи:**
1. Обнаружение всех структурных элементов документа
2. Вычисление метрик контента
3. Определение соотношений различных типов контента
4. Классификация типа документа
5. Оценка сложности документа

**Принципы работы:**
- **Полнота анализа**: Обнаруживаются все типы элементов (заголовки, код, списки, таблицы)
- **Точность метрик**: Используются проверенные алгоритмы для вычисления метрик
- **Производительность**: Оптимизированные регулярные выражения и кеширование
- **Расширяемость**: Легко добавить новые типы анализа

### 3.2 Интерфейс ContentAnalyzer

```go
type ContentAnalyzer interface {
    // Полный анализ документа
    AnalyzeContent(content string) *DocumentAnalysis
    
    // Обнаружение блоков кода
    DetectCodeBlocks(content string) []ExtendedCodeBlock
    
    // Обнаружение списков
    DetectLists(content string) []ListElement
    
    // Обнаружение таблиц
    DetectTables(content string) []Table
    
    // Анализ структуры заголовков
    AnalyzeHeaders(content string) *HeaderStructure
    
    // Вычисление метрик
    CalculateMetrics(content string) *ContentMetrics
}
```

### 3.3 Конфигурация анализатора

```go
type AnalyzerConfig struct {
    // Пороги для определения типов контента
    CodeRatioThreshold float64  // 0.7 - порог для code_heavy
    ListRatioThreshold float64  // 0.6 - порог для list_heavy
    MixedContentMin    float64  // 0.2 - минимум для mixed
    MixedContentMax    float64  // 0.7 - максимум для mixed
    
    // Настройки анализа
    MinCodeBlockSize   int      // 10 - минимальный размер блока кода
    MinListItems       int      // 3 - минимум элементов для списка
    MinTableColumns    int      // 2 - минимум колонок для таблицы
    
    // Поддерживаемые языки программирования
    SupportedLanguages []string
}
```

**Значения по умолчанию:**
- CodeRatioThreshold: 0.7
- ListRatioThreshold: 0.6
- MixedContentMin: 0.2
- MixedContentMax: 0.7
- MinCodeBlockSize: 10 символов
- MinListItems: 3 элемента
- MinTableColumns: 2 колонки

**Поддерживаемые языки:**
go, python, javascript, typescript, java, cpp, c, csharp, php, ruby, rust, kotlin, swift, scala, shell, bash, yaml, json, toml, ini, xml, html, css, sql, dockerfile, makefile


### 3.4 Метрики контента (ContentMetrics)

ContentMetrics содержит детальную информацию о характеристиках документа:

```go
type ContentMetrics struct {
    // Базовые метрики
    TotalCharacters   int     // Общее количество символов (Unicode)
    TotalLines        int     // Общее количество строк
    TotalWords        int     // Общее количество слов
    
    // Метрики строк
    AverageLineLength float64 // Средняя длина строки
    MaxLineLength     int     // Максимальная длина строки
    EmptyLines        int     // Количество пустых строк
    IndentedLines     int     // Количество строк с отступом
    
    // Анализ контента
    LanguageCount     map[string]int  // Количество упоминаний языков
    PunctuationRatio  float64         // Соотношение знаков препинания
    SpecialChars      map[string]int  // Специальные символы
}
```

**Вычисление метрик:**

**1. TotalCharacters:**
```
TotalCharacters = len([]rune(content))
```
Используются руны (Unicode символы), а не байты, для корректного подсчета многобайтовых символов.

**2. TotalWords:**
```
TotalWords = len(strings.Fields(content))
```
Разбивает текст по пробельным символам.

**3. AverageLineLength:**
```
AverageLineLength = TotalLength / TotalLines

где TotalLength = сумма длин всех строк
```

**4. PunctuationRatio:**
```
PunctuationRatio = PunctuationCount / TotalCharacters

где PunctuationCount = количество символов, для которых unicode.IsPunct(r) = true
```

**5. SpecialChars:**
Подсчитываются следующие специальные символы:
- `#` - заголовки
- `*` - списки, выделение
- `_` - выделение
- `` ` `` - код
- `[`, `]` - ссылки
- `(`, `)` - ссылки
- `{`, `}` - код
- `<`, `>` - HTML
- `|` - таблицы
- `-` - списки, разделители
- `=` - заголовки
- `+` - списки


### 3.5 Обнаружение блоков кода (DetectCodeBlocks)

Система обнаруживает два типа блоков кода:

#### 3.5.1 Fenced блоки (огражденные)

**Формат:**
```
```language
код
```
```

**Регулярное выражение:**
```regex
^```(\w*)$
```
- Группа 1: язык программирования (опционально)

**Алгоритм обнаружения:**
```
1. Разбить контент на строки
2. inBlock = false
3. currentBlock = null
4. FOR EACH line IN lines:
   trimmed = TrimSpace(line)
   
   IF trimmed начинается с "```" THEN
      IF NOT inBlock THEN
         // Начало блока
         language = trimmed[3:]  // Все после ```
         currentBlock = новый ExtendedCodeBlock
         currentBlock.StartLine = lineNum + 1
         currentBlock.Language = language
         currentBlock.IsFenced = true
         inBlock = true
      ELSE
         // Конец блока
         currentBlock.EndLine = lineNum + 1
         currentBlock.Complexity = AnalyzeCodeComplexity(currentBlock.Content)
         ExtractCodeStructure(currentBlock)
         IF len(TrimSpace(currentBlock.Content)) > 0 THEN
            blocks.append(currentBlock)
         currentBlock = null
         inBlock = false
   ELSE IF inBlock THEN
      // Добавляем содержимое к блоку
      IF currentBlock.Content != "" THEN
         currentBlock.Content += "\n"
      currentBlock.Content += line

5. IF inBlock AND currentBlock != null THEN
   // Блок не был закрыт - все равно добавляем
   currentBlock.EndLine = len(lines)
   currentBlock.Complexity = AnalyzeCodeComplexity(currentBlock.Content)
   ExtractCodeStructure(currentBlock)
   blocks.append(currentBlock)

6. RETURN blocks
```

#### 3.5.2 Indented блоки (с отступом)

**Формат:**
```
    код с 4 пробелами
    или с табуляцией
```

**Правило обнаружения:**
Строка считается частью indented блока, если:
- Начинается с 4 пробелов ИЛИ табуляции
- НЕ находится внутри fenced блока

**Алгоритм обнаружения:**
```
1. Получить все fenced блоки
2. Создать карту fencedLines (строки внутри fenced блоков)
3. inBlock = false
4. currentBlock = null
5. FOR EACH line IN lines:
   IF line в fencedLines THEN
      IF inBlock THEN
         // Завершаем текущий indented блок
         FinalizeBlock(currentBlock)
         currentBlock = null
         inBlock = false
      CONTINUE
   
   IF line начинается с "    " ИЛИ "\t" THEN
      IF NOT inBlock THEN
         // Начало нового блока
         currentBlock = новый ExtendedCodeBlock
         currentBlock.StartLine = lineNum + 1
         currentBlock.IsIndented = true
         currentBlock.Content = TrimPrefix(line, "    " или "\t")
         inBlock = true
      ELSE
         // Продолжение блока
         trimmedLine = TrimPrefix(line, "    " или "\t")
         currentBlock.Content += "\n" + trimmedLine
   ELSE IF inBlock THEN
      // Конец блока
      FinalizeBlock(currentBlock)
      currentBlock = null
      inBlock = false

6. IF inBlock AND currentBlock != null THEN
   FinalizeBlock(currentBlock)

7. RETURN blocks
```

**FinalizeBlock:**
```
1. IF currentBlock == null OR TrimSpace(currentBlock.Content) == "" THEN
   RETURN

2. currentBlock.EndLine = lineNum

3. IF currentBlock.Language == "" THEN
   currentBlock.Language = DetectLanguage(currentBlock.Content)

4. currentBlock.Complexity = AnalyzeCodeComplexity(currentBlock.Content)

5. blocks.append(currentBlock)
```


### 3.6 Определение языка программирования (DetectLanguage)

Для indented блоков кода язык определяется автоматически по содержимому.

**Алгоритм:**
```
1. contentLower = ToLower(content)

2. Определить паттерны для каждого языка:
   patterns = {
       "go": ["package", "func", "import", "var", "fmt."],
       "python": ["def", "import", "class", "print(", "self"],
       "javascript": ["function", "var", "let", "const", "console."],
       "java": ["public class", "static", "void", "System."],
       "sql": ["select", "from", "where", "insert"]
   }

3. maxScore = 0
   detected = ""

4. FOR EACH (lang, indicators) IN patterns:
   score = 0
   FOR EACH indicator IN indicators:
      IF contentLower содержит indicator THEN
         score++
   
   IF score > maxScore AND score >= 2 THEN
      maxScore = score
      detected = lang

5. RETURN detected
```

**Примеры:**

**Python:**
```python
def hello():
    print("Hello")
```
Обнаружено: "def", "print(" → score = 2 → язык = "python"

**Go:**
```go
package main
import "fmt"
func main() {
    fmt.Println("Hello")
}
```
Обнаружено: "package", "import", "func", "fmt." → score = 4 → язык = "go"

### 3.7 Анализ сложности кода (AnalyzeCodeComplexity)

Вычисляет оценку сложности блока кода на основе эвристик.

**Алгоритм:**
```
1. complexity = 0

2. // Базовая сложность по размеру
   lines = Split(content, "\n")
   complexity += len(lines) / 10  // 1 балл за каждые 10 строк

3. // Сложность за управляющие структуры
   keywords = ["if", "for", "while", "switch", "case", 
               "try", "catch", "function", "def", "class"]
   
   FOR EACH keyword IN keywords:
      count = Count(ToLower(content), keyword)
      complexity += count

4. RETURN complexity
```

**Примеры:**

**Простой код (10 строк, 1 функция):**
```
complexity = 10/10 + 1 = 2
```

**Сложный код (50 строк, 5 if, 3 for, 2 функции):**
```
complexity = 50/10 + 5 + 3 + 2 = 15
```

### 3.8 Извлечение структуры кода (ExtractCodeStructure)

Извлекает имена функций и классов из блока кода.

**Регулярные выражения по языкам:**

**Go:**
```regex
Функция: func\s+(\w+)
Структура: type\s+(\w+)\s+struct
```

**Python:**
```regex
Функция: def\s+(\w+)
Класс: class\s+(\w+)
```

**JavaScript/TypeScript:**
```regex
Функция: function\s+(\w+)
Класс: class\s+(\w+)
```

**Алгоритм:**
```
1. SWITCH block.Language:
   CASE "go", "golang":
      IF match = Regex("func\s+(\w+)").Find(content) THEN
         block.FunctionName = match[1]
      IF match = Regex("type\s+(\w+)\s+struct").Find(content) THEN
         block.ClassName = match[1]
   
   CASE "python", "py":
      IF match = Regex("def\s+(\w+)").Find(content) THEN
         block.FunctionName = match[1]
      IF match = Regex("class\s+(\w+)").Find(content) THEN
         block.ClassName = match[1]
   
   CASE "javascript", "js", "typescript", "ts":
      IF match = Regex("function\s+(\w+)").Find(content) THEN
         block.FunctionName = match[1]
      IF match = Regex("class\s+(\w+)").Find(content) THEN
         block.ClassName = match[1]
```

**Примеры:**

**Go:**
```go
func ProcessData(input string) error {
    // ...
}
```
→ FunctionName = "ProcessData"

**Python:**
```python
class DataProcessor:
    def process(self, data):
        pass
```
→ ClassName = "DataProcessor", FunctionName = "process"


### 3.9 Обнаружение списков (DetectLists)

Система обнаруживает три типа списков:
1. Unordered (неупорядоченные): -, *, +
2. Ordered (упорядоченные): 1., 2., 3.
3. Task (задачи): - [ ], - [x]

**Регулярные выражения:**

```regex
Unordered: ^(\s*)([-*+])\s+(.*)$
Ordered:   ^(\s*)(\d+)\.\s+(.*)$
Task:      ^(\s*)([-*+])\s+\[([ xX])\]\s+(.*)$
```

**Структура ListElement:**
```go
type ListElement struct {
    Type      string        // "ordered" | "unordered" | "task"
    Level     int           // Уровень вложенности (0, 1, 2, ...)
    StartLine int
    EndLine   int
    Content   string
    Items     []ListElement // Вложенные элементы
}
```

**Определение уровня вложенности:**
```
Level = количество пробелов в начале / 2

Примеры:
"- Item"      → Level = 0 (0 пробелов)
"  - Item"    → Level = 1 (2 пробела)
"    - Item"  → Level = 2 (4 пробела)
```

**Алгоритм обнаружения:**
```
1. Разбить контент на строки
2. Создать ListParser
3. RETURN ListParser.ProcessListItems(lines)
```

**ListParser.ProcessListItems:**
```
1. lists = []
2. currentList = null
3. stack = []  // Стек для отслеживания вложенности

4. FOR EACH line IN lines:
   IF line соответствует паттерну списка THEN
      level = CalculateLevel(line)
      type = DetermineType(line)
      content = ExtractContent(line)
      
      element = новый ListElement
      element.Type = type
      element.Level = level
      element.StartLine = lineNum + 1
      element.Content = content
      
      // Управление вложенностью
      WHILE len(stack) > 0 AND stack[top].Level >= level:
         stack.pop()
      
      IF len(stack) > 0 THEN
         parent = stack[top]
         parent.Items.append(element)
      ELSE
         lists.append(element)
      
      stack.push(element)
      currentList = element
   
   ELSE IF currentList != null AND line не пустая THEN
      // Продолжение контента элемента списка
      currentList.Content += "\n" + line
   
   ELSE
      // Конец списка
      currentList = null
      stack = []

5. RETURN lists
```

**Примеры:**

**Простой список:**
```markdown
- Item 1
- Item 2
- Item 3
```
→ 3 ListElement с Level = 0

**Вложенный список:**
```markdown
- Parent 1
  - Child 1.1
  - Child 1.2
- Parent 2
```
→ 2 ListElement с Level = 0, каждый содержит Items с Level = 1

**Task список:**
```markdown
- [ ] Task 1
- [x] Task 2 (completed)
- [ ] Task 3
```
→ 3 ListElement с Type = "task"


### 3.10 Обнаружение таблиц (DetectTables)

Система обнаруживает Markdown таблицы в формате:

```markdown
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
```

**Структура Table:**
```go
type Table struct {
    StartLine  int
    EndLine    int
    Rows       int      // Количество строк данных (без заголовка)
    Columns    int      // Количество колонок
    Headers    []string // Заголовки колонок
    TableType  string   // "data" | "comparison" | "configuration"
    Content    string   // Полное содержимое таблицы
    HasHeaders bool     // Есть ли заголовки
}
```

**Регулярные выражения:**

```regex
Строка таблицы: ^.*\|.*$
Разделитель:    ^[\|\-\:\s]+$
```

**Алгоритм обнаружения:**
```
1. tables = []
2. lines = Split(content, "\n")

3. FOR i, line IN lines:
   IF IsTableSeparator(line) AND i > 0 THEN
      headerLine = lines[i-1]
      
      IF IsTableRow(headerLine) THEN
         // Нашли таблицу
         tableLines = lines[i-1:]  // От заголовка до конца
         table = ParseTable(tableLines, i)
         
         IF table != null THEN
            tables.append(table)

4. RETURN tables
```

**IsTableSeparator:**
```
1. trimmed = TrimSpace(line)
2. // Разделитель состоит из |, -, : и пробелов
3. RETURN Regex("^[\|\-\:\s]+$").Match(trimmed) AND Contains(trimmed, "|")
```

**IsTableRow:**
```
1. trimmed = TrimSpace(line)
2. RETURN Contains(trimmed, "|") AND len(trimmed) > 0
```

**ParseTable:**
```
1. IF len(lines) < 2 THEN
   RETURN null

2. IF NOT IsTableSeparator(lines[1]) THEN
   RETURN null

3. // Подсчитываем колонки по разделителю
   separatorParts = Split(lines[1], "|")
   columns = 0
   FOR EACH part IN separatorParts:
      IF TrimSpace(part) != "" THEN
         columns++
   
   IF columns <= 0 THEN
      RETURN null

4. // Извлекаем заголовки
   headers = []
   IF IsTableRow(lines[0]) THEN
      headerCells = Split(lines[0], "|")
      FOR EACH cell IN headerCells:
         trimmed = TrimSpace(cell)
         IF trimmed != "" THEN
            headers.append(trimmed)

5. // Извлекаем строки данных
   rows = 0
   content = ""
   endLine = startLine
   
   FOR i, line IN lines:
      IF i == 1 THEN
         CONTINUE  // Пропускаем разделитель
      
      IF IsTableRow(line) THEN
         rows++
         IF content != "" THEN
            content += "\n"
         content += line
         endLine = startLine + i
      ELSE IF i > 1 THEN
         BREAK  // Конец таблицы

6. IF rows == 0 THEN
   RETURN null

7. table = новая Table
   table.StartLine = startLine
   table.EndLine = endLine
   table.Rows = rows
   table.Columns = columns
   table.Headers = headers
   table.Content = content
   table.HasHeaders = len(headers) > 0
   table.TableType = "data"  // Простая классификация

8. RETURN table
```

**Примеры:**

**Простая таблица:**
```markdown
| Name | Age | City |
|------|-----|------|
| John | 30  | NYC  |
| Jane | 25  | LA   |
```
→ Table: Rows=2, Columns=3, Headers=["Name", "Age", "City"]

**Таблица без заголовков:**
```markdown
|------|-----|------|
| John | 30  | NYC  |
| Jane | 25  | LA   |
```
→ Table: Rows=2, Columns=3, Headers=[], HasHeaders=false


### 3.11 Анализ заголовков (AnalyzeHeaders)

Система обнаруживает ATX-стиль заголовков (с символами #).

**Структура Header:**
```go
type Header struct {
    Level     int      // 1-6 (количество #)
    Text      string   // Текст заголовка
    StartLine int
    EndLine   int
    Content   string   // Контент секции под заголовком
    Parent    *Header  // Родительский заголовок
    Children  []Header // Дочерние заголовки
}
```

**Структура HeaderStructure:**
```go
type HeaderStructure struct {
    Headers      []Header         // Все заголовки
    MaxLevel     int              // Максимальный уровень (1-6)
    Hierarchy    map[int][]Header // Заголовки по уровням
    HasStructure bool             // Есть ли четкая структура (>= 3 заголовков)
}
```

**Регулярное выражение:**
```regex
^(#{1,6})\s+(.*)$
```
- Группа 1: уровень заголовка (количество #)
- Группа 2: текст заголовка

**Алгоритм:**
```
1. structure = новая HeaderStructure
   structure.Headers = []
   structure.Hierarchy = {}
   structure.MaxLevel = 0

2. lines = Split(content, "\n")
3. headerRegex = Compile("^(#{1,6})\s+(.*)$")
4. headerStack = []  // Стек для отслеживания иерархии

5. FOR lineNum, line IN lines:
   trimmed = TrimSpace(line)
   matches = headerRegex.FindSubmatch(trimmed)
   
   IF matches != null THEN
      level = len(matches[1])  // Количество #
      text = TrimSpace(matches[2])
      
      header = новый Header
      header.Level = level
      header.Text = text
      header.StartLine = lineNum + 1
      header.EndLine = lineNum + 1
      
      // Устанавливаем родительские связи
      WHILE len(headerStack) > 0 AND headerStack[top].Level >= level:
         headerStack.pop()
      
      IF len(headerStack) > 0 THEN
         parent = headerStack[top]
         header.Parent = parent
         parent.Children.append(header)
      
      headerStack.push(header)
      structure.Headers.append(header)
      
      IF structure.Hierarchy[level] == null THEN
         structure.Hierarchy[level] = []
      structure.Hierarchy[level].append(header)
      
      IF level > structure.MaxLevel THEN
         structure.MaxLevel = level

6. structure.HasStructure = len(structure.Headers) >= 3

7. RETURN structure
```

**Примеры:**

**Простая иерархия:**
```markdown
# Title
## Section 1
### Subsection 1.1
## Section 2
```

Результат:
```
Headers:
  - Level=1, Text="Title", Parent=null
  - Level=2, Text="Section 1", Parent="Title"
  - Level=3, Text="Subsection 1.1", Parent="Section 1"
  - Level=2, Text="Section 2", Parent="Title"

Hierarchy:
  1: ["Title"]
  2: ["Section 1", "Section 2"]
  3: ["Subsection 1.1"]

MaxLevel: 3
HasStructure: true
```

**Плоская структура:**
```markdown
## Section 1
## Section 2
## Section 3
```

Результат:
```
Headers:
  - Level=2, Text="Section 1", Parent=null
  - Level=2, Text="Section 2", Parent=null
  - Level=2, Text="Section 3", Parent=null

Hierarchy:
  2: ["Section 1", "Section 2", "Section 3"]

MaxLevel: 2
HasStructure: true
```


### 3.12 Вычисление соотношений контента (CalculateContentRatios)

Определяет процентное соотношение различных типов контента в документе.

**Алгоритм:**
```
1. totalChars = len([]rune(content))
   IF totalChars == 0 THEN
      RETURN

2. // Подсчитываем символы в блоках кода
   codeChars = 0.0
   FOR EACH block IN codeBlocks:
      codeChars += len([]rune(block.Content))
   
   analysis.CodeRatio = codeChars / totalChars

3. // Подсчитываем символы в списках
   listChars = 0.0
   FOR EACH list IN lists:
      listChars += len([]rune(list.Content))
   
   analysis.ListRatio = listChars / totalChars

4. // Подсчитываем символы в таблицах
   tableChars = 0.0
   FOR EACH table IN tables:
      tableChars += len([]rune(table.Content))
   
   analysis.TableRatio = tableChars / totalChars

5. // Остальное - текст
   analysis.TextRatio = 1.0 - analysis.CodeRatio - analysis.ListRatio - analysis.TableRatio
   
   IF analysis.TextRatio < 0 THEN
      analysis.TextRatio = 0
```

**Примеры:**

**Документ с кодом (1000 символов):**
```
Код: 700 символов
Текст: 300 символов

CodeRatio = 700 / 1000 = 0.7
TextRatio = 300 / 1000 = 0.3
ListRatio = 0.0
TableRatio = 0.0
```

**Смешанный документ (2000 символов):**
```
Код: 600 символов
Списки: 400 символов
Таблицы: 200 символов
Текст: 800 символов

CodeRatio = 600 / 2000 = 0.3
ListRatio = 400 / 2000 = 0.2
TableRatio = 200 / 2000 = 0.1
TextRatio = 800 / 2000 = 0.4
```

### 3.13 Классификация типа контента (GetPrimaryContentType)

Определяет основной тип контента документа на основе соотношений.

**Алгоритм:**
```
1. // Проверяем на смешанный контент (высокий приоритет)
   IF HasMixedContent THEN
      IF CodeRatio > 0.1 AND CodeRatio < 0.8 THEN
         RETURN "mixed"

2. // Проверяем на code_heavy
   IF CodeRatio > 0.7 THEN
      RETURN "code_heavy"

3. // Проверяем на list_heavy
   IF ListRatio > 0.6 AND CodeRatio < 0.3 AND NOT HasMixedContent THEN
      RETURN "list_heavy"

4. // Fallback
   RETURN "primary"
```

**HasMixedContent:**
```
1. contentTypes = 0

2. IF CodeRatio > 0.1 THEN
      contentTypes++
   IF ListRatio > 0.1 THEN
      contentTypes++
   IF TableRatio > 0.1 THEN
      contentTypes++
   IF TextRatio > 0.1 THEN
      contentTypes++

3. RETURN contentTypes >= 3
```

**Примеры:**

**Code Heavy:**
```
CodeRatio = 0.8, TextRatio = 0.2
→ ContentType = "code_heavy"
```

**List Heavy:**
```
ListRatio = 0.7, TextRatio = 0.3, CodeRatio = 0.0
→ ContentType = "list_heavy"
```

**Mixed:**
```
CodeRatio = 0.3, ListRatio = 0.2, TableRatio = 0.15, TextRatio = 0.35
→ HasMixedContent = true (4 типа > 0.1)
→ ContentType = "mixed"
```

**Primary:**
```
TextRatio = 0.9, CodeRatio = 0.05, ListRatio = 0.05
→ ContentType = "primary"
```


### 3.14 Оценка сложности документа (CalculateComplexityScore)

Вычисляет общую оценку сложности документа по шкале 0.0-1.0.

**Формула:**
```
ComplexityScore = StructuralComplexity + ContentComplexity + SizeComplexity
```

**1. Структурная сложность (0-0.3):**
```
StructuralComplexity = HeaderComplexity + ListComplexity + TableComplexity

HeaderComplexity = (MaxHeaderLevel / 6) * 0.1
  // Нормализуем к максимальному уровню 6

ListComplexity = (NestedListDepth / 5) * 0.1
  // Нормализуем к глубине 5

TableComplexity = HasTables ? 0.1 : 0
```

**2. Сложность контента (0-0.4):**
```
ContentComplexity = CodeComplexity + MixedComplexity

CodeComplexity = 
  IF CodeRatio > 0.5 THEN 0.2
  ELSE IF CodeRatio > 0.2 THEN 0.1
  ELSE 0

MixedComplexity = HasMixedContent ? 0.2 : 0
```

**3. Размер документа (0-0.3):**
```
SizeComplexity = 
  IF DocumentSize > 50000 THEN 0.3
  ELSE IF DocumentSize > 20000 THEN 0.2
  ELSE IF DocumentSize > 10000 THEN 0.1
  ELSE 0
```

**Полный алгоритм:**
```
1. score = 0.0

2. // Структурная сложность
   headerComplexity = min(MaxHeaderLevel / 6.0, 1.0) * 0.1
   listComplexity = min(NestedListDepth / 5.0, 1.0) * 0.1
   tableComplexity = HasTables ? 0.1 : 0
   
   structuralComplexity = headerComplexity + listComplexity + tableComplexity
   score += structuralComplexity

3. // Сложность контента
   codeComplexity = 0.0
   IF CodeRatio > 0.5 THEN
      codeComplexity = 0.2
   ELSE IF CodeRatio > 0.2 THEN
      codeComplexity = 0.1
   
   mixedComplexity = HasMixedContent ? 0.2 : 0
   
   contentComplexity = codeComplexity + mixedComplexity
   score += contentComplexity

4. // Размер документа
   sizeComplexity = 0.0
   IF DocumentSize > 50000 THEN
      sizeComplexity = 0.3
   ELSE IF DocumentSize > 20000 THEN
      sizeComplexity = 0.2
   ELSE IF DocumentSize > 10000 THEN
      sizeComplexity = 0.1
   
   score += sizeComplexity

5. // Убеждаемся, что score в диапазоне [0, 1]
   IF score > 1.0 THEN
      score = 1.0

6. RETURN score
```

**Примеры:**

**Простой документ:**
```
DocumentSize = 5000
MaxHeaderLevel = 2
NestedListDepth = 0
HasTables = false
CodeRatio = 0.0
HasMixedContent = false

StructuralComplexity = (2/6)*0.1 + 0 + 0 = 0.033
ContentComplexity = 0 + 0 = 0
SizeComplexity = 0

ComplexityScore = 0.033
```

**Средний документ:**
```
DocumentSize = 15000
MaxHeaderLevel = 3
NestedListDepth = 2
HasTables = true
CodeRatio = 0.3
HasMixedContent = false

StructuralComplexity = (3/6)*0.1 + (2/5)*0.1 + 0.1 = 0.19
ContentComplexity = 0.1 + 0 = 0.1
SizeComplexity = 0.1

ComplexityScore = 0.39
```

**Сложный документ:**
```
DocumentSize = 60000
MaxHeaderLevel = 6
NestedListDepth = 5
HasTables = true
CodeRatio = 0.6
HasMixedContent = true

StructuralComplexity = (6/6)*0.1 + (5/5)*0.1 + 0.1 = 0.3
ContentComplexity = 0.2 + 0.2 = 0.4
SizeComplexity = 0.3

ComplexityScore = 1.0
```

### 3.15 Полный процесс анализа (AnalyzeContent)

Главный метод, который координирует весь процесс анализа.

**Алгоритм:**
```
1. analysis = новый DocumentAnalysis
   analysis.DocumentSize = len([]rune(content))
   analysis.HeaderCount = {}
   analysis.Languages = []

2. // Вычисляем базовые метрики
   analysis.Metrics = CalculateMetrics(content)

3. // Анализируем структурные элементы
   analysis.BlockElements = AnalyzeBlockElements(content)

4. // Анализируем заголовки
   headerStructure = AnalyzeHeaders(content)
   FOR EACH level, headers IN headerStructure.Hierarchy:
      analysis.HeaderCount[level] = len(headers)
   analysis.MaxHeaderLevel = headerStructure.MaxLevel

5. // Обнаруживаем блоки кода
   codeBlocks = DetectCodeBlocks(content)
   analysis.CodeBlockCount = len(codeBlocks)
   analysis.InlineCodeCount = CountInlineCode(content)

6. // Обнаруживаем списки
   lists = DetectLists(content)
   analysis.ListCount = len(lists)
   analysis.NestedListDepth = GetMaxListDepth(lists)
   analysis.HasNestedLists = analysis.NestedListDepth > 1

7. // Обнаруживаем таблицы
   tables = DetectTables(content)
   analysis.TableCount = len(tables)
   analysis.HasTables = analysis.TableCount > 0

8. // Вычисляем соотношения контента
   CalculateContentRatios(content, analysis, codeBlocks, lists, tables)

9. // Определяем языки программирования
   analysis.Languages = ExtractLanguages(codeBlocks)

10. // Определяем тип контента и сложность
    analysis.ContentType = analysis.GetPrimaryContentType()
    analysis.HasMixedContent = HasMixedContent(analysis)
    analysis.ComplexityScore = analysis.CalculateComplexityScore()

11. RETURN analysis
```

Этот процесс обеспечивает полный и детальный анализ документа, который затем используется для выбора оптимальной стратегии разбиения.


## 4. Стратегии разбиения

### 4.1 CodeStrategy (Стратегия кода)

#### 4.1.1 Назначение и применение

CodeStrategy - специализированная стратегия для обработки документов с большим количеством программного кода. Основная цель - сохранить блоки кода атомарными (неразделенными) и поддерживать контекст между кодом и его описанием.

**Когда применяется:**
```
CanHandle возвращает true, если:
1. CodeRatio >= CodeRatioThreshold (по умолчанию 0.7)
   ИЛИ
2. CodeBlockCount >= 3 AND CodeRatio >= 0.3
   ИЛИ
3. len(Languages) > 0 AND CodeRatio >= 0.2
```

**Приоритет:** 1 (самый высокий)

**Ключевые особенности:**
- Блоки кода сохраняются атомарно (не разбиваются)
- Автоматическое определение языка программирования
- Извлечение имен функций и классов
- Оценка сложности кода
- Поддержка oversize блоков (больше MaxChunkSize)

#### 4.1.2 Конфигурация

```go
type CodeStrategyConfig struct {
    MaxChunkSize       int      // 1000 - максимальный размер чанка
    MinChunkSize       int      // 100 - минимальный размер чанка
    MaxFunctionSize    int      // 2000 - максимальный размер функции
    PreserveComments   bool     // true - сохранять комментарии
    OversizeThreshold  int      // 4000 - порог для oversize
    SupportedLanguages []string // Поддерживаемые языки
}
```

**Значения по умолчанию:**
- MaxChunkSize: 1000 символов
- MinChunkSize: 100 символов
- MaxFunctionSize: 2000 символов
- PreserveComments: true
- OversizeThreshold: 4000 символов
- SupportedLanguages: ["go", "python", "javascript", "typescript", "java"]


#### 4.1.3 Алгоритм работы

**Главный алгоритм Apply:**
```
1. chunks = []
2. chunkIndex = 1

3. // Обнаруживаем все блоки кода
   codeBlocks = FindCodeBlocks(content)

4. // Разбиваем документ на секции (код и текст)
   sections = SegmentContentWithCode(content, codeBlocks)

5. FOR EACH section IN sections:
   sectionChunks = ProcessSection(section, file, analysis, config, &chunkIndex)
   chunks.append(sectionChunks)

6. RETURN chunks
```

**FindCodeBlocks (обнаружение блоков кода):**
```
1. blocks = []
2. lines = Split(content, "\n")
3. currentBlock = null
4. inBlock = false

5. FOR lineNum, line IN lines:
   trimmed = TrimSpace(line)
   
   IF trimmed начинается с "```" THEN
      IF NOT inBlock THEN
         // Начало блока
         language = trimmed[3:]  // Все после ```
         currentBlock = новый ExtendedCodeBlock
         currentBlock.StartLine = lineNum + 1
         currentBlock.Language = language
         currentBlock.IsFenced = true
         currentBlock.Content = ""
         inBlock = true
      ELSE
         // Конец блока
         currentBlock.EndLine = lineNum + 1
         currentBlock.Content = TrimSuffix(currentBlock.Content, "\n")
         AnalyzeCodeBlock(currentBlock)
         blocks.append(currentBlock)
         currentBlock = null
         inBlock = false
   
   ELSE IF inBlock AND currentBlock != null THEN
      // Добавляем содержимое к блоку
      IF currentBlock.Content != "" THEN
         currentBlock.Content += "\n"
      currentBlock.Content += line

6. RETURN blocks
```

**AnalyzeCodeBlock (анализ блока кода):**
```
1. IF block.Language == "" THEN
   block.Language = DetectLanguage(block.Content)

2. block.Complexity = CalculateComplexity(block.Content)

3. ExtractStructure(block)
   // Извлекает FunctionName и ClassName
```


#### 4.1.4 Сегментация контента (SegmentContentWithCode)

Разбивает документ на секции, чередуя текст и код.

**Алгоритм:**
```
1. sections = []
2. lines = Split(content, "\n")

3. IF len(codeBlocks) == 0 THEN
   // Нет кода - вся секция текстовая
   RETURN [CodeSection{
      Content: content,
      StartLine: 1,
      EndLine: len(lines),
      Type: "text"
   }]

4. currentLine = 1

5. FOR EACH block IN codeBlocks:
   // Текст перед блоком кода
   IF currentLine < block.StartLine THEN
      textContent = Join(lines[currentLine-1 : block.StartLine-1], "\n")
      IF TrimSpace(textContent) != "" THEN
         sections.append(CodeSection{
            Content: textContent,
            StartLine: currentLine,
            EndLine: block.StartLine - 1,
            Type: "text"
         })
   
   // Блок кода
   codeContent = Join(lines[block.StartLine-1 : block.EndLine], "\n")
   sections.append(CodeSection{
      Content: codeContent,
      StartLine: block.StartLine,
      EndLine: block.EndLine,
      Type: "code",
      CodeBlocks: [block],
      Language: block.Language
   })
   
   currentLine = block.EndLine + 1

6. // Оставшийся текст после последнего блока
   IF currentLine <= len(lines) THEN
      textContent = Join(lines[currentLine-1:], "\n")
      IF TrimSpace(textContent) != "" THEN
         sections.append(CodeSection{
            Content: textContent,
            StartLine: currentLine,
            EndLine: len(lines),
            Type: "text"
         })

7. RETURN sections
```

**Структура CodeSection:**
```go
type CodeSection struct {
    Content    string              // Содержимое секции
    StartLine  int                 // Начальная строка
    EndLine    int                 // Конечная строка
    Type       string              // "text" | "code" | "mixed"
    CodeBlocks []ExtendedCodeBlock // Блоки кода в секции
    Language   string              // Язык (для code секций)
}
```

**Пример:**

**Входной документ:**
```markdown
# API Documentation

This is an introduction.

```python
def hello():
    print("Hello")
```

This is a description.

```go
func main() {
    fmt.Println("Hello")
}
```

End of document.
```

**Результат сегментации:**
```
Section 1: Type="text", Lines=1-3
  "# API Documentation\n\nThis is an introduction."

Section 2: Type="code", Lines=5-7, Language="python"
  "```python\ndef hello():\n    print(\"Hello\")\n```"

Section 3: Type="text", Lines=9-9
  "This is a description."

Section 4: Type="code", Lines=11-14, Language="go"
  "```go\nfunc main() {\n    fmt.Println(\"Hello\")\n}\n```"

Section 5: Type="text", Lines=16-16
  "End of document."
```


#### 4.1.5 Обработка секций (ProcessSection)

**Алгоритм:**
```
1. chunks = []

2. SWITCH section.Type:
   CASE "code":
      chunk = CreateCodeChunk(section, file, analysis, config, chunkIndex)
      chunks.append(chunk)
      chunkIndex++
   
   CASE "text":
      textChunks = SplitTextSection(section, file, analysis, config, &chunkIndex)
      chunks.append(textChunks)

3. RETURN chunks
```

**CreateCodeChunk (создание чанка для кода):**
```
1. metadata = GetStrategyMetadata(analysis, config)

2. IF len(section.CodeBlocks) > 0 THEN
   block = section.CodeBlocks[0]
   metadata["language"] = block.Language
   metadata["function_name"] = block.FunctionName
   metadata["class_name"] = block.ClassName
   metadata["complexity"] = block.Complexity
   metadata["is_fenced"] = block.IsFenced
   
   contentSize = len([]byte(section.Content))
   IF contentSize > MaxChunkSize THEN
      metadata["oversize"] = "true"
      metadata["oversize_single_code_block"] = "true"

3. metadata["chunk_index"] = chunkIndex
   metadata["id"] = CalculateContentHash(section.Content, chunkIndex)
   metadata["path"] = file.Path
   metadata["source_id"] = file.SourceID
   metadata["content_type"] = "code"

4. chunk = CreateChunk(section.Content, section.StartLine, section.EndLine, file, metadata)

5. RETURN chunk
```

**SplitTextSection (разбиение текстовой секции):**
```
1. IF len(section.Content) <= MaxChunkSize THEN
   // Создаем один чанк
   metadata = GetStrategyMetadata(analysis, config)
   metadata["chunk_index"] = chunkIndex
   metadata["id"] = CalculateContentHash(section.Content, chunkIndex)
   metadata["path"] = file.Path
   metadata["source_id"] = file.SourceID
   metadata["content_type"] = "text"
   
   chunk = CreateChunk(section.Content, section.StartLine, section.EndLine, file, metadata)
   chunkIndex++
   RETURN [chunk]

2. // Разбиваем большую секцию
   chunks = []
   parts = SplitBySize(section.Content, MaxChunkSize, true)
   currentLine = section.StartLine
   
   FOR i, part IN parts:
      lines = Split(part, "\n")
      endLine = currentLine + len(lines) - 1
      
      metadata = GetStrategyMetadata(analysis, config)
      metadata["chunk_index"] = chunkIndex
      metadata["id"] = CalculateContentHash(part, chunkIndex)
      metadata["path"] = file.Path
      metadata["source_id"] = file.SourceID
      metadata["content_type"] = "text"
      metadata["split_part"] = i + 1
      metadata["total_parts"] = len(parts)
      
      chunk = CreateChunk(part, currentLine, endLine, file, metadata)
      chunks.append(chunk)
      
      chunkIndex++
      currentLine = endLine + 1
   
   RETURN chunks
```


#### 4.1.6 Извлечение структуры кода (ExtractStructure)

Извлекает имена функций и классов из блока кода.

**Алгоритм:**
```
1. content = block.Content

2. // Извлекаем функции
   IF content содержит "func " ИЛИ "function " ИЛИ "def " THEN
      lines = Split(content, "\n")
      FOR EACH line IN lines:
         IF line содержит ключевое слово функции THEN
            block.FunctionName = ExtractFunctionName(line)
            BREAK

3. // Извлекаем классы
   IF content содержит "class " THEN
      lines = Split(content, "\n")
      FOR EACH line IN lines:
         IF line содержит "class " THEN
            block.ClassName = ExtractClassName(line)
            BREAK
```

**ExtractFunctionName:**
```
1. parts = Split(line, пробелы)

2. FOR i, part IN parts:
   IF part == "func" ИЛИ part == "function" ИЛИ part == "def" THEN
      IF i + 1 < len(parts) THEN
         name = parts[i + 1]
         name = Split(name, "(")[0]  // Убираем параметры
         RETURN name

3. RETURN ""
```

**ExtractClassName:**
```
1. parts = Split(line, пробелы)

2. FOR i, part IN parts:
   IF part == "class" THEN
      IF i + 1 < len(parts) THEN
         name = parts[i + 1]
         name = Split(name, ":")[0]  // Убираем наследование (Python)
         name = Split(name, "{")[0]  // Убираем тело (Go, Java)
         name = TrimSpace(name)
         RETURN name

3. RETURN ""
```

**Примеры:**

**Go:**
```go
func ProcessData(input string) error {
    return nil
}
```
→ FunctionName = "ProcessData"

**Python:**
```python
class DataProcessor:
    def process(self, data):
        pass
```
→ ClassName = "DataProcessor", FunctionName = "process"

**JavaScript:**
```javascript
function calculateSum(a, b) {
    return a + b;
}
```
→ FunctionName = "calculateSum"

**Java:**
```java
public class UserService {
    public void save(User user) {
        // ...
    }
}
```
→ ClassName = "UserService", FunctionName = "save"


#### 4.1.7 Метаданные чанков

CodeStrategy добавляет следующие метаданные к чанкам:

**Общие метаданные:**
```
strategy: "code"
adaptive: "true"
code_ratio: "0.750"
code_blocks_count: "5"
detected_languages: "go,python,javascript"
preserve_functions: "true"
allow_oversize: "true"
chunk_index: 1
id: "hash_value"
path: "path/to/file.md"
source_id: "source_123"
```

**Метаданные для code чанков:**
```
content_type: "code"
language: "python"
function_name: "process_data"
class_name: "DataProcessor"
complexity: 15
is_fenced: "true"
oversize: "true"  // Если размер > MaxChunkSize
oversize_single_code_block: "true"  // Если это один большой блок кода
```

**Метаданные для text чанков:**
```
content_type: "text"
split_part: 1  // Если секция разбита
total_parts: 3  // Общее количество частей
```

#### 4.1.8 Полный пример работы

**Входной документ:**
```markdown
# API Guide

This guide explains our API.

```python
def authenticate(token):
    """Authenticate user with token"""
    if not token:
        raise ValueError("Token required")
    return validate_token(token)
```

The authenticate function validates tokens.

```python
def get_user(user_id):
    """Get user by ID"""
    return database.query(user_id)
```

End of guide.
```

**Результат разбиения:**

**Chunk 1 (text):**
```
Content: "# API Guide\n\nThis guide explains our API."
StartLine: 1
EndLine: 3
Metadata:
  strategy: "code"
  content_type: "text"
  chunk_index: 1
```

**Chunk 2 (code):**
```
Content: "```python\ndef authenticate(token):\n    ...\n```"
StartLine: 5
EndLine: 10
Metadata:
  strategy: "code"
  content_type: "code"
  language: "python"
  function_name: "authenticate"
  complexity: 3
  is_fenced: "true"
  chunk_index: 2
```

**Chunk 3 (text):**
```
Content: "The authenticate function validates tokens."
StartLine: 12
EndLine: 12
Metadata:
  strategy: "code"
  content_type: "text"
  chunk_index: 3
```

**Chunk 4 (code):**
```
Content: "```python\ndef get_user(user_id):\n    ...\n```"
StartLine: 14
EndLine: 17
Metadata:
  strategy: "code"
  content_type: "code"
  language: "python"
  function_name: "get_user"
  complexity: 2
  is_fenced: "true"
  chunk_index: 4
```

**Chunk 5 (text):**
```
Content: "End of guide."
StartLine: 19
EndLine: 19
Metadata:
  strategy: "code"
  content_type: "text"
  chunk_index: 5
```


### 4.2 ListStrategy (Стратегия списков)

#### 4.2.1 Назначение и применение

ListStrategy специализируется на обработке документов с большим количеством списков, сохраняя структуру вложенности и группируя связанные элементы.

**Когда применяется:**
```
CanHandle возвращает true, если:
1. ListCount >= ListCountThreshold (по умолчанию 5) AND CodeRatio < 0.3
   ИЛИ
2. ListRatio > 0.6
   ИЛИ
3. HasNestedLists AND ListCount >= 3
```

**Приоритет:** 3

**Ключевые особенности:**
- Группирует связанные элементы списков
- Сохраняет структуру вложенности
- Разбивает по заголовкам если есть
- Поддерживает все типы списков (ordered, unordered, task)

#### 4.2.2 Конфигурация

```go
type ListStrategyConfig struct {
    MaxChunkSize      int  // 300 - максимальный размер чанка
    MinChunkSize      int  // 50 - минимальный размер чанка
    PreserveNesting   bool // true - сохранять вложенность
    MaxItemsPerChunk  int  // 10 - максимум элементов в чанке
    MinItemsThreshold int  // 5 - минимум элементов для применения
    MaxItemSize       int  // 1000 - максимальный размер элемента
}
```

#### 4.2.3 Алгоритм работы

**Главный алгоритм:**
```
1. sections = ParseDocumentSections(content)
   // Разбивает по заголовкам и обнаруживает списки

2. FOR EACH section IN sections:
   IF section содержит списки THEN
      IF размер секции <= MaxChunkSize THEN
         Создать один чанк для всей секции
      ELSE
         Группировать элементы списка в чанки
         Сохранять вложенность
   ELSE
      Обработать как текст

3. RETURN chunks
```

**Метаданные чанков:**
```
strategy: "list"
list_type: "ordered" | "unordered" | "task" | "mixed"
item_count: количество элементов
nesting_depth: глубина вложенности
preserve_nesting: "true"
```

**Пример:**

**Входной документ:**
```markdown
## Features

- Feature 1
  - Sub-feature 1.1
  - Sub-feature 1.2
- Feature 2
- Feature 3
```

**Результат:**
```
Chunk 1:
  Content: "## Features\n\n- Feature 1\n  - Sub-feature 1.1\n  - Sub-feature 1.2\n- Feature 2\n- Feature 3"
  Metadata:
    strategy: "list"
    list_type: "unordered"
    item_count: 5
    nesting_depth: 2
```


### 4.3 TableStrategy (Стратегия таблиц)

#### 4.3.1 Назначение и применение

TableStrategy обрабатывает документы с таблицами, сохраняя их структуру и при необходимости разбивая большие таблицы с сохранением заголовков.

**Когда применяется:**
```
CanHandle возвращает true, если:
1. TableCount >= 2
   ИЛИ
2. TableRatio > 0.4
   ИЛИ
3. TableCount >= 1 AND TableRatio > 0.2
```

**Приоритет:** 4

**Ключевые особенности:**
- Сохраняет структуру таблиц
- Разбивает большие таблицы по строкам
- Сохраняет заголовки при разбиении
- Группирует таблицы с контекстом

#### 4.3.2 Конфигурация

```go
type TableStrategyConfig struct {
    MaxTableSize      int  // 8192 - максимальный размер таблицы
    PreserveHeaders   bool // true - сохранять заголовки
    SplitLargeTables  bool // true - разбивать большие таблицы
    MaxRowsPerChunk   int  // 10 - максимум строк в чанке
}
```

#### 4.3.3 Алгоритм разбиения больших таблиц

```
1. IF размер таблицы <= MaxTableSize THEN
   Создать один чанк

2. ELSE IF SplitLargeTables = true THEN
   rows = таблица.Rows
   headerRow = таблица.Headers
   
   chunks = []
   currentRows = []
   
   FOR EACH row IN rows:
      currentRows.append(row)
      
      IF len(currentRows) >= MaxRowsPerChunk THEN
         IF PreserveHeaders THEN
            content = headerRow + separatorRow + currentRows
         ELSE
            content = currentRows
         
         chunks.append(CreateChunk(content))
         currentRows = []
   
   IF len(currentRows) > 0 THEN
      chunks.append(CreateChunk(headerRow + separatorRow + currentRows))

3. ELSE
   Создать oversize чанк
```

**Метаданные чанков:**
```
strategy: "table"
table_type: "data" | "comparison" | "configuration"
row_count: количество строк
column_count: количество колонок
has_headers: "true" | "false"
table_headers: "Header1,Header2,Header3"
```

**Пример:**

**Входной документ:**
```markdown
| Name | Age | City |
|------|-----|------|
| John | 30  | NYC  |
| Jane | 25  | LA   |
```

**Результат:**
```
Chunk 1:
  Content: "| Name | Age | City |\n|------|-----|------|\n| John | 30  | NYC  |\n| Jane | 25  | LA   |"
  Metadata:
    strategy: "table"
    table_type: "data"
    row_count: 2
    column_count: 3
    has_headers: "true"
    table_headers: "Name,Age,City"
```


### 4.4 MixedStrategy (Стратегия смешанного контента)

#### 4.4.1 Назначение и применение

MixedStrategy - самая сложная стратегия, которая обрабатывает документы со смешанным контентом (код + текст + списки + таблицы), адаптивно выбирая подход для каждого элемента.

**Когда применяется:**
```
CanHandle возвращает true, если:
1. HasMixedContent = true
   ИЛИ
2. CodeRatio >= 0.3 AND CodeRatio <= 0.7 AND HasSignificantStructure
   ИЛИ
3. Есть 2+ разных типа элементов (код, списки, таблицы, текст)
```

**Приоритет:** 2 (второй после CodeStrategy)

**Ключевые особенности:**
- Обнаруживает все типы элементов
- Группирует связанные элементы
- Сохраняет контекст между элементами
- Адаптивно разбивает с учетом типа контента

#### 4.4.2 Конфигурация

```go
type MixedStrategyConfig struct {
    MaxChunkSize        int     // 400 - максимальный размер чанка
    AdaptiveThreshold   float64 // 0.3 - порог для адаптивности
    PreserveCodeBlocks  bool    // true - сохранять блоки кода
    CodeTextBalance     float64 // 0.3 - баланс код/текст
    ContextOverlap      int     // 200 - перекрытие для контекста
}
```

#### 4.4.3 Алгоритм работы

```
1. // Обнаруживаем все элементы
   elements = []
   elements.append(FindHeaders(content))
   elements.append(FindCodeBlocks(content))
   elements.append(FindLists(content))
   elements.append(FindTables(content))
   elements.append(FindTextBlocks(content))

2. // Сортируем по позиции
   Sort(elements, by: StartLine)

3. // Группируем элементы в секции
   sections = []
   currentSection = null
   
   FOR EACH element IN elements:
      IF element.Type == "header" THEN
         // Заголовок начинает новую секцию
         IF currentSection != null THEN
            sections.append(currentSection)
         currentSection = новая Section
         currentSection.Header = element
      ELSE
         // Добавляем элемент к текущей секции
         currentSection.Elements.append(element)

4. // Обрабатываем каждую секцию
   FOR EACH section IN sections:
      IF размер секции <= MaxChunkSize THEN
         Создать один чанк
      ELSE IF ContextFlow = true THEN
         Разбить с сохранением контекста (overlap)
      ELSE
         Разбить по элементам

5. RETURN chunks
```

**Метаданные чанков:**
```
strategy: "mixed"
section_type: "header_with_content" | "code_with_explanation" | "mixed_elements"
dominant_type: тип доминирующего контента
has_code: "true" | "false"
has_lists: "true" | "false"
has_tables: "true" | "false"
has_headers: "true" | "false"
context_flow: "true" | "false"
element_count: количество элементов
```

**Пример:**

**Входной документ:**
```markdown
## API Usage

To use the API:

1. Get an API key
2. Make a request

```python
import requests
response = requests.get(url, headers=headers)
```

The response contains:

| Field | Type | Description |
|-------|------|-------------|
| id    | int  | User ID     |
| name  | str  | User name   |
```

**Результат:**
```
Chunk 1:
  Content: "## API Usage\n\nTo use the API:\n\n1. Get an API key\n2. Make a request"
  Metadata:
    strategy: "mixed"
    section_type: "header_with_content"
    has_lists: "true"
    has_headers: "true"
    element_count: 2

Chunk 2:
  Content: "```python\nimport requests\nresponse = requests.get(url, headers=headers)\n```"
  Metadata:
    strategy: "mixed"
    section_type: "code_with_explanation"
    has_code: "true"
    dominant_type: "code"

Chunk 3:
  Content: "The response contains:\n\n| Field | Type | Description |\n..."
  Metadata:
    strategy: "mixed"
    section_type: "mixed_elements"
    has_tables: "true"
    element_count: 2
```


### 4.5 StructuralStrategy (Структурная стратегия)

#### 4.5.1 Назначение и применение

StructuralStrategy разбивает документы по заголовкам, сохраняя иерархическую структуру документа.

**Когда применяется:**
```
CanHandle возвращает true, если:
1. TotalHeaders >= 3
   ИЛИ
2. MaxHeaderLevel >= 3 AND TotalHeaders >= 2
   ИЛИ
3. HasSignificantStructure AND CodeRatio < 0.3
```

**Приоритет:** 5

**Ключевые особенности:**
- Разбивает по заголовкам
- Сохраняет иерархию заголовков
- Группирует короткие секции
- Разбивает длинные секции по подзаголовкам

#### 4.5.2 Конфигурация

```go
type StructuralStrategyConfig struct {
    MaxSectionSize       int  // 4000 - максимальный размер секции
    MinSectionSize       int  // 200 - минимальный размер секции
    RespectHeaderLevels  bool // true - учитывать уровни заголовков
    MaxHeaderLevel       int  // 3 - максимальный уровень для разбиения
    CombineShortSections bool // true - объединять короткие секции
}
```

#### 4.5.3 Алгоритм работы

```
1. // Находим все заголовки
   headers = FindHeaders(content)

2. // Строим иерархию
   hierarchy = BuildHierarchy(headers)

3. // Создаем секции
   sections = []
   
   // Преамбула (если есть)
   IF есть контент до первого заголовка THEN
      sections.append(PreambleSection)
   
   // Секция для каждого заголовка
   FOR EACH header IN headers:
      section = новая Section
      section.Header = header
      section.Content = контент от header до следующего header
      sections.append(section)

4. // Обрабатываем каждую секцию
   FOR EACH section IN sections:
      IF размер <= MaxSectionSize THEN
         Создать один чанк
      ELSE IF есть подзаголовки THEN
         Разбить по подзаголовкам
      ELSE
         Разбить по размеру

5. RETURN chunks
```

**Метаданные чанков:**
```
strategy: "structural"
section_type: "section" | "subsection" | "subsubsection"
header_text: текст заголовка
header_level: уровень заголовка (1-6)
header_hierarchy: "Title > Section > Subsection"
parent_header: родительский заголовок
children_count: количество дочерних секций
is_leaf: "true" | "false"
```

**Пример:**

**Входной документ:**
```markdown
# Documentation

## Introduction

This is the introduction.

## Features

### Feature 1

Description of feature 1.

### Feature 2

Description of feature 2.

## Conclusion

Final thoughts.
```

**Результат:**
```
Chunk 1:
  Content: "## Introduction\n\nThis is the introduction."
  Metadata:
    strategy: "structural"
    section_type: "section"
    header_text: "Introduction"
    header_level: 2
    header_hierarchy: "Documentation > Introduction"
    parent_header: "Documentation"
    is_leaf: "true"

Chunk 2:
  Content: "### Feature 1\n\nDescription of feature 1."
  Metadata:
    strategy: "structural"
    section_type: "subsection"
    header_text: "Feature 1"
    header_level: 3
    header_hierarchy: "Documentation > Features > Feature 1"
    parent_header: "Features"
    is_leaf: "true"

Chunk 3:
  Content: "### Feature 2\n\nDescription of feature 2."
  Metadata:
    strategy: "structural"
    section_type: "subsection"
    header_text: "Feature 2"
    header_level: 3
    header_hierarchy: "Documentation > Features > Feature 2"
    parent_header: "Features"
    is_leaf: "true"

Chunk 4:
  Content: "## Conclusion\n\nFinal thoughts."
  Metadata:
    strategy: "structural"
    section_type: "section"
    header_text: "Conclusion"
    header_level: 2
    header_hierarchy: "Documentation > Conclusion"
    parent_header: "Documentation"
    is_leaf: "true"
```


### 4.6 SentencesStrategy (Стратегия предложений - Fallback)

#### 4.6.1 Назначение и применение

SentencesStrategy - это fallback стратегия, которая применяется когда другие стратегии не подходят. Разбивает текст на предложения и группирует их в чанки.

**Когда применяется:**
```
CanHandle возвращает true ВСЕГДА
(используется как fallback)
```

**Приоритет:** 6 (самый низкий)

**Ключевые особенности:**
- Разбивает текст на предложения
- Группирует предложения в чанки
- Сохраняет границы параграфов
- Добавляет перекрытие между чанками

#### 4.6.2 Конфигурация

```go
type SentencesStrategyConfig struct {
    TargetChunkSize        int  // 1500 - целевой размер чанка
    PreserveParagraphs     bool // true - сохранять параграфы
    SentenceOverlap        int  // 1 - количество предложений для перекрытия
    MaxSentencesPerChunk   int  // 3 - максимум предложений в чанке
}
```

#### 4.6.3 Алгоритм работы

```
1. // Разбиваем текст на параграфы
   paragraphs = Split(content, "\n\n")

2. // Разбиваем каждый параграф на предложения
   sentences = []
   FOR EACH paragraph IN paragraphs:
      paragraphSentences = SplitSentences(paragraph)
      sentences.append(paragraphSentences)

3. // Группируем предложения в чанки
   chunks = []
   currentChunk = ""
   previousSentences = []
   
   FOR EACH sentence IN sentences:
      IF размер(currentChunk + sentence) > TargetChunkSize THEN
         // Сохраняем текущий чанк
         chunks.append(CreateChunk(currentChunk))
         
         // Начинаем новый чанк с перекрытием
         IF SentenceOverlap > 0 THEN
            overlapSentences = последние N предложений из previousSentences
            currentChunk = Join(overlapSentences) + sentence
         ELSE
            currentChunk = sentence
      ELSE
         currentChunk += sentence
      
      previousSentences.append(sentence)

4. IF currentChunk != "" THEN
   chunks.append(CreateChunk(currentChunk))

5. RETURN chunks
```

**SplitSentences (разбиение на предложения):**
```
1. // Используем регулярное выражение для поиска границ предложений
   pattern = "[.!?][\s\n]"
   
2. sentences = []
   currentSentence = ""
   
   FOR EACH char IN text:
      currentSentence += char
      
      IF char соответствует pattern THEN
         sentences.append(TrimSpace(currentSentence))
         currentSentence = ""
   
   IF currentSentence != "" THEN
      sentences.append(TrimSpace(currentSentence))

3. RETURN sentences
```

**Метаданные чанков:**
```
strategy: "sentences"
sentence_count: количество предложений
word_count: количество слов
avg_words_per_sentence: среднее количество слов
text_complexity: оценка сложности
fallback_strategy: "true"
```

**Пример:**

**Входной документ:**
```markdown
This is the first sentence. This is the second sentence. This is the third sentence.

This is a new paragraph. It has multiple sentences. Each sentence is important.
```

**Результат:**
```
Chunk 1:
  Content: "This is the first sentence. This is the second sentence. This is the third sentence."
  Metadata:
    strategy: "sentences"
    sentence_count: 3
    word_count: 18
    avg_words_per_sentence: 6
    fallback_strategy: "true"

Chunk 2:
  Content: "This is the third sentence. This is a new paragraph. It has multiple sentences."
  Metadata:
    strategy: "sentences"
    sentence_count: 3
    word_count: 16
    avg_words_per_sentence: 5.3
    fallback_strategy: "true"
    has_overlap: "true"
    overlap_size: 30

Chunk 3:
  Content: "It has multiple sentences. Each sentence is important."
  Metadata:
    strategy: "sentences"
    sentence_count: 2
    word_count: 9
    avg_words_per_sentence: 4.5
    fallback_strategy: "true"
```


## 5. Выбор стратегии (StrategySelector)

### 5.1 Назначение

StrategySelector - компонент, который выбирает оптимальную стратегию разбиения на основе анализа документа. Это критически важный компонент, который определяет качество итогового разбиения.

### 5.2 Режимы выбора

**1. Strict Mode (строгий режим):**
- Выбирает стратегию только по приоритету
- Игнорирует оценку качества
- Используется когда нужна предсказуемость
- Конфигурация: `PriorityMode = "strict"`

**2. Weighted Mode (взвешенный режим - по умолчанию):**
- Комбинирует приоритет и оценку качества
- Формула: `WeightedScore = (1.0/Priority)*0.5 + QualityScore*0.5`
- Позволяет качеству влиять на выбор
- Конфигурация: `PriorityMode = "weighted"`

### 5.3 Полный алгоритм выбора

```
1. candidates = []

2. FOR EACH зарегистрированная стратегия:
   a. canHandle = strategy.CanHandle(analysis, config)
   
   b. IF canHandle THEN
      qualityScore = EvaluateStrategy(strategy, analysis)
      priority = strategy.GetPriority()
      
      candidate = новый Candidate
      candidate.Strategy = strategy
      candidate.QualityScore = qualityScore
      candidate.Priority = priority
      
      candidates.append(candidate)

3. IF len(candidates) == 0 THEN
   RETURN error "no viable strategies"

4. IF config.PriorityMode == "strict" THEN
   // Сортируем только по приоритету (меньше = выше)
   Sort(candidates, by: Priority ASC)
   RETURN candidates[0].Strategy

5. ELSE IF config.PriorityMode == "weighted" THEN
   // Вычисляем взвешенную оценку
   FOR EACH candidate IN candidates:
      priorityWeight = 1.0 / candidate.Priority
      candidate.WeightedScore = priorityWeight * 0.5 + candidate.QualityScore * 0.5
   
   // Сортируем по взвешенной оценке (больше = лучше)
   Sort(candidates, by: WeightedScore DESC)
   RETURN candidates[0].Strategy

6. ELSE
   RETURN error "unknown priority mode"
```

### 5.4 Оценка стратегий (EvaluateStrategy)

Каждая стратегия оценивается по шкале 0.0-1.0 на основе характеристик документа.

**CodeStrategy:**
```
score = 0.0

IF CodeRatio > 0.7 THEN
   score += 0.8
ELSE IF CodeRatio > 0.5 THEN
   score += 0.6
ELSE IF CodeRatio > 0.3 THEN
   score += 0.3

IF CodeBlockCount >= 5 THEN
   score += 0.2
ELSE IF CodeBlockCount >= 2 THEN
   score += 0.1

IF len(Languages) > 1 THEN
   score += 0.1

RETURN min(score, 1.0)
```

**ListStrategy:**
```
score = 0.0

IF ListCount >= 5 THEN
   score += 0.8
ELSE IF ListCount >= 3 THEN
   score += 0.5
ELSE IF ListCount >= 1 THEN
   score += 0.2

IF HasNestedLists THEN
   score += 0.2

IF ListRatio > 0.6 THEN
   score += 0.3
ELSE IF ListRatio > 0.3 THEN
   score += 0.15

RETURN min(score, 1.0)
```

**TableStrategy:**
```
score = 0.0

IF TableCount >= 2 THEN
   score += 0.8
ELSE IF TableCount >= 1 THEN
   score += 0.6

IF TableRatio > 0.4 THEN
   score += 0.3
ELSE IF TableRatio > 0.2 THEN
   score += 0.15

RETURN min(score, 1.0)
```

**MixedStrategy:**
```
score = 0.0

// Снижаем приоритет если доминирует один тип
IF TableRatio > 0.6 OR CodeRatio > 0.7 OR ListRatio > 0.7 THEN
   RETURN 0.2

IF HasMixedContent THEN
   score += 0.7

IF CodeRatio >= 0.3 AND CodeRatio <= 0.7 THEN
   score += 0.3

// Подсчитываем разнообразие типов
elementTypes = 0
IF CodeRatio > 0.1 THEN elementTypes++
IF ListRatio > 0.1 THEN elementTypes++
IF TableRatio > 0.1 THEN elementTypes++
IF TextRatio > 0.3 THEN elementTypes++

IF elementTypes >= 3 THEN
   score += 0.2
ELSE IF elementTypes >= 2 THEN
   score += 0.1

RETURN min(score, 1.0)
```

**StructuralStrategy:**
```
score = 0.0
TotalHeaders = sum(HeaderCount values)

IF TotalHeaders >= 3 THEN
   score += 0.7
ELSE IF TotalHeaders >= 2 THEN
   score += 0.4

IF MaxHeaderLevel >= 3 THEN
   score += 0.2
ELSE IF MaxHeaderLevel >= 2 THEN
   score += 0.1

IF HasSignificantStructure() THEN
   score += 0.2

RETURN min(score, 1.0)
```

**SentencesStrategy:**
```
score = 0.0

IF TextRatio > 0.8 THEN
   score += 0.8
ELSE IF TextRatio > 0.6 THEN
   score += 0.6
ELSE IF TextRatio > 0.4 THEN
   score += 0.3

IF ComplexityScore < 0.3 THEN
   score += 0.2

score += 0.1  // Базовая оценка как fallback

RETURN min(score, 1.0)
```


### 5.5 Примеры выбора стратегии

#### Пример 1: Документ с кодом

**Анализ документа:**
```
CodeRatio = 0.8
CodeBlockCount = 5
Languages = ["python", "go"]
ListCount = 1
TableCount = 0
TotalHeaders = 2
```

**Оценка стратегий:**
```
CodeStrategy:
  CanHandle: true (CodeRatio >= 0.7)
  QualityScore: 0.8 + 0.2 + 0.1 = 1.0
  Priority: 1
  WeightedScore: (1.0/1)*0.5 + 1.0*0.5 = 1.0

MixedStrategy:
  CanHandle: false (CodeRatio > 0.7, доминирует код)
  
StructuralStrategy:
  CanHandle: false (CodeRatio >= 0.3)

SentencesStrategy:
  CanHandle: true (всегда)
  QualityScore: 0.1 (fallback)
  Priority: 6
  WeightedScore: (1.0/6)*0.5 + 0.1*0.5 = 0.217
```

**Выбранная стратегия:** CodeStrategy (WeightedScore = 1.0)

#### Пример 2: Смешанный документ

**Анализ документа:**
```
CodeRatio = 0.4
ListRatio = 0.2
TableRatio = 0.1
TextRatio = 0.3
HasMixedContent = true
CodeBlockCount = 3
ListCount = 4
TableCount = 1
TotalHeaders = 5
```

**Оценка стратегий:**
```
CodeStrategy:
  CanHandle: true (CodeBlockCount >= 3 AND CodeRatio >= 0.3)
  QualityScore: 0.3 + 0.1 = 0.4
  Priority: 1
  WeightedScore: (1.0/1)*0.5 + 0.4*0.5 = 0.7

MixedStrategy:
  CanHandle: true (HasMixedContent = true)
  QualityScore: 0.7 + 0.3 + 0.2 = 1.0 (4 типа элементов)
  Priority: 2
  WeightedScore: (1.0/2)*0.5 + 1.0*0.5 = 0.75

ListStrategy:
  CanHandle: false (ListCount < 5)

StructuralStrategy:
  CanHandle: true (TotalHeaders >= 3)
  QualityScore: 0.7 + 0.2 = 0.9
  Priority: 5
  WeightedScore: (1.0/5)*0.5 + 0.9*0.5 = 0.55
```

**Выбранная стратегия:** MixedStrategy (WeightedScore = 0.75)

#### Пример 3: Структурированный документ

**Анализ документа:**
```
CodeRatio = 0.05
ListRatio = 0.1
TextRatio = 0.85
TotalHeaders = 8
MaxHeaderLevel = 4
HasSignificantStructure = true
```

**Оценка стратегий:**
```
CodeStrategy:
  CanHandle: false (CodeRatio < 0.2)

ListStrategy:
  CanHandle: false (ListCount < 3)

StructuralStrategy:
  CanHandle: true (TotalHeaders >= 3)
  QualityScore: 0.7 + 0.2 + 0.2 = 1.0
  Priority: 5
  WeightedScore: (1.0/5)*0.5 + 1.0*0.5 = 0.6

SentencesStrategy:
  CanHandle: true (всегда)
  QualityScore: 0.8 + 0.1 = 0.9
  Priority: 6
  WeightedScore: (1.0/6)*0.5 + 0.9*0.5 = 0.533
```

**Выбранная стратегия:** StructuralStrategy (WeightedScore = 0.6)

### 5.6 Сравнение режимов

**Strict Mode:**
```
Документ: CodeRatio=0.4, ListRatio=0.5, TotalHeaders=5

Кандидаты:
1. CodeStrategy (Priority=1, QualityScore=0.4)
2. MixedStrategy (Priority=2, QualityScore=0.8)
3. StructuralStrategy (Priority=5, QualityScore=0.9)

Выбор: CodeStrategy (Priority=1)
```

**Weighted Mode:**
```
Документ: CodeRatio=0.4, ListRatio=0.5, TotalHeaders=5

Кандидаты:
1. CodeStrategy (Priority=1, QualityScore=0.4, WeightedScore=0.7)
2. MixedStrategy (Priority=2, QualityScore=0.8, WeightedScore=0.65)
3. StructuralStrategy (Priority=5, QualityScore=0.9, WeightedScore=0.55)

Выбор: CodeStrategy (WeightedScore=0.7)
```

В этом примере оба режима выбрали одну стратегию, но weighted mode учитывает качество, что может привести к другому выбору в пограничных случаях.


## 6. Обработка специальных случаев

### 6.1 PreambleHandler (Обработчик преамбулы)

#### 6.1.1 Назначение

PreambleHandler обрабатывает контент, который находится до первого заголовка в документе. Это может быть введение, метаданные, или описание документа.

#### 6.1.2 Конфигурация

```go
type PreambleConfig struct {
    Enabled            bool   // true - включить обработку
    MaxSize            int    // 4096 - максимальный размер преамбулы
    SplitStrategy      string // "sentences" - стратегия разбиения
    PreserveFormatting bool   // true - сохранять форматирование
    MinSize            int    // 100 - минимальный размер
}
```

#### 6.1.3 Алгоритм

```
1. // Находим первый заголовок
   firstHeaderLine = FindFirstHeader(content)
   
   IF firstHeaderLine == 0 THEN
      // Нет заголовков - нет преамбулы
      RETURN null

2. // Извлекаем преамбулу
   preamble = content[0 : firstHeaderLine]
   
   IF len(TrimSpace(preamble)) < MinSize THEN
      // Преамбула слишком маленькая
      RETURN null

3. // Обрабатываем преамбулу
   IF len(preamble) <= MaxSize THEN
      // Создаем один чанк
      chunk = CreateChunk(preamble)
      chunk.Metadata["type"] = "preamble"
      chunk.Metadata["is_introduction"] = DetermineIfIntroduction(preamble)
      RETURN [chunk]
   
   ELSE
      // Разбиваем большую преамбулу
      IF SplitStrategy == "sentences" THEN
         chunks = SplitBySentences(preamble, MaxSize)
      ELSE
         chunks = SplitBySize(preamble, MaxSize)
      
      FOR EACH chunk IN chunks:
         chunk.Metadata["type"] = "preamble"
         chunk.Metadata["split"] = "true"
      
      RETURN chunks
```

**Пример:**

**Входной документ:**
```markdown
This document describes the API. It provides comprehensive information about all endpoints and their usage.

# Introduction

The API allows...
```

**Результат:**
```
Chunk (Preamble):
  Content: "This document describes the API. It provides comprehensive information about all endpoints and their usage."
  Metadata:
    type: "preamble"
    is_introduction: "true"
    split: "false"
```


### 6.2 OverlapProcessor (Процессор перекрытия)

#### 6.2.1 Назначение

OverlapProcessor создает перекрытие между соседними чанками для сохранения контекста. Это критически важно для RAG систем, где контекст между чанками может быть потерян.

#### 6.2.2 Конфигурация

```go
type OverlapConfig struct {
    Enabled                 bool    // true - включить перекрытие
    AbsoluteOverlap         int     // 200 - абсолютный размер перекрытия
    RespectBoundaries       bool    // true - учитывать границы
    PreferParagraphBoundary bool    // true - предпочитать границы параграфов
    PreferSentenceBoundary  bool    // true - предпочитать границы предложений
    MaxOverlapRatio         float64 // 0.3 - максимум 30% от размера чанка
    MinOverlapSize          int     // 50 - минимальный размер перекрытия
}
```

#### 6.2.3 Алгоритм

```
1. FOR i = 0 TO len(chunks) - 2:
   chunk1 = chunks[i]
   chunk2 = chunks[i + 1]
   
   // Вычисляем размер перекрытия
   overlapSize = CalculateOverlapSize(chunk1, chunk2, config)
   
   // Извлекаем перекрытие из конца chunk1
   overlap = ExtractOverlap(chunk1, overlapSize, config)
   
   // Добавляем перекрытие в начало chunk2
   chunk2.Content = overlap + chunk2.Content
   chunk2.Metadata["has_overlap"] = "true"
   chunk2.Metadata["overlap_size"] = overlapSize

2. RETURN chunks
```

**CalculateOverlapSize:**
```
1. // Базовый размер перекрытия
   overlapSize = min(AbsoluteOverlap, len(chunk1.Content) * MaxOverlapRatio)

2. // Убеждаемся, что не меньше минимума
   overlapSize = max(overlapSize, MinOverlapSize)

3. // Убеждаемся, что не больше размера chunk1
   overlapSize = min(overlapSize, len(chunk1.Content))

4. RETURN overlapSize
```

**ExtractOverlap:**
```
1. content = chunk1.Content
   targetSize = overlapSize

2. IF RespectBoundaries THEN
   // Ищем ближайшую границу
   boundaries = []
   
   IF PreferParagraphBoundary THEN
      boundaries.append(FindParagraphBoundaries(content))
   
   IF PreferSentenceBoundary THEN
      boundaries.append(FindSentenceBoundaries(content))
   
   // Находим ближайшую границу к targetSize
   bestBoundary = FindClosestBoundary(boundaries, len(content) - targetSize)
   
   IF bestBoundary != -1 THEN
      overlapStart = bestBoundary
   ELSE
      overlapStart = len(content) - targetSize
ELSE
   overlapStart = len(content) - targetSize

3. overlap = content[overlapStart:]

4. RETURN overlap
```

**FindParagraphBoundaries:**
```
1. boundaries = []
2. lines = Split(content, "\n")
3. position = 0

4. FOR i, line IN lines:
   IF i > 0 AND lines[i-1] == "" AND line != "" THEN
      // Начало нового параграфа
      boundaries.append(position)
   position += len(line) + 1  // +1 для \n

5. RETURN boundaries
```

**FindSentenceBoundaries:**
```
1. boundaries = []
2. pattern = "[.!?][\s\n]"

3. FOR match IN FindAllMatches(pattern, content):
   boundaries.append(match.End)

4. RETURN boundaries
```

**Пример:**

**Входные чанки:**
```
Chunk 1:
  "This is the first paragraph. It has multiple sentences. This is important context."

Chunk 2:
  "This is the second paragraph. It continues the discussion."
```

**После обработки:**
```
Chunk 1:
  "This is the first paragraph. It has multiple sentences. This is important context."
  (без изменений)

Chunk 2:
  "This is important context. This is the second paragraph. It continues the discussion."
  Metadata:
    has_overlap: "true"
    overlap_size: 28
```


### 6.3 ErrorHandler и FallbackChain

#### 6.3.1 Категории ошибок

1. **Input Validation** - невалидный вход
   - Пустой контент
   - Невалидная кодировка
   - Отсутствующий файл

2. **Processing Errors** - ошибки обработки
   - Ошибки парсинга
   - Превышение лимитов памяти
   - Таймауты

3. **Strategy Failures** - ошибки стратегии
   - Стратегия не может обработать
   - Ошибка в алгоритме стратегии
   - Невалидный результат

4. **Resource Limits** - превышение лимитов
   - Слишком большой файл
   - Слишком много чанков
   - Превышение времени обработки

#### 6.3.2 Стратегии восстановления

**1. CleanAndRetry:**
```
1. Очистить контент:
   - Удалить невалидные символы
   - Нормализовать переносы строк
   - Удалить BOM

2. Повторить обработку

3. IF успешно THEN
   Добавить metadata["recovery"] = "clean_and_retry"
   RETURN результат
ELSE
   Попробовать следующую стратегию восстановления
```

**2. FallbackStrategy:**
```
1. Получить список стратегий по убыванию приоритета

2. FOR EACH strategy IN strategies:
   TRY:
      result = strategy.Apply(content)
      IF result валиден THEN
         Добавить metadata["recovery"] = "fallback_strategy"
         Добавить metadata["fallback_from"] = original_strategy
         RETURN result
   CATCH error:
      CONTINUE

3. IF все стратегии не сработали THEN
   Попробовать EmergencyFallback
```

**3. PartialResults:**
```
1. IF есть частичные результаты THEN
   Добавить metadata["recovery"] = "partial_results"
   Добавить metadata["partial"] = "true"
   Добавить metadata["error"] = error_message
   RETURN частичные результаты

2. ELSE
   Попробовать EmergencyFallback
```

**4. EmergencyFallback:**
```
1. // Базовое разбиение по размеру
   chunks = []
   parts = SplitBySize(content, MaxChunkSize, respectBoundaries=false)
   
   FOR i, part IN parts:
      chunk = CreateChunk(part)
      chunk.Metadata["recovery"] = "emergency_fallback"
      chunk.Metadata["emergency"] = "true"
      chunks.append(chunk)

2. RETURN chunks
```

#### 6.3.3 Алгоритм обработки ошибок

```
1. TRY:
   result = ProcessContent(content)
   RETURN result

2. CATCH error:
   category = DetermineErrorCategory(error)
   
   SWITCH category:
      CASE "input_validation":
         strategy = CleanAndRetry
      CASE "processing_error":
         strategy = FallbackStrategy
      CASE "strategy_failure":
         strategy = FallbackStrategy
      CASE "resource_limits":
         strategy = PartialResults
      DEFAULT:
         strategy = EmergencyFallback
   
   result = ApplyRecoveryStrategy(strategy, content, error)
   
   IF result != null THEN
      RETURN result
   ELSE
      RETURN error
```


### 6.4 StreamingProcessor (Потоковый процессор)

#### 6.4.1 Назначение

StreamingProcessor обрабатывает большие файлы (>10MB) потоково, разбивая их на окна и обрабатывая каждое окно отдельно для экономии памяти.

#### 6.4.2 Конфигурация

```go
type StreamingConfig struct {
    StreamingThreshold int64 // 10MB - порог для потоковой обработки
    ChunkSize          int64 // 1MB - размер окна обработки
    BufferSize         int   // 64KB - размер буфера чтения
    MaxMemoryUsage     int64 // 100MB - максимальное использование памяти
}
```

#### 6.4.3 Алгоритм

```
1. fileSize = GetFileSize(file)

2. IF fileSize <= StreamingThreshold THEN
   // Обычная обработка
   content = ReadFile(file)
   RETURN ProcessContent(content)

3. // Потоковая обработка
   reader = OpenFileReader(file)
   allChunks = []
   windowStart = 0

4. WHILE NOT EOF:
   // Читаем окно
   window = ReadWindow(reader, ChunkSize)
   
   // Находим безопасную границу для разрыва
   boundary = FindSafeBoundary(window)
   
   // Обрабатываем окно
   windowChunks = ProcessWindow(window[:boundary])
   allChunks.append(windowChunks)
   
   // Возвращаем непрочитанную часть в буфер
   IF boundary < len(window) THEN
      reader.Seek(windowStart + boundary)
   
   windowStart += boundary
   
   // Освобождаем память
   FreeMemory(window)

5. RETURN allChunks
```

**FindSafeBoundary:**
```
1. // Ищем безопасную границу для разрыва окна
   boundaries = []
   
   // Конец строки
   lastNewline = LastIndexOf(window, "\n")
   IF lastNewline != -1 THEN
      boundaries.append(lastNewline + 1)
   
   // Граница параграфа
   lastParagraph = LastIndexOf(window, "\n\n")
   IF lastParagraph != -1 THEN
      boundaries.append(lastParagraph + 2)
   
   // Конец блока кода
   lastCodeBlock = LastIndexOf(window, "```\n")
   IF lastCodeBlock != -1 THEN
      boundaries.append(lastCodeBlock + 4)

2. IF len(boundaries) > 0 THEN
   // Выбираем самую позднюю границу
   RETURN max(boundaries)
ELSE
   // Нет безопасной границы - разрываем по размеру
   RETURN len(window)
```

**Пример:**

**Большой файл (15MB):**
```
1. Разбить на окна по 1MB
2. Обработать каждое окно:
   Window 1 (0-1MB): 50 чанков
   Window 2 (1-2MB): 48 чанков
   ...
   Window 15 (14-15MB): 52 чанков
3. Объединить результаты: 750 чанков
4. Максимальное использование памяти: ~5MB (вместо 15MB)
```

### 6.5 Оптимизации

#### 6.5.1 Кеширование регулярных выражений

```go
var (
    headerRegex    *regexp.Regexp
    codeBlockRegex *regexp.Regexp
    listRegex      *regexp.Regexp
    tableRegex     *regexp.Regexp
)

func init() {
    // Компилируем все regex один раз при инициализации
    headerRegex = regexp.MustCompile(`^(#{1,6})\s+(.*)$`)
    codeBlockRegex = regexp.MustCompile(`^```(\w*)$`)
    listRegex = regexp.MustCompile(`^(\s*)([-*+]|\d+\.)\s+(.*)$`)
    tableRegex = regexp.MustCompile(`^.*\|.*$`)
}
```

**Ускорение:** 60-80% для операций с регулярными выражениями

#### 6.5.2 Memory Pooling

```go
var bufferPool = sync.Pool{
    New: func() interface{} {
        return make([]byte, 64*1024) // 64KB буфер
    },
}

func ProcessContent(content string) {
    buffer := bufferPool.Get().([]byte)
    defer bufferPool.Put(buffer)
    
    // Используем buffer для обработки
    ...
}
```

**Эффект:**
- Снижение GC pressure на 50-70%
- Уменьшение аллокаций на 50-70%
- Ускорение на 20-30%

#### 6.5.3 Параллельная обработка

```go
type ConcurrentProcessor struct {
    workerCount int
    jobQueue    chan Job
    resultQueue chan Result
}

func (cp *ConcurrentProcessor) ProcessFiles(files []File) []Result {
    // Запускаем воркеры
    for i := 0; i < cp.workerCount; i++ {
        go cp.worker()
    }
    
    // Отправляем задачи
    for _, file := range files {
        cp.jobQueue <- Job{File: file}
    }
    
    // Собираем результаты
    results := make([]Result, 0, len(files))
    for i := 0; i < len(files); i++ {
        results = append(results, <-cp.resultQueue)
    }
    
    return results
}
```

**Конфигурация:**
```go
type ConcurrentConfig struct {
    WorkerCount    int  // 4 - количество воркеров
    QueueSize      int  // 100 - размер очереди
    Enabled        bool // true - включить параллельную обработку
    MaxConcurrency int  // 8 - максимальная параллельность
}
```

**Ускорение:** 3-4x на многоядерных системах (при обработке множества файлов)


## 7. Структуры данных - Дополнительные примеры

### 7.1 Полный пример Chunk с метаданными

```go
Chunk{
    FileID: 12345,
    Content: "```python\ndef process_data(input):\n    return input.upper()\n```",
    StartLine: 10,
    EndLine: 13,
    Metadata: map[string]string{
        // Базовые метаданные
        "extractor": "markdown",
        "type": "code",
        "path": "docs/api.md",
        "source_id": "source_123",
        "start_line": "10",
        "end_line": "13",
        "chunk_index": "5",
        "id": "hash_abc123",
        
        // Метаданные стратегии
        "strategy": "code",
        "adaptive": "true",
        "code_ratio": "0.750",
        "code_blocks_count": "5",
        "detected_languages": "python",
        "preserve_functions": "true",
        "allow_oversize": "true",
        
        // Метаданные кода
        "content_type": "code",
        "language": "python",
        "function_name": "process_data",
        "complexity": "2",
        "is_fenced": "true",
    },
}
```

### 7.2 Полный пример DocumentAnalysis

```go
DocumentAnalysis{
    // Основные характеристики
    ContentType: "mixed",
    DocumentSize: 15000,
    
    // Метрики
    Metrics: ContentMetrics{
        TotalCharacters: 15000,
        TotalLines: 450,
        TotalWords: 2500,
        AverageLineLength: 33.3,
        MaxLineLength: 120,
        EmptyLines: 50,
        IndentedLines: 80,
        PunctuationRatio: 0.08,
        LanguageCount: map[string]int{
            "python": 3,
            "go": 2,
        },
        SpecialChars: map[string]int{
            "#": 15,
            "`": 120,
            "*": 45,
            "-": 30,
            "|": 24,
        },
    },
    
    // Структурные элементы
    HeaderCount: map[int]int{
        1: 1,
        2: 5,
        3: 10,
    },
    ListCount: 8,
    TableCount: 2,
    BlockElements: []BlockElement{...},
    
    // Соотношения контента
    CodeRatio: 0.35,
    TextRatio: 0.45,
    ListRatio: 0.15,
    TableRatio: 0.05,
    Languages: []string{"python", "go"},
    
    // Сложность
    MaxHeaderLevel: 3,
    NestedListDepth: 2,
    CodeBlockCount: 5,
    InlineCodeCount: 20,
    
    // Флаги
    HasTables: true,
    HasNestedLists: true,
    HasMixedContent: true,
    ComplexityScore: 0.65,
}
```

### 7.3 Конфигурации - Полные примеры

**Config (главная конфигурация):**
```go
Config{
    MaxChunkSize: 8192,
    MinChunkSize: 100,
    AdaptiveChunking: true,
    OptimizedProcessing: true,
    ConcurrentProcessing: true,
    QualityThreshold: 0.8,
    PerformanceMode: "balanced",
    DebugMode: false,
    
    StrategyConfig: &StrategyConfig{...},
    PreambleConfig: &PreambleConfig{...},
    OverlapConfig: &OverlapConfig{...},
    ConcurrentConfig: &ConcurrentConfig{...},
}
```

**StrategyConfig:**
```go
StrategyConfig{
    PriorityMode: "weighted",
    CodeRatioThreshold: 0.7,
    ListCountThreshold: 5,
    TableCountThreshold: 2,
    HeaderCountThreshold: 3,
    MixedContentBalance: 0.3,
    MaxChunkSize: 4096,
    MinChunkSize: 100,
    ContextOverlap: 200,
    
    CodeStrategy: &CodeStrategyConfig{
        MaxChunkSize: 1000,
        MinChunkSize: 100,
        MaxFunctionSize: 2000,
        PreserveComments: true,
        OversizeThreshold: 4000,
        SupportedLanguages: []string{"go", "python", "javascript"},
    },
    
    ListStrategy: &ListStrategyConfig{
        MaxChunkSize: 300,
        MinChunkSize: 50,
        PreserveNesting: true,
        MaxItemsPerChunk: 10,
        MinItemsThreshold: 5,
        MaxItemSize: 1000,
    },
    
    TableStrategy: &TableStrategyConfig{
        MaxTableSize: 8192,
        PreserveHeaders: true,
        SplitLargeTables: true,
        MaxRowsPerChunk: 10,
    },
    
    MixedStrategy: &MixedStrategyConfig{
        MaxChunkSize: 400,
        AdaptiveThreshold: 0.3,
        PreserveCodeBlocks: true,
        CodeTextBalance: 0.3,
        ContextOverlap: 200,
    },
    
    StructuralStrategy: &StructuralStrategyConfig{
        MaxSectionSize: 4000,
        MinSectionSize: 200,
        RespectHeaderLevels: true,
        MaxHeaderLevel: 3,
        CombineShortSections: true,
    },
    
    SentencesStrategy: &SentencesStrategyConfig{
        TargetChunkSize: 1500,
        PreserveParagraphs: true,
        SentenceOverlap: 1,
        MaxSentencesPerChunk: 3,
    },
}
```


## 8. Алгоритмы и формулы - Сводка

### 8.1 Ключевые регулярные выражения

```regex
# Заголовки
^(#{1,6})\s+(.*)$

# Fenced блоки кода
^```(\w*)$

# Списки
Unordered: ^(\s*)([-*+])\s+(.*)$
Ordered:   ^(\s*)(\d+)\.\s+(.*)$
Task:      ^(\s*)([-*+])\s+\[([ xX])\]\s+(.*)$

# Таблицы
Строка:     ^.*\|.*$
Разделитель: ^[\|\-\:\s]+$

# Предложения
[.!?][\s\n]

# Инлайн код
`[^`]+`
```

### 8.2 Ключевые формулы

**ComplexityScore:**
```
ComplexityScore = StructuralComplexity + ContentComplexity + SizeComplexity

StructuralComplexity = (MaxHeaderLevel/6)*0.1 + (NestedListDepth/5)*0.1 + (HasTables ? 0.1 : 0)
ContentComplexity = CodeComplexity + MixedComplexity
SizeComplexity = DocumentSize > 50000 ? 0.3 : DocumentSize > 20000 ? 0.2 : DocumentSize > 10000 ? 0.1 : 0

Диапазон: [0.0, 1.0]
```

**ContentRatios:**
```
CodeRatio = CodeChars / TotalChars
ListRatio = ListChars / TotalChars
TableRatio = TableChars / TotalChars
TextRatio = 1.0 - CodeRatio - ListRatio - TableRatio

Диапазон: [0.0, 1.0] для каждого
Сумма: ≈ 1.0
```

**WeightedScore (для выбора стратегии):**
```
WeightedScore = (1.0 / Priority) * 0.5 + QualityScore * 0.5

где:
  Priority: 1-6 (меньше = выше приоритет)
  QualityScore: 0.0-1.0

Диапазон: [0.0, 1.0]
```

**OverlapSize:**
```
OverlapSize = min(AbsoluteOverlap, ChunkSize * MaxOverlapRatio)
OverlapSize = max(OverlapSize, MinOverlapSize)
OverlapSize = min(OverlapSize, ChunkSize)

где:
  AbsoluteOverlap: 200 символов
  MaxOverlapRatio: 0.3 (30%)
  MinOverlapSize: 50 символов
```

**CodeComplexity:**
```
Complexity = (LineCount / 10) + KeywordCount

где:
  KeywordCount = Count("if") + Count("for") + Count("while") + 
                 Count("switch") + Count("case") + Count("try") + 
                 Count("catch") + Count("function") + Count("def") + 
                 Count("class")
```

**ListLevel (уровень вложенности):**
```
Level = LeadingSpaces / 2

Примеры:
  "- Item"      → Level = 0
  "  - Item"    → Level = 1
  "    - Item"  → Level = 2
```

### 8.3 Блок-схемы ключевых процессов

**Главный процесс извлечения:**
```
START
  ↓
[Проверить размер файла]
  ↓
[Размер > 10MB?] ─Yes→ [StreamingProcessor] → END
  ↓ No
[Валидация входа]
  ↓
[Нормализация контента]
  ↓
[ContentAnalyzer.AnalyzeContent]
  ↓
[StrategySelector.SelectStrategy]
  ↓
[Strategy.Apply]
  ↓
[PreambleHandler.ProcessPreamble]
  ↓
[OverlapProcessor.ProcessChunks]
  ↓
[Обогащение метаданными]
  ↓
[Валидация результата]
  ↓
END (chunks)
```

**Процесс выбора стратегии:**
```
START
  ↓
[Для каждой стратегии]
  ↓
[CanHandle?] ─No→ [Следующая стратегия]
  ↓ Yes
[Вычислить QualityScore]
  ↓
[Добавить в кандидаты]
  ↓
[Есть кандидаты?] ─No→ ERROR
  ↓ Yes
[Режим = strict?] ─Yes→ [Сортировать по Priority] → [Выбрать первую]
  ↓ No
[Вычислить WeightedScore]
  ↓
[Сортировать по WeightedScore]
  ↓
[Выбрать первую]
  ↓
END (strategy)
```


## 9. Примеры и тестовые случаи

### 9.1 Edge Cases (Граничные случаи)

#### 9.1.1 Пустой документ

**Входной документ:**
```markdown
```

**Результат:**
```
Error: "empty content"
```

#### 9.1.2 Документ без заголовков

**Входной документ:**
```markdown
This is just plain text without any structure.
It has multiple paragraphs.

But no headers at all.
```

**Результат:**
```
Strategy: SentencesStrategy (fallback)
Chunks: 1
Chunk 1:
  Content: весь текст
  Metadata:
    strategy: "sentences"
    fallback_strategy: "true"
```

#### 9.1.3 Очень большой блок кода (>4000 символов)

**Входной документ:**
```markdown
# Code Example

```python
# Очень длинный код (5000 строк)
...
```
```

**Результат:**
```
Strategy: CodeStrategy
Chunks: 1
Chunk 1:
  Content: весь блок кода
  Metadata:
    strategy: "code"
    language: "python"
    oversize: "true"
    oversize_single_code_block: "true"
```

#### 9.1.4 Глубоко вложенные списки (5 уровней)

**Входной документ:**
```markdown
- Level 0
  - Level 1
    - Level 2
      - Level 3
        - Level 4
          - Level 5
```

**Результат:**
```
Strategy: ListStrategy
Chunks: 1
Chunk 1:
  Content: весь список с вложенностью
  Metadata:
    strategy: "list"
    nesting_depth: 5
    preserve_nesting: "true"
```

#### 9.1.5 Таблица с большим количеством строк (100 строк)

**Входной документ:**
```markdown
| ID | Name | Value |
|----|------|-------|
| 1  | A    | 100   |
| 2  | B    | 200   |
...
| 100| Z    | 10000 |
```

**Результат:**
```
Strategy: TableStrategy
Chunks: 10 (по 10 строк каждый)
Chunk 1:
  Content: заголовок + разделитель + строки 1-10
  Metadata:
    strategy: "table"
    row_count: 10
    has_headers: "true"
    split_part: 1
    total_parts: 10
```

#### 9.1.6 Unicode и специальные символы

**Входной документ:**
```markdown
# Документация на русском

Это текст с эмодзи 🚀 и специальными символами: ©, ®, ™.

Также есть китайские символы: 你好世界
```

**Результат:**
```
Strategy: StructuralStrategy
Chunks: 1
Chunk 1:
  Content: весь текст (корректно обработан Unicode)
  Metadata:
    strategy: "structural"
    header_text: "Документация на русском"
```

#### 9.1.7 Смешанный контент с некорректным Markdown

**Входной документ:**
```markdown
# Header

Some text

```python
def func():
    print("Hello")
# Забыли закрыть блок кода

More text
```

**Результат:**
```
Strategy: MixedStrategy (с восстановлением)
Chunks: 2
Chunk 1:
  Content: "# Header\n\nSome text"
  Metadata:
    strategy: "mixed"
    recovery: "clean_and_retry"

Chunk 2:
  Content: "```python\ndef func():\n    print(\"Hello\")\n```\n\nMore text"
  Metadata:
    strategy: "mixed"
    recovery: "clean_and_retry"
    code_block_auto_closed: "true"
```

#### 9.1.8 Документ только с кодом (без текста)

**Входной документ:**
```markdown
```python
def func1():
    pass
```

```go
func main() {}
```

```javascript
function test() {}
```
```

**Результат:**
```
Strategy: CodeStrategy
Chunks: 3
Chunk 1:
  Content: Python код
  Metadata:
    strategy: "code"
    language: "python"
    function_name: "func1"

Chunk 2:
  Content: Go код
  Metadata:
    strategy: "code"
    language: "go"
    function_name: "main"

Chunk 3:
  Content: JavaScript код
  Metadata:
    strategy: "code"
    language: "javascript"
    function_name: "test"
```


## 10. Справочная информация

### 10.1 Константы и пороговые значения

**Размеры чанков:**
```
MaxChunkSize (общий): 8192 символов
MinChunkSize (общий): 100 символов

CodeStrategy:
  MaxChunkSize: 1000 символов
  MaxFunctionSize: 2000 символов
  OversizeThreshold: 4000 символов

ListStrategy:
  MaxChunkSize: 300 символов
  MinChunkSize: 50 символов
  MaxItemsPerChunk: 10 элементов

TableStrategy:
  MaxTableSize: 8192 символов
  MaxRowsPerChunk: 10 строк

MixedStrategy:
  MaxChunkSize: 400 символов
  ContextOverlap: 200 символов

StructuralStrategy:
  MaxSectionSize: 4000 символов
  MinSectionSize: 200 символов

SentencesStrategy:
  TargetChunkSize: 1500 символов
  MaxSentencesPerChunk: 3 предложения
```

**Пороги для анализа:**
```
CodeRatioThreshold: 0.7 (70% кода)
ListRatioThreshold: 0.6 (60% списков)
MixedContentMin: 0.2 (20% минимум для mixed)
MixedContentMax: 0.7 (70% максимум для mixed)

ListCountThreshold: 5 списков
TableCountThreshold: 2 таблицы
HeaderCountThreshold: 3 заголовка

MinCodeBlockSize: 10 символов
MinListItems: 3 элемента
MinTableColumns: 2 колонки
```

**Перекрытие:**
```
AbsoluteOverlap: 200 символов
MaxOverlapRatio: 0.3 (30% от размера чанка)
MinOverlapSize: 50 символов
SentenceOverlap: 1 предложение
```

**Потоковая обработка:**
```
StreamingThreshold: 10MB
ChunkSize (окно): 1MB
BufferSize: 64KB
MaxMemoryUsage: 100MB
```

**Параллельная обработка:**
```
WorkerCount: 4 воркера
QueueSize: 100 задач
MaxConcurrency: 8
```

### 10.2 Значения по умолчанию

**Config:**
```go
{
    MaxChunkSize: 8192,
    MinChunkSize: 100,
    AdaptiveChunking: true,
    OptimizedProcessing: true,
    ConcurrentProcessing: true,
    QualityThreshold: 0.8,
    PerformanceMode: "balanced",
    DebugMode: false,
}
```

**StrategyConfig:**
```go
{
    PriorityMode: "weighted",
    CodeRatioThreshold: 0.7,
    ListCountThreshold: 5,
    TableCountThreshold: 2,
    HeaderCountThreshold: 3,
    MixedContentBalance: 0.3,
    MaxChunkSize: 4096,
    MinChunkSize: 100,
    ContextOverlap: 200,
}
```

**PreambleConfig:**
```go
{
    Enabled: true,
    MaxSize: 4096,
    SplitStrategy: "sentences",
    PreserveFormatting: true,
    MinSize: 100,
}
```

**OverlapConfig:**
```go
{
    Enabled: true,
    AbsoluteOverlap: 200,
    RespectBoundaries: true,
    PreferParagraphBoundary: true,
    PreferSentenceBoundary: true,
    MaxOverlapRatio: 0.3,
    MinOverlapSize: 50,
}
```

### 10.3 Рекомендации по настройке

**Для документации с большим количеством кода:**
```go
config.StrategyConfig.CodeRatioThreshold = 0.6  // Снизить порог
config.StrategyConfig.CodeStrategy.MaxChunkSize = 1500  // Увеличить размер
config.StrategyConfig.CodeStrategy.PreserveComments = true
```

**Для документации со списками:**
```go
config.StrategyConfig.ListCountThreshold = 3  // Снизить порог
config.StrategyConfig.ListStrategy.MaxItemsPerChunk = 15  // Больше элементов
config.StrategyConfig.ListStrategy.PreserveNesting = true
```

**Для больших документов:**
```go
config.MaxChunkSize = 12000  // Увеличить размер чанков
config.StrategyConfig.StructuralStrategy.MaxSectionSize = 6000
config.OverlapConfig.AbsoluteOverlap = 300  // Больше перекрытие
```

**Для RAG систем:**
```go
config.OverlapConfig.Enabled = true
config.OverlapConfig.AbsoluteOverlap = 250
config.OverlapConfig.RespectBoundaries = true
config.AdaptiveChunking = true
```

**Для производительности:**
```go
config.OptimizedProcessing = true
config.ConcurrentProcessing = true
config.ConcurrentConfig.WorkerCount = 8  // Больше воркеров
config.PerformanceMode = "fast"
```

**Для качества:**
```go
config.QualityThreshold = 0.9  // Выше порог качества
config.StrategyConfig.PriorityMode = "weighted"  // Учитывать качество
config.PerformanceMode = "quality"
```

### 10.4 FAQ (Часто задаваемые вопросы)

**Q: Почему мой документ разбивается не той стратегией?**
A: Проверьте соотношения контента (CodeRatio, ListRatio и т.д.) и пороговые значения. Возможно, нужно настроить пороги в StrategyConfig.

**Q: Как увеличить размер чанков?**
A: Установите `config.MaxChunkSize` и соответствующие значения для каждой стратегии (например, `config.StrategyConfig.CodeStrategy.MaxChunkSize`).

**Q: Почему блоки кода разбиваются?**
A: Блоки кода сохраняются атомарно, но если блок больше `OversizeThreshold` (4000), он помечается как oversize. Увеличьте `OversizeThreshold` если нужно.

**Q: Как отключить перекрытие между чанками?**
A: Установите `config.OverlapConfig.Enabled = false`.

**Q: Как обрабатываются большие файлы?**
A: Файлы >10MB обрабатываются потоково через StreamingProcessor. Настройте `config.StreamingThreshold` для изменения порога.

**Q: Можно ли использовать только одну стратегию?**
A: Да, зарегистрируйте только нужную стратегию в StrategySelector или установите очень высокие пороги для остальных.

**Q: Как работает weighted mode?**
A: Weighted mode комбинирует приоритет стратегии и её качество: `WeightedScore = (1.0/Priority)*0.5 + QualityScore*0.5`. Это позволяет выбрать стратегию с лучшим качеством, даже если у неё ниже приоритет.

**Q: Что делать если документ не разбивается корректно?**
A: 1) Проверьте анализ документа (DocumentAnalysis), 2) Проверьте какая стратегия выбрана, 3) Настройте пороги для нужной стратегии, 4) Включите DebugMode для детальной информации.

**Q: Как обрабатываются ошибки?**
A: Система использует FallbackChain с несколькими стратегиями восстановления: CleanAndRetry, FallbackStrategy, PartialResults, EmergencyFallback.

**Q: Можно ли добавить свою стратегию?**
A: Да, реализуйте интерфейс ChunkingStrategy и зарегистрируйте её в StrategySelector.


---

## Заключение

Данная документация предоставляет полное описание алгоритма чанкования Markdown документов, реализованного в сервисе meaning-extractor. Документация является самодостаточной и содержит всю необходимую информацию для реализации алгоритма с нуля на любом языке программирования.

### Ключевые моменты

**1. Адаптивный подход:**
Система автоматически выбирает оптимальную стратегию разбиения на основе анализа документа, что обеспечивает высокое качество результата для различных типов контента.

**2. Сохранение семантики:**
Все стратегии разбиения учитывают семантические границы (заголовки, параграфы, предложения, блоки кода), что критически важно для RAG систем.

**3. Производительность:**
Система оптимизирована для обработки больших объемов данных с использованием потоковой обработки, кеширования и параллелизма.

**4. Надежность:**
Многоуровневая система обработки ошибок с fallback механизмами обеспечивает стабильную работу даже с некорректными данными.

**5. Гибкость:**
Богатая система конфигурации позволяет настроить алгоритм под конкретные требования проекта.

### Покрытие требований

Документация полностью покрывает все 10 требований из спецификации:

✅ **Требование 1:** Архитектурный обзор - Раздел 2
✅ **Требование 2:** Анализ контента - Раздел 3
✅ **Требование 3:** Стратегии разбиения - Раздел 4
✅ **Требование 4:** Выбор стратегии - Раздел 5
✅ **Требование 5:** Обработка специальных случаев - Раздел 6
✅ **Требование 6:** Структуры данных - Раздел 7
✅ **Требование 7:** Алгоритмы и формулы - Раздел 8
✅ **Требование 8:** Примеры и тестовые случаи - Раздел 9
✅ **Требование 9:** Принципы и философия - Раздел 1
✅ **Требование 10:** Полнота и самодостаточность - Вся документация

### Структура документации

Документация организована в 10 основных разделов:

1. **Введение и обзор системы** - Назначение, проблема, решение, принципы
2. **Архитектура и компоненты** - Структура системы, компоненты, взаимодействие
3. **Анализ контента** - ContentAnalyzer, метрики, алгоритмы обнаружения
4. **Стратегии разбиения** - 6 стратегий с детальным описанием
5. **Выбор стратегии** - StrategySelector, режимы, оценка
6. **Обработка специальных случаев** - Preamble, Overlap, Errors, Streaming, Оптимизации
7. **Структуры данных** - Все структуры с примерами
8. **Алгоритмы и формулы** - Регулярные выражения, формулы, блок-схемы
9. **Примеры и тестовые случаи** - Примеры для каждой стратегии, edge cases
10. **Справочная информация** - Константы, значения по умолчанию, рекомендации, FAQ

### Использование документации

**Для разработчиков:**
- Используйте разделы 2-8 для понимания архитектуры и алгоритмов
- Раздел 9 содержит примеры для тестирования реализации
- Раздел 10 - справочник для быстрого поиска значений

**Для архитекторов:**
- Раздел 1 описывает принципы и философию
- Раздел 2 показывает общую архитектуру
- Раздел 5 объясняет логику принятия решений

**Для тестировщиков:**
- Раздел 9 содержит тестовые случаи и edge cases
- Каждая стратегия имеет примеры входа/выхода
- Раздел 10 содержит FAQ с типичными проблемами

### Дальнейшее развитие

Документация может быть расширена следующими разделами:
- Производительность и бенчмарки
- Интеграция с другими системами
- Миграция между версиями
- Расширенные примеры использования
- Troubleshooting guide

---

**Версия документации:** 1.0
**Дата создания:** 2025-01-25
**Язык:** Русский
**Статус:** Завершено

