# Elements Guide

## 🎯 Overview

The `stage1.element_detector` module provides detection and analysis of structural Markdown elements including headers, lists, and tables with detailed metadata and hierarchy information.

## 📋 Main Functions

### `detect_elements(md_text: str) -> ElementCollection`

Detect all structural elements in Markdown text:

```python
from stage1.element_detector import detect_elements

markdown = """
# API Documentation

## Introduction
This API provides access to our services with comprehensive endpoints.

### Authentication
Use API keys for authentication:

1. Get your API key from the dashboard
2. Include it in the Authorization header
3. Make requests to protected endpoints

#### Rate Limits
- Free tier: 1000 requests per hour
- Pro tier: 10000 requests per hour  
- Enterprise: Unlimited requests

| Tier | Hourly Limit | Burst Limit |
|------|--------------|-------------|
| Free | 1,000        | 100/min     |
| Pro  | 10,000       | 500/min     |
| Enterprise | Unlimited | 1000/min   |

## Examples

### Python Example
Here's how to use the API with Python:

```python
import requests
headers = {'Authorization': 'Bearer your-key'}
response = requests.get('https://api.example.com/users', headers=headers)
```

### Task List
- [x] Implement authentication
- [ ] Add rate limiting
- [ ] Write documentation
- [x] Deploy to production

> **Important**: Always use HTTPS for API requests.

---

## Support
Contact us at support@example.com for help.
"""

elements = detect_elements(markdown)

print(f"Headers: {len(elements.headers)}")
print(f"Lists: {len(elements.lists)}")
print(f"Tables: {len(elements.tables)}")
print(f"Blockquotes: {len(elements.blockquotes)}")
print(f"Horizontal rules: {len(elements.horizontal_rules)}")
```

## 🏗️ Element Structures

### ElementCollection

The main container for all detected elements:

```python
from stage1.types import ElementCollection

elements = detect_elements(markdown_text)

# Access different element types
headers = elements.headers              # List[Header]
lists = elements.lists                 # List[List]
tables = elements.tables               # List[Table]
blockquotes = elements.blockquotes     # List[Blockquote]
horizontal_rules = elements.horizontal_rules  # List[HorizontalRule]

# Summary methods
total_elements = elements.count_total()
element_summary = elements.get_summary()
hierarchy = elements.get_hierarchy()

print(f"Total elements: {total_elements}")
print(f"Summary: {element_summary}")
```

### Header Elements

```python
from stage1.types import Header

# Header properties
for header in elements.headers:
    print(f"Level: {header.level}")           # 1-6 (h1-h6)
    print(f"Text: {header.text}")             # Header text content
    print(f"Anchor: {header.anchor}")         # Generated anchor ID
    print(f"Line: {header.line}")             # Line number (0-based)
    print(f"Raw: {header.raw_content}")       # Original markdown
    
    # Position information
    print(f"Start pos: {header.start_pos}")   # Position object
    print(f"End pos: {header.end_pos}")       # Position object
    
    # Hierarchy relationships
    print(f"Parent: {header.parent_id}")      # Parent header ID
    print(f"Children: {header.children_ids}") # Child header IDs
    print(f"Depth: {header.depth}")           # Depth in hierarchy
    
    # Content analysis
    print(f"Word count: {header.word_count}")
    print(f"Is empty: {header.is_empty()}")
```

### List Elements

```python
from stage1.types import List, ListItem, ListType

# List properties
for list_elem in elements.lists:
    print(f"Type: {list_elem.type}")          # ListType enum
    print(f"Items: {len(list_elem.items)}")   # Number of items
    print(f"Start line: {list_elem.start_line}")
    print(f"End line: {list_elem.end_line}")
    print(f"Max nesting: {list_elem.max_nesting_level}")
    print(f"Is tight: {list_elem.is_tight}")  # Tight vs loose list
    
    # List items
    for item in list_elem.items:
        print(f"  Content: {item.content}")
        print(f"  Level: {item.nesting_level}")
        print(f"  Marker: {item.marker}")      # List marker (-, *, 1., etc.)
        print(f"  Is checked: {item.is_checked}")  # For task lists
        print(f"  Has children: {item.has_children}")

# List types
print(f"Ordered list: {ListType.ORDERED}")
print(f"Unordered list: {ListType.UNORDERED}")
print(f"Task list: {ListType.TASK}")
```

### Table Elements

```python
from stage1.types import Table, TableRow, TableAlignment

# Table properties
for table in elements.tables:
    print(f"Columns: {table.column_count}")
    print(f"Rows: {len(table.rows)}")
    print(f"Headers: {table.headers}")        # Column headers
    print(f"Alignment: {table.alignment}")    # Column alignment
    print(f"Has header row: {table.has_header_row}")
    print(f"Start line: {table.start_line}")
    print(f"End line: {table.end_line}")
    
    # Table rows
    for i, row in enumerate(table.rows):
        print(f"  Row {i}: {row.cells}")
        print(f"    Is header: {row.is_header}")
        print(f"    Cell count: {len(row.cells)}")
        
        # Individual cells
        for j, cell in enumerate(row.cells):
            print(f"      Cell {j}: '{cell.content}'")
            print(f"        Alignment: {cell.alignment}")
            print(f"        Is empty: {cell.is_empty()}")

# Table alignment types
print(f"Left: {TableAlignment.LEFT}")
print(f"Center: {TableAlignment.CENTER}")
print(f"Right: {TableAlignment.RIGHT}")
print(f"None: {TableAlignment.NONE}")
```

### Blockquote Elements

```python
from stage1.types import Blockquote

# Blockquote properties
for quote in elements.blockquotes:
    print(f"Content: {quote.content}")
    print(f"Level: {quote.nesting_level}")    # Nesting depth
    print(f"Start line: {quote.start_line}")
    print(f"End line: {quote.end_line}")
    print(f"Line count: {quote.line_count}")
    
    # Nested content analysis
    print(f"Has nested quotes: {quote.has_nested_quotes}")
    print(f"Has code blocks: {quote.has_code_blocks}")
    print(f"Has lists: {quote.has_lists}")
```

### Horizontal Rule Elements

```python
from stage1.types import HorizontalRule

# Horizontal rule properties
for rule in elements.horizontal_rules:
    print(f"Line: {rule.line}")               # Line number
    print(f"Marker: {rule.marker}")           # Marker used (---, ***, ___)
    print(f"Length: {rule.length}")           # Number of markers
    print(f"Raw content: {rule.raw_content}") # Original text
```

## 🔍 Advanced Detection

### ElementDetector Class

For advanced configuration and analysis:

```python
from stage1.element_detector import ElementDetector
from stage1.config import DetectorConfig

# Create detector with custom configuration
config = DetectorConfig(
    detect_headers=True,
    detect_lists=True,
    detect_tables=True,
    detect_blockquotes=True,
    detect_horizontal_rules=True,
    generate_anchors=True,
    build_hierarchy=True
)

detector = ElementDetector(config)

# Detect elements
elements = detector.detect_elements(markdown_text)

# Get detection statistics
stats = detector.get_detection_stats()
print(f"Processing time: {stats['processing_time']:.3f}s")
print(f"Elements found: {stats['total_elements']}")
print(f"Memory usage: {stats['memory_usage']}MB")
```

### Header Hierarchy Analysis

```python
# Build and analyze header hierarchy
elements = detect_elements(markdown_text)

def print_header_hierarchy(headers, level=0):
    """Print header hierarchy with indentation."""
    for header in headers:
        if header.depth == level:
            indent = "  " * level
            print(f"{indent}H{header.level}: {header.text}")
            
            # Find and print children
            children = [h for h in headers if h.parent_id == header.anchor]
            if children:
                print_header_hierarchy(children, level + 1)

print_header_hierarchy(elements.headers)

# Get hierarchy statistics
hierarchy_stats = elements.get_hierarchy_stats()
print(f"Max depth: {hierarchy_stats['max_depth']}")
print(f"Total sections: {hierarchy_stats['total_sections']}")
print(f"Orphaned headers: {hierarchy_stats['orphaned_headers']}")
```

### Anchor Generation

```python
# Headers automatically get anchor IDs
for header in elements.headers:
    print(f"'{header.text}' -> '{header.anchor}'")

# Examples of anchor generation:
# "API Documentation" -> "api-documentation"
# "Getting Started" -> "getting-started"
# "User Authentication & Security" -> "user-authentication--security"
# "FAQ (Frequently Asked Questions)" -> "faq-frequently-asked-questions"

# Custom anchor generation
from stage1.element_detector import generate_anchor

custom_anchor = generate_anchor("Custom Header Text!", prefix="section-")
print(f"Custom anchor: {custom_anchor}")  # "section-custom-header-text"
```

### List Analysis

```python
# Analyze list structures
for list_elem in elements.lists:
    print(f"List type: {list_elem.type}")
    print(f"Nesting levels: {list_elem.get_nesting_levels()}")
    print(f"Item count by level: {list_elem.get_item_count_by_level()}")
    
    # Task list analysis
    if list_elem.type == ListType.TASK:
        completed = list_elem.get_completed_items()
        pending = list_elem.get_pending_items()
        print(f"Completed: {len(completed)}/{len(list_elem.items)}")
        print(f"Progress: {list_elem.get_completion_percentage():.1f}%")
    
    # Nested structure analysis
    nested_items = list_elem.get_nested_items()
    for level, items in nested_items.items():
        print(f"  Level {level}: {len(items)} items")
```

### Table Analysis

```python
# Analyze table structures
for table in elements.tables:
    print(f"Table dimensions: {table.rows} x {table.column_count}")
    print(f"Column alignments: {table.alignment}")
    
    # Data analysis
    data_rows = table.get_data_rows()  # Exclude header rows
    print(f"Data rows: {len(data_rows)}")
    
    # Column analysis
    for i, header in enumerate(table.headers):
        column_data = table.get_column_data(i)
        print(f"Column '{header}': {len(column_data)} values")
        
        # Check for empty cells
        empty_cells = sum(1 for cell in column_data if cell.is_empty())
        print(f"  Empty cells: {empty_cells}/{len(column_data)}")
    
    # Table validation
    validation = table.validate()
    if not validation.is_valid:
        print(f"Table issues: {validation.issues}")
```

## 🎯 Integration Examples

### With AST Parser

```python
from stage1.markdown_ast import parse_to_ast
from stage1.element_detector import detect_elements
from stage1.types import NodeType

# Parse both AST and elements
ast = parse_to_ast(markdown_text)
elements = detect_elements(markdown_text)

# Correlate elements with AST nodes
for header in elements.headers:
    # Find corresponding AST node
    for node in ast.find_children(NodeType.HEADER):
        if (node.start_pos.line <= header.line <= node.end_pos.line):
            print(f"Header '{header.text}' matches AST node at line {node.start_pos.line}")

# Cross-reference lists
for list_elem in elements.lists:
    list_nodes = ast.find_children(NodeType.LIST)
    matching_node = None
    for node in list_nodes:
        if node.start_pos.line == list_elem.start_line:
            matching_node = node
            break
    
    if matching_node:
        print(f"List at line {list_elem.start_line} has AST representation")
```

### With Content Analyzer

```python
from stage1.content_analyzer import analyze_content
from stage1.element_detector import detect_elements

# Analyze content and detect elements
analysis = analyze_content(markdown_text)
elements = detect_elements(markdown_text)

# Correlate analysis with elements
print(f"Content complexity: {analysis.complexity_score}")
print(f"Structural elements: {elements.count_total()}")

# Header analysis
header_ratio = len(elements.headers) / analysis.total_lines
print(f"Header density: {header_ratio:.3f} headers per line")

# List analysis
if elements.lists:
    avg_list_size = sum(len(lst.items) for lst in elements.lists) / len(elements.lists)
    print(f"Average list size: {avg_list_size:.1f} items")

# Table analysis
if elements.tables:
    total_cells = sum(table.column_count * len(table.rows) for table in elements.tables)
    print(f"Total table cells: {total_cells}")
```

### With Fenced Block Extractor

```python
from stage1.fenced_block_extractor import extract_fenced_blocks
from stage1.element_detector import detect_elements

# Extract blocks and detect elements
blocks = extract_fenced_blocks(markdown_text)
elements = detect_elements(markdown_text)

# Find code blocks within lists
for list_elem in elements.lists:
    list_blocks = []
    for block in blocks:
        if list_elem.start_line <= block.start_line <= list_elem.end_line:
            list_blocks.append(block)
    
    if list_blocks:
        print(f"List at line {list_elem.start_line} contains {len(list_blocks)} code blocks")

# Find code blocks within blockquotes
for quote in elements.blockquotes:
    quote_blocks = []
    for block in blocks:
        if quote.start_line <= block.start_line <= quote.end_line:
            quote_blocks.append(block)
    
    if quote_blocks:
        print(f"Blockquote at line {quote.start_line} contains {len(quote_blocks)} code blocks")
```

## ⚡ Performance Tips

### Efficient Element Detection

```python
# Selective detection for better performance
from stage1.config import DetectorConfig

# Only detect what you need
config = DetectorConfig(
    detect_headers=True,
    detect_lists=False,      # Skip if not needed
    detect_tables=False,     # Skip if not needed
    detect_blockquotes=False,
    detect_horizontal_rules=False
)

detector = ElementDetector(config)
elements = detector.detect_elements(markdown_text)
```

### Batch Processing

```python
def detect_elements_batch(documents: List[str]) -> List[ElementCollection]:
    """Efficiently process multiple documents."""
    detector = ElementDetector()
    results = []
    
    for doc in documents:
        elements = detector.detect_elements(doc)
        results.append(elements)
    
    return results

# Process multiple documents
documents = [doc1, doc2, doc3]
all_elements = detect_elements_batch(documents)
```

### Caching Results

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_detect_elements(md_text: str) -> ElementCollection:
    """Cache element detection results."""
    return detect_elements(md_text)

# Use cached detection
elements1 = cached_detect_elements(document)
elements2 = cached_detect_elements(document)  # Uses cache
```

## 🔧 Configuration Options

### DetectorConfig

```python
from stage1.config import DetectorConfig

config = DetectorConfig(
    # Element types to detect
    detect_headers=True,
    detect_lists=True,
    detect_tables=True,
    detect_blockquotes=True,
    detect_horizontal_rules=True,
    
    # Header processing
    generate_anchors=True,           # Generate anchor IDs
    build_hierarchy=True,            # Build header hierarchy
    normalize_anchors=True,          # Normalize anchor format
    anchor_prefix="",                # Prefix for anchors
    max_header_level=6,              # Maximum header level to detect
    
    # List processing
    detect_task_lists=True,          # Detect task lists (checkboxes)
    normalize_list_markers=True,     # Normalize list markers
    calculate_nesting=True,          # Calculate nesting levels
    max_list_depth=10,               # Maximum list nesting depth
    
    # Table processing
    detect_alignment=True,           # Detect column alignment
    normalize_tables=True,           # Normalize table format
    require_headers=False,           # Require table headers
    min_table_columns=2,             # Minimum columns for table detection
    
    # Performance settings
    max_elements=10000,              # Maximum elements to detect
    enable_caching=True,             # Cache detection results
    processing_timeout=30.0          # Maximum processing time (seconds)
)
```

## 📊 Element Statistics

### Getting Statistics

```python
# Get comprehensive element statistics
elements = detect_elements(markdown_text)
stats = elements.get_detailed_stats()

print(f"Element counts: {stats['counts']}")
print(f"Hierarchy depth: {stats['hierarchy_depth']}")
print(f"Average list size: {stats['avg_list_size']}")
print(f"Table complexity: {stats['table_complexity']}")
print(f"Processing metrics: {stats['processing']}")
```

### Element Distribution

```python
# Analyze element distribution
distribution = elements.get_distribution()

print("Element distribution by type:")
for element_type, count in distribution.items():
    percentage = (count / elements.count_total()) * 100
    print(f"  {element_type}: {count} ({percentage:.1f}%)")

# Analyze by document sections
section_stats = elements.get_section_stats()
for section, stats in section_stats.items():
    print(f"Section '{section}': {stats['element_count']} elements")
```