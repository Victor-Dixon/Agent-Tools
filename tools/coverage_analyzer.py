#!/usr/bin/env python3
"""
Coverage Analyzer - Consolidated Test Coverage Analysis Tool
=============================================================

Consolidates test coverage gap analysis, pipeline execution, and usage analysis.

Replaces:
- analyze_test_coverage_gaps_clean.py
- run_coverage_analysis.py (pipeline aspects)
- test_usage_analyzer.py (usage aspects)

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-03
V2 Compliant: Yes (<300 lines)
SSOT Domain: analytics

<!-- SSOT Domain: analytics -->
"""

import ast
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Load unnecessary files data
try:
    with open("agent_workspaces/Agent-5/unnecessary_files_analysis.json", "r", encoding="utf-8") as f:
        unnecessary_data = json.load(f)
    unnecessary_files = set()
    for category in ["unused", "deprecated_directory", "deletion_markers", "duplicates"]:
        for file_info in unnecessary_data.get(category, []):
            unnecessary_files.add(file_info["file_path"])
except Exception:
    unnecessary_files = set()


class CoverageAnalyzer:
    """Unified test coverage analyzer."""

    def __init__(self, src_root: str = "src", tests_root: str = "tests"):
        """Initialize analyzer."""
        self.src_root = Path(src_root)
        self.tests_root = Path(tests_root)
        self.unnecessary_files = unnecessary_files
        self.thresholds = {"global_line_coverage_min": 85, "changed_code_line_coverage_min": 95}

    def find_source_files(self) -> List[Path]:
        """Find all Python source files, excluding unnecessary ones."""
        source_files = []
        for path in self.src_root.rglob("*.py"):
            if "__pycache__" not in str(path) and "__init__" not in str(path):
                if str(path) not in self.unnecessary_files:
                    source_files.append(path)
        return sorted(source_files)

    def find_test_files(self) -> List[Path]:
        """Find all test files."""
        test_files = []
        for path in self.tests_root.rglob("test_*.py"):
            if "__pycache__" not in str(path):
                test_files.append(path)
        return sorted(test_files)

    def get_test_for_source(self, source_file: Path) -> Optional[Path]:
        """Find corresponding test file for source file."""
        relative = source_file.relative_to(self.src_root)
        test_name = f"test_{relative.stem}.py"
        possible_paths = [
            self.tests_root / relative.parent / test_name,
            self.tests_root / "core" / relative.name.replace(".py", f"test_{relative.name}"),
            self.tests_root / "unit" / relative.name.replace(".py", f"test_{relative.name}"),
        ]
        for path in possible_paths:
            if path.exists():
                return path
        for test_file in self.find_test_files():
            if relative.stem in test_file.stem or test_file.stem.replace("test_", "") == relative.stem:
                return test_file
        return None

    def analyze_file(self, source_file: Path) -> Dict[str, Any]:
        """Analyze a single source file."""
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), str(source_file))
            classes, functions = [], []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                    functions.append(node.name)
            test_file = self.get_test_for_source(source_file)
            return {
                "source_file": str(source_file),
                "relative_path": str(source_file.relative_to(self.src_root)),
                "test_file": str(test_file) if test_file else None,
                "has_test": test_file is not None,
                "class_count": len(classes),
                "function_count": len(functions),
                "classes": classes,
                "functions": functions,
            }
        except Exception as e:
            return {"source_file": str(source_file), "error": str(e), "has_test": False}

    def calculate_priority(self, file_data: Dict[str, Any]) -> int:
        """Calculate priority score."""
        priority = 0
        if not file_data.get("has_test", False):
            priority += 100
        priority += file_data.get("class_count", 0) * 10
        priority += file_data.get("function_count", 0) * 5
        path = file_data.get("relative_path", "")
        if any(kw in path for kw in ["core", "engine", "coordinator", "orchestrator"]):
            priority += 50
        if "services" in path:
            priority += 25
        return priority

    def analyze_coverage_gaps(self) -> Dict[str, Any]:
        """Analyze test coverage gaps."""
        source_files = self.find_source_files()
        test_files = self.find_test_files()
        print(f"🔍 Analyzing {len(source_files)} source files...")
        
        analyzed = []
        for source_file in source_files:
            file_data = self.analyze_file(source_file)
            file_data["priority"] = self.calculate_priority(file_data)
            analyzed.append(file_data)
        
        analyzed.sort(key=lambda x: x.get("priority", 0), reverse=True)
        total_files = len(analyzed)
        files_with_tests = sum(1 for f in analyzed if f.get("has_test", False))
        coverage_percentage = (files_with_tests / total_files * 100) if total_files > 0 else 0
        
        return {
            "total_source_files": total_files,
            "total_test_files": len(test_files),
            "files_with_tests": files_with_tests,
            "files_without_tests": total_files - files_with_tests,
            "coverage_percentage": round(coverage_percentage, 2),
            "all_files": analyzed,
        }

    def run_coverage_pipeline(self) -> bool:
        """Run coverage analysis pipeline."""
        print("\n🔄 Running coverage pipeline...")
        commands = [
            (["pytest", "-q", "--maxfail=1"], "Quick test check"),
            (["coverage", "run", "-m", "pytest", "-q"], "Tests with coverage"),
            (["coverage", "html", "-d", ".coverage_html"], "HTML report"),
            (["coverage", "report", "--show-missing"], "Coverage report"),
        ]
        success = True
        for cmd, desc in commands:
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(f"✅ {desc} completed")
            except subprocess.CalledProcessError:
                print(f"❌ {desc} failed")
                success = False
        return success

    def analyze_test_usage(self, module_path: Path) -> Dict[str, Any]:
        """Analyze test usage for a module."""
        try:
            with open(module_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(module_path))
            functions, classes = [], []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not any(isinstance(p, ast.ClassDef) for p in ast.walk(tree) if hasattr(p, 'body') and node in getattr(p, 'body', [])):
                        functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
            
            test_file = self.get_test_for_source(module_path)
            tested_methods = set()
            if test_file and test_file.exists():
                try:
                    with open(test_file, "r", encoding="utf-8") as f:
                        test_tree = ast.parse(f.read(), filename=str(test_file))
                    for node in ast.walk(test_tree):
                        if isinstance(node, ast.Call):
                            if isinstance(node.func, ast.Attribute):
                                tested_methods.add(node.func.attr)
                except Exception:
                    pass
            
            return {
                "module": str(module_path),
                "functions": len(functions),
                "classes": len(classes),
                "tested_methods": len(tested_methods),
                "has_test": test_file is not None,
            }
        except Exception as e:
            return {"module": str(module_path), "error": str(e)}

    def generate_priority_matrix(self, analysis: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Generate priority matrix."""
        matrix = {"critical": [], "high": [], "medium": [], "low": []}
        for file_data in analysis["all_files"]:
            if not file_data.get("has_test", False):
                priority = file_data.get("priority", 0)
                if priority >= 200:
                    matrix["critical"].append(file_data)
                elif priority >= 150:
                    matrix["high"].append(file_data)
                elif priority >= 100:
                    matrix["medium"].append(file_data)
                else:
                    matrix["low"].append(file_data)
        return matrix

    def analyze(self) -> Dict[str, Any]:
        """Run comprehensive coverage analysis."""
        print("🔍 COVERAGE ANALYZER")
        print("=" * 60)
        
        gaps = self.analyze_coverage_gaps()
        matrix = self.generate_priority_matrix(gaps)
        
        print(f"\n✅ Analysis complete!")
        print(f"   Coverage: {gaps['coverage_percentage']}%")
        print(f"   Files without tests: {gaps['files_without_tests']}")
        print(f"   Critical priority: {len(matrix['critical'])} files")
        
        return {
            "summary": {
                "total_source_files": gaps["total_source_files"],
                "coverage_percentage": gaps["coverage_percentage"],
                "files_without_tests": gaps["files_without_tests"],
            },
            "gaps": gaps,
            "priority_matrix": matrix,
        }

    def save_results(self, results: Dict[str, Any], output_path: Path):
        """Save analysis results."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"✅ Results saved to: {output_path}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Coverage Analyzer")
    parser.add_argument("--output", type=Path,
                       default=Path("agent_workspaces/Agent-5/coverage_analysis.json"),
                       help="Output JSON file path")
    parser.add_argument("--pipeline", action="store_true", help="Run coverage pipeline")
    parser.add_argument("--src-root", type=str, default="src", help="Source root directory")
    parser.add_argument("--tests-root", type=str, default="tests", help="Tests root directory")
    
    args = parser.parse_args()
    
    analyzer = CoverageAnalyzer(src_root=args.src_root, tests_root=args.tests_root)
    
    if args.pipeline:
        analyzer.run_coverage_pipeline()
    
    results = analyzer.analyze()
    analyzer.save_results(results, args.output)
    
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()


