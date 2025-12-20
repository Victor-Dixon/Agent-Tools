#!/usr/bin/env python3
"""
Tools Consolidation Quick Analyzer
===================================

Fast analysis of tools directory for consolidation opportunities.
Uses file names and basic metadata only - no full file reads.

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-01-27
Priority: CRITICAL
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any


def quick_analyze_tool(tool_path: Path) -> Dict[str, Any]:
    """Quick analysis using only file name and size."""
    try:
        stat = tool_path.stat()
        name = tool_path.stem
        
        # Categorize by name patterns only (fast)
        name_lower = name.lower()
        categories = []
        
        if any(kw in name_lower for kw in ['status', 'check', 'monitor', 'health']):
            categories.append('monitoring')
        if any(kw in name_lower for kw in ['analyze', 'scan', 'audit', 'report', 'analysis']):
            categories.append('analysis')
        if any(kw in name_lower for kw in ['validate', 'verify', 'test']):
            categories.append('validation')
        if any(kw in name_lower for kw in ['captain', 'coordinate', 'gas', 'fuel']):
            categories.append('captain')
        if any(kw in name_lower for kw in ['consolidation', 'merge', 'consolidate']):
            categories.append('consolidation')
        if any(kw in name_lower for kw in ['queue', 'message', 'delivery']):
            categories.append('messaging')
        if any(kw in name_lower for kw in ['automate', 'auto', 'scheduler']):
            categories.append('automation')
        
        return {
            "name": name,
            "size": stat.st_size,
            "categories": categories if categories else ["other"],
        }
    except Exception as e:
        return {"name": tool_path.stem, "error": str(e)}


def find_name_duplicates(tools: List[Dict]) -> List[List[str]]:
    """Find tools with similar names."""
    duplicates = []
    name_groups = defaultdict(list)
    
    for tool in tools:
        if "error" in tool:
            continue
        name = tool["name"]
        # Remove common prefixes
        base = re.sub(r'^(agent_|captain_|check_|verify_|test_|validate_|quick_|auto_)', '', name.lower())
        name_groups[base].append(name)
    
    # Return groups with multiple tools
    for base, names in name_groups.items():
        if len(names) > 1:
            duplicates.append(names)
    
    return duplicates


def main():
    """Fast consolidation analysis."""
    print("🔍 Tools Consolidation Quick Analyzer")
    print("=" * 60)
    
    tools_dir = Path("tools")
    tools = []
    grouped = defaultdict(list)
    
    print("\n📋 Scanning tools (fast mode)...")
    for tool_file in tools_dir.glob("*.py"):
        if tool_file.name.startswith("__"):
            continue
        tool_data = quick_analyze_tool(tool_file)
        tools.append(tool_data)
        
        # Group by category
        for cat in tool_data.get("categories", ["other"]):
            grouped[cat].append(tool_data["name"])
    
    print(f"✅ Found {len(tools)} tools")
    
    # Category summary
    print("\n📊 Tools by Category:")
    for category in sorted(grouped.keys()):
        print(f"  {category}: {len(grouped[category])} tools")
    
    # Find duplicates
    print("\n🔍 Finding duplicates...")
    duplicates = find_name_duplicates(tools)
    print(f"✅ Found {len(duplicates)} duplicate groups")
    
    # Top consolidation opportunities
    print("\n🎯 TOP CONSOLIDATION OPPORTUNITIES:")
    
    # By category size
    large_categories = [(cat, len(tools)) for cat, tools in grouped.items() if len(tools) > 5]
    large_categories.sort(key=lambda x: -x[1])
    
    for cat, count in large_categories[:5]:
        print(f"  {cat.upper()}: {count} tools - Consider consolidation")
        print(f"    Examples: {', '.join(grouped[cat][:5])}")
    
    # Duplicates
    if duplicates:
        print(f"\n  DUPLICATES: {len(duplicates)} groups found")
        for dup_group in duplicates[:5]:
            print(f"    - {', '.join(dup_group)}")
    
    # Save quick report
    report = {
        "total_tools": len(tools),
        "categories": {cat: len(tools) for cat, tools in grouped.items()},
        "duplicate_groups": len(duplicates),
        "top_consolidation_opportunities": {
            cat: grouped[cat][:10] for cat, _ in large_categories[:5]
        },
        "duplicates": duplicates[:10],
    }
    
    report_path = Path("agent_workspaces/Agent-8/TOOLS_CONSOLIDATION_QUICK.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    
    print(f"\n✅ Quick report saved: {report_path}")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()


