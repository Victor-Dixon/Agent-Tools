#!/usr/bin/env python3
"""
V2 Function Size Checker - Agent-3
===================================

Checks all functions in files to ensure they meet V2 compliance (<30 lines).

Author: Agent-3 (Infrastructure & DevOps Specialist)
V2 Compliant: <400 lines
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Any


def get_function_sizes(file_path: Path) -> List[Dict[str, Any]]:
    """Get function sizes from a Python file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
        
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Calculate function size (end_lineno - lineno + 1)
                start_line = node.lineno
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                size = end_line - start_line + 1
                
                functions.append({
                    "name": node.name,
                    "start_line": start_line,
                    "end_line": end_line,
                    "size": size,
                    "violation": size > 30,
                })
        
        return functions
    except Exception as e:
        return [{"error": str(e)}]


def check_directory(directory: Path, pattern: str = "*.py") -> Dict[str, Any]:
    """Check all Python files in a directory."""
    results = {
        "files_checked": 0,
        "files_with_violations": 0,
        "total_functions": 0,
        "violations": [],
    }
    
    for file_path in directory.rglob(pattern):
        if file_path.name.startswith("__"):
            continue
        
        functions = get_function_sizes(file_path)
        if functions and "error" not in functions[0]:
            results["files_checked"] += 1
            results["total_functions"] += len(functions)
            
            violations = [f for f in functions if f.get("violation")]
            if violations:
                results["files_with_violations"] += 1
                results["violations"].append({
                    "file": str(file_path.relative_to(directory.parent)),
                    "functions": violations,
                })
    
    return results


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="V2 Function Size Checker")
    parser.add_argument("directory", nargs="?", default="src/core/error_handling", help="Directory to check")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    if not directory.exists():
        print(f"❌ Directory not found: {directory}")
        return 1
    
    print(f"🔍 Checking function sizes in: {directory}")
    print("=" * 70)
    
    results = check_directory(directory)
    
    print(f"\n📊 Results:")
    print(f"  Files checked: {results['files_checked']}")
    print(f"  Total functions: {results['total_functions']}")
    print(f"  Files with violations: {results['files_with_violations']}")
    print(f"  Total violations: {sum(len(v['functions']) for v in results['violations'])}")
    
    if results["violations"]:
        print(f"\n⚠️  Violations Found:")
        for violation in results["violations"]:
            print(f"\n  📄 {violation['file']}:")
            for func in violation["functions"]:
                print(f"    - {func['name']}(): {func['size']} lines (lines {func['start_line']}-{func['end_line']})")
    else:
        print(f"\n✅ No violations found - all functions <30 lines!")
    
    if args.report:
        report_file = Path("agent_workspaces/Agent-3/v2_function_size_report.txt")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("V2 Function Size Verification Report\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Directory: {directory}\n")
            f.write(f"Files checked: {results['files_checked']}\n")
            f.write(f"Total functions: {results['total_functions']}\n")
            f.write(f"Files with violations: {results['files_with_violations']}\n\n")
            
            if results["violations"]:
                f.write("Violations:\n")
                for violation in results["violations"]:
                    f.write(f"\n{violation['file']}:\n")
                    for func in violation["functions"]:
                        f.write(f"  - {func['name']}(): {func['size']} lines\n")
            else:
                f.write("✅ No violations found!\n")
        
        print(f"\n📄 Report saved: {report_file}")
    
    return 0 if not results["violations"] else 1


if __name__ == "__main__":
    exit(main())

