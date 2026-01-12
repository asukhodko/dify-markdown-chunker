#!/usr/bin/env python3
"""Verify documentation for compliance with requirements.

This script validates documentation files against the specification requirements:
- Checks for forbidden tokens (document_loader, embedding, vector_store)
- Validates parameters against canonical schema
- Verifies links and file references
- Checks auto-generated parameter table consistency
"""

import re
import yaml
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Set
import sys


class DocumentationValidator:
    """Validates documentation files against requirements."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # Forbidden tokens (complete ban as per requirements)
        self.forbidden_tokens = {
            'document_loader',
            'embedding', 
            'vector_store'
        }
        
        # Load canonical schema
        self.canonical_schema = self._load_canonical_schema()
    
    def _load_canonical_schema(self) -> Dict[str, Any]:
        """Load canonical parameter schema from tool YAML."""
        schema_path = self.project_root / "tools" / "markdown_chunk_tool.yaml"
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.errors.append(f"Failed to load canonical schema: {e}")
            return {}
    
    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🔍 Starting documentation validation...")
        
        # Check README
        readme_path = self.project_root / "README.md"
        if readme_path.exists():
            self._validate_readme(readme_path)
        else:
            self.errors.append("README.md not found")
        
        # Check docs directory
        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            self._validate_docs_directory(docs_dir)
        
        # Check examples
        examples_dir = self.project_root / "examples"
        if examples_dir.exists():
            self._validate_examples_directory(examples_dir)
        
        # Report results
        self._report_results()
        
        return len(self.errors) == 0
    
    def _validate_readme(self, readme_path: Path):
        """Validate README.md file."""
        print(f"📄 Validating {readme_path.name}...")
        
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"Failed to read {readme_path}: {e}")
            return
        
        # Check for forbidden tokens
        self._check_forbidden_tokens(content, readme_path.name)
        
        # Validate parameter table
        self._validate_parameter_table(content, readme_path.name)
        
        # Check required sections
        self._check_required_sections(content, readme_path.name)
        
        # Validate links
        self._validate_links(content, readme_path.name)
    
    def _validate_docs_directory(self, docs_dir: Path):
        """Validate all markdown files in docs directory."""
        print(f"📁 Validating docs directory...")
        
        for md_file in docs_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for forbidden tokens
                relative_path = md_file.relative_to(self.project_root)
                self._check_forbidden_tokens(content, str(relative_path))
                
            except Exception as e:
                self.warnings.append(f"Failed to read {md_file}: {e}")
    
    def _validate_examples_directory(self, examples_dir: Path):
        """Validate examples directory structure and files."""
        print(f"📁 Validating examples directory...")
        
        # Check required subdirectories
        required_dirs = ['inputs', 'configs', 'outputs']
        for dir_name in required_dirs:
            dir_path = examples_dir / dir_name
            if not dir_path.exists():
                self.errors.append(f"Missing required directory: examples/{dir_name}")
        
        # Validate config files reference existing inputs
        configs_dir = examples_dir / "configs"
        inputs_dir = examples_dir / "inputs"
        
        if configs_dir.exists() and inputs_dir.exists():
            self._validate_config_input_references(configs_dir, inputs_dir)
    
    def _check_forbidden_tokens(self, content: str, file_name: str):
        """Check for forbidden tokens in content."""
        content_lower = content.lower()
        
        for token in self.forbidden_tokens:
            if token in content_lower:
                # Find line numbers for better error reporting
                lines = content.split('\n')
                line_numbers = []
                for i, line in enumerate(lines, 1):
                    if token in line.lower():
                        line_numbers.append(i)
                
                self.errors.append(
                    f"Forbidden token '{token}' found in {file_name} "
                    f"at line(s): {', '.join(map(str, line_numbers))}"
                )
    
    def _validate_parameter_table(self, content: str, file_name: str):
        """Validate auto-generated parameter table against canonical schema."""
        # Find parameter table markers
        start_marker = "<!-- params-table:start -->"
        end_marker = "<!-- params-table:end -->"
        
        start_pos = content.find(start_marker)
        end_pos = content.find(end_marker)
        
        if start_pos == -1 or end_pos == -1:
            self.errors.append(f"Parameter table markers not found in {file_name}")
            return
        
        # Extract table content
        table_content = content[start_pos + len(start_marker):end_pos].strip()
        
        # Parse table rows
        table_rows = [line.strip() for line in table_content.split('\n') if line.strip()]
        if len(table_rows) < 3:  # Header + separator + at least one row
            self.errors.append(f"Invalid parameter table format in {file_name}")
            return
        
        # Extract parameter names from table
        table_params = set()
        for row in table_rows[2:]:  # Skip header and separator
            if row.startswith('|') and row.endswith('|'):
                cells = [cell.strip() for cell in row.split('|')[1:-1]]
                if cells:
                    param_name = cells[0].strip('`')
                    table_params.add(param_name)
        
        # Extract parameters from canonical schema
        schema_params = set()
        for param in self.canonical_schema.get('parameters', []):
            if param['name'] != 'input_text':  # Skip input_text
                schema_params.add(param['name'])
        
        # Check for missing or extra parameters
        missing_params = schema_params - table_params
        extra_params = table_params - schema_params
        
        if missing_params:
            self.errors.append(
                f"Parameters missing from table in {file_name}: {', '.join(missing_params)}"
            )
        
        if extra_params:
            self.errors.append(
                f"Extra parameters in table in {file_name}: {', '.join(extra_params)}"
            )
    
    def _check_required_sections(self, content: str, file_name: str):
        """Check for required sections in README."""
        required_sections = [
            "Что это такое",
            "Когда использовать", 
            "Быстрый старт в Dify UI",
            "Настройка параметров",
            "Формат выходных данных",
            "Стратегии разделения",
            "Troubleshooting"
        ]
        
        for section in required_sections:
            if section not in content:
                self.warnings.append(f"Required section '{section}' not found in {file_name}")
    
    def _validate_links(self, content: str, file_name: str):
        """Validate markdown links point to existing files."""
        # Find markdown links [text](path)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        
        for link_text, link_path in links:
            # Skip external URLs
            if link_path.startswith(('http://', 'https://', 'mailto:')):
                continue
            
            # Skip anchors
            if link_path.startswith('#'):
                continue
            
            # Check if file exists
            if '/' in link_path:
                full_path = self.project_root / link_path
            else:
                full_path = self.project_root / link_path
            
            if not full_path.exists():
                self.warnings.append(f"Broken link in {file_name}: {link_path}")
    
    def _validate_config_input_references(self, configs_dir: Path, inputs_dir: Path):
        """Validate that config files reference existing input files."""
        for config_file in configs_dir.glob("*.json"):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                input_file = config.get('input_file')
                if input_file:
                    input_path = inputs_dir / input_file
                    if not input_path.exists():
                        self.errors.append(
                            f"Config {config_file.name} references non-existent input: {input_file}"
                        )
                
            except Exception as e:
                self.warnings.append(f"Failed to parse config {config_file.name}: {e}")
    
    def _report_results(self):
        """Report validation results."""
        print("\n" + "="*60)
        print("📊 VALIDATION RESULTS")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All validation checks passed!")
        elif not self.errors:
            print(f"\n✅ Validation passed with {len(self.warnings)} warnings")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} errors and {len(self.warnings)} warnings")


def main():
    """Main function."""
    project_root = Path(__file__).parent.parent
    validator = DocumentationValidator(project_root)
    
    success = validator.validate_all()
    
    if success:
        print("\n🎉 Documentation validation completed successfully!")
        return 0
    else:
        print("\n💥 Documentation validation failed!")
        print("\nTo fix issues:")
        print("1. Remove all forbidden tokens (document_loader, embedding, vector_store)")
        print("2. Run 'python scripts/update_params_table.py' to update parameter table")
        print("3. Fix broken links and missing files")
        print("4. Re-run validation")
        return 1


if __name__ == "__main__":
    exit(main())