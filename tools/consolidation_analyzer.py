#!/usr/bin/env python3
"""
Consolidation Analyzer - Unified Tool Consolidation Analysis
============================================================

Consolidates general tool consolidation analysis, QA validation analysis,
and comprehensive QA tool analysis into a single unified tool.

Replaces:
- tools_consolidation_analyzer.py
- analyze_qa_validation_tools.py
- analyze_all_qa_tools.py

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-03
V2 Compliant: Yes (<300 lines)
SSOT Domain: analytics

<!-- SSOT Domain: analytics -->
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

# SSOT Domain: analytics


class ConsolidationAnalyzer:
    """Unified consolidation analyzer for tools and QA analysis."""

    def __init__(self, tools_dir: Path = None, candidates_file: Path = None):
        """Initialize analyzer."""
        self.tools_dir = tools_dir or Path("tools")
        self.candidates_file = candidates_file
        self.qa_keywords = ['valid', 'verify', 'check', 'test', 'qa', 'coverage', 'quality', 'ssot', 'import', 'chain', 'config', 'tracker', 'analyzer', 'prioritizer', 'gap']

    def analyze_tool_file(self, tool_path: Path) -> Dict[str, Any]:
        """Analyze a single tool file."""
        try:
            content = tool_path.read_text(encoding="utf-8")
            lines = len(content.splitlines())
            description = ""
            if '"""' in content:
                doc_start = content.find('"""')
                doc_end = content.find('"""', doc_start + 3)
                if doc_end > doc_start:
                    description = content[doc_start + 3:doc_end].strip().split('\n')[0]
            functions = re.findall(r'def\s+(\w+)', content)
            classes = re.findall(r'class\s+(\w+)', content)
            content_lower = content.lower()
            categories = []
            if any(kw in content_lower for kw in ['status', 'check', 'monitor', 'health']): categories.append('monitoring')
            if any(kw in content_lower for kw in ['analyze', 'scan', 'audit', 'report']): categories.append('analysis')
            if any(kw in content_lower for kw in ['validate', 'verify', 'check', 'test']): categories.append('validation')
            if any(kw in content_lower for kw in ['consolidation', 'merge', 'consolidate']): categories.append('consolidation')
            return {"name": tool_path.stem, "path": str(tool_path), "lines": lines, "description": description[:200] if description else "No description", "categories": categories if categories else ["other"], "functions": functions[:5], "classes": classes}
        except Exception as e:
            return {"name": tool_path.stem, "path": str(tool_path), "error": str(e)}

    def is_qa_tool(self, tool: Dict[str, Any]) -> bool:
        """Check if tool is QA/validation/testing related."""
        name = tool.get('name', '').lower()
        path = tool.get('path', '').lower()
        return any(kw in name or kw in path for kw in self.qa_keywords) or ('test' in name and any(x in name for x in ['tracker', 'analyzer', 'prioritizer', 'coverage', 'gap']))

    def categorize_qa_tools(self, tools: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize QA tools by pattern."""
        categories = defaultdict(list)
        for tool in tools:
            name = tool.get('name', '').lower()
            path = tool.get('path', '').lower()
            if 'ssot' in name and 'valid' in name: categories['ssot_validation'].append(tool)
            elif 'import' in name and ('valid' in name or 'chain' in name): categories['import_validation'].append(tool)
            elif 'config' in name and 'valid' in name: categories['config_validation'].append(tool)
            elif 'coverage' in name or ('test' in name and 'coverage' in path): categories['test_coverage'].append(tool)
            elif 'test' in name and any(x in name for x in ['tracker', 'analyzer', 'prioritizer', 'gap']): categories['test_infrastructure'].append(tool)
            elif 'quality' in name or 'qa' in name: categories['quality_standards'].append(tool)
            elif 'valid' in name or 'verify' in name: categories['general_validation'].append(tool)
            elif 'check' in name or 'health' in name: categories['health_checks'].append(tool)
            else: categories['other_qa'].append(tool)
        return dict(categories)

    def group_tools_by_category(self, tools: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group tools by category."""
        grouped = defaultdict(list)
        for tool in tools:
            if "error" in tool: grouped["errors"].append(tool)
            elif "categories" in tool:
                for cat in tool["categories"]: grouped[cat].append(tool)
            else: grouped["other"].append(tool)
        return dict(grouped)

    def identify_duplicates(self, tools: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Identify potential duplicate tools."""
        duplicates = []
        name_groups = defaultdict(list)
        for tool in tools:
            if "error" in tool: continue
            normalized = re.sub(r'^(agent_|captain_|check_|verify_|test_|validate_)', '', tool["name"].lower())
            name_groups[normalized].append(tool)
        for normalized, group in name_groups.items():
            if len(group) > 1: duplicates.append(group)
        desc_groups = defaultdict(list)
        for tool in tools:
            if "error" in tool or not tool.get("description"): continue
            desc_key = tool["description"].lower()[:50]
            desc_groups[desc_key].append(tool)
        for desc_key, group in desc_groups.items():
            if len(group) > 1 and group not in duplicates:
                if all(t.get("description", "")[:50].lower() == desc_key for t in group): duplicates.append(group)
        return duplicates

    def analyze_tools_directory(self) -> Dict[str, Any]:
        """Analyze tools directory directly."""
        tools = []
        for tool_file in self.tools_dir.glob("*.py"):
            if tool_file.name.startswith("__"): continue
            tools.append(self.analyze_tool_file(tool_file))
        grouped = self.group_tools_by_category(tools)
        duplicates = self.identify_duplicates(tools)
        return {"tools": tools, "grouped": grouped, "duplicates": duplicates, "total": len(tools)}

    def analyze_from_json(self, filter_qa: bool = False) -> Dict[str, Any]:
        """Analyze tools from consolidation candidates JSON."""
        if not self.candidates_file or not self.candidates_file.exists():
            return {"error": "Candidates file not found"}
        with open(self.candidates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        all_tools = []
        for category in ['monitoring', 'validation', 'analysis']:
            all_tools.extend(data.get(category, []))
        if filter_qa:
            qa_tools = [t for t in all_tools if self.is_qa_tool(t)]
            categories = self.categorize_qa_tools(qa_tools)
            return {"tools": qa_tools, "categories": categories, "total": len(qa_tools), "qa_specific": True}
        return {"tools": all_tools, "total": len(all_tools), "qa_specific": False}

    def generate_consolidation_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate consolidation plan from analysis."""
        plan = {"recommendations": [], "core_tools": []}
        if analysis.get("qa_specific"):
            categories = analysis.get("categories", {})
            for cat, tools in categories.items():
                if len(tools) > 1:
                    plan["core_tools"].append({"category": cat, "consolidates": len(tools), "tools": [t['name'] for t in tools[:5]]})
        else:
            grouped = analysis.get("grouped", {})
            duplicates = analysis.get("duplicates", [])
            for category, tools in grouped.items():
                if len(tools) > 5:
                    plan["recommendations"].append({"category": category, "action": "consolidate", "tools_count": len(tools)})
            for dup_group in duplicates:
                if len(dup_group) > 1:
                    plan["recommendations"].append({"action": "merge", "tools": [t['name'] for t in dup_group]})
        return plan

    def analyze(self, mode: str = "directory", filter_qa: bool = False) -> Dict[str, Any]:
        """Run comprehensive consolidation analysis."""
        if mode == "directory":
            analysis = self.analyze_tools_directory()
        else:
            analysis = self.analyze_from_json(filter_qa=filter_qa)
        plan = self.generate_consolidation_plan(analysis)
        return {"analysis": analysis, "plan": plan}

    def save_results(self, results: Dict[str, Any], output_path: Path):
        """Save analysis results."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"✅ Results saved to: {output_path}")


def main():
    """Main entry point."""
    import argparse
    parser = argparse.ArgumentParser(description="Consolidation Analyzer")
    parser.add_argument("--mode", choices=["directory", "json"], default="directory", help="Analysis mode")
    parser.add_argument("--tools-dir", type=Path, default=Path("tools"), help="Tools directory")
    parser.add_argument("--candidates", type=Path, help="Consolidation candidates JSON file")
    parser.add_argument("--filter-qa", action="store_true", help="Filter QA tools only")
    parser.add_argument("--output", type=Path, default=Path("agent_workspaces/Agent-5/consolidation_analysis.json"), help="Output file")
    args = parser.parse_args()
    
    analyzer = ConsolidationAnalyzer(tools_dir=args.tools_dir, candidates_file=args.candidates)
    results = analyzer.analyze(mode=args.mode, filter_qa=args.filter_qa)
    analyzer.save_results(results, args.output)
    
    print(f"\n📊 Analysis Summary:")
    print(f"  Total Tools: {results['analysis'].get('total', 0)}")
    if results['analysis'].get('qa_specific'):
        print(f"  QA Categories: {len(results['analysis'].get('categories', {}))}")
    print(f"  Recommendations: {len(results['plan'].get('recommendations', []))}")
    print(f"  Core Tools: {len(results['plan'].get('core_tools', []))}")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()


