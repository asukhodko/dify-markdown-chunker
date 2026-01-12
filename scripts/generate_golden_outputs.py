#!/usr/bin/env python3
"""Generate golden outputs for documentation examples.

This script runs the Advanced Markdown Chunker tool with each configuration
to generate reference outputs for documentation and testing.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path to import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from adapter import MigrationAdapter


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_input_text(input_file: str) -> str:
    """Load input text from examples/inputs directory."""
    input_path = project_root / "examples" / "inputs" / input_file
    with open(input_path, 'r', encoding='utf-8') as f:
        return f.read()


def run_tool_with_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Run the markdown chunk tool with given configuration."""
    # Load input text
    input_text = load_input_text(config["input_file"])
    
    # Extract parameters
    params = config["parameters"]
    max_chunk_size = params.get("max_chunk_size", 4096)
    chunk_overlap = params.get("chunk_overlap", 200)
    strategy = params.get("strategy", "auto")
    include_metadata = params.get("include_metadata", True)
    enable_hierarchy = params.get("enable_hierarchy", False)
    debug = params.get("debug", False)
    leaf_only = params.get("leaf_only", False)
    
    # Create adapter instance
    adapter = MigrationAdapter(leaf_only=leaf_only)
    
    # Build config using adapter
    chunker_config = adapter.build_chunker_config(
        max_chunk_size=max_chunk_size,
        chunk_overlap=chunk_overlap,
        strategy=strategy,
    )
    
    # Parse tool flags
    include_metadata, enable_hierarchy, debug, _ = adapter.parse_tool_flags(
        include_metadata=include_metadata,
        enable_hierarchy=enable_hierarchy,
        debug=debug,
        leaf_only=leaf_only,
    )
    
    # Run chunking through adapter
    results = adapter.run_chunking(
        input_text=input_text,
        config=chunker_config,
        include_metadata=include_metadata,
        enable_hierarchy=enable_hierarchy,
        debug=debug,
    )
    
    return {
        "config": config,
        "input_file": config["input_file"],
        "parameters": config["parameters"],
        "chunks": results,
        "chunk_count": len(results) if results else 0
    }


def main():
    """Generate golden outputs for all configurations."""
    configs_dir = project_root / "examples" / "configs"
    outputs_dir = project_root / "examples" / "outputs"
    
    # Create outputs directory if it doesn't exist
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each configuration file
    for config_file in configs_dir.glob("*.json"):
        print(f"Processing {config_file.name}...")
        
        try:
            # Load configuration
            config = load_config(config_file)
            
            # Run tool
            result = run_tool_with_config(config)
            
            # Save output
            output_file = outputs_dir / f"{config_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ Generated {result['chunk_count']} chunks -> {output_file.name}")
            
        except Exception as e:
            print(f"  ✗ Error processing {config_file.name}: {e}")
            continue
    
    print("\nGolden output generation complete!")


if __name__ == "__main__":
    main()