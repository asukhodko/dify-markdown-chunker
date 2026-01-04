#!/usr/bin/env python3
"""Analyze differences between debug and normal hierarchical chunking."""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple

def find_debug_normal_pairs():
    """Find matching debug/normal snapshot pairs."""
    snapshots_dir = Path("tests/golden_before_migration")
    
    # Load snapshot index
    with open(snapshots_dir / "snapshot_index.json", 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    debug_snapshots = {}
    normal_snapshots = {}
    
    # Categorize snapshots
    for snapshot_id, info in index["snapshots"].items():
        params = info["parameters"]
        if params.get("enable_hierarchy", False):
            key = (info["fixture_name"], 
                   params.get("include_metadata", True),
                   params.get("strategy", "auto"))
            
            if params.get("debug", False):
                debug_snapshots[key] = snapshot_id
            else:
                normal_snapshots[key] = snapshot_id
    
    # Find matching pairs
    pairs = []
    for key in debug_snapshots:
        if key in normal_snapshots:
            pairs.append((debug_snapshots[key], normal_snapshots[key], key))
    
    return pairs

def analyze_pair(debug_id: str, normal_id: str, key: Tuple[str, bool, str]):
    """Analyze a debug/normal pair."""
    snapshots_dir = Path("tests/golden_before_migration")
    
    # Load snapshots
    with open(snapshots_dir / f"{debug_id}.json", 'r', encoding='utf-8') as f:
        debug_data = json.load(f)
    
    with open(snapshots_dir / f"{normal_id}.json", 'r', encoding='utf-8') as f:
        normal_data = json.load(f)
    
    debug_output = debug_data["output"]
    normal_output = normal_data["output"]
    
    fixture_name, include_metadata, strategy = key
    
    print(f"\n=== {fixture_name} (metadata={include_metadata}, strategy={strategy}) ===")
    print(f"Debug chunks: {len(debug_output)}")
    print(f"Normal chunks: {len(normal_output)}")
    
    if len(debug_output) > len(normal_output):
        print("✓ Debug mode returns MORE chunks (includes root/intermediate)")
        
        # Analyze chunk types
        debug_types = []
        normal_types = []
        
        for i, chunk in enumerate(debug_output):
            if '<metadata>' in chunk:
                # Extract metadata
                start = chunk.find('<metadata>') + len('<metadata>')
                end = chunk.find('</metadata>')
                if start > 0 and end > 0:
                    try:
                        metadata_str = chunk[start:end].strip()
                        metadata = json.loads(metadata_str)
                        content_type = metadata.get('content_type', 'unknown')
                        is_root = metadata.get('is_root', False)
                        is_leaf = metadata.get('is_leaf', False)
                        hierarchy_level = metadata.get('hierarchy_level', -1)
                        
                        debug_types.append({
                            'index': i,
                            'content_type': content_type,
                            'is_root': is_root,
                            'is_leaf': is_leaf,
                            'hierarchy_level': hierarchy_level
                        })
                    except:
                        debug_types.append({'index': i, 'error': 'parse_failed'})
        
        for i, chunk in enumerate(normal_output):
            if '<metadata>' in chunk:
                start = chunk.find('<metadata>') + len('<metadata>')
                end = chunk.find('</metadata>')
                if start > 0 and end > 0:
                    try:
                        metadata_str = chunk[start:end].strip()
                        metadata = json.loads(metadata_str)
                        content_type = metadata.get('content_type', 'unknown')
                        is_root = metadata.get('is_root', False)
                        is_leaf = metadata.get('is_leaf', False)
                        hierarchy_level = metadata.get('hierarchy_level', -1)
                        
                        normal_types.append({
                            'index': i,
                            'content_type': content_type,
                            'is_root': is_root,
                            'is_leaf': is_leaf,
                            'hierarchy_level': hierarchy_level
                        })
                    except:
                        normal_types.append({'index': i, 'error': 'parse_failed'})
        
        print("\nDebug chunk types:")
        for chunk_info in debug_types[:5]:  # Show first 5
            print(f"  {chunk_info}")
        
        print("\nNormal chunk types:")
        for chunk_info in normal_types[:5]:  # Show first 5
            print(f"  {chunk_info}")
            
        # Count by type
        debug_root_count = sum(1 for c in debug_types if c.get('is_root', False))
        debug_leaf_count = sum(1 for c in debug_types if c.get('is_leaf', False))
        normal_root_count = sum(1 for c in normal_types if c.get('is_root', False))
        normal_leaf_count = sum(1 for c in normal_types if c.get('is_leaf', False))
        
        print(f"\nDebug: {debug_root_count} root, {debug_leaf_count} leaf")
        print(f"Normal: {normal_root_count} root, {normal_leaf_count} leaf")
        
    elif len(debug_output) == len(normal_output):
        print("⚠ Same chunk count - debug may affect metadata only")
    else:
        print("❌ Unexpected: normal has more chunks than debug")
    
    return {
        'fixture_name': fixture_name,
        'debug_count': len(debug_output),
        'normal_count': len(normal_output),
        'difference': len(debug_output) - len(normal_output)
    }

def main():
    """Main analysis function."""
    print("Analyzing debug vs normal hierarchical chunking differences...")
    
    pairs = find_debug_normal_pairs()
    print(f"Found {len(pairs)} debug/normal pairs to analyze")
    
    results = []
    for debug_id, normal_id, key in pairs[:5]:  # Analyze first 5 pairs
        result = analyze_pair(debug_id, normal_id, key)
        results.append(result)
    
    print("\n=== Summary ===")
    for result in results:
        diff = result['difference']
        print(f"{result['fixture_name']}: debug={result['debug_count']}, normal={result['normal_count']}, diff=+{diff}")
    
    print("\n=== Debug Logic Conclusion ===")
    print("Based on analysis:")
    print("- Debug mode (enable_hierarchy=True, debug=True): returns result.chunks (ALL chunks)")
    print("- Normal mode (enable_hierarchy=True, debug=False): returns result.get_flat_chunks() (LEAF only)")
    print("- Debug mode includes root chunks, intermediate chunks, and leaf chunks")
    print("- Normal mode includes only leaf chunks (actual content chunks)")

if __name__ == "__main__":
    main()