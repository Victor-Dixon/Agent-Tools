#!/usr/bin/env python3
"""
Tools Consolidation & Ranking - Complete Analysis
==================================================

Comprehensive tool to:
1. Identify duplicate/similar tools
2. Rank tools by utility and importance
3. Generate consolidation plan
4. Create final ranking report

Author: Agent-2 (Architecture & Design Specialist)
Date: 2025-01-27
V2 Compliance: <400 lines
Priority: CRITICAL - Blocking Phase 1
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def get_all_tools() -> List[Dict[str, Any]]:
    """Get all tools in tools directory with metadata."""
    tools_dir = Path("tools")
    tools = []
    
    for tool_file in sorted(tools_dir.glob("*.py")):
        if tool_file.name.startswith("__"):
            continue
        
        try:
            content = tool_file.read_text(encoding="utf-8")
            lines = len(content.splitlines())
            
            # Extract description from docstring
            description = ""
            if '"""' in content:
                doc_start = content.find('"""')
                doc_end = content.find('"""', doc_start + 3)
                if doc_end > doc_start:
                    description = content[doc_start + 3:doc_end].strip().split('\n')[0]
            
            # Extract key functions/classes
            functions = re.findall(r'def\s+(\w+)', content)
            classes = re.findall(r'class\s+(\w+)', content)
            
            # Determine category from name/path
            category = _categorize_tool(tool_file.name, description)
            
            tools.append({
                "name": tool_file.stem,
                "path": str(tool_file),
                "lines": lines,
                "description": description[:200] if description else "No description",
                "functions": functions[:5],  # First 5 functions
                "classes": classes[:3],  # First 3 classes
                "category": category,
            })
        except Exception as e:
            print(f"⚠️ Error reading {tool_file}: {e}")
    
    return tools


def _categorize_tool(name: str, description: str) -> str:
    """Categorize tool based on name and description."""
    name_lower = name.lower()
    desc_lower = description.lower()
    
    # Captain tools
    if "captain" in name_lower:
        return "captain"
    
    # Agent tools
    if "agent" in name_lower:
        return "agent"
    
    # Analysis tools
    if any(x in name_lower for x in ["analyze", "analysis", "scanner", "audit"]):
        return "analysis"
    
    # Monitoring tools
    if any(x in name_lower for x in ["monitor", "status", "check", "health"]):
        return "monitoring"
    
    # Automation tools
    if any(x in name_lower for x in ["auto", "automation", "automate"]):
        return "automation"
    
    # Consolidation tools
    if any(x in name_lower for x in ["consolidat", "merge", "overlap"]):
        return "consolidation"
    
    # Quality tools
    if any(x in name_lower for x in ["v2", "compliance", "quality", "validator"]):
        return "quality"
    
    # Coordination tools
    if any(x in name_lower for x in ["coordination", "message", "discord"]):
        return "coordination"
    
    # Task tools
    if any(x in name_lower for x in ["task", "mission", "workflow"]):
        return "task"
    
    return "other"


def find_duplicates(tools: List[Dict[str, Any]]) -> List[Tuple[str, List[str]]]:
    """Find duplicate/similar tools."""
    duplicates = []
    tool_groups = defaultdict(list)
    
    # Known duplicates from consolidation strategy
    known_duplicates = {
        "linecount": ["quick_linecount", "quick_line_counter"],
        "projectscanner": ["projectscanner", "projectscanner_core", "projectscanner_language_analyzer", 
                          "projectscanner_modular_reports", "projectscanner_workers", "projectscanner_legacy_reports",
                          "comprehensive_project_analyzer"],
        "v2_compliance": ["v2_compliance_checker", "v2_compliance_batch_checker", "v2_checker_cli"],
        "toolbelt": ["toolbelt", "agent_toolbelt"],
        "toolbelt_help": ["toolbelt_help", "captain_toolbelt_help"],
        "refactor": ["refactor_analyzer", "refactor_validator"],
    }
    
    # Add known duplicates
    for base_name, tool_names in known_duplicates.items():
        # Filter to only tools that actually exist
        existing_tools = [t for t in tool_names if any(tool["name"] == t for tool in tools)]
        if len(existing_tools) > 1:
            duplicates.append((base_name, existing_tools))
    
    # Group by similar names (more conservative)
    for tool in tools:
        name = tool["name"].lower()
        # Remove common prefixes/suffixes for grouping
        base_name = re.sub(r'^(auto_|quick_|captain_|agent_)', '', name)
        base_name = re.sub(r'(_tool|_cli|_checker|_validator|_analyzer|_reporter)$', '', base_name)
        
        # Skip if already in known duplicates
        if not any(base_name in dup[0] for dup in duplicates):
            tool_groups[base_name].append(tool["name"])
    
    # Find groups with multiple tools (only exact matches)
    for base_name, tool_names in tool_groups.items():
        if len(tool_names) > 1 and len(base_name) > 5:  # Only meaningful base names
            # Check if they're actually similar (not just coincidental)
            if all(tn.lower().startswith(base_name[:10]) or base_name[:10] in tn.lower() for tn in tool_names):
                duplicates.append((base_name, tool_names))
    
    return duplicates


def rank_tools(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Rank tools by utility and importance."""
    ranked = []
    
    for tool in tools:
        score = 0
        
        # Size scoring (smaller is better for maintainability)
        if tool["lines"] < 200:
            score += 10
        elif tool["lines"] < 400:
            score += 5
        else:
            score += 1
        
        # Category scoring
        category_scores = {
            "captain": 20,
            "agent": 15,
            "monitoring": 15,
            "automation": 12,
            "analysis": 10,
            "quality": 10,
            "consolidation": 8,
            "coordination": 8,
            "task": 8,
            "other": 5,
        }
        score += category_scores.get(tool["category"], 5)
        
        # Description scoring (has description = better)
        if tool["description"] and tool["description"] != "No description":
            score += 5
        
        # Functionality scoring (has functions = better)
        if tool["functions"]:
            score += len(tool["functions"]) * 2
        
        # Critical tool names
        critical_tools = [
            "agent_status_quick_check",
            "agent_mission_controller",
            "autonomous_task_engine",
            "projectscanner",
            "v2_compliance_checker",
            "status_monitor_recovery_trigger",
        ]
        if any(ct in tool["name"].lower() for ct in critical_tools):
            score += 20
        
        tool["score"] = score
        ranked.append(tool)
    
    # Sort by score (descending)
    ranked.sort(key=lambda x: x["score"], reverse=True)
    
    return ranked


def generate_consolidation_plan(duplicates: List[Tuple[str, List[str]]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate consolidation plan for duplicates."""
    plan = {
        "duplicates": [],
        "recommendations": [],
    }
    
    tool_dict = {t["name"]: t for t in tools}
    
    for base_name, tool_names in duplicates:
        if len(tool_names) <= 1:
            continue
        
        # Get tool details
        tool_details = [tool_dict.get(name, {}) for name in tool_names]
        
        # Determine which to keep (prefer smaller, better described, V2 compliant)
        keep_candidate = None
        keep_score = -1
        
        # Known consolidation rules from architectural decisions
        consolidation_rules = {
            "projectscanner": {
                "keep_patterns": ["projectscanner_core", "projectscanner_language", "projectscanner_modular", "projectscanner_workers"],
                "deprecate_patterns": ["comprehensive_project_analyzer"],
            },
            "v2_compliance": {
                "keep_patterns": ["v2_checker_cli", "v2_checker_"],
                "deprecate_patterns": ["v2_compliance_checker", "v2_compliance_batch_checker"],
            },
        }
        
        # Check if this group matches a known rule
        rule_match = None
        for rule_name, rule in consolidation_rules.items():
            if rule_name in base_name.lower():
                rule_match = rule
                break
        
        for tool in tool_details:
            if not tool:
                continue
            score = 0
            
            # Apply consolidation rules
            if rule_match:
                tool_name = tool.get("name", "").lower()
                if any(pattern in tool_name for pattern in rule_match.get("keep_patterns", [])):
                    score += 50  # High priority for rule matches
                if any(pattern in tool_name for pattern in rule_match.get("deprecate_patterns", [])):
                    score -= 50  # Low priority for deprecate matches
            
            # General scoring
            if tool.get("lines", 0) < 300:
                score += 10
            if tool.get("description") and tool["description"] != "No description":
                score += 5
            if "v2" in tool.get("name", "").lower() and "checker" in tool.get("name", "").lower():
                score += 10
            if "projectscanner" in tool.get("name", "").lower() and "core" in tool.get("name", "").lower():
                score += 15  # Prefer modular projectscanner
            
            if score > keep_score:
                keep_score = score
                keep_candidate = tool
        
        if keep_candidate:
            plan["duplicates"].append({
                "base_name": base_name,
                "tools": tool_names,
                "keep": keep_candidate["name"],
                "deprecate": [name for name in tool_names if name != keep_candidate["name"]],
                "reason": f"Keep {keep_candidate['name']} (better description, smaller size, or V2 compliant)",
            })
    
    return plan


def generate_final_report(tools: List[Dict[str, Any]], duplicates: List[Tuple[str, List[str]]], ranked: List[Dict[str, Any]], plan: Dict[str, Any]) -> str:
    """Generate final consolidation and ranking report."""
    report_path = Path("agent_workspaces/Agent-2/TOOLS_CONSOLIDATION_AND_RANKING_COMPLETE.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    report = f"""# 🛠️ Tools Consolidation & Ranking - COMPLETE REPORT

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Agent**: Agent-2 (Architecture & Design Specialist)  
**Priority**: 🚨 **CRITICAL - BLOCKING PHASE 1**  
**Status**: ✅ **COMPLETE**

---

## 📊 **EXECUTIVE SUMMARY**

**Total Tools Analyzed**: {len(tools)}  
**Duplicate Groups Found**: {len(duplicates)}  
**Tools Ranked**: {len(ranked)}  
**Consolidation Opportunities**: {len(plan.get('duplicates', []))}

---

## 🏆 **TOP 20 RANKED TOOLS**

"""
    
    for i, tool in enumerate(ranked[:20], 1):
        report += f"""
### **{i}. {tool['name']}** (Score: {tool['score']})
- **Category**: {tool['category'].title()}
- **Lines**: {tool['lines']}
- **Description**: {tool['description']}
- **Path**: `{tool['path']}`
"""
    
    report += f"""

---

## 🔄 **DUPLICATE TOOLS IDENTIFIED**

"""
    
    for dup in plan.get("duplicates", [])[:20]:  # Show top 20
        report += f"""
### **{dup['base_name']}**
- **Keep**: `{dup['keep']}`
- **Deprecate**: {', '.join([f'`{d}`' for d in dup['deprecate']])}
- **Reason**: {dup['reason']}
"""
    
    report += f"""

---

## 📋 **CONSOLIDATION RECOMMENDATIONS**

### **Priority 1: Critical Duplicates** (Immediate Action)

"""
    
    critical_dups = [d for d in plan.get("duplicates", []) if len(d["tools"]) >= 3]
    for dup in critical_dups[:10]:
        report += f"""
1. **{dup['base_name']}** - {len(dup['tools'])} tools
   - Keep: `{dup['keep']}`
   - Deprecate: {len(dup['deprecate'])} tools
"""
    
    report += f"""

### **Priority 2: High-Value Consolidations**

"""
    
    high_value = [d for d in plan.get("duplicates", []) if 2 <= len(d["tools"]) < 3]
    for dup in high_value[:10]:
        report += f"""
1. **{dup['base_name']}** - {len(dup['tools'])} tools
   - Keep: `{dup['keep']}`
   - Deprecate: {', '.join([f'`{d}`' for d in dup['deprecate']])}
"""
    
    report += f"""

---

## 🎯 **CATEGORY RANKINGS**

"""
    
    # Group by category
    by_category = defaultdict(list)
    for tool in ranked:
        by_category[tool["category"]].append(tool)
    
    for category, cat_tools in sorted(by_category.items()):
        report += f"""
### **{category.title()}** ({len(cat_tools)} tools)
"""
        for tool in cat_tools[:5]:
            report += f"- **{tool['name']}** (Score: {tool['score']}) - {tool['description']}\n"
    
    report += f"""

---

## ✅ **CONSOLIDATION ACTIONS**

### **Immediate Actions**:
1. Review duplicate groups
2. Archive/deprecate redundant tools
3. Update toolbelt registry
4. Update documentation

### **Next Steps**:
1. Execute consolidation plan
2. Update tool references
3. Test consolidated tools
4. Document changes

---

## 🐝 **WE. ARE. SWARM.**

**Status**: ✅ **TOOLS CONSOLIDATION & RANKING COMPLETE**

**Agent-2 (Architecture & Design Specialist)**  
**Tools Consolidation & Ranking - 2025-01-27**

---

*Tools consolidation and ranking complete. Ready for Phase 1 execution!*
"""
    
    report_path.write_text(report, encoding="utf-8")
    return str(report_path)


def main():
    """Main execution."""
    print("🛠️ Tools Consolidation & Ranking - COMPLETE ANALYSIS")
    print("=" * 60)
    
    # Get all tools
    print("\n📋 Scanning tools directory...")
    tools = get_all_tools()
    print(f"✅ Found {len(tools)} tools")
    
    # Find duplicates
    print("\n🔍 Finding duplicate tools...")
    duplicates = find_duplicates(tools)
    print(f"✅ Found {len(duplicates)} duplicate groups")
    
    # Rank tools
    print("\n🏆 Ranking tools...")
    ranked = rank_tools(tools)
    print(f"✅ Ranked {len(ranked)} tools")
    
    # Generate consolidation plan
    print("\n📋 Generating consolidation plan...")
    plan = generate_consolidation_plan(duplicates, tools)
    print(f"✅ Generated plan with {len(plan['duplicates'])} consolidation opportunities")
    
    # Generate final report
    print("\n📝 Generating final report...")
    report_path = generate_final_report(tools, duplicates, ranked, plan)
    print(f"✅ Report created: {report_path}")
    
    # Save JSON data
    json_path = Path("agent_workspaces/Agent-2/TOOLS_CONSOLIDATION_AND_RANKING_DATA.json")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_data = {
        "tools": tools,
        "ranked": ranked,
        "duplicates": duplicates,
        "plan": plan,
        "timestamp": datetime.now().isoformat(),
    }
    json_path.write_text(json.dumps(json_data, indent=2), encoding="utf-8")
    print(f"✅ Data saved: {json_path}")
    
    print("\n📊 SUMMARY:")
    print(f"   Total Tools: {len(tools)}")
    print(f"   Duplicate Groups: {len(duplicates)}")
    print(f"   Consolidation Opportunities: {len(plan['duplicates'])}")
    print(f"   Top Tool: {ranked[0]['name']} (Score: {ranked[0]['score']})")
    
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()

