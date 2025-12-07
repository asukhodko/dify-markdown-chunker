# Feature 07: LangChain Adapter

## Краткое описание

Официальный адаптер для интеграции markdown_chunker_v2 с LangChain — самым популярным фреймворком для RAG приложений.

---

## Метаданные

| Параметр | Значение |
|----------|----------|
| **Фаза** | 3 — Интеграция и Adoption |
| **Приоритет** | HIGH |
| **Effort** | 2-3 дня |
| **Impact** | High |
| **Уникальность** | No |

---

## Проблема

### Текущее состояние

- markdown_chunker_v2 не имеет официальной интеграции с LangChain
- Пользователи должны писать кастомный код для интеграции
- Это создаёт барьер для adoption

### LangChain экосистема

LangChain — де-факто стандарт для RAG:
- 75K+ GitHub stars
- Используется в production многими компаниями
- Имеет стандартизированные интерфейсы для text splitters

---

## Решение

### Package Structure

```
langchain-markdown-chunker/
├── langchain_markdown_chunker/
│   ├── __init__.py
│   ├── text_splitter.py
│   └── document_transformer.py
├── tests/
│   ├── test_text_splitter.py
│   └── test_document_transformer.py
├── pyproject.toml
├── README.md
└── LICENSE
```

### TextSplitter Implementation

```python
from typing import Any, List, Optional
from langchain.text_splitter import TextSplitter
from langchain.schema import Document
from markdown_chunker import MarkdownChunker, ChunkConfig

class MarkdownChunkerTextSplitter(TextSplitter):
    """
    LangChain TextSplitter adapter for markdown_chunker_v2.
    
    Provides intelligent, structure-aware markdown chunking
    with automatic strategy selection.
    
    Example:
        >>> from langchain_markdown_chunker import MarkdownChunkerTextSplitter
        >>> splitter = MarkdownChunkerTextSplitter(
        ...     max_chunk_size=1500,
        ...     overlap_size=100
        ... )
        >>> chunks = splitter.split_text(markdown_content)
    """
    
    def __init__(
        self,
        max_chunk_size: int = 2000,
        min_chunk_size: int = 200,
        overlap_size: int = 100,
        preserve_code_blocks: bool = True,
        preserve_tables: bool = True,
        strategy_override: Optional[str] = None,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        
        self.config = ChunkConfig(
            max_chunk_size=max_chunk_size,
            min_chunk_size=min_chunk_size,
            overlap_size=overlap_size,
            preserve_code_blocks=preserve_code_blocks,
            preserve_tables=preserve_tables,
            strategy_override=strategy_override
        )
        self.chunker = MarkdownChunker(self.config)
    
    def split_text(self, text: str) -> List[str]:
        """
        Split markdown text into chunks.
        
        Args:
            text: Markdown text to split
            
        Returns:
            List of text chunks
        """
        result = self.chunker.chunk(text)
        return [chunk.content for chunk in result.chunks]
    
    def split_documents(
        self, 
        documents: List[Document]
    ) -> List[Document]:
        """
        Split documents into smaller chunks.
        
        Preserves and enriches document metadata.
        
        Args:
            documents: List of LangChain Documents
            
        Returns:
            List of chunked Documents with metadata
        """
        output_documents = []
        
        for doc in documents:
            result = self.chunker.chunk(doc.page_content)
            
            for i, chunk in enumerate(result.chunks):
                # Merge original metadata with chunk metadata
                chunk_metadata = {
                    **doc.metadata,
                    "chunk_index": i,
                    "total_chunks": len(result.chunks),
                    "strategy_used": result.strategy_used,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "header_path": chunk.header_path,
                }
                
                output_documents.append(Document(
                    page_content=chunk.content,
                    metadata=chunk_metadata
                ))
        
        return output_documents
    
    @classmethod
    def from_config(cls, config: ChunkConfig) -> "MarkdownChunkerTextSplitter":
        """Create splitter from ChunkConfig."""
        return cls(
            max_chunk_size=config.max_chunk_size,
            min_chunk_size=config.min_chunk_size,
            overlap_size=config.overlap_size,
        )
```

### DocumentTransformer Implementation

```python
from langchain.schema import BaseDocumentTransformer
from typing import Sequence

class MarkdownChunkerTransformer(BaseDocumentTransformer):
    """
    Document transformer using markdown_chunker_v2.
    
    Can be used in LangChain pipelines and chains.
    """
    
    def __init__(self, config: Optional[ChunkConfig] = None):
        self.config = config or ChunkConfig()
        self.chunker = MarkdownChunker(self.config)
    
    def transform_documents(
        self, 
        documents: Sequence[Document],
        **kwargs: Any
    ) -> Sequence[Document]:
        """Transform documents by chunking."""
        splitter = MarkdownChunkerTextSplitter.from_config(self.config)
        return splitter.split_documents(list(documents))
    
    async def atransform_documents(
        self, 
        documents: Sequence[Document],
        **kwargs: Any
    ) -> Sequence[Document]:
        """Async version of transform_documents."""
        return self.transform_documents(documents, **kwargs)
```

---

## Usage Examples

### Basic Usage

```python
from langchain_markdown_chunker import MarkdownChunkerTextSplitter

# Create splitter
splitter = MarkdownChunkerTextSplitter(
    max_chunk_size=1500,
    overlap_size=100
)

# Split text
with open("docs/api.md") as f:
    markdown = f.read()

chunks = splitter.split_text(markdown)
print(f"Created {len(chunks)} chunks")
```

### With Document Loaders

```python
from langchain.document_loaders import DirectoryLoader
from langchain_markdown_chunker import MarkdownChunkerTextSplitter

# Load markdown files
loader = DirectoryLoader("docs/", glob="**/*.md")
documents = loader.load()

# Split with markdown-aware chunking
splitter = MarkdownChunkerTextSplitter(
    max_chunk_size=2000,
    preserve_code_blocks=True
)
chunks = splitter.split_documents(documents)

# Store in vector database
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

vectorstore = Chroma.from_documents(
    chunks,
    embedding=OpenAIEmbeddings()
)
```

### In RAG Pipeline

```python
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

# Create QA chain with markdown-chunked docs
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(),
    retriever=vectorstore.as_retriever(),
    chain_type="stuff"
)

answer = qa.run("How do I authenticate with the API?")
```

---

## Package Configuration

### pyproject.toml

```toml
[project]
name = "langchain-markdown-chunker"
version = "0.1.0"
description = "LangChain adapter for markdown_chunker_v2"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your@email.com"}
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "langchain-core>=0.1.0",
    "markdown-chunker>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## Тестирование

### Unit Tests

```python
def test_split_text():
    """split_text возвращает list of strings"""
    splitter = MarkdownChunkerTextSplitter()
    chunks = splitter.split_text("# Header\n\nParagraph")
    assert isinstance(chunks, list)
    assert all(isinstance(c, str) for c in chunks)

def test_split_documents():
    """split_documents сохраняет и обогащает metadata"""
    splitter = MarkdownChunkerTextSplitter()
    docs = [Document(page_content="# Header\n\nText", metadata={"source": "test.md"})]
    chunks = splitter.split_documents(docs)
    
    assert all(c.metadata.get("source") == "test.md" for c in chunks)
    assert all("chunk_index" in c.metadata for c in chunks)

def test_config_passthrough():
    """Конфигурация корректно передаётся в chunker"""
    
def test_integration_with_vectorstore():
    """Интеграция с Chroma работает"""
```

---

## Ожидаемые результаты

### Adoption Metrics

| Метрика | Цель (6 месяцев) |
|---------|------------------|
| PyPI downloads/month | 1000+ |
| GitHub stars | 50+ |
| Issues/PRs from community | 10+ |

### User Benefits

1. **Zero custom code** — drop-in replacement
2. **Rich metadata** — header_path, strategy_used, etc.
3. **Familiar API** — стандартный LangChain interface

---

## Риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| LangChain API changes | Medium | Medium | Pin version, monitor releases |
| Maintenance burden | Low | Medium | Automated tests |

---

## Acceptance Criteria

- [ ] Package опубликован в PyPI
- [ ] TextSplitter interface полностью реализован
- [ ] DocumentTransformer interface реализован
- [ ] Metadata enrichment работает
- [ ] Интеграция с Chroma/FAISS протестирована
- [ ] README с примерами
- [ ] CI/CD для automated publishing

---

## Примеры из тестового корпуса

В ТЕСТОВОМ КОРПУСЕ ПРИМЕРОВ СЕЙЧАС НЕТ.

Эта фича является интеграционной и не требует специфических тестовых файлов в корпусе. Для тестирования интеграции можно использовать любые файлы из `tests/corpus/`.
