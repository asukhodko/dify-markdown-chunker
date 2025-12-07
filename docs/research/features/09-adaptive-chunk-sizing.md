# Feature 09: Adaptive Chunk Sizing

## Краткое описание

Автоматическая настройка размера чанка на основе сложности и типа контента. Code-heavy контент получает большие чанки, простой текст — меньшие.

---

## Метаданные

| Параметр | Значение |
|----------|----------|
| **Фаза** | 3 — Интеграция и Adoption |
| **Приоритет** | MEDIUM |
| **Effort** | 2-3 дня |
| **Impact** | Medium |
| **Уникальность** | No |

---

## Проблема

### Текущее состояние

- Фиксированный `max_chunk_size` для всего контента
- Не учитывается сложность контента
- Один размер не оптимален для разных типов

### Почему это неоптимально

| Тип контента | Оптимальный размер | Причина |
|--------------|-------------------|---------|
| Code-heavy | 2500-3500 chars | Код нельзя разрывать, нужен контекст |
| Tables | 2000-3000 chars | Таблицы atomic, могут быть большими |
| Simple text | 1000-1500 chars | Меньше = лучше retrieval precision |
| Mixed | 1500-2000 chars | Баланс |

---

## Решение

### Архитектура

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class AdaptiveSizeConfig:
    """Конфигурация для adaptive sizing."""
    base_size: int = 1500
    min_scale: float = 0.5       # Минимум 50% от base
    max_scale: float = 1.5       # Максимум 150% от base
    
    # Weights для факторов сложности
    code_weight: float = 0.4
    table_weight: float = 0.3
    list_weight: float = 0.2
    sentence_length_weight: float = 0.1

class AdaptiveSizeCalculator:
    """
    Расчёт оптимального размера чанка на основе контента.
    """
    
    def __init__(self, config: Optional[AdaptiveSizeConfig] = None):
        self.config = config or AdaptiveSizeConfig()
    
    def calculate_optimal_size(
        self,
        content: str,
        analysis: Optional[ContentAnalysis] = None
    ) -> int:
        """
        Рассчитать оптимальный размер чанка.
        
        Args:
            content: Текст для анализа
            analysis: Готовый ContentAnalysis (опционально)
            
        Returns:
            Оптимальный размер в символах
        """
        if analysis is None:
            analysis = self._quick_analyze(content)
        
        complexity = self._calculate_complexity(analysis)
        
        # Scale factor: min_scale to max_scale
        scale = self.config.min_scale + complexity * (
            self.config.max_scale - self.config.min_scale
        )
        
        return int(self.config.base_size * scale)
    
    def _calculate_complexity(
        self,
        analysis: ContentAnalysis
    ) -> float:
        """
        Рассчитать сложность контента (0.0 - 1.0).
        
        Высокая сложность = нужны большие чанки
        """
        factors = {
            'code_ratio': min(analysis.code_ratio, 1.0),
            'table_ratio': min(analysis.table_ratio, 1.0),
            'list_ratio': min(analysis.list_ratio, 1.0),
            'sentence_length': min(
                analysis.avg_sentence_length / 100.0, 
                1.0
            ),
        }
        
        weights = {
            'code_ratio': self.config.code_weight,
            'table_ratio': self.config.table_weight,
            'list_ratio': self.config.list_weight,
            'sentence_length': self.config.sentence_length_weight,
        }
        
        complexity = sum(
            factors[k] * weights[k] 
            for k in factors
        )
        
        return min(complexity, 1.0)
    
    def _quick_analyze(self, content: str) -> ContentAnalysis:
        """Быстрый анализ контента."""
        lines = content.split('\n')
        total_chars = len(content)
        
        # Code detection
        code_chars = 0
        in_code_block = False
        for line in lines:
            if line.startswith('```'):
                in_code_block = not in_code_block
            elif in_code_block:
                code_chars += len(line)
        
        # Table detection
        table_chars = sum(
            len(line) for line in lines 
            if '|' in line and line.strip().startswith('|')
        )
        
        # List detection
        list_chars = sum(
            len(line) for line in lines
            if line.strip().startswith(('-', '*', '+')) or
               (line.strip() and line.strip()[0].isdigit() and '.' in line[:5])
        )
        
        return ContentAnalysis(
            code_ratio=code_chars / max(total_chars, 1),
            table_ratio=table_chars / max(total_chars, 1),
            list_ratio=list_chars / max(total_chars, 1),
            avg_sentence_length=self._avg_sentence_length(content),
        )
    
    def _avg_sentence_length(self, text: str) -> float:
        """Средняя длина предложения."""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if not sentences:
            return 0
        return sum(len(s) for s in sentences) / len(sentences)
```

### Интеграция с Chunker

```python
@dataclass
class ChunkConfig:
    # Existing
    max_chunk_size: int = 2000
    min_chunk_size: int = 200
    
    # Adaptive sizing
    use_adaptive_sizing: bool = False
    adaptive_config: Optional[AdaptiveSizeConfig] = None
    
    def get_effective_max_size(
        self,
        content: str = "",
        analysis: Optional[ContentAnalysis] = None
    ) -> int:
        """Получить эффективный max size."""
        if self.use_adaptive_sizing and content:
            calculator = AdaptiveSizeCalculator(self.adaptive_config)
            return calculator.calculate_optimal_size(content, analysis)
        return self.max_chunk_size

class MarkdownChunker:
    def chunk(self, text: str) -> ChunkingResult:
        # 1. Parse and analyze
        parsed = self.parser.parse(text)
        analysis = self.analyzer.analyze(parsed)
        
        # 2. Get adaptive size per section (if enabled)
        if self.config.use_adaptive_sizing:
            # Calculate size for each major section
            section_sizes = self._calculate_section_sizes(
                parsed.sections, analysis
            )
        else:
            section_sizes = None
        
        # 3. Apply strategy with sizes
        return self._apply_strategy(
            text, parsed, analysis, section_sizes
        )
```

---

## Примеры

### Code-Heavy Document

```markdown
# API Client

```python
class APIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}"
        })
    
    def get(self, endpoint: str) -> dict:
        response = self.session.get(f"{BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    
    # ... много кода ...
```
```

**Complexity:** ~0.7 (high code ratio)
**Optimal size:** 1500 * 1.35 = **2025 chars**

### Simple Text Document

```markdown
# Introduction

Welcome to our documentation. This guide will help you get started
with our product. We'll cover the basics and then move on to
more advanced topics.

Our product is designed to be simple and intuitive...
```

**Complexity:** ~0.15 (low, simple text)
**Optimal size:** 1500 * 0.65 = **975 chars**

---

## Тестирование

### Unit Tests

```python
def test_code_heavy_larger_chunks():
    """Code-heavy контент получает большие чанки"""
    calculator = AdaptiveSizeCalculator()
    code_content = "```python\n" + "x = 1\n" * 100 + "```"
    size = calculator.calculate_optimal_size(code_content)
    assert size > 1500  # Base size

def test_simple_text_smaller_chunks():
    """Простой текст получает меньшие чанки"""
    calculator = AdaptiveSizeCalculator()
    simple_text = "This is simple text. " * 50
    size = calculator.calculate_optimal_size(simple_text)
    assert size < 1500  # Base size

def test_mixed_content_medium_chunks():
    """Смешанный контент получает средние чанки"""
    
def test_custom_weights():
    """Custom weights влияют на расчёт"""
    
def test_min_max_bounds():
    """Размер не выходит за min/max scale"""
```

---

## Ожидаемые улучшения

| Метрика | До | После | Улучшение |
|---------|-----|-------|-----------|
| Retrieval precision | 75% | 82%+ | +7% |
| Code chunk quality | 70% | 85%+ | +15% |
| Text chunk quality | 80% | 85%+ | +5% |

---

## Конфигурация

### Default Config

```python
# Стандартная конфигурация
config = ChunkConfig(
    use_adaptive_sizing=True,
    adaptive_config=AdaptiveSizeConfig(
        base_size=1500,
        min_scale=0.5,   # 750 chars minimum
        max_scale=1.5,   # 2250 chars maximum
    )
)
```

### Custom Config

```python
# Для code-heavy документации
config = ChunkConfig(
    use_adaptive_sizing=True,
    adaptive_config=AdaptiveSizeConfig(
        base_size=2000,
        min_scale=0.7,   # 1400 chars minimum
        max_scale=1.8,   # 3600 chars maximum
        code_weight=0.6,  # Больший вес для кода
    )
)
```

---

## Риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Непредсказуемые размеры | Medium | Low | Document behavior |
| Over-optimization | Low | Low | Conservative defaults |

---

## Acceptance Criteria

- [ ] Code-heavy контент получает ≥ base_size
- [ ] Simple text получает ≤ base_size
- [ ] min/max scale соблюдаются
- [ ] Feature работает как optional
- [ ] Weights конфигурируются
- [ ] Retrieval quality улучшается
- [ ] Документация с примерами

---

## Примеры из тестового корпуса

Следующие файлы демонстрируют разную сложность контента и подходят для тестирования Adaptive Chunk Sizing:

### Code-Heavy файлы (должны получать большие чанки)

| Файл | Code Ratio | Ожидаемый scale |
|------|------------|---------------|
| [face_recognition.md](../../../tests/corpus/github_readmes/python/face_recognition.md) | 60% | 1.4-1.5x |
| [axios.md](../../../tests/corpus/github_readmes/javascript/axios.md) | 50% | 1.3-1.4x |
| [engineering_blogs_026.md](../../../tests/corpus/engineering_blogs/engineering_blogs_026.md) | 44% | 1.2-1.3x |
| [hugo.md](../../../tests/corpus/github_readmes/go/hugo.md) | 39% | 1.2x |
| [debug_logs_002.md](../../../tests/corpus/debug_logs/debug_logs_002.md) | 36% | 1.1-1.2x |

### Simple Text файлы (должны получать меньшие чанки)

| Файл | Code Ratio | Ожидаемый scale |
|------|------------|---------------|
| [unstructured_001.md](../../../tests/corpus/personal_notes/unstructured/unstructured_001.md) | 0% | 0.5-0.6x |
| [unstructured_004.md](../../../tests/corpus/personal_notes/unstructured/unstructured_004.md) | 0% | 0.5x |
| [unstructured_009.md](../../../tests/corpus/personal_notes/unstructured/unstructured_009.md) | 0% | 0.5-0.6x |
| [changelogs_004.md](../../../tests/corpus/changelogs/changelogs_004.md) | 0% | 0.6-0.7x |
| [kubernetes.md](../../../tests/corpus/github_readmes/go/kubernetes.md) | 6% | 0.6-0.7x |

### Mixed Content файлы (средние чанки)

| Файл | Code Ratio | Ожидаемый scale |
|------|------------|---------------|
| [mixed_content_004.md](../../../tests/corpus/mixed_content/mixed_content_004.md) | 12% | 0.8-1.0x |
| [mixed_content_005.md](../../../tests/corpus/mixed_content/mixed_content_005.md) | 11% | 0.8-1.0x |
| [research_notes_007.md](../../../tests/corpus/research_notes/research_notes_007.md) | 23% | 0.9-1.1x |
| [gin.md](../../../tests/corpus/github_readmes/go/gin.md) | 13% | 0.8-1.0x |
