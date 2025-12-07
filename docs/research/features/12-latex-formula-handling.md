# Feature 12: LaTeX Formula Handling

## Краткое описание

Правильная обработка математических формул LaTeX — распознавание и сохранение как atomic blocks.

---

## Метаданные

| Параметр | Значение |
|----------|----------|
| **Фаза** | 4 — Продвинутые возможности |
| **Приоритет** | LOW |
| **Effort** | 1-2 дня |
| **Impact** | Medium |
| **Уникальность** | No |

---

## Проблема

### Текущее состояние

Математические формулы не распознаются как atomic blocks:
- Могут быть разорваны между чанками
- Inline формулы `$...$` могут ломать парсинг
- Display формулы `$$...$$` не группируются

### User Need

C7.1: "LaTeX formulas broken" — Medium frequency, High severity

### Типичный проблемный контент

```markdown
## Quadratic Formula

The solution to $ax^2 + bx + c = 0$ is given by:

$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$

This formula is known as the quadratic formula.
```

**Проблема:** Display формула может быть разорвана или отделена от объяснения.

---

## Решение

### Архитектура

```python
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class LatexType(Enum):
    INLINE = "inline"           # $...$
    DISPLAY = "display"         # $$...$$
    ENVIRONMENT = "environment" # \begin{equation}...\end{equation}

@dataclass
class LatexBlock:
    """Блок LaTeX формулы."""
    content: str          # Полное содержимое включая delimiters
    latex_type: LatexType
    start_pos: int        # Позиция в исходном тексте
    end_pos: int
    start_line: int
    end_line: int
    
    @property
    def formula(self) -> str:
        """Формула без delimiters."""
        if self.latex_type == LatexType.INLINE:
            return self.content[1:-1]
        elif self.latex_type == LatexType.DISPLAY:
            return self.content[2:-2]
        else:
            # Environment
            return self.content

class LatexExtractor:
    """
    Извлечение LaTeX формул из текста.
    """
    
    # Patterns
    DISPLAY_PATTERN = r'\$\$(.+?)\$\$'
    INLINE_PATTERN = r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)'
    
    # Environment patterns
    EQUATION_ENVS = ['equation', 'align', 'gather', 'multline', 'eqnarray']
    ENV_PATTERN = r'\\begin\{(%s)\*?\}(.+?)\\end\{\1\*?\}'
    
    def extract(self, text: str) -> list[LatexBlock]:
        """Извлечь все LaTeX blocks."""
        blocks = []
        
        # 1. Display math ($$...$$)
        blocks.extend(self._extract_display(text))
        
        # 2. Equation environments
        blocks.extend(self._extract_environments(text))
        
        # 3. Inline math ($...$) - только если нужно
        # blocks.extend(self._extract_inline(text))
        
        # Sort by position
        blocks.sort(key=lambda b: b.start_pos)
        
        return blocks
    
    def _extract_display(self, text: str) -> list[LatexBlock]:
        """Извлечь display math ($$...$$)."""
        blocks = []
        
        for match in re.finditer(self.DISPLAY_PATTERN, text, re.DOTALL):
            blocks.append(LatexBlock(
                content=match.group(0),
                latex_type=LatexType.DISPLAY,
                start_pos=match.start(),
                end_pos=match.end(),
                start_line=text[:match.start()].count('\n'),
                end_line=text[:match.end()].count('\n')
            ))
        
        return blocks
    
    def _extract_environments(self, text: str) -> list[LatexBlock]:
        """Извлечь equation environments."""
        blocks = []
        
        env_names = '|'.join(self.EQUATION_ENVS)
        pattern = self.ENV_PATTERN % env_names
        
        for match in re.finditer(pattern, text, re.DOTALL):
            blocks.append(LatexBlock(
                content=match.group(0),
                latex_type=LatexType.ENVIRONMENT,
                start_pos=match.start(),
                end_pos=match.end(),
                start_line=text[:match.start()].count('\n'),
                end_line=text[:match.end()].count('\n')
            ))
        
        return blocks
    
    def _extract_inline(self, text: str) -> list[LatexBlock]:
        """Извлечь inline math ($...$)."""
        blocks = []
        
        # Более сложный pattern чтобы избежать false positives
        for match in re.finditer(self.INLINE_PATTERN, text):
            # Проверить, что это не часть display math
            if text[match.start()-1:match.start()] == '$':
                continue
            if match.end() < len(text) and text[match.end()] == '$':
                continue
            
            blocks.append(LatexBlock(
                content=match.group(0),
                latex_type=LatexType.INLINE,
                start_pos=match.start(),
                end_pos=match.end(),
                start_line=text[:match.start()].count('\n'),
                end_line=text[:match.end()].count('\n')
            ))
        
        return blocks
```

### Интеграция с Parser

```python
class MarkdownParser:
    def __init__(self):
        self.latex_extractor = LatexExtractor()
    
    def parse(self, text: str) -> ParsedDocument:
        # 1. Extract LaTeX blocks (treat as atomic)
        latex_blocks = self.latex_extractor.extract(text)
        
        # 2. Replace with placeholders for safe parsing
        safe_text, latex_map = self._replace_latex_with_placeholders(
            text, latex_blocks
        )
        
        # 3. Parse remaining content
        parsed = self._parse_content(safe_text)
        
        # 4. Restore LaTeX blocks
        parsed = self._restore_latex(parsed, latex_map)
        
        # 5. Add latex blocks to analysis
        parsed.latex_blocks = latex_blocks
        
        return parsed
```

### Интеграция с Strategy

```python
class CodeAwareStrategy(BaseStrategy):
    def apply(
        self,
        text: str,
        analysis: ContentAnalysis,
        config: ChunkConfig
    ) -> list[Chunk]:
        # Treat LaTeX blocks similar to code blocks
        atomic_blocks = []
        
        # Add code blocks
        atomic_blocks.extend(analysis.code_blocks)
        
        # Add LaTeX blocks (display only)
        for latex in analysis.latex_blocks:
            if latex.latex_type in [LatexType.DISPLAY, LatexType.ENVIRONMENT]:
                atomic_blocks.append(latex)
        
        # Never split atomic blocks
        return self._chunk_preserving_atomic(text, atomic_blocks, config)
```

---

## Примеры

### Display Math

```markdown
The Euler's identity:

$$
e^{i\pi} + 1 = 0
$$

This is considered one of the most beautiful equations.
```

**Результат:** Формула и объяснение в одном чанке.

### Equation Environment

```markdown
Maxwell's equations in differential form:

\begin{align}
\nabla \cdot \mathbf{E} &= \frac{\rho}{\epsilon_0} \\
\nabla \cdot \mathbf{B} &= 0 \\
\nabla \times \mathbf{E} &= -\frac{\partial \mathbf{B}}{\partial t} \\
\nabla \times \mathbf{B} &= \mu_0\mathbf{J} + \mu_0\epsilon_0\frac{\partial \mathbf{E}}{\partial t}
\end{align}
```

**Результат:** Весь блок align как atomic unit.

---

## Тестирование

### Unit Tests

```python
def test_extract_display_math():
    """Display math извлекается"""
    text = "Text $$x^2$$ more text"
    blocks = LatexExtractor().extract(text)
    assert len(blocks) == 1
    assert blocks[0].latex_type == LatexType.DISPLAY

def test_extract_equation_env():
    """Equation environment извлекается"""
    text = r"Text \begin{equation}x=1\end{equation} more"
    blocks = LatexExtractor().extract(text)
    assert len(blocks) == 1
    assert blocks[0].latex_type == LatexType.ENVIRONMENT

def test_multiline_display():
    """Multiline display math извлекается"""
    text = "$$\nx = 1\ny = 2\n$$"
    blocks = LatexExtractor().extract(text)
    assert len(blocks) == 1

def test_latex_not_split():
    """LaTeX blocks не разрываются"""
    
def test_latex_with_context():
    """LaTeX сохраняется с окружающим контекстом"""
```

---

## Ожидаемые улучшения

### Типы документов

| Тип | Поддержка до | Поддержка после |
|-----|--------------|-----------------|
| Scientific papers | ⚠️ | ✅ |
| Math documentation | ⚠️ | ✅ |
| Academic notes | ⚠️ | ✅ |
| Technical specs | ⚠️ | ✅ |

---

## Конфигурация

```python
@dataclass
class ChunkConfig:
    # LaTeX handling
    preserve_latex: bool = True
    latex_context_binding: bool = True  # Bind to explanation
```

---

## Зависимости

### Изменяет

- `MarkdownParser` — latex extraction
- `ContentAnalysis` — latex_blocks field
- `CodeAwareStrategy` — treat latex as atomic

### Не требует внешних зависимостей

Только regex — нет ML или heavy dependencies.

---

## Риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| False positives ($ in text) | Medium | Low | Conservative patterns |
| Complex nested LaTeX | Low | Low | Basic support first |

---

## Acceptance Criteria

- [ ] Display math ($$...$$) распознаётся
- [ ] Equation environments распознаются
- [ ] LaTeX blocks не разрываются
- [ ] Multiline formulas поддерживаются
- [ ] Context binding работает
- [ ] preserve_latex конфигурируется
- [ ] Inline math (опционально)

---

## Примеры из тестового корпуса

### Директория: `tests/corpus/scientific/`

Добавлены файлы с разнообразным LaTeX-контентом для тестирования:

| Файл | Описание | LaTeX Features |
|------|----------|----------------|
| [machine-learning-equations.md](../../../tests/corpus/scientific/machine-learning-equations.md) | ML формулы: KL-Divergence, GAN, VAE, Diffusion | Display math `$$...$$`, inline `$...$`, align environments |
| [statistics-fundamentals.md](../../../tests/corpus/scientific/statistics-fundamentals.md) | Статистика: распределения, тесты, регрессия | Формулы с греческими буквами, суммы, интегралы |
| [calculus-analysis.md](../../../tests/corpus/scientific/calculus-analysis.md) | Математический анализ: пределы, производные, интегралы | Multiline displays, limits, fractions |
| [linear-algebra-essentials.md](../../../tests/corpus/scientific/linear-algebra-essentials.md) | Линейная алгебра: матрицы, SVD, eigenvalues | Matrices, vectors, determinants |
| [physics-equations.md](../../../tests/corpus/scientific/physics-equations.md) | Физика: механика, электромагнетизм, квантовая механика | Maxwell's equations, align blocks |
| [neural-network-backprop.md](../../../tests/corpus/scientific/neural-network-backprop.md) | Backpropagation в нейросетях | Mixed inline/display, cases |

### Покрытие LaTeX-паттернов

- **Display math:** `$$...$$` — все файлы
- **Inline math:** `$...$` — все файлы
- **Align environments:** `\begin{align}...\end{align}` — physics, ML
- **Matrices:** `\begin{pmatrix}...\end{pmatrix}` — linear algebra
- **Greek letters:** $\alpha, \beta, \gamma, \sigma, \lambda$ — все файлы
- **Fractions:** `\frac{}{}` — все файлы
- **Subscripts/superscripts:** $x_i$, $x^2$ — все файлы
- **Summations:** $\sum_{i=1}^{n}$ — statistics, calculus
- **Integrals:** $\int_{-\infty}^{\infty}$ — calculus, physics

### Рекомендации по тестированию

1. **Атомарность:** Display формулы не должны разрываться между чанками
2. **Контекст:** Формула должна оставаться с объяснительным текстом
3. **Multiline:** `align` блоки сохраняются целиком
4. **Inline:** Параграфы с `$...$` не разбиваются посередине формулы
