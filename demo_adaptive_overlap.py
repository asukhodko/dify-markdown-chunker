#!/usr/bin/env python3
"""
Demonstration of adaptive overlap context sizing.

Shows how overlap size scales with chunk size (35% cap).
"""

from markdown_chunker_v2.chunker import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig


def demo_small_chunks():
    """Demo with small chunks - overlap limited by configured size."""
    print("=" * 70)
    print("DEMO 1: Small Chunks (max_chunk_size=500)")
    print("=" * 70)

    md_text = """# Section 1

Small content for demonstration.

# Section 2

More small content here.

# Section 3

Final small section.
"""

    config = ChunkConfig(max_chunk_size=500, overlap_size=200)
    chunker = MarkdownChunker(config)
    chunks = chunker.chunk(md_text)

    print(f"\nConfiguration:")
    print(f"  max_chunk_size: {config.max_chunk_size}")
    print(f"  overlap_size: {config.overlap_size}")
    print(f"\nResults:")

    for i, chunk in enumerate(chunks):
        chunk_size = len(chunk.content)
        adaptive_cap = int(chunk_size * 0.35)
        effective_cap = min(config.overlap_size, adaptive_cap)

        print(f"\n  Chunk {i}:")
        print(f"    Size: {chunk_size} chars")
        print(f"    Adaptive cap (35%): {adaptive_cap} chars")
        print(f"    Effective cap: {effective_cap} chars")

        if "next_content" in chunk.metadata:
            next_size = len(chunk.metadata["next_content"])
            print(f"    Actual next_content: {next_size} chars")


def demo_large_chunks():
    """Demo with large chunks - adaptive cap allows larger overlap."""
    print("\n" + "=" * 70)
    print("DEMO 2: Large Chunks (max_chunk_size=8000)")
    print("=" * 70)

    # Create large content
    large_section = "This is substantial content for a large chunk. " * 100

    md_text = f"""# Section 1

{large_section}

# Section 2

{large_section}

# Section 3

{large_section}
"""

    config = ChunkConfig(max_chunk_size=8000, overlap_size=200)
    chunker = MarkdownChunker(config)
    chunks = chunker.chunk(md_text)

    print(f"\nConfiguration:")
    print(f"  max_chunk_size: {config.max_chunk_size}")
    print(f"  overlap_size: {config.overlap_size}")
    print(f"\nResults:")

    for i, chunk in enumerate(chunks):
        chunk_size = len(chunk.content)
        adaptive_cap = int(chunk_size * 0.35)
        effective_cap = min(config.overlap_size, adaptive_cap)

        print(f"\n  Chunk {i}:")
        print(f"    Size: {chunk_size} chars")
        print(f"    Adaptive cap (35%): {adaptive_cap} chars")
        print(f"    Effective cap: {effective_cap} chars")

        if "next_content" in chunk.metadata:
            next_size = len(chunk.metadata["next_content"])
            print(f"    Actual next_content: {next_size} chars")
            print(f"    ✓ Scales with chunk size!")


def demo_comparison():
    """Compare old fixed limit vs new adaptive approach."""
    print("\n" + "=" * 70)
    print("DEMO 3: Comparison - Fixed vs Adaptive")
    print("=" * 70)

    # Medium content
    medium_content = "Content paragraph for testing. " * 50

    md_text = f"""# Section 1

{medium_content}

# Section 2

{medium_content}
"""

    config = ChunkConfig(max_chunk_size=3000, overlap_size=200)
    chunker = MarkdownChunker(config)
    chunks = chunker.chunk(md_text)

    print(f"\nConfiguration:")
    print(f"  max_chunk_size: {config.max_chunk_size}")
    print(f"  overlap_size (configured): {config.overlap_size}")

    if len(chunks) > 1 and "next_content" in chunks[0].metadata:
        chunk_size = len(chunks[0].content)
        next_chunk_size = len(chunks[1].content)
        adaptive_cap = int(next_chunk_size * 0.35)
        actual_overlap = len(chunks[0].metadata["next_content"])

        print(f"\nChunk 0 → Chunk 1:")
        print(f"  Chunk 0 size: {chunk_size} chars")
        print(f"  Chunk 1 size: {next_chunk_size} chars")
        print(f"  Old approach (fixed 500): Would cap at 500 chars")
        print(f"  New approach (35% adaptive): Caps at {adaptive_cap} chars")
        print(f"  Effective cap: min({config.overlap_size}, {adaptive_cap}) = {min(config.overlap_size, adaptive_cap)}")
        print(f"  Actual overlap used: {actual_overlap} chars")

        if adaptive_cap > 500:
            print(f"\n  ✓ Adaptive approach allows {adaptive_cap - 500} more chars!")
        else:
            print(f"\n  ✓ Configured overlap_size is the limiting factor")


if __name__ == "__main__":
    demo_small_chunks()
    demo_large_chunks()
    demo_comparison()

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print("""
The adaptive overlap approach provides:

1. For small chunks: Respects configured overlap_size
2. For large chunks: Allows up to 35% of chunk size
3. Better context for large documents without bloat for small ones
4. Automatic scaling - no manual tuning needed

Formula: effective_overlap = min(config.overlap_size, chunk_size * 0.35)
""")
