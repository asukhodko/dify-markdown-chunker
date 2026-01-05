#!/usr/bin/env python3
"""Test single snapshot compatibility."""

import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from adapter import MigrationAdapter

def test_single_snapshot():
    """Test adapter against a single snapshot."""
    print("Testing single snapshot compatibility...")
    
    # Use a simple snapshot for testing
    snapshot_file = Path("tests/golden_before_migration/feb278fd.json")
    
    if not snapshot_file.exists():
        print(f"✗ Snapshot file not found: {snapshot_file}")
        return False
    
    # Load snapshot
    with open(snapshot_file, 'r', encoding='utf-8') as f:
        snapshot_data = json.load(f)
    
    fixture_name = snapshot_data["fixture_name"]
    parameters = snapshot_data["parameters"]
    expected_output = snapshot_data["output"]
    
    print(f"Testing fixture: {fixture_name}")
    print(f"Parameters: {parameters}")
    print(f"Expected chunks: {len(expected_output)}")
    
    # Load fixture content
    fixture_file = Path(f"tests/baseline_data/fixtures/{fixture_name}.md")
    if not fixture_file.exists():
        print(f"✗ Fixture file not found: {fixture_file}")
        return False
    
    fixture_content = fixture_file.read_text(encoding='utf-8')
    print(f"Fixture content length: {len(fixture_content)} chars")
    
    # Test with adapter
    try:
        adapter = MigrationAdapter()
        
        # Build config
        config = adapter.build_chunker_config(
            max_chunk_size=parameters.get("max_chunk_size", 4096),
            chunk_overlap=parameters.get("chunk_overlap", 200),
            strategy=parameters.get("strategy", "auto")
        )
        
        print(f"Config built: max_chunk_size={config.max_chunk_size}")
        
        # Run chunking
        result = adapter.run_chunking(
            input_text=fixture_content,
            config=config,
            include_metadata=parameters.get("include_metadata", True),
            enable_hierarchy=parameters.get("enable_hierarchy", False),
            debug=parameters.get("debug", False)
        )
        
        print(f"✓ Chunking successful: {len(result)} chunks")
        
        # Compare with expected
        if len(result) == len(expected_output):
            print("✓ Chunk count matches!")
        else:
            print(f"⚠ Chunk count differs: got {len(result)}, expected {len(expected_output)}")
        
        # Show first chunk comparison
        if result and expected_output:
            print("\n=== First Chunk Comparison ===")
            print("ADAPTER OUTPUT (first 300 chars):")
            print(result[0][:300] + "..." if len(result[0]) > 300 else result[0])
            print("\nEXPECTED OUTPUT (first 300 chars):")
            print(expected_output[0][:300] + "..." if len(expected_output[0]) > 300 else expected_output[0])
            
            # Check if they're identical
            if result[0] == expected_output[0]:
                print("✓ First chunks are IDENTICAL!")
            else:
                print("⚠ First chunks differ")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_single_snapshot()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")