# Целевая Архитектура: Компоненты

## Parser (parser.py)

```python
"""
Парсинг markdown документов.

Единственная точка парсинга — результат кэшируется и передаётся дальше.
"""

import re
from typing import List
from .types import ContentAnalysis, CodeBlock, Header, Table


class Parser:
    """
    Парсер markdown документов.
    
    Извлекает структурные элементы и вычисляет метрики
    для выбора стратегии чанкинга.
    """
    
    def parse(self, md_text: str) -> ContentAnalysis:
        """
        Парсинг документа.
        
        Args:
            md_text: Markdown текст
            
        Returns:
            ContentAnalysis с метриками и извлечёнными элементами
        """
        # Нормализация line endings (FINDING-EDGE-2 fix)
        md_text = self._normalize_line_endings(md_text)
        
        lines = md_text.split('\n')
    
    def _normalize_line_endings(self, text: str) -> str:
        """
        Нормализация line endings к Unix-стилю.
        
        Конвертирует:
        - \r\n (Windows) → \n
        - \r (old Mac) → \n
        """
        return text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Извлечение элементов
        code_blocks = self._extract_code_blocks(md_text)
        headers = self._extract_headers(lines)
        tables = self._extract_tables(md_text)
        
        # Вычисление метрик
        total_chars = len(md_text)
        total_lines = len(lines)
        
        code_chars = sum(len(b.full_content) for b in code_blocks)
        code_ratio = code_chars / total_chars if total_chars > 0 else 0.0
        
        max_depth = max((h.level for h in headers), default=0)
        
        return ContentAnalysis(
            total_chars=total_chars,
            total_lines=total_lines,
            code_ratio=code_ratio,
            text_ratio=1.0 - code_ratio,
            code_block_count=len(code_blocks),
            header_count=len(headers),
            table_count=len(tables),
            max_header_depth=max_depth,
            code_blocks=[self._code_block_to_dict(b) for b in code_blocks],
            headers=[self._header_to_dict(h) for h in headers],
            tables=[self._table_to_dict(t) for t in tables],
        )
    
    def _extract_code_blocks(self, text: str) -> List[CodeBlock]:
        """Извлечение code blocks."""
        pattern = r'^```(\w*)\n(.*?)^```'
        blocks = []
        
        for match in re.finditer(pattern, text, re.MULTILINE | re.DOTALL):
            lang = match.group(1)
            content = match.group(2).rstrip('\n')
            start = text[:match.start()].count('\n') + 1
            end = text[:match.end()].count('\n') + 1
            
            blocks.append(CodeBlock(
                content=content,
                language=lang,
                start_line=start,
                end_line=end,
            ))
        
        return blocks
    
    def _extract_headers(self, lines: List[str]) -> List[Header]:
        """Извлечение заголовков."""
        headers = []
        
        for i, line in enumerate(lines, 1):
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                headers.append(Header(
                    text=match.group(2).strip(),
                    level=len(match.group(1)),
                    line=i,
                ))
        
        return headers
    
    def _extract_tables(self, text: str) -> List[Table]:
        """Извлечение таблиц."""
        # Простая эвристика: строки с | и разделитель ---
        tables = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            if '|' in lines[i] and i + 1 < len(lines) and '---' in lines[i + 1]:
                start = i + 1
                end = i + 1
                
                # Найти конец таблицы
                while end < len(lines) and '|' in lines[end]:
                    end += 1
                
                content = '\n'.join(lines[start-1:end])
                tables.append(Table(
                    content=content,
                    start_line=start,
                    end_line=end,
                    row_count=end - start,
                ))
                i = end
            else:
                i += 1
        
        return tables
    
    def _code_block_to_dict(self, block: CodeBlock) -> dict:
        return {
            "content": block.content,
            "language": block.language,
            "start_line": block.start_line,
            "end_line": block.end_line,
        }
    
    def _header_to_dict(self, header: Header) -> dict:
        return {
            "text": header.text,
            "level": header.level,
            "line": header.line,
        }
    
    def _table_to_dict(self, table: Table) -> dict:
        return {
            "content": table.content,
            "start_line": table.start_line,
            "end_line": table.end_line,
        }
```

## MarkdownChunker (chunker.py)

```python
"""
Главный класс чанкинга.

Линейный pipeline: parse → select → apply → post-process → return
"""

import time
from typing import List, Optional
from .types import Chunk, ChunkingResult, ContentAnalysis
from .config import ChunkConfig
from .parser import Parser
from .validator import Validator
from .strategies import CodeAwareStrategy, StructuralStrategy, FallbackStrategy
from .strategies.base import BaseStrategy


class MarkdownChunker:
    """
    Главный интерфейс для чанкинга markdown документов.
    
    Usage:
        chunker = MarkdownChunker()
        result = chunker.chunk("# Hello\n\nWorld")
        print(result.chunks)
    """
    
    def __init__(self, config: Optional[ChunkConfig] = None):
        self.config = config or ChunkConfig.default()
        self._parser = Parser()
        self._validator = Validator()
        self._strategies: List[BaseStrategy] = [
            CodeAwareStrategy(),
            StructuralStrategy(),
            FallbackStrategy(),
        ]
    
    def chunk(self, md_text: str) -> ChunkingResult:
        """
        Разбить markdown на чанки.
        
        Args:
            md_text: Markdown текст
            
        Returns:
            ChunkingResult с чанками и метаданными
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        # Handle empty input
        if not md_text or not md_text.strip():
            return ChunkingResult(
                chunks=[],
                strategy_used="none",
                processing_time=time.time() - start_time,
            )
        
        # 1. Parse (один раз)
        analysis = self._parser.parse(md_text)
        
        # 2. Select strategy
        strategy = self._select_strategy(analysis)
        
        # 3. Apply strategy
        try:
            chunks = strategy.apply(md_text, analysis, self.config)
        except Exception as e:
            errors.append(f"Strategy {strategy.name} failed: {e}")
            # Fallback
            chunks = FallbackStrategy().apply(md_text, analysis, self.config)
            strategy = FallbackStrategy()
        
        # 4. Post-process
        chunks = self._post_process(chunks, analysis)
        
        # 5. Validate (включая PROP-1: No Content Loss)
        validation = self._validator.validate(chunks, self.config, md_text)
        if not validation.is_valid:
            errors.extend(validation.errors)
        warnings.extend(validation.warnings)
        
        return ChunkingResult(
            chunks=chunks,
            strategy_used=strategy.name,
            processing_time=time.time() - start_time,
            errors=errors,
            warnings=warnings,
        )
    
    def _select_strategy(self, analysis: ContentAnalysis) -> BaseStrategy:
        """Выбор стратегии на основе анализа."""
        # Override
        if self.config.strategy_override:
            for s in self._strategies:
                if s.name == self.config.strategy_override:
                    return s
        
        # Auto-select
        for strategy in self._strategies:
            if strategy.can_handle(analysis, self.config):
                return strategy
        
        # Fallback always handles
        return self._strategies[-1]
    
    def _post_process(
        self, 
        chunks: List[Chunk], 
        analysis: ContentAnalysis
    ) -> List[Chunk]:
        """
        Пост-обработка чанков.
        
        Включает:
        - Валидацию code fence balance (MC-002 fix)
        - Применение overlap (MC-003 fix)
        - Сортировку по позиции (PROP-3)
        - Пометку oversize чанков (Phase 1.2 fix)
        """
        if not chunks:
            return chunks
        
        # MC-002 fix: Validate code fence balance
        chunks = self._validate_code_fence_balance(chunks)
        
        # Apply overlap
        if self.config.overlap_size > 0:
            chunks = self._apply_overlap(chunks)
        
        # Sort by position (PROP-3: Monotonic ordering)
        chunks = sorted(chunks, key=lambda c: (c.start_line, c.end_line))
        
        # Phase 1.2 fix: Flag oversize chunks
        chunks = self._flag_oversize_chunks(chunks)
        
        return chunks
    
    def _validate_code_fence_balance(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Проверка баланса code fences (MC-002 fix).
        
        Каждый чанк должен иметь чётное количество ```.
        Нечётное означает, что code block разрезан.
        """
        for i, chunk in enumerate(chunks):
            fence_count = chunk.content.count('```')
            if fence_count % 2 != 0:
                # Логируем ошибку, но не падаем
                chunk.metadata["fence_balance_error"] = True
                chunk.metadata["fence_count"] = fence_count
        return chunks
    
    def _flag_oversize_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Пометка oversize чанков (Phase 1.2 fix).
        
        Чанки больше max_chunk_size должны иметь флаг allow_oversize.
        """
        for chunk in chunks:
            if chunk.size > self.config.max_chunk_size:
                if not chunk.metadata.get("allow_oversize"):
                    # Определить причину
                    if '```' in chunk.content:
                        reason = "code_block_integrity"
                    elif '|' in chunk.content and '---' in chunk.content:
                        reason = "table_integrity"
                    else:
                        reason = "section_integrity"
                    
                    chunk.metadata["allow_oversize"] = True
                    chunk.metadata["oversize_reason"] = reason
        return chunks
    
    def _apply_overlap(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Добавление overlap в метаданные.
        
        ВАЖНО (MC-003 fix): Overlap не должен разрезать code blocks.
        """
        for i in range(1, len(chunks)):
            prev_content = chunks[i-1].content
            
            # Ограничение overlap до 50% размера чанка (Phase 2.2 fix)
            max_overlap = min(
                self.config.overlap_size,
                len(prev_content) // 2
            )
            
            overlap = prev_content[-max_overlap:]
            
            # MC-003 fix: Не разрезать code blocks
            # Если overlap начинается внутри code block, обрезать до начала блока
            if '```' in overlap:
                fence_pos = overlap.rfind('```')
                # Проверить, что это не закрывающий fence
                if overlap.count('```') % 2 == 1:
                    # Нечётное количество — обрезать
                    overlap = overlap[fence_pos + 3:].lstrip()
            
            # Симметричное обрезание (Phase 2.1 fix)
            overlap = overlap.strip()
            
            # Найти границу слова
            if overlap and not overlap[0].isspace():
                space_pos = overlap.find(' ')
                if space_pos > 0:
                    overlap = overlap[space_pos + 1:]
            
            chunks[i].metadata["previous_content"] = overlap
            chunks[i].metadata["overlap_size"] = len(overlap)
        
        return chunks
    
    def get_available_strategies(self) -> List[str]:
        """Список доступных стратегий."""
        return [s.name for s in self._strategies]
```

## Validator (validator.py)

```python
"""
Валидация чанков.

Проверяет доменные свойства PROP-1, PROP-2, PROP-3, PROP-4, PROP-5.
"""

from typing import List
from .types import Chunk, ValidationResult
from .config import ChunkConfig


class Validator:
    """
    Валидатор чанков.
    
    Проверяет соответствие доменным свойствам.
    """
    
    def validate(
        self, 
        chunks: List[Chunk], 
        config: ChunkConfig,
        original_text: str = None
    ) -> ValidationResult:
        """
        Валидация списка чанков.
        
        Проверяет:
        - PROP-1: No content loss (если передан original_text)
        - PROP-2: Size bounds
        - PROP-3: Monotonic ordering
        - PROP-4: No empty chunks
        - PROP-5: Valid line numbers
        """
        errors = []
        warnings = []
        
        # PROP-1: No content loss
        if original_text:
            self._validate_content_completeness(original_text, chunks, errors, warnings)
        
        for i, chunk in enumerate(chunks):
            # PROP-2: Size bounds
            if chunk.size > config.max_chunk_size:
                if not chunk.is_oversize:
                    errors.append(
                        f"Chunk {i}: size {chunk.size} exceeds max "
                        f"{config.max_chunk_size} without oversize flag"
                    )
            
            # PROP-4: No empty (уже в Chunk.__post_init__)
            # Дополнительная проверка на случай обхода
            if not chunk.content.strip():
                errors.append(f"Chunk {i}: empty content")
            
            # PROP-5: Valid line numbers (уже в Chunk.__post_init__)
            if chunk.start_line < 1:
                errors.append(f"Chunk {i}: invalid start_line {chunk.start_line}")
            if chunk.end_line < chunk.start_line:
                errors.append(
                    f"Chunk {i}: end_line {chunk.end_line} < "
                    f"start_line {chunk.start_line}"
                )
        
        # PROP-3: Monotonic ordering
        for i in range(len(chunks) - 1):
            if chunks[i].start_line > chunks[i+1].start_line:
                errors.append(
                    f"Chunks {i} and {i+1}: out of order "
                    f"({chunks[i].start_line} > {chunks[i+1].start_line})"
                )
        
        # Warnings for small chunks
        for i, chunk in enumerate(chunks):
            if chunk.size < config.min_chunk_size:
                warnings.append(
                    f"Chunk {i}: size {chunk.size} below min {config.min_chunk_size}"
                )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
    
    def _validate_content_completeness(
        self,
        original_text: str,
        chunks: List[Chunk],
        errors: List[str],
        warnings: List[str]
    ) -> None:
        """
        PROP-1: No Content Loss.
        
        Проверяет, что весь контент сохранён в чанках.
        """
        if not chunks:
            if original_text.strip():
                errors.append("PROP-1: No chunks produced for non-empty input")
            return
        
        # Подсчёт символов (без учёта overlap)
        input_chars = len(original_text.strip())
        output_chars = 0
        
        for i, chunk in enumerate(chunks):
            content = chunk.content
            # Вычесть overlap из подсчёта (он дублируется)
            overlap_size = chunk.metadata.get("overlap_size", 0)
            if i > 0 and overlap_size > 0:
                # Первый чанк не имеет overlap
                output_chars += len(content) - overlap_size
            else:
                output_chars += len(content)
        
        # Допускаем 5% потерь из-за нормализации whitespace
        if output_chars < input_chars * 0.95:
            errors.append(
                f"PROP-1: Content loss detected - "
                f"input {input_chars} chars, output {output_chars} chars "
                f"({output_chars/input_chars*100:.1f}%)"
            )
        elif output_chars < input_chars * 0.99:
            warnings.append(
                f"PROP-1: Minor content difference - "
                f"input {input_chars} chars, output {output_chars} chars"
            )
    
    def _validate_overlap_content_match(
        self,
        chunks: List[Chunk],
        errors: List[str],
        warnings: List[str]
    ) -> None:
        """
        Проверка соответствия overlap content и metadata (FINDING-PROP1-1, PROP1-2 fix).
        
        Для каждого чанка с overlap:
        - overlap_size должен соответствовать реальному размеру previous_content
        - previous_content должен быть суффиксом предыдущего чанка
        """
        for i in range(1, len(chunks)):
            chunk = chunks[i]
            prev_chunk = chunks[i - 1]
            
            overlap_size = chunk.metadata.get("overlap_size", 0)
            previous_content = chunk.metadata.get("previous_content", "")
            
            if overlap_size > 0:
                # Проверка 1: overlap_size соответствует previous_content
                if len(previous_content) != overlap_size:
                    warnings.append(
                        f"Chunk {i}: overlap_size ({overlap_size}) differs from "
                        f"previous_content length ({len(previous_content)})"
                    )
                
                # Проверка 2: previous_content является суффиксом предыдущего чанка
                if previous_content and not prev_chunk.content.endswith(previous_content):
                    warnings.append(
                        f"Chunk {i}: previous_content does not match "
                        f"end of chunk {i-1}"
                    )
    
    def _validate_table_containment(
        self,
        original_text: str,
        chunks: List[Chunk],
        errors: List[str],
        warnings: List[str]
    ) -> None:
        """
        Проверка целостности таблиц (FINDING-PROP7-1 fix).
        
        Каждая таблица должна быть полностью в одном чанке.
        """
        tables = self._extract_tables(original_text)
        
        for table in tables:
            table_header = table['content'].split('\n')[0]
            containing_chunks = [
                i for i, chunk in enumerate(chunks)
                if table_header in chunk.content
            ]
            
            if len(containing_chunks) == 0:
                errors.append(
                    f"PROP-7: Table at line {table['start_line']} not found in any chunk"
                )
            elif len(containing_chunks) > 1:
                errors.append(
                    f"PROP-7: Table at line {table['start_line']} spans multiple chunks"
                )
    
    def _extract_tables(self, text: str) -> List[dict]:
        """Извлечение таблиц из текста."""
        tables = []
        lines = text.split('\n')
        
        i = 0
        while i < len(lines):
            if '|' in lines[i] and i + 1 < len(lines) and '---' in lines[i + 1]:
                start = i
                content_lines = [lines[i]]
                i += 1
                
                while i < len(lines) and '|' in lines[i]:
                    content_lines.append(lines[i])
                    i += 1
                
                tables.append({
                    'start_line': start + 1,
                    'end_line': i,
                    'content': '\n'.join(content_lines)
                })
            else:
                i += 1
        
        return tables


```

## Диаграмма взаимодействия

```
┌─────────────────────────────────────────────────────────────┐
│                    MarkdownChunker                          │
│                                                             │
│  chunk(md_text)                                             │
│      │                                                      │
│      ├──► Parser.parse(md_text)                            │
│      │        └──► ContentAnalysis                         │
│      │                                                      │
│      ├──► _select_strategy(analysis)                       │
│      │        └──► Strategy                                │
│      │                                                      │
│      ├──► strategy.apply(md_text, analysis, config)        │
│      │        └──► List[Chunk]                             │
│      │                                                      │
│      ├──► _post_process(chunks, analysis)                  │
│      │        ├──► _apply_overlap()                        │
│      │        └──► sort by position                        │
│      │                                                      │
│      ├──► Validator.validate(chunks, config)               │
│      │        └──► ValidationResult                        │
│      │                                                      │
│      └──► ChunkingResult                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Принципы

1. **Один проход парсинга** — результат передаётся дальше
2. **Линейный pipeline** — без условных веток
3. **Централизованная валидация** — один Validator
4. **Простые компоненты** — каждый < 200 строк
