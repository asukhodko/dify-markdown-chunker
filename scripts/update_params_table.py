#!/usr/bin/env python3
"""Update parameters table in README from tool schema.

This script reads the canonical parameter schema from tools/markdown_chunk_tool.yaml
and updates the auto-generated table in README between the markers.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, Any, List


def load_tool_schema() -> Dict[str, Any]:
    """Load tool schema from YAML file."""
    schema_path = Path(__file__).parent.parent / "tools" / "markdown_chunk_tool.yaml"
    with open(schema_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def extract_parameters(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract parameter information from schema."""
    parameters = []
    
    for param in schema.get('parameters', []):
        # Skip input_text as it's not a configuration parameter
        if param['name'] == 'input_text':
            continue
            
        param_info = {
            'name': param['name'],
            'type': param['type'],
            'required': param.get('required', False),
            'default': param.get('default', ''),
            'description': param.get('human_description', {}).get('ru_RU', 
                          param.get('human_description', {}).get('en_US', ''))
        }
        
        # Handle select type with options
        if param['type'] == 'select' and 'options' in param:
            options = [opt['value'] for opt in param['options']]
            param_info['options'] = options
            
        parameters.append(param_info)
    
    return parameters


def format_parameter_type(param: Dict[str, Any]) -> str:
    """Format parameter type for display."""
    param_type = param['type']
    
    if param_type == 'select':
        return 'выбор'
    elif param_type == 'number':
        return 'число'
    elif param_type == 'boolean':
        return 'булево'
    elif param_type == 'string':
        return 'строка'
    else:
        return param_type


def format_default_value(param: Dict[str, Any]) -> str:
    """Format default value for display."""
    default = param.get('default', '')
    
    if default == '':
        return '-' if param.get('required', False) else ''
    elif isinstance(default, bool):
        return 'true' if default else 'false'
    else:
        return str(default)


def generate_table(parameters: List[Dict[str, Any]]) -> str:
    """Generate markdown table from parameters."""
    lines = [
        "| Параметр | Тип | По умолчанию | Описание |",
        "|----------|-----|--------------|----------|"
    ]
    
    for param in parameters:
        name = f"`{param['name']}`"
        param_type = format_parameter_type(param)
        default = format_default_value(param)
        description = param.get('description', '').strip()
        
        # Add options info for select type
        if param['type'] == 'select' and 'options' in param:
            options_str = '/'.join(param['options'])
            description += f" ({options_str})"
        
        lines.append(f"| {name} | {param_type} | {default} | {description} |")
    
    return '\n'.join(lines)


def update_readme_table(readme_path: Path, new_table: str) -> bool:
    """Update the parameters table in README file."""
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the markers
    start_marker = "<!-- params-table:start -->"
    end_marker = "<!-- params-table:end -->"
    
    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker)
    
    if start_pos == -1 or end_pos == -1:
        print(f"❌ Markers not found in {readme_path}")
        return False
    
    # Replace content between markers
    new_content = (
        content[:start_pos + len(start_marker)] +
        '\n' + new_table + '\n' +
        content[end_pos:]
    )
    
    # Write back to file
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True


def main():
    """Main function."""
    try:
        # Load schema and extract parameters
        schema = load_tool_schema()
        parameters = extract_parameters(schema)
        
        print(f"📋 Extracted {len(parameters)} parameters from schema")
        
        # Generate table
        table = generate_table(parameters)
        print("📝 Generated parameters table")
        
        # Update README files
        project_root = Path(__file__).parent.parent
        readme_files = [
            project_root / "README_new.md",
            project_root / "README.md"  # Update both files
        ]
        
        updated_count = 0
        for readme_path in readme_files:
            if readme_path.exists():
                if update_readme_table(readme_path, table):
                    print(f"✅ Updated {readme_path.name}")
                    updated_count += 1
                else:
                    print(f"⚠️  Could not update {readme_path.name}")
        
        if updated_count > 0:
            print(f"\n🎉 Successfully updated {updated_count} README file(s)")
        else:
            print("\n❌ No README files were updated")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())