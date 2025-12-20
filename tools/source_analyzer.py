#!/usr/bin/env python3
"""
Source Analyzer - Consolidated Source Directory & Language Analysis
====================================================================

Consolidates source directory analysis, messaging file analysis,
and language-specific analysis into a single unified tool.

Replaces:
- analyze_src_directories.py
- analyze_messaging_files.py
- src_directory_analyzers.py
- projectscanner_language_analyzer.py

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
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# SSOT Domain: analytics


class SourceAnalyzer:
    """Unified source directory and language analyzer."""

    def __init__(self, project_root: Path = None):
        """Initialize analyzer."""
        self.project_root = project_root or Path.cwd()
        self.skip_dirs = {"__pycache__", ".git", "node_modules", "venv", ".venv", "env", ".pytest_cache"}

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a file based on its extension."""
        ext = file_path.suffix.lower()
        if ext == ".py":
            return self._analyze_python(file_path)
        elif ext in [".js", ".ts", ".jsx", ".tsx"]:
            return self._analyze_javascript(file_path)
        elif ext == ".md":
            return self._analyze_markdown(file_path)
        elif ext in [".yml", ".yaml"]:
            return self._analyze_yaml(file_path)
        else:
            return {"language": ext, "functions": [], "classes": {}, "line_count": 0, "complexity": 0, "error": "Unsupported file type"}

    def _analyze_python(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Python file using AST."""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            functions, classes, imports, routes = [], {}, [], []
            complexity = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                    complexity += 1
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call) and hasattr(decorator.func, "attr"):
                            if decorator.func.attr.lower() in {"route", "get", "post", "put", "delete", "patch"}:
                                path = "/unknown"
                                if decorator.args and isinstance(decorator.args[0], ast.Constant):
                                    path = decorator.args[0].value
                                routes.append({"function": node.name, "method": decorator.func.attr.upper(), "path": path})
                elif isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    classes[node.name] = {"methods": methods, "line_count": len(node.body)}
                    complexity += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    else:
                        imports.extend([f"{node.module or ''}.{alias.name}" for alias in node.names])
            return {"language": ".py", "functions": functions, "classes": classes, "imports": imports, "routes": routes, "line_count": len(content.splitlines()), "complexity": complexity, "function_count": len(functions), "class_count": len(classes), "import_count": len(imports)}
        except Exception as e:
            return {"language": ".py", "functions": [], "classes": {}, "imports": [], "line_count": 0, "complexity": 0, "error": str(e)}

    def _analyze_javascript(self, file_path: Path) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            functions = re.findall(r"function\s+(\w+)\s*\(", content)
            classes = re.findall(r"class\s+(\w+)", content)
            imports = re.findall(r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]', content)
            return {"language": ".js", "functions": functions, "classes": {cls: {"methods": []} for cls in classes}, "imports": imports, "line_count": len(content.splitlines()), "complexity": len(functions) + len(classes), "function_count": len(functions), "class_count": len(classes), "import_count": len(imports)}
        except Exception as e:
            return {"language": ".js", "functions": [], "classes": {}, "imports": [], "line_count": 0, "complexity": 0, "error": str(e)}

    def _analyze_markdown(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Markdown file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            headers = re.findall(r"^#+\s+(.+)$", content, re.MULTILINE)
            return {"language": ".md", "functions": [], "classes": {}, "headers": headers, "line_count": len(content.splitlines()), "complexity": len(headers), "header_count": len(headers)}
        except Exception as e:
            return {"language": ".md", "functions": [], "classes": {}, "line_count": 0, "complexity": 0, "error": str(e)}

    def _analyze_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Analyze YAML file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            keys = [line.split(":")[0].strip() for line in content.splitlines() if ":" in line and not line.startswith("#")]
            return {"language": ".yml", "functions": [], "classes": {}, "keys": keys, "line_count": len(content.splitlines()), "complexity": len(keys), "key_count": len(keys)}
        except Exception as e:
            return {"language": ".yml", "functions": [], "classes": {}, "line_count": 0, "complexity": 0, "error": str(e)}

    def get_directory_structure(self, root_path: Path, max_depth: int = 3) -> Dict[str, Any]:
        """Get directory structure with file counts."""
        structure = {}
        total_files, total_dirs = 0, 0
        for root, dirs, files in os.walk(root_path):
            rel_path = os.path.relpath(root, root_path) if Path(root) != root_path else "."
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]
            if any(skip in Path(rel_path).parts for skip in self.skip_dirs): continue
            file_counts = Counter(Path(f).suffix.lower() for f in files)
            structure[rel_path] = {"files": dict(file_counts), "file_count": len(files), "subdirs": len(dirs)}
            total_files += len(files)
            total_dirs += len(dirs)
            if root.count(os.sep) - str(root_path).count(os.sep) >= max_depth: dirs[:] = []
        return {"structure": structure, "total_files": total_files, "total_dirs": total_dirs}

    def analyze_directories(self, directories: List[str]) -> Dict[str, Any]:
        """Analyze multiple directories comprehensively."""
        all_analysis = {}
        total_files, total_lines, total_functions, total_classes, total_imports = 0, 0, 0, 0, 0
        file_types = Counter()
        complexity_by_type = defaultdict(list)
        for directory in directories:
            if not os.path.exists(directory): continue
            directory_analysis = {}
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = Path(root) / file
                    if any(skip in file_path.parts for skip in self.skip_dirs): continue
                    analysis = self.analyze_file(file_path)
                    directory_analysis[str(file_path.relative_to(directory))] = analysis
                    total_files += 1
                    total_lines += analysis.get("line_count", 0)
                    total_functions += analysis.get("function_count", 0)
                    total_classes += analysis.get("class_count", 0)
                    total_imports += analysis.get("import_count", 0)
                    file_type = analysis.get("language", "unknown")
                    file_types[file_type] += 1
                    complexity_by_type[file_type].append(analysis.get("complexity", 0))
            all_analysis[directory] = directory_analysis
        avg_complexity = {ft: sum(c) / len(c) if c else 0 for ft, c in complexity_by_type.items()}
        return {"directories": all_analysis, "summary": {"total_files": total_files, "total_lines": total_lines, "total_functions": total_functions, "total_classes": total_classes, "total_imports": total_imports, "file_types": dict(file_types), "avg_complexity_by_type": avg_complexity, "total_directories": len(directories)}}

    def analyze_messaging_files(self, messaging_dirs: List[str] = None) -> Dict[str, Any]:
        """Analyze messaging-related files."""
        if messaging_dirs is None:
            messaging_dirs = ["src/services/messaging", "src/core/messaging", "agent_workspaces"]
        messaging_files = []
        for dir_path in messaging_dirs:
            dir_p = Path(dir_path)
            if not dir_p.exists(): continue
            for file_path in dir_p.rglob("*.py"):
                if any(skip in file_path.parts for skip in self.skip_dirs): continue
                analysis = self.analyze_file(file_path)
                if "error" not in analysis:
                    messaging_files.append({"file": str(file_path), "analysis": analysis})
        return {"category": "messaging", "files_analyzed": len(messaging_files), "files": messaging_files[:50], "timestamp": datetime.now().isoformat()}

    def analyze(self, directories: List[str] = None, messaging: bool = False) -> Dict[str, Any]:
        """Run comprehensive source analysis."""
        results = {"timestamp": datetime.now().isoformat(), "analyses": {}}
        if directories:
            results["analyses"]["directories"] = self.analyze_directories(directories)
        if messaging:
            results["analyses"]["messaging"] = self.analyze_messaging_files()
        return results

    def save_results(self, results: Dict[str, Any], output_path: Path):
        """Save analysis results."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"✅ Results saved to: {output_path}")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Source Analyzer")
    parser.add_argument("--directories", type=str, nargs="+", help="Directories to analyze")
    parser.add_argument("--messaging", action="store_true", help="Analyze messaging files")
    parser.add_argument("--structure", type=Path, help="Get directory structure")
    parser.add_argument("--file", type=Path, help="Analyze specific file")
    parser.add_argument("--output", type=Path, default=Path("agent_workspaces/Agent-5/source_analysis.json"), help="Output file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    analyzer = SourceAnalyzer()
    
    if args.file:
        result = analyzer.analyze_file(args.file)
        print(json.dumps(result, indent=2) if args.json else f"File: {args.file}, Functions: {len(result.get('functions', []))}, Classes: {len(result.get('classes', {}))}")
    elif args.structure:
        result = analyzer.get_directory_structure(args.structure)
        print(json.dumps(result, indent=2) if args.json else f"Files: {result['total_files']}, Dirs: {result['total_dirs']}")
    else:
        results = analyzer.analyze(directories=args.directories, messaging=args.messaging)
        analyzer.save_results(results, args.output)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"✅ Analysis complete: {args.output}")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()


