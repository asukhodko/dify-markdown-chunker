"""Pytest configuration for migration tests."""

import pytest
import json
from pathlib import Path
from typing import Dict, List, Any


@pytest.fixture
def baseline_fixtures_dir():
    """Path to baseline fixtures directory."""
    return Path(__file__).parent / "baseline_data" / "fixtures"


@pytest.fixture
def baseline_fixtures(baseline_fixtures_dir):
    """Load all baseline fixtures."""
    fixtures = {}
    for fixture_file in baseline_fixtures_dir.glob("*.md"):
        fixtures[fixture_file.stem] = fixture_file.read_text(encoding="utf-8")
    return fixtures


@pytest.fixture
def plugin_tool_params():
    """Load plugin tool parameters from baseline."""
    params_file = Path(__file__).parent / "baseline_data" / "plugin_tool_params.json"
    with open(params_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data["params"]


@pytest.fixture
def plugin_config_keys():
    """Load plugin config keys from baseline."""
    keys_file = Path(__file__).parent / "baseline_data" / "plugin_config_keys.json"
    with open(keys_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data["keys"]


@pytest.fixture
def param_test_matrix():
    """Fixed parameter matrix for migration testing (10-30 test cases)."""
    return [
        # Core combinations
        {"include_metadata": True, "enable_hierarchy": False, "strategy": "auto"},
        {"include_metadata": False, "enable_hierarchy": False, "strategy": "auto"},
        {"include_metadata": True, "enable_hierarchy": True, "debug": False, "strategy": "auto"},
        {"include_metadata": True, "enable_hierarchy": True, "debug": True, "strategy": "auto"},
        {"include_metadata": False, "enable_hierarchy": True, "debug": False, "strategy": "auto"},
        {"include_metadata": False, "enable_hierarchy": True, "debug": True, "strategy": "auto"},
        
        # Strategy variations
        {"include_metadata": True, "strategy": "code_aware"},
        {"include_metadata": True, "strategy": "list_aware"},
        {"include_metadata": True, "strategy": "structural"},
        {"include_metadata": True, "strategy": "fallback"},
        {"include_metadata": False, "strategy": "code_aware"},
        
        # Size variations
        {"include_metadata": True, "chunk_overlap": 0},
        {"include_metadata": True, "max_chunk_size": 1000},  # Small to trigger more chunks
        {"include_metadata": False, "chunk_overlap": 0},
        {"include_metadata": False, "max_chunk_size": 1000},
        
        # Hierarchy + strategy combinations
        {"include_metadata": True, "enable_hierarchy": True, "debug": False, "strategy": "code_aware"},
        {"include_metadata": True, "enable_hierarchy": True, "debug": True, "strategy": "structural"},
        
        # Edge cases
        {"include_metadata": True, "chunk_overlap": 500, "max_chunk_size": 2000},
        {"include_metadata": False, "chunk_overlap": 100, "max_chunk_size": 8192},
    ]


@pytest.fixture
def pre_migration_snapshot_dir():
    """Directory for pre-migration snapshots (will be created in task 1.3)."""
    return Path(__file__).parent / "golden_before_migration"


@pytest.fixture
def config_defaults_snapshot_file():
    """File for config defaults snapshot (will be created in task 1.3)."""
    return Path(__file__).parent / "config_defaults_snapshot.json"