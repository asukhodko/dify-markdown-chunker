# Feature 14: Streaming Processing

## Краткое описание

Потоковая обработка больших файлов для снижения потребления памяти и поддержки файлов >10MB.

---

## Метаданные

| Параметр | Значение |
|----------|----------|
| **Фаза** | 5 — Производительность и полировка |
| **Приоритет** | LOW |
| **Effort** | 5-7 дней |
| **Impact** | Medium |
| **Уникальность** | No |

---

## Проблема

### Текущее состояние

- Весь документ загружается в память
- Парсинг и chunking работают с полным текстом
- Для файлов >10MB возможны проблемы с памятью

### User Need

C8.2: "Memory issues with big docs" — Low frequency, High severity

### Типичные большие файлы

| Тип | Размер | Примеры |
|-----|--------|---------|
| Полная документация проекта | 5-50MB | Kubernetes docs, AWS docs |
| Concatenated changelogs | 10-20MB | Долгоживущие проекты |
| Generated API reference | 20-100MB | OpenAPI → Markdown |
| Book manuscripts | 1-10MB | Technical books |

---

## Решение

### Архитектура

```python
from typing import Iterator, Optional
from dataclasses import dataclass
import io

@dataclass
class StreamingConfig:
    """Конфигурация для streaming обработки."""
    buffer_size: int = 100_000        # 100KB buffer
    overlap_lines: int = 20           # Lines to keep for context
    max_memory_mb: int = 100          # Max memory usage

class StreamingChunker:
    """
    Потоковый chunker для больших файлов.
    """
    
    def __init__(
        self,
        config: ChunkConfig,
        streaming_config: Optional[StreamingConfig] = None
    ):
        self.config = config
        self.streaming_config = streaming_config or StreamingConfig()
        self.base_chunker = MarkdownChunker(config)
    
    def chunk_file(
        self,
        file_path: str
    ) -> Iterator[Chunk]:
        """
        Потоково обработать файл.
        
        Args:
            file_path: Путь к markdown файлу
            
        Yields:
            Chunk objects
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            yield from self.chunk_stream(f)
    
    def chunk_stream(
        self,
        stream: io.TextIOBase
    ) -> Iterator[Chunk]:
        """
        Потоково обработать text stream.
        
        Args:
            stream: Text stream (file, StringIO, etc.)
            
        Yields:
            Chunk objects
        """
        buffer = []
        buffer_size = 0
        chunk_index = 0
        overlap_buffer = []
        
        for line in stream:
            buffer.append(line)
            buffer_size += len(line)
            
            # Process buffer when it reaches threshold
            if buffer_size >= self.streaming_config.buffer_size:
                # Find safe split point
                split_idx = self._find_safe_split_point(buffer)
                
                # Process complete section
                text_to_process = ''.join(buffer[:split_idx])
                
                # Add overlap from previous buffer
                if overlap_buffer:
                    text_to_process = ''.join(overlap_buffer) + text_to_process
                
                # Chunk this section
                for chunk in self._process_buffer(
                    text_to_process, 
                    chunk_index
                ):
                    yield chunk
                    chunk_index += 1
                
                # Keep overlap for next buffer
                overlap_buffer = buffer[
                    max(0, split_idx - self.streaming_config.overlap_lines):
                    split_idx
                ]
                
                # Reset buffer
                buffer = buffer[split_idx:]
                buffer_size = sum(len(line) for line in buffer)
        
        # Process remaining buffer
        if buffer:
            text_to_process = ''.join(overlap_buffer + buffer)
            for chunk in self._process_buffer(text_to_process, chunk_index):
                yield chunk
    
    def _find_safe_split_point(self, buffer: list[str]) -> int:
        """
        Найти безопасную точку разделения.
        
        Не разрывать:
        - Code blocks
        - Tables
        - Lists
        - Headers (keep with content)
        """
        # Start from 80% of buffer
        start_idx = int(len(buffer) * 0.8)
        
        for i in range(start_idx, len(buffer)):
            line = buffer[i]
            
            # Empty line between sections is safe
            if not line.strip():
                # Check next line
                if i + 1 < len(buffer):
                    next_line = buffer[i + 1]
                    # Safe if next line is header
                    if next_line.startswith('#'):
                        return i + 1
                    # Safe if we're not in code block
                    if not self._in_code_block(buffer[:i]):
                        return i + 1
        
        # Fallback: split at 80%
        return start_idx
    
    def _in_code_block(self, lines: list[str]) -> bool:
        """Проверить, находимся ли внутри code block."""
        fence_count = 0
        for line in lines:
            if line.strip().startswith('```') or line.strip().startswith('~~~'):
                fence_count += 1
        return fence_count % 2 == 1
    
    def _process_buffer(
        self,
        text: str,
        start_index: int
    ) -> Iterator[Chunk]:
        """Обработать buffer через base chunker."""
        result = self.base_chunker.chunk(text)
        
        for i, chunk in enumerate(result.chunks):
            # Adjust chunk index for streaming
            chunk.metadata['stream_chunk_index'] = start_index + i
            yield chunk
```

### Async Support

```python
import aiofiles
from typing import AsyncIterator

class AsyncStreamingChunker(StreamingChunker):
    """Async версия streaming chunker."""
    
    async def chunk_file_async(
        self,
        file_path: str
    ) -> AsyncIterator[Chunk]:
        """
        Async потоковая обработка файла.
        """
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            buffer = []
            buffer_size = 0
            chunk_index = 0
            
            async for line in f:
                buffer.append(line)
                buffer_size += len(line)
                
                if buffer_size >= self.streaming_config.buffer_size:
                    # Process buffer (sync, CPU-bound)
                    for chunk in self._process_buffer_sync(buffer, chunk_index):
                        yield chunk
                        chunk_index += 1
                    
                    buffer = []
                    buffer_size = 0
            
            # Process remaining
            if buffer:
                for chunk in self._process_buffer_sync(buffer, chunk_index):
                    yield chunk
```

---

## Usage Examples

### Basic File Streaming

```python
from markdown_chunker import StreamingChunker, ChunkConfig

config = ChunkConfig(max_chunk_size=2000)
streamer = StreamingChunker(config)

# Process large file
for chunk in streamer.chunk_file("large_documentation.md"):
    # Process each chunk immediately
    vector_db.add(chunk.content, chunk.metadata)
    
print("Processing complete!")
```

### Memory-Constrained Environment

```python
from markdown_chunker import StreamingChunker, StreamingConfig

# Strict memory limits
streaming_config = StreamingConfig(
    buffer_size=50_000,     # 50KB buffer
    max_memory_mb=50        # Max 50MB
)

streamer = StreamingChunker(
    config=ChunkConfig(),
    streaming_config=streaming_config
)

# Process with minimal memory
chunk_count = 0
for chunk in streamer.chunk_file("huge_docs.md"):
    chunk_count += 1
    process_chunk(chunk)

print(f"Processed {chunk_count} chunks with minimal memory")
```

### Async Processing

```python
import asyncio

async def process_large_file(file_path: str):
    streamer = AsyncStreamingChunker(ChunkConfig())
    
    async for chunk in streamer.chunk_file_async(file_path):
        await vector_db.add_async(chunk.content, chunk.metadata)

asyncio.run(process_large_file("large_docs.md"))
```

### Progress Tracking

```python
from markdown_chunker import StreamingChunker
import os

file_path = "large_documentation.md"
file_size = os.path.getsize(file_path)

streamer = StreamingChunker(ChunkConfig())
processed_bytes = 0

for chunk in streamer.chunk_file(file_path):
    processed_bytes += len(chunk.content)
    progress = (processed_bytes / file_size) * 100
    print(f"\rProgress: {progress:.1f}%", end="")

print("\nDone!")
```

---

## Тестирование

### Unit Tests

```python
def test_streaming_produces_same_chunks():
    """Streaming даёт те же результаты что и обычный chunking"""
    text = "# Header\n\nParagraph\n\n## Section\n\nMore text"
    
    # Regular chunking
    regular = MarkdownChunker(config).chunk(text)
    
    # Streaming chunking
    streaming_chunks = list(StreamingChunker(config).chunk_stream(
        io.StringIO(text)
    ))
    
    assert len(regular.chunks) == len(streaming_chunks)

def test_large_file_memory_usage():
    """Streaming использует ограниченную память"""
    import tracemalloc
    
    tracemalloc.start()
    
    for chunk in StreamingChunker(config).chunk_file("10mb_file.md"):
        pass  # Just iterate
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    assert peak < 50 * 1024 * 1024  # < 50MB

def test_code_block_not_split():
    """Code blocks не разрываются при streaming"""
    
def test_overlap_between_buffers():
    """Overlap между buffers сохраняет контекст"""
```

---

## Ожидаемые улучшения

### Memory Usage

| Размер файла | Regular | Streaming |
|--------------|---------|-----------|
| 1MB | 10MB | 5MB |
| 10MB | 100MB | 10MB |
| 100MB | 1GB+ (OOM) | 20MB |

### Use Cases

| Scenario | До | После |
|----------|-----|-------|
| 10MB doc on 512MB RAM | Fails | Works |
| 100MB doc processing | Impossible | Possible |
| Real-time ingestion | Full load first | Stream processing |

---

## Конфигурация

```python
@dataclass
class StreamingConfig:
    buffer_size: int = 100_000        # Bytes per buffer
    overlap_lines: int = 20           # Context lines
    max_memory_mb: int = 100          # Memory limit
    safe_split_threshold: float = 0.8 # Where to look for split
```

---

## Зависимости

### Optional Dependencies

```
aiofiles>=23.0  # For async support
```

### Memory Profiling (dev)

```
tracemalloc  # Built-in Python
memory_profiler>=0.60  # Optional
```

---

## Риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Chunk quality at boundaries | Medium | Medium | Smart split detection |
| Complexity | High | Medium | Good testing |
| Different results vs regular | Low | High | Extensive testing |

---

## Acceptance Criteria

- [ ] StreamingChunker API создан
- [ ] chunk_file() работает для >10MB файлов
- [ ] Memory usage < 50MB для любого размера файла
- [ ] Code blocks не разрываются между buffers
- [ ] Overlap сохраняет контекст
- [ ] Async support (optional)
- [ ] Progress tracking возможен
- [ ] Результаты идентичны regular chunking (где возможно)

---

## Примеры из тестового корпуса

Следующие большие файлы подходят для тестирования Streaming Processing:

### Очень большие файлы (>50KB)

| Файл | Размер | Строк | Описание |
|------|--------|-------|----------|
| [youtube-dl.md](../../../tests/corpus/github_readmes/python/youtube-dl.md) | 101KB | 1581 | Огромный README, идеален для streaming |
| [webpack.md](../../../tests/corpus/github_readmes/javascript/webpack.md) | 80KB | 662 | Большая документация |
| [axios.md](../../../tests/corpus/github_readmes/javascript/axios.md) | 72KB | 1802 | Много строк |

### Большие файлы (20-50KB)

| Файл | Размер | Строк | Описание |
|------|--------|-------|----------|
| [node.md](../../../tests/corpus/github_readmes/javascript/node.md) | 42KB | 922 | Node.js README |
| [pytorch.md](../../../tests/corpus/github_readmes/python/pytorch.md) | 27KB | 575 | PyTorch README |
| [fastapi.md](../../../tests/corpus/github_readmes/python/fastapi.md) | 26KB | 563 | FastAPI README |
| [spaCy.md](../../../tests/corpus/github_readmes/python/spaCy.md) | 24KB | 293 | spaCy README |
| [eslint.md](../../../tests/corpus/github_readmes/javascript/eslint.md) | 20KB | 355 | ESLint README |

### Средние файлы для сравнения (10-20KB)

| Файл | Размер | Строк | Описание |
|------|--------|-------|----------|
| [face_recognition.md](../../../tests/corpus/github_readmes/python/face_recognition.md) | 19KB | 416 | Для сравнения с regular chunking |
| [celery.md](../../../tests/corpus/github_readmes/python/celery.md) | 18KB | 609 | Celery README |
| [hugo.md](../../../tests/corpus/github_readmes/go/hugo.md) | 13KB | 283 | Hugo README |
| [tensorflow.md](../../../tests/corpus/github_readmes/python/tensorflow.md) | 12KB | 174 | TensorFlow README |
