# Advanced Features Research

## Executive Summary

Исследование продвинутых возможностей для дифференциации markdown_chunker_v2 и достижения статуса "top-1 candidate". Оценены feasibility, impact и effort для каждой возможности.

**Top 5 рекомендуемых возможностей:**
1. Semantic Boundary Detection (embeddings)
2. Nested Fencing Support (unique differentiator)
3. Smart List Strategy (restore + improve)
4. Token-Aware Sizing
5. Hierarchical Chunking

---

## Category 1: Semantic Analysis

### 1.1 Semantic Boundary Detection

**Description:** Использование sentence embeddings для определения оптимальных границ чанков на основе семантических переходов.

**How It Works:**
```python
from sentence_transformers import SentenceTransformer
import numpy as np

def find_semantic_boundaries(text: str, threshold: float = 0.3) -> list[int]:
    """
    Find semantic boundaries using embedding similarity.
    
    Returns list of paragraph indices where semantic shift occurs.
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    paragraphs = text.split('\n\n')
    
    if len(paragraphs) < 2:
        return []
    
    embeddings = model.encode(paragraphs)
    boundaries = []
    
    for i in range(len(embeddings) - 1):
        similarity = cosine_similarity(embeddings[i], embeddings[i+1])
        if similarity < threshold:
            boundaries.append(i + 1)
    
    return boundaries
```

**Pros:**
- Significantly improves semantic coherence
- Language-agnostic
- Adapts to content automatically

**Cons:**
- Requires ML model (dependency)
- Slower than rule-based
- Model size (~90MB for MiniLM)

**Feasibility:** High — well-established technique
**Impact:** Very High — major quality improvement
**Effort:** Medium (M)
**Priority:** HIGH

---

### 1.2 Topic Modeling (LDA/BERTopic)

**Description:** Использование topic modeling для группировки контента по темам.

**How It Works:**
```python
from bertopic import BERTopic

def group_by_topic(paragraphs: list[str]) -> dict[int, list[int]]:
    """Group paragraphs by topic."""
    model = BERTopic()
    topics, _ = model.fit_transform(paragraphs)
    
    topic_groups = {}
    for i, topic in enumerate(topics):
        if topic not in topic_groups:
            topic_groups[topic] = []
        topic_groups[topic].append(i)
    
    return topic_groups
```

**Pros:**
- Can identify thematic sections
- Useful for long documents

**Cons:**
- Heavy dependency (BERTopic)
- Overkill for most documents
- Slow for real-time use

**Feasibility:** Medium — complex integration
**Impact:** Medium — niche use case
**Effort:** Large (L)
**Priority:** LOW

---

### 1.3 Named Entity Recognition (NER)

**Description:** Использование NER для группировки контента по сущностям (API names, classes, etc.).

**How It Works:**
```python
import spacy

def extract_entities(text: str) -> dict[str, list[str]]:
    """Extract named entities from text."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    
    entities = {}
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        entities[ent.label_].append(ent.text)
    
    return entities
```

**Pros:**
- Can identify important entities
- Useful for metadata enrichment

**Cons:**
- Standard NER not great for code entities
- Would need custom model for technical content
- Heavy dependency

**Feasibility:** Low — needs custom training
**Impact:** Low — limited use case
**Effort:** Extra Large (XL)
**Priority:** LOW

---

## Category 2: Context-Aware Chunking

### 2.1 Adaptive Chunk Sizing

**Description:** Автоматическая настройка размера чанка на основе сложности контента.

**How It Works:**
```python
def calculate_optimal_size(content: str, base_size: int = 1500) -> int:
    """
    Calculate optimal chunk size based on content complexity.
    
    Complex content (code, tables) -> larger chunks
    Simple text -> smaller chunks
    """
    complexity = calculate_complexity(content)
    
    # Scale factor: 0.5 to 1.5
    scale = 0.5 + complexity  # complexity is 0-1
    
    return int(base_size * scale)

def calculate_complexity(content: str) -> float:
    """Calculate content complexity (0-1)."""
    factors = {
        'code_ratio': count_code_chars(content) / len(content),
        'table_ratio': count_table_chars(content) / len(content),
        'list_ratio': count_list_chars(content) / len(content),
        'avg_sentence_length': avg_sentence_length(content) / 100,
    }
    
    weights = {'code_ratio': 0.4, 'table_ratio': 0.3, 
               'list_ratio': 0.2, 'avg_sentence_length': 0.1}
    
    return sum(factors[k] * weights[k] for k in factors)
```

**Pros:**
- Better size optimization
- Adapts to content automatically
- No external dependencies

**Cons:**
- More complex logic
- Harder to predict chunk sizes
- May need tuning

**Feasibility:** High — straightforward implementation
**Impact:** Medium — incremental improvement
**Effort:** Small (S)
**Priority:** MEDIUM

---

### 2.2 Hierarchical Chunking

**Description:** Создание иерархии чанков (parent-child) для многоуровневого retrieval.

**How It Works:**
```python
@dataclass
class HierarchicalChunk:
    content: str
    level: int  # 0 = document, 1 = section, 2 = subsection, etc.
    parent_id: Optional[str]
    children_ids: list[str]
    metadata: dict

def create_hierarchy(text: str, headers: list[Header]) -> list[HierarchicalChunk]:
    """
    Create hierarchical chunk structure.
    
    Level 0: Full document summary
    Level 1: Section chunks (H1, H2)
    Level 2: Subsection chunks (H3, H4)
    Level 3: Paragraph chunks
    """
    chunks = []
    
    # Level 0: Document summary
    doc_chunk = HierarchicalChunk(
        content=generate_summary(text),
        level=0,
        parent_id=None,
        children_ids=[],
        metadata={'type': 'document'}
    )
    chunks.append(doc_chunk)
    
    # Level 1-3: Section hierarchy
    # ... implementation
    
    return chunks
```

**Pros:**
- Enables multi-level retrieval
- Better for complex documents
- Preserves document structure

**Cons:**
- More complex data model
- Requires index support
- May increase storage

**Feasibility:** Medium — needs architecture changes
**Impact:** High — enables new use cases
**Effort:** Large (L)
**Priority:** MEDIUM

---

### 2.3 Cross-Reference Preservation

**Description:** Сохранение внутренних ссылок между чанками.

**How It Works:**
```python
def extract_references(text: str) -> list[Reference]:
    """Extract internal references (links, anchors)."""
    # Find markdown links
    link_pattern = r'\[([^\]]+)\]\(#([^\)]+)\)'
    links = re.findall(link_pattern, text)
    
    # Find anchor definitions
    anchor_pattern = r'^#{1,6}\s+(.+?)(?:\s+\{#([^\}]+)\})?$'
    anchors = re.findall(anchor_pattern, text, re.MULTILINE)
    
    return [Reference(text=l[0], target=l[1]) for l in links]

def preserve_references(chunks: list[Chunk]) -> list[Chunk]:
    """Add reference metadata to chunks."""
    for chunk in chunks:
        refs = extract_references(chunk.content)
        chunk.metadata['references'] = refs
        chunk.metadata['defines_anchors'] = extract_anchors(chunk.content)
    
    return chunks
```

**Pros:**
- Maintains document navigation
- Useful for documentation
- Low overhead

**Cons:**
- Limited use case
- Requires index support for resolution

**Feasibility:** High — simple implementation
**Impact:** Low — niche feature
**Effort:** Small (S)
**Priority:** LOW

---

### 2.4 Code-Context Binding (Enhanced)

**Description:** Улучшенная привязка кода к объяснениям.

**Current State:** Already implemented in CodeAware strategy

**Enhancements:**
```python
def enhanced_code_context_binding(
    code_block: FencedBlock,
    surrounding_text: str,
    config: ChunkConfig
) -> str:
    """
    Enhanced code-context binding.
    
    1. Include preceding explanation (up to N chars)
    2. Include following explanation (up to N chars)
    3. Include related code blocks (same function/class)
    4. Add semantic summary if context is large
    """
    context_before = extract_context_before(code_block, surrounding_text)
    context_after = extract_context_after(code_block, surrounding_text)
    
    # Check if code references other code blocks
    related_blocks = find_related_code_blocks(code_block, surrounding_text)
    
    return combine_with_context(
        code_block,
        context_before,
        context_after,
        related_blocks
    )
```

**Feasibility:** High — extends existing feature
**Impact:** Medium — incremental improvement
**Effort:** Small (S)
**Priority:** MEDIUM

---

## Category 3: Specialized Handlers

### 3.1 Nested Fencing Support — UNIQUE DIFFERENTIATOR

**Description:** Поддержка вложенных code blocks (четверные бэктики, тильды).

**Problem:**
```markdown
Here's how to document code:

````markdown
```python
def hello():
    print("Hello")
```
````
```

Current chunkers break this. We can be the first to handle it correctly.

**Implementation:**
```python
def extract_nested_code_blocks(text: str) -> list[FencedBlock]:
    """
    Extract code blocks with proper nesting support.
    
    Handles:
    - Triple backticks (```)
    - Quadruple backticks (````)
    - Quintuple backticks (`````)
    - Tilde fencing (~~~, ~~~~)
    """
    blocks = []
    lines = text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for fence start (3+ backticks or tildes)
        fence_match = re.match(r'^(`{3,}|~{3,})(\w*)', line)
        if fence_match:
            fence = fence_match.group(1)
            fence_char = fence[0]
            fence_len = len(fence)
            language = fence_match.group(2)
            
            # Find matching close fence (same char, same or more length)
            content_lines = []
            i += 1
            while i < len(lines):
                close_match = re.match(rf'^{fence_char}{{{fence_len},}}$', lines[i])
                if close_match:
                    break
                content_lines.append(lines[i])
                i += 1
            
            blocks.append(FencedBlock(
                content='\n'.join(content_lines),
                language=language,
                fence_type=fence_char,
                fence_length=fence_len
            ))
        
        i += 1
    
    return blocks
```

**Pros:**
- Unique differentiator — no competitor handles this well
- Critical for documentation templates
- Relatively simple to implement

**Cons:**
- Edge cases can be tricky
- Need thorough testing

**Feasibility:** High — well-defined problem
**Impact:** High — unique feature
**Effort:** Medium (M)
**Priority:** HIGH

---

### 3.2 LaTeX Formula Handling

**Description:** Правильная обработка математических формул.

**Patterns to Handle:**
- Inline: `$E = mc^2$`
- Display: `$$\int_0^\infty e^{-x^2} dx$$`
- Environments: `\begin{equation}...\end{equation}`

**Implementation:**
```python
def extract_latex_blocks(text: str) -> list[LatexBlock]:
    """Extract LaTeX formulas as atomic blocks."""
    blocks = []
    
    # Display math ($$...$$)
    display_pattern = r'\$\$(.+?)\$\$'
    for match in re.finditer(display_pattern, text, re.DOTALL):
        blocks.append(LatexBlock(
            content=match.group(0),
            type='display',
            start=match.start(),
            end=match.end()
        ))
    
    # Equation environments
    env_pattern = r'\\begin\{(equation|align|gather)\}(.+?)\\end\{\1\}'
    for match in re.finditer(env_pattern, text, re.DOTALL):
        blocks.append(LatexBlock(
            content=match.group(0),
            type='environment',
            start=match.start(),
            end=match.end()
        ))
    
    return blocks
```

**Feasibility:** High — regex-based
**Impact:** Medium — niche but important
**Effort:** Small (S)
**Priority:** MEDIUM

---

### 3.3 Diagram Support (Mermaid/PlantUML)

**Description:** Распознавание и сохранение диаграмм.

**Implementation:**
```python
def extract_diagrams(text: str) -> list[DiagramBlock]:
    """Extract diagram blocks."""
    diagrams = []
    
    # Mermaid
    mermaid_pattern = r'```mermaid\n(.+?)\n```'
    for match in re.finditer(mermaid_pattern, text, re.DOTALL):
        diagrams.append(DiagramBlock(
            content=match.group(0),
            type='mermaid',
            start=match.start(),
            end=match.end()
        ))
    
    # PlantUML
    plantuml_pattern = r'```plantuml\n(.+?)\n```'
    # ... similar
    
    return diagrams
```

**Feasibility:** High — already handled as code blocks
**Impact:** Low — already works via code block handling
**Effort:** Small (S)
**Priority:** LOW

---

### 3.4 Tables with Embedded Code

**Description:** Специальная обработка таблиц с кодом в ячейках.

**Example:**
```markdown
| Function | Example |
|----------|---------|
| `map` | `[1,2,3].map(x => x*2)` |
| `filter` | `[1,2,3].filter(x => x>1)` |
```

**Implementation:**
```python
def handle_code_tables(table: TableBlock) -> TableBlock:
    """
    Handle tables with code in cells.
    
    Ensures inline code is preserved and table stays intact.
    """
    # Tables are already atomic in CodeAware
    # Just need to ensure inline code backticks don't confuse parser
    
    table.metadata['has_code'] = '`' in table.content
    return table
```

**Feasibility:** High — minor enhancement
**Impact:** Low — already mostly works
**Effort:** Small (S)
**Priority:** LOW

---

## Category 4: Performance & Integration

### 4.1 Token-Aware Sizing

**Description:** Размер чанков на основе токенов (для LLM context windows).

**Implementation:**
```python
import tiktoken

def chunk_by_tokens(
    text: str,
    max_tokens: int = 512,
    model: str = "gpt-4"
) -> list[str]:
    """
    Chunk text by token count.
    
    Ensures chunks fit within LLM context windows.
    """
    encoding = tiktoken.encoding_for_model(model)
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for paragraph in text.split('\n\n'):
        para_tokens = len(encoding.encode(paragraph))
        
        if current_tokens + para_tokens > max_tokens:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            current_chunk = [paragraph]
            current_tokens = para_tokens
        else:
            current_chunk.append(paragraph)
            current_tokens += para_tokens
    
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks
```

**Pros:**
- Precise sizing for LLMs
- Prevents context overflow
- Industry standard approach

**Cons:**
- Requires tiktoken dependency
- Model-specific encoding

**Feasibility:** High — well-established
**Impact:** High — important for LLM use
**Effort:** Small (S)
**Priority:** HIGH

---

### 4.2 Streaming Processing

**Description:** Обработка больших файлов потоково.

**Implementation:**
```python
def chunk_streaming(
    file_path: str,
    config: ChunkConfig
) -> Iterator[Chunk]:
    """
    Stream chunks from large file.
    
    Memory-efficient for files > 10MB.
    """
    with open(file_path, 'r') as f:
        buffer = []
        buffer_size = 0
        
        for line in f:
            buffer.append(line)
            buffer_size += len(line)
            
            if buffer_size >= config.max_chunk_size * 2:
                # Process buffer
                text = ''.join(buffer)
                for chunk in process_buffer(text, config):
                    yield chunk
                
                # Keep overlap
                buffer = buffer[-10:]  # Keep last 10 lines
                buffer_size = sum(len(l) for l in buffer)
```

**Feasibility:** Medium — needs architecture changes
**Impact:** Medium — niche use case
**Effort:** Medium (M)
**Priority:** LOW

---

## Feature Priority Matrix

| Feature | Feasibility | Impact | Effort | Priority | Unique? |
|---------|-------------|--------|--------|----------|---------|
| Semantic Boundary Detection | High | Very High | M | HIGH | No |
| Nested Fencing Support | High | High | M | HIGH | **YES** |
| Smart List Strategy | High | High | M | HIGH | Partial |
| Token-Aware Sizing | High | High | S | HIGH | No |
| Adaptive Chunk Sizing | High | Medium | S | MEDIUM | No |
| Hierarchical Chunking | Medium | High | L | MEDIUM | No |
| LaTeX Formula Handling | High | Medium | S | MEDIUM | No |
| Enhanced Code-Context | High | Medium | S | MEDIUM | No |
| Topic Modeling | Medium | Medium | L | LOW | No |
| Cross-Reference Preservation | High | Low | S | LOW | No |
| Streaming Processing | Medium | Medium | M | LOW | No |
| NER-based Grouping | Low | Low | XL | LOW | No |

---

## Unique Differentiators

### 1. Nested Fencing Support (UNIQUE)
No competitor handles this correctly. Critical for documentation templates.

### 2. Smart List Strategy (PARTIAL)
Unstructured has element-based lists, but no semantic grouping.

### 3. Code-Context Binding (UNIQUE)
No competitor explicitly binds code to explanations.

### 4. Automatic Strategy Selection (PARTIAL)
Only Unstructured and Chonkie have similar features.

---

## Implementation Roadmap

### Phase 1 (Month 1-2): Core Improvements
1. Restore Smart List Strategy
2. Add Nested Fencing Support
3. Add Token-Aware Sizing

### Phase 2 (Month 3-4): Semantic Features
4. Implement Semantic Boundary Detection
5. Add Adaptive Chunk Sizing
6. Enhance Code-Context Binding

### Phase 3 (Month 5-6): Advanced Features
7. Add Hierarchical Chunking
8. Add LaTeX Formula Handling
9. Performance optimizations

---

## Conclusion

Для достижения статуса "top-1 candidate" рекомендуется фокус на:

1. **Nested Fencing Support** — уникальный дифференциатор
2. **Smart List Strategy** — восстановление критичной функциональности
3. **Semantic Boundary Detection** — значительное улучшение качества
4. **Token-Aware Sizing** — важно для LLM интеграции

Эти 4 возможности дадут наибольший impact при разумных затратах на реализацию.
