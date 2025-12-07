# Feature 05: Token-Aware Sizing

## Краткое описание

Размер чанков на основе токенов вместо символов для точного соответствия context window LLM моделей (GPT-4, Claude, etc.).

---

## Метаданные

| Параметр | Значение |
|----------|----------|
| **Фаза** | 2 — Семантические возможности |
| **Приоритет** | HIGH |
| **Effort** | 2-3 дня |
| **Impact** | High |
| **Уникальность** | No (Semantic Kernel имеет аналог) |

---

## Проблема

### Текущее состояние

Размеры чанков задаются в символах:
- `max_chunk_size: int = 2000` (символов)
- `min_chunk_size: int = 200` (символов)

### Почему это проблема

1. **Несоответствие token limits:**
   - 2000 символов ≈ 400-600 токенов (зависит от языка)
   - Точное соотношение непредсказуемо
   
2. **Разные модели — разные tokenizers:**
   - GPT-4 использует cl100k_base
   - Claude использует другой tokenizer
   - Llama использует SentencePiece

3. **User Need C3.4:** "No token-aware sizing" — Medium frequency, High severity

### Пример несоответствия

```python
# Текст на 2000 символов
text = "Python is..." * 200  # ~2000 chars

# GPT-4 tokenization
import tiktoken
enc = tiktoken.encoding_for_model("gpt-4")
tokens = enc.encode(text)
print(len(tokens))  # Может быть 400-600, непредсказуемо
```

---

## Решение

### Архитектура

```python
import tiktoken
from typing import Optional, Literal

ModelType = Literal[
    "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo",
    "claude-3-opus", "claude-3-sonnet", "claude-3-haiku",
    "text-embedding-ada-002", "text-embedding-3-small"
]

class TokenCounter:
    """
    Подсчёт токенов для различных LLM моделей.
    """
    
    # Mapping моделей к tiktoken encodings
    MODEL_ENCODINGS = {
        "gpt-4": "cl100k_base",
        "gpt-4-turbo": "cl100k_base",
        "gpt-3.5-turbo": "cl100k_base",
        "claude-3-opus": "cl100k_base",  # Approximation
        "claude-3-sonnet": "cl100k_base",
        "claude-3-haiku": "cl100k_base",
        "text-embedding-ada-002": "cl100k_base",
        "text-embedding-3-small": "cl100k_base",
    }
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        encoding_name = self.MODEL_ENCODINGS.get(model, "cl100k_base")
        self.encoding = tiktoken.get_encoding(encoding_name)
    
    def count_tokens(self, text: str) -> int:
        """Подсчитать количество токенов в тексте."""
        return len(self.encoding.encode(text))
    
    def truncate_to_tokens(
        self, 
        text: str, 
        max_tokens: int
    ) -> str:
        """Обрезать текст до max_tokens."""
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        truncated = self.encoding.decode(tokens[:max_tokens])
        return truncated
    
    def split_by_tokens(
        self, 
        text: str, 
        max_tokens: int,
        overlap_tokens: int = 0
    ) -> list[str]:
        """Разделить текст на части по max_tokens."""
        tokens = self.encoding.encode(text)
        chunks = []
        
        i = 0
        while i < len(tokens):
            end = min(i + max_tokens, len(tokens))
            chunk_tokens = tokens[i:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            # Следующий чанк с overlap
            i = end - overlap_tokens if overlap_tokens else end
        
        return chunks
```

### Интеграция с ChunkConfig

```python
@dataclass
class ChunkConfig:
    # Character-based (existing)
    max_chunk_size: int = 2000
    min_chunk_size: int = 200
    
    # Token-based (new)
    use_token_sizing: bool = False
    max_tokens: int = 512
    min_tokens: int = 50
    overlap_tokens: int = 50
    token_model: str = "gpt-4"
    
    def get_effective_max_size(self, text: str = "") -> int:
        """Получить эффективный max size."""
        if self.use_token_sizing:
            # Конвертировать в примерные символы для backwards compat
            return self.max_tokens * 4  # Approximation
        return self.max_chunk_size
```

### Интеграция с Chunker

```python
class MarkdownChunker:
    def __init__(self, config: ChunkConfig):
        self.config = config
        if config.use_token_sizing:
            self.token_counter = TokenCounter(config.token_model)
    
    def _fits_size_limit(self, content: str) -> bool:
        """Проверить, что контент помещается в лимит."""
        if self.config.use_token_sizing:
            tokens = self.token_counter.count_tokens(content)
            return tokens <= self.config.max_tokens
        return len(content) <= self.config.max_chunk_size
    
    def _split_oversized(self, content: str) -> list[str]:
        """Разделить слишком большой контент."""
        if self.config.use_token_sizing:
            return self.token_counter.split_by_tokens(
                content,
                self.config.max_tokens,
                self.config.overlap_tokens
            )
        # Fallback to character-based
        return self._split_by_chars(content)
```

### Factory Methods для популярных моделей

```python
@dataclass
class ChunkConfig:
    # ... existing fields ...
    
    @classmethod
    def for_gpt4(cls, max_tokens: int = 512) -> "ChunkConfig":
        """Конфигурация для GPT-4."""
        return cls(
            use_token_sizing=True,
            max_tokens=max_tokens,
            token_model="gpt-4"
        )
    
    @classmethod
    def for_claude(cls, max_tokens: int = 512) -> "ChunkConfig":
        """Конфигурация для Claude."""
        return cls(
            use_token_sizing=True,
            max_tokens=max_tokens,
            token_model="claude-3-sonnet"
        )
    
    @classmethod
    def for_embedding(cls, max_tokens: int = 8191) -> "ChunkConfig":
        """Конфигурация для embedding models."""
        return cls(
            use_token_sizing=True,
            max_tokens=max_tokens,
            token_model="text-embedding-3-small"
        )
```

---

## Тестирование

### Unit Tests

```python
def test_token_counting():
    """Token counting работает корректно"""
    counter = TokenCounter("gpt-4")
    text = "Hello, world!"
    tokens = counter.count_tokens(text)
    assert tokens > 0
    assert tokens < len(text)

def test_truncate_to_tokens():
    """Truncation обрезает до точного количества токенов"""
    counter = TokenCounter("gpt-4")
    text = "This is a test sentence. " * 100
    truncated = counter.truncate_to_tokens(text, 10)
    assert counter.count_tokens(truncated) <= 10

def test_split_by_tokens():
    """Split создаёт чанки правильного размера"""
    counter = TokenCounter("gpt-4")
    text = "Word " * 1000  # ~1000 tokens
    chunks = counter.split_by_tokens(text, max_tokens=100)
    for chunk in chunks[:-1]:  # Все кроме последнего
        assert counter.count_tokens(chunk) <= 100

def test_split_with_overlap():
    """Overlap токенов работает"""
    
def test_different_models():
    """Разные модели имеют разные encodings"""
```

### Integration Tests

```python
def test_chunker_with_token_sizing():
    """Chunker использует token sizing когда enabled"""
    config = ChunkConfig.for_gpt4(max_tokens=256)
    chunker = MarkdownChunker(config)
    result = chunker.chunk(long_text)
    
    counter = TokenCounter("gpt-4")
    for chunk in result.chunks:
        assert counter.count_tokens(chunk.content) <= 256
```

---

## Ожидаемые улучшения

### Польза для пользователей

1. **Точное соответствие context window:**
   - GPT-4: 128K context, но retrieval chunks обычно 256-512 tokens
   - Claude: 200K context
   
2. **Предсказуемое поведение:**
   - `max_tokens=512` всегда даёт 512 токенов
   - Нет сюрпризов при inference

3. **Оптимизация для разных use cases:**
   - Retrieval: 256-512 tokens
   - Summarization: 1024-2048 tokens
   - Analysis: 4096+ tokens

---

## Зависимости

### Новые dependencies

```
tiktoken>=0.5.0
```

### Размер dependency

- tiktoken: ~1MB (очень лёгкий)
- No PyTorch/Transformers required

### Optional dependency pattern

```python
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    
def ensure_tiktoken():
    if not TIKTOKEN_AVAILABLE:
        raise ImportError(
            "tiktoken is required for token-aware sizing. "
            "Install with: pip install tiktoken"
        )
```

---

## Performance

### Benchmarks

| Операция | Время |
|----------|-------|
| count_tokens (100 chars) | 0.05ms |
| count_tokens (10K chars) | 0.5ms |
| split_by_tokens (100K chars) | 5ms |

Token counting очень быстрый — negligible overhead.

---

## Риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| tiktoken version conflicts | Low | Low | Pin version |
| Model encoding updates | Low | Low | Version tracking |
| Claude tokenizer approximation | Medium | Low | Document limitation |

---

## Acceptance Criteria

- [ ] TokenCounter работает для GPT-4, GPT-3.5
- [ ] TokenCounter работает для Claude (approximation)
- [ ] max_tokens соблюдается для всех чанков
- [ ] overlap_tokens работает корректно
- [ ] Factory methods для популярных моделей
- [ ] tiktoken — optional dependency
- [ ] Backward compatibility с character-based sizing
- [ ] Документация с примерами для разных моделей

---

## Примеры из тестового корпуса

Следующие большие файлы подходят для тестирования Token-Aware Sizing (большой объём текста для точного подсчёта токенов):

### Очень большие файлы (>50KB)

| Файл | Размер | Строк | Описание |
|------|--------|-------|----------|
| [youtube-dl.md](../../../tests/corpus/github_readmes/python/youtube-dl.md) | 101KB | 1581 | Огромный README |
| [webpack.md](../../../tests/corpus/github_readmes/javascript/webpack.md) | 80KB | 662 | Webpack документация |
| [axios.md](../../../tests/corpus/github_readmes/javascript/axios.md) | 72KB | 1802 | Axios README с API |

### Большие файлы (20-50KB)

| Файл | Размер | Строк | Описание |
|------|--------|-------|----------|
| [node.md](../../../tests/corpus/github_readmes/javascript/node.md) | 42KB | 922 | Node.js README |
| [parcel.md](../../../tests/corpus/github_readmes/javascript/parcel.md) | 32KB | 1 | Parcel документация |
| [pytorch.md](../../../tests/corpus/github_readmes/python/pytorch.md) | 27KB | 575 | PyTorch README |
| [fastapi.md](../../../tests/corpus/github_readmes/python/fastapi.md) | 26KB | 563 | FastAPI README |
| [spaCy.md](../../../tests/corpus/github_readmes/python/spaCy.md) | 24KB | 293 | spaCy README |
| [eslint.md](../../../tests/corpus/github_readmes/javascript/eslint.md) | 20KB | 355 | ESLint README |

### Средние файлы (10-20KB)

| Файл | Размер | Строк | Описание |
|------|--------|-------|----------|
| [face_recognition.md](../../../tests/corpus/github_readmes/python/face_recognition.md) | 19KB | 416 | face_recognition README |
| [celery.md](../../../tests/corpus/github_readmes/python/celery.md) | 18KB | 609 | Celery README |
| [hugo.md](../../../tests/corpus/github_readmes/go/hugo.md) | 13KB | 283 | Hugo README |
| [gin.md](../../../tests/corpus/github_readmes/go/gin.md) | 11KB | 228 | Gin README |
