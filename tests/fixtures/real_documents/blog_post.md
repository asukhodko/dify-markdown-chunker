# Building a Production-Ready RAG System: Lessons Learned

Author: Jane Developer
Date: November 16, 2025
Tags: RAG, LLM, Python, Production

## Introduction

After six months of building and deploying a production RAG (Retrieval-Augmented Generation) system, I've learned valuable lessons about what works and what doesn't. This post shares practical insights from real-world experience.

## The Challenge

Our team needed to build a system that could answer questions about our extensive technical documentation (over 500 documents, 50MB of markdown). The requirements were clear:

- Response time under 2 seconds
- Accurate answers with source citations
- Handle 1000+ concurrent users
- Cost-effective (under $500/month)

## Architecture Overview

We settled on a three-tier architecture:

```
User Query → Vector Search → LLM Generation → Response
     ↓            ↓              ↓
  Embedding    Pinecone      GPT-4
```

### Component Selection

After evaluating multiple options, we chose:

1. **Embedding Model**: OpenAI text-embedding-ada-002
   - Pros: High quality, fast, well-supported
   - Cons: Cost ($0.0001 per 1K tokens)

2. **Vector Database**: Pinecone
   - Pros: Managed service, excellent performance
   - Cons: $70/month minimum

3. **LLM**: GPT-4
   - Pros: Best quality answers
   - Cons: Expensive ($0.03 per 1K tokens)

## The Chunking Problem

One of the biggest challenges was document chunking. We tried three approaches:

### Approach 1: Fixed-Size Chunks (Failed)

```python
def chunk_fixed(text, size=1000):
    return [text[i:i+size] for i in range(0, len(text), size)]
```

**Problems:**
- Split code blocks mid-function
- Broke tables
- Lost context at boundaries

### Approach 2: Sentence-Based (Better)

```python
import nltk

def chunk_sentences(text, max_sentences=10):
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current = []
    
    for sent in sentences:
        current.append(sent)
        if len(current) >= max_sentences:
            chunks.append(' '.join(current))
            current = []
    
    if current:
        chunks.append(' '.join(current))
    
    return chunks
```

**Problems:**
- Still broke code blocks
- Didn't respect markdown structure
- Lost header context

### Approach 3: Semantic Chunking (Winner!)

We finally adopted a semantic chunking library that:
- Respects markdown structure
- Preserves code blocks
- Maintains header hierarchy
- Adds overlap for context

```python
from markdown_chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig

config = ChunkConfig.for_dify_rag()
chunker = MarkdownChunker(config)

chunks = chunker.chunk(documentation)
```

**Results:**
- 95% answer accuracy (up from 70%)
- Zero broken code examples
- Better source attribution

## Performance Optimization

### Initial Performance

- Average query time: 4.2 seconds
- P95: 8.5 seconds
- Cost per query: $0.08

### Optimizations Applied

1. **Caching**: Redis cache for common queries
   ```python
   import redis
   
   cache = redis.Redis(host='localhost', port=6379)
   
   def get_answer(query):
       cached = cache.get(query)
       if cached:
           return cached
       
       answer = generate_answer(query)
       cache.setex(query, 3600, answer)  # 1 hour TTL
       return answer
   ```

2. **Batch Processing**: Process multiple embeddings at once
   ```python
   # Before: One at a time
   embeddings = [embed(chunk) for chunk in chunks]
   
   # After: Batch of 100
   embeddings = embed_batch(chunks, batch_size=100)
   ```

3. **Async Operations**: Use asyncio for parallel requests
   ```python
   import asyncio
   
   async def process_query(query):
       embedding_task = asyncio.create_task(get_embedding(query))
       search_task = asyncio.create_task(vector_search(await embedding_task))
       results = await search_task
       return await generate_answer(results)
   ```

### Final Performance

- Average query time: 1.8 seconds (57% improvement)
- P95: 3.2 seconds (62% improvement)
- Cost per query: $0.03 (62% reduction)

## Lessons Learned

### 1. Chunking Matters More Than You Think

Don't underestimate the importance of good chunking. It's the foundation of your RAG system. Bad chunks = bad answers, no matter how good your LLM is.

### 2. Overlap Is Essential

Add 10-20% overlap between chunks to maintain context. This single change improved our accuracy by 15%.

### 3. Monitor Everything

Track these metrics:
- Query latency (p50, p95, p99)
- Embedding cost
- LLM cost
- Cache hit rate
- Answer accuracy

### 4. Start Simple, Optimize Later

We spent 2 weeks on premature optimization. Should have launched with a simple solution and optimized based on real usage data.

### 5. Test With Real Users

Our internal testing showed 90% accuracy. Real users? 70%. Always test with actual users before claiming success.

## Cost Breakdown

Monthly costs for 10,000 queries:

| Component | Cost | Percentage |
|-----------|------|------------|
| Pinecone | $70 | 35% |
| OpenAI Embeddings | $50 | 25% |
| GPT-4 | $60 | 30% |
| Infrastructure | $20 | 10% |
| **Total** | **$200** | **100%** |

## Future Improvements

We're planning several enhancements:

1. **Fine-tuned Embeddings**: Train custom embedding model on our domain
2. **Hybrid Search**: Combine vector search with keyword search
3. **Query Rewriting**: Improve query understanding
4. **Multi-modal Support**: Add support for images and diagrams
5. **Streaming Responses**: Stream LLM output for better UX

## Conclusion

Building a production RAG system is challenging but rewarding. The key is to:

- Invest time in proper document chunking
- Monitor and optimize continuously
- Test with real users early
- Start simple and iterate

Our system now handles 1000+ queries per day with 95% user satisfaction. The journey from 70% to 95% accuracy taught us that details matter, especially in chunking and retrieval.

## Resources

- [Our Open Source Chunking Library](https://github.com/example/markdown-chunker)
- [RAG Best Practices Guide](https://example.com/rag-guide)
- [Vector Database Comparison](https://example.com/vector-db-comparison)

## Questions?

Feel free to reach out:
- Twitter: @janedev
- Email: jane@example.com
- LinkedIn: linkedin.com/in/janedev

---

*This post is part of our "Production ML" series. Subscribe to get notified of new posts.*
