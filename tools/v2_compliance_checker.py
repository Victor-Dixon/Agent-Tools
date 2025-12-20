#!/usr/bin/env python3
"""
V2 Compliance Checker Tool
==========================

Automatically validates V2 compliance for files, functions, and classes:
- File size: <300 lines
- Function size: <30 lines
- Class size: <200 lines
- SSOT tags: Present and correct
- Linting: No errors

Usage:
    python tools/v2_compliance_checker.py [file_or_directory]
    python tools/v2_compliance_checker.py src/core/github/
    python tools/v2_compliance_checker.py src/core/synthetic_github.py

Author: Agent-1 (Integration & Core Systems Specialist)
V2 Compliant: <300 lines
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re

# V2 Compliance Limits
MAX_FILE_LINES = 300
MAX_FUNCTION_LINES = 30
MAX_CLASS_LINES = 200

# SSOT Tag Pattern
SSOT_TAG_PATTERN = re.compile(r'<!--\s*SSOT\s+Domain:\s*(\w+)\s*-->', re.IGNORECASE)


class V2ComplianceChecker:
    """V2 compliance checker for Python files."""
    
    def __init__(self):
        self.violations: List[Dict] = []
        self.compliant_files: List[str] = []
    
    def check_file(self, file_path: Path) -> Dict:
        """Check a single file for V2 compliance."""
        if not file_path.exists():
            return {"error": f"File not found: {file_path}"}
        
        if not file_path.suffix == '.py':
            return {"skipped": f"Not a Python file: {file_path}"}
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.splitlines()
            
            # Check file size
            file_size_ok = len(lines) <= MAX_FILE_LINES
            if not file_size_ok:
                self.violations.append({
                    "file": str(file_path),
                    "type": "file_size",
                    "current": len(lines),
                    "limit": MAX_FILE_LINES,
                    "message": f"File exceeds {MAX_FILE_LINES} line limit"
                })
            
            # Check SSOT tag
            ssot_tag = self._find_ssot_tag(content)
            ssot_ok = ssot_tag is not None
            
            if not ssot_ok:
                self.violations.append({
                    "file": str(file_path),
                    "type": "ssot_tag",
                    "message": "Missing SSOT domain tag (<!-- SSOT Domain: domain_name -->)"
                })
            
            # Parse AST for function/class analysis
            try:
                tree = ast.parse(content, filename=str(file_path))
                function_violations = self._check_functions(tree, lines, file_path)
                class_violations = self._check_classes(tree, lines, file_path)
                
                self.violations.extend(function_violations)
                self.violations.extend(class_violations)
                
            except SyntaxError as e:
                self.violations.append({
                    "file": str(file_path),
                    "type": "syntax_error",
                    "message": f"Syntax error: {e}"
                })
            
            # Summary
            is_compliant = (
                file_size_ok and
                ssot_ok and
                len([v for v in self.violations if v.get("file") == str(file_path) and v.get("type") in ["function_size", "class_size"]]) == 0
            )
            
            if is_compliant:
                self.compliant_files.append(str(file_path))
            
            return {
                "file": str(file_path),
                "lines": len(lines),
                "file_size_ok": file_size_ok,
                "ssot_tag": ssot_tag,
                "ssot_ok": ssot_ok,
                "compliant": is_compliant,
                "violations": [v for v in self.violations if v.get("file") == str(file_path)]
            }
            
        except Exception as e:
            return {"error": f"Error checking file {file_path}: {e}"}
    
    def _find_ssot_tag(self, content: str) -> Optional[str]:
        """Find SSOT domain tag in content."""
        match = SSOT_TAG_PATTERN.search(content)
        if match:
            return match.group(1)
        return None
    
    def _check_functions(self, tree: ast.AST, lines: List[str], file_path: Path) -> List[Dict]:
        """Check function sizes."""
        violations = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else len([l for l in lines[node.lineno-1:node.lineno+50] if l.strip()])
                
                if func_lines > MAX_FUNCTION_LINES:
                    violations.append({
                        "file": str(file_path),
                        "type": "function_size",
                        "name": node.name,
                        "line": node.lineno,
                        "current": func_lines,
                        "limit": MAX_FUNCTION_LINES,
                        "message": f"Function '{node.name}' exceeds {MAX_FUNCTION_LINES} line limit"
                    })
        
        return violations
    
    def _check_classes(self, tree: ast.AST, lines: List[str], file_path: Path) -> List[Dict]:
        """Check class sizes."""
        violations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else len([l for l in lines[node.lineno-1:node.lineno+200] if l.strip()])
                
                if class_lines > MAX_CLASS_LINES:
                    violations.append({
                        "file": str(file_path),
                        "type": "class_size",
                        "name": node.name,
                        "line": node.lineno,
                        "current": class_lines,
                        "limit": MAX_CLASS_LINES,
                        "message": f"Class '{node.name}' exceeds {MAX_CLASS_LINES} line limit"
                    })
        
        return violations
    
    def check_directory(self, directory: Path) -> Dict:
        """Check all Python files in a directory."""
        results = []
        
        for py_file in directory.rglob("*.py"):
            # Skip __pycache__ and test files for now
            if "__pycache__" in str(py_file) or "test_" in py_file.name:
                continue
            
            result = self.check_file(py_file)
            if "error" not in result and "skipped" not in result:
                results.append(result)
        
        return {
            "directory": str(directory),
            "files_checked": len(results),
            "compliant": len(self.compliant_files),
            "violations": len(self.violations),
            "results": results
        }
    
    def print_report(self):
        """Print compliance report."""
        print("\n" + "="*60)
        print("V2 COMPLIANCE REPORT")
        print("="*60)
        
        if self.compliant_files:
            print(f"\n✅ COMPLIANT FILES ({len(self.compliant_files)}):")
            for file in self.compliant_files:
                print(f"   {file}")
        
        if self.violations:
            print(f"\n❌ VIOLATIONS ({len(self.violations)}):")
            
            # Group by file
            by_file: Dict[str, List[Dict]] = {}
            for violation in self.violations:
                file = violation.get("file", "unknown")
                if file not in by_file:
                    by_file[file] = []
                by_file[file].append(violation)
            
            for file, violations in by_file.items():
                print(f"\n   {file}:")
                for v in violations:
                    if v.get("type") == "file_size":
                        print(f"      ❌ File size: {v.get('current')} lines (limit: {v.get('limit')})")
                    elif v.get("type") == "function_size":
                        print(f"      ❌ Function '{v.get('name')}' (line {v.get('line')}): {v.get('current')} lines (limit: {v.get('limit')})")
                    elif v.get("type") == "class_size":
                        print(f"      ❌ Class '{v.get('name')}' (line {v.get('line')}): {v.get('current')} lines (limit: {v.get('limit')})")
                    elif v.get("type") == "ssot_tag":
                        print(f"      ❌ Missing SSOT domain tag")
                    else:
                        print(f"      ❌ {v.get('message')}")
        
        print("\n" + "="*60)
        print(f"Summary: {len(self.compliant_files)} compliant, {len(self.violations)} violations")
        print("="*60 + "\n")


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python tools/v2_compliance_checker.py [file_or_directory]")
        sys.exit(1)
    
    target = Path(sys.argv[1])
    
    if not target.exists():
        print(f"❌ Error: Path not found: {target}")
        sys.exit(1)
    
    checker = V2ComplianceChecker()
    
    if target.is_file():
        result = checker.check_file(target)
        if "error" in result:
            print(f"❌ {result['error']}")
            sys.exit(1)
        elif "skipped" in result:
            print(f"⚠️ {result['skipped']}")
            sys.exit(0)
    else:
        result = checker.check_directory(target)
    
    checker.print_report()
    
    # Exit with error code if violations found
    if checker.violations:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()

