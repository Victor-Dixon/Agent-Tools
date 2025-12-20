#!/usr/bin/env python3
"""
Code Duplication Checker
========================

Scans project for duplicate code patterns, functions, and logic.
Identifies duplicate functions, classes, and code blocks.

Author: Agent-2 (Architecture & Design Specialist)
V2 Compliant: <300 lines
"""

import ast
import sys
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import difflib

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class DuplicationChecker:
    """Code duplication checker for Python files."""

    def __init__(self):
        self.duplicates: List[Dict] = []
        self.function_signatures: Dict[str, List[Dict]] = defaultdict(list)
        self.class_signatures: Dict[str, List[Dict]] = defaultdict(list)
        self.code_blocks: Dict[str, List[Dict]] = defaultdict(list)

    def normalize_code(self, code: str) -> str:
        """Normalize code for comparison (remove whitespace, comments)."""
        lines = code.splitlines()
        normalized = []
        for line in lines:
            # Remove comments
            if '#' in line:
                line = line[:line.index('#')]
            # Strip whitespace
            line = line.strip()
            if line:
                normalized.append(line)
        return '\n'.join(normalized)

    def get_function_signature(self, node: ast.FunctionDef) -> str:
        """Get normalized function signature."""
        args = [arg.arg for arg in node.args.args]
        return f"{node.name}({', '.join(args)})"

    def get_function_body_hash(self, node: ast.FunctionDef) -> str:
        """Get hash of function body for duplicate detection."""
        body_lines = [ast.unparse(line) for line in node.body if isinstance(
            line, (ast.Expr, ast.Assign, ast.Return, ast.If, ast.For, ast.While))]
        body_code = '\n'.join(body_lines)
        normalized = self.normalize_code(body_code)
        return hashlib.md5(normalized.encode()).hexdigest()

    def check_file(self, file_path: Path) -> Dict:
        """Check a single file for duplicates."""
        if not file_path.exists() or not file_path.suffix == '.py':
            return {"skipped": f"Not a Python file: {file_path}"}

        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))

            # Check functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    sig = self.get_function_signature(node)
                    body_hash = self.get_function_body_hash(node)

                    # Get function source
                    try:
                        func_source = ast.get_source_segment(content, node)
                        if func_source:
                            normalized_body = self.normalize_code(func_source)
                            body_hash = hashlib.md5(
                                normalized_body.encode()).hexdigest()
                    except:
                        pass

                    self.function_signatures[sig].append({
                        "file": str(file_path.relative_to(project_root)),
                        "line": node.lineno,
                        "name": node.name,
                        "body_hash": body_hash,
                        "source": func_source if 'func_source' in locals() else None
                    })

                # Check classes
                elif isinstance(node, ast.ClassDef):
                    class_methods = [
                        n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    class_sig = f"{node.name}({', '.join(class_methods)})"

                    self.class_signatures[class_sig].append({
                        "file": str(file_path.relative_to(project_root)),
                        "line": node.lineno,
                        "name": node.name,
                        "methods": class_methods
                    })

        except SyntaxError as e:
            return {"error": f"Syntax error in {file_path}: {e}"}
        except Exception as e:
            return {"error": f"Error processing {file_path}: {e}"}

        return {"processed": True}

    def find_duplicates(self) -> Dict:
        """Find duplicate patterns."""
        results = {
            "duplicate_functions": [],
            "duplicate_classes": [],
            "similar_code_blocks": []
        }

        # Find duplicate functions (same signature + similar body)
        for sig, occurrences in self.function_signatures.items():
            if len(occurrences) > 1:
                # Group by body hash
                by_hash = defaultdict(list)
                for occ in occurrences:
                    by_hash[occ["body_hash"]].append(occ)

                # Find exact duplicates (same body hash)
                for body_hash, occs in by_hash.items():
                    if len(occs) > 1:
                        results["duplicate_functions"].append({
                            "signature": sig,
                            "count": len(occs),
                            "occurrences": occs,
                            "type": "exact"
                        })

        # Find duplicate classes (same name + similar methods)
        for sig, occurrences in self.class_signatures.items():
            if len(occurrences) > 1:
                results["duplicate_classes"].append({
                    "signature": sig,
                    "count": len(occurrences),
                    "occurrences": occurrences
                })

        return results


def scan_codebase() -> Dict:
    """Scan entire codebase for duplicates."""
    checker = DuplicationChecker()

    src_dir = project_root / "src"
    if not src_dir.exists():
        return {"error": "src/ directory not found"}

    python_files = list(src_dir.rglob("*.py"))
    total_files = len(python_files)

    print(f"🔍 Scanning {total_files} Python files for duplicates...\n")

    for py_file in python_files:
        if py_file.is_file():
            checker.check_file(py_file)

    # Find duplicates
    results = checker.find_duplicates()

    # Calculate statistics
    total_duplicate_functions = len(results["duplicate_functions"])
    total_duplicate_classes = len(results["duplicate_classes"])

    return {
        "total_files": total_files,
        "duplicate_functions": total_duplicate_functions,
        "duplicate_classes": total_duplicate_classes,
        "details": results
    }


def print_report(results: Dict):
    """Print duplication report."""
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return

    print("\n" + "="*70)
    print("📊 CODE DUPLICATION REPORT")
    print("="*70)

    print(f"\n📁 FILES SCANNED: {results['total_files']}")
    print(f"\n🔍 DUPLICATES FOUND:")
    print(f"  Duplicate Functions: {results['duplicate_functions']}")
    print(f"  Duplicate Classes: {results['duplicate_classes']}")

    if results['details']['duplicate_functions']:
        print(f"\n📋 DUPLICATE FUNCTIONS (Top 20):")
        for i, dup in enumerate(results['details']['duplicate_functions'][:20], 1):
            print(f"  {i:2d}. {dup['signature']}")
            print(f"      Found {dup['count']} times in:")
            for occ in dup['occurrences'][:3]:
                print(f"        - {occ['file']}:{occ['line']}")
            if len(dup['occurrences']) > 3:
                print(f"        ... and {len(dup['occurrences']) - 3} more")

    if results['details']['duplicate_classes']:
        print(f"\n📋 DUPLICATE CLASSES:")
        for i, dup in enumerate(results['details']['duplicate_classes'][:10], 1):
            print(f"  {i:2d}. {dup['signature']}")
            print(f"      Found {dup['count']} times in:")
            for occ in dup['occurrences'][:3]:
                print(f"        - {occ['file']}:{occ['line']}")

    print("\n" + "="*70 + "\n")


def main():
    """CLI entry point."""
    results = scan_codebase()
    print_report(results)

    # Exit with error code if duplicates found
    if results.get("duplicate_functions", 0) > 0 or results.get("duplicate_classes", 0) > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()




