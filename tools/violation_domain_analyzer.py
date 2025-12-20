#!/usr/bin/env python3
"""
Violation Domain Analyzer - Domain Boundary Analysis Tool
=========================================================

Analyzes violation locations to determine if they are true duplicates
(consolidate) or naming collisions with different domain purposes (rename).

This tool helps identify domain boundaries before consolidation to prevent
breaking changes and maintain proper architecture.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-12-05
V2 Compliant: Yes (<300 lines)
SSOT Domain: analysis

Usage:
    python tools/violation_domain_analyzer.py --class-name Task --locations file1.py:16 file2.py:35
    python tools/violation_domain_analyzer.py --class-name Task --scan-dir src/
"""

import ast
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import re


class ViolationDomainAnalyzer:
    """Analyzes violations to determine domain boundaries and consolidation strategy."""

    def __init__(self):
        self.domain_indicators = {
            "domain": ["domain", "entity", "value_object"],
            "gaming": ["gaming", "game", "fsm", "dreamos"],
            "infrastructure": ["infrastructure", "persistence", "repository"],
            "tools": ["tools", "tool", "autonomous"],
            "services": ["services", "service", "contract"],
            "orchestrators": ["orchestrator", "scheduler"],
            "core": ["core", "intelligent_context"],
        }

    def analyze_class_definition(self, file_path: Path, line_number: int) -> Dict[str, Any]:
        """Analyze a single class definition."""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Get line numbers for class definition
                    class_start = node.lineno
                    class_end = node.end_lineno if hasattr(node, "end_lineno") else class_start
                    
                    if class_start <= line_number <= class_end:
                        return {
                            "file": str(file_path),
                            "line": line_number,
                            "class_name": node.name,
                            "base_classes": [base.id for base in node.bases if isinstance(base, ast.Name)],
                            "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                            "properties": [n.name for n in node.body if isinstance(n, ast.Name)],
                            "docstring": ast.get_docstring(node),
                            "domain_context": self._detect_domain(file_path, node),
                            "structure": self._analyze_structure(node),
                        }
            
            return {"file": str(file_path), "line": line_number, "error": "Class not found"}
        except Exception as e:
            return {"file": str(file_path), "line": line_number, "error": str(e)}

    def _detect_domain(self, file_path: Path, class_node: ast.ClassDef) -> str:
        """Detect domain context from file path and class structure."""
        file_path_str = str(file_path).lower()
        
        # Check file path for domain indicators
        for domain, indicators in self.domain_indicators.items():
            if any(indicator in file_path_str for indicator in indicators):
                return domain
        
        # Check class docstring
        docstring = ast.get_docstring(class_node)
        if docstring:
            docstring_lower = docstring.lower()
            for domain, indicators in self.domain_indicators.items():
                if any(indicator in docstring_lower for indicator in indicators):
                    return domain
        
        # Default to "unknown"
        return "unknown"

    def _analyze_structure(self, class_node: ast.ClassDef) -> Dict[str, Any]:
        """Analyze class structure to understand purpose."""
        structure = {
            "is_dataclass": False,
            "is_enum": False,
            "has_business_rules": False,
            "has_lifecycle_methods": False,
            "field_count": 0,
            "method_count": 0,
        }
        
        # Check for dataclass decorator
        for decorator in class_node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id in ["dataclass"]:
                structure["is_dataclass"] = True
            elif isinstance(decorator, ast.Attribute) and decorator.attr in ["dataclass"]:
                structure["is_dataclass"] = True
        
        # Check for enum inheritance
        for base in class_node.bases:
            if isinstance(base, ast.Name) and "Enum" in base.id:
                structure["is_enum"] = True
        
        # Analyze methods
        methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
        structure["method_count"] = len(methods)
        
        # Check for business rule indicators
        business_rule_keywords = ["validate", "check", "can_", "is_", "has_", "assign", "complete"]
        for method in methods:
            method_lower = method.name.lower()
            if any(keyword in method_lower for keyword in business_rule_keywords):
                structure["has_business_rules"] = True
            if any(keyword in method_lower for keyword in ["assign", "complete", "cancel"]):
                structure["has_lifecycle_methods"] = True
        
        # Count fields (assignments in __init__ or class variables)
        for node in class_node.body:
            if isinstance(node, ast.AnnAssign) or isinstance(node, ast.Assign):
                structure["field_count"] += 1
        
        return structure

    def compare_locations(self, locations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple violation locations to determine if they're duplicates."""
        if len(locations) < 2:
            return {"error": "Need at least 2 locations to compare"}
        
        comparison = {
            "locations": locations,
            "total_locations": len(locations),
            "domain_distribution": defaultdict(int),
            "structure_similarity": {},
            "consolidation_recommendation": "UNKNOWN",
            "rationale": "",
            "strategy": {},
        }
        
        # Analyze domain distribution
        for loc in locations:
            if "domain_context" in loc:
                comparison["domain_distribution"][loc["domain_context"]] += 1
        
        # Determine if same domain or different domains
        unique_domains = set(loc.get("domain_context", "unknown") for loc in locations)
        
        if len(unique_domains) == 1:
            # Same domain - likely true duplicate
            comparison["consolidation_recommendation"] = "CONSOLIDATE"
            comparison["rationale"] = f"All locations in same domain: {unique_domains.pop()}"
            comparison["strategy"] = {
                "action": "consolidate",
                "ssot": locations[0]["file"],
                "approach": "Merge implementations into single SSOT",
            }
        else:
            # Different domains - likely naming collision
            comparison["consolidation_recommendation"] = "RENAME"
            comparison["rationale"] = f"Locations span multiple domains: {', '.join(unique_domains)}"
            comparison["strategy"] = {
                "action": "rename",
                "approach": "Rename domain-specific classes to avoid confusion",
                "domains": list(unique_domains),
            }
        
        # Analyze structure similarity
        structures = [loc.get("structure", {}) for loc in locations]
        structure_types = set()
        for struct in structures:
            if struct.get("is_dataclass"):
                structure_types.add("dataclass")
            elif struct.get("is_enum"):
                structure_types.add("enum")
            else:
                structure_types.add("regular_class")
        
        comparison["structure_similarity"] = {
            "types": list(structure_types),
            "is_similar": len(structure_types) == 1,
        }
        
        return comparison

    def analyze_class_name(self, class_name: str, scan_dir: Path) -> Dict[str, Any]:
        """Scan directory for all instances of a class name."""
        locations = []
        
        for py_file in scan_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content, str(py_file))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == class_name:
                        analysis = self.analyze_class_definition(py_file, node.lineno)
                        locations.append(analysis)
            except Exception:
                continue
        
        if not locations:
            return {"error": f"Class '{class_name}' not found in {scan_dir}"}
        
        return self.compare_locations(locations)


def parse_location(location_str: str) -> Tuple[Path, int]:
    """Parse location string like 'file.py:16' into Path and line number."""
    if ":" not in location_str:
        raise ValueError(f"Invalid location format: {location_str}. Expected 'file.py:line'")
    
    file_path_str, line_str = location_str.rsplit(":", 1)
    file_path = Path(file_path_str)
    line_number = int(line_str)
    
    return file_path, line_number


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze violation locations for domain boundaries"
    )
    parser.add_argument(
        "--class-name",
        required=True,
        help="Class name to analyze (e.g., 'Task', 'AgentStatus')",
    )
    parser.add_argument(
        "--locations",
        nargs="+",
        help="Location strings like 'file.py:16'",
    )
    parser.add_argument(
        "--scan-dir",
        type=Path,
        default=Path("src"),
        help="Directory to scan for class instances (default: src/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for analysis results (JSON)",
    )
    
    args = parser.parse_args()
    
    analyzer = ViolationDomainAnalyzer()
    
    if args.locations:
        # Analyze specific locations
        locations = []
        for loc_str in args.locations:
            try:
                file_path, line_number = parse_location(loc_str)
                analysis = analyzer.analyze_class_definition(file_path, line_number)
                locations.append(analysis)
            except Exception as e:
                print(f"⚠️  Error parsing location '{loc_str}': {e}")
                continue
        
        if locations:
            result = analyzer.compare_locations(locations)
        else:
            print("❌ No valid locations to analyze")
            return 1
    else:
        # Scan directory
        result = analyzer.analyze_class_name(args.class_name, args.scan_dir)
        if "error" in result:
            print(f"❌ {result['error']}")
            return 1
    
    # Print results
    print(f"\n📊 Violation Domain Analysis: {args.class_name}")
    print("=" * 70)
    
    print(f"\n📍 Locations Found: {result.get('total_locations', len(result.get('locations', [])))}")
    
    print("\n🌍 Domain Distribution:")
    for domain, count in result.get("domain_distribution", {}).items():
        print(f"  - {domain}: {count} location(s)")
    
    print(f"\n💡 Recommendation: {result.get('consolidation_recommendation', 'UNKNOWN')}")
    print(f"📝 Rationale: {result.get('rationale', 'N/A')}")
    
    strategy = result.get("strategy", {})
    if strategy:
        print(f"\n🎯 Strategy: {strategy.get('action', 'N/A').upper()}")
        if "approach" in strategy:
            print(f"   Approach: {strategy['approach']}")
        if "ssot" in strategy:
            print(f"   SSOT: {strategy['ssot']}")
    
    # Output to file if requested
    if args.output:
        import json
        args.output.write_text(json.dumps(result, indent=2, default=str))
        print(f"\n💾 Results saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    exit(main())

