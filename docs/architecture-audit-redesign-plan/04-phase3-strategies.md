# План Редизайна: Фаза 3 — Стратегии

## Цель

Сократить количество стратегий с 6 до 3, удалить дублирование кода.

## Длительность: 5-6 дней

## Текущее состояние

| Стратегия | Строк | Статус |
|-----------|-------|--------|
| CodeStrategy | 624 | → Объединить в CodeAware |
| MixedStrategy | 848 | → Объединить в CodeAware |
| TableStrategy | 465 | → Объединить в CodeAware |
| ListStrategy | 856 | → Удалить (исключена из auto) |
| StructuralStrategy | 1720 | → Упростить |
| SentencesStrategy | 525 | → Переименовать в Fallback |

**Итого:** ~5038 строк → ~500 строк

## Задачи

### 3.1 Создать BaseStrategy (0.5 дня)

```python
# markdown_chunker/strategies/base.py

from abc import ABC, abstractmethod
from typing import List
from ..types import Chunk, ContentAnalysis
from ..config import ChunkConfig


class BaseStrategy(ABC):
    """Базовый класс для стратегий."""
    
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
        """Может ли обработать контент."""
    
    @abstractmethod
    def apply(
        self, 
        md_text: str, 
        analysis: ContentAnalysis, 
        config: ChunkConfig
    ) -> List[Chunk]:
        """Применить стратегию."""
    
    def _create_chunk(self, content: str, start_line: int, end_line: int, **metadata) -> Chunk:
        """Создать чанк."""
        return Chunk(
            content=content,
            start_line=start_line,
            end_line=end_line,
            metadata={"strategy": self.name, **metadata}
        )
    
    def _split_at_boundary(self, content: str, max_size: int) -> List[str]:
        """Разбить по семантическим границам."""
        # ... реализация
```

### 3.2 Создать CodeAwareStrategy (2 дня)

**Объединяет:** CodeStrategy + MixedStrategy + TableStrategy

**Логика:**
1. Извлечь атомарные блоки (code, tables)
2. Разбить документ на сегменты вокруг атомарных блоков
3. Группировать сегменты в чанки
4. Атомарные блоки не разбиваются

```python
# markdown_chunker/strategies/code_aware.py

class CodeAwareStrategy(BaseStrategy):
    """Стратегия для документов с кодом и таблицами."""
    
    @property
    def name(self) -> str:
        return "code_aware"
    
    @property
    def priority(self) -> int:
        return 1
    
    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        return (
            analysis.code_ratio >= config.code_threshold or
            analysis.code_block_count >= 1 or
            analysis.table_count >= 1
        )
    
    def apply(self, md_text: str, analysis: ContentAnalysis, config: ChunkConfig) -> List[Chunk]:
        chunks = []
        
        # 1. Извлечь атомарные блоки
        atomic_blocks = self._get_atomic_blocks(analysis)
        
        # 2. Разбить на сегменты
        segments = self._split_around_atomic(md_text, atomic_blocks)
        
        # 3. Создать чанки
        for segment in segments:
            if segment.is_atomic:
                # Атомарный блок — один чанк
                chunks.append(self._create_chunk(
                    content=segment.content,
                    start_line=segment.start_line,
                    end_line=segment.end_line,
                    content_type=segment.block_type,
                    allow_oversize=len(segment.content) > config.max_chunk_size
                ))
            else:
                # Текст — разбить если нужно
                chunks.extend(self._chunk_text(segment, config))
        
        return chunks
```

### 3.3 Упростить StructuralStrategy (1.5 дня)

**Текущее:** 1720 строк с Phase 2 и block-based логикой
**Целевое:** ~200 строк

**Удалить:**
- Phase 2 логику (SectionBuilder)
- Block-based логику (BlockPacker)
- Сложную обработку header_path

**Оставить:**
- Разбиение по заголовкам
- Простой header_path

```python
# markdown_chunker/strategies/structural.py

class StructuralStrategy(BaseStrategy):
    """Стратегия для структурированных документов."""
    
    @property
    def name(self) -> str:
        return "structural"
    
    @property
    def priority(self) -> int:
        return 2
    
    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        return (
            analysis.header_count >= config.structure_threshold and
            analysis.max_header_depth > 1
        )
    
    def apply(self, md_text: str, analysis: ContentAnalysis, config: ChunkConfig) -> List[Chunk]:
        chunks = []
        
        # 1. Разбить по заголовкам
        sections = self._split_by_headers(md_text, analysis.headers)
        
        # 2. Обработать секции
        header_path = []
        for section in sections:
            header_path = self._update_path(header_path, section)
            chunks.extend(self._process_section(section, header_path, config))
        
        return chunks
```

### 3.4 Создать FallbackStrategy (0.5 дня)

**Бывшая:** SentencesStrategy
**Изменения:** Только переименование и упрощение

```python
# markdown_chunker/strategies/fallback.py

class FallbackStrategy(BaseStrategy):
    """Универсальная fallback-стратегия."""
    
    @property
    def name(self) -> str:
        return "fallback"
    
    @property
    def priority(self) -> int:
        return 3
    
    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        return True  # Всегда может обработать
    
    def apply(self, md_text: str, analysis: ContentAnalysis, config: ChunkConfig) -> List[Chunk]:
        # Разбить по параграфам, группировать до max_size
        # ...
```

### 3.5 Удалить ListStrategy (0.5 дня)

**Причина:** Исключена из auto-mode, не используется

**Шаги:**
1. Удалить `list_strategy.py`
2. Удалить из `__init__.py`
3. Удалить тесты
4. Удалить параметры конфигурации (`list_count_threshold`, `list_ratio_threshold`)

### 3.6 Создать StrategySelector (0.5 дня)

```python
# markdown_chunker/strategies/__init__.py

class StrategySelector:
    """Выбор стратегии."""
    
    def __init__(self):
        self.strategies = [
            CodeAwareStrategy(),
            StructuralStrategy(),
            FallbackStrategy(),
        ]
    
    def select(self, analysis: ContentAnalysis, config: ChunkConfig) -> BaseStrategy:
        for strategy in self.strategies:
            if strategy.can_handle(analysis, config):
                return strategy
        return self.strategies[-1]  # Fallback
```

## Критерии завершения

- [ ] CodeAwareStrategy создана и работает
- [ ] StructuralStrategy упрощена до ~200 строк
- [ ] FallbackStrategy создана
- [ ] ListStrategy удалена
- [ ] StrategySelector создан
- [ ] Все property-based тесты проходят

## Риски

| Риск | Вероятность | Митигация |
|------|-------------|-----------|
| Потеря edge cases из старых стратегий | Средняя | Сравнение на реальных документах |
| Регрессия в обработке кода | Средняя | Property-based тесты |

## Результат

После завершения фазы 3:
- 3 стратегии вместо 6
- ~500 строк вместо ~5000
- Простая логика выбора стратегии
