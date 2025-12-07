# Feature 08: LlamaIndex Adapter

## Краткое описание

Официальный адаптер для интеграции markdown_chunker_v2 с LlamaIndex — вторым по популярности фреймворком для RAG.

---

## Метаданные

| Параметр | Значение |
|----------|----------|
| **Фаза** | 3 — Интеграция и Adoption |
| **Приоритет** | HIGH |
| **Effort** | 3-5 дней |
| **Impact** | High |
| **Уникальность** | No |

---

## Проблема

### Текущее состояние

- Нет официальной интеграции с LlamaIndex
- LlamaIndex имеет специфичный API (NodeParser, TextNode)
- Поддержка hierarchical relationships требует дополнительной работы

### LlamaIndex экосистема

- 30K+ GitHub stars
- Фокус на structured data и hierarchical indexing
- Популярен для enterprise RAG

---

## Решение

### Package Structure

```
llama-index-markdown-chunker/
├── llama_index_markdown_chunker/
│   ├── __init__.py
│   └── node_parser.py
├── tests/
│   └── test_node_parser.py
├── pyproject.toml
├── README.md
└── LICENSE
```

### NodeParser Implementation

```python
from typing import Any, List, Optional, Sequence
from llama_index.core.node_parser import NodeParser
from llama_index.core.schema import (
    BaseNode, 
    Document, 
    TextNode,
    NodeRelationship,
    RelatedNodeInfo
)
from markdown_chunker import MarkdownChunker, ChunkConfig

class MarkdownChunkerNodeParser(NodeParser):
    """
    LlamaIndex NodeParser adapter for markdown_chunker_v2.
    
    Provides intelligent, structure-aware markdown chunking
    with hierarchical node relationships.
    
    Example:
        >>> from llama_index_markdown_chunker import MarkdownChunkerNodeParser
        >>> parser = MarkdownChunkerNodeParser(
        ...     max_chunk_size=1500,
        ...     include_hierarchy=True
        ... )
        >>> nodes = parser.get_nodes_from_documents(documents)
    """
    
    max_chunk_size: int = 2000
    min_chunk_size: int = 200
    overlap_size: int = 100
    include_hierarchy: bool = True
    preserve_code_blocks: bool = True
    
    def __init__(
        self,
        max_chunk_size: int = 2000,
        min_chunk_size: int = 200,
        overlap_size: int = 100,
        include_hierarchy: bool = True,
        preserve_code_blocks: bool = True,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.overlap_size = overlap_size
        self.include_hierarchy = include_hierarchy
        self.preserve_code_blocks = preserve_code_blocks
        
        self.config = ChunkConfig(
            max_chunk_size=max_chunk_size,
            min_chunk_size=min_chunk_size,
            overlap_size=overlap_size,
            preserve_code_blocks=preserve_code_blocks,
        )
        self.chunker = MarkdownChunker(self.config)
    
    def _parse_nodes(
        self,
        nodes: Sequence[BaseNode],
        show_progress: bool = False,
        **kwargs: Any
    ) -> List[BaseNode]:
        """Parse nodes into smaller chunks."""
        all_nodes = []
        
        for node in nodes:
            if isinstance(node, TextNode):
                parsed_nodes = self._parse_single_node(node)
                all_nodes.extend(parsed_nodes)
            else:
                all_nodes.append(node)
        
        return all_nodes
    
    def _parse_single_node(self, node: TextNode) -> List[TextNode]:
        """Parse a single node into chunks."""
        result = self.chunker.chunk(node.text)
        
        parsed_nodes = []
        prev_node = None
        
        for i, chunk in enumerate(result.chunks):
            # Create new node
            new_node = TextNode(
                text=chunk.content,
                metadata={
                    **node.metadata,
                    "chunk_index": i,
                    "total_chunks": len(result.chunks),
                    "strategy_used": result.strategy_used,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "header_path": chunk.header_path,
                    "content_type": chunk.metadata.get("content_type"),
                },
            )
            
            # Set relationships
            relationships = {}
            
            # Source relationship
            relationships[NodeRelationship.SOURCE] = RelatedNodeInfo(
                node_id=node.node_id,
                metadata={"original_text_length": len(node.text)}
            )
            
            # Previous/Next relationships
            if prev_node:
                relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(
                    node_id=prev_node.node_id
                )
                prev_node.relationships[NodeRelationship.NEXT] = RelatedNodeInfo(
                    node_id=new_node.node_id
                )
            
            new_node.relationships = relationships
            parsed_nodes.append(new_node)
            prev_node = new_node
        
        # Add parent/child relationships if hierarchy enabled
        if self.include_hierarchy:
            self._add_hierarchy_relationships(parsed_nodes, result)
        
        return parsed_nodes
    
    def _add_hierarchy_relationships(
        self,
        nodes: List[TextNode],
        result: ChunkingResult
    ) -> None:
        """Add parent/child relationships based on header hierarchy."""
        # Build hierarchy from header_path
        hierarchy = {}
        
        for node in nodes:
            header_path = node.metadata.get("header_path", "")
            if header_path:
                parts = header_path.split(" > ")
                for i, part in enumerate(parts[:-1]):
                    parent_path = " > ".join(parts[:i+1])
                    child_path = " > ".join(parts[:i+2])
                    
                    if parent_path not in hierarchy:
                        hierarchy[parent_path] = []
                    if child_path not in hierarchy[parent_path]:
                        hierarchy[parent_path].append(child_path)
        
        # Apply relationships
        for node in nodes:
            header_path = node.metadata.get("header_path", "")
            if header_path:
                parts = header_path.split(" > ")
                if len(parts) > 1:
                    parent_path = " > ".join(parts[:-1])
                    # Find parent node
                    for other_node in nodes:
                        if other_node.metadata.get("header_path") == parent_path:
                            node.relationships[NodeRelationship.PARENT] = RelatedNodeInfo(
                                node_id=other_node.node_id
                            )
                            break
```

---

## Usage Examples

### Basic Usage

```python
from llama_index.core import VectorStoreIndex
from llama_index.core.readers import SimpleDirectoryReader
from llama_index_markdown_chunker import MarkdownChunkerNodeParser

# Load documents
documents = SimpleDirectoryReader("docs/").load_data()

# Create node parser
node_parser = MarkdownChunkerNodeParser(
    max_chunk_size=1500,
    include_hierarchy=True
)

# Parse into nodes
nodes = node_parser.get_nodes_from_documents(documents)

# Create index
index = VectorStoreIndex(nodes)
```

### With Query Engine

```python
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI

# Configure LLM
Settings.llm = OpenAI(model="gpt-4")

# Create query engine
query_engine = index.as_query_engine()

# Query
response = query_engine.query("How does authentication work?")
print(response)
```

### Hierarchical Retrieval

```python
from llama_index.core.retrievers import RecursiveRetriever

# Use hierarchical relationships for better retrieval
retriever = RecursiveRetriever(
    "root",
    retriever_dict={"root": index.as_retriever()},
    node_dict={node.node_id: node for node in nodes},
)

# Retrieval includes parent/child context
nodes = retriever.retrieve("API authentication")
```

---

## Package Configuration

### pyproject.toml

```toml
[project]
name = "llama-index-markdown-chunker"
version = "0.1.0"
description = "LlamaIndex adapter for markdown_chunker_v2"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
dependencies = [
    "llama-index-core>=0.10.0",
    "markdown-chunker>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]
```

---

## Тестирование

### Unit Tests

```python
def test_parse_nodes():
    """Nodes парсятся корректно"""
    parser = MarkdownChunkerNodeParser()
    doc = Document(text="# Header\n\nParagraph\n\n## Section\n\nMore text")
    nodes = parser.get_nodes_from_documents([doc])
    
    assert len(nodes) >= 1
    assert all(isinstance(n, TextNode) for n in nodes)

def test_relationships():
    """PREVIOUS/NEXT relationships создаются"""
    parser = MarkdownChunkerNodeParser()
    doc = Document(text="# Header\n\n" + "Paragraph. " * 500)
    nodes = parser.get_nodes_from_documents([doc])
    
    if len(nodes) > 1:
        assert NodeRelationship.NEXT in nodes[0].relationships
        assert NodeRelationship.PREVIOUS in nodes[1].relationships

def test_hierarchy_relationships():
    """PARENT/CHILD relationships создаются при include_hierarchy=True"""
    
def test_metadata_enrichment():
    """Metadata обогащается chunk information"""
```

---

## Ожидаемые результаты

### Adoption Metrics

| Метрика | Цель (6 месяцев) |
|---------|------------------|
| PyPI downloads/month | 500+ |
| GitHub stars | 30+ |

### User Benefits

1. **Hierarchical retrieval** — parent/child relationships
2. **Rich metadata** — header_path, content_type
3. **Standard LlamaIndex API**

---

## Риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| LlamaIndex API changes | High | Medium | Pin versions, monitor |
| Complex relationships | Medium | Low | Fallback to flat |

---

## Acceptance Criteria

- [ ] Package опубликован в PyPI
- [ ] NodeParser interface реализован
- [ ] PREVIOUS/NEXT relationships работают
- [ ] PARENT/CHILD relationships работают (optional)
- [ ] SOURCE relationship сохраняется
- [ ] Metadata enrichment работает
- [ ] Integration с VectorStoreIndex протестирована
- [ ] README с примерами

---

## Примеры из тестового корпуса

В ТЕСТОВОМ КОРПУСЕ ПРИМЕРОВ СЕЙЧАС НЕТ.

Эта фича является интеграционной и не требует специфических тестовых файлов в корпусе. Для тестирования иерархических связей рекомендуются файлы с глубокой иерархией заголовков из `tests/corpus/github_readmes/`.
