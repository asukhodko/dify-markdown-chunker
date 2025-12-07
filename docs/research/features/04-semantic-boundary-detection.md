# Feature 04: Semantic Boundary Detection

## Краткое описание

Использование sentence embeddings для определения оптимальных границ чанков на основе семантических переходов между параграфами. Значительное улучшение качества chunking.

---

## Метаданные

| Параметр | Значение |
|----------|----------|
| **Фаза** | 2 — Семантические возможности |
| **Приоритет** | HIGH |
| **Effort** | 5-7 дней |
| **Impact** | Very High |
| **Уникальность** | No (Chonkie имеет аналог) |

---

## Проблема

### Текущее состояние

Границы чанков определяются на основе:
- Структурных элементов (headers, code blocks)
- Размера (max_chunk_size)
- Типа контента (tables, lists)

**Не учитывается:**
- Семантическая связность параграфов
- Тематические переходы
- Логическая завершённость

### Последствия

1. Связанные по смыслу параграфы разделяются
2. Несвязанные параграфы объединяются
3. Retrieval quality страдает
4. User Need C2.1: "Related paragraphs separated" — Very High frequency, Critical severity

### Пример проблемы

```markdown
# API Reference

## Authentication

The API uses OAuth 2.0 for authentication. You need to obtain
an access token before making requests.

To get a token, send a POST request to /oauth/token with your
client credentials. The response will contain your access token.

Here's an example of how to use the token in requests:

```python
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("/api/data", headers=headers)
```

## Rate Limiting

The API enforces rate limits to ensure fair usage...
```

**Текущее поведение:** Может разорвать объяснение OAuth от примера кода
**Желаемое поведение:** Semantic boundary между "Authentication" и "Rate Limiting"

---

## Решение

### Архитектура

```python
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Optional

class SemanticBoundaryDetector:
    """
    Определение семантических границ с использованием embeddings.
    """
    
    def __init__(
        self, 
        model_name: str = 'all-MiniLM-L6-v2',
        threshold: float = 0.3,
        min_segment_size: int = 100
    ):
        self.model = SentenceTransformer(model_name)
        self.threshold = threshold
        self.min_segment_size = min_segment_size
    
    def find_boundaries(
        self, 
        text: str,
        paragraphs: Optional[list[str]] = None
    ) -> list[int]:
        """
        Найти семантические границы в тексте.
        
        Returns:
            Список индексов параграфов, где происходит semantic shift
        """
        if paragraphs is None:
            paragraphs = self._split_paragraphs(text)
        
        if len(paragraphs) < 2:
            return []
        
        # Получить embeddings для всех параграфов
        embeddings = self.model.encode(
            paragraphs, 
            show_progress_bar=False,
            convert_to_numpy=True
        )
        
        boundaries = []
        for i in range(len(embeddings) - 1):
            similarity = self._cosine_similarity(
                embeddings[i], 
                embeddings[i + 1]
            )
            
            # Низкая similarity = семантический переход
            if similarity < self.threshold:
                boundaries.append(i + 1)
        
        return boundaries
    
    def _cosine_similarity(
        self, 
        vec1: np.ndarray, 
        vec2: np.ndarray
    ) -> float:
        """Вычислить cosine similarity между векторами."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2)
    
    def _split_paragraphs(self, text: str) -> list[str]:
        """Разделить текст на параграфы."""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if p.strip()]
```

### Интеграция с Chunker

```python
class MarkdownChunker:
    def __init__(
        self, 
        config: ChunkConfig,
        use_semantic_boundaries: bool = False
    ):
        self.config = config
        self.use_semantic_boundaries = use_semantic_boundaries
        
        if use_semantic_boundaries:
            self.semantic_detector = SemanticBoundaryDetector(
                threshold=config.semantic_threshold
            )
    
    def chunk(self, text: str) -> ChunkingResult:
        # 1. Parse document
        parsed = self.parser.parse(text)
        
        # 2. Get structural boundaries
        structural_boundaries = self._get_structural_boundaries(parsed)
        
        # 3. Get semantic boundaries (if enabled)
        if self.use_semantic_boundaries:
            semantic_boundaries = self.semantic_detector.find_boundaries(
                text, parsed.paragraphs
            )
            # Merge boundaries
            boundaries = self._merge_boundaries(
                structural_boundaries,
                semantic_boundaries
            )
        else:
            boundaries = structural_boundaries
        
        # 4. Create chunks
        return self._create_chunks(text, boundaries)
```

### Конфигурация

```python
@dataclass
class ChunkConfig:
    # Existing
    max_chunk_size: int = 2000
    min_chunk_size: int = 200
    
    # Semantic boundaries
    use_semantic_boundaries: bool = False
    semantic_threshold: float = 0.3
    semantic_model: str = 'all-MiniLM-L6-v2'
```

---

## Модели

### Рекомендуемые модели

| Модель | Размер | Скорость | Качество | Рекомендация |
|--------|--------|----------|----------|--------------|
| all-MiniLM-L6-v2 | 90MB | Fast | Good | **Default** |
| all-mpnet-base-v2 | 420MB | Medium | Best | Quality-focused |
| paraphrase-MiniLM-L3-v2 | 45MB | Fastest | Fair | Speed-focused |

### Multilingual Support

| Модель | Языки | Размер |
|--------|-------|--------|
| paraphrase-multilingual-MiniLM-L12-v2 | 50+ | 470MB |
| distiluse-base-multilingual-cased-v2 | 50+ | 520MB |

---

## Тестирование

### Unit Tests

```python
def test_semantic_boundary_detection():
    """Semantic boundaries определяются корректно"""
    text = """
    Introduction to Python programming.
    Python is a versatile language.
    
    Now let's talk about databases.
    SQL is used for querying data.
    """
    detector = SemanticBoundaryDetector(threshold=0.5)
    boundaries = detector.find_boundaries(text)
    # Ожидаем boundary между Python и databases
    assert len(boundaries) >= 1

def test_no_boundary_similar_content():
    """Похожий контент не создаёт boundaries"""
    text = """
    Python has great libraries.
    Python libraries include NumPy and Pandas.
    Python data science ecosystem is mature.
    """
    boundaries = detector.find_boundaries(text)
    assert len(boundaries) == 0

def test_threshold_sensitivity():
    """Threshold влияет на количество boundaries"""
    
def test_empty_text():
    """Пустой текст не вызывает ошибок"""
    
def test_single_paragraph():
    """Один параграф — нет boundaries"""
```

### Integration Tests

```python
def test_semantic_with_structural():
    """Semantic boundaries дополняют structural"""
    
def test_semantic_improves_quality():
    """SCS улучшается с semantic boundaries"""
```

---

## Ожидаемые улучшения

### Метрики качества

| Метрика | До | После | Улучшение |
|---------|-----|-------|-----------|
| SCS (overall) | 1.3 | 1.7-1.8 | +30-40% |
| CPS (overall) | 75% | 85%+ | +10% |
| Overall quality | 78 | 86+ | +10% |

### Польза для пользователей

1. **Лучший retrieval** — связанные параграфы вместе
2. **Меньше irrelevant chunks** — темы не смешиваются
3. **Language-agnostic** — работает для любых языков

---

## Зависимости

### Новые dependencies

```
sentence-transformers>=2.2.0
torch>=2.0.0 (transitive)
transformers>=4.0.0 (transitive)
```

### Optional dependency

Semantic boundaries — optional feature:
```python
try:
    from sentence_transformers import SentenceTransformer
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
```

---

## Performance

### Benchmarks

| Документ | Размер | Время (без semantic) | Время (с semantic) |
|----------|--------|---------------------|-------------------|
| Small | 5KB | 10ms | 150ms |
| Medium | 50KB | 50ms | 400ms |
| Large | 200KB | 150ms | 1200ms |

### Оптимизации

1. **Caching** — кешировать embeddings для повторных запросов
2. **Batching** — обрабатывать параграфы батчами
3. **GPU acceleration** — использовать GPU если доступен
4. **Lazy loading** — загружать модель только при необходимости

---

## Риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Slow processing | High | Medium | Optional feature, caching |
| Large dependencies | Medium | Medium | Optional install |
| Model download | Medium | Low | Pre-download option |
| GPU memory | Low | Low | CPU fallback |

---

## Acceptance Criteria

- [ ] Semantic boundaries определяются с accuracy > 80%
- [ ] Feature работает как optional (без ML deps)
- [ ] Threshold конфигурируется
- [ ] Multilingual модель доступна
- [ ] SCS улучшается минимум на 25%
- [ ] Caching реализован для production use
- [ ] Документация для настройки

---

## Примеры из тестового корпуса

Следующие файлы подходят для тестирования Semantic Boundary Detection (содержат разнообразный контент с семантическими переходами):

### Engineering Blogs и Research Notes

| Файл | Строк | Описание |
|------|-------|----------|
| [engineering_blogs_026.md](../../../tests/corpus/engineering_blogs/engineering_blogs_026.md) | 191 | Технический блог с тематическими переходами |
| [research_notes_007.md](../../../tests/corpus/research_notes/research_notes_007.md) | 97 | Исследовательские заметки |

### Mixed Content (разнообразный контент)

| Файл | Строк | Описание |
|------|-------|----------|
| [mixed_content_004.md](../../../tests/corpus/mixed_content/mixed_content_004.md) | 84 | Смешанный контент |
| [mixed_content_005.md](../../../tests/corpus/mixed_content/mixed_content_005.md) | 95 | Разнообразные секции |
| [mixed_content_007.md](../../../tests/corpus/mixed_content/mixed_content_007.md) | 93 | Смешанный контент |
| [mixed_content_009.md](../../../tests/corpus/mixed_content/mixed_content_009.md) | 64 | Mixed content |
| [mixed_content_014.md](../../../tests/corpus/mixed_content/mixed_content_014.md) | 65 | Mixed content |

### Документация с тематическими разделами

| Файл | Строк | Описание |
|------|-------|----------|
| [docker_005.md](../../../tests/corpus/technical_docs/docker/docker_005.md) | 348 | Docker документация |
| [pytorch.md](../../../tests/corpus/github_readmes/python/pytorch.md) | 575 | PyTorch README с разделами |
| [fastapi.md](../../../tests/corpus/github_readmes/python/fastapi.md) | 563 | FastAPI документация |
| [spaCy.md](../../../tests/corpus/github_readmes/python/spaCy.md) | 293 | spaCy README |
