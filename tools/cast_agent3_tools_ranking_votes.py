#!/usr/bin/env python3
"""
Cast All Tools Ranking Debate Votes - Agent-3
=============================================

Casts votes on all 6 categories for the tools ranking debate.
Ensures all votes are properly recorded in the debate file.

Author: Agent-3 (Infrastructure & DevOps Specialist)
Date: 2025-11-23
Priority: URGENT - Captain directive
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
    agent_id = "Agent-3"
    
    debate_file = Path("debates") / f"{debate_id}.json"
    
    if not debate_file.exists():
        print(f"❌ Debate file not found: {debate_file}")
        return False
    
    # Load debate
    with open(debate_file, 'r') as f:
        debate_data = json.load(f)
    
    # Agent-3's votes with reasoning (Infrastructure & DevOps perspective)
    votes = [
        {
            "option": "Best Overall Tool (Most Useful)",
            "argument": (
                "Mission Control is the comprehensive workflow orchestration tool that runs all 5 workflow steps. "
                "From an infrastructure perspective, it provides end-to-end automation, coordinates agent activities, "
                "and ensures systematic execution. It's the masterpiece tool that enables autonomous mission generation "
                "and execution - critical for swarm operations."
            ),
            "confidence": 10
        },
        {
            "option": "Best Monitoring Tool",
            "argument": (
                "Workspace Health Checker provides comprehensive monitoring of agent workspaces, status.json files, "
                "inbox status, and devlog tracking. As Infrastructure & DevOps specialist, monitoring is critical for "
                "system health. This tool provides the most comprehensive monitoring solution for agent workspace health, "
                "which is foundational for infrastructure operations."
            ),
            "confidence": 9
        },
        {
            "option": "Best Automation Tool",
            "argument": (
                "Swarm Autonomous Orchestrator is the core automation engine for swarm coordination. It enables "
                "autonomous task execution, agent coordination, and system-wide automation. From an infrastructure "
                "perspective, automation is fundamental to DevOps operations, and this tool provides the highest level "
                "of automation capability for the swarm."
            ),
            "confidence": 10
        },
        {
            "option": "Best Analysis Tool",
            "argument": (
                "Repo Overlap Analyzer is essential for infrastructure consolidation analysis. I've used this tool "
                "extensively for identifying repository overlaps, consolidation opportunities, and infrastructure patterns. "
                "It provides comprehensive analysis of repository relationships, which is critical for infrastructure "
                "consolidation work."
            ),
            "confidence": 9
        },
        {
            "option": "Best Quality Tool",
            "argument": (
                "V2 Compliance Checker is fundamental to maintaining code quality and architectural standards. "
                "As Infrastructure specialist, ensuring V2 compliance across all tools and modules is critical. "
                "This tool provides comprehensive compliance checking, which is essential for maintaining code quality "
                "and architectural integrity."
            ),
            "confidence": 9
        },
        {
            "option": "Most Critical Tool",
            "argument": (
                "Swarm Autonomous Orchestrator is the most critical tool because it enables the entire swarm to function "
                "autonomously. Without orchestration, agents cannot coordinate, tasks cannot be executed systematically, "
                "and the swarm cannot operate effectively. From an infrastructure perspective, orchestration is the "
                "foundation of all swarm operations - it's the critical infrastructure that enables everything else."
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
        vote_key = f"{agent_id}_{option.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')}"
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


