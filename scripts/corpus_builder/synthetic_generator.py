"""Synthetic document generator for all categories."""

import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from .base import BaseGenerator, CollectionResult, DocumentMetadata


class SyntheticGenerator(BaseGenerator):
    """Generator for synthetic markdown documents."""

    def __init__(self, output_dir: Path, category: str, subcategory: str = None):
        super().__init__(output_dir)
        self.category = category
        self.subcategory = subcategory

    def generate(self, count: int) -> List[CollectionResult]:
        """Generate synthetic documents."""
        results = []
        
        print(f"Generating {count} {self.category} documents...")
        
        for i in range(count):
            try:
                if self.category == "personal_notes":
                    if self.subcategory == "unstructured":
                        content = self._generate_unstructured_note(i)
                    elif self.subcategory == "journals":
                        content = self._generate_journal(i)
                    elif self.subcategory == "cheatsheets":
                        content = self._generate_cheatsheet(i)
                    else:
                        content = self._generate_unstructured_note(i)
                        
                elif self.category == "debug_logs":
                    content = self._generate_debug_log(i)
                    
                elif self.category == "nested_fencing":
                    content = self._generate_nested_fencing(i)
                    
                elif self.category == "research_notes":
                    content = self._generate_research_note(i)
                    
                elif self.category == "mixed_content":
                    content = self._generate_mixed_content(i)
                    
                else:
                    content = self._generate_generic(i)
                
                # Analyze and create metadata
                analysis = self._analyze_content(content)
                
                filename = self._generate_filename(i)
                
                metadata = DocumentMetadata(
                    filename=filename,
                    category=self.category,
                    subcategory=self.subcategory,
                    size_bytes=len(content.encode("utf-8")),
                    source="synthetic",
                    collection_date=datetime.now().isoformat(),
                    content_hash=self._compute_hash(content),
                    **analysis,
                )
                
                metadata.expected_strategy = self._determine_expected_strategy(analysis)
                
                # Save
                if self.save_document(content, filename, metadata):
                    results.append(
                        CollectionResult(success=True, content=content, metadata=metadata)
                    )
                    print(f"  ✓ {filename}")
                else:
                    results.append(
                        CollectionResult(success=False, error="Failed to save")
                    )
                    print(f"  ✗ {filename}")
                    
            except Exception as e:
                print(f"  ✗ Error generating document {i}: {str(e)}")
                results.append(CollectionResult(success=False, error=str(e)))
        
        return results

    def _generate_filename(self, index: int) -> str:
        """Generate filename for document."""
        if self.subcategory:
            return f"{self.subcategory}_{index:03d}.md"
        return f"{self.category}_{index:03d}.md"

    def _generate_unstructured_note(self, index: int) -> str:
        """Generate an unstructured personal note."""
        topics = ["async programming", "database optimization", "API design", 
                  "caching strategies", "testing patterns", "debugging tips",
                  "performance tuning", "code refactoring"]
        topic = random.choice(topics)
        
        langs = ["Python", "JavaScript", "Go", "Rust", "Java"]
        lang = random.choice(langs)
        
        # Vary size
        paragraphs = random.randint(3, 15)
        
        lines = [f"# Quick Notes on {topic}\n"]
        
        # Add some irregular structure
        if random.random() > 0.5:
            lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n")
        
        for i in range(paragraphs):
            # Mix of different content types
            if random.random() < 0.3:
                # Code snippet (sometimes unfenced)
                if random.random() < 0.5:
                    lines.append(f"```{lang.lower()}\n")
                    lines.append(f"# Example code for {topic}\n")
                    lines.append(f"def example():\n    pass\n")
                    lines.append("```\n\n")
                else:
                    lines.append(f"Just use: def example(): pass\n\n")
            else:
                # Text paragraph
                lines.append(f"Today learned about {topic} in {lang}. ")
                lines.append(f"Key points: remember to use best practices. ")
                lines.append(f"TODO: try this with real code.\n\n")
                
            if random.random() < 0.2:
                lines.append(f"## Subsection {i}\n\n")
        
        # Add some abbreviations and informal language
        lines.append("BTW, this works great. IMHO it's the best approach.\n\n")
        lines.append("TODO:\n- Test this\n- Write docs\n- Fix bugs\n")
        
        return "".join(lines)

    def _generate_journal(self, index: int) -> str:
        """Generate an engineering journal entry."""
        date = datetime.now() - timedelta(days=random.randint(0, 365))
        
        problems = [
            "API returning 500 errors",
            "Memory leak in production",
            "Database deadlocks",
            "Slow query performance",
            "Race condition in concurrent code",
            "Cache invalidation issues"
        ]
        
        problem = random.choice(problems)
        lang = random.choice(["python", "javascript", "go", "java"])
        
        content = f"""# {date.strftime('%Y-%m-%d')} Debug Session

## Problem

{problem} - occurring intermittently in production.

## Investigation

1. Checked logs - found suspicious patterns
2. Traced to root cause in core component
3. Identified the problematic code section

## Code Analysis

Before (problematic):

```{lang}
# Bad implementation
def process_data(data):
    result = expensive_operation(data)
    # Missing error handling
    # Missing resource cleanup
    return result
```

After (fixed):

```{lang}
# Improved implementation  
def process_data(data):
    try:
        result = expensive_operation(data)
        return result
    except Exception as e:
        logger.error(f"Processing failed: {{e}}")
        return None
    finally:
        cleanup_resources()
```

## Lessons Learned

- Always add proper error handling
- Use try/finally for resource cleanup
- Add monitoring and alerting
- Test edge cases thoroughly

## Follow-up Tasks

- [ ] Add unit tests for error cases
- [ ] Update documentation
- [ ] Monitor metrics for 24h
"""
        
        return content

    def _generate_cheatsheet(self, index: int) -> str:
        """Generate a technical cheatsheet."""
        tools = [
            ("Git", "git"),
            ("Docker", "docker"),
            ("Kubernetes", "kubectl"),
            ("Vim", "vim"),
            ("SQL", "sql"),
            ("Bash", "bash"),
        ]
        
        tool_name, cmd_prefix = random.choice(tools)
        
        content = f"""# {tool_name} Cheatsheet

## Basic Commands

| Command | Description |
|---------|-------------|
| `{cmd_prefix} init` | Initialize new repository |
| `{cmd_prefix} status` | Check current status |
| `{cmd_prefix} list` | List all items |
| `{cmd_prefix} show <id>` | Show details |

## Common Operations

### Creating Items

```bash
{cmd_prefix} create <name>
{cmd_prefix} add <file>
{cmd_prefix} commit -m "message"
```

### Viewing Items

- `{cmd_prefix} log` - view history
- `{cmd_prefix} diff` - show changes  
- `{cmd_prefix} show` - display content

### Modifying Items

```bash
{cmd_prefix} update <id>
{cmd_prefix} delete <id>
{cmd_prefix} rename <old> <new>
```

## Advanced Usage

### Configuration

```bash
{cmd_prefix} config --global user.name "Name"
{cmd_prefix} config --global user.email "email@example.com"
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Permission denied | Run with sudo |
| Not found | Check path |
| Conflict | Resolve manually |

## Tips & Tricks

1. Use aliases for common commands
2. Enable auto-completion
3. Read the manual: `man {cmd_prefix}`
4. Check version: `{cmd_prefix} --version`

## References

- Official docs: https://docs.example.com
- Community guide: https://guide.example.com
"""
        
        return content

    def _generate_debug_log(self, index: int) -> str:
        """Generate a debugging log document."""
        techs = [
            ("Node.js", "javascript"),
            ("Python", "python"),
            ("Java", "java"),
            ("Go", "go"),
        ]
        
        tech, lang = random.choice(techs)
        
        issues = [
            ("Memory Leak", "memory usage grows over time"),
            ("Performance Issue", "slow response times"),
            ("Crash", "application crashes unexpectedly"),
            ("Data Corruption", "incorrect data in database"),
        ]
        
        issue_name, symptom = random.choice(issues)
        
        content = f"""# Debugging {issue_name} in {tech} Application

## Symptoms

- {symptom}
- Eventually leads to system failure
- Occurs under high load conditions

## Environment

- {tech} version: latest
- OS: Linux
- Load: 1000+ requests/second

## Code Under Investigation

```{lang}
// Main application code
function processRequest(req) {{
    const data = fetchData(req.id);
    const result = transformData(data);
    cache[req.id] = result;  // Potential issue here
    return result;
}}
```

## Diagnostic Output

```
Memory Usage Timeline:
T+0min:  512MB
T+10min: 1.2GB
T+20min: 2.5GB
T+30min: 4.1GB (OOM kill)
```

## Heap Analysis

```
Top Memory Consumers:
Object Type      | Count  | Size
-----------------|--------|--------
CachedData       | 50000  | 2.1GB
RequestContext   | 30000  | 800MB
ConnectionPool   | 500    | 50MB
```

## Root Cause

The cache grows unbounded because there's no eviction policy.

## Solution

Implemented LRU cache with size limits:

```{lang}
// Fixed implementation
const LRU = require('lru-cache');
const cache = new LRU({{
    max: 1000,
    maxAge: 1000 * 60 * 5  // 5 minutes
}});

function processRequest(req) {{
    const data = fetchData(req.id);
    const result = transformData(data);
    cache.set(req.id, result);
    return result;
}}
```

## Verification

After fix:
- Memory stable at ~600MB
- No OOM kills in 7 days
- Performance improved 20%

## Lessons

1. Always set limits on caches
2. Monitor memory usage
3. Use profiling tools early
4. Test under realistic load
"""
        
        return content

    def _generate_nested_fencing(self, index: int) -> str:
        """Generate document with nested code fences."""
        nesting = random.randint(3, 5)
        
        content = """# How to Write Technical Documentation

## Including Code Examples

When documenting code, you need to show examples in markdown.

### Basic Code Block

Use triple backticks:

"""
        
        if nesting >= 3:
            content += "```markdown\n"
            content += "Here's how to show Python:\n\n"
            content += "```python\n"
            content += "def hello():\n"
            content += "    print('Hello, World!')\n"
            content += "```\n"
            content += "```\n\n"
        
        if nesting >= 4:
            content += "### Nested Examples\n\n"
            content += "For meta-documentation:\n\n"
            content += "````markdown\n"
            content += "To show markdown within markdown:\n\n"
            content += "```markdown\n"
            content += "# Example\n"
            content += "```python\n"
            content += "code here\n"
            content += "```\n"
            content += "```\n"
            content += "````\n\n"
        
        if nesting >= 5:
            content += "### Triple Nesting\n\n"
            content += "`````markdown\n"
            content += "Even more nested:\n\n"
            content += "````markdown\n"
            content += "```markdown\n"
            content += "```python\n"
            content += "def nested():\n"
            content += "    pass\n"
            content += "```\n"
            content += "```\n"
            content += "````\n"
            content += "`````\n\n"
        
        content += """## Best Practices

1. Use appropriate fence depth
2. Specify language for syntax highlighting
3. Keep examples concise
4. Test all code examples

## Alternatives

You can also use tilde fences:

~~~python
def alternative():
    return True
~~~
"""
        
        return content

    def _generate_research_note(self, index: int) -> str:
        """Generate a research note document."""
        fields = ["Machine Learning", "Distributed Systems", "Database Theory", "Computer Vision"]
        field = random.choice(fields)
        
        content = f"""# Research Notes: {field} Study

## Abstract

This document summarizes research findings on {field.lower()} 
optimization techniques. We investigate novel approaches and 
compare them with existing baselines.

## Literature Review

### Key Papers

1. Smith et al. (2023) - "Advanced Techniques in {field}"
2. Jones & Brown (2022) - "Optimization Strategies"
3. Lee et al. (2021) - "Benchmark Analysis"

### Related Work

Previous studies have shown that traditional approaches have 
limitations. Our work builds on [Smith2023] and extends it
with new methodologies.

## Methodology

### Experimental Setup

```python
import numpy as np
import pandas as pd

# Configuration
config = {{
    'dataset_size': 10000,
    'test_split': 0.2,
    'random_seed': 42
}}

# Load and prepare data
data = load_dataset(config['dataset_size'])
train, test = split_data(data, config['test_split'])
```

### Metrics

| Metric | Baseline | Our Approach | Improvement |
|--------|----------|--------------|-------------|
| Accuracy | 0.85 | 0.92 | +8.2% |
| Latency | 150ms | 95ms | -36.7% |
| Memory | 2GB | 1.2GB | -40% |

## Results

### Primary Findings

Our approach demonstrates significant improvements:

```python
# Results analysis
results = {{
    'accuracy': 0.92,
    'precision': 0.89,
    'recall': 0.94,
    'f1_score': 0.91
}}

print(f"F1 Score: {{results['f1_score']:.2f}}")
```

### Statistical Significance

- p-value < 0.01 for all metrics
- 95% confidence intervals shown in Table 1
- Reproducible across 10 independent runs

## Discussion

The results indicate that our approach is superior to baselines
in most scenarios. However, edge cases require further investigation.

### Limitations

1. Dataset size limited to 10K samples
2. Single domain evaluation
3. Computational cost for training

## Conclusions

This research demonstrates feasibility of the proposed approach.
Future work will address current limitations and explore
additional domains.

## References

[Smith2023] Smith, J., et al. "Advanced Techniques." Journal of AI, 2023.
[Jones2022] Jones, A. & Brown, B. "Optimization." Proceedings of ML, 2022.
[Lee2021] Lee, C., et al. "Benchmarks." ACM Computing, 2021.
"""
        
        return content

    def _generate_mixed_content(self, index: int) -> str:
        """Generate document with mixed content and edge cases."""
        
        # Create extreme cases
        edge_cases = random.sample([
            self._add_unicode_content,
            self._add_long_table,
            self._add_deep_list,
            self._add_very_long_line,
            self._add_empty_sections,
        ], k=random.randint(2, 4))
        
        content = f"""# Mixed Content Document {index}

## Overview 🚀

This document contains various markdown elements to test edge cases.

### Unicode Characters

Support for: 日本語, 한국어, العربية, Emoji: 🎉 ✨ 🔥

"""
        
        # Add selected edge cases
        for add_edge_case in edge_cases:
            content += add_edge_case()
        
        # Add normal content mixed in
        content += """
## Code Examples

Multiple languages in one document:

```python
def python_example():
    return "Hello from Python"
```

```javascript
function jsExample() {
    return "Hello from JavaScript";
}
```

```go
func goExample() string {
    return "Hello from Go"
}
```

## Lists and Tables Mixed

### Feature Comparison

| Feature | Version 1 | Version 2 | Version 3 |
|---------|-----------|-----------|-----------|
| Speed | Fast | Faster | Fastest |
| Memory | 1GB | 500MB | 200MB |

### Task List

- [x] Complete phase 1
- [x] Review code
- [ ] Deploy to production
- [ ] Monitor metrics

## Conclusion

This mixed document tests various edge cases and content types.
"""
        
        return content

    def _add_unicode_content(self) -> str:
        """Add content with unicode."""
        return """
### Unicode Test Section

Text with various scripts: Привет мир! 你好世界! مرحبا بالعالم!

Code with unicode:

```python
message = "Hello 世界 🌍"
print(f"Message: {message}")
```

"""

    def _add_long_table(self) -> str:
        """Add a very wide table."""
        headers = " | ".join([f"Col{i}" for i in range(25)])
        separator = " | ".join(["---" for _ in range(25)])
        row = " | ".join([f"Val{i}" for i in range(25)])
        
        return f"""
### Very Wide Table

| {headers} |
| {separator} |
| {row} |
| {row} |

"""

    def _add_deep_list(self) -> str:
        """Add deeply nested list."""
        content = "\n### Deeply Nested List\n\n"
        
        for i in range(12):
            indent = "  " * i
            content += f"{indent}- Level {i+1} item\n"
        
        return content + "\n"

    def _add_very_long_line(self) -> str:
        """Add a very long line."""
        long_text = " ".join(["word"] * 300)
        return f"\n### Long Line Test\n\n{long_text}\n\n"

    def _add_empty_sections(self) -> str:
        """Add empty sections."""
        return """
### Empty Section

### Another Empty Section

#### Subsection With No Content

"""

    def _generate_generic(self, index: int) -> str:
        """Generate generic document."""
        return f"""# Generic Document {index}

## Introduction

This is a generic markdown document for corpus testing.

## Content

Some sample content here.

```python
def example():
    return "Hello, World!"
```

## Conclusion

End of document.
"""
