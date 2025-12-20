#!/usr/bin/env python3
"""
Cast All Tools Ranking Debate Votes - Agent-2
=============================================

Casts votes on all 6 categories for the tools ranking debate.
Ensures all votes are properly recorded in the debate file.

Author: Agent-2 (Architecture & Design Specialist)
Date: 2025-01-27
Priority: HIGH - Captain directive
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def cast_all_votes():
    """Cast votes on all 6 categories for tools ranking debate."""
    
    debate_id = "debate_tools_ranking_20251124"
    agent_id = "Agent-2"
    
    debate_file = Path("debates") / f"{debate_id}.json"
    
    if not debate_file.exists():
        print(f"❌ Debate file not found: {debate_file}")
        return False
    
    # Load debate
    with open(debate_file, 'r') as f:
        debate_data = json.load(f)
    
    # Agent-2's votes with reasoning
    votes = [
        {
            "option": "Best Overall Tool (Most Useful)",
            "argument": (
                "Based on comprehensive analysis of 234 tools, status_monitor_recovery_trigger "
                "scored highest (56 points) and is critical for system resilience. It enables "
                "autonomous recovery from agent stalls, integrates with Discord alerts, and "
                "provides standalone recovery capability independent of main orchestrator. "
                "This tool directly addresses system health and autonomy - core requirements."
            ),
            "confidence": 9
        },
        {
            "option": "Best Monitoring Tool",
            "argument": (
                "agent_status_quick_check scored 55 points and provides fast agent progress "
                "verification. It includes devlog status checking, comprehensive status "
                "display, and is essential for coordination. Monitoring is critical for "
                "swarm coordination and this tool is the most comprehensive monitoring solution."
            ),
            "confidence": 8
        },
        {
            "option": "Best Automation Tool",
            "argument": (
                "autonomous_task_engine scored 48 points and is described as 'The Masterpiece Tool "
                "for Swarm Intelligence'. It enables autonomous task execution, swarm coordination, "
                "and represents the core of our autonomous agent system. Automation is fundamental "
                "to our swarm architecture."
            ),
            "confidence": 8
        },
        {
            "option": "Best Analysis Tool",
            "argument": (
                "projectscanner_core scored 50 points and is part of the modular, battle-tested "
                "project scanner system. It provides comprehensive project analysis, V2 compliance "
                "checking, and is essential for understanding codebase structure. The modular "
                "architecture (projectscanner_*.py) is superior to monolithic alternatives."
            ),
            "confidence": 9
        },
        {
            "option": "Best Quality Tool",
            "argument": (
                "v2_checker_cli is the modular V2 compliance checker (part of v2_checker_*.py "
                "system). V2 compliance is fundamental to our architecture standards. The modular "
                "refactor is superior to the old monolith (v2_compliance_checker.py). Quality "
                "tools ensure code standards and maintainability."
            ),
            "confidence": 9
        },
        {
            "option": "Most Critical Tool",
            "argument": (
                "status_monitor_recovery_trigger is the most critical tool because it enables "
                "system resilience and autonomous recovery. Without it, stalled agents would "
                "require manual intervention. It integrates with Discord alerts, provides "
                "standalone recovery, and is essential for maintaining swarm health. Critical "
                "for system autonomy and reliability."
            ),
            "confidence": 10
        }
    ]
    
    print(f"🗳️ Casting All Votes for Tools Ranking Debate")
    print(f"📋 Debate ID: {debate_id}")
    print(f"🤖 Agent: {agent_id}")
    print("=" * 60)
    
    # Initialize votes and arguments if needed
    if "votes" not in debate_data:
        debate_data["votes"] = {}
    if "arguments" not in debate_data:
        debate_data["arguments"] = []
    
    # Cast each vote
    votes_cast = 0
    for vote in votes:
        option = vote["option"]
        argument = vote["argument"]
        confidence = vote.get("confidence", 5)
        
        print(f"\n📊 Voting: {option}")
        
        # Record vote
        vote_data = {
            "option": option,
            "timestamp": datetime.now().isoformat(),
            "confidence": confidence,
            "argument": argument,
        }
        
        # Store vote (using option as key for multiple votes per agent)
        vote_key = f"{agent_id}_{option.replace(' ', '_').replace('(', '').replace(')', '')}"
        debate_data["votes"][vote_key] = vote_data
        
        # Add to arguments
        debate_data["arguments"].append({
            "agent_id": agent_id,
            "option": option,
            "argument": argument,
            "confidence": confidence,
            "timestamp": vote_data["timestamp"],
        })
        
        votes_cast += 1
        print(f"   ✅ Vote cast (Confidence: {confidence}/10)")
    
    # Save updated debate
    debate_file.write_text(json.dumps(debate_data, indent=2), encoding="utf-8")
    
    print("\n" + "=" * 60)
    print(f"✅ All {votes_cast} votes cast successfully!")
    print(f"📝 Debate file updated: {debate_file}")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")
    
    return True


if __name__ == "__main__":
    cast_all_votes()


