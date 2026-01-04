#!/usr/bin/env python3
"""Analyze debug behavior from pre-migration snapshots."""

import json
from pathlib import Path
from typing import Dict, List, Any

def analyze_debug_behavior():
    """Analyze debug behavior patterns from snapshots."""
    print("Analyzing debug behavior from snapshots...")
    
    snapshots_dir = Path("tests/golden_before_migration")
    
    # Load snapshot index
    with open(snapshots_dir / "snapshot_index.json", 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    debug_snapshots = []
    normal_snapshots = []
    
    # Find debug vs normal snapshots with hierarchy enabled
    for snapshot_id, info in index["snapshots"].items():
        params = info["parameters"]
        if params.get("enable_hierarchy", False):
            if params.get("debug", False):
                debug_snapshots.append((snapshot_id, info))
            else:
                normal_snapshots.append((snapshot_id, info))
    
    print(f"Found {len(debug_snapshots)} debug snapshots")
    print(f"Found {len(normal_snapshots)} normal hierarchical snapshots")
    
    # Find matching pairs (same fixture, same params except debug)
    pairs = []
    for debug_id, debug_info in debug_snapshots:
        debug_params = debug_info["parameters"].copy()
        debug_params["debug"] = False  # Look for matching normal version
        
        for normal_id, normal_info in normal_snapshots:
            if (normal_info["fixture_name"] == debug_info["fixture_name"] and
                normal_info["parameters"] == debug_params):
                pairs.append((debug_id, normal_id, debug_info["fixture_name"]))
                break
    
    print(f"Found {len(pairs)} matching debug/normal pairs")
    
    # Analyze differences
    for debug_id, normal_id, fixture_name in pairs[:3]:  # Analyze first 3 pairs
        print(f"\n=== Analyzing {fixture_name} ===")
        
        # Load snapshots
        with open(snapshots_dir / f"{debug_id}.json", 'r', encoding='utf-8') as f:
            debug_data = json.load(f)
        
        with open(snapshots_dir / f"{normal_id}.json", 'r', encoding='utf-8') as f:
            normal_data = json.load(f)
        
        debug_output = debug_data["output"]
        normal_output = normal_data["output"]
        
        print(f"Debug chunks: {len(debug_output)}")
        print(f"Normal chunks: {len(normal_output)}")
        
        if len(debug_output) > len(normal_output):
            print("Debug mode returns MORE chunks (includes intermediate/root)")
            
            # Show first few chunks to understand structure
            print("\nFirst debug chunk:")
            print(debug_output[0][:300] + "..." if len(debug_output[0]) > 300 else debug_output[0])
            
            print("\nFirst normal chunk:")
            print(normal_output[0][:300] + "..." if len(normal_output[0]) > 300 else normal_output[0])
            
        elif len(debug_output) == len(normal_output):
            print("Same chunk count - debug may affect metadata only")
        else:
            print("Unexpected: normal has more chunks than debug")
    
    return pairs

def extract_debug_logic():
    """Extract debug logic patterns."""
    print("\n=== Debug Logic Analysis ===")
    print("Based on original tool code:")
    print("- enable_hierarchy=True, debug=True: returns result.chunks (all chunks)")
    print("- enable_hierarchy=True, debug=False: returns result.get_flat_chunks() (leaf only)")
    print("- enable_hierarchy=False: debug flag ignored")
    print("\nThis suggests debug mode in hierarchical chunking includes:")
    print("- Root chunks (document-level)")
    print("- Intermediate chunks (section-level)")
    print("- Leaf chunks (content-level)")
    print("\nWhile normal mode only returns leaf chunks for actual content.")

if __name__ == "__main__":
    pairs = analyze_debug_behavior()
    extract_debug_logic()