# Integration Analysis

## Executive Summary

Анализ требований интеграции с популярными RAG-платформами и форматами экспорта. Определены необходимые адаптеры и форматы для seamless интеграции.

**Ключевые findings:**
- Текущий формат Chunk совместим с большинством платформ
- Требуются минимальные адаптеры для LangChain и LlamaIndex
- Dify интеграция уже работает (основной use case)
- JSON/JSONL экспорт покрывает большинство потребностей

## Platform Requirements

### 1. Dify

**Current Status:** ✅ Fully Compatible

**Integration Point:** Custom tool/plugin

**Required Format:**
```python
{
    "content": str,           # Chunk text
    "metadata": {
        "source": str,        # File path
        "chunk_index": int,   # Sequential index
        "total_chunks": int,  # Total count
        # Optional
        "start_line": int,
        "end_line": int,
        "content_type": str,
    }
}
```

**Current Compatibility:**
| Field | Status | Notes |
|-------|--------|-------|
| content | ✅ | Direct mapping |
| source | ⚠️ | Need to add to metadata |
| chunk_index | ✅ | Already present |
| total_chunks | ⚠️ | Need to add |
| start_line | ✅ | Already present |
| end_line | ✅ | Already present |
| content_type | ✅ | Already present |

**Required Changes:**
```python
def to_dify_format(chunks: list[Chunk], source: str) -> list[dict]:
    """Convert chunks to Dify format."""
    total = len(chunks)
    return [
        {
            "content": chunk.content,
            "metadata": {
                "source": source,
                "chunk_index": i,
                "total_chunks": total,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "content_type": chunk.metadata.get("content_type", "text"),
            }
        }
        for i, chunk in enumerate(chunks)
    ]
```

**Effort:** Small (S)

---

### 2. LangChain

**Current Status:** ⚠️ Needs Adapter

**Integration Point:** Custom TextSplitter or Document loader

**Required Format:**
```python
from langchain.schema import Document

Document(
    page_content=str,         # Chunk text
    metadata={
        "source": str,        # File path
        "chunk_id": str,      # Unique ID
        # Optional
        "start_index": int,
        "end_index": int,
    }
)
```

**Adapter Implementation:**
```python
from langchain.schema import Document
from langchain.text_splitter import TextSplitter
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig

class MarkdownChunkerSplitter(TextSplitter):
    """LangChain adapter for markdown_chunker_v2."""
    
    def __init__(self, config: ChunkConfig = None, **kwargs):
        super().__init__(**kwargs)
        self._chunker = MarkdownChunker(config)
    
    def split_text(self, text: str) -> list[str]:
        """Split text into chunks."""
        chunks = self._chunker.chunk(text)
        return [chunk.content for chunk in chunks]
    
    def split_documents(self, documents: list[Document]) -> list[Document]:
        """Split documents into chunks."""
        result = []
        for doc in documents:
            chunks = self._chunker.chunk(doc.page_content)
            for i, chunk in enumerate(chunks):
                result.append(Document(
                    page_content=chunk.content,
                    metadata={
                        **doc.metadata,
                        "chunk_id": f"{doc.metadata.get('source', 'unknown')}_{i}",
                        "chunk_index": i,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "content_type": chunk.metadata.get("content_type"),
                        "header_path": chunk.metadata.get("header_path", []),
                    }
                ))
        return result

# Usage
from langchain.document_loaders import TextLoader

loader = TextLoader("document.md")
documents = loader.load()

splitter = MarkdownChunkerSplitter(
    config=ChunkConfig(max_chunk_size=1500)
)
chunks = splitter.split_documents(documents)
```

**Effort:** Small (S)

---

### 3. LlamaIndex

**Current Status:** ⚠️ Needs Adapter

**Integration Point:** Custom NodeParser

**Required Format:**
```python
from llama_index.core.schema import TextNode, NodeRelationship

TextNode(
    text=str,                 # Chunk text
    id_=str,                  # Unique ID
    metadata={},              # Custom metadata
    relationships={           # Node relationships
        NodeRelationship.PARENT: ...,
        NodeRelationship.PREVIOUS: ...,
        NodeRelationship.NEXT: ...,
    }
)
```

**Adapter Implementation:**
```python
from llama_index.core.node_parser import NodeParser
from llama_index.core.schema import TextNode, NodeRelationship, RelatedNodeInfo
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig

class MarkdownChunkerNodeParser(NodeParser):
    """LlamaIndex adapter for markdown_chunker_v2."""
    
    def __init__(self, config: ChunkConfig = None):
        self._chunker = MarkdownChunker(config)
    
    def _parse_nodes(self, documents, show_progress=False):
        """Parse documents into nodes."""
        all_nodes = []
        
        for doc in documents:
            chunks = self._chunker.chunk(doc.text)
            nodes = []
            
            for i, chunk in enumerate(chunks):
                node_id = f"{doc.id_}_{i}"
                node = TextNode(
                    text=chunk.content,
                    id_=node_id,
                    metadata={
                        "source": doc.metadata.get("source"),
                        "chunk_index": i,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "content_type": chunk.metadata.get("content_type"),
                        "header_path": chunk.metadata.get("header_path", []),
                    }
                )
                nodes.append(node)
            
            # Add relationships
            for i, node in enumerate(nodes):
                if i > 0:
                    node.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(
                        node_id=nodes[i-1].id_
                    )
                if i < len(nodes) - 1:
                    node.relationships[NodeRelationship.NEXT] = RelatedNodeInfo(
                        node_id=nodes[i+1].id_
                    )
            
            all_nodes.extend(nodes)
        
        return all_nodes

# Usage
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("./docs").load_data()
parser = MarkdownChunkerNodeParser(
    config=ChunkConfig(max_chunk_size=1500)
)
nodes = parser.get_nodes_from_documents(documents)
```

**Effort:** Medium (M)

---

### 4. Haystack

**Current Status:** ⚠️ Needs Adapter

**Integration Point:** Custom DocumentSplitter

**Required Format:**
```python
from haystack import Document

Document(
    content=str,              # Chunk text
    meta={                    # Metadata
        "source": str,
        "split_id": int,
    }
)
```

**Adapter Implementation:**
```python
from haystack import Document
from haystack.components.preprocessors import DocumentSplitter
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig

class MarkdownChunkerSplitter:
    """Haystack adapter for markdown_chunker_v2."""
    
    def __init__(self, config: ChunkConfig = None):
        self._chunker = MarkdownChunker(config)
    
    def run(self, documents: list[Document]) -> dict:
        """Split documents."""
        result = []
        
        for doc in documents:
            chunks = self._chunker.chunk(doc.content)
            for i, chunk in enumerate(chunks):
                result.append(Document(
                    content=chunk.content,
                    meta={
                        **doc.meta,
                        "split_id": i,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "content_type": chunk.metadata.get("content_type"),
                    }
                ))
        
        return {"documents": result}
```

**Effort:** Small (S)

---

## Export Formats

### JSON

**Status:** ✅ Supported

```python
def export_json(chunks: list[Chunk], filepath: str):
    """Export chunks to JSON."""
    data = [
        {
            "content": chunk.content,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "size": chunk.size,
            "metadata": chunk.metadata,
        }
        for chunk in chunks
    ]
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
```

### JSONL (JSON Lines)

**Status:** ✅ Supported

```python
def export_jsonl(chunks: list[Chunk], filepath: str):
    """Export chunks to JSONL (one JSON object per line)."""
    with open(filepath, 'w') as f:
        for chunk in chunks:
            data = {
                "content": chunk.content,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "size": chunk.size,
                "metadata": chunk.metadata,
            }
            f.write(json.dumps(data) + '\n')
```

### Parquet

**Status:** ⚠️ Needs Implementation

```python
import pyarrow as pa
import pyarrow.parquet as pq

def export_parquet(chunks: list[Chunk], filepath: str):
    """Export chunks to Parquet format."""
    data = {
        "content": [c.content for c in chunks],
        "start_line": [c.start_line for c in chunks],
        "end_line": [c.end_line for c in chunks],
        "size": [c.size for c in chunks],
        "content_type": [c.metadata.get("content_type") for c in chunks],
        "has_code": [c.metadata.get("has_code") for c in chunks],
    }
    
    table = pa.table(data)
    pq.write_table(table, filepath)
```

**Effort:** Small (S) — requires pyarrow dependency

---

## Metadata Standards

### Recommended Metadata Schema

```python
@dataclass
class ChunkMetadata:
    # Required
    chunk_index: int          # Sequential index within document
    content_type: str         # text/code/table/mixed
    
    # Recommended
    source: str               # Source file path
    start_line: int           # Start line in source
    end_line: int             # End line in source
    header_path: list[str]    # Hierarchical header path
    
    # Optional
    has_code: bool            # Contains code blocks
    has_table: bool           # Contains tables
    language: str             # Primary code language (if applicable)
    strategy: str             # Strategy used for chunking
    
    # For overlap
    previous_content: str     # Overlap from previous chunk
    next_content: str         # Overlap from next chunk
    overlap_size: int         # Size of overlap
```

### Compatibility Matrix

| Field | Dify | LangChain | LlamaIndex | Haystack |
|-------|------|-----------|------------|----------|
| content | ✅ | ✅ | ✅ | ✅ |
| chunk_index | ✅ | ✅ | ✅ | ✅ |
| source | ✅ | ✅ | ✅ | ✅ |
| start_line | ✅ | ⚠️ | ✅ | ⚠️ |
| end_line | ✅ | ⚠️ | ✅ | ⚠️ |
| header_path | ⚠️ | ⚠️ | ✅ | ⚠️ |
| content_type | ✅ | ⚠️ | ✅ | ⚠️ |
| relationships | ❌ | ❌ | ✅ | ❌ |

**Legend:** ✅ Native support | ⚠️ Via custom metadata | ❌ Not supported

---

## API Requirements

### Real-time Chunking API

**Endpoint Design:**
```python
# FastAPI example
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChunkRequest(BaseModel):
    text: str
    config: dict = None

class ChunkResponse(BaseModel):
    chunks: list[dict]
    total_chunks: int
    strategy_used: str

@app.post("/chunk", response_model=ChunkResponse)
async def chunk_text(request: ChunkRequest):
    config = ChunkConfig(**request.config) if request.config else None
    chunker = MarkdownChunker(config)
    
    chunks, strategy, _ = chunker.chunk_with_analysis(request.text)
    
    return ChunkResponse(
        chunks=[
            {
                "content": c.content,
                "start_line": c.start_line,
                "end_line": c.end_line,
                "metadata": c.metadata,
            }
            for c in chunks
        ],
        total_chunks=len(chunks),
        strategy_used=strategy,
    )
```

**Performance Requirements:**
- Response time < 100ms for documents < 100KB
- Support for streaming responses for large documents
- Rate limiting for public API

---

## Recommendations

### Priority 1: Create Official Adapters

| Adapter | Effort | Impact | Priority |
|---------|--------|--------|----------|
| LangChain | S | High | HIGH |
| LlamaIndex | M | High | HIGH |
| Haystack | S | Medium | MEDIUM |

### Priority 2: Add Export Formats

| Format | Effort | Impact | Priority |
|--------|--------|--------|----------|
| JSONL | S | High | HIGH |
| Parquet | S | Medium | MEDIUM |

### Priority 3: Enhance Metadata

| Enhancement | Effort | Impact | Priority |
|-------------|--------|--------|----------|
| Add `source` field | S | High | HIGH |
| Add `total_chunks` | S | Medium | MEDIUM |
| Standardize schema | S | Medium | MEDIUM |

---

## Conclusion

markdown_chunker_v2 имеет хорошую базу для интеграции:
- Формат Chunk уже совместим с большинством платформ
- Требуются минимальные адаптеры (< 100 строк каждый)
- JSON/JSONL экспорт покрывает основные потребности

Рекомендуемые действия:
1. Создать официальные адаптеры для LangChain и LlamaIndex
2. Добавить JSONL экспорт
3. Стандартизировать metadata schema
4. Опубликовать интеграционную документацию
