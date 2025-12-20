#!/usr/bin/env python3
"""
Architectural Checker - Detect Architectural Issues Before Runtime
Finds missing methods, circular imports, and architectural bugs.
"""

import sys
import ast
import re
from pathlib import Path
from typing import List, Dict, Set

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))


def extract_method_calls(file_path: Path) -> List[Dict]:
    """Extract all method calls from a file."""
    calls = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    calls.append({
                        'line': node.lineno,
                        'method': node.func.attr,
                        'object': ast.unparse(node.func.value) if hasattr(ast, 'unparse') else 'unknown'
                    })
    except Exception as e:
        print(f"⚠️  Could not parse {file_path}: {e}")
    
    return calls


def extract_class_methods(file_path: Path) -> Dict[str, List[str]]:
    """Extract all methods defined in classes."""
    class_methods = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(item.name)
                class_methods[node.name] = methods
    except Exception as e:
        print(f"⚠️  Could not parse {file_path}: {e}")
    
    return class_methods


def find_missing_methods(file_path: Path) -> List[Dict]:
    """Find method calls to undefined methods."""
    issues = []
    
    # Get method calls and class definitions
    calls = extract_method_calls(file_path)
    class_methods = extract_class_methods(file_path)
    
    # Check for self.method() calls
    for call in calls:
        if call['object'] == 'self':
            # Find which class this is in
            found = False
            for class_name, methods in class_methods.items():
                if call['method'] in methods:
                    found = True
                    break
            
            if not found and not call['method'].startswith('_'):
                issues.append({
                    'file': file_path,
                    'line': call['line'],
                    'type': 'missing_method',
                    'method': call['method'],
                    'message': f"Method '{call['method']}' called but not defined in any class"
                })
    
    return issues


def find_circular_imports(directory: Path) -> List[Dict]:
    """Find potential circular import issues."""
    import_graph = {}
    
    # Build import graph
    for py_file in directory.rglob("*.py"):
        imports = set()
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract imports
            import_pattern = r'from\s+([\w.]+)\s+import'
            for match in re.finditer(import_pattern, content):
                module = match.group(1)
                if module.startswith('src.'):
                    imports.add(module)
            
            import_graph[str(py_file.relative_to(repo_root))] = imports
        except:
            pass
    
    # Detect cycles
    issues = []
    for file, imports in import_graph.items():
        for imported in imports:
            # Check if imported module imports this file back
            imported_path = imported.replace('.', '/') + '.py'
            if imported_path in import_graph:
                if any(imp in file for imp in import_graph[imported_path]):
                    issues.append({
                        'type': 'circular_import',
                        'file1': file,
                        'file2': imported_path,
                        'message': f"Potential circular import: {file} ↔ {imported_path}"
                    })
    
    return issues


def main():
    """Run architectural checks."""
    
    if len(sys.argv) < 2:
        print("Usage: python captain_architectural_checker.py <file-or-directory>")
        print("\nExamples:")
        print("  python captain_architectural_checker.py src/core/messaging_pyautogui.py")
        print("  python captain_architectural_checker.py src/services/")
        return 1
    
    target = Path(sys.argv[1])
    
    if not target.exists():
        print(f"❌ Path not found: {target}")
        return 1
    
    print(f"🔍 ARCHITECTURAL ANALYSIS")
    print(f"=" * 70)
    print(f"Target: {target}")
    print(f"=" * 70)
    print()
    
    all_issues = []
    
    # Check missing methods
    if target.is_file():
        files_to_check = [target]
    else:
        files_to_check = list(target.rglob("*.py"))
    
    print(f"🔎 CHECKING MISSING METHODS")
    print(f"-" * 70)
    
    for file_path in files_to_check:
        issues = find_missing_methods(file_path)
        all_issues.extend(issues)
        
        if issues:
            print(f"\n⚠️  {file_path.relative_to(repo_root)}")
            for issue in issues:
                print(f"   Line {issue['line']}: {issue['message']}")
    
    if not any(i['type'] == 'missing_method' for i in all_issues):
        print("✅ No missing methods found")
    print()
    
    # Check circular imports
    if target.is_dir():
        print(f"🔄 CHECKING CIRCULAR IMPORTS")
        print(f"-" * 70)
        
        circular_issues = find_circular_imports(target)
        all_issues.extend(circular_issues)
        
        if circular_issues:
            for issue in circular_issues:
                print(f"⚠️  {issue['message']}")
        else:
            print("✅ No circular imports detected")
        print()
    
    # Summary
    print(f"=" * 70)
    print(f"📊 SUMMARY")
    print(f"=" * 70)
    print(f"Files checked: {len(files_to_check)}")
    print(f"Total issues: {len(all_issues)}")
    print(f"- Missing methods: {len([i for i in all_issues if i['type'] == 'missing_method'])}")
    print(f"- Circular imports: {len([i for i in all_issues if i['type'] == 'circular_import'])}")
    print()
    
    if all_issues:
        print(f"❌ Found {len(all_issues)} architectural issues!")
        return 1
    else:
        print("✅ No architectural issues found!")
        return 0

if __name__ == "__main__":
    sys.exit(main())

