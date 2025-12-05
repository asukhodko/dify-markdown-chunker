# Test Migration Quick Reference Guide

**Quick start guide for migrating legacy tests to v2**

## TL;DR - Common Migration Patterns

### 1. Basic Import Fix (90% of cases)

```python
# BEFORE (legacy)
from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig, Chunk

# AFTER (v2)
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig, Chunk
```

### 2. Parser Import Fix

```python
# BEFORE (legacy)
from markdown_chunker.parser import ParserInterface
from markdown_chunker.parser.types import ContentAnalysis

# AFTER (v2)
from markdown_chunker_v2.parser import Parser
from markdown_chunker_v2.types import ContentAnalysis
```

### 3. Config Adaptation

```python
# BEFORE (legacy - 32 parameters)
config = ChunkConfig(
    max_chunk_size=2048,
    min_chunk_size=256,
    overlap_size=100,
    enable_overlap=True,
    block_based_splitting=True,
    preserve_code_blocks=True,
    enable_deduplication=False,
    # ... 25 more parameters omitted
)

# AFTER (v2 - 8 parameters)
config = ChunkConfig(
    max_chunk_size=2048,
    min_chunk_size=256,
    overlap_size=100,
    enable_overlap=True,
    preserve_atomic_blocks=True,  # ← replaces multiple legacy flags
    # v2 parameters: max_chunk_size, min_chunk_size, overlap_size,
    #                enable_overlap, preserve_atomic_blocks,
    #                code_fence_margin, overlap_metadata_mode, fallback_enabled
)
```

## Migration Checklist

Use this for every test file:

```markdown
- [ ] Update imports to markdown_chunker_v2
- [ ] Replace ChunkConfig (32 → 8 params)
- [ ] Update strategy references (6 → 3 strategies)
- [ ] Run test: pytest tests/path/to/test.py -v
- [ ] Fix any assertion errors
- [ ] Verify no warnings
- [ ] Add migration note to docstring
- [ ] Commit: "test: migrate [test_name] to v2"
```

## Import Mapping Table

| Legacy Import | V2 Import |
|---------------|-----------|
| `markdown_chunker.chunker.core.MarkdownChunker` | `markdown_chunker_v2.MarkdownChunker` |
| `markdown_chunker.chunker.types.ChunkConfig` | `markdown_chunker_v2.ChunkConfig` |
| `markdown_chunker.chunker.types.Chunk` | `markdown_chunker_v2.Chunk` |
| `markdown_chunker.parser.ParserInterface` | `markdown_chunker_v2.parser.Parser` |
| `markdown_chunker.parser.types.ContentAnalysis` | `markdown_chunker_v2.types.ContentAnalysis` |
| `markdown_chunker.chunker.strategies.*` | `markdown_chunker_v2.strategies.*` |
| `markdown_chunker.chunker.components.OverlapManager` | ⚠️ Integrated in v2 strategies |

## Strategy Mapping

| Legacy Strategy | V2 Strategy | Notes |
|-----------------|-------------|-------|
| `code` | `code_aware` | Renamed |
| `structural` | `structural` | Same name |
| `list` | `structural` | Merged into structural |
| `table` | `structural` | Merged into structural |
| `sentences` | `fallback` | Simple text chunking |
| `mixed` | *automatic* | No explicit mixed strategy in v2 |

## Config Parameter Mapping

| Legacy Parameter | V2 Parameter | Notes |
|------------------|--------------|-------|
| `max_chunk_size` | `max_chunk_size` | Same |
| `min_chunk_size` | `min_chunk_size` | Same |
| `overlap_size` | `overlap_size` | Same |
| `enable_overlap` | `enable_overlap` | Same |
| `block_based_splitting` | `preserve_atomic_blocks` | Renamed & simplified |
| `preserve_code_blocks` | `preserve_atomic_blocks` | Merged |
| `code_fence_margin` | `code_fence_margin` | Same |
| `enable_deduplication` | ❌ Removed | Not in v2 |
| `enable_size_normalization` | ❌ Removed | Always enabled in v2 |
| `strategy_override` | ❌ Removed | Automatic selection in v2 |
| *27 other legacy params* | ❌ Removed | Simplified in v2 |

## Common Migration Scenarios

### Scenario 1: Property-Based Test (Easy)

**Time**: 15-30 minutes

```python
# BEFORE
from hypothesis import given, strategies as st
from markdown_chunker.chunker.core import MarkdownChunker

@given(text=st.text(min_size=10))
def test_property(text):
    chunker = MarkdownChunker()
    chunks = chunker.chunk(text)
    assert len(chunks) > 0

# AFTER
from hypothesis import given, strategies as st
from markdown_chunker_v2 import MarkdownChunker

@given(text=st.text(min_size=10))
def test_property(text):
    chunker = MarkdownChunker()
    chunks = chunker.chunk(text)
    assert len(chunks) > 0
```

### Scenario 2: Test with Custom Config (Moderate)

**Time**: 30-45 minutes

```python
# BEFORE
from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig

def test_with_config():
    config = ChunkConfig(
        max_chunk_size=1000,
        block_based_splitting=True,
        preserve_code_blocks=True,
        enable_deduplication=False,
    )
    chunker = MarkdownChunker(config)
    chunks = chunker.chunk("# Test")
    assert len(chunks) == 1

# AFTER
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig

def test_with_config():
    config = ChunkConfig(
        max_chunk_size=1000,
        preserve_atomic_blocks=True,  # replaces block_based_splitting + preserve_code_blocks
    )
    chunker = MarkdownChunker(config)
    chunks = chunker.chunk("# Test")
    assert len(chunks) == 1
```

### Scenario 3: Parser Test (Moderate-Hard)

**Time**: 45-60 minutes

```python
# BEFORE
from markdown_chunker.parser import ParserInterface
from markdown_chunker.parser.types import ContentAnalysis

def test_parser():
    parser = ParserInterface()
    result = parser.process_document("# Test\n\nContent")
    assert result.analysis.total_chars > 0

# AFTER
from markdown_chunker_v2.parser import Parser
from markdown_chunker_v2.types import ContentAnalysis

def test_parser():
    parser = Parser()
    analysis = parser.parse("# Test\n\nContent")
    assert isinstance(analysis, ContentAnalysis)
    assert analysis.total_chars > 0
```

### Scenario 4: Strategy-Specific Test (Hard)

**Time**: 1-2 hours

```python
# BEFORE
from markdown_chunker.chunker.strategies.code_strategy import CodeStrategy
from markdown_chunker.chunker.types import ChunkConfig

def test_code_strategy():
    strategy = CodeStrategy()
    config = ChunkConfig.for_code_heavy()
    # ... test implementation

# AFTER - Option 1: Test through chunker
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig

def test_code_strategy():
    chunker = MarkdownChunker()
    chunks = chunker.chunk("```python\ncode\n```")
    assert chunks[0].metadata.get('strategy') == 'code_aware'

# AFTER - Option 2: Test strategy directly
from markdown_chunker_v2.strategies import CodeAwareStrategy
from markdown_chunker_v2 import ChunkConfig

def test_code_strategy():
    strategy = CodeAwareStrategy()
    config = ChunkConfig()
    # ... adapt test to v2 strategy API
```

## Testing Commands

### Run Single Test File
```bash
pytest tests/path/to/test_file.py -v
```

### Run Single Test Function
```bash
pytest tests/path/to/test_file.py::test_function_name -v
```

### Run with Import Error Details
```bash
pytest tests/path/to/test_file.py -v -s --tb=short
```

### Collect Without Running
```bash
pytest tests/path/to/test_file.py --collect-only
```

### Run P0 Tests
```bash
make test-p0
```

## Troubleshooting

### Issue: Import Error After Migration

**Symptom**: `ModuleNotFoundError: No module named 'markdown_chunker_v2.X'`

**Solution**: Check v2 module structure
```python
# V2 module structure:
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig, Chunk
from markdown_chunker_v2.types import ContentAnalysis, FencedBlock
from markdown_chunker_v2.parser import Parser
from markdown_chunker_v2.strategies import CodeAwareStrategy, StructuralStrategy, FallbackStrategy
```

### Issue: Test Passes But Validates Wrong Thing

**Symptom**: Test passes but seems to validate different behavior

**Solution**: Review assertions
1. Check what property/behavior test validates
2. Verify v2 has equivalent behavior
3. Update assertions to match v2 metadata structure
4. Compare with baseline.json if available

### Issue: Config Parameter Not Found

**Symptom**: `TypeError: __init__() got an unexpected keyword argument 'X'`

**Solution**: Check parameter mapping
1. Look up parameter in mapping table above
2. Use v2 equivalent or remove if deprecated
3. Consolidate related flags into single v2 parameter

### Issue: Strategy Not Selected

**Symptom**: Test expects strategy 'X' but gets 'structural'

**Solution**: V2 uses automatic strategy selection
```python
# BEFORE: Explicit strategy
chunks = chunker.chunk(text, strategy='code')

# AFTER: Automatic selection based on content
chunks = chunker.chunk(text)  # strategy selected automatically
# Check selected strategy:
assert chunks[0].metadata['strategy'] == 'code_aware'
```

## Migration Decision Tree

```
Is test marked P0?
├─ YES: Migrate now (this sprint)
└─ NO: Is test marked P1?
    ├─ YES: Schedule for next 2-3 sprints
    └─ NO: Is test marked P2?
        ├─ YES: Migrate opportunistically
        └─ NO: Is test Category E?
            ├─ YES: Archive with documentation
            └─ NO: Evaluate in Phase 4
```

## When to Ask for Help

Migrate the test yourself if:
- ✅ Simple import fix
- ✅ Config adaptation (follow mapping table)
- ✅ Property-based test
- ✅ Similar to already-migrated test

Ask for help if:
- ❌ Test uses removed components (OverlapManager, etc.)
- ❌ Unclear what test validates
- ❌ V2 equivalent behavior not obvious
- ❌ Test requires v2 implementation changes
- ❌ Stuck for more than 30 minutes

## References

- **Full Design**: [legacy-test-analysis.md](./legacy-test-analysis.md)
- **Migration Status**: [test-migration-status.md](./test-migration-status.md)
- **P0 Tasks**: [p0-migration-tasks.md](./p0-migration-tasks.md)
- **V2 Migration Guide**: [../../docs/MIGRATION.md](../../docs/MIGRATION.md)
- **V2 API Docs**: [../../docs/api/](../../docs/api/)

## Quick Commands Reference

```bash
# Verify import structure
ls -la markdown_chunker_v2/

# Check v2 config parameters
venv/bin/python3.12 -c "from markdown_chunker_v2 import ChunkConfig; print(ChunkConfig.__init__.__doc__)"

# Find similar migrated tests
grep -r "from markdown_chunker_v2 import" tests/

# Run P0 tests
make test-p0

# Run all tests
make test-all

# Get test count
pytest tests/ --collect-only -q | tail -1
```
