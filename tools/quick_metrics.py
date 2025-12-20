#!/usr/bin/env python3
"""
Quick File Metrics Tool
========================

⚠️ DEPRECATED: This tool has been migrated to tools_v2.
Use: python -m tools_v2.toolbelt bi.metrics <files>
See: tools_v2/categories/bi_tools.py for the adapter.

Fast analysis of Python file metrics without full project scan.
Perfect for verifying file state before starting work.

Usage:
    python tools/quick_metrics.py src/core/shared_utilities.py
    python tools/quick_metrics.py src/services/*.py
    python tools/quick_metrics.py --pattern "vector*.py"

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-10-13
License: MIT
"""

import argparse
import ast
import sys
from pathlib import Path
from typing import List, Dict, Any
import glob


def analyze_file(file_path: Path) -> Dict[str, Any]:
    """Quick analysis of a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.splitlines()
        tree = ast.parse(content)
        
        # Count elements
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        
        # Calculate complexity (rough estimate)
        complexity = len([n for n in ast.walk(tree) if isinstance(n, (
            ast.If, ast.For, ast.While, ast.With, ast.Try, 
            ast.ExceptHandler, ast.FunctionDef, ast.ClassDef
        ))])
        
        # V2 compliance checks
        violations = []
        if len(lines) > 400:
            violations.append(f"File size: {len(lines)} lines (>400)")
        
        long_functions = [f for f in functions if (
            hasattr(f, 'end_lineno') and hasattr(f, 'lineno') and 
            (f.end_lineno - f.lineno) > 50
        )]
        if long_functions:
            violations.append(f"{len(long_functions)} functions >50 lines")
        
        if len(functions) > 30:
            violations.append(f"{len(functions)} functions (>30 recommended max)")
        
        if len(classes) > 10:
            violations.append(f"{len(classes)} classes (>10 may need splitting)")
        
        return {
            "file": str(file_path),
            "lines": len(lines),
            "classes": len(classes),
            "functions": len(functions),
            "imports": len(imports),
            "complexity": complexity,
            "v2_compliant": len(violations) == 0,
            "violations": violations,
            "status": "✅" if len(violations) == 0 else "⚠️"
        }
    except SyntaxError as e:
        return {
            "file": str(file_path),
            "error": f"Syntax error: {e}",
            "status": "❌"
        }
    except Exception as e:
        return {
            "file": str(file_path),
            "error": str(e),
            "status": "❌"
        }


def analyze_multiple(file_paths: List[Path]) -> List[Dict[str, Any]]:
    """Analyze multiple files."""
    results = []
    for file_path in file_paths:
        if file_path.suffix == '.py':
            results.append(analyze_file(file_path))
    return results


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Quick metrics for Python files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Single file
    python tools/quick_metrics.py src/core/shared_utilities.py
    
    # Multiple files
    python tools/quick_metrics.py src/services/agent_vector_utils.py src/services/messaging_cli.py
    
    # Pattern matching
    python tools/quick_metrics.py --pattern "src/services/agent_*.py"
    
    # Directory
    python tools/quick_metrics.py src/core/utilities/
    
    # JSON output
    python tools/quick_metrics.py src/core/ --json --summary

Perfect for quick verification before starting refactoring work!
        """
    )
    
    parser.add_argument('files', nargs='*', help='Files or directories to analyze')
    parser.add_argument('--pattern', '-p', help='Glob pattern for files')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--summary', '-s', action='store_true', help='Show summary only')
    parser.add_argument('--violations-only', '-v', action='store_true', 
                       help='Show only files with violations')
    
    args = parser.parse_args()
    
    # Collect files
    file_paths = []
    
    if args.pattern:
        file_paths.extend([Path(f) for f in glob.glob(args.pattern, recursive=True)])
    
    for file_arg in args.files:
        path = Path(file_arg)
        if path.is_dir():
            file_paths.extend(path.rglob('*.py'))
        elif path.is_file():
            file_paths.append(path)
        else:
            # Try as glob
            file_paths.extend([Path(f) for f in glob.glob(file_arg, recursive=True)])
    
    if not file_paths:
        parser.print_help()
        sys.exit(1)
    
    # Analyze
    results = analyze_multiple(file_paths)
    
    if args.json:
        import json
        print(json.dumps(results, indent=2))
    else:
        # Pretty print
        print("\n" + "="*70)
        print("📊 QUICK FILE METRICS")
        print("="*70)
        
        for result in results:
            if args.violations_only and result.get("v2_compliant", False):
                continue
            
            print(f"\n{result['status']} {result['file']}")
            
            if "error" in result:
                print(f"  ❌ Error: {result['error']}")
            else:
                if not args.summary:
                    print(f"  Lines: {result['lines']}")
                    print(f"  Classes: {result['classes']}")
                    print(f"  Functions: {result['functions']}")
                    print(f"  Imports: {result['imports']}")
                    print(f"  Complexity: {result['complexity']}")
                
                if result['violations']:
                    print(f"  ⚠️  Violations:")
                    for violation in result['violations']:
                        print(f"    - {violation}")
                elif not args.summary:
                    print(f"  ✅ V2 Compliant")
        
        # Summary
        if len(results) > 1:
            total = len(results)
            compliant = sum(1 for r in results if r.get("v2_compliant", False))
            errors = sum(1 for r in results if "error" in r)
            
            print("\n" + "="*70)
            print("📈 SUMMARY")
            print("="*70)
            print(f"Total files: {total}")
            print(f"V2 Compliant: {compliant} ({100*compliant//total if total > 0 else 0}%)")
            print(f"With violations: {total - compliant - errors}")
            print(f"Errors: {errors}")
        
        print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
