#!/usr/bin/env python3
"""
Unified Test Coverage Tool - V2 Compliant
==========================================

<!-- SSOT Domain: qa -->

Consolidates test coverage tracking, prioritization, and gap analysis.
Replaces: test_coverage_tracker.py, test_coverage_prioritizer.py, analyze_test_coverage_gaps_clean.py

V2 Compliance: <300 lines, single responsibility
Author: Agent-8 (Testing & Quality Assurance Specialist)
Date: 2025-12-03
"""

import ast
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class TestCoverageStatus:
    """Test coverage status for a file."""
    source_file: str
    test_file: Optional[str] = None
    status: str = "PENDING"  # "PENDING", "IN_PROGRESS", "COMPLETE"
    priority: str = "MEDIUM"  # "HIGH", "MEDIUM", "LOW"
    test_count: int = 0
    notes: str = ""


class UnifiedTestCoverage:
    """Unified test coverage tool combining tracking, prioritization, and gap analysis."""
    
    def __init__(self, agent_id: Optional[str] = None, src_dir: Path = Path("src"), tests_dir: Path = Path("tests")):
        """Initialize unified test coverage tool."""
        self.agent_id = agent_id
        self.src_dir = src_dir
        self.tests_dir = tests_dir
        self.statuses: Dict[str, TestCoverageStatus] = {}
        self.priority_weights = {
            "core_infrastructure": 10,
            "services": 8,
            "repositories": 7,
            "utils": 5,
            "discord_commander": 4,
            "other": 3
        }
        self._load_unnecessary_files()
    
    def _load_unnecessary_files(self) -> set:
        """Load unnecessary files data if available."""
        try:
            with open("agent_workspaces/Agent-5/unnecessary_files_analysis.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            unnecessary = set()
            for category in ["unused", "deprecated_directory", "deletion_markers", "duplicates"]:
                for file_info in data.get(category, []):
                    unnecessary.add(file_info["file_path"])
            return unnecessary
        except Exception:
            return set()
    
    # ================================
    # TRACKING FUNCTIONALITY
    # ================================
    
    def load_status(self, workspace_path: Optional[str] = None) -> None:
        """Load test coverage status from file."""
        if not self.agent_id:
            return
        status_file = Path(workspace_path or f"agent_workspaces/{self.agent_id}") / "test_coverage_status.json"
        if status_file.exists():
            with open(status_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.statuses = {k: TestCoverageStatus(**v) for k, v in data.items()}
    
    def save_status(self, workspace_path: Optional[str] = None) -> None:
        """Save test coverage status to file."""
        if not self.agent_id:
            return
        status_file = Path(workspace_path or f"agent_workspaces/{self.agent_id}") / "test_coverage_status.json"
        status_file.parent.mkdir(parents=True, exist_ok=True)
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump({k: asdict(v) for k, v in self.statuses.items()}, f, indent=2)
    
    def add_file(self, source_file: str, priority: str = "MEDIUM") -> None:
        """Add a file to track."""
        if source_file not in self.statuses:
            self.statuses[source_file] = TestCoverageStatus(
                source_file=source_file,
                priority=priority
            )
    
    def update_status(self, source_file: str, test_file: Optional[str] = None,
                     status: Optional[str] = None, test_count: Optional[int] = None,
                     notes: Optional[str] = None) -> None:
        """Update status for a file."""
        if source_file not in self.statuses:
            self.add_file(source_file)
        status_obj = self.statuses[source_file]
        if test_file:
            status_obj.test_file = test_file
        if status:
            status_obj.status = status
        if test_count is not None:
            status_obj.test_count = test_count
        if notes:
            status_obj.notes = notes
    
    def get_progress(self) -> Dict[str, int]:
        """Get progress statistics."""
        total = len(self.statuses)
        complete = sum(1 for s in self.statuses.values() if s.status == "COMPLETE")
        return {
            "total": total,
            "complete": complete,
            "pending": total - complete,
            "completion_percentage": (complete / total * 100) if total > 0 else 0
        }
    
    # ================================
    # PRIORITIZATION FUNCTIONALITY
    # ================================
    
    def _categorize_file(self, file_path: Path) -> str:
        """Categorize file by path."""
        path_str = str(file_path)
        if "core" in path_str:
            return "core_infrastructure"
        elif "services" in path_str:
            return "services"
        elif "repositories" in path_str:
            return "repositories"
        elif "utils" in path_str:
            return "utils"
        elif "discord_commander" in path_str:
            return "discord_commander"
        return "other"
    
    def _count_complexity(self, file_path: Path) -> Dict[str, int]:
        """Count complexity metrics."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            lines = len(open(file_path, 'r', encoding='utf-8').readlines())
            return {
                'functions': functions,
                'classes': classes,
                'lines': lines,
                'complexity_score': functions * 2 + classes * 3 + (lines // 10)
            }
        except Exception:
            return {'functions': 0, 'classes': 0, 'lines': 0, 'complexity_score': 0}
    
    def _check_has_tests(self, file_path: Path) -> bool:
        """Check if file has corresponding test file."""
        file_stem = file_path.stem
        test_patterns = [f"test_{file_stem}.py", f"test_{file_path.parent.name}_{file_stem}.py"]
        for pattern in test_patterns:
            if list(self.tests_dir.rglob(pattern)):
                return True
        return False
    
    def prioritize_files(self, focus: Optional[str] = None) -> List[Dict]:
        """Prioritize files for test coverage."""
        python_files = [f for f in self.src_dir.rglob("*.py")
                       if "test_" not in f.name and f.name != "__init__.py"]
        if focus:
            python_files = [f for f in python_files if focus in str(f)]
        
        prioritized = []
        for file_path in python_files:
            category = self._categorize_file(file_path)
            complexity = self._count_complexity(file_path)
            has_tests = self._check_has_tests(file_path)
            if has_tests:
                continue
            
            category_weight = self.priority_weights.get(category, 3)
            complexity_weight = min(complexity['complexity_score'] / 10, 5)
            priority_score = category_weight * 3 + complexity_weight * 2
            
            prioritized.append({
                'file': str(file_path.relative_to(Path.cwd())),
                'category': category,
                'priority_score': round(priority_score, 2),
                'complexity': complexity,
                'has_tests': has_tests
            })
        
        prioritized.sort(key=lambda x: x['priority_score'], reverse=True)
        return prioritized
    
    # ================================
    # GAP ANALYSIS FUNCTIONALITY
    # ================================
    
    def analyze_gaps(self) -> Dict[str, Any]:
        """Analyze test coverage gaps."""
        source_files = [f for f in self.src_dir.rglob("*.py")
                       if "__pycache__" not in str(f) and "__init__" not in str(f)]
        test_files = list(self.tests_dir.rglob("test_*.py"))
        
        analyzed = []
        for source_file in source_files:
            has_test = self._check_has_tests(source_file)
            complexity = self._count_complexity(source_file)
            priority = 100 if not has_test else 0
            priority += complexity.get('class_count', 0) * 10
            priority += complexity.get('function_count', 0) * 5
            
            analyzed.append({
                "source_file": str(source_file),
                "has_test": has_test,
                "priority": priority,
                "complexity": complexity
            })
        
        analyzed.sort(key=lambda x: x.get("priority", 0), reverse=True)
        files_with_tests = sum(1 for f in analyzed if f.get("has_test", False))
        total_files = len(analyzed)
        
        return {
            "total_source_files": total_files,
            "files_with_tests": files_with_tests,
            "files_without_tests": total_files - files_with_tests,
            "coverage_percentage": round((files_with_tests / total_files * 100) if total_files > 0 else 0, 2),
            "all_files": analyzed
        }
    
    # ================================
    # REPORTING
    # ================================
    
    def generate_report(self, mode: str = "tracking") -> str:
        """Generate coverage report."""
        if mode == "tracking":
            progress = self.get_progress()
            return f"# Test Coverage Progress\n\nTotal: {progress['total']}, Complete: {progress['complete']} ({progress['completion_percentage']:.1f}%)"
        elif mode == "gaps":
            gaps = self.analyze_gaps()
            return f"# Test Coverage Gaps\n\nCoverage: {gaps['coverage_percentage']}%, Gaps: {gaps['files_without_tests']}"
        return "# Test Coverage Report"


def main():
    """CLI interface."""
    parser = argparse.ArgumentParser(description="Unified test coverage tool")
    parser.add_argument("--agent", help="Agent ID for tracking")
    parser.add_argument("--track", action="store_true", help="Track coverage")
    parser.add_argument("--prioritize", action="store_true", help="Prioritize files")
    parser.add_argument("--gaps", action="store_true", help="Analyze gaps")
    parser.add_argument("--report", action="store_true", help="Generate report")
    parser.add_argument("--add", help="Add file to track")
    parser.add_argument("--update", help="Update file status")
    args = parser.parse_args()
    
    tool = UnifiedTestCoverage(agent_id=args.agent)
    if args.agent:
        tool.load_status()
    
    if args.add:
        tool.add_file(args.add)
        print(f"✅ Added {args.add}")
    
    if args.track:
        progress = tool.get_progress()
        print(f"📊 Progress: {progress['complete']}/{progress['total']} ({progress['completion_percentage']:.1f}%)")
    
    if args.prioritize:
        prioritized = tool.prioritize_files()
        print(f"📋 Top 10 priorities:")
        for item in prioritized[:10]:
            print(f"  {item['file']} (Score: {item['priority_score']})")
    
    if args.gaps:
        gaps = tool.analyze_gaps()
        print(f"📊 Coverage: {gaps['coverage_percentage']}%")
        print(f"📊 Gaps: {gaps['files_without_tests']} files")
    
    if args.report:
        print(tool.generate_report())
    
    if args.agent:
        tool.save_status()


if __name__ == "__main__":
    main()


