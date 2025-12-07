# Feature 01: Smart List Strategy

## Краткое описание

Восстановление и улучшение стратегии для документов с высоким содержанием списков (changelogs, feature lists, outlines, checklists).

---

## Метаданные

| Параметр | Значение |
|----------|----------|
| **Фаза** | 1 — Восстановление ядра |
| **Приоритет** | CRITICAL |
| **Effort** | 5-7 дней |
| **Impact** | High |
| **Уникальность** | Partial |

---

## Проблема

### Текущее состояние

При переходе с v1.x (6 стратегий) на v2.0 (3 стратегии) List Strategy была полностью удалена. Теперь list-heavy документы обрабатываются CodeAware или Structural стратегиями, которые не оптимизированы для списков.

### Масштаб проблемы

- **Затронуто документов:** 20-25% от общего корпуса
- **Типы документов:**
  - Changelogs (50+ файлов в тестовом корпусе)
  - Feature lists
  - TODO/task lists
  - Outlines и структурные заметки
  - Checklists

### Потерянные возможности v1.x

1. **List detection** — специальная обработка для list-heavy документов
2. **Hierarchy preservation** — вложенные списки сохранялись вместе
3. **List grouping** — связанные пункты в одном чанке
4. **List-context binding** — список со своим вводным параграфом

### Пример деградации

**Входной документ:**
```markdown
# Features

Our product includes:

- **Authentication**
  - OAuth 2.0 support
  - SAML integration
  - MFA options
    - SMS
    - Authenticator app
    - Hardware keys

- **Authorization**
  - Role-based access
  - Permission groups
  - Custom policies
```

**V1.x (List Strategy):** 2 чанка
- Chunk 1: Header + "Authentication" с под-пунктами
- Chunk 2: "Authorization" с под-пунктами

**V2.0 (CodeAware/Structural):** 3-4 чанка
- Может разорвать вложенные пункты
- Может отделить заголовок от списка

---

## Решение

### Архитектура

```python
class ListAwareStrategy(BaseStrategy):
    """
    Стратегия для документов с высоким содержанием списков.
    
    Активация: list_ratio > 40% OR list_count >= 5
    """
    
    def should_apply(self, analysis: ContentAnalysis) -> bool:
        return (
            analysis.list_ratio > 0.40 or 
            analysis.list_count >= 5
        )
    
    def apply(
        self, 
        text: str, 
        analysis: ContentAnalysis, 
        config: ChunkConfig
    ) -> list[Chunk]:
        """
        Основная логика:
        1. Идентифицировать list blocks с контекстом
        2. Группировать вложенные списки
        3. Сохранять list introduction с самим списком
        4. Соблюдать max_chunk_size с сохранением иерархии
        """
        pass
```

### Ключевые компоненты

#### 1. List Block Detection
```python
@dataclass
class ListBlock:
    content: str
    start_line: int
    end_line: int
    depth: int          # Уровень вложенности (0 = top-level)
    item_count: int     # Количество пунктов
    list_type: str      # 'bullet', 'numbered', 'checkbox'
    parent_index: Optional[int]  # Индекс родительского списка
```

#### 2. Context Binding
```python
def bind_list_context(
    list_block: ListBlock, 
    preceding_text: str
) -> str:
    """
    Привязка списка к вводному параграфу.
    
    Пример:
    "The following features are available:" + список
    """
    # Найти последний параграф перед списком
    # Проверить, является ли он введением к списку
    # Включить в чанк если да
```

#### 3. Hierarchy Preservation
```python
def preserve_hierarchy(
    items: list[ListItem],
    max_size: int
) -> list[list[ListItem]]:
    """
    Группировка с сохранением вложенности.
    
    Никогда не разрывать:
    - Родительский пункт и его дочерние
    - Вложенный список на середине
    """
```

### Критерии активации

| Условие | Порог | Приоритет |
|---------|-------|-----------|
| List ratio | > 40% | Primary |
| List count | >= 5 | Secondary |
| Nested depth | > 2 | Boost |

---

## Ожидаемые улучшения

### Метрики качества

| Метрика | До | После | Улучшение |
|---------|-----|-------|-----------|
| SCS (list-heavy docs) | 1.2 | 1.5+ | +25% |
| CPS (list-heavy docs) | 70% | 85%+ | +15% |
| BQS (list-heavy docs) | 0.85 | 0.92+ | +8% |
| Overall quality | 78 | 82+ | +5% |

### Польза для пользователей

1. **Changelogs** — версии остаются целыми с изменениями
2. **Feature lists** — функции с описаниями в одном чанке
3. **Task lists** — задачи с под-задачами вместе
4. **Outlines** — структура документа сохраняется

---

## Тестирование

### Unit Tests

```python
def test_list_strategy_activation():
    """List Strategy активируется при list_ratio > 40%"""
    
def test_nested_list_preservation():
    """Вложенные списки не разрываются"""
    
def test_list_context_binding():
    """Вводный параграф включается в чанк со списком"""
    
def test_max_size_with_hierarchy():
    """При превышении max_size иерархия сохраняется"""
```

### Тестовые файлы из корпуса

- `tests/corpus/changelogs/` — 50+ changelog файлов
- `tests/corpus/github_readmes/` — README с feature lists
- `tests/corpus/personal_notes/cheatsheets/` — cheatsheets со списками

---

## Зависимости

### Требует реализации до

- **Feature 03: List Detection в Parser** — парсер должен извлекать list information

### Влияет на

- Strategy Selector — добавление нового критерия выбора
- ContentAnalysis — новые поля для list metrics

---

## Риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Слишком агрессивная группировка | Medium | Medium | Configurable thresholds |
| Конфликт с CodeAware | Low | Low | Чёткие критерии приоритета |
| Performance overhead | Low | Low | Lazy list parsing |

---

## Acceptance Criteria

- [ ] List Strategy активируется для документов с list_ratio > 40% ИЛИ list_count >= 5
- [ ] Вложенные списки никогда не разрываются между чанками
- [ ] Вводный параграф включается в чанк со списком
- [ ] max_chunk_size соблюдается с минимальным нарушением иерархии
- [ ] Все существующие тесты проходят
- [ ] Новые тесты для list functionality покрывают edge cases
- [ ] Метрики SCS для list-heavy docs улучшаются минимум на 20%

---

## Примеры из тестового корпуса

Следующие файлы демонстрируют list-heavy контент и подходят для тестирования Smart List Strategy:

### Changelogs (высокое содержание списков)

| Файл | Списков | Строк | Описание |
|------|---------|-------|----------|
| [changelogs_005.md](../../../tests/corpus/changelogs/changelogs_005.md) | 128 | 256 | Changelog с максимальным количеством списков |
| [changelogs_010.md](../../../tests/corpus/changelogs/changelogs_010.md) | 128 | 253 | Большой changelog |
| [changelogs_034.md](../../../tests/corpus/changelogs/changelogs_034.md) | 126 | 252 | Changelog с глубокой вложенностью |
| [changelogs_020.md](../../../tests/corpus/changelogs/changelogs_020.md) | 118 | 237 | Типичный changelog проекта |
| [changelogs_004.md](../../../tests/corpus/changelogs/changelogs_004.md) | 118 | 241 | Changelog с разными типами списков |
| [changelogs_018.md](../../../tests/corpus/changelogs/changelogs_018.md) | 102 | 199 | Средний changelog |
| [changelogs_026.md](../../../tests/corpus/changelogs/changelogs_026.md) | 96 | 208 | Changelog с вложенными списками |
| [changelogs_031.md](../../../tests/corpus/changelogs/changelogs_031.md) | 90 | 183 | Changelog с категориями |

### GitHub READMEs с большим количеством списков

| Файл | Списков | Описание |
|------|---------|----------|
| [node.md](../../../tests/corpus/github_readmes/javascript/node.md) | 660 | Node.js README с огромным количеством списков |
| [express.md](../../../tests/corpus/github_readmes/javascript/express.md) | 85 | Express.js с feature lists |
| [axios.md](../../../tests/corpus/github_readmes/javascript/axios.md) | 89 | Axios с API списками |
| [gin.md](../../../tests/corpus/github_readmes/go/gin.md) | 66 | Gin framework features |
| [changelogs_003.md](../../../tests/corpus/changelogs/changelogs_003.md) | 72 | Типичный changelog |

### Personal Notes с списками

| Файл | Списков | Описание |
|------|---------|----------|
| [cheatsheets_003.md](../../../tests/corpus/personal_notes/cheatsheets/cheatsheets_003.md) | 9 | Cheatsheet со списками команд |
