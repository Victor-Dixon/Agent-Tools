#!/usr/bin/env python3
"""
Code Analysis Tool - Consolidated Complexity & Refactoring Analysis
====================================================================

Consolidates complexity analysis, refactoring suggestions, and AST-based
code structure analysis into a single unified tool.

Replaces:
- complexity_analyzer_core.py
- complexity_analyzer_formatters.py
- refactor_analyzer.py
- refactoring_ast_analyzer.py

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-03
V2 Compliant: Yes (<300 lines)
SSOT Domain: analytics

<!-- SSOT Domain: analytics -->
"""

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# SSOT Domain: analytics


@dataclass
class ComplexityMetrics:
    """Complexity metrics for a code entity."""
    entity_name: str
    entity_type: str
    cyclomatic: int
    cognitive: int
    nesting_depth: int
    line_count: int
    start_line: int
    end_line: int


@dataclass
class ComplexityViolation:
    """Represents a complexity violation."""
    file_path: str
    entity_name: str
    entity_type: str
    violation_type: str
    current_value: int
    threshold: int
    line_number: int
    severity: str
    suggestion: str


@dataclass
class RefactoringSuggestion:
    """Refactoring suggestion for a file."""
    priority: str
    type: str
    message: str
    candidates: List[str] = None


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor for cyclomatic complexity."""
    def __init__(self):
        self.complexity = 1
        self.nesting_level = 0
        self.max_nesting = 0
    
    def visit_If(self, node):
        self.complexity += 1
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1
    
    def visit_While(self, node):
        self.complexity += 1
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1
    
    def visit_For(self, node):
        self.complexity += 1
        self.nesting_level += 1
        self.max_nesting = max(self.max_nesting, self.nesting_level)
        self.generic_visit(node)
        self.nesting_level -= 1
    
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)


class CognitiveVisitor(ast.NodeVisitor):
    """AST visitor for cognitive complexity."""
    def __init__(self):
        self.complexity = 0
        self.nesting_level = 0
    
    def visit_If(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
    
    def visit_While(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
    
    def visit_For(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1


class CodeAnalysisTool:
    """Unified code analysis tool for complexity and refactoring."""
    
    CYCLOMATIC_THRESHOLD = 10
    COGNITIVE_THRESHOLD = 15
    NESTING_THRESHOLD = 4
    FILE_SIZE_THRESHOLD = 400
    
    def __init__(self):
        """Initialize analyzer."""
        pass
    
    def analyze_complexity(self, file_path: Path) -> Dict[str, Any]:
        """Analyze file for complexity metrics."""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            metrics = []
            violations = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metric = self._analyze_function(node, file_path, content)
                    if metric:
                        metrics.append(metric)
                        violations.extend(self._check_violations(metric, file_path))
            
            avg_cyclomatic = sum(m.cyclomatic for m in metrics) / len(metrics) if metrics else 0
            avg_cognitive = sum(m.cognitive for m in metrics) / len(metrics) if metrics else 0
            max_nesting = max((m.nesting_depth for m in metrics), default=0)
            
            return {
                "file_path": str(file_path),
                "total_functions": len(metrics),
                "avg_cyclomatic": round(avg_cyclomatic, 1),
                "avg_cognitive": round(avg_cognitive, 1),
                "max_nesting": max_nesting,
                "violations": [self._violation_to_dict(v) for v in violations],
                "metrics": [self._metric_to_dict(m) for m in metrics],
            }
        except Exception:
            return {"file_path": str(file_path), "error": "Analysis failed"}
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: Path, content: str) -> Optional[ComplexityMetrics]:
        """Analyze complexity of a single function."""
        try:
            cyclomatic_visitor = ComplexityVisitor()
            cyclomatic_visitor.visit(node)
            cognitive_visitor = CognitiveVisitor()
            cognitive_visitor.visit(node)
            end_line = node.end_lineno if hasattr(node, "end_lineno") else node.lineno
            line_count = end_line - node.lineno + 1
            entity_type = "method" if node.col_offset > 0 else "function"
            return ComplexityMetrics(
                entity_name=node.name,
                entity_type=entity_type,
                cyclomatic=cyclomatic_visitor.complexity,
                cognitive=cognitive_visitor.complexity,
                nesting_depth=cyclomatic_visitor.max_nesting,
                line_count=line_count,
                start_line=node.lineno,
                end_line=end_line,
            )
        except Exception:
            return None
    
    def _check_violations(self, metric: ComplexityMetrics, file_path: Path) -> List[ComplexityViolation]:
        """Check for complexity violations."""
        violations = []
        checks = [
            (metric.cyclomatic, self.CYCLOMATIC_THRESHOLD, "CYCLOMATIC", "Extract conditional logic, use early returns"),
            (metric.cognitive, self.COGNITIVE_THRESHOLD, "COGNITIVE", "Reduce nesting, extract helper functions"),
            (metric.nesting_depth, self.NESTING_THRESHOLD, "NESTING", "Use early returns, extract inner loops"),
        ]
        for value, threshold, vtype, suggestion in checks:
            if value > threshold:
                violations.append(ComplexityViolation(
                    file_path=str(file_path), entity_name=metric.entity_name, entity_type=metric.entity_type,
                    violation_type=vtype, current_value=value, threshold=threshold, line_number=metric.start_line,
                    severity=self._get_severity(value, threshold), suggestion=suggestion,
                ))
        return violations
    
    def _get_severity(self, value: int, threshold: int) -> str:
        """Determine severity based on threshold."""
        ratio = value / threshold
        return "HIGH" if ratio >= 2.0 else "MEDIUM" if ratio >= 1.5 else "LOW"
    
    def analyze_refactoring(self, file_path: Path) -> Dict[str, Any]:
        """Analyze file for refactoring opportunities."""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
            total_lines = len(content.split('\n'))
            functions, classes, imports = [], [], []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    end = node.end_lineno if hasattr(node, "end_lineno") else node.lineno
                    functions.append({"name": node.name, "lines": end - node.lineno + 1, "private": node.name.startswith('_'), "start": node.lineno})
                elif isinstance(node, ast.ClassDef) and node.col_offset == 0:
                    end = node.end_lineno if hasattr(node, "end_lineno") else node.lineno
                    classes.append({"name": node.name, "lines": end - node.lineno + 1, "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)]), "start": node.lineno})
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(f"from {node.module} import ..." if isinstance(node, ast.ImportFrom) else f"import {node.names[0].name}")
            suggestions = []
            if total_lines > self.FILE_SIZE_THRESHOLD:
                suggestions.append({"priority": "CRITICAL" if total_lines > 600 else "MAJOR", "type": "file_size", "message": f"File has {total_lines} lines (target: ≤{self.FILE_SIZE_THRESHOLD})"})
                large = [f for f in functions if f["lines"] > 30 and f["private"]]
                if large: suggestions.append({"priority": "HIGH", "type": "extract_functions", "message": f"Extract {len(large)} large private functions", "candidates": [f["name"] for f in large[:3]]})
                scanners = [f for f in functions if "scan" in f["name"].lower() or "check" in f["name"].lower()]
                if len(scanners) > 3: suggestions.append({"priority": "HIGH", "type": "extract_scanners", "message": f"Extract {len(scanners)} scanner functions", "candidates": [f["name"] for f in scanners]})
            return {"file": str(file_path), "total_lines": total_lines, "functions": functions, "classes": classes, "imports": imports, "suggestions": suggestions, "v2_compliant": total_lines <= self.FILE_SIZE_THRESHOLD}
        except Exception as e:
            return {"file": str(file_path), "error": str(e)}
    
    
    def _violation_to_dict(self, v: ComplexityViolation) -> Dict[str, Any]:
        """Convert violation to dict."""
        return {"entity_name": v.entity_name, "entity_type": v.entity_type, "violation_type": v.violation_type, "current_value": v.current_value, "threshold": v.threshold, "line_number": v.line_number, "severity": v.severity, "suggestion": v.suggestion}
    
    def _metric_to_dict(self, m: ComplexityMetrics) -> Dict[str, Any]:
        """Convert metric to dict."""
        return {"entity_name": m.entity_name, "entity_type": m.entity_type, "cyclomatic": m.cyclomatic, "cognitive": m.cognitive, "nesting_depth": m.nesting_depth, "line_count": m.line_count, "start_line": m.start_line, "end_line": m.end_line}
    
    def generate_report(self, file_path: Path, output_path: Path = None):
        """Generate comprehensive analysis report."""
        c, r = self.analyze_complexity(file_path), self.analyze_refactoring(file_path)
        report = f"# Code Analysis: {file_path.name}\n\n## Complexity\n- Functions: {c.get('total_functions', 0)}, Avg Cyclomatic: {c.get('avg_cyclomatic', 0):.1f}, Violations: {len(c.get('violations', []))}\n\n## Refactoring\n- Lines: {r.get('total_lines', 0)}, V2: {'✅' if r.get('v2_compliant') else '❌'}, Suggestions: {len(r.get('suggestions', []))}\n\n---\n🐝 **WE. ARE. SWARM. ⚡🔥**\n"
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report, encoding="utf-8")
            print(f"✅ Report: {output_path}")
        else:
            print(report)


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Code Analysis Tool")
    parser.add_argument("file", type=Path, help="Python file to analyze")
    parser.add_argument("--output", type=Path, help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    tool = CodeAnalysisTool()
    if args.json:
        result = {"complexity": tool.analyze_complexity(args.file), "refactoring": tool.analyze_refactoring(args.file)}
        print(json.dumps(result, indent=2))
    else:
        tool.generate_report(args.file, args.output)
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()

