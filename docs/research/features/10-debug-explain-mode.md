# Feature 10: Debug/Explain Mode

## Краткое описание

Режим объяснения решений chunker — пользователи могут понять, почему chunker принял определённые решения о границах и стратегии.

---

## Метаданные

| Параметр | Значение |
|----------|----------|
| **Фаза** | 3 — Интеграция и Adoption |
| **Приоритет** | MEDIUM |
| **Effort** | 2-3 дня |
| **Impact** | Medium |
| **Уникальность** | No |

---

## Проблема

### Текущее состояние

- Chunker работает как "чёрный ящик"
- Пользователи не понимают, почему получились такие чанки
- Сложно отлаживать неоптимальные результаты

### User Needs

- C9.3: "No strategy explanation" — Low frequency, Low severity
- C9.4: "Hard to debug chunking" — Medium frequency, Medium severity

### Типичные вопросы пользователей

1. "Почему этот код оказался в отдельном чанке?"
2. "Почему была выбрана эта стратегия?"
3. "Почему граница прошла именно здесь?"
4. "Как улучшить результат для моего документа?"

---

## Решение

### Архитектура

```python
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class DecisionType(Enum):
    STRATEGY_SELECTION = "strategy_selection"
    BOUNDARY_PLACEMENT = "boundary_placement"
    CHUNK_MERGE = "chunk_merge"
    CHUNK_SPLIT = "chunk_split"
    ELEMENT_PRESERVATION = "element_preservation"

@dataclass
class Decision:
    """Одно решение chunker."""
    type: DecisionType
    description: str
    reason: str
    line_number: Optional[int] = None
    details: dict = field(default_factory=dict)

@dataclass
class ChunkExplanation:
    """Объяснение для одного чанка."""
    chunk_index: int
    start_line: int
    end_line: int
    decisions: list[Decision] = field(default_factory=list)
    
    def summary(self) -> str:
        """Краткое summary объяснения."""
        return f"Chunk {self.chunk_index}: {len(self.decisions)} decisions"

@dataclass
class ExplainResult:
    """Полный результат с объяснениями."""
    chunks: list[Chunk]
    strategy_used: str
    explanations: list[ChunkExplanation]
    global_decisions: list[Decision]
    
    def print_report(self) -> None:
        """Вывести human-readable отчёт."""
        print(f"=== Chunking Explanation ===\n")
        print(f"Strategy: {self.strategy_used}")
        print(f"Total chunks: {len(self.chunks)}\n")
        
        print("Global Decisions:")
        for decision in self.global_decisions:
            print(f"  - {decision.description}")
            print(f"    Reason: {decision.reason}")
        
        print("\nChunk Details:")
        for explanation in self.explanations:
            print(f"\n  Chunk {explanation.chunk_index} "
                  f"(lines {explanation.start_line}-{explanation.end_line}):")
            for decision in explanation.decisions:
                print(f"    - {decision.description}")
```

### Integration с Chunker

```python
class MarkdownChunker:
    def chunk(
        self,
        text: str,
        explain: bool = False
    ) -> ChunkingResult | ExplainResult:
        """
        Chunk markdown text.
        
        Args:
            text: Markdown text to chunk
            explain: If True, return ExplainResult with explanations
            
        Returns:
            ChunkingResult or ExplainResult (if explain=True)
        """
        # Parse
        parsed = self.parser.parse(text)
        analysis = self.analyzer.analyze(parsed)
        
        # Select strategy with explanation
        strategy, strategy_decisions = self._select_strategy_explained(
            analysis
        ) if explain else (self._select_strategy(analysis), [])
        
        # Apply strategy with explanation
        if explain:
            chunks, chunk_explanations = strategy.apply_explained(
                text, analysis, self.config
            )
            return ExplainResult(
                chunks=chunks,
                strategy_used=strategy.name,
                explanations=chunk_explanations,
                global_decisions=strategy_decisions
            )
        else:
            chunks = strategy.apply(text, analysis, self.config)
            return ChunkingResult(chunks=chunks, strategy_used=strategy.name)
    
    def _select_strategy_explained(
        self,
        analysis: ContentAnalysis
    ) -> tuple[BaseStrategy, list[Decision]]:
        """Выбор стратегии с объяснением."""
        decisions = []
        
        # Check CodeAware conditions
        if analysis.code_ratio >= 0.3 or analysis.code_block_count >= 1:
            decisions.append(Decision(
                type=DecisionType.STRATEGY_SELECTION,
                description="Selected CodeAware strategy",
                reason=f"code_ratio={analysis.code_ratio:.2%} >= 30% "
                       f"OR code_blocks={analysis.code_block_count} >= 1",
                details={"code_ratio": analysis.code_ratio}
            ))
            return CodeAwareStrategy(self.config), decisions
        
        # Check Structural conditions
        if analysis.header_count >= 3:
            decisions.append(Decision(
                type=DecisionType.STRATEGY_SELECTION,
                description="Selected Structural strategy",
                reason=f"header_count={analysis.header_count} >= 3",
                details={"header_count": analysis.header_count}
            ))
            return StructuralStrategy(self.config), decisions
        
        # Fallback
        decisions.append(Decision(
            type=DecisionType.STRATEGY_SELECTION,
            description="Selected Fallback strategy",
            reason="No specific content patterns detected",
            details={}
        ))
        return FallbackStrategy(self.config), decisions
```

### Strategy Implementation

```python
class BaseStrategy:
    def apply_explained(
        self,
        text: str,
        analysis: ContentAnalysis,
        config: ChunkConfig
    ) -> tuple[list[Chunk], list[ChunkExplanation]]:
        """Apply strategy with explanations."""
        raise NotImplementedError

class CodeAwareStrategy(BaseStrategy):
    def apply_explained(
        self,
        text: str,
        analysis: ContentAnalysis,
        config: ChunkConfig
    ) -> tuple[list[Chunk], list[ChunkExplanation]]:
        chunks = []
        explanations = []
        
        # Process code blocks
        for block in analysis.code_blocks:
            explanation = ChunkExplanation(
                chunk_index=len(chunks),
                start_line=block.start_line,
                end_line=block.end_line,
                decisions=[
                    Decision(
                        type=DecisionType.ELEMENT_PRESERVATION,
                        description=f"Preserved {block.language} code block",
                        reason="Code blocks are never split",
                        line_number=block.start_line,
                        details={"language": block.language, "lines": block.end_line - block.start_line}
                    )
                ]
            )
            
            # Add context binding decision if applicable
            if block.has_preceding_context:
                explanation.decisions.append(Decision(
                    type=DecisionType.CHUNK_MERGE,
                    description="Included preceding explanation",
                    reason="Code block bound to explaining paragraph"
                ))
            
            explanations.append(explanation)
            chunks.append(self._create_chunk(block, text))
        
        return chunks, explanations
```

---

## Usage Examples

### Basic Explain Mode

```python
from markdown_chunker import MarkdownChunker

chunker = MarkdownChunker()
result = chunker.chunk(markdown_text, explain=True)

# Print human-readable report
result.print_report()
```

Output:
```
=== Chunking Explanation ===

Strategy: CodeAware
Total chunks: 5

Global Decisions:
  - Selected CodeAware strategy
    Reason: code_ratio=45.00% >= 30% OR code_blocks=3 >= 1

Chunk Details:

  Chunk 0 (lines 1-15):
    - Preserved python code block
      Reason: Code blocks are never split
    - Included preceding explanation
      Reason: Code block bound to explaining paragraph

  Chunk 1 (lines 16-30):
    - Boundary placed at header
      Reason: ## Section Header creates natural boundary
```

### Programmatic Access

```python
result = chunker.chunk(text, explain=True)

# Analyze decisions
for explanation in result.explanations:
    print(f"Chunk {explanation.chunk_index}:")
    for decision in explanation.decisions:
        if decision.type == DecisionType.BOUNDARY_PLACEMENT:
            print(f"  Boundary at line {decision.line_number}: {decision.reason}")
```

### JSON Export

```python
import json

result = chunker.chunk(text, explain=True)

# Export as JSON for analysis
export = {
    "strategy": result.strategy_used,
    "chunk_count": len(result.chunks),
    "global_decisions": [
        {"type": d.type.value, "description": d.description, "reason": d.reason}
        for d in result.global_decisions
    ],
    "chunks": [
        {
            "index": e.chunk_index,
            "lines": f"{e.start_line}-{e.end_line}",
            "decisions": [
                {"type": d.type.value, "description": d.description}
                for d in e.decisions
            ]
        }
        for e in result.explanations
    ]
}

print(json.dumps(export, indent=2))
```

---

## Тестирование

### Unit Tests

```python
def test_explain_returns_explain_result():
    """explain=True возвращает ExplainResult"""
    chunker = MarkdownChunker()
    result = chunker.chunk("# Header\n\nText", explain=True)
    assert isinstance(result, ExplainResult)

def test_explain_has_strategy_decision():
    """ExplainResult содержит решение о стратегии"""
    result = chunker.chunk(text, explain=True)
    strategy_decisions = [
        d for d in result.global_decisions
        if d.type == DecisionType.STRATEGY_SELECTION
    ]
    assert len(strategy_decisions) >= 1

def test_explain_chunk_count_matches():
    """Количество explanations = количество chunks"""
    result = chunker.chunk(text, explain=True)
    assert len(result.explanations) == len(result.chunks)

def test_explain_code_preservation():
    """Code block preservation объясняется"""
    
def test_print_report():
    """print_report не вызывает ошибок"""
```

---

## Ожидаемые результаты

### User Benefits

1. **Понимание поведения** — ясно, почему chunker так работает
2. **Отладка** — легко найти причину неоптимальных результатов
3. **Настройка** — понимание, какие параметры менять
4. **Документация** — примеры в explain mode как обучающий материал

---

## Риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Performance overhead | Medium | Low | Only when explain=True |
| Verbose output | Low | Low | Levels of detail |

---

## Acceptance Criteria

- [ ] `explain=True` возвращает ExplainResult
- [ ] Strategy selection объясняется
- [ ] Boundary decisions объясняются
- [ ] Element preservation объясняется
- [ ] print_report() работает
- [ ] JSON export работает
- [ ] Performance impact < 5% when explain=False
- [ ] Документация с примерами

---

## Примеры из тестового корпуса

В ТЕСТОВОМ КОРПУСЕ ПРИМЕРОВ СЕЙЧАС НЕТ.

Эта фича является инструментом отладки и не требует специфических тестовых файлов. Для демонстрации работы explain mode можно использовать любые файлы из `tests/corpus/`.

Рекомендуется использовать файлы с разными стратегиями:
- `tests/corpus/changelogs/` — для Structural strategy
- `tests/corpus/github_readmes/python/face_recognition.md` — для CodeAware strategy
- `tests/corpus/personal_notes/unstructured/` — для Fallback strategy
