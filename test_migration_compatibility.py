#!/usr/bin/env python3
"""Test migration compatibility by comparing outputs."""

import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from adapter import MigrationAdapter

def test_migration_compatibility():
    """Test that migration adapter produces expected outputs."""
    print("Testing migration compatibility...")
    
    # Load one snapshot for comparison
    snapshots_dir = Path("tests/golden_before_migration")
    snapshot_files = list(snapshots_dir.glob("*.json"))
    
    if not snapshot_files:
        print("✗ No snapshots found")
        return False
    
    # Test with first snapshot
    snapshot_file = snapshot_files[0]
    print(f"Testing with snapshot: {snapshot_file.name}")
    
    with open(snapshot_file, 'r', encoding='utf-8') as f:
        snapshot_data = json.load(f)
    
    fixture_name = snapshot_data["fixture_name"]
    parameters = snapshot_data["parameters"]
    expected_output = snapshot_data["output"]
    
    print(f"Fixture: {fixture_name}")
    print(f"Parameters: {parameters}")
    
    # Load fixture content
    fixture_file = Path(f"tests/baseline_data/fixtures/{fixture_name}.md")
    if not fixture_file.exists():
        print(f"✗ Fixture file not found: {fixture_file}")
        return False
    
    fixture_content = fixture_file.read_text(encoding='utf-8')
    
    # Test with adapter
    adapter = MigrationAdapter()
    
    try:
        # Build config
        config = adapter.build_chunker_config(
            max_chunk_size=parameters.get("max_chunk_size", 4096),
            chunk_overlap=parameters.get("chunk_overlap", 200),
            strategy=parameters.get("strategy", "auto")
        )
        
        # Run chunking
        result = adapter.run_chunking(
            input_text=fixture_content,
            config=config,
            include_metadata=parameters.get("include_metadata", True),
            enable_hierarchy=parameters.get("enable_hierarchy", False),
            debug=parameters.get("debug", False)
        )
        
        print(f"✓ Chunking successful: {len(result)} chunks")
        print(f"✓ Expected: {len(expected_output)} chunks")
        
        if len(result) == len(expected_output):
            print("✓ Chunk count matches!")
        else:
            print(f"⚠ Chunk count differs: got {len(result)}, expected {len(expected_output)}")
        
        # Show first chunk comparison
        if result and expected_output:
            print("\nFirst chunk comparison:")
            print("=== ADAPTER OUTPUT ===")
            print(result[0][:200] + "..." if len(result[0]) > 200 else result[0])
            print("\n=== EXPECTED OUTPUT ===")
            print(expected_output[0][:200] + "..." if len(expected_output[0]) > 200 else expected_output[0])
        
        return True
        
    except Exception as e:
        print(f"✗ Migration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_migration_compatibility()
    sys.exit(0 if success else 1)