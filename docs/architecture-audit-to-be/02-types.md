# Целевая Архитектура: Типы Данных

## Обзор

Все типы данных в одном файле `types.py` (~300 строк).

## Chunk

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class Chunk:
    """
    Единица результата чанкинга.
    
    Инварианты:
    - start_line >= 1 (1-based)
    - end_line >= start_line
    - content.strip() != "" (не пустой)
    """
    content: str
    start_line: int
    end_line: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.start_line < 1:
            raise ValueError("start_line must be >= 1")
        if self.end_line < self.start_line:
            raise ValueError("end_line must be >= start_line")
        if not self.content.strip():
            raise ValueError("content cannot be empty")
    
    @property
    def size(self) -> int:
        """Размер в символах."""
        return len(self.content)
    
    @property
    def line_count(self) -> int:
        """Количество строк."""
        return self.end_line - self.start_line + 1
    
    @property
    def is_oversize(self) -> bool:
        """Помечен ли как oversize."""
        return self.metadata.get("allow_oversize", False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация в dict."""
        return {
            "content": self.content,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "size": self.size,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Chunk":
        """Десериализация из dict."""
        return cls(
            content=data["content"],
            start_line=data["start_line"],
            end_line=data["end_line"],
            metadata=data.get("metadata", {}),
        )
```

## ChunkingResult

```python
@dataclass
class ChunkingResult:
    """
    Результат операции чанкинга.
    
    Содержит чанки и метаданные о процессе.
    """
    chunks: List[Chunk]
    strategy_used: str
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        """Успешно ли завершился чанкинг."""
        return len(self.chunks) > 0 or len(self.errors) == 0
    
    @property
    def total_chunks(self) -> int:
        return len(self.chunks)
    
    @property
    def total_size(self) -> int:
        return sum(c.size for c in self.chunks)
    
    @property
    def average_size(self) -> float:
        if not self.chunks:
            return 0.0
        return self.total_size / len(self.chunks)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunks": [c.to_dict() for c in self.chunks],
            "strategy_used": self.strategy_used,
            "processing_time": self.processing_time,
            "errors": self.errors,
            "warnings": self.warnings,
            "statistics": {
                "total_chunks": self.total_chunks,
                "total_size": self.total_size,
                "average_size": self.average_size,
            },
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChunkingResult":
        return cls(
            chunks=[Chunk.from_dict(c) for c in data["chunks"]],
            strategy_used=data["strategy_used"],
            processing_time=data.get("processing_time", 0.0),
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
        )
```

## ContentAnalysis

```python
@dataclass
class ContentAnalysis:
    """
    Результат анализа markdown документа.
    
    Используется для выбора стратегии.
    """
    total_chars: int
    total_lines: int
    
    # Соотношения типов контента
    code_ratio: float = 0.0      # Доля кода (0.0-1.0)
    text_ratio: float = 1.0      # Доля текста
    
    # Счётчики элементов
    code_block_count: int = 0
    header_count: int = 0
    table_count: int = 0
    list_count: int = 0
    
    # Структура
    max_header_depth: int = 0    # Максимальная глубина заголовков (1-6)
    
    # Извлечённые элементы (для стратегий)
    code_blocks: List[Dict[str, Any]] = field(default_factory=list)
    headers: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def is_code_heavy(self) -> bool:
        """Документ с преобладанием кода."""
        return self.code_ratio >= 0.3 and self.code_block_count >= 1
    
    @property
    def is_structured(self) -> bool:
        """Документ с иерархией заголовков."""
        return self.header_count >= 3 and self.max_header_depth > 1
    
    @property
    def content_type(self) -> str:
        """Определение типа контента."""
        if self.is_code_heavy:
            return "code"
        if self.is_structured:
            return "structured"
        return "text"
```

## CodeBlock

```python
@dataclass
class CodeBlock:
    """
    Извлечённый блок кода.
    """
    content: str           # Содержимое без маркеров ```
    language: str = ""     # Язык программирования
    start_line: int = 0    # Начальная строка (включая ```)
    end_line: int = 0      # Конечная строка (включая ```)
    
    @property
    def full_content(self) -> str:
        """Полное содержимое с маркерами."""
        return f"```{self.language}\n{self.content}\n```"
    
    @property
    def size(self) -> int:
        return len(self.full_content)
```

## Header

```python
@dataclass
class Header:
    """
    Извлечённый заголовок.
    """
    text: str              # Текст заголовка
    level: int             # Уровень (1-6)
    line: int              # Номер строки
    
    @property
    def markdown(self) -> str:
        """Markdown представление."""
        return "#" * self.level + " " + self.text
```

## Table

```python
@dataclass
class Table:
    """
    Извлечённая таблица.
    """
    content: str           # Полное содержимое таблицы
    start_line: int
    end_line: int
    row_count: int = 0
    column_count: int = 0
    
    @property
    def size(self) -> int:
        return len(self.content)
```

## ValidationResult

```python
@dataclass
class ValidationResult:
    """
    Результат валидации чанков.
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def __bool__(self) -> bool:
        return self.is_valid
```

## Сравнение с текущей реализацией

| Аспект | Было | Стало |
|--------|------|-------|
| Файлов с типами | 2 | 1 |
| Строк кода | ~2000 | ~300 |
| Классов | 15+ | 7 |
| Полей в ChunkConfig | 32 | 8-10 |
| Методов в Chunk | 15+ | 6 |

## Принципы

1. **Минимализм** — только необходимые поля
2. **Иммутабельность** — dataclass frozen где возможно
3. **Валидация** — в `__post_init__`
4. **Сериализация** — `to_dict`/`from_dict` для JSON
