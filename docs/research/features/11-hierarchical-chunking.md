# Feature 11: Hierarchical Chunking

## Краткое описание

Создание иерархии чанков (parent-child) для многоуровневого retrieval. Поддержка Document → Section → Subsection → Paragraph levels.

---

## Метаданные

| Параметр | Значение |
|----------|----------|
| **Фаза** | 4 — Продвинутые возможности |
| **Приоритет** | MEDIUM |
| **Effort** | 7-10 дней |
| **Impact** | High |
| **Уникальность** | No (LlamaIndex имеет аналог) |

---

## Проблема

### Текущее состояние

- Flat chunk structure — все чанки на одном уровне
- Нет связей parent-child между чанками
- Retrieval возвращает только конкретный чанк

### Ограничения flat structure

1. **Потеря контекста:**
   - Чанк о деталях API не связан с overview секцией
   - Retrieval может вернуть детали без контекста

2. **Навигация:**
   - Невозможно "подняться" к parent секции
   - Невозможно "спуститься" к sub-секциям

3. **Multi-level retrieval:**
   - Для overview вопросов нужны высокоуровневые чанки
   - Для detail вопросов нужны детальные чанки

---

## Решение

### Архитектура

```python
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import uuid

class ChunkLevel(Enum):
    DOCUMENT = 0      # Весь документ / summary
    SECTION = 1       # H1 секции
    SUBSECTION = 2    # H2 секции
    PARAGRAPH = 3     # H3+ и параграфы

@dataclass
class HierarchicalChunk:
    """Чанк с иерархическими связями."""
    id: str
    content: str
    level: ChunkLevel
    
    # Иерархия
    parent_id: Optional[str] = None
    children_ids: list[str] = field(default_factory=list)
    
    # Sibling navigation
    prev_sibling_id: Optional[str] = None
    next_sibling_id: Optional[str] = None
    
    # Metadata
    header_path: str = ""
    start_line: int = 0
    end_line: int = 0
    summary: Optional[str] = None  # Для высокоуровневых чанков
    
    metadata: dict = field(default_factory=dict)
    
    @property
    def has_children(self) -> bool:
        return len(self.children_ids) > 0
    
    @property
    def is_leaf(self) -> bool:
        return not self.has_children
    
    @property
    def depth(self) -> int:
        return self.level.value

@dataclass
class HierarchicalChunkingResult:
    """Результат hierarchical chunking."""
    chunks: list[HierarchicalChunk]
    root_id: str  # ID document-level chunk
    strategy_used: str
    
    def get_chunk(self, chunk_id: str) -> Optional[HierarchicalChunk]:
        """Найти чанк по ID."""
        for chunk in self.chunks:
            if chunk.id == chunk_id:
                return chunk
        return None
    
    def get_children(self, chunk_id: str) -> list[HierarchicalChunk]:
        """Получить дочерние чанки."""
        chunk = self.get_chunk(chunk_id)
        if not chunk:
            return []
        return [self.get_chunk(cid) for cid in chunk.children_ids if self.get_chunk(cid)]
    
    def get_parent(self, chunk_id: str) -> Optional[HierarchicalChunk]:
        """Получить родительский чанк."""
        chunk = self.get_chunk(chunk_id)
        if not chunk or not chunk.parent_id:
            return None
        return self.get_chunk(chunk.parent_id)
    
    def get_ancestors(self, chunk_id: str) -> list[HierarchicalChunk]:
        """Получить всех предков (от parent до root)."""
        ancestors = []
        current = self.get_chunk(chunk_id)
        while current and current.parent_id:
            parent = self.get_chunk(current.parent_id)
            if parent:
                ancestors.append(parent)
            current = parent
        return ancestors
    
    def get_flat_chunks(self) -> list[HierarchicalChunk]:
        """Получить только leaf чанки для обычного retrieval."""
        return [c for c in self.chunks if c.is_leaf]
```

### Hierarchical Chunker

```python
class HierarchicalChunker:
    """
    Chunker с поддержкой иерархии.
    """
    
    def __init__(self, config: ChunkConfig):
        self.config = config
        self.base_chunker = MarkdownChunker(config)
    
    def chunk(
        self,
        text: str,
        include_summaries: bool = False
    ) -> HierarchicalChunkingResult:
        """
        Создать иерархическую структуру чанков.
        
        Args:
            text: Markdown text
            include_summaries: Генерировать summaries для section chunks
        """
        # 1. Parse document structure
        parsed = self.parser.parse(text)
        sections = self._extract_sections(parsed)
        
        # 2. Create document-level chunk
        doc_chunk = self._create_document_chunk(text, sections)
        all_chunks = [doc_chunk]
        
        # 3. Create section hierarchy
        section_chunks = self._create_section_chunks(
            sections, 
            doc_chunk.id,
            include_summaries
        )
        all_chunks.extend(section_chunks)
        
        # 4. Create paragraph-level chunks for each section
        for section_chunk in section_chunks:
            if section_chunk.level == ChunkLevel.SUBSECTION:
                para_chunks = self._create_paragraph_chunks(
                    section_chunk.content,
                    section_chunk.id
                )
                section_chunk.children_ids = [c.id for c in para_chunks]
                all_chunks.extend(para_chunks)
        
        # 5. Link siblings
        self._link_siblings(all_chunks)
        
        return HierarchicalChunkingResult(
            chunks=all_chunks,
            root_id=doc_chunk.id,
            strategy_used="hierarchical"
        )
    
    def _create_document_chunk(
        self,
        text: str,
        sections: list[Section]
    ) -> HierarchicalChunk:
        """Создать document-level chunk."""
        # Extract title and first paragraph as summary
        title = sections[0].header if sections else "Document"
        summary = self._generate_summary(text) if len(text) > 1000 else text[:500]
        
        return HierarchicalChunk(
            id=str(uuid.uuid4()),
            content=summary,
            level=ChunkLevel.DOCUMENT,
            header_path=title,
            summary=summary,
            children_ids=[],  # Will be populated later
            metadata={"full_text_length": len(text)}
        )
    
    def _create_section_chunks(
        self,
        sections: list[Section],
        parent_id: str,
        include_summaries: bool
    ) -> list[HierarchicalChunk]:
        """Создать чанки для секций."""
        chunks = []
        current_parent = parent_id
        
        for section in sections:
            level = self._header_level_to_chunk_level(section.level)
            
            chunk = HierarchicalChunk(
                id=str(uuid.uuid4()),
                content=section.content,
                level=level,
                parent_id=current_parent if level.value > 1 else parent_id,
                header_path=section.header_path,
                start_line=section.start_line,
                end_line=section.end_line,
            )
            
            if include_summaries and len(section.content) > 500:
                chunk.summary = self._generate_summary(section.content)
            
            chunks.append(chunk)
            
            # Update parent for children
            if level == ChunkLevel.SECTION:
                current_parent = chunk.id
        
        return chunks
    
    def _header_level_to_chunk_level(self, header_level: int) -> ChunkLevel:
        """Конвертировать header level в chunk level."""
        mapping = {
            1: ChunkLevel.SECTION,
            2: ChunkLevel.SUBSECTION,
        }
        return mapping.get(header_level, ChunkLevel.PARAGRAPH)
```

---

## Usage Examples

### Basic Usage

```python
from markdown_chunker import HierarchicalChunker, ChunkConfig

config = ChunkConfig(max_chunk_size=2000)
chunker = HierarchicalChunker(config)

result = chunker.chunk(markdown_text)

# Access root
root = result.get_chunk(result.root_id)
print(f"Document: {root.header_path}")

# Access sections
for child_id in root.children_ids:
    section = result.get_chunk(child_id)
    print(f"  Section: {section.header_path}")
```

### Multi-Level Retrieval

```python
def retrieve_with_context(query: str, result: HierarchicalChunkingResult):
    """Retrieval с иерархическим контекстом."""
    # 1. Find matching leaf chunks
    leaf_chunks = result.get_flat_chunks()
    matches = search(query, leaf_chunks)
    
    # 2. Add parent context
    for match in matches:
        ancestors = result.get_ancestors(match.id)
        match.context = " > ".join([a.header_path for a in reversed(ancestors)])
    
    return matches
```

### Hierarchical Summarization

```python
def hierarchical_summary(result: HierarchicalChunkingResult):
    """Создать иерархическое summary."""
    root = result.get_chunk(result.root_id)
    
    summary = f"# {root.header_path}\n\n"
    summary += f"{root.summary}\n\n"
    
    for section_id in root.children_ids:
        section = result.get_chunk(section_id)
        summary += f"## {section.header_path}\n"
        if section.summary:
            summary += f"{section.summary}\n\n"
    
    return summary
```

---

## Тестирование

### Unit Tests

```python
def test_creates_hierarchy():
    """Иерархия создаётся корректно"""
    text = "# Doc\n\n## Section 1\n\nText\n\n## Section 2\n\nMore text"
    result = chunker.chunk(text)
    
    root = result.get_chunk(result.root_id)
    assert root.level == ChunkLevel.DOCUMENT
    assert len(root.children_ids) >= 2

def test_parent_child_links():
    """Parent-child связи корректны"""
    result = chunker.chunk(text)
    for chunk in result.chunks:
        if chunk.parent_id:
            parent = result.get_chunk(chunk.parent_id)
            assert chunk.id in parent.children_ids

def test_get_ancestors():
    """get_ancestors возвращает путь до root"""
    
def test_sibling_links():
    """Sibling links корректны"""
    
def test_flat_chunks():
    """get_flat_chunks возвращает только листья"""
```

---

## Ожидаемые улучшения

### Use Cases

| Use Case | Без иерархии | С иерархией |
|----------|--------------|-------------|
| Overview вопросы | Возвращает детали | Возвращает section summary |
| Detail вопросы | OK | OK + context from parent |
| Navigation | Нет | Parent/child/sibling links |
| Summarization | Плоский список | Иерархическое summary |

---

## Зависимости

### Изменяет

- Новый `HierarchicalChunker` class
- Новый `HierarchicalChunk` type
- Новый `HierarchicalChunkingResult` type

### Совместимость

- Стандартный `MarkdownChunker` остаётся для flat chunking
- `HierarchicalChunker` — отдельный класс

---

## Риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Complexity | High | Medium | Clear documentation |
| Storage overhead | Medium | Low | Optional feature |
| Integration complexity | Medium | Medium | Adapters for frameworks |

---

## Acceptance Criteria

- [ ] Document-level chunk создаётся
- [ ] Section chunks создаются из H1/H2
- [ ] Parent-child relationships корректны
- [ ] Sibling relationships корректны
- [ ] get_ancestors() работает
- [ ] get_flat_chunks() для compatibility
- [ ] Summary generation (optional)
- [ ] Integration с LlamaIndex adapter
- [ ] Документация с примерами

---

## Примеры из тестового корпуса

Следующие файлы с глубокой иерархией заголовков подходят для тестирования Hierarchical Chunking:

### Файлы с большим количеством заголовков (>30)

| Файл | Headers | Строк | Описание |
|------|---------|-------|----------|
| [youtube-dl.md](../../../tests/corpus/github_readmes/python/youtube-dl.md) | 123 | 1581 | Огромная иерархия |
| [axios.md](../../../tests/corpus/github_readmes/javascript/axios.md) | 85 | 1802 | Глубокая структура |
| [docker_005.md](../../../tests/corpus/technical_docs/docker/docker_005.md) | 53 | 348 | Docker документация |
| [pytorch.md](../../../tests/corpus/github_readmes/python/pytorch.md) | 47 | 575 | PyTorch иерархия |
| [changelogs_005.md](../../../tests/corpus/changelogs/changelogs_005.md) | 45 | 256 | Changelog с версиями |
| [changelogs_010.md](../../../tests/corpus/changelogs/changelogs_010.md) | 44 | 253 | Changelog |
| [changelogs_034.md](../../../tests/corpus/changelogs/changelogs_034.md) | 44 | 252 | Changelog |
| [face_recognition.md](../../../tests/corpus/github_readmes/python/face_recognition.md) | 43 | 416 | face_recognition README |

### Файлы со средней иерархией (15-30 headers)

| Файл | Headers | Строк | Описание |
|------|---------|-------|----------|
| [webpack.md](../../../tests/corpus/github_readmes/javascript/webpack.md) | 34 | 662 | Webpack README |
| [go_007.md](../../../tests/corpus/github_readmes/go/go_007.md) | 31 | 182 | Go README |
| [changelogs_003.md](../../../tests/corpus/changelogs/changelogs_003.md) | 28 | 154 | Changelog |
| [fastapi.md](../../../tests/corpus/github_readmes/python/fastapi.md) | 27 | 563 | FastAPI README |
| [engineering_blogs_026.md](../../../tests/corpus/engineering_blogs/engineering_blogs_026.md) | 27 | 191 | Технический блог |
| [eslint.md](../../../tests/corpus/github_readmes/javascript/eslint.md) | 26 | 355 | ESLint README |

### Компактные файлы с иерархией

| Файл | Headers | Строк | Описание |
|------|---------|-------|----------|
| [research_notes_007.md](../../../tests/corpus/research_notes/research_notes_007.md) | 18 | 97 | Заметки со структурой |
| [mixed_content_005.md](../../../tests/corpus/mixed_content/mixed_content_005.md) | 14 | 95 | Mixed content |
