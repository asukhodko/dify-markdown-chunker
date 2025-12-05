# Competitor Analysis Matrix

## Executive Summary

Проведён анализ 10 решений для markdown chunking. Ключевые findings:
- Большинство решений используют простое разделение по заголовкам или размеру
- Немногие сохраняют семантическую связность код-текст
- Обработка вложенных code blocks — слабое место почти всех решений
- markdown_chunker_v2 уже имеет преимущества в code-aware chunking

## Analyzed Solutions

### 1. LangChain MarkdownTextSplitter

**Source:** `langchain.text_splitter.MarkdownTextSplitter`

**Approach:**
- Рекурсивное разделение по markdown-специфичным разделителям
- Иерархия разделителей: `\n## `, `\n### `, `\n#### `, `\n- `, `\n\n`, `\n`, ` `
- Наследует от `RecursiveCharacterTextSplitter`

**Features:**
| Feature | Supported | Notes |
|---------|-----------|-------|
| Header-based splitting | ✅ | Primary method |
| Code block preservation | ⚠️ | Partial - may split large blocks |
| Table preservation | ❌ | No special handling |
| List preservation | ⚠️ | Splits by list items |
| Nested fencing | ❌ | Not supported |
| Metadata enrichment | ⚠️ | Basic (headers only via MarkdownHeaderTextSplitter) |
| Configurable chunk size | ✅ | chunk_size, chunk_overlap |
| Semantic boundaries | ❌ | Character-based, not semantic |

**Strengths:**
- Простота использования
- Хорошая интеграция с LangChain ecosystem
- MarkdownHeaderTextSplitter добавляет header metadata

**Weaknesses:**
- Может разрывать code blocks
- Нет понимания семантической связи код-текст
- Таблицы не обрабатываются специально
- Нет поддержки nested fencing

**Unique Features:** None significant

---

### 2. LlamaIndex MarkdownNodeParser

**Source:** `llama_index.core.node_parser.MarkdownNodeParser`

**Approach:**
- Парсинг markdown в AST-подобную структуру
- Разделение по секциям (headers)
- Сохранение иерархии документа

**Features:**
| Feature | Supported | Notes |
|---------|-----------|-------|
| Header-based splitting | ✅ | Primary method |
| Code block preservation | ✅ | Keeps blocks intact |
| Table preservation | ⚠️ | Basic support |
| List preservation | ⚠️ | Within sections |
| Nested fencing | ❌ | Not supported |
| Metadata enrichment | ✅ | Rich metadata (headers, relationships) |
| Configurable chunk size | ⚠️ | Limited control |
| Semantic boundaries | ⚠️ | Section-based |

**Strengths:**
- Хорошее сохранение структуры документа
- Rich metadata с иерархией заголовков
- Интеграция с LlamaIndex indexing

**Weaknesses:**
- Менее гибкая настройка размера чанков
- Большие секции не разбиваются оптимально
- Нет adaptive sizing

**Unique Features:**
- Hierarchical node relationships (parent/child)

---

### 3. Unstructured partition_md

**Source:** `unstructured.partition.md.partition_md`

**Approach:**
- Элемент-ориентированный парсинг
- Каждый элемент (paragraph, code, table) — отдельный объект
- Chunking через отдельный `chunk_elements()`

**Features:**
| Feature | Supported | Notes |
|---------|-----------|-------|
| Header-based splitting | ✅ | Element-based |
| Code block preservation | ✅ | As separate elements |
| Table preservation | ✅ | As separate elements |
| List preservation | ✅ | As separate elements |
| Nested fencing | ❌ | Not supported |
| Metadata enrichment | ✅ | Element type, coordinates |
| Configurable chunk size | ✅ | Via chunking strategies |
| Semantic boundaries | ⚠️ | Element boundaries |

**Strengths:**
- Отличное сохранение структурных элементов
- Множество chunking strategies (by_title, basic, etc.)
- Хорошая типизация элементов

**Weaknesses:**
- Может создавать слишком мелкие чанки
- Потеря контекста между элементами
- Сложный API

**Unique Features:**
- Element-level metadata (coordinates, type)
- Multiple chunking strategies

---

### 4. Haystack MarkdownToDocument

**Source:** `haystack.components.converters.MarkdownToDocument`

**Approach:**
- Конвертация markdown в Document objects
- Базовое разделение, фокус на pipeline integration

**Features:**
| Feature | Supported | Notes |
|---------|-----------|-------|
| Header-based splitting | ⚠️ | Via separate splitter |
| Code block preservation | ⚠️ | Basic |
| Table preservation | ⚠️ | Basic |
| List preservation | ⚠️ | Basic |
| Nested fencing | ❌ | Not supported |
| Metadata enrichment | ⚠️ | Basic |
| Configurable chunk size | ✅ | Via DocumentSplitter |
| Semantic boundaries | ❌ | Character-based |

**Strengths:**
- Хорошая интеграция с Haystack pipelines
- Простота использования

**Weaknesses:**
- Минимальная markdown-специфичная логика
- Требует дополнительных компонентов для качественного chunking

**Unique Features:** None significant

---

### 5. Semantic Kernel TextChunker

**Source:** `semantic_kernel.text.text_chunker`

**Approach:**
- Универсальный text chunker
- Markdown не является primary focus

**Features:**
| Feature | Supported | Notes |
|---------|-----------|-------|
| Header-based splitting | ❌ | Generic text splitting |
| Code block preservation | ❌ | No special handling |
| Table preservation | ❌ | No special handling |
| List preservation | ❌ | No special handling |
| Nested fencing | ❌ | Not supported |
| Metadata enrichment | ❌ | Minimal |
| Configurable chunk size | ✅ | Token-based |
| Semantic boundaries | ❌ | Token-based |

**Strengths:**
- Token-aware splitting (важно для LLM)
- Простота

**Weaknesses:**
- Не понимает markdown структуру
- Не подходит для markdown-специфичных задач

**Unique Features:**
- Token-based sizing (tiktoken integration)

---

### 6. txtai Textractor

**Source:** `txtai.pipeline.Textractor`

**Approach:**
- Extraction-focused, не chunking-focused
- Markdown через общий text pipeline

**Features:**
| Feature | Supported | Notes |
|---------|-----------|-------|
| Header-based splitting | ❌ | Not primary function |
| Code block preservation | ❌ | Generic text |
| Table preservation | ❌ | Generic text |
| List preservation | ❌ | Generic text |
| Nested fencing | ❌ | Not supported |
| Metadata enrichment | ⚠️ | Basic |
| Configurable chunk size | ⚠️ | Via separate components |
| Semantic boundaries | ❌ | Not focus |

**Strengths:**
- Хорошая интеграция с txtai ecosystem
- Semantic search capabilities

**Weaknesses:**
- Не специализирован на markdown
- Требует дополнительной обработки

**Unique Features:** None for markdown

---

### 7. Chonkie

**Source:** GitHub: `bhavnicksm/chonkie`

**Approach:**
- Специализированный chunker с multiple strategies
- Semantic chunking support

**Features:**
| Feature | Supported | Notes |
|---------|-----------|-------|
| Header-based splitting | ✅ | Via strategies |
| Code block preservation | ⚠️ | Depends on strategy |
| Table preservation | ⚠️ | Depends on strategy |
| List preservation | ⚠️ | Depends on strategy |
| Nested fencing | ❌ | Not documented |
| Metadata enrichment | ✅ | Good metadata |
| Configurable chunk size | ✅ | Multiple options |
| Semantic boundaries | ✅ | SemanticChunker |

**Strengths:**
- Multiple chunking strategies
- Semantic chunking с embeddings
- Active development

**Weaknesses:**
- Относительно новый проект
- Документация в развитии

**Unique Features:**
- SemanticChunker с embedding-based boundaries
- SDPMChunker (Semantic Double-Pass Merge)

---

### 8. DocArray

**Source:** `docarray.documents`

**Approach:**
- Document-oriented data structure
- Chunking через transformations

**Features:**
| Feature | Supported | Notes |
|---------|-----------|-------|
| Header-based splitting | ⚠️ | Via custom logic |
| Code block preservation | ❌ | No special handling |
| Table preservation | ❌ | No special handling |
| List preservation | ❌ | No special handling |
| Nested fencing | ❌ | Not supported |
| Metadata enrichment | ✅ | Rich document model |
| Configurable chunk size | ⚠️ | Custom implementation |
| Semantic boundaries | ❌ | Not built-in |

**Strengths:**
- Flexible document model
- Good for multimodal content

**Weaknesses:**
- Не специализирован на markdown chunking
- Требует custom implementation

**Unique Features:**
- Multimodal document support

---

### 9. MarkItDown (Microsoft)

**Source:** GitHub: `microsoft/markitdown`

**Approach:**
- Конвертация различных форматов В markdown
- Не chunking tool

**Features:**
| Feature | Supported | Notes |
|---------|-----------|-------|
| Header-based splitting | ❌ | Not a chunker |
| Code block preservation | N/A | Converter, not chunker |
| Table preservation | N/A | Converter, not chunker |
| List preservation | N/A | Converter, not chunker |
| Nested fencing | N/A | Converter, not chunker |
| Metadata enrichment | N/A | Converter, not chunker |
| Configurable chunk size | N/A | Converter, not chunker |
| Semantic boundaries | N/A | Converter, not chunker |

**Note:** Включён для полноты, но это converter, не chunker.

---

### 10. Custom RAG Implementations

**Sources:** Dify, PrivateGPT, LocalGPT, etc.

**Common Approaches:**
- Обычно используют LangChain или LlamaIndex под капотом
- Иногда custom regex-based splitting
- Редко — sophisticated markdown parsing

**Common Weaknesses:**
- Простое разделение по размеру
- Потеря структуры документа
- Нет code-context binding



## Comparison Matrix

| Feature | LangChain | LlamaIndex | Unstructured | Haystack | Semantic Kernel | txtai | Chonkie | DocArray | markdown_chunker_v2 |
|---------|-----------|------------|--------------|----------|-----------------|-------|---------|----------|---------------------|
| Header-based splitting | ✅ | ✅ | ✅ | ⚠️ | ❌ | ❌ | ✅ | ⚠️ | ✅ |
| Code block preservation | ⚠️ | ✅ | ✅ | ⚠️ | ❌ | ❌ | ⚠️ | ❌ | ✅ |
| Table preservation | ❌ | ⚠️ | ✅ | ⚠️ | ❌ | ❌ | ⚠️ | ❌ | ✅ |
| List preservation | ⚠️ | ⚠️ | ✅ | ⚠️ | ❌ | ❌ | ⚠️ | ❌ | ⚠️ |
| Nested fencing | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ⚠️ |
| Metadata enrichment | ⚠️ | ✅ | ✅ | ⚠️ | ❌ | ⚠️ | ✅ | ✅ | ✅ |
| Configurable size | ✅ | ⚠️ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ⚠️ | ✅ |
| Semantic boundaries | ❌ | ⚠️ | ⚠️ | ❌ | ❌ | ❌ | ✅ | ❌ | ⚠️ |
| Strategy selection | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |
| Code-context binding | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

**Legend:** ✅ Full support | ⚠️ Partial support | ❌ Not supported

## Unique Features by Competitor

| Solution | Unique Feature | Potential for markdown_chunker_v2 |
|----------|---------------|-----------------------------------|
| LangChain | MarkdownHeaderTextSplitter с header metadata | Already have header_path |
| LlamaIndex | Hierarchical node relationships | Consider parent-child chunk links |
| Unstructured | Element-level typing and coordinates | Consider element type metadata |
| Chonkie | SemanticChunker с embeddings | **HIGH PRIORITY** - semantic boundary detection |
| Chonkie | SDPMChunker (double-pass merge) | Consider multi-pass refinement |
| Semantic Kernel | Token-based sizing | Consider token-aware chunk sizing |

## Gap Analysis: markdown_chunker_v2 vs Competitors

### Areas Where We Lead
1. **Code-context binding** — уникальная возможность, нет у конкурентов
2. **Automatic strategy selection** — только Unstructured и Chonkie имеют подобное
3. **Table preservation** — лучше чем у большинства
4. **Configurable with sensible defaults** — баланс гибкости и простоты

### Areas for Improvement
1. **Semantic boundary detection** — Chonkie имеет embedding-based boundaries
2. **List handling** — Unstructured лучше сохраняет структуру списков
3. **Nested fencing** — никто не поддерживает хорошо, opportunity!
4. **Token-aware sizing** — Semantic Kernel имеет, важно для LLM
5. **Hierarchical chunks** — LlamaIndex имеет parent-child relationships

## Recommendations from Competitor Analysis

### High Priority
1. **Implement semantic boundary detection** (inspired by Chonkie)
   - Use sentence embeddings to detect topic shifts
   - Improve boundary quality significantly

2. **Restore and improve List Strategy** (inspired by Unstructured)
   - Better list structure preservation
   - List-context binding (list + explanation)

3. **Add nested fencing support** (unique opportunity)
   - No competitor handles this well
   - Important for documentation templates

### Medium Priority
4. **Add token-aware chunk sizing** (inspired by Semantic Kernel)
   - Important for LLM context windows
   - tiktoken integration

5. **Add hierarchical chunk relationships** (inspired by LlamaIndex)
   - Parent-child links between chunks
   - Better for hierarchical retrieval

### Low Priority
6. **Add element-level metadata** (inspired by Unstructured)
   - More detailed content typing
   - Position information

## Conclusion

markdown_chunker_v2 уже имеет конкурентные преимущества в:
- Code-aware chunking
- Automatic strategy selection
- Table preservation

Ключевые возможности для достижения "top-1" статуса:
1. Semantic boundary detection (embeddings)
2. Improved list handling
3. Nested fencing support (unique differentiator)
4. Token-aware sizing
