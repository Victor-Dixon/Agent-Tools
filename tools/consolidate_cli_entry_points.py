#!/usr/bin/env python3
"""
Consolidate CLI Entry Points - Unified CLI Framework
====================================================

Identifies all CLI entry points (main() functions) and creates a unified CLI framework.
This addresses the 100+ duplicate main() functions found in project scan.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-04
V2 Compliant: Yes (<300 lines)
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent


def find_cli_entry_points(directory: Path) -> Dict[str, List[str]]:
    """Find all CLI entry points (main() functions and if __name__ == '__main__')."""
    cli_files = defaultdict(list)
    
    for py_file in directory.rglob("*.py"):
        # Skip certain directories
        if any(skip in str(py_file) for skip in ['__pycache__', '.git', 'node_modules', 'venv', 'htmlcov']):
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(py_file))
            
            has_main = False
            has_main_guard = False
            
            # Check for main() function
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == 'main':
                    has_main = True
                    break
            
            # Check for if __name__ == '__main__'
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    if isinstance(node.test, ast.Compare):
                        if (isinstance(node.test.left, ast.Name) and 
                            node.test.left.id == '__name__' and
                            len(node.test.comparators) == 1 and
                            isinstance(node.test.comparators[0], ast.Constant) and
                            node.test.comparators[0].value == '__main__'):
                            has_main_guard = True
                            break
            
            if has_main or has_main_guard:
                relative_path = str(py_file.relative_to(PROJECT_ROOT))
                cli_files[relative_path] = {
                    'has_main_function': has_main,
                    'has_main_guard': has_main_guard,
                    'file_path': relative_path
                }
        
        except Exception as e:
            # Skip files that can't be parsed
            continue
    
    return cli_files


def categorize_cli_files(cli_files: Dict) -> Dict[str, List[str]]:
    """Categorize CLI files by domain/functionality."""
    categories = defaultdict(list)
    
    for file_path, info in cli_files.items():
        path_parts = Path(file_path).parts
        
        # Categorize by directory structure
        if 'tools' in path_parts:
            if 'deprecated' in path_parts:
                categories['deprecated_tools'].append(file_path)
            else:
                categories['tools'].append(file_path)
        elif 'src' in path_parts:
            if 'cli' in file_path.lower():
                categories['src_cli'].append(file_path)
            elif 'services' in path_parts:
                categories['services_cli'].append(file_path)
            elif 'core' in path_parts:
                categories['core_cli'].append(file_path)
            else:
                categories['src_other'].append(file_path)
        elif 'agent_workspaces' in path_parts:
            categories['agent_scripts'].append(file_path)
        elif 'temp_repos' in path_parts:
            categories['temp_repos'].append(file_path)
        else:
            categories['root_scripts'].append(file_path)
    
    return categories


def generate_cli_framework_plan(categories: Dict[str, List[str]]) -> Dict:
    """Generate plan for unified CLI framework."""
    plan = {
        'total_cli_files': sum(len(files) for files in categories.values()),
        'categories': {cat: len(files) for cat, files in categories.items()},
        'consolidation_strategy': {
            'tools': 'Create tools/cli/ subdirectory with unified CLI dispatcher',
            'src_cli': 'Consolidate into src/core/cli/ with domain-specific commands',
            'services_cli': 'Migrate to src/services/cli/ with service-specific commands',
            'deprecated_tools': 'Archive or remove (already in deprecated/)',
            'temp_repos': 'Review and potentially remove (temporary)',
            'agent_scripts': 'Keep as-is (agent-specific)',
            'root_scripts': 'Review and consolidate into appropriate domain'
        },
        'recommended_structure': {
            'tools/cli/': 'Unified CLI dispatcher for all tool commands',
            'src/core/cli/': 'Core system CLI commands',
            'src/services/cli/': 'Service-specific CLI commands',
            'src/workflows/cli.py': 'Workflow CLI (already exists)',
            'src/vision/cli.py': 'Vision CLI (already exists)'
        }
    }
    
    return plan


def main():
    """Analyze CLI entry points and generate consolidation plan."""
    print("🔍 Finding CLI entry points...")
    print()
    
    # Find CLI files in src/ and tools/
    src_cli = find_cli_entry_points(PROJECT_ROOT / "src")
    tools_cli = find_cli_entry_points(PROJECT_ROOT / "tools")
    root_cli = find_cli_entry_points(PROJECT_ROOT)
    
    # Combine and deduplicate
    all_cli = {**src_cli, **tools_cli}
    # Remove tools from root_cli (already counted)
    for key in list(root_cli.keys()):
        if key.startswith('tools/') or key.startswith('src/'):
            del root_cli[key]
    all_cli.update(root_cli)
    
    print(f"📊 Found {len(all_cli)} CLI entry points")
    print()
    
    # Categorize
    categories = categorize_cli_files(all_cli)
    
    print("📋 Categories:")
    for cat, files in sorted(categories.items()):
        print(f"   {cat}: {len(files)} files")
    print()
    
    # Generate plan
    plan = generate_cli_framework_plan(categories)
    
    # Save results
    output_file = PROJECT_ROOT / "docs" / "archive" / "consolidation" / "cli_consolidation_plan.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'cli_files': all_cli,
            'categories': {cat: files for cat, files in categories.items()},
            'plan': plan
        }, f, indent=2)
    
    print(f"✅ CLI analysis saved to: {output_file}")
    print()
    print("🎯 Consolidation Strategy:")
    print(f"   • Total CLI files: {plan['total_cli_files']}")
    print(f"   • Tools CLI: {plan['categories'].get('tools', 0)} files → Consolidate into tools/cli/")
    print(f"   • Source CLI: {plan['categories'].get('src_cli', 0)} files → Consolidate into src/core/cli/")
    print(f"   • Deprecated: {plan['categories'].get('deprecated_tools', 0)} files → Archive/remove")


if __name__ == "__main__":
    main()

