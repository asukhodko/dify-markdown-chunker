# Feature 02: Nested Fencing Support

## Краткое описание

Поддержка вложенных code blocks с использованием четверных/пятерных backticks (````, `````) и tilde fencing (~~~~). Уникальный дифференциатор — ни один конкурент не обрабатывает это корректно.

---

## Метаданные

| Параметр | Значение |
|----------|----------|
| **Фаза** | 1 — Восстановление ядра |
| **Приоритет** | CRITICAL |
| **Effort** | 3-5 дней |
| **Impact** | High |
| **Уникальность** | **YES** — уникальный дифференциатор |

---

## Проблема

### Текущее состояние

Ни один существующий markdown chunker (LangChain, LlamaIndex, Unstructured, Chonkie) не обрабатывает вложенные code blocks корректно. Это критично для:

- Documentation templates
- Meta-documentation (документация о том, как писать документацию)
- Tutorial-style content с примерами кода внутри markdown
- README файлы с примерами использования

### Пример проблемного контента

~~~~markdown
# How to Write Documentation

When documenting code, use fenced code blocks:

```markdown
Here's how to show a Python example:

```python
def hello():
    print("Hello, World!")
```

And here's JavaScript:

```javascript
function hello() {
    console.log("Hello, World!");
}
```
```

## Escaping

For showing markdown itself, use more backticks:

`````markdown
````markdown
```python
code here
```
````
`````
~~~~

### Как это ломается сейчас

1. Парсер находит первые ``` и начинает code block
2. Встречает вложенные ``` и закрывает block преждевременно
3. Остальной контент интерпретируется как обычный текст
4. Структура документа полностью нарушается

### Тестовый корпус

В `tests/corpus/nested_fencing/` — 20+ файлов специально для тестирования:
- Triple → Quadruple backticks
- Quadruple → Quintuple backticks
- Mixed nesting levels
- Tilde fencing (~~~~~)

---

## Решение

### Алгоритм парсинга

```python
def extract_nested_code_blocks(text: str) -> list[FencedBlock]:
    """
    Извлечение code blocks с корректной поддержкой вложенности.
    
    Обрабатывает:
    - Triple backticks (```)
    - Quadruple backticks (````)
    - Quintuple backticks (`````)
    - Tilde fencing (~~~, ~~~~, ~~~~~)
    """
    blocks = []
    lines = text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Проверка на начало fence (3+ backticks или tildes)
        fence_match = re.match(r'^(`{3,}|~{3,})(\w*)', line)
        if fence_match:
            fence = fence_match.group(1)
            fence_char = fence[0]
            fence_len = len(fence)
            language = fence_match.group(2)
            
            # Поиск закрывающего fence (тот же символ, та же или большая длина)
            content_lines = []
            start_line = i
            i += 1
            
            while i < len(lines):
                # Закрывающий fence должен:
                # 1. Начинаться с того же символа
                # 2. Иметь ту же или большую длину
                # 3. Не иметь текста после (кроме пробелов)
                close_pattern = rf'^{fence_char}{{{fence_len},}}\s*$'
                if re.match(close_pattern, lines[i]):
                    break
                content_lines.append(lines[i])
                i += 1
            
            blocks.append(FencedBlock(
                content='\n'.join(content_lines),
                language=language,
                fence_type=fence_char,
                fence_length=fence_len,
                start_line=start_line,
                end_line=i
            ))
        
        i += 1
    
    return blocks
```

### Структура данных

```python
@dataclass
class FencedBlock:
    content: str           # Содержимое без fence
    language: str          # Язык (python, markdown, etc.)
    fence_type: str        # '`' или '~'
    fence_length: int      # 3, 4, 5, ...
    start_line: int        # Начальная строка
    end_line: int          # Конечная строка
    
    @property
    def is_nested(self) -> bool:
        """Проверка, содержит ли block вложенные code blocks"""
        inner_fence = '`{3,}|~{3,}'
        return bool(re.search(inner_fence, self.content))
```

### Интеграция с существующим парсером

```python
class MarkdownParser:
    def parse(self, text: str) -> ParsedDocument:
        # 1. Сначала извлечь все fenced blocks с учётом вложенности
        fenced_blocks = self._extract_nested_fenced_blocks(text)
        
        # 2. Заменить blocks на placeholders для безопасного парсинга
        safe_text, block_map = self._replace_with_placeholders(
            text, fenced_blocks
        )
        
        # 3. Парсить остальной контент
        parsed = self._parse_content(safe_text)
        
        # 4. Восстановить blocks
        parsed = self._restore_blocks(parsed, block_map)
        
        return parsed
```

---

## Тестовые сценарии

### Базовые сценарии

~~~python
def test_quadruple_backticks():
    """Четверные backticks корректно обрабатываются"""
    text = '''
````markdown
```python
code
```
````
'''
    blocks = extract_nested_code_blocks(text)
    assert len(blocks) == 1
    assert '```python' in blocks[0].content

def test_mixed_fence_types():
    """Смешанные типы (backticks + tildes) обрабатываются"""
    
def test_quintuple_backticks():
    """Пятерные backticks для глубокой вложенности"""
    
def test_unmatched_fences():
    """Незакрытые fence не ломают парсинг"""
~~~

### Edge Cases

```python
def test_fence_in_inline_code():
    """Backticks в inline code (`...`) не интерпретируются как fence"""
    
def test_fence_in_comment():
    """Fence внутри HTML комментариев игнорируются"""
    
def test_indented_fence():
    """Indented fence blocks (4+ пробелов) обрабатываются"""
```

---

## Ожидаемые улучшения

### Конкурентное преимущество

| Решение | Nested Fencing Support |
|---------|------------------------|
| LangChain | ❌ |
| LlamaIndex | ❌ |
| Unstructured | ❌ |
| Chonkie | ❌ |
| Haystack | ❌ |
| **markdown_chunker_v2** | **✅** |

### Типы документов

- **Documentation templates:** 100% корректная обработка
- **Meta-documentation:** README о том, как писать README
- **Tutorials:** Примеры кода внутри markdown блоков
- **Style guides:** Примеры форматирования

---

## Зависимости

### Требует изменений в

- `markdown_chunker_v2/parser.py` — основной парсер
- `markdown_chunker_v2/types.py` — расширение FencedBlock

### Не влияет на

- Стратегии chunking (они получают уже parsed content)
- API контракты

---

## Риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Edge cases в реальных docs | Medium | Medium | Comprehensive test corpus |
| Performance impact | Low | Low | Regex optimization |
| Breaking existing behavior | Low | High | Backward compatibility tests |

---

## Acceptance Criteria

- [ ] Четверные backticks (````) корректно парсятся
- [ ] Пятерные backticks (`````) корректно парсятся
- [ ] Tilde fencing (~~~~) корректно парсится
- [ ] Смешанные типы fence работают вместе
- [ ] Вложенность любой глубины поддерживается
- [ ] Незакрытые fence не ломают документ
- [ ] Все файлы в tests/corpus/nested_fencing/ обрабатываются корректно
- [ ] Производительность не деградирует более чем на 5%
- [ ] Обратная совместимость с существующими документами

---

## Примеры из тестового корпуса

Следующие файлы специально созданы для тестирования nested fencing:

### Nested Fencing Examples

| Файл | Строк | Описание |
|------|-------|----------|
| [nested_fencing_011.md](../../../tests/corpus/nested_fencing/nested_fencing_011.md) | 50 | Базовый пример вложенных code blocks |
| [nested_fencing_013.md](../../../tests/corpus/nested_fencing/nested_fencing_013.md) | 65 | Более сложные вложенные fences |

### Дополнительные примеры с code blocks

Файлы с высоким code_ratio, которые могут содержать примеры nested fencing:

| Файл | Code Ratio | Описание |
|------|------------|----------|
| [engineering_blogs_026.md](../../../tests/corpus/engineering_blogs/engineering_blogs_026.md) | 44% | Технический блог с code examples |
| [debug_logs_002.md](../../../tests/corpus/debug_logs/debug_logs_002.md) | 36% | Debug log с кодом |
| [hugo.md](../../../tests/corpus/github_readmes/go/hugo.md) | 39% | Hugo README с примерами |
