#!/usr/bin/env python3
"""Simple test script for migration adapter."""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from adapter import MigrationAdapter

def test_adapter():
    """Test basic adapter functionality."""
    print("Testing MigrationAdapter...")
    
    # Initialize adapter
    adapter = MigrationAdapter()
    print("✓ Adapter initialized")
    
    # Test config building
    config = adapter.build_chunker_config()
    print(f"✓ Config built: max_chunk_size={config.max_chunk_size}, overlap_size={config.overlap_size}")
    
    # Test flag parsing
    include_metadata, enable_hierarchy, debug = adapter.parse_tool_flags()
    print(f"✓ Flags parsed: metadata={include_metadata}, hierarchy={enable_hierarchy}, debug={debug}")
    
    # Test simple chunking
    text = "# Header\n\nThis is a test paragraph with some content."
    
    try:
        result = adapter.run_chunking(
            input_text=text,
            config=config,
            include_metadata=True,
            enable_hierarchy=False,
            debug=False
        )
        print(f"✓ Chunking successful: {len(result)} chunks")
        print(f"  First chunk preview: {result[0][:100]}...")
        
    except Exception as e:
        print(f"✗ Chunking failed: {e}")
        return False
    
    print("✓ All tests passed!")
    return True

if __name__ == "__main__":
    success = test_adapter()
    sys.exit(0 if success else 1)