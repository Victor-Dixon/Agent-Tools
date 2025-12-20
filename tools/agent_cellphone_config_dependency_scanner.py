#!/usr/bin/env python3
"""
Agent_Cellphone Config Dependency Scanner

Scans Agent_Cellphone codebase for config_manager.py and config.py imports
to create dependency map for Phase 2 migration.

V2 Compliant: <400 lines
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class ConfigDependencyScanner:
    """Scans codebase for config dependencies."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.dependencies: Dict[str, List[Dict]] = defaultdict(list)
        self.import_patterns = [
            (r'from\s+.*config_manager\s+import\s+([^\n]+)', 'config_manager'),
            (r'from\s+.*\.config_manager\s+import\s+([^\n]+)', 'config_manager'),
            (r'import\s+.*config_manager', 'config_manager'),
            (r'from\s+.*config\s+import\s+([^\n]+)', 'config'),
            (r'from\s+.*\.config\s+import\s+([^\n]+)', 'config'),
            (r'import\s+.*config\s+as', 'config'),
        ]
        
    def scan_repo(self) -> Dict[str, any]:
        """Scan repository for config dependencies."""
        if not self.repo_path.exists():
            return {'error': f'Repository not found: {self.repo_path}'}
        
        # Scan Python files
        python_files = list(self.repo_path.rglob('*.py'))
        
        for py_file in python_files:
            # Skip common non-code directories
            if any(skip in str(py_file) for skip in ['.git', '__pycache__', 'node_modules', '.venv', 'venv', '.pytest_cache']):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                self._scan_file(py_file, content)
            except Exception as e:
                print(f"Warning: Could not read {py_file}: {e}")
        
        return self._format_results()
    
    def _scan_file(self, file_path: Path, content: str):
        """Scan single file for config imports."""
        relative_path = str(file_path.relative_to(self.repo_path))
        
        for pattern, config_type in self.import_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                import_line = match.group(0).strip()
                
                # Extract imported items
                imported_items = []
                if 'import' in import_line:
                    if 'from' in import_line:
                        # from X import Y, Z
                        imported = match.group(1) if match.lastindex else ''
                        imported_items = [item.strip() for item in imported.split(',')]
                    else:
                        # import X
                        imported_items = [import_line.replace('import', '').strip()]
                
                self.dependencies[config_type].append({
                    'file': relative_path,
                    'line': line_num,
                    'import_statement': import_line,
                    'imported_items': imported_items,
                })
    
    def _format_results(self) -> Dict[str, any]:
        """Format scan results."""
        total_files = len(set(
            dep['file'] for deps in self.dependencies.values() for dep in deps
        ))
        
        return {
            'summary': {
                'total_files_with_config_imports': total_files,
                'config_manager_imports': len(self.dependencies.get('config_manager', [])),
                'config_imports': len(self.dependencies.get('config', [])),
            },
            'config_manager_dependencies': self.dependencies.get('config_manager', []),
            'config_dependencies': self.dependencies.get('config', []),
            'all_dependencies': dict(self.dependencies),
        }


def main():
    """Main entry point."""
    agent_cellphone_path = Path('D:/Agent_Cellphone')
    
    if not agent_cellphone_path.exists():
        print(f"❌ Agent_Cellphone repository not found at: {agent_cellphone_path}")
        print("   Please update the path in the script if needed.")
        return 1
    
    print("🔍 Agent_Cellphone Config Dependency Scanner")
    print("=" * 60)
    print(f"Scanning: {agent_cellphone_path}")
    print()
    
    scanner = ConfigDependencyScanner(agent_cellphone_path)
    results = scanner.scan_repo()
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return 1
    
    # Print summary
    summary = results['summary']
    print(f"📊 Summary:")
    print(f"   Files with config imports: {summary['total_files_with_config_imports']}")
    print(f"   config_manager imports: {summary['config_manager_imports']}")
    print(f"   config imports: {summary['config_imports']}")
    print()
    
    # Print config_manager dependencies
    if results['config_manager_dependencies']:
        print(f"📁 config_manager.py dependencies ({len(results['config_manager_dependencies'])}):")
        for dep in results['config_manager_dependencies'][:10]:  # Show first 10
            print(f"   {dep['file']}:{dep['line']} - {dep['import_statement'][:60]}")
        if len(results['config_manager_dependencies']) > 10:
            print(f"   ... and {len(results['config_manager_dependencies']) - 10} more")
        print()
    
    # Print config dependencies
    if results['config_dependencies']:
        print(f"📁 config.py dependencies ({len(results['config_dependencies'])}):")
        for dep in results['config_dependencies'][:10]:  # Show first 10
            print(f"   {dep['file']}:{dep['line']} - {dep['import_statement'][:60]}")
        if len(results['config_dependencies']) > 10:
            print(f"   ... and {len(results['config_dependencies']) - 10} more")
        print()
    
    # Save results
    output_file = Path(__file__).parent.parent / 'docs' / 'organization' / 'PHASE2_AGENT_CELLPHONE_DEPENDENCY_MAP.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Results saved to: {output_file}")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    exit(main())

