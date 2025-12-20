#!/usr/bin/env python3
"""
Violation Consolidation Analyzer Tool
======================================

A tool I wished I had during Phase 1 Violation Consolidation analysis.
Automates the analysis of duplicate classes/functions to determine if they
are true duplicates or domain-specific naming collisions.

Author: Agent-1 (Integration & Core Systems Specialist)
Created: 2025-12-05
License: MIT
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class ViolationLocation:
    """Represents a violation location."""
    file_path: str
    line_number: int
    class_or_function_name: str
    type: str  # "class" or "function"
    code_snippet: str
    imports: List[str]
    context: str  # Surrounding code context


@dataclass
class ViolationAnalysis:
    """Analysis result for a violation."""
    name: str
    locations: List[ViolationLocation]
    is_true_duplicate: bool
    is_domain_specific: bool
    recommended_action: str  # "consolidate", "rename", "keep_separate"
    confidence: float  # 0.0 to 1.0
    reasoning: str
    domain_analysis: Dict[str, List[str]]  # domain -> [file_paths]


class ViolationConsolidationAnalyzer:
    """Analyzes violations to determine consolidation strategy."""
    
    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.violations: Dict[str, List[ViolationLocation]] = defaultdict(list)
        self.domain_patterns = {
            "gaming": ["gaming", "dreamos", "fsm", "osrs"],
            "contract": ["contract", "task_repo"],
            "scheduler": ["scheduler", "overnight", "orchestrator"],
            "autonomous": ["autonomous", "task_engine", "markov"],
            "domain": ["domain", "entities", "value_objects"],
            "infrastructure": ["infrastructure", "persistence", "repositories"],
            "core": ["core", "intelligent_context", "coordination"],
        }
    
    def scan_violations(self, violation_name: str, violation_type: str = "class") -> List[ViolationLocation]:
        """Scan codebase for violation locations."""
        locations = []
        
        for py_file in self.root_path.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
            
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
                visitor = ViolationVisitor(violation_name, violation_type, py_file)
                visitor.visit(tree)
                locations.extend(visitor.locations)
            except (SyntaxError, UnicodeDecodeError):
                continue
        
        return locations
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [
            "__pycache__",
            ".git",
            "node_modules",
            "venv",
            "env",
            "temp_repos",
            "archive",
        ]
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def analyze_violation(self, violation_name: str, violation_type: str = "class") -> ViolationAnalysis:
        """Analyze a violation to determine consolidation strategy."""
        locations = self.scan_violations(violation_name, violation_type)
        
        if len(locations) < 2:
            return ViolationAnalysis(
                name=violation_name,
                locations=locations,
                is_true_duplicate=False,
                is_domain_specific=False,
                recommended_action="keep_separate",
                confidence=1.0,
                reasoning="Only one location found, no consolidation needed",
                domain_analysis={}
            )
        
        # Analyze domains
        domain_analysis = self._analyze_domains(locations)
        
        # Check if true duplicate
        is_true_duplicate = self._check_true_duplicate(locations)
        
        # Check if domain-specific
        is_domain_specific = len(domain_analysis) > 1
        
        # Determine recommended action
        recommended_action, confidence, reasoning = self._recommend_action(
            is_true_duplicate, is_domain_specific, domain_analysis, locations
        )
        
        return ViolationAnalysis(
            name=violation_name,
            locations=locations,
            is_true_duplicate=is_true_duplicate,
            is_domain_specific=is_domain_specific,
            recommended_action=recommended_action,
            confidence=confidence,
            reasoning=reasoning,
            domain_analysis=domain_analysis
        )
    
    def _analyze_domains(self, locations: List[ViolationLocation]) -> Dict[str, List[str]]:
        """Analyze which domains each location belongs to."""
        domain_map = defaultdict(list)
        
        for location in locations:
            file_path = location.file_path.lower()
            matched_domains = []
            
            for domain, patterns in self.domain_patterns.items():
                if any(pattern in file_path for pattern in patterns):
                    matched_domains.append(domain)
            
            if matched_domains:
                for domain in matched_domains:
                    domain_map[domain].append(location.file_path)
            else:
                domain_map["unknown"].append(location.file_path)
        
        return dict(domain_map)
    
    def _check_true_duplicate(self, locations: List[ViolationLocation]) -> bool:
        """Check if locations are true duplicates (same code, same purpose)."""
        if len(locations) < 2:
            return False
        
        # Compare code snippets (simplified - could use AST comparison)
        code_snippets = [loc.code_snippet for loc in locations]
        
        # If all code snippets are identical, likely true duplicate
        if len(set(code_snippets)) == 1:
            return True
        
        # If code snippets are very similar (>90% similarity), likely duplicate
        # (Simplified - would use more sophisticated comparison in production)
        return False
    
    def _recommend_action(
        self,
        is_true_duplicate: bool,
        is_domain_specific: bool,
        domain_analysis: Dict[str, List[str]],
        locations: List[ViolationLocation]
    ) -> Tuple[str, float, str]:
        """Recommend consolidation action."""
        if is_true_duplicate:
            return "consolidate", 0.9, "True duplicate detected - consolidate to SSOT"
        
        if is_domain_specific:
            return "rename", 0.85, f"Domain-specific classes detected across {len(domain_analysis)} domains - rename to avoid confusion"
        
        if len(locations) == 2:
            # Check if they're in same domain
            if len(domain_analysis) == 1:
                return "consolidate", 0.7, "Two locations in same domain - likely can consolidate"
            else:
                return "rename", 0.75, "Two locations in different domains - rename for clarity"
        
        return "keep_separate", 0.6, "Multiple locations with unclear relationship - manual review needed"
    
    def generate_report(self, analyses: List[ViolationAnalysis], output_path: Path) -> None:
        """Generate analysis report."""
        report = {
            "summary": {
                "total_violations": len(analyses),
                "true_duplicates": sum(1 for a in analyses if a.is_true_duplicate),
                "domain_specific": sum(1 for a in analyses if a.is_domain_specific),
                "recommended_consolidate": sum(1 for a in analyses if a.recommended_action == "consolidate"),
                "recommended_rename": sum(1 for a in analyses if a.recommended_action == "rename"),
            },
            "analyses": [asdict(analysis) for analysis in analyses]
        }
        
        output_path.write_text(json.dumps(report, indent=2, default=str))
        print(f"✅ Report generated: {output_path}")


class ViolationVisitor(ast.NodeVisitor):
    """AST visitor to find violation locations."""
    
    def __init__(self, target_name: str, violation_type: str, file_path: Path):
        self.target_name = target_name
        self.violation_type = violation_type
        self.file_path = file_path
        self.locations: List[ViolationLocation] = []
        self.imports: List[str] = []
    
    def visit_Import(self, node: ast.Import) -> None:
        """Track imports."""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track imports."""
        if node.module:
            for alias in node.names:
                self.imports.append(f"{node.module}.{alias.name}")
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        if self.violation_type == "class" and node.name == self.target_name:
            code_snippet = ast.get_source_segment(
                self.file_path.read_text(encoding="utf-8"), node
            ) or ""
            
            self.locations.append(ViolationLocation(
                file_path=str(self.file_path),
                line_number=node.lineno,
                class_or_function_name=node.name,
                type="class",
                code_snippet=code_snippet[:500],  # Limit snippet size
                imports=self.imports.copy(),
                context=self._get_context(node)
            ))
        
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        if self.violation_type == "function" and node.name == self.target_name:
            code_snippet = ast.get_source_segment(
                self.file_path.read_text(encoding="utf-8"), node
            ) or ""
            
            self.locations.append(ViolationLocation(
                file_path=str(self.file_path),
                line_number=node.lineno,
                class_or_function_name=node.name,
                type="function",
                code_snippet=code_snippet[:500],
                imports=self.imports.copy(),
                context=self._get_context(node)
            ))
        
        self.generic_visit(node)
    
    def _get_context(self, node: ast.AST) -> str:
        """Get surrounding context."""
        # Simplified - would extract more context in production
        return f"Line {node.lineno}"


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze violations for consolidation")
    parser.add_argument("violation_name", help="Name of class or function to analyze")
    parser.add_argument("--type", choices=["class", "function"], default="class", help="Violation type")
    parser.add_argument("--root", type=Path, default=Path("."), help="Root directory to scan")
    parser.add_argument("--output", type=Path, help="Output report path (JSON)")
    
    args = parser.parse_args()
    
    analyzer = ViolationConsolidationAnalyzer(args.root)
    analysis = analyzer.analyze_violation(args.violation_name, args.type)
    
    print(f"\n📊 Analysis for '{args.violation_name}' ({args.type}):")
    print(f"   Locations found: {len(analysis.locations)}")
    print(f"   True duplicate: {analysis.is_true_duplicate}")
    print(f"   Domain-specific: {analysis.is_domain_specific}")
    print(f"   Recommended action: {analysis.recommended_action}")
    print(f"   Confidence: {analysis.confidence:.2f}")
    print(f"   Reasoning: {analysis.reasoning}")
    
    if analysis.domain_analysis:
        print(f"\n   Domain breakdown:")
        for domain, files in analysis.domain_analysis.items():
            print(f"     {domain}: {len(files)} files")
    
    if args.output:
        analyzer.generate_report([analysis], args.output)


if __name__ == "__main__":
    main()

