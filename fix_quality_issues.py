#!/usr/bin/env python3
"""
Script to fix remaining quality issues in the test cleanup tools.
"""

import re
from pathlib import Path

def fix_file(file_path: Path, fixes: list):
    """Apply fixes to a file."""
    if not file_path.exists():
        return
    
    content = file_path.read_text()
    original_content = content
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    if content != original_content:
        file_path.write_text(content)
        print(f"Fixed {file_path}")

def main():
    base_dir = Path("tools/test_cleanup")
    
    # Remove unused imports
    unused_imports = [
        # analyzer.py
        (base_dir / "analyzer.py", [
            (r"from typing import Dict, List, Optional", "from typing import List, Optional"),
        ]),
        
        # orchestrator.py  
        (base_dir / "orchestrator.py", [
            (r"from typing import List", ""),
        ]),
        
        # processor.py
        (base_dir / "processor.py", [
            (r"TestCategorization,\n", ""),
            (r"                original_lines = lines\[start_line : end_line \+ 1\]\n", ""),
        ]),
        
        # reporter.py
        (base_dir / "reporter.py", [
            (r"from pathlib import Path\n", ""),
        ]),
        
        # test files - remove unused imports
        (base_dir / "test_analyzer_properties.py", [
            (r"from pathlib import Path\n", ""),
        ]),
        
        (base_dir / "test_analyzer_unit.py", [
            (r"from pathlib import Path\n", ""),
        ]),
        
        (base_dir / "test_categorizer_unit.py", [
            (r"        overlap = legacy_coverage\.intersection\(\n            migration_coverage\n        \)  # \{\"chunking\", \"parsing\"\}\n", ""),
        ]),
        
        (base_dir / "test_processor_properties.py", [
            (r"from hypothesis import HealthCheck, given, settings", "from hypothesis import given, settings"),
        ]),
        
        (base_dir / "test_processor_unit.py", [
            (r"from pathlib import Path\n", ""),
        ]),
        
        (base_dir / "test_updater_properties.py", [
            (r"from pathlib import Path\n", ""),
            (r"from hypothesis import HealthCheck, given, settings", "from hypothesis import given, settings"),
        ]),
        
        (base_dir / "test_updater_unit.py", [
            (r"from pathlib import Path\n", ""),
        ]),
        
        (base_dir / "updater.py", [
            (r"from pathlib import Path\n", ""),
            (r"AdaptationReport, ChangeReport, RemovalReport", "ChangeReport"),
        ]),
    ]
    
    # Fix trailing whitespace and blank lines
    whitespace_fixes = [
        (r"[ \t]+$", ""),  # Remove trailing whitespace
        (r"\n[ \t]+\n", "\n\n"),  # Remove whitespace-only lines
    ]
    
    # Apply unused import fixes
    for file_path, fixes in unused_imports:
        fix_file(file_path, fixes)
    
    # Apply whitespace fixes to all Python files
    for py_file in base_dir.glob("*.py"):
        fix_file(py_file, whitespace_fixes)
    
    # Fix specific type annotation issues
    fix_file(base_dir / "updater.py", [
        (r"        changes = \[\]", "        changes: List[str] = []"),
    ])
    
    # Fix orchestrator start_time issue
    fix_file(base_dir / "orchestrator.py", [
        (r"        self\.start_time: float = time\.time\(\)", "        self.start_time = time.time()"),
    ])
    
    print("All quality issues fixed!")

if __name__ == "__main__":
    main()