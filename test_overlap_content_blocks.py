#!/usr/bin/env python3
"""Test to verify content blocks are included in overlap instead of just headers."""

from markdown_chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig
import logging

# Enable DEBUG logging to see what blocks are being selected
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

# Create config with 200-char overlap
config = ChunkConfig(
    max_chunk_size=1000,
    overlap_size=200,
    enable_overlap=True,
    block_based_overlap=False  # Use new metadata-mode overlap
)

# Test text with clear structure: headers + paragraphs
markdown_text = """# Section A

## Subsection A1

This is the first paragraph with substantial content.
It has multiple lines to make it longer than just headers.
We want this content to appear in the overlap, not just headers.

## Subsection A2

This is the second paragraph with different content.
It also has multiple lines of actual text.
This should be extracted as overlap context.

# Section B

## Subsection B1

Third paragraph with more content here.
Multiple lines again to ensure we have enough text.
This helps test the overlap extraction properly.
"""

# Create chunker and chunk the text
chunker = MarkdownChunker(config)
result = chunker.chunk(
    markdown_text,
    strategy="structural",
    include_metadata=True,
    return_format="objects"  # Get Chunk objects
)

# Display results
print("\n" + "="*80)
print("OVERLAP CONTENT ANALYSIS")
print("="*80)

for i, chunk in enumerate(result):
    print(f"\n{'='*80}")
    print(f"CHUNK {i}")
    print(f"{'='*80}")
    
    # Show content preview
    content = chunk.content
    print(f"\nContent ({len(content)} chars):")
    print(content[:300] + ("..." if len(content) > 300 else ""))
    
    # Show overlap fields
    metadata = chunk.metadata
    
    if 'previous_content' in metadata:
        prev = metadata['previous_content']
        print(f"\n✓ previous_content ({len(prev)} chars):")
        print(prev[:200] + ("..." if len(prev) > 200 else ""))
    else:
        print("\n✗ previous_content: Not present")
    
    if 'next_content' in metadata:
        next_ctx = metadata['next_content']
        print(f"\n✓ next_content ({len(next_ctx)} chars):")
        print(next_ctx[:200] + ("..." if len(next_ctx) > 200 else ""))
    else:
        print("\n✗ next_content: Not present")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
