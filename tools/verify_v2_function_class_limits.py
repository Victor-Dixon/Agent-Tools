#!/usr/bin/env python3
"""
V2 Function/Class Limit Verification Tool
========================================

Verifies V2 compliance for function and class size limits:
- Functions: Maximum 30 lines
- Classes: Maximum 200 lines

Usage:
    python tools/verify_v2_function_class_limits.py [path]
    
    If path not provided, checks all Python files in src/
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# V2 Compliance Limits
MAX_FUNCTION_LINES = 30
MAX_CLASS_LINES = 200


class V2LimitChecker(ast.NodeVisitor):
    """AST visitor to check function and class line limits."""
    
    def __init__(self, source_lines: List[str], file_path: str):
        self.source_lines = source_lines
        self.file_path = file_path
        self.function_offenders: List[Dict] = []
        self.class_offenders: List[Dict] = []
        
    def _get_line_count(self, node: ast.AST) -> int:
        """Calculate line count for a node (excluding decorators)."""
        if not hasattr(node, 'lineno') or not hasattr(node, 'end_lineno'):
            return 0
        
        start_line = node.lineno - 1  # Convert to 0-based index
        end_line = node.end_lineno - 1 if node.end_lineno else start_line
        
        # Count non-empty lines
        line_count = 0
        for i in range(start_line, end_line + 1):
            if i < len(self.source_lines):
                line = self.source_lines[i].rstrip()
                # Count non-empty, non-comment-only lines
                if line and not line.strip().startswith('#'):
                    line_count += 1
        
        return line_count
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Check function line limits."""
        line_count = self._get_line_count(node)
        
        if line_count > MAX_FUNCTION_LINES:
            self.function_offenders.append({
                'name': node.name,
                'line': node.lineno,
                'line_count': line_count,
                'limit': MAX_FUNCTION_LINES,
                'excess': line_count - MAX_FUNCTION_LINES
            })
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Check async function line limits."""
        line_count = self._get_line_count(node)
        
        if line_count > MAX_FUNCTION_LINES:
            self.function_offenders.append({
                'name': f'async {node.name}',
                'line': node.lineno,
                'line_count': line_count,
                'limit': MAX_FUNCTION_LINES,
                'excess': line_count - MAX_FUNCTION_LINES
            })
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Check class line limits."""
        line_count = self._get_line_count(node)
        
        if line_count > MAX_CLASS_LINES:
            self.class_offenders.append({
                'name': node.name,
                'line': node.lineno,
                'line_count': line_count,
                'limit': MAX_CLASS_LINES,
                'excess': line_count - MAX_CLASS_LINES
            })
        
        self.generic_visit(node)


def check_file(file_path: Path) -> Tuple[List[Dict], List[Dict]]:
    """Check a single file for V2 compliance."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
            source_lines = source.splitlines()
        
        tree = ast.parse(source, filename=str(file_path))
        checker = V2LimitChecker(source_lines, str(file_path))
        checker.visit(tree)
        
        return checker.function_offenders, checker.class_offenders
    except SyntaxError as e:
        print(f"⚠️  Syntax error in {file_path}: {e}", file=sys.stderr)
        return [], []
    except Exception as e:
        print(f"⚠️  Error checking {file_path}: {e}", file=sys.stderr)
        return [], []


def check_directory(directory: Path) -> Tuple[List[Dict], List[Dict]]:
    """Check all Python files in a directory recursively."""
    all_function_offenders: List[Dict] = []
    all_class_offenders: List[Dict] = []
    
    for py_file in directory.rglob('*.py'):
        # Skip __pycache__ and virtual environments
        if '__pycache__' in str(py_file) or 'venv' in str(py_file):
            continue
        
        func_offenders, class_offenders = check_file(py_file)
        
        # Add file path to each offender
        for offender in func_offenders:
            offender['file'] = str(py_file.relative_to(directory))
        for offender in class_offenders:
            offender['file'] = str(py_file.relative_to(directory))
        
        all_function_offenders.extend(func_offenders)
        all_class_offenders.extend(class_offenders)
    
    return all_function_offenders, all_class_offenders


def print_report(function_offenders: List[Dict], class_offenders: List[Dict]):
    """Print compliance report."""
    print("=" * 80)
    print("V2 FUNCTION/CLASS LIMIT VERIFICATION REPORT")
    print("=" * 80)
    print()
    
    print(f"Function Limit: {MAX_FUNCTION_LINES} lines")
    print(f"Class Limit: {MAX_CLASS_LINES} lines")
    print()
    
    # Function offenders
    if function_offenders:
        print(f"❌ FUNCTION OFFENDERS ({len(function_offenders)}):")
        print("-" * 80)
        for offender in sorted(function_offenders, key=lambda x: (x['file'], x['line'])):
            print(f"  {offender['file']}:{offender['line']}")
            print(f"    Function: {offender['name']}")
            print(f"    Lines: {offender['line_count']} (limit: {offender['limit']}, excess: {offender['excess']})")
            print()
    else:
        print("✅ No function limit violations found")
        print()
    
    # Class offenders
    if class_offenders:
        print(f"❌ CLASS OFFENDERS ({len(class_offenders)}):")
        print("-" * 80)
        for offender in sorted(class_offenders, key=lambda x: (x['file'], x['line'])):
            print(f"  {offender['file']}:{offender['line']}")
            print(f"    Class: {offender['name']}")
            print(f"    Lines: {offender['line_count']} (limit: {offender['limit']}, excess: {offender['excess']})")
            print()
    else:
        print("✅ No class limit violations found")
        print()
    
    # Summary
    total_offenders = len(function_offenders) + len(class_offenders)
    print("=" * 80)
    if total_offenders == 0:
        print("✅ V2 COMPLIANCE: PASS - All functions and classes within limits")
    else:
        print(f"❌ V2 COMPLIANCE: FAIL - {total_offenders} violations found")
        print(f"   Functions: {len(function_offenders)}")
        print(f"   Classes: {len(class_offenders)}")
    print("=" * 80)
    
    return total_offenders == 0


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        target_path = Path(sys.argv[1])
    else:
        target_path = Path('src')
    
    if not target_path.exists():
        print(f"❌ Error: Path not found: {target_path}", file=sys.stderr)
        sys.exit(1)
    
    if target_path.is_file():
        function_offenders, class_offenders = check_file(target_path)
        # Add file path to offenders
        for offender in function_offenders:
            offender['file'] = str(target_path)
        for offender in class_offenders:
            offender['file'] = str(target_path)
    else:
        function_offenders, class_offenders = check_directory(target_path)
    
    is_compliant = print_report(function_offenders, class_offenders)
    sys.exit(0 if is_compliant else 1)


if __name__ == '__main__':
    main()

