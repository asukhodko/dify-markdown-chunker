#!/usr/bin/env python3
"""
P1 Test Analysis Script

Analyzes legacy P1 tests to extract test intents and map them to v2 API concepts.
Produces structured output for test-intent-analysis.md.
"""

import ast
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class ExtractedIntent:
    """Represents the extracted intent of a single test."""
    file_path: str
    test_name: str
    intent: str
    v2_component: str
    test_type: str  # property, unit, integration
    property_statement: Optional[str] = None
    legacy_imports: List[str] = field(default_factory=list)
    v2_applicable: bool = True
    removed_functionality: bool = False
    notes: str = ""


@dataclass
class FileAnalysisResult:
    """Analysis result for a single test file."""
    file_path: str
    test_count: int
    legacy_imports: List[str]
    v2_applicable: bool
    removed_functionality: bool
    tests: List[ExtractedIntent]


# V2 component mapping rules
V2_COMPONENT_MAPPING = {
    # Parser-related
    'content_analysis': 'Parser.analyze() → ContentAnalysis',
    'fenced_block': 'ContentAnalysis.code_blocks',
    'header': 'ContentAnalysis.headers',
    'table': 'ContentAnalysis.tables',
    'preamble': 'ContentAnalysis.has_preamble',
    'line_number': 'ContentAnalysis (line positions)',
    'position': 'ContentAnalysis (positions)',
    'parser': 'Parser',
    
    # Chunker-related
    'chunk': 'MarkdownChunker.chunk() → List[Chunk]',
    'chunker': 'MarkdownChunker',
    'config': 'ChunkConfig',
    'overlap': 'ChunkConfig.overlap_size',
    'metadata': 'Chunk.metadata',
    'size': 'ChunkConfig.max_chunk_size / min_chunk_size',
    
    # Strategy-related
    'code_strategy': 'CodeAwareStrategy',
    'code_aware': 'CodeAwareStrategy',
    'structural': 'StructuralStrategy',
    'fallback': 'FallbackStrategy',
    'strategy': 'Strategy (base)',
    
    # Removed strategies (mark as not applicable)
    'list_strategy': 'REMOVED: ListStrategy',
    'table_strategy': 'REMOVED: TableStrategy',
    'sentences_strategy': 'REMOVED: SentencesStrategy',
    'mixed_strategy': 'REMOVED: MixedStrategy',
    
    # Other
    'serialization': 'Chunk.to_dict() / from_dict()',
    'validation': 'Validator',
    'error': 'Error handling',
    'integration': 'End-to-end pipeline',
    'performance': 'Performance',
    'regression': 'Regression prevention',
}

# Removed functionality patterns
REMOVED_PATTERNS = [
    'list_strategy', 'table_strategy', 'sentences_strategy', 'mixed_strategy',
    'stage1', 'stage2', 'phase1', 'phase2', 'block_packer',
    'nesting_resolver', 'legacy_ast', 'dynamic_strategy',
]


def discover_test_files(base_path: str, category: str = 'p1') -> List[str]:
    """Discover all test files in the given directory."""
    test_files = []
    base = Path(base_path)
    
    for path in base.rglob('test_*.py'):
        # Skip __pycache__ and other non-test directories
        if '__pycache__' in str(path):
            continue
        test_files.append(str(path))
    
    return sorted(test_files)


def extract_imports(tree: ast.AST) -> List[str]:
    """Extract all import statements from AST."""
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
    
    return imports


def extract_test_functions(tree: ast.AST) -> List[ast.FunctionDef]:
    """Extract all test functions/methods from AST."""
    tests = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith('test_'):
                tests.append(node)
        elif isinstance(node, ast.ClassDef):
            # Check for test classes
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name.startswith('test_'):
                        tests.append(item)
    
    return tests


def infer_test_type(test_name: str, docstring: str, imports: List[str]) -> str:
    """Infer test type from name, docstring, and imports."""
    name_lower = test_name.lower()
    doc_lower = docstring.lower() if docstring else ''
    
    # Check for property-based testing
    if any('hypothesis' in imp for imp in imports):
        return 'property'
    if 'property' in name_lower or 'property' in doc_lower:
        return 'property'
    if '@given' in doc_lower or 'for any' in doc_lower or 'for all' in doc_lower:
        return 'property'
    
    # Check for integration tests
    if 'integration' in name_lower or 'e2e' in name_lower or 'end_to_end' in name_lower:
        return 'integration'
    if 'full_pipeline' in name_lower or 'full_api' in name_lower:
        return 'integration'
    
    return 'unit'


def infer_v2_component(test_name: str, file_path: str, imports: List[str]) -> str:
    """Infer the V2 component being tested."""
    name_lower = test_name.lower()
    path_lower = file_path.lower()
    
    # Check file path first
    if '/parser/' in path_lower:
        # More specific parser components
        for key, component in V2_COMPONENT_MAPPING.items():
            if key in name_lower:
                return component
        return 'Parser'
    
    if '/chunker/' in path_lower:
        # Check for specific strategies
        if 'code' in name_lower and 'strategy' in name_lower:
            return V2_COMPONENT_MAPPING['code_aware']
        if 'structural' in name_lower:
            return V2_COMPONENT_MAPPING['structural']
        if 'fallback' in name_lower:
            return V2_COMPONENT_MAPPING['fallback']
        if 'list_strategy' in name_lower or 'list_strategy' in path_lower:
            return V2_COMPONENT_MAPPING['list_strategy']
        if 'table_strategy' in name_lower or 'table_strategy' in path_lower:
            return V2_COMPONENT_MAPPING['table_strategy']
        if 'sentences' in name_lower or 'sentences' in path_lower:
            return V2_COMPONENT_MAPPING['sentences_strategy']
        if 'mixed' in name_lower or 'mixed' in path_lower:
            return V2_COMPONENT_MAPPING['mixed_strategy']
        
        # Other chunker components
        for key, component in V2_COMPONENT_MAPPING.items():
            if key in name_lower:
                return component
        return 'MarkdownChunker'
    
    if '/integration/' in path_lower:
        return 'End-to-end pipeline'
    
    if '/api/' in path_lower:
        return 'API layer'
    
    if '/regression/' in path_lower:
        return 'Regression prevention'
    
    if '/performance/' in path_lower:
        return 'Performance'
    
    # Default: try to match by name
    for key, component in V2_COMPONENT_MAPPING.items():
        if key in name_lower:
            return component
    
    return 'Unknown'


def is_removed_functionality(test_name: str, file_path: str, imports: List[str]) -> bool:
    """Check if test covers removed functionality."""
    combined = (test_name + file_path + ' '.join(imports)).lower()
    
    for pattern in REMOVED_PATTERNS:
        if pattern in combined:
            return True
    
    return False


def extract_intent_from_docstring(docstring: str, test_name: str) -> str:
    """Extract or generate intent description from docstring."""
    if docstring:
        # Clean up docstring
        lines = docstring.strip().split('\n')
        # Take first non-empty line as intent
        for line in lines:
            line = line.strip()
            if line and not line.startswith(':'):
                return line
    
    # Generate intent from test name
    # Convert test_something_works to "Verify something works"
    name = test_name.replace('test_', '').replace('_', ' ')
    return f"Verify {name}"


def extract_property_statement(docstring: str, test_name: str) -> Optional[str]:
    """Extract formal property statement if present."""
    if not docstring:
        return None
    
    doc_lower = docstring.lower()
    
    # Look for "for any" or "for all" patterns
    patterns = [
        r'for any[^.]+\.',
        r'for all[^.]+\.',
        r'property:[^.]+\.',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, doc_lower, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    
    return None


def analyze_test_file(file_path: str) -> FileAnalysisResult:
    """Analyze a single test file and extract all test intents."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return FileAnalysisResult(
            file_path=file_path,
            test_count=0,
            legacy_imports=[],
            v2_applicable=False,
            removed_functionality=False,
            tests=[]
        )
    
    imports = extract_imports(tree)
    test_functions = extract_test_functions(tree)
    
    # Check for legacy imports
    legacy_imports = [imp for imp in imports if 'markdown_chunker.' in imp and 'markdown_chunker_v2' not in imp]
    
    # Check if file tests removed functionality
    removed = is_removed_functionality('', file_path, imports)
    
    tests = []
    for func in test_functions:
        docstring = ast.get_docstring(func) or ''
        test_name = func.name
        
        test_type = infer_test_type(test_name, docstring, imports)
        v2_component = infer_v2_component(test_name, file_path, imports)
        intent = extract_intent_from_docstring(docstring, test_name)
        property_stmt = extract_property_statement(docstring, test_name) if test_type == 'property' else None
        test_removed = is_removed_functionality(test_name, file_path, imports)
        
        tests.append(ExtractedIntent(
            file_path=file_path,
            test_name=test_name,
            intent=intent,
            v2_component=v2_component,
            test_type=test_type,
            property_statement=property_stmt,
            legacy_imports=legacy_imports,
            v2_applicable=not test_removed and 'REMOVED' not in v2_component,
            removed_functionality=test_removed or 'REMOVED' in v2_component,
            notes=''
        ))
    
    return FileAnalysisResult(
        file_path=file_path,
        test_count=len(tests),
        legacy_imports=legacy_imports,
        v2_applicable=not removed,
        removed_functionality=removed,
        tests=tests
    )


def analyze_directory(directory: str) -> List[FileAnalysisResult]:
    """Analyze all test files in a directory."""
    test_files = discover_test_files(directory)
    results = []
    
    for file_path in test_files:
        analysis = analyze_test_file(file_path)
        if analysis.test_count > 0:
            results.append(analysis)
    
    return results


def format_test_intent_yaml(intent: ExtractedIntent) -> str:
    """Format a single test intent as YAML."""
    lines = [
        f"  - name: {intent.test_name}",
        f"    intent: \"{intent.intent}\"",
        f"    v2_component: {intent.v2_component}",
        f"    test_type: {intent.test_type}",
        f"    v2_applicable: {str(intent.v2_applicable).lower()}",
        f"    removed_functionality: {str(intent.removed_functionality).lower()}",
    ]
    
    if intent.property_statement:
        lines.append(f"    property: \"{intent.property_statement}\"")
    
    if intent.notes:
        lines.append(f"    notes: \"{intent.notes}\"")
    
    return '\n'.join(lines)


def format_file_analysis_yaml(analysis: FileAnalysisResult) -> str:
    """Format a file analysis as YAML."""
    lines = [
        f"test_file: {analysis.file_path}",
        f"test_count: {analysis.test_count}",
        f"legacy_imports:",
    ]
    
    for imp in analysis.legacy_imports[:5]:  # Limit to 5 imports
        lines.append(f"  - {imp}")
    
    lines.extend([
        f"v2_applicable: {str(analysis.v2_applicable).lower()}",
        f"removed_functionality: {str(analysis.removed_functionality).lower()}",
        "",
        "tests:",
    ])
    
    for test in analysis.tests:
        lines.append(format_test_intent_yaml(test))
    
    return '\n'.join(lines)


def generate_markdown_section(analyses: List[FileAnalysisResult], section_name: str) -> str:
    """Generate a markdown section for a group of analyses."""
    total_tests = sum(a.test_count for a in analyses)
    applicable_tests = sum(
        sum(1 for t in a.tests if t.v2_applicable) 
        for a in analyses
    )
    removed_tests = sum(
        sum(1 for t in a.tests if t.removed_functionality)
        for a in analyses
    )
    
    lines = [
        f"## {section_name}",
        "",
        f"**Files analyzed**: {len(analyses)}",
        f"**Total tests**: {total_tests}",
        f"**V2 applicable**: {applicable_tests}",
        f"**Removed functionality**: {removed_tests}",
        "",
    ]
    
    for analysis in analyses:
        lines.append(f"### {analysis.file_path}")
        lines.append("")
        lines.append("```yaml")
        lines.append(format_file_analysis_yaml(analysis))
        lines.append("```")
        lines.append("")
    
    return '\n'.join(lines)


def main():
    """Main entry point for the analysis script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze P1 tests')
    parser.add_argument('--output', '-o', default='docs/legacy-tests-analysis/test-intent-analysis.md',
                        help='Output file path')
    parser.add_argument('--directory', '-d', default='tests',
                        help='Test directory to analyze')
    args = parser.parse_args()
    
    print(f"Analyzing tests in {args.directory}...")
    
    # Analyze each subdirectory
    sections = {
        'Parser Tests': 'tests/parser',
        'Chunker Tests': 'tests/chunker',
        'Integration Tests': 'tests/integration',
        'API Tests': 'tests/api',
        'Regression Tests': 'tests/regression',
        'Performance Tests': 'tests/performance',
    }
    
    all_analyses = {}
    total_tests = 0
    total_applicable = 0
    total_removed = 0
    
    for section_name, directory in sections.items():
        if os.path.exists(directory):
            analyses = analyze_directory(directory)
            all_analyses[section_name] = analyses
            
            section_tests = sum(a.test_count for a in analyses)
            section_applicable = sum(sum(1 for t in a.tests if t.v2_applicable) for a in analyses)
            section_removed = sum(sum(1 for t in a.tests if t.removed_functionality) for a in analyses)
            
            total_tests += section_tests
            total_applicable += section_applicable
            total_removed += section_removed
            
            print(f"  {section_name}: {len(analyses)} files, {section_tests} tests")
    
    # Generate output
    output_lines = [
        "# Test Intent Analysis",
        "",
        "This document contains the extracted intents from all P1 legacy tests,",
        "mapped to v2 API concepts.",
        "",
        "## Summary",
        "",
        f"- **Total test files analyzed**: {sum(len(a) for a in all_analyses.values())}",
        f"- **Total tests**: {total_tests}",
        f"- **V2 applicable tests**: {total_applicable}",
        f"- **Removed functionality tests**: {total_removed}",
        "",
    ]
    
    for section_name, analyses in all_analyses.items():
        output_lines.append(generate_markdown_section(analyses, section_name))
    
    # Write output
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"\nOutput written to {args.output}")
    print(f"Total: {total_tests} tests analyzed")


if __name__ == '__main__':
    main()
