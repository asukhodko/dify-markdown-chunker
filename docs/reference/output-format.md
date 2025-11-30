# Output Format Documentation

## Overview

The Advanced Markdown Chunker plugin returns results in a format compatible with Dify's knowledge pipeline UI.

## Output Structure

### Result Field

The `result` field contains an **array of strings**, where each string represents one chunk.

```json
{
  "result": [
    "<metadata>\n{...json...}\n</metadata>\n<chunk content>",
    "<metadata>\n{...json...}\n</metadata>\n<chunk content>",
    "..."
  ]
}
```

### String Format

Each string in the `result` array follows this format:

```
<metadata>
{
  "chunk_index": 0,
  "content_type": "list",
  "strategy": "list",
  "char_count": 78,
  "line_count": 2,
  ...
}
</metadata>
<chunk content here>
```

**Components:**

1. **Metadata Block** (optional, when `include_metadata=true`):
   - Starts with `<metadata>` tag
   - Contains JSON object with chunk metadata
   - Ends with `</metadata>` tag
   - Followed by newline

2. **Content**:
   - The actual chunk text
   - Preserves original Markdown formatting

### Without Metadata

When `include_metadata=false`, the result contains only content:

```json
{
  "result": [
    "# Header\n\nContent here...",
    "More content...",
    "..."
  ]
}
```

## Metadata Fields

When metadata is included, each chunk contains **only RAG-useful fields**. Statistical and internal fields are filtered out to reduce size and improve relevance.

### Core Fields (Always Included)
- `chunk_index`: Position in the document (0-based)
- `content_type`: Type of content (list, code, table, text, etc.)
- `is_first_chunk`, `is_last_chunk`: Position indicators
- `is_continuation`: Whether chunk continues from previous

### Structural Fields (Semantic Indicators)
- `has_bold`, `has_italic`, `has_inline_code`: Formatting indicators
- `has_urls`, `has_emails`: Link indicators
- `has_preamble`: Whether chunk has preamble
- `preamble`: If present, contains `{content: "..."}` with preamble text

### Overlap Fields (When Overlap Enabled)
- `has_overlap`: Whether chunk has overlap
- `overlap_type`: Type of overlap (prefix/suffix)

### Content-Specific Fields

**For Lists:**
- `list_type`: ordered/unordered
- `has_nested_lists`: Whether contains nested lists
- `has_nested_items`: Whether has nested items

**For Code:**
- `language`: Programming language (if specified)
- `has_syntax_highlighting`: Whether language is specified

**For Tables:**
- `row_count`: Number of rows
- `column_count`: Number of columns
- `has_header`: Whether table has header row

### Filtered Out (Not Included)

The following fields are **excluded** as they don't help with RAG retrieval:

**Statistical fields:**
- `avg_line_length`, `avg_word_length`, `char_count`, `line_count`, `size_bytes`, `word_count`

**Count fields:**
- `item_count`, `nested_item_count`, `unordered_item_count`, `ordered_item_count`, `max_nesting`, `task_item_count`

**Internal fields:**
- `execution_fallback_level`, `execution_fallback_used`, `execution_strategy_used`, `strategy`, `total_chunks`, `preview`

**Preamble internal fields:**
- `preamble.char_count`, `preamble.line_count`, `preamble.has_metadata`, `preamble.metadata_fields`, `preamble.type`, `preamble_type`

## Compatibility

### Why This Format?

Dify's knowledge pipeline UI expects `result` to be an array of strings:
- ✅ Compatible with React rendering
- ✅ Can be displayed directly in UI
- ✅ Metadata preserved but encoded as string
- ✅ Can be parsed by downstream processors

### Previous Format (Incompatible)

The previous format returned objects:

```json
{
  "result": [
    {
      "content": "...",
      "metadata": {...}
    }
  ]
}
```

This caused React error #31: "Objects are not valid as a React child"

## Usage Examples

### Parsing Metadata

To extract metadata from a chunk string:

```python
import json
import re

def parse_chunk(chunk_str):
    """Parse chunk string into content and metadata."""
    # Check if metadata exists
    if not chunk_str.startswith("<metadata>"):
        return {"content": chunk_str, "metadata": None}
    
    # Extract metadata block
    match = re.match(r'<metadata>\n(.*?)\n</metadata>\n(.*)', chunk_str, re.DOTALL)
    if not match:
        return {"content": chunk_str, "metadata": None}
    
    metadata_json = match.group(1)
    content = match.group(2)
    
    try:
        metadata = json.loads(metadata_json)
        return {"content": content, "metadata": metadata}
    except json.JSONDecodeError:
        return {"content": chunk_str, "metadata": None}

# Example usage
chunk = result["result"][0]
parsed = parse_chunk(chunk)
print(f"Content: {parsed['content']}")
print(f"Metadata: {parsed['metadata']}")
```

### JavaScript/TypeScript

```typescript
interface ParsedChunk {
  content: string;
  metadata: Record<string, any> | null;
}

function parseChunk(chunkStr: string): ParsedChunk {
  // Check if metadata exists
  if (!chunkStr.startsWith("<metadata>")) {
    return { content: chunkStr, metadata: null };
  }
  
  // Extract metadata block
  const match = chunkStr.match(/<metadata>\n(.*?)\n<\/metadata>\n(.*)/s);
  if (!match) {
    return { content: chunkStr, metadata: null };
  }
  
  const [, metadataJson, content] = match;
  
  try {
    const metadata = JSON.parse(metadataJson);
    return { content, metadata };
  } catch {
    return { content: chunkStr, metadata: null };
  }
}

// Example usage
const chunk = result.result[0];
const parsed = parseChunk(chunk);
console.log("Content:", parsed.content);
console.log("Metadata:", parsed.metadata);
```

## Best Practices

1. **Always validate format**: Check for `<metadata>` tag before parsing
2. **Handle missing metadata**: Some chunks may not have metadata
3. **Preserve original format**: Don't modify chunk strings unnecessarily
4. **Use metadata for filtering**: Filter chunks by content_type, strategy, etc.
5. **Consider overlap**: Use overlap fields to deduplicate if needed

## Version History

- **2.0.2** (2025-11-23): Changed to string array format for UI compatibility
- **2.0.1** (2025-11-23): Object array format (incompatible with UI)
- **2.0.0** (2025-11-23): Initial release

---

**Note:** This format is designed for compatibility with Dify's knowledge pipeline UI while preserving all metadata functionality.
