#!/usr/bin/env python3
"""
Test Usage Analyzer
===================

Identify unused functionality via test coverage analysis.
Finds methods only tested but never used in production.

Author: Agent-1 (Integration & Core Systems Specialist)
V2 Compliant: <300 lines
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def find_tested_functions(test_dir: Path) -> Set[str]:
    """Find all functions that are tested."""
    tested = set()
    
    if not test_dir.exists():
        return tested
    
    for test_file in test_dir.rglob("test_*.py"):
        try:
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content, filename=str(test_file))
            
            # Find function calls in tests
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        tested.add(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        tested.add(node.func.attr)
        except Exception:
            continue
    
    return tested


def find_used_functions(source_dir: Path) -> Set[str]:
    """Find all functions used in production code."""
    used = set()
    
    if not source_dir.exists():
        return used
    
    # Exclude test directories
    exclude_dirs = {"tests", "test", "__pycache__", ".pytest_cache"}
    
    for py_file in source_dir.rglob("*.py"):
        # Skip test files and excluded directories
        if any(excluded in py_file.parts for excluded in exclude_dirs):
            continue
        
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content, filename=str(py_file))
            
            # Find function calls
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        used.add(node.func.id)
                    elif isinstance(node.func, ast.Attribute):
                        used.add(node.func.attr)
        except Exception:
            continue
    
    return used


def analyze_unused_via_tests(project_root: Path) -> Dict[str, List[str]]:
    """Analyze functions that are tested but never used in production."""
    test_dir = project_root / "tests"
    source_dir = project_root / "src"
    tools_dir = project_root / "tools"
    
    # Find tested functions
    tested = find_tested_functions(test_dir)
    
    # Find used functions in production
    used_src = find_used_functions(source_dir)
    used_tools = find_used_functions(tools_dir)
    used = used_src | used_tools
    
    # Functions tested but not used
    unused_via_tests = tested - used
    
    return {
        "tested_functions": list(tested),
        "used_functions": list(used),
        "unused_via_tests": list(unused_via_tests),
        "count_tested": len(tested),
        "count_used": len(used),
        "count_unused": len(unused_via_tests),
    }


def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Usage Analyzer")
    parser.add_argument(
        "--output",
        help="Output file for results (JSON)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    
    args = parser.parse_args()
    
    print("🔍 Analyzing test usage...")
    results = analyze_unused_via_tests(project_root)
    
    print(f"\n📊 Results:")
    print(f"   Tested functions: {results['count_tested']}")
    print(f"   Used in production: {results['count_used']}")
    print(f"   Unused via tests: {results['count_unused']}")
    
    if results["unused_via_tests"]:
        print(f"\n⚠️  Functions tested but not used in production:")
        for func in sorted(results["unused_via_tests"])[:20]:
            print(f"   - {func}")
        if len(results["unused_via_tests"]) > 20:
            print(f"   ... and {len(results['unused_via_tests']) - 20} more")
    else:
        print("\n✅ No unused functions found (all tested functions are used)")
    
    if args.output:
        import json
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {output_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

