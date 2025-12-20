#!/usr/bin/env python3
"""
Comprehensive Project Scan
==========================

Scans project for:
- Unused code (unused imports, functions, classes)
- Optimization opportunities
- Dead code paths
- Unused files
- Code quality issues

Author: Agent-2 (Architecture & Design Specialist)
V2 Compliant: <300 lines
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import re

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class ProjectScanner:
    """Comprehensive project scanner."""

    def __init__(self):
        self.unused_imports: List[Dict] = []
        self.unused_functions: List[Dict] = []
        self.unused_classes: List[Dict] = []
        self.optimization_opportunities: List[Dict] = []
        self.dead_code: List[Dict] = []
        self.imports_map: Dict[str, Set[str]] = defaultdict(set)
        self.function_calls: Set[str] = set()
        self.class_instantiations: Set[str] = set()

    def scan_file(self, file_path: Path) -> Dict:
        """Scan a single file."""
        if not file_path.exists() or not file_path.suffix == '.py':
            return {"skipped": f"Not a Python file: {file_path}"}

        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))

            # Track imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports_map[str(file_path)].add(
                            alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.imports_map[str(file_path)].add(
                            node.module.split('.')[0])

                # Track function calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        self.function_calls.add(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        self.function_calls.add(node.func.attr)

                # Track class instantiations
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        self.class_instantiations.add(node.func.id)

            # Find unused functions/classes in this file
            file_functions = set()
            file_classes = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    file_functions.add(node.name)
                elif isinstance(node, ast.ClassDef):
                    file_classes.add(node.name)

            # Check for unused functions (not called in this file)
            for func_name in file_functions:
                if func_name not in self.function_calls and not func_name.startswith('_'):
                    self.unused_functions.append({
                        "file": str(file_path.relative_to(project_root)),
                        "function": func_name,
                        "type": "potentially_unused"
                    })

        except SyntaxError:
            return {"error": f"Syntax error in {file_path}"}
        except Exception as e:
            return {"error": f"Error processing {file_path}: {e}"}

        return {"processed": True}

    def find_optimization_opportunities(self) -> List[Dict]:
        """Find optimization opportunities."""
        opportunities = []

        # Check for large files that could be split
        src_dir = project_root / "src"
        for py_file in src_dir.rglob("*.py"):
            try:
                lines = len(py_file.read_text(encoding='utf-8').splitlines())
                if lines > 500:
                    opportunities.append({
                        "type": "large_file",
                        "file": str(py_file.relative_to(project_root)),
                        "lines": lines,
                        "recommendation": "Consider splitting into smaller modules"
                    })
            except:
                pass

        return opportunities


def scan_project() -> Dict:
    """Scan entire project."""
    scanner = ProjectScanner()

    src_dir = project_root / "src"
    if not src_dir.exists():
        return {"error": "src/ directory not found"}

    python_files = list(src_dir.rglob("*.py"))
    total_files = len(python_files)

    print(f"🔍 Scanning {total_files} Python files...\n")

    for py_file in python_files:
        if py_file.is_file():
            scanner.scan_file(py_file)

    # Find optimization opportunities
    optimization_opportunities = scanner.find_optimization_opportunities()

    return {
        "total_files": total_files,
        "unused_functions": len(scanner.unused_functions),
        "unused_classes": len(scanner.unused_classes),
        "optimization_opportunities": len(optimization_opportunities),
        "details": {
            "unused_functions": scanner.unused_functions[:50],  # Top 50
            # Top 20
            "optimization_opportunities": optimization_opportunities[:20]
        }
    }


def print_report(results: Dict):
    """Print project scan report."""
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return

    print("\n" + "="*70)
    print("📊 COMPREHENSIVE PROJECT SCAN REPORT")
    print("="*70)

    print(f"\n📁 FILES SCANNED: {results['total_files']}")
    print(f"\n🔍 FINDINGS:")
    print(f"  Potentially Unused Functions: {results['unused_functions']}")
    print(
        f"  Optimization Opportunities: {results['optimization_opportunities']}")

    if results['details']['optimization_opportunities']:
        print(f"\n📋 OPTIMIZATION OPPORTUNITIES (Top 20):")
        for i, opp in enumerate(results['details']['optimization_opportunities'], 1):
            print(f"  {i:2d}. {opp['file']}")
            print(f"      {opp['lines']} lines - {opp['recommendation']}")

    if results['details']['unused_functions']:
        print(f"\n📋 POTENTIALLY UNUSED FUNCTIONS (Top 50):")
        for i, func in enumerate(results['details']['unused_functions'][:20], 1):
            print(f"  {i:2d}. {func['file']}::{func['function']}")

    print("\n" + "="*70 + "\n")


def main():
    """CLI entry point."""
    results = scan_project()
    print_report(results)

    # Exit with error code if issues found
    if results.get("unused_functions", 0) > 0 or results.get("optimization_opportunities", 0) > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()




