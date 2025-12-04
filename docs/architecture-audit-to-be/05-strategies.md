# Целевая Архитектура: Стратегии

## Обзор

3 стратегии вместо 6:
- **CodeAwareStrategy** — для документов с кодом, таблицами, смешанным контентом
- **StructuralStrategy** — для документов с иерархией заголовков
- **FallbackStrategy** — универсальный fallback по предложениям

## BaseStrategy (strategies/base.py)

```python
"""
Базовый класс для стратегий чанкинга.
"""

from abc import ABC, abstractmethod
from typing import List
from ..types import Chunk, ContentAnalysis
from ..config import ChunkConfig


class BaseStrategy(ABC):
    """
    Абстрактный базовый класс для стратегий.
    
    Каждая стратегия должна реализовать:
    - name: имя стратегии
    - priority: приоритет (меньше = выше)
    - can_handle(): может ли обработать контент
    - apply(): применить стратегию
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Имя стратегии."""
    
    @property
    @abstractmethod
    def priority(self) -> int:
        """Приоритет (1 = высший)."""
    
    @abstractmethod
    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        """Может ли стратегия обработать данный контент."""
    
    @abstractmethod
    def apply(
        self, 
        md_text: str, 
        analysis: ContentAnalysis, 
        config: ChunkConfig
    ) -> List[Chunk]:
        """Применить стратегию и вернуть чанки."""
    
    def _create_chunk(
        self,
        content: str,
        start_line: int,
        end_line: int,
        **metadata
    ) -> Chunk:
        """Создать чанк с метаданными стратегии."""
        return Chunk(
            content=content,
            start_line=start_line,
            end_line=end_line,
            metadata={
                "strategy": self.name,
                **metadata
            }
        )
    
    def _split_at_boundary(
        self, 
        content: str, 
        max_size: int
    ) -> List[str]:
        """
        Разбить контент по семантическим границам.
        
        Приоритет: параграф > предложение > слово
        """
        if len(content) <= max_size:
            return [content]
        
        parts = []
        remaining = content
        
        while remaining:
            if len(remaining) <= max_size:
                parts.append(remaining)
                break
            
            # Найти границу
            split_pos = self._find_boundary(remaining, max_size)
            
            parts.append(remaining[:split_pos].rstrip())
            remaining = remaining[split_pos:].lstrip()
        
        return parts
    
    def _find_boundary(self, content: str, max_pos: int) -> int:
        """Найти лучшую границу для разбиения."""
        # Параграф
        pos = content.rfind('\n\n', 0, max_pos)
        if pos > 0:
            return pos + 2
        
        # Предложение
        for end in ['. ', '! ', '? ']:
            pos = content.rfind(end, 0, max_pos)
            if pos > 0:
                return pos + 2
        
        # Слово
        pos = content.rfind(' ', 0, max_pos)
        if pos > 0:
            return pos + 1
        
        # Hard split
        return max_pos
    
    def _validate_code_fence_balance(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Валидация баланса code fences (Phase 1.1 fix).
        
        Проверяет, что ни один чанк не имеет несбалансированных ```.
        Несбалансированные fences означают, что code block был разрезан.
        """
        for i, chunk in enumerate(chunks):
            fence_count = chunk.content.count('```')
            
            if fence_count % 2 != 0:
                # Несбалансированные fences — ошибка
                import logging
                logger = logging.getLogger(__name__)
                logger.error(
                    f"Chunk {i} has unbalanced code fences ({fence_count}). "
                    f"Code blocks should never be split."
                )
                chunk.metadata["fence_balance_error"] = True
                chunk.metadata["fence_count"] = fence_count
        
        return chunks
```

## CodeAwareStrategy (strategies/code_aware.py)

```python
"""
Стратегия для документов с кодом.

Объединяет функциональность бывших CodeStrategy, MixedStrategy, TableStrategy.
Обрабатывает документы с code blocks, таблицами, смешанным контентом.
"""

from typing import List
from ..types import Chunk, ContentAnalysis
from ..config import ChunkConfig
from .base import BaseStrategy


class CodeAwareStrategy(BaseStrategy):
    """
    Стратегия для документов с кодом и атомарными элементами.
    
    Приоритет: 1 (высший)
    
    Критерии применимости:
    - code_ratio >= 0.3 ИЛИ
    - code_block_count >= 1 ИЛИ
    - table_count >= 1
    
    Алгоритм:
    1. Извлечь атомарные блоки (code, tables)
    2. Разбить документ на сегменты вокруг атомарных блоков
    3. Группировать сегменты в чанки с учётом размеров
    4. Атомарные блоки не разбиваются (allow_oversize если нужно)
    """
    
    @property
    def name(self) -> str:
        return "code_aware"
    
    @property
    def priority(self) -> int:
        return 1
    
    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        """Может обработать если есть код или таблицы."""
        return (
            analysis.code_ratio >= config.code_threshold or
            analysis.code_block_count >= 1 or
            analysis.table_count >= 1
        )
    
    def apply(
        self, 
        md_text: str, 
        analysis: ContentAnalysis, 
        config: ChunkConfig
    ) -> List[Chunk]:
        """Применить стратегию."""
        chunks = []
        
        # 1. Извлечь атомарные блоки с позициями
        atomic_blocks = self._extract_atomic_blocks(md_text, analysis)
        
        # 2. Разбить на сегменты
        segments = self._split_around_atomic(md_text, atomic_blocks)
        
        # 3. Группировать в чанки
        current_content = ""
        current_start = 1
        
        for segment in segments:
            if segment.is_atomic:
                # Сначала flush накопленный текст
                if current_content.strip():
                    chunks.extend(self._create_text_chunks(
                        current_content, current_start, config
                    ))
                    current_content = ""
                
                # Добавить атомарный блок как отдельный чанк
                chunk = self._create_chunk(
                    content=segment.content,
                    start_line=segment.start_line,
                    end_line=segment.end_line,
                    content_type=segment.block_type,
                    allow_oversize=len(segment.content) > config.max_chunk_size
                )
                chunks.append(chunk)
                current_start = segment.end_line + 1
            else:
                # Накапливать текст
                if not current_content:
                    current_start = segment.start_line
                current_content += segment.content
        
        # Flush оставшийся текст
        if current_content.strip():
            chunks.extend(self._create_text_chunks(
                current_content, current_start, config
            ))
        
        return chunks
    
    def _extract_atomic_blocks(self, md_text: str, analysis: ContentAnalysis):
        """Извлечь code blocks и таблицы."""
        # Упрощённая реализация — детали в реальном коде
        blocks = []
        # ... извлечение code blocks по ```
        # ... извлечение таблиц по | и ---
        return blocks
    
    def _split_around_atomic(self, md_text: str, atomic_blocks):
        """Разбить текст на сегменты вокруг атомарных блоков."""
        # Упрощённая реализация
        segments = []
        # ... логика разбиения
        return segments
    
    def _create_text_chunks(
        self, 
        content: str, 
        start_line: int, 
        config: ChunkConfig
    ) -> List[Chunk]:
        """Создать чанки из текстового контента."""
        if len(content) <= config.max_chunk_size:
            return [self._create_chunk(
                content=content,
                start_line=start_line,
                end_line=start_line + content.count('\n'),
                content_type="text"
            )]
        
        # Разбить по границам
        parts = self._split_at_boundary(content, config.max_chunk_size)
        chunks = []
        current_line = start_line
        
        for part in parts:
            line_count = part.count('\n')
            chunks.append(self._create_chunk(
                content=part,
                start_line=current_line,
                end_line=current_line + line_count,
                content_type="text"
            ))
            current_line += line_count + 1
        
        return chunks
```

## StructuralStrategy (strategies/structural.py)

```python
"""
Стратегия для документов с иерархией заголовков.

Упрощённая версия бывшей StructuralStrategy (1720 строк → ~200 строк).
"""

from typing import List
from ..types import Chunk, ContentAnalysis
from ..config import ChunkConfig
from .base import BaseStrategy


class StructuralStrategy(BaseStrategy):
    """
    Стратегия для структурированных документов.
    
    Приоритет: 2
    
    Критерии применимости:
    - header_count >= 3 И
    - max_header_depth > 1
    
    Алгоритм:
    1. Разбить документ на секции по заголовкам
    2. Для каждой секции:
       - Если размер <= max_chunk_size → один чанк
       - Если размер > max_chunk_size → разбить по подзаголовкам или параграфам
    3. Добавить header_path в метаданные
    """
    
    @property
    def name(self) -> str:
        return "structural"
    
    @property
    def priority(self) -> int:
        return 2
    
    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        """Может обработать если есть структура заголовков."""
        return (
            analysis.header_count >= config.structure_threshold and
            analysis.max_header_depth > 1
        )
    
    def apply(
        self, 
        md_text: str, 
        analysis: ContentAnalysis, 
        config: ChunkConfig
    ) -> List[Chunk]:
        """Применить стратегию."""
        chunks = []
        
        # 1. Разбить на секции по заголовкам
        sections = self._split_by_headers(md_text)
        
        # 2. Обработать каждую секцию
        header_path = []
        
        for section in sections:
            # Обновить header_path
            header_path = self._update_header_path(
                header_path, section.header_level, section.header_text
            )
            
            # Создать чанки из секции
            section_chunks = self._process_section(
                section, header_path, config
            )
            chunks.extend(section_chunks)
        
        return chunks
    
    def _split_by_headers(self, md_text: str):
        """Разбить документ на секции по заголовкам."""
        import re
        
        sections = []
        header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        
        # Найти все заголовки
        matches = list(header_pattern.finditer(md_text))
        
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(md_text)
            
            sections.append({
                'header_level': len(match.group(1)),
                'header_text': match.group(2),
                'content': md_text[start:end],
                'start_pos': start
            })
        
        return sections
    
    def _update_header_path(
        self, 
        current_path: List[str], 
        level: int, 
        text: str
    ) -> List[str]:
        """Обновить путь заголовков."""
        # Обрезать путь до текущего уровня
        new_path = current_path[:level - 1]
        new_path.append(text)
        return new_path
    
    def _process_section(
        self, 
        section: dict, 
        header_path: List[str], 
        config: ChunkConfig
    ) -> List[Chunk]:
        """Обработать секцию и создать чанки."""
        content = section['content']
        
        # MC-001 fix: использовать oversize_tolerance для сохранения целостности секций
        # Если секция немного превышает max_chunk_size, лучше сохранить её целиком
        effective_max = int(config.max_chunk_size * (1 + config.oversize_tolerance))
        
        if len(content) <= effective_max:
            # Секция помещается в один чанк (с учётом tolerance)
            return [self._create_chunk(
                content=content,
                start_line=1,  # Упрощённо
                end_line=content.count('\n') + 1,
                content_type="section",
                header_path=header_path.copy(),
                allow_oversize=len(content) > config.max_chunk_size
            )]
        
        # Разбить по параграфам (секция слишком большая даже с tolerance)
        parts = self._split_at_boundary(content, config.max_chunk_size)
        chunks = []
        
        for part in parts:
            chunks.append(self._create_chunk(
                content=part,
                start_line=1,
                end_line=part.count('\n') + 1,
                content_type="section",
                header_path=header_path.copy()
            ))
        
        return chunks
```

## FallbackStrategy (strategies/fallback.py)

```python
"""
Универсальная fallback-стратегия.

Бывшая SentencesStrategy. Всегда может обработать любой контент.
"""

from typing import List
from ..types import Chunk, ContentAnalysis
from ..config import ChunkConfig
from .base import BaseStrategy


class FallbackStrategy(BaseStrategy):
    """
    Универсальная fallback-стратегия.
    
    Приоритет: 3 (низший)
    
    Критерии применимости:
    - Всегда True (универсальный fallback)
    
    Алгоритм:
    1. Разбить на параграфы
    2. Группировать параграфы до max_chunk_size
    3. Если параграф > max_chunk_size → разбить по предложениям
    """
    
    @property
    def name(self) -> str:
        return "fallback"
    
    @property
    def priority(self) -> int:
        return 3
    
    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        """Всегда может обработать."""
        return True
    
    def apply(
        self, 
        md_text: str, 
        analysis: ContentAnalysis, 
        config: ChunkConfig
    ) -> List[Chunk]:
        """Применить стратегию."""
        chunks = []
        
        # 1. Разбить на параграфы
        paragraphs = md_text.split('\n\n')
        
        # 2. Группировать в чанки
        current_content = ""
        current_start = 1
        current_line = 1
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                current_line += 2
                continue
            
            para_with_sep = para + '\n\n'
            
            # MC-001 fix: использовать oversize_tolerance
            effective_max = int(config.max_chunk_size * (1 + config.oversize_tolerance))
            
            # Проверить, поместится ли параграф
            if len(current_content) + len(para_with_sep) <= config.max_chunk_size:
                if not current_content:
                    current_start = current_line
                current_content += para_with_sep
            elif len(current_content) + len(para_with_sep) <= effective_max:
                # MC-001: немного превышает, но в пределах tolerance — сохранить целостность
                if not current_content:
                    current_start = current_line
                current_content += para_with_sep
            else:
                # Flush текущий чанк
                if current_content.strip():
                    chunks.append(self._create_chunk(
                        content=current_content.rstrip(),
                        start_line=current_start,
                        end_line=current_line - 1,
                        content_type="text",
                        allow_oversize=len(current_content) > config.max_chunk_size
                    ))
                
                # Начать новый чанк
                if len(para) <= config.max_chunk_size:
                    current_content = para_with_sep
                    current_start = current_line
                else:
                    # Параграф слишком большой — разбить
                    parts = self._split_at_boundary(para, config.max_chunk_size)
                    for part in parts:
                        chunks.append(self._create_chunk(
                            content=part,
                            start_line=current_line,
                            end_line=current_line + part.count('\n'),
                            content_type="text"
                        ))
                    current_content = ""
            
            current_line += para.count('\n') + 2
        
        # Flush оставшийся контент
        if current_content.strip():
            chunks.append(self._create_chunk(
                content=current_content.rstrip(),
                start_line=current_start,
                end_line=current_line - 1,
                content_type="text"
            ))
        
        return chunks
```

## StrategySelector

```python
"""
Выбор стратегии на основе анализа контента.
"""

from typing import List, Optional
from ..types import ContentAnalysis
from ..config import ChunkConfig
from .base import BaseStrategy
from .code_aware import CodeAwareStrategy
from .structural import StructuralStrategy
from .fallback import FallbackStrategy


class StrategySelector:
    """
    Выбирает оптимальную стратегию для документа.
    
    Порядок проверки (по приоритету):
    1. CodeAwareStrategy — если есть код или таблицы
    2. StructuralStrategy — если есть структура заголовков
    3. FallbackStrategy — всегда (универсальный fallback)
    """
    
    def __init__(self):
        self.strategies: List[BaseStrategy] = [
            CodeAwareStrategy(),
            StructuralStrategy(),
            FallbackStrategy(),
        ]
    
    def select(
        self, 
        analysis: ContentAnalysis, 
        config: ChunkConfig
    ) -> BaseStrategy:
        """Выбрать стратегию для контента."""
        for strategy in self.strategies:
            if strategy.can_handle(analysis, config):
                return strategy
        
        # Fallback всегда возвращает True, но на всякий случай
        return self.strategies[-1]
    
    def get_available_strategies(self) -> List[str]:
        """Получить список доступных стратегий."""
        return [s.name for s in self.strategies]
```

## Сравнение с текущей реализацией

| Аспект | Текущее | Целевое |
|--------|---------|---------|
| Количество стратегий | 6 | 3 |
| Строк кода в стратегиях | ~5000 | ~500 |
| Файлов стратегий | 7 | 4 |
| ListStrategy | Есть (исключена из auto) | Удалена |
| TableStrategy | Отдельная | Объединена в CodeAware |
| MixedStrategy | Отдельная | Объединена в CodeAware |
| Fallback-цепочка | 3 уровня | 1 уровень (FallbackStrategy) |

## Ключевые упрощения

1. **Удаление ListStrategy** — была исключена из auto-mode, значит не нужна
2. **Объединение Code + Mixed + Table** — общая логика обработки атомарных блоков
3. **Упрощение StructuralStrategy** — 1720 → ~200 строк, убраны Phase 2 и block-based
4. **Простой fallback** — без цепочки, FallbackStrategy всегда работает
5. **Единый StrategySelector** — простой выбор по приоритету

## MC-001 Fix: oversize_tolerance

Все стратегии используют `config.oversize_tolerance` для сохранения целостности контента:

```python
# Вычисление эффективного максимума с учётом tolerance
effective_max = int(config.max_chunk_size * (1 + config.oversize_tolerance))

# Пример: max_chunk_size=4096, oversize_tolerance=0.2
# effective_max = 4096 * 1.2 = 4915

# Если контент <= effective_max, сохраняем целиком
# Если контент > effective_max, разбиваем
```

Это решает проблему MC-001 (потеря контента при разбиении секций на границе max_chunk_size).
