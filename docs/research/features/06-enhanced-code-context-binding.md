# Feature 06: Enhanced Code-Context Binding

## Краткое описание

Улучшенная привязка code blocks к окружающим объяснениям (explanation → code → output pattern). Уникальный дифференциатор.

---

## Метаданные

| Параметр | Значение |
|----------|----------|
| **Фаза** | 2 — Семантические возможности |
| **Приоритет** | MEDIUM |
| **Effort** | 2-3 дня |
| **Impact** | Medium |
| **Уникальность** | **YES** — уникальный дифференциатор |

---

## Проблема

### Текущее состояние

CodeAware Strategy уже привязывает код к контексту, но базово:
- Включает preceding paragraph
- Включает code block
- Может включать following paragraph

### Что можно улучшить

1. **Более умное определение контекста:**
   - Не весь preceding text, а только relevant объяснение
   - Распознавание "setup" кода vs "example" кода

2. **Связанные code blocks:**
   - Последовательные примеры (Step 1, Step 2, Step 3)
   - Before/After паттерны

3. **Output binding:**
   - Код + ожидаемый вывод вместе
   - Код + error message вместе

### User Needs

- C1.2: "Code loses surrounding explanation" — High frequency, Critical severity
- C2.3: "Examples separated from explanations" — High frequency, Critical severity

---

## Решение

### Архитектура

```python
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class CodeBlockRole(Enum):
    EXAMPLE = "example"        # Демонстрационный код
    SETUP = "setup"            # Подготовительный код
    OUTPUT = "output"          # Вывод/результат
    ERROR = "error"            # Ошибка/traceback
    BEFORE = "before"          # "Before" в before/after
    AFTER = "after"            # "After" в before/after
    UNKNOWN = "unknown"

@dataclass
class CodeContext:
    """Контекст для code block."""
    code_block: FencedBlock
    role: CodeBlockRole
    explanation_before: Optional[str]
    explanation_after: Optional[str]
    related_blocks: list[FencedBlock]
    output_block: Optional[FencedBlock]

class CodeContextBinder:
    """
    Улучшенная привязка кода к контексту.
    """
    
    # Patterns для определения роли
    SETUP_PATTERNS = [
        r'first,?\s+(you\s+)?need\s+to',
        r'install|import|require',
        r'setup|configuration|initialize',
    ]
    
    OUTPUT_PATTERNS = [
        r'^output:?\s*$',
        r'^result:?\s*$',
        r'^console:?\s*$',
        r'^stdout:?\s*$',
    ]
    
    BEFORE_AFTER_PATTERNS = [
        r'before[:\s]',
        r'after[:\s]',
        r'old\s+(?:code|version)',
        r'new\s+(?:code|version)',
    ]
    
    def bind_context(
        self,
        code_block: FencedBlock,
        surrounding_text: str,
        all_blocks: list[FencedBlock],
        config: ChunkConfig
    ) -> CodeContext:
        """
        Создать полный контекст для code block.
        """
        # 1. Определить роль блока
        role = self._determine_role(code_block, surrounding_text)
        
        # 2. Извлечь explanation before
        explanation_before = self._extract_explanation_before(
            code_block, surrounding_text, config.max_context_chars
        )
        
        # 3. Извлечь explanation after
        explanation_after = self._extract_explanation_after(
            code_block, surrounding_text, config.max_context_chars
        )
        
        # 4. Найти связанные blocks
        related_blocks = self._find_related_blocks(
            code_block, all_blocks
        )
        
        # 5. Найти output block
        output_block = self._find_output_block(
            code_block, all_blocks
        )
        
        return CodeContext(
            code_block=code_block,
            role=role,
            explanation_before=explanation_before,
            explanation_after=explanation_after,
            related_blocks=related_blocks,
            output_block=output_block
        )
    
    def _determine_role(
        self,
        block: FencedBlock,
        context: str
    ) -> CodeBlockRole:
        """Определить роль code block."""
        # Проверить language tag
        if block.language in ['output', 'console', 'stdout']:
            return CodeBlockRole.OUTPUT
        
        if block.language in ['error', 'traceback']:
            return CodeBlockRole.ERROR
        
        # Проверить preceding text
        preceding = self._get_preceding_text(block, context, chars=100)
        
        for pattern in self.OUTPUT_PATTERNS:
            if re.search(pattern, preceding, re.IGNORECASE):
                return CodeBlockRole.OUTPUT
        
        for pattern in self.SETUP_PATTERNS:
            if re.search(pattern, preceding, re.IGNORECASE):
                return CodeBlockRole.SETUP
        
        # Проверить before/after
        for pattern in self.BEFORE_AFTER_PATTERNS:
            match = re.search(pattern, preceding, re.IGNORECASE)
            if match:
                if 'before' in match.group().lower() or 'old' in match.group().lower():
                    return CodeBlockRole.BEFORE
                return CodeBlockRole.AFTER
        
        return CodeBlockRole.EXAMPLE
    
    def _find_related_blocks(
        self,
        block: FencedBlock,
        all_blocks: list[FencedBlock]
    ) -> list[FencedBlock]:
        """Найти связанные code blocks."""
        related = []
        block_idx = all_blocks.index(block)
        
        # Проверить соседние blocks
        for i in [block_idx - 1, block_idx + 1]:
            if 0 <= i < len(all_blocks):
                neighbor = all_blocks[i]
                if self._are_related(block, neighbor):
                    related.append(neighbor)
        
        return related
    
    def _are_related(
        self,
        block1: FencedBlock,
        block2: FencedBlock
    ) -> bool:
        """Определить, связаны ли два blocks."""
        # Одинаковый язык
        if block1.language == block2.language:
            return True
        
        # Близко по строкам (< 5 строк между)
        gap = abs(block1.end_line - block2.start_line)
        if gap < 5:
            return True
        
        return False
```

### Интеграция с CodeAware Strategy

```python
class CodeAwareStrategy(BaseStrategy):
    def __init__(self, config: ChunkConfig):
        self.config = config
        self.context_binder = CodeContextBinder()
    
    def apply(
        self,
        text: str,
        analysis: ContentAnalysis,
        config: ChunkConfig
    ) -> list[Chunk]:
        # 1. Получить все code blocks
        code_blocks = analysis.code_blocks
        
        # 2. Для каждого block создать enhanced context
        contexts = []
        for block in code_blocks:
            context = self.context_binder.bind_context(
                block, text, code_blocks, config
            )
            contexts.append(context)
        
        # 3. Создать chunks с полным контекстом
        return self._create_chunks_with_context(contexts, text)
```

---

## Примеры

### Before/After Pattern

```markdown
## Fixing the Bug

Before (problematic code):

```python
def process(data):
    result = data.split(',')  # Fails on None
    return result
```

After (fixed code):

```python
def process(data):
    if data is None:
        return []
    result = data.split(',')
    return result
```
```

**Результат:** Оба блока в одном чанке с объяснениями.

### Code + Output Pattern

```markdown
## Example Usage

```python
print("Hello, World!")
```

Output:

```
Hello, World!
```
```

**Результат:** Код и output вместе в одном чанке.

---

## Тестирование

### Unit Tests

```python
def test_determine_role_output():
    """Output blocks распознаются"""
    
def test_determine_role_setup():
    """Setup blocks распознаются"""
    
def test_before_after_binding():
    """Before/After связываются"""
    
def test_code_output_binding():
    """Code + Output связываются"""
    
def test_related_blocks_detection():
    """Связанные blocks находятся"""
```

---

## Ожидаемые улучшения

| Метрика | До | После | Улучшение |
|---------|-----|-------|-----------|
| Code-related retrieval quality | 70% | 85%+ | +15% |
| Context preservation | 75% | 90%+ | +15% |

---

## Зависимости

### Изменяет

- `CodeAwareStrategy` — основная логика
- Chunk metadata — добавление code_role

---

## Риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Over-binding (слишком большие chunks) | Medium | Medium | Configurable limits |
| Misclassification роли | Low | Low | Fallback to EXAMPLE |

---

## Acceptance Criteria

- [ ] Before/After patterns распознаются и связываются
- [ ] Code + Output связываются
- [ ] Setup code отмечается в metadata
- [ ] Связанные blocks группируются
- [ ] max_context_chars соблюдается
- [ ] Retrieval quality для code questions улучшается

---

## Примеры из тестового корпуса

Следующие файлы с высоким code_ratio подходят для тестирования Code-Context Binding:

### Файлы с высоким code_ratio (>30%)

| Файл | Code Ratio | Описание |
|------|------------|----------|
| [face_recognition.md](../../../tests/corpus/github_readmes/python/face_recognition.md) | 60% | Много примеров кода с объяснениями |
| [axios.md](../../../tests/corpus/github_readmes/javascript/axios.md) | 50% | API примеры с контекстом |
| [engineering_blogs_026.md](../../../tests/corpus/engineering_blogs/engineering_blogs_026.md) | 44% | Технический блог с code examples |
| [hugo.md](../../../tests/corpus/github_readmes/go/hugo.md) | 39% | Hugo примеры |
| [three.js.md](../../../tests/corpus/github_readmes/javascript/three.js.md) | 38% | Three.js examples |
| [debug_logs_002.md](../../../tests/corpus/debug_logs/debug_logs_002.md) | 36% | Debug log с кодом |
| [docker_005.md](../../../tests/corpus/technical_docs/docker/docker_005.md) | 34% | Docker документация |
| [youtube-dl.md](../../../tests/corpus/github_readmes/python/youtube-dl.md) | 33% | Много code examples |
| [go_007.md](../../../tests/corpus/github_readmes/go/go_007.md) | 31% | Go примеры |
| [journals_003.md](../../../tests/corpus/personal_notes/journals/journals_003.md) | 30% | Журнал с кодом |

### Файлы со смешанным code-text контентом (10-30%)

| Файл | Code Ratio | Описание |
|------|------------|----------|
| [click.md](../../../tests/corpus/github_readmes/python/click.md) | 27% | CLI примеры |
| [research_notes_007.md](../../../tests/corpus/research_notes/research_notes_007.md) | 23% | Заметки с кодом |
| [lodash.md](../../../tests/corpus/github_readmes/javascript/lodash.md) | 23% | Lodash examples |
| [requests.md](../../../tests/corpus/github_readmes/python/requests.md) | 19% | Requests примеры |
| [nuxt.md](../../../tests/corpus/github_readmes/javascript/nuxt.md) | 19% | Nuxt.js examples |
| [flask.md](../../../tests/corpus/github_readmes/python/flask.md) | 19% | Flask примеры |
