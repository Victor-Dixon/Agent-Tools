#!/usr/bin/env python3
"""
TROOP Config Dependency Scanner

Scans TROOP codebase for config.py imports to create dependency map.

V2 Compliant: <400 lines
"""

import re
import json
from pathlib import Path
from collections import defaultdict


class TROOPConfigScanner:
    """Scans TROOP for config dependencies."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.dependencies = []
        
    def scan_repo(self) -> dict:
        """Scan repository for config dependencies."""
        if not self.repo_path.exists():
            return {'error': f'Repository not found: {self.repo_path}'}
        
        python_files = list(self.repo_path.rglob('*.py'))
        
        for py_file in python_files:
            if any(skip in str(py_file) for skip in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                self._scan_file(py_file, content)
            except Exception as e:
                print(f"Warning: Could not read {py_file}: {e}")
        
        return {
            'summary': {
                'total_files_with_config_imports': len(self.dependencies),
            },
            'dependencies': self.dependencies,
        }
    
    def _scan_file(self, file_path: Path, content: str):
        """Scan single file for config imports."""
        relative_path = str(file_path.relative_to(self.repo_path))
        
        patterns = [
            (r'from\s+.*config.*import', 'from_import'),
            (r'import\s+.*config', 'import'),
            (r'config_handling\.config', 'config_handling'),
        ]
        
        for pattern, import_type in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                import_line = match.group(0).strip()
                
                self.dependencies.append({
                    'file': relative_path,
                    'line': line_num,
                    'import_statement': import_line,
                    'import_type': import_type,
                })


def main():
    """Main entry point."""
    troop_path = Path('D:/TROOP')
    
    if not troop_path.exists():
        print(f"❌ TROOP repository not found at: {troop_path}")
        return 1
    
    print("🔍 TROOP Config Dependency Scanner")
    print("=" * 60)
    
    scanner = TROOPConfigScanner(troop_path)
    results = scanner.scan_repo()
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return 1
    
    summary = results['summary']
    print(f"📊 Summary:")
    print(f"   Files with config imports: {summary['total_files_with_config_imports']}")
    print()
    
    if results['dependencies']:
        print(f"📁 Config dependencies ({len(results['dependencies'])}):")
        for dep in results['dependencies'][:15]:
            print(f"   {dep['file']}:{dep['line']} - {dep['import_statement'][:60]}")
        if len(results['dependencies']) > 15:
            print(f"   ... and {len(results['dependencies']) - 15} more")
        print()
    
    output_file = Path(__file__).parent.parent / 'docs' / 'organization' / 'PHASE2_TROOP_DEPENDENCY_MAP.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Results saved to: {output_file}")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    exit(main())

