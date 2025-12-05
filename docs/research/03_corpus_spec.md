# Test Corpus Specification

## Overview

Спецификация тестового корпуса для оценки качества markdown chunking. Корпус включает 400+ документов различных типов для comprehensive testing.

## Corpus Structure

```
corpus/
├── technical_docs/           # 100 файлов
│   ├── kubernetes/          # 25 файлов
│   ├── docker/              # 25 файлов
│   ├── react/               # 25 файлов
│   └── aws/                 # 25 файлов
├── github_readmes/          # 100 файлов
│   ├── python/              # 25 файлов
│   ├── javascript/          # 25 файлов
│   ├── go/                  # 25 файлов
│   └── rust/                # 25 файлов
├── changelogs/              # 50 файлов
├── engineering_blogs/       # 50 файлов
├── personal_notes/          # 30 файлов
│   ├── unstructured/        # 10 файлов
│   ├── journals/            # 10 файлов
│   └── cheatsheets/         # 10 файлов
├── debug_logs/              # 20 файлов
├── nested_fencing/          # 20 файлов
├── research_notes/          # 20 файлов
└── mixed_content/           # 20 файлов
```

**Total: 410 documents**

## Category Specifications

### 1. Technical Documentation (100 files)

**Source:** Official documentation from popular projects

**Characteristics:**
- Well-structured with clear header hierarchy
- Mix of code examples and explanations
- Tables for API references
- Lists for features/options

**Sample Sources:**
| Project | URL | Files |
|---------|-----|-------|
| Kubernetes | kubernetes.io/docs | 25 |
| Docker | docs.docker.com | 25 |
| React | react.dev | 25 |
| AWS | docs.aws.amazon.com | 25 |

**Size Distribution:**
- Small (< 5KB): 20%
- Medium (5-50KB): 60%
- Large (> 50KB): 20%

---

### 2. GitHub READMEs (100 files)

**Source:** Top starred repositories by language

**Selection Criteria:**
- Stars > 10,000
- README > 1KB
- Contains code examples

**Sample Repositories:**
| Language | Examples |
|----------|----------|
| Python | tensorflow, pytorch, django, flask, requests |
| JavaScript | react, vue, angular, next.js, express |
| Go | kubernetes, docker, hugo, gin, cobra |
| Rust | rust, deno, ripgrep, alacritty, bat |

**Characteristics:**
- Badges and shields at top
- Installation instructions with code
- Usage examples
- Feature lists
- Contributing guidelines

---

### 3. Changelogs (50 files)

**Source:** Popular open-source projects

**Formats:**
- Keep a Changelog format (30 files)
- GitHub Releases format (10 files)
- Custom formats (10 files)

**Characteristics:**
- Version headers (## [1.0.0])
- Date stamps
- Categorized changes (Added, Changed, Fixed, Removed)
- Links to issues/PRs

**Sample Sources:**
- semantic-release projects
- Major frameworks (React, Vue, Angular)
- CLI tools (npm, yarn, pnpm)

---

### 4. Engineering Blogs (50 files)

**Source:** FAANG and top tech company blogs

**Sources:**
| Company | Blog |
|---------|------|
| Netflix | netflixtechblog.com |
| Uber | eng.uber.com |
| Airbnb | medium.com/airbnb-engineering |
| Stripe | stripe.com/blog/engineering |
| Cloudflare | blog.cloudflare.com |

**Characteristics:**
- Long-form content (2000-10000 words)
- Code examples in multiple languages
- Diagrams (often as images, sometimes Mermaid)
- Technical depth with explanations

---

### 5. Personal Notes (30 files)

**Source:** Synthetic/anonymized examples

#### 5.1 Unstructured Notes (10 files)
```markdown
# Example: Unstructured Note

Today I learned about async/await in Python.

The basic syntax is:
async def foo():
    await bar()

Need to remember: always use asyncio.run() at top level.

Also looked at threading vs multiprocessing. Threading for I/O bound,
multiprocessing for CPU bound tasks.

TODO: try this with the API client
```

**Characteristics:**
- No clear structure
- Mixed topics
- Incomplete sentences
- Personal abbreviations

#### 5.2 Engineering Journals (10 files)
```markdown
# 2024-01-15 Debug Session

## Problem
API returning 500 errors intermittently.

## Investigation
1. Checked logs - found timeout errors
2. Traced to database connection pool exhaustion
3. Root cause: connection leak in transaction handling

## Solution
```python
# Before (leaking)
conn = pool.get_connection()
cursor = conn.cursor()
cursor.execute(query)
# Missing: conn.close()

# After (fixed)
with pool.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute(query)
```

## Lessons Learned
- Always use context managers for resources
- Add connection pool monitoring
```

**Characteristics:**
- Date-based entries
- Problem-solution structure
- Code snippets with before/after
- Personal reflections

#### 5.3 Cheatsheets (10 files)
```markdown
# Git Cheatsheet

## Basic Commands
| Command | Description |
|---------|-------------|
| `git init` | Initialize repo |
| `git clone <url>` | Clone repo |
| `git add .` | Stage all changes |

## Branching
- `git branch` - list branches
- `git checkout -b <name>` - create and switch
- `git merge <branch>` - merge branch

## Advanced
### Interactive Rebase
```bash
git rebase -i HEAD~3
```
```

**Characteristics:**
- Dense information
- Tables and lists
- Code snippets
- Minimal prose

---

### 6. Debug Logs (20 files)

**Characteristics:**
- Multi-language code blocks
- Error messages and stack traces
- Step-by-step debugging
- Long code excerpts

**Example Structure:**
```markdown
# Debugging Memory Leak in Node.js App

## Symptoms
- Memory usage grows over time
- Eventually OOM kill

## Code Under Investigation

```javascript
// server.js
const express = require('express');
const app = express();

let cache = {};

app.get('/data/:id', (req, res) => {
    const id = req.params.id;
    if (!cache[id]) {
        cache[id] = fetchData(id); // Never cleaned up!
    }
    res.json(cache[id]);
});
```

## Heap Snapshot Analysis

```
Constructor          | Count | Size
---------------------|-------|--------
Object               | 50000 | 12MB
Array                | 30000 | 8MB
(closure)            | 20000 | 5MB
```

## Fix

```javascript
const LRU = require('lru-cache');
const cache = new LRU({ max: 1000 });
```
```

---

### 7. Nested Fencing (20 files)

**Purpose:** Test handling of documentation templates and meta-documentation

**Example:**
````markdown
# How to Write Documentation

## Code Examples

When documenting code, use fenced code blocks:

```markdown
Here's how to show a Python example:

```python
def hello():
    print("Hello, World!")
```

And here's JavaScript:

```javascript
function hello() {
    console.log("Hello, World!");
}
```
```

## Escaping

For showing markdown itself, use more backticks:

`````markdown
````markdown
```python
code here
```
````
`````
````

**Characteristics:**
- Triple, quadruple, quintuple backticks
- Tilde fencing (~~~)
- Mixed nesting levels
- Meta-documentation

---

### 8. Research Notes (20 files)

**Characteristics:**
- Literature references
- Hypothesis and conclusions
- Data and analysis
- Mixed content types

---

### 9. Mixed Content (20 files)

**Characteristics:**
- All content types in one document
- Realistic complexity
- Edge cases

## Size Distribution

| Size Category | Range | Count | Percentage |
|---------------|-------|-------|------------|
| Tiny | < 1KB | 20 | 5% |
| Small | 1-5KB | 80 | 20% |
| Medium | 5-20KB | 160 | 39% |
| Large | 20-100KB | 120 | 29% |
| Very Large | > 100KB | 30 | 7% |

## Content Characteristics Distribution

| Characteristic | High | Medium | Low |
|----------------|------|--------|-----|
| Code ratio | 100 | 150 | 160 |
| Table count | 80 | 120 | 210 |
| List ratio | 100 | 150 | 160 |
| Header depth | 150 | 180 | 80 |
| Nested fencing | 20 | 30 | 360 |

## Collection Instructions

### Automated Collection Script

```python
#!/usr/bin/env python3
"""
Corpus collection script for markdown chunker testing.
"""

import requests
import os
from pathlib import Path

GITHUB_API = "https://api.github.com"
CORPUS_DIR = Path("corpus")

def collect_github_readmes(language: str, count: int = 25):
    """Collect top README files for a language."""
    url = f"{GITHUB_API}/search/repositories"
    params = {
        "q": f"language:{language} stars:>10000",
        "sort": "stars",
        "per_page": count
    }
    # ... implementation
    
def collect_docs(project: str, docs_url: str):
    """Collect documentation from a project."""
    # ... implementation

if __name__ == "__main__":
    # Collect GitHub READMEs
    for lang in ["python", "javascript", "go", "rust"]:
        collect_github_readmes(lang)
    
    # Collect technical docs
    collect_docs("kubernetes", "https://kubernetes.io/docs/")
    # ... etc
```

### Manual Collection Guidelines

1. **Technical Docs:** Download from official documentation sites
2. **READMEs:** Use GitHub API or raw.githubusercontent.com
3. **Changelogs:** Look for CHANGELOG.md in repositories
4. **Blogs:** Save as markdown (use markdownify if needed)
5. **Personal Notes:** Create synthetic examples following templates

## Validation Checklist

- [ ] Total files ≥ 400
- [ ] All categories represented
- [ ] Size distribution matches spec
- [ ] Content characteristics varied
- [ ] No duplicate content
- [ ] All files valid markdown
- [ ] Metadata recorded for each file
