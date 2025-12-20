#!/usr/bin/env python3
"""
Tools Ranking Debate - Rank Consolidated Tools Directory
==========================================================

Uses debate system to rank tools in consolidated tools directory
(now that v2_tools doesn't exist) and identify best tool on toolbelt.

Author: Agent-2 (Architecture & Design Specialist)
Date: 2025-01-27
V2 Compliance: <300 lines
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import debate tools
try:
    import sys
    from pathlib import Path
    # Add tools_v2 to path
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    from tools_v2.categories.debate_tools import DebateStartTool, DebateVoteTool, DebateStatusTool
    DEBATE_AVAILABLE = True
except ImportError as e:
    DEBATE_AVAILABLE = False
    print(f"⚠️ Debate tools not available - using fallback ranking: {e}")


def get_all_tools() -> list[dict]:
    """Get list of all tools in consolidated tools directory."""
    tools_dir = Path("tools")
    tools = []
    
    # Get all Python files in tools directory
    for tool_file in tools_dir.glob("*.py"):
        if tool_file.name.startswith("__"):
            continue
        
        # Read file to get basic info
        try:
            content = tool_file.read_text(encoding="utf-8")
            lines = len(content.splitlines())
            
            # Try to extract docstring or description
            description = ""
            if '"""' in content:
                doc_start = content.find('"""')
                doc_end = content.find('"""', doc_start + 3)
                if doc_end > doc_start:
                    description = content[doc_start + 3:doc_end].strip().split('\n')[0]
            
            tools.append({
                "name": tool_file.stem,
                "path": str(tool_file),
                "lines": lines,
                "description": description[:100] if description else "No description",
            })
        except Exception as e:
            print(f"⚠️ Error reading {tool_file}: {e}")
    
    return sorted(tools, key=lambda x: x["name"])


def start_tools_ranking_debate(tools: list[dict]) -> str:
    """Start debate to rank tools."""
    if not DEBATE_AVAILABLE:
        print("⚠️ Debate system not available - using simple ranking")
        return None
    
    # Create debate options based on tool categories
    options = [
        "Best Overall Tool (Most Useful)",
        "Best Monitoring Tool",
        "Best Automation Tool",
        "Best Analysis Tool",
        "Best Quality Tool",
        "Most Critical Tool",
    ]
    
    debate_tool = DebateStartTool()
    result = debate_tool.execute({
        "topic": "Rank Tools in Consolidated Tools Directory - Which is the Best Tool on the Toolbelt?",
        "description": f"Ranking {len(tools)} tools in consolidated tools directory. Tools to evaluate: {', '.join([t['name'] for t in tools[:20]])}...",
        "options": options,
        "deadline": (datetime.now() + timedelta(hours=24)).isoformat(),
    })
    
    if result.success:
        debate_id = result.output["debate_id"]
        print(f"✅ Debate started: {debate_id}")
        print(f"📋 Topic: {result.output['topic']}")
        print(f"🗳️ Options: {', '.join(options)}")
        return debate_id
    else:
        print(f"❌ Failed to start debate: {result.output}")
        return None


def create_tools_ranking_report(tools: list[dict]) -> str:
    """Create ranking report for tools."""
    report_path = Path("agent_workspaces/Agent-2/TOOLS_RANKING_DEBATE_REPORT.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    report = f"""# 🛠️ Tools Ranking Debate Report

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Agent**: Agent-2 (Architecture & Design Specialist)  
**Total Tools**: {len(tools)}

---

## 📊 Tools Inventory

### **Tools in Consolidated Directory**:

"""
    
    # Group by size
    small_tools = [t for t in tools if t["lines"] < 200]
    medium_tools = [t for t in tools if 200 <= t["lines"] < 400]
    large_tools = [t for t in tools if t["lines"] >= 400]
    
    report += f"""
**By Size**:
- Small (<200 lines): {len(small_tools)}
- Medium (200-400 lines): {len(medium_tools)}
- Large (≥400 lines): {len(large_tools)}

---

## 🗳️ Debate Status

**Debate Topic**: Rank Tools in Consolidated Tools Directory - Which is the Best Tool on the Toolbelt?

**Options**:
1. Best Overall Tool (Most Useful)
2. Best Monitoring Tool
3. Best Automation Tool
4. Best Analysis Tool
5. Best Quality Tool
6. Most Critical Tool

---

## 📋 Tools List

"""
    
    for i, tool in enumerate(tools[:50], 1):  # Show first 50
        report += f"{i}. **{tool['name']}** ({tool['lines']} lines)\n"
        report += f"   - {tool['description']}\n\n"
    
    if len(tools) > 50:
        report += f"\n*... and {len(tools) - 50} more tools*\n"
    
    report += """
---

## 🎯 Next Steps

1. Agents vote on best tool categories
2. Aggregate votes to determine rankings
3. Identify best overall tool on toolbelt
4. Document findings

---

*Report generated by Agent-2 - Tools Ranking Debate System*
"""
    
    report_path.write_text(report, encoding="utf-8")
    return str(report_path)


def main():
    """Main execution."""
    print("🛠️ Tools Ranking Debate - Agent-2")
    print("=" * 60)
    
    # Get all tools
    print("\n📋 Scanning tools directory...")
    tools = get_all_tools()
    print(f"✅ Found {len(tools)} tools")
    
    # Create ranking report
    print("\n📝 Creating ranking report...")
    report_path = create_tools_ranking_report(tools)
    print(f"✅ Report created: {report_path}")
    
    # Start debate
    print("\n🗳️ Starting debate...")
    debate_id = start_tools_ranking_debate(tools)
    
    if debate_id:
        print(f"\n✅ Debate started successfully!")
        print(f"📋 Debate ID: {debate_id}")
        print(f"\n📝 Next steps:")
        print(f"   1. Agents vote using: python tools/agent_toolbelt.py debate.vote --debate-id {debate_id}")
        print(f"   2. Check status: python tools/agent_toolbelt.py debate.status --debate-id {debate_id}")
        print(f"   3. Review report: {report_path}")
    else:
        print("\n⚠️ Debate system not available - using fallback")
        print(f"📝 Review report: {report_path}")
    
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()


