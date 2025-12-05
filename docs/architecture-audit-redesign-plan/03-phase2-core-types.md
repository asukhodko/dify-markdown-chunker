# План Редизайна: Фаза 2 — Типы и Парсер

## Цель

Упростить типы данных и парсер, удалить дублирование.

## Длительность: 4-5 дней

## Задачи

### 2.1 Объединить types.py (1 день)

**Текущее состояние:**
- `parser/types.py` — 931 строка
- `chunker/types.py` — 1079 строк
- Дублирование: Position, ContentAnalysis частично

**Целевое состояние:**
- `types.py` — ~400 строк

**Шаги:**
1. Создать `markdown_chunker/types.py`
2. Перенести `Chunk`, `ChunkingResult` из `chunker/types.py`
3. Перенести `ContentAnalysis`, `FencedBlock` из `parser/types.py`
4. Удалить дублирующие определения
5. Обновить импорты во всех файлах

```python
# markdown_chunker/types.py

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Chunk:
    """Чанк документа."""
    content: str
    start_line: int
    end_line: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # ... методы


@dataclass
class ChunkingResult:
    """Результат чанкинга."""
    chunks: List[Chunk]
    strategy_used: str
    processing_time: float
    # ... остальные поля


@dataclass
class ContentAnalysis:
    """Анализ контента документа."""
    total_chars: int
    total_lines: int
    code_ratio: float
    code_block_count: int
    header_count: int
    max_header_depth: int
    table_count: int
    # ... остальные поля
```

### 2.2 Упростить ChunkConfig (1 день)

**Текущее состояние:**
- 32 параметра
- 6 параметров для багфиксов (MC-001 через MC-006)
- 3 неиспользуемых параметра (streaming, fallback_strategy)

**Целевое состояние:**
- 8 параметров

**Шаги:**
1. Создать `markdown_chunker/config.py`
2. Оставить только необходимые параметры
3. Удалить MC-* параметры (сделать поведение по умолчанию)
4. Удалить неиспользуемые параметры

```python
# markdown_chunker/config.py

from dataclasses import dataclass


@dataclass
class ChunkConfig:
    """Конфигурация чанкинга."""
    
    # Размеры
    max_chunk_size: int = 4096
    min_chunk_size: int = 512
    overlap_size: int = 200  # 0 = disabled
    
    # Поведение
    preserve_atomic_blocks: bool = True
    extract_preamble: bool = True
    
    # Пороги стратегий
    code_threshold: float = 0.3
    structure_threshold: int = 3
    
    def __post_init__(self):
        """Валидация."""
        if self.max_chunk_size <= 0:
            raise ValueError("max_chunk_size must be positive")
        if self.min_chunk_size <= 0:
            raise ValueError("min_chunk_size must be positive")
        if self.min_chunk_size > self.max_chunk_size:
            self.min_chunk_size = self.max_chunk_size // 2
```

### 2.3 Упростить парсер (2-3 дня)

**Текущее состояние:**
- 15 файлов в `parser/`
- 50+ экспортов в `__init__.py`
- Deprecated Simple API
- Backward compatibility код

**Целевое состояние:**
- 1 файл `parser.py` (~500 строк)
- 5-10 экспортов
- Line ending normalization в начале

**Шаги:**
1. Создать `markdown_chunker/parser.py`
2. **Добавить `_normalize_line_endings()` в начало `parse()`** (FINDING-EDGE-2 fix)
3. Перенести основную логику из `parser/core.py`
4. Упростить `ContentAnalysis` — только нужные поля
5. Удалить deprecated Simple API
6. Удалить backward compatibility

**Line Ending Normalization:**
```python
def _normalize_line_endings(self, text: str) -> str:
    """Нормализация line endings к Unix-стилю."""
    return text.replace('\r\n', '\n').replace('\r', '\n')

def parse(self, md_text: str) -> ContentAnalysis:
    # Нормализация в начале pipeline
    md_text = self._normalize_line_endings(md_text)
    # ... остальная логика
```

```python
# markdown_chunker/parser.py

"""
Парсер markdown-документов.

Упрощённая версия — только необходимая функциональность.
"""

import re
from typing import List, Optional
from .types import ContentAnalysis, FencedBlock


class Parser:
    """
    Парсер markdown-документов.
    
    Извлекает:
    - Code blocks (fenced)
    - Заголовки
    - Таблицы
    - Метрики контента
    """
    
    def analyze(self, md_text: str) -> ContentAnalysis:
        """Проанализировать документ."""
        code_blocks = self._extract_code_blocks(md_text)
        headers = self._extract_headers(md_text)
        tables = self._extract_tables(md_text)
        
        # Вычислить метрики
        total_chars = len(md_text)
        total_lines = md_text.count('\n') + 1
        code_chars = sum(len(b.content) for b in code_blocks)
        code_ratio = code_chars / total_chars if total_chars > 0 else 0
        
        return ContentAnalysis(
            total_chars=total_chars,
            total_lines=total_lines,
            code_ratio=code_ratio,
            code_block_count=len(code_blocks),
            header_count=len(headers),
            max_header_depth=max((h['level'] for h in headers), default=0),
            table_count=len(tables),
            code_blocks=code_blocks,
            headers=headers,
            tables=tables,
        )
    
    def _extract_code_blocks(self, md_text: str) -> List[FencedBlock]:
        """Извлечь code blocks."""
        pattern = re.compile(r'^(`{3,})(\w*)\n(.*?)\n\1', re.MULTILINE | re.DOTALL)
        blocks = []
        
        for match in pattern.finditer(md_text):
            blocks.append(FencedBlock(
                language=match.group(2) or None,
                content=match.group(3),
                start_pos=match.start(),
                end_pos=match.end(),
            ))
        
        return blocks
    
    def _extract_headers(self, md_text: str) -> List[dict]:
        """Извлечь заголовки."""
        pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        headers = []
        
        for match in pattern.finditer(md_text):
            headers.append({
                'level': len(match.group(1)),
                'text': match.group(2),
                'pos': match.start(),
            })
        
        return headers
    
    def _extract_tables(self, md_text: str) -> List[dict]:
        """Извлечь таблицы."""
        # Простая эвристика: строки с | и ---
        tables = []
        lines = md_text.split('\n')
        
        i = 0
        while i < len(lines):
            if '|' in lines[i] and i + 1 < len(lines) and '---' in lines[i + 1]:
                # Найдена таблица
                start = i
                while i < len(lines) and '|' in lines[i]:
                    i += 1
                tables.append({
                    'start_line': start,
                    'end_line': i - 1,
                })
            else:
                i += 1
        
        return tables
```

## Критерии завершения

- [ ] `types.py` создан и содержит все типы
- [ ] `config.py` создан с 8 параметрами
- [ ] `parser.py` создан и работает
- [ ] Все property-based тесты проходят
- [ ] Старые файлы помечены как deprecated

## Риски

| Риск | Вероятность | Митигация |
|------|-------------|-----------|
| Сломаны импорты | Высокая | Постепенная миграция, алиасы |
| Потеря функциональности парсера | Средняя | Сравнение результатов |

## Результат

После завершения фазы 2:
- Типы консолидированы в одном файле
- Конфигурация упрощена до 8 параметров
- Парсер упрощён до ~500 строк
