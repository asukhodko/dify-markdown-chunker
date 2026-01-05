#!/usr/bin/env python3
"""Quick test of migration adapter."""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_basic_adapter():
    """Test basic adapter functionality."""
    try:
        from adapter import MigrationAdapter
        print("✓ Adapter imported successfully")
        
        adapter = MigrationAdapter()
        print("✓ Adapter initialized")
        
        # Test config building
        config = adapter.build_chunker_config()
        print(f"✓ Config built: {type(config).__name__}")
        
        # Test simple chunking
        text = "# Test Header\n\nThis is a simple test paragraph."
        
        result = adapter.run_chunking(
            input_text=text,
            config=config,
            include_metadata=True,
            enable_hierarchy=False,
            debug=False
        )
        
        print(f"✓ Chunking successful: {len(result)} chunks")
        if result:
            print(f"  First chunk preview: {result[0][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_adapter()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")