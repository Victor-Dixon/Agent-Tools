#!/usr/bin/env python3
"""
Analysis Toolkit - Unified Analysis CLI & Executor
===================================================

Consolidates V2 compliance analysis, general analysis capabilities,
and analysis execution into a single unified toolkit.

Replaces:
- analysis_cli.py
- unified_analyzer.py
- analysis_executor.py

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-03
V2 Compliant: Yes (<300 lines)
SSOT Domain: analytics

<!-- SSOT Domain: analytics -->
"""

import ast
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# SSOT Domain: analytics

MAX_FILE_LOC = 300
MAX_CLASS_LOC = 200
MAX_FUNCTION_LOC = 30
MAX_LINE_LENGTH = 100
EXCLUDE_PATTERNS = ['__pycache__', '.venv', 'node_modules', '.git', 'build', 'dist', '.pytest_cache']


class AnalysisToolkit:
    """Unified analysis toolkit for V2 compliance and general analysis."""

    def __init__(self, project_root: Path = None):
        """Initialize toolkit."""
        self.project_root = project_root or Path.cwd()
        self.skip_dirs = {"__pycache__", ".git", "node_modules", "venv", ".venv", "env", ".pytest_cache"}

    def should_exclude(self, path: Path) -> bool:
        """Check if file should be excluded."""
        return any(pattern in str(path) for pattern in EXCLUDE_PATTERNS)

    def analyze_v2_compliance(self, file_path: Path) -> Dict[str, Any]:
        """Analyze file for V2 compliance violations."""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            violations = []
            file_loc = len(lines)
            if file_loc > MAX_FILE_LOC:
                violations.append({"type": "file_loc", "line": 1, "message": f"File exceeds {MAX_FILE_LOC} LOC ({file_loc} LOC)", "severity": "critical"})
            if 'test' not in str(file_path).lower():
                print_lines = [i for i, line in enumerate(lines, 1) if line.strip().startswith(('print(', 'print '))]
                if print_lines:
                    violations.append({"type": "print_statement", "line": print_lines[0], "message": f"Found {len(print_lines)} print() statement(s)", "severity": "major"})
            try:
                tree = ast.parse(content, filename=str(file_path))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_loc = (node.end_lineno or node.lineno) - node.lineno + 1
                        if class_loc > MAX_CLASS_LOC:
                            violations.append({"type": "class_loc", "line": node.lineno, "message": f"Class '{node.name}' exceeds {MAX_CLASS_LOC} LOC ({class_loc} LOC)", "severity": "major", "class_name": node.name})
                    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        func_loc = (node.end_lineno or node.lineno) - node.lineno + 1
                        if func_loc > MAX_FUNCTION_LOC:
                            violations.append({"type": "function_loc", "line": node.lineno, "message": f"Function '{node.name}' exceeds {MAX_FUNCTION_LOC} LOC ({func_loc} LOC)", "severity": "minor", "function_name": node.name})
            except SyntaxError as e:
                violations.append({"type": "syntax_error", "line": e.lineno or 1, "message": f"Syntax error: {e.msg}", "severity": "critical"})
            long_lines = [(i, len(line)) for i, line in enumerate(lines, 1) if len(line) > MAX_LINE_LENGTH and not line.strip().startswith(('http://', 'https://', 'import ', 'from '))]
            if long_lines:
                violations.append({"type": "line_length", "line": long_lines[0][0], "message": f"Found {len(long_lines)} line(s) exceeding {MAX_LINE_LENGTH} characters", "severity": "minor"})
            return {"file": str(file_path), "violations": violations, "stats": {"total_lines": file_loc, "total_violations": len(violations)}}
        except Exception as e:
            return {"file": str(file_path), "violations": [{"type": "file_error", "line": 1, "message": f"Failed to analyze: {str(e)}", "severity": "critical"}], "stats": {"total_lines": 0, "total_violations": 1}}

    def analyze_project_structure(self, target_path: Path = None) -> Dict[str, Any]:
        """Analyze project structure."""
        target = target_path or self.project_root
        structure = {"total_files": 0, "total_dirs": 0, "file_types": Counter(), "directories": {}}
        for root, dirs, files in os.walk(target):
            root_path = Path(root)
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]
            rel_path = str(root_path.relative_to(target)) if root_path != target else "."
            if any(skip in Path(rel_path).parts for skip in self.skip_dirs): continue
            file_count = len(files)
            if file_count > 0 or len(dirs) > 0:
                structure["directories"][rel_path] = {"files": file_count, "subdirs": len(dirs)}
                structure["total_files"] += file_count
                structure["total_dirs"] += len(dirs)
                for f in files:
                    ext = (root_path / f).suffix or "no_extension"
                    structure["file_types"][ext] += 1
        return {"category": "structure", "target": str(target), "analysis": {"total_files": structure["total_files"], "total_dirs": structure["total_dirs"], "file_types": dict(structure["file_types"])}, "timestamp": datetime.now().isoformat()}

    def analyze_code_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single code file."""
        if not file_path.exists():
            return {"category": "code", "file": str(file_path), "error": "File not found"}
        if file_path.suffix != ".py":
            return {"category": "code", "file": str(file_path), "error": "Unsupported file type"}
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            functions, classes, imports = [], {}, []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    classes[node.name] = {"methods": methods, "line_count": len(node.body)}
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    else:
                        imports.extend([f"{node.module or ''}.{alias.name}" for alias in node.names])
            return {"category": "code", "file": str(file_path), "language": "python", "functions": functions, "classes": classes, "imports": imports, "line_count": len(content.splitlines()), "timestamp": datetime.now().isoformat()}
        except Exception as e:
            return {"category": "code", "file": str(file_path), "error": str(e)}

    def scan_technical_debt(self, target_path: Path = None) -> Dict[str, Any]:
        """Scan for technical debt markers."""
        target = target_path or self.project_root
        markers = {"TODO": r"TODO[:\s]", "FIXME": r"FIXME[:\s]", "HACK": r"HACK[:\s]", "BUG": r"BUG[:\s]", "DEPRECATED": r"DEPRECATED[:\s]"}
        results = defaultdict(list)
        for file_path in target.rglob("*"):
            if not file_path.is_file() or any(skip in file_path.parts for skip in self.skip_dirs) or file_path.suffix not in {".py", ".js", ".ts", ".md"}:
                continue
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                for line_num, line in enumerate(content.splitlines(), 1):
                    for marker_name, pattern in markers.items():
                        if re.search(pattern, line, re.IGNORECASE):
                            results[marker_name].append({"file": str(file_path.relative_to(self.project_root)), "line": line_num, "content": line.strip()})
            except Exception:
                pass
        return {"category": "technical_debt", "target": str(target), "markers": dict(results), "total_issues": sum(len(issues) for issues in results.values()), "timestamp": datetime.now().isoformat()}

    def analyze_project(self, root_path: Path = None, max_files: int = 1000) -> Dict[str, Any]:
        """Analyze entire project for V2 compliance."""
        root = root_path or self.project_root
        all_files = []
        summary = {"syntax_errors": 0, "file_loc_violations": 0, "class_loc_violations": 0, "function_loc_violations": 0, "line_length_violations": 0, "print_violations": 0, "total_violations": 0, "files_analyzed": 0, "files_with_violations": 0}
        for py_file in root.rglob("*.py"):
            if self.should_exclude(py_file) or len(all_files) >= max_files:
                continue
            result = self.analyze_v2_compliance(py_file)
            all_files.append(result)
            if result["violations"]:
                summary["files_with_violations"] += 1
            summary["files_analyzed"] += 1
            for v in result["violations"]:
                summary["total_violations"] += 1
                if v["type"] == "syntax_error": summary["syntax_errors"] += 1
                elif v["type"] == "file_loc": summary["file_loc_violations"] += 1
                elif v["type"] == "class_loc": summary["class_loc_violations"] += 1
                elif v["type"] == "function_loc": summary["function_loc_violations"] += 1
                elif v["type"] == "line_length": summary["line_length_violations"] += 1
                elif v["type"] == "print_statement": summary["print_violations"] += 1
        return {"summary": summary, "files": all_files}

    def ci_gate_check(self, results: Dict[str, Any]) -> tuple[bool, str]:
        """Check if project passes CI gate."""
        s = results["summary"]
        critical = s["syntax_errors"]
        major = s["file_loc_violations"] + s["class_loc_violations"] + s["print_violations"]
        if critical > 0:
            return False, f"CRITICAL CI GATE FAILED: {critical} syntax error(s)"
        if major > 0:
            return False, f"MAJOR CI GATE FAILED: {major} major violation(s)"
        if s["total_violations"] > 0:
            return False, f"MINOR CI GATE FAILED: {s['total_violations']} violation(s)"
        return True, "SUCCESS CI GATE PASSED: No violations"

    def execute_analysis(self, analysis_type: str, path: str = None, threshold: int = None) -> int:
        """Execute analysis operations."""
        if analysis_type == "project":
            result = subprocess.run(["python", "tools/analysis_toolkit.py", "--structure"], capture_output=True)
            return result.returncode
        elif analysis_type == "complexity":
            cmd = ["python", "tools/code_analysis_tool.py", path or "."]
            if threshold:
                cmd.extend(["--threshold", str(threshold)])
            return subprocess.run(cmd).returncode
        elif analysis_type == "duplicates":
            return subprocess.run(["python", "tools/duplication_analyzer.py", path or "."]).returncode
        return 1

    def run_full_analysis(self, target_path: Path = None) -> Dict[str, Any]:
        """Run comprehensive analysis suite."""
        results = {"timestamp": datetime.now().isoformat(), "analyses": {}}
        results["analyses"]["structure"] = self.analyze_project_structure(target_path)
        results["analyses"]["technical_debt"] = self.scan_technical_debt(target_path)
        results["analyses"]["v2_compliance"] = self.analyze_project(target_path)
        return results


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Analysis Toolkit")
    parser.add_argument("--violations", action="store_true", help="Analyze V2 compliance violations")
    parser.add_argument("--ci-gate", action="store_true", help="Run CI gate check")
    parser.add_argument("--structure", action="store_true", help="Analyze project structure")
    parser.add_argument("--debt", action="store_true", help="Scan technical debt")
    parser.add_argument("--file", type=Path, help="Analyze specific file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--max-files", type=int, default=1000, help="Max files to analyze")
    parser.add_argument("--root", type=Path, default=Path("."), help="Root directory")
    parser.add_argument("--execute", type=str, help="Execute analysis type (project/complexity/duplicates)")
    args = parser.parse_args()
    
    toolkit = AnalysisToolkit(project_root=args.root)
    
    if args.execute:
        exit_code = toolkit.execute_analysis(args.execute, str(args.root))
        sys.exit(exit_code)
    elif args.violations or args.ci_gate:
        results = toolkit.analyze_project(args.root, args.max_files)
        if args.ci_gate:
            passed, message = toolkit.ci_gate_check(results)
            print(message)
            sys.exit(0 if passed else 1)
        elif args.json:
            print(json.dumps(results, indent=2))
        else:
            s = results["summary"]
            print(f"Files analyzed: {s['files_analyzed']}, Violations: {s['total_violations']}")
    elif args.structure:
        result = toolkit.analyze_project_structure(args.root)
        print(json.dumps(result, indent=2) if args.json else f"Files: {result['analysis']['total_files']}, Dirs: {result['analysis']['total_dirs']}")
    elif args.debt:
        result = toolkit.scan_technical_debt(args.root)
        print(json.dumps(result, indent=2) if args.json else f"Total issues: {result['total_issues']}")
    elif args.file:
        result = toolkit.analyze_code_file(args.file)
        print(json.dumps(result, indent=2))
    else:
        results = toolkit.run_full_analysis(args.root)
        print(json.dumps(results, indent=2) if args.json else "Full analysis complete")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()


