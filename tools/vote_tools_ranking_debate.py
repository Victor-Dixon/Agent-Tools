#!/usr/bin/env python3
"""
Vote on Tools Ranking Debate - Agent-2
=======================================

Votes on the tools ranking debate with Agent-2's reasoning.

Author: Agent-2 (Architecture & Design Specialist)
Date: 2025-01-27
Priority: HIGH - Part of tools consolidation
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def vote_on_tools_ranking_debate():
    """Vote on tools ranking debate with Agent-2's reasoning."""
    
    debate_id = "debate_tools_ranking_20251124"
    agent_id = "Agent-2"
    
    # Agent-2's votes based on analysis
    votes = {
        "Best Overall Tool (Most Useful)": {
            "option": "Best Overall Tool (Most Useful)",
            "tool": "status_monitor_recovery_trigger",
            "reasoning": (
                "Based on comprehensive analysis of 234 tools, status_monitor_recovery_trigger "
                "scored highest (56 points) and is critical for system resilience. It enables "
                "autonomous recovery from agent stalls, integrates with Discord alerts, and "
                "provides standalone recovery capability independent of main orchestrator. "
                "This tool directly addresses system health and autonomy - core requirements."
            )
        },
        "Best Monitoring Tool": {
            "option": "Best Monitoring Tool",
            "tool": "agent_status_quick_check",
            "reasoning": (
                "agent_status_quick_check scored 55 points and provides fast agent progress "
                "verification. It includes devlog status checking, comprehensive status "
                "display, and is essential for coordination. Monitoring is critical for "
                "swarm coordination and this tool is the most comprehensive monitoring solution."
            )
        },
        "Best Automation Tool": {
            "option": "Best Automation Tool",
            "tool": "autonomous_task_engine",
            "reasoning": (
                "autonomous_task_engine scored 48 points and is described as 'The Masterpiece Tool "
                "for Swarm Intelligence'. It enables autonomous task execution, swarm coordination, "
                "and represents the core of our autonomous agent system. Automation is fundamental "
                "to our swarm architecture."
            )
        },
        "Best Analysis Tool": {
            "option": "Best Analysis Tool",
            "tool": "projectscanner_core",
            "reasoning": (
                "projectscanner_core scored 50 points and is part of the modular, battle-tested "
                "project scanner system. It provides comprehensive project analysis, V2 compliance "
                "checking, and is essential for understanding codebase structure. The modular "
                "architecture (projectscanner_*.py) is superior to monolithic alternatives."
            )
        },
        "Best Quality Tool": {
            "option": "Best Quality Tool",
            "tool": "v2_checker_cli",
            "reasoning": (
                "v2_checker_cli is the modular V2 compliance checker (part of v2_checker_*.py "
                "system). V2 compliance is fundamental to our architecture standards. The modular "
                "refactor is superior to the old monolith (v2_compliance_checker.py). Quality "
                "tools ensure code standards and maintainability."
            )
        },
        "Most Critical Tool": {
            "option": "Most Critical Tool",
            "tool": "status_monitor_recovery_trigger",
            "reasoning": (
                "status_monitor_recovery_trigger is the most critical tool because it enables "
                "system resilience and autonomous recovery. Without it, stalled agents would "
                "require manual intervention. It integrates with Discord alerts, provides "
                "standalone recovery, and is essential for maintaining swarm health. Critical "
                "for system autonomy and reliability."
            )
        }
    }
    
    # Try to vote using debate tools
    try:
        from tools_v2.categories.debate_tools import DebateVoteTool
        
        vote_tool = DebateVoteTool()
        
        print(f"🗳️ Voting on Tools Ranking Debate: {debate_id}")
        print(f"📋 Agent: {agent_id}")
        print("=" * 60)
        
        for category, vote_data in votes.items():
            print(f"\n📊 Voting: {category}")
            print(f"   Tool: {vote_data['tool']}")
            print(f"   Reasoning: {vote_data['reasoning'][:100]}...")
            
            result = vote_tool.execute({
                "debate_id": debate_id,
                "agent_id": agent_id,
                "option": vote_data["option"],
                "argument": vote_data["reasoning"]
            })
            
            if result.success:
                print(f"   ✅ Vote cast successfully")
            else:
                print(f"   ❌ Vote failed: {result.error_message}")
        
        print("\n" + "=" * 60)
        print("✅ All votes cast!")
        print("\n🐝 WE. ARE. SWARM. ⚡🔥")
        
    except ImportError as e:
        print(f"⚠️ Debate tools not available: {e}")
        print("📝 Creating vote record manually...")
        
        # Create vote record file
        vote_record = {
            "debate_id": debate_id,
            "agent_id": agent_id,
            "votes": votes,
            "timestamp": "2025-01-27T20:45:00.000000Z"
        }
        
        import json
        record_path = Path(f"agent_workspaces/Agent-2/TOOLS_RANKING_DEBATE_VOTES.json")
        record_path.parent.mkdir(parents=True, exist_ok=True)
        record_path.write_text(json.dumps(vote_record, indent=2), encoding="utf-8")
        
        print(f"✅ Vote record created: {record_path}")
        print("\n📋 Agent-2's Votes:")
        for category, vote_data in votes.items():
            print(f"\n{category}:")
            print(f"  Tool: {vote_data['tool']}")
            print(f"  Reasoning: {vote_data['reasoning']}")
        
        print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    vote_on_tools_ranking_debate()


