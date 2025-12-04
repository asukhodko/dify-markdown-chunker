# Архитектурный Аудит: Доменные Свойства

## Обзор

Формализованные доменные свойства системы чанкинга — это инварианты, которые должны выполняться независимо от реализации. Они служат основой для property-based тестирования и контрактом для редизайна.

## Критические свойства (MUST HAVE)

### PROP-1: No Content Loss

**Формулировка:** Для любого валидного markdown-документа, конкатенация содержимого всех чанков (за вычетом overlap) должна быть эквивалентна исходному документу.

```
∀ doc ∈ ValidMarkdown:
  concat(chunks) - overlaps ≡ doc
```

**Примечания:**
- "Эквивалентность" допускает нормализацию whitespace
- Overlap вычитается из начала каждого чанка кроме первого
- Preamble может дублироваться в метаданных

**Тест:**
```python
@given(markdown_documents())
def test_no_content_loss(doc):
    chunks = chunker.chunk(doc)
    reconstructed = reconstruct_without_overlap(chunks)
    assert normalize(reconstructed) == normalize(doc)
```

### PROP-2: Chunk Size Bounds

**Формулировка:** Для любого чанка, его размер должен быть ≤ max_chunk_size, ИЛИ чанк должен быть помечен как oversize.

```
∀ chunk ∈ Chunks:
  len(chunk.content) ≤ config.max_chunk_size 
  ∨ chunk.metadata["allow_oversize"] = True
```

**Примечания:**
- Oversize допускается только для атомарных элементов (code blocks, tables)
- Oversize чанки должны иметь причину в метаданных

**Тест:**
```python
@given(markdown_documents(), chunk_configs())
def test_size_bounds(doc, config):
    chunks = chunker.chunk(doc, config)
    for chunk in chunks:
        if len(chunk.content) > config.max_chunk_size:
            assert chunk.metadata.get("allow_oversize") == True
            assert chunk.metadata.get("oversize_reason") is not None
```

### PROP-3: Monotonic Ordering

**Формулировка:** Для любой последовательности чанков, значения start_line должны быть монотонно неубывающими.

```
∀ i < j:
  chunks[i].start_line ≤ chunks[j].start_line
```

**Примечания:**
- Допускается равенство (для чанков из одной строки)
- Overlap не нарушает порядок

**Тест:**
```python
@given(markdown_documents())
def test_monotonic_ordering(doc):
    chunks = chunker.chunk(doc)
    for i in range(len(chunks) - 1):
        assert chunks[i].start_line <= chunks[i+1].start_line
```

### PROP-4: No Empty Chunks

**Формулировка:** Для любого чанка, его содержимое не должно быть пустым или состоять только из whitespace.

```
∀ chunk ∈ Chunks:
  chunk.content.strip() ≠ ""
```

**Тест:**
```python
@given(markdown_documents())
def test_no_empty_chunks(doc):
    chunks = chunker.chunk(doc)
    for chunk in chunks:
        assert chunk.content.strip(), f"Empty chunk at lines {chunk.start_line}-{chunk.end_line}"
```

### PROP-5: Valid Line Numbers

**Формулировка:** Для любого чанка, start_line ≥ 1 и end_line ≥ start_line.

```
∀ chunk ∈ Chunks:
  chunk.start_line ≥ 1 ∧ chunk.end_line ≥ chunk.start_line
```

**Примечания:**
- Нумерация строк 1-based
- Валидация в конструкторе Chunk

**Тест:**
```python
@given(markdown_documents())
def test_valid_line_numbers(doc):
    chunks = chunker.chunk(doc)
    for chunk in chunks:
        assert chunk.start_line >= 1
        assert chunk.end_line >= chunk.start_line
```

## Важные свойства (SHOULD HAVE)

### PROP-6: Code Block Integrity

**Формулировка:** Для любого code block в исходном документе, он должен появиться целиком в ровно одном чанке.

```
∀ code_block ∈ doc.code_blocks:
  ∃! chunk ∈ Chunks: code_block ⊆ chunk.content
```

**Примечания:**
- Code block определяется как текст между ``` маркерами
- Допускается oversize для больших блоков

**Тест:**
```python
@given(markdown_with_code_blocks())
def test_code_block_integrity(doc):
    code_blocks = extract_code_blocks(doc)
    chunks = chunker.chunk(doc)
    
    for block in code_blocks:
        containing_chunks = [c for c in chunks if block in c.content]
        assert len(containing_chunks) == 1, f"Code block split across chunks"
```

### PROP-7: Table Integrity

**Формулировка:** Для любой таблицы в исходном документе, она должна появиться целиком в ровно одном чанке.

```
∀ table ∈ doc.tables:
  ∃! chunk ∈ Chunks: table ⊆ chunk.content
```

**Тест:**
```python
@given(markdown_with_tables())
def test_table_integrity(doc):
    tables = extract_tables(doc)
    chunks = chunker.chunk(doc)
    
    for table in tables:
        containing_chunks = [c for c in chunks if table in c.content]
        assert len(containing_chunks) == 1, f"Table split across chunks"
```

### PROP-8: Serialization Round-Trip

**Формулировка:** Для любого ChunkingResult, сериализация в dict и обратно должна давать эквивалентный результат.

```
∀ result ∈ ChunkingResult:
  ChunkingResult.from_dict(result.to_dict()) ≡ result
```

**Тест:**
```python
@given(chunking_results())
def test_serialization_roundtrip(result):
    serialized = result.to_dict()
    deserialized = ChunkingResult.from_dict(serialized)
    
    assert len(deserialized.chunks) == len(result.chunks)
    for orig, deser in zip(result.chunks, deserialized.chunks):
        assert orig.content == deser.content
        assert orig.start_line == deser.start_line
        assert orig.end_line == deser.end_line
```

## Желательные свойства (NICE TO HAVE)

### PROP-9: Idempotence

**Формулировка:** Повторный чанкинг того же документа с той же конфигурацией должен давать идентичный результат.

```
∀ doc, config:
  chunk(doc, config) ≡ chunk(doc, config)
```

**Тест:**
```python
@given(markdown_documents(), chunk_configs())
def test_idempotence(doc, config):
    result1 = chunker.chunk(doc, config)
    result2 = chunker.chunk(doc, config)
    
    assert len(result1) == len(result2)
    for c1, c2 in zip(result1, result2):
        assert c1.content == c2.content
```

### PROP-10: Header Path Correctness

**Формулировка:** Для любого чанка с header_path, путь должен соответствовать реальной иерархии заголовков в документе.

```
∀ chunk with header_path:
  header_path reflects actual document hierarchy at chunk.start_line
```

**Тест:**
```python
@given(markdown_with_headers())
def test_header_path_correctness(doc):
    chunks = chunker.chunk(doc)
    headers = extract_header_hierarchy(doc)
    
    for chunk in chunks:
        if "header_path" in chunk.metadata:
            expected_path = get_header_path_at_line(headers, chunk.start_line)
            assert chunk.metadata["header_path"] == expected_path
```

## Матрица свойств

| # | Свойство | Критичность | Сложность теста | Покрытие |
|---|----------|-------------|-----------------|----------|
| 1 | No Content Loss | CRITICAL | Medium | ✓ |
| 2 | Size Bounds | CRITICAL | Low | ✓ |
| 3 | Monotonic Order | CRITICAL | Low | ✓ |
| 4 | No Empty Chunks | CRITICAL | Low | ✓ |
| 5 | Valid Line Numbers | CRITICAL | Low | ✓ |
| 6 | Code Block Integrity | HIGH | Medium | ✓ |
| 7 | Table Integrity | HIGH | Medium | ✓ |
| 8 | Round-Trip | HIGH | Low | ✓ |
| 9 | Idempotence | MEDIUM | Low | ✓ |
| 10 | Header Path | MEDIUM | High | ✓ |

## Контракт для редизайна

```python
@dataclass
class ChunkingContract:
    """
    Контракт, который должна выполнять любая реализация чанкера.
    Используется для валидации редизайна.
    """
    
    # CRITICAL — нарушение = баг
    no_content_loss: bool = True      # PROP-1
    size_bounds: bool = True          # PROP-2
    monotonic_order: bool = True      # PROP-3
    no_empty_chunks: bool = True      # PROP-4
    valid_line_numbers: bool = True   # PROP-5
    
    # HIGH — нарушение = серьёзная проблема
    code_block_integrity: bool = True # PROP-6
    table_integrity: bool = True      # PROP-7
    serialization_roundtrip: bool = True  # PROP-8
    
    # MEDIUM — нарушение = нежелательно
    idempotence: bool = True          # PROP-9
    header_path_correctness: bool = True  # PROP-10
```

## Генераторы для тестов

```python
from hypothesis import strategies as st

@st.composite
def markdown_documents(draw):
    """Генератор произвольных markdown документов."""
    sections = draw(st.lists(markdown_sections(), min_size=0, max_size=10))
    return "\n\n".join(sections)

@st.composite
def markdown_sections(draw):
    """Генератор секций markdown."""
    section_type = draw(st.sampled_from([
        "header", "paragraph", "code_block", "list", "table"
    ]))
    
    if section_type == "header":
        level = draw(st.integers(min_value=1, max_value=6))
        text = draw(st.text(min_size=1, max_size=50))
        return "#" * level + " " + text
    elif section_type == "code_block":
        lang = draw(st.sampled_from(["python", "javascript", "", "rust"]))
        code = draw(st.text(min_size=1, max_size=500))
        return f"```{lang}\n{code}\n```"
    # ... и т.д.

@st.composite
def chunk_configs(draw):
    """Генератор конфигураций."""
    max_size = draw(st.integers(min_value=100, max_value=10000))
    min_size = draw(st.integers(min_value=10, max_value=max_size // 2))
    return ChunkConfig(max_chunk_size=max_size, min_chunk_size=min_size)
```
