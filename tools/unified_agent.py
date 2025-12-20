#!/usr/bin/env python3
"""
Unified Agent - Consolidated Agent Operations Tool
==================================================

<!-- SSOT Domain: coordination -->

Consolidates all agent operations into a single unified tool.
Replaces 12+ individual agent tools with modular agent system.

Agent Categories:
- orient - Agent orientation
- tasks - Task management
- status - Status monitoring
- lifecycle - Lifecycle management
- onboard - Onboarding operations

Author: Agent-5 (Business Intelligence Specialist) - Executing Agent-8's Consolidation Plan
Date: 2025-12-06
V2 Compliant: Yes
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedAgent:
    """Unified agent operations system consolidating all agent capabilities."""
    
    def __init__(self):
        """Initialize unified agent."""
        self.project_root = project_root
        self.agent_workspaces = project_root / "agent_workspaces"
    
    def orient_agent(self, agent_id: str = None) -> Dict[str, Any]:
        """Orient an agent to their workspace and current state."""
        try:
            from tools.agent_orient import quick_start, list_systems, list_tools
            
            # Agent orient doesn't take agent_id, it's a general tool
            return {
                "category": "orient",
                "agent": agent_id or "all",
                "message": "Use 'python tools/agent_orient.py' for orientation",
                "available_commands": ["quick_start", "list_systems", "list_tools"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Agent orientation failed: {e}")
            return {
                "category": "orient",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def tasks_find(self, agent_id: str = None, task_keyword: str = None) -> Dict[str, Any]:
        """Find tasks for an agent."""
        try:
            from tools.agent_task_finder import find_violations, load_project_analysis
            
            data = load_project_analysis()
            tasks = find_violations(data)
            
            return {
                "category": "tasks",
                "action": "find",
                "agent": agent_id,
                "tasks": tasks,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Task finding failed: {e}")
            return {
                "category": "tasks",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def status_check(self, agent_id: str = None) -> Dict[str, Any]:
        """Check agent status."""
        try:
            from tools.check_status_monitor_and_agent_statuses import check_all_agent_statuses
            
            if agent_id:
                # Check single agent
                status_file = self.agent_workspaces / agent_id / "status.json"
                if status_file.exists():
                    with open(status_file, 'r', encoding='utf-8') as f:
                        status = json.load(f)
                    return {
                        "category": "status",
                        "action": "check",
                        "agent": agent_id,
                        "status": status,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "category": "status",
                        "action": "check",
                        "agent": agent_id,
                        "error": "Status file not found",
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                # Check all agents
                statuses = check_all_agent_statuses()
                return {
                    "category": "status",
                    "action": "check",
                    "agent": "all",
                    "statuses": statuses,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {
                "category": "status",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def status_activity(self, agent_id: str = None) -> Dict[str, Any]:
        """Detect agent activity."""
        try:
            from tools.agent_activity_detector import AgentActivityDetector
            
            detector = AgentActivityDetector()
            
            if agent_id:
                activity = detector.detect_agent_activity(agent_id)
                return {
                    "category": "status",
                    "action": "activity",
                    "agent": agent_id,
                    "activity": {
                        "is_active": activity.is_active,
                        "last_activity": activity.last_activity.isoformat() if activity.last_activity else None,
                        "inactivity_duration_minutes": activity.inactivity_duration_minutes,
                        "activity_sources": activity.activity_sources
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Check all agents (use SSOT constant)
                from src.core.constants.agent_constants import AGENT_PROCESSING_ORDER
                agents = AGENT_PROCESSING_ORDER
                activities = {}
                for agent in agents:
                    try:
                        activity = detector.detect_agent_activity(agent)
                        activities[agent] = {
                            "is_active": activity.is_active,
                            "last_activity": activity.last_activity.isoformat() if activity.last_activity else None,
                            "inactivity_duration_minutes": activity.inactivity_duration_minutes
                        }
                    except Exception as e:
                        activities[agent] = {"error": str(e)}
                
                return {
                    "category": "status",
                    "action": "activity",
                    "agent": "all",
                    "activities": activities,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Activity detection failed: {e}")
            return {
                "category": "status",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def lifecycle_automate(self, agent_id: str = None) -> Dict[str, Any]:
        """Automate agent lifecycle operations."""
        try:
            from tools.agent_lifecycle_automator import StatusUpdater, PipelineGas, WorkspaceCleanup
            
            if agent_id:
                updater = StatusUpdater(agent_id)
                return {
                    "category": "lifecycle",
                    "action": "automate",
                    "agent": agent_id,
                    "message": "Lifecycle automation initialized",
                    "components": ["StatusUpdater", "PipelineGas", "WorkspaceCleanup"],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "category": "lifecycle",
                    "action": "automate",
                    "message": "Lifecycle automation requires agent_id",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Lifecycle automation failed: {e}")
            return {
                "category": "lifecycle",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def onboard_hard(self, agents: List[str] = None) -> Dict[str, Any]:
        """Hard onboard agents."""
        try:
            from tools.hard_onboard_agents_6_7_8 import hard_onboard_agents
            
            if agents:
                result = hard_onboard_agents(agents)
            else:
                # Default to agents 6, 7, 8
                result = hard_onboard_agents(["Agent-6", "Agent-7", "Agent-8"])
            
            return {
                "category": "onboard",
                "action": "hard",
                "agents": agents or ["Agent-6", "Agent-7", "Agent-8"],
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Hard onboarding failed: {e}")
            return {
                "category": "onboard",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def lifecycle_heal(self, agent_id: str = None) -> Dict[str, Any]:
        """Heal stalled agents."""
        try:
            from tools.heal_stalled_agents import run_healing_check
            import asyncio
            
            # Run healing check
            result = asyncio.run(run_healing_check())
            
            return {
                "category": "lifecycle",
                "action": "heal",
                "agent": agent_id or "all",
                "message": "Healing check completed",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Healing failed: {e}")
            return {
                "category": "lifecycle",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def main():
    """CLI entry point for unified agent tool."""
    parser = argparse.ArgumentParser(
        description="Unified Agent Operations Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m tools.unified_agent orient --agent Agent-1
  python -m tools.unified_agent tasks find --agent Agent-1
  python -m tools.unified_agent status check --agent Agent-1
  python -m tools.unified_agent status activity
  python -m tools.unified_agent lifecycle automate
  python -m tools.unified_agent onboard hard --agents Agent-6 Agent-7 Agent-8
  python -m tools.unified_agent lifecycle heal --agent Agent-1
        """
    )
    
    parser.add_argument(
        "category",
        choices=["orient", "tasks", "status", "lifecycle", "onboard"],
        help="Agent operation category"
    )
    
    parser.add_argument(
        "action",
        help="Action to perform within category"
    )
    
    parser.add_argument("--agent", help="Agent ID")
    parser.add_argument("--agents", nargs="+", help="Multiple agent IDs")
    parser.add_argument("--keyword", help="Task keyword for search")
    
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    agent = UnifiedAgent()
    results = {}
    
    # Route to appropriate category method
    if args.category == "orient":
        if args.action == "agent" and args.agent:
            results = agent.orient_agent(args.agent)
        else:
            results = {"error": "Agent ID required for orientation"}
    
    elif args.category == "tasks":
        if args.action == "find":
            results = agent.tasks_find(args.agent, args.keyword)
        else:
            results = {"error": f"Unknown tasks action: {args.action}"}
    
    elif args.category == "status":
        if args.action == "check":
            results = agent.status_check(args.agent)
        elif args.action == "activity":
            results = agent.status_activity(args.agent)
        else:
            results = {"error": f"Unknown status action: {args.action}"}
    
    elif args.category == "lifecycle":
        if args.action == "automate":
            results = agent.lifecycle_automate(args.agent)
        elif args.action == "heal":
            results = agent.lifecycle_heal(args.agent)
        else:
            results = {"error": f"Unknown lifecycle action: {args.action}"}
    
    elif args.category == "onboard":
        if args.action == "hard":
            agents = args.agents if args.agents else None
            results = agent.onboard_hard(agents)
        else:
            results = {"error": f"Unknown onboard action: {args.action}"}
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        if "error" in results:
            print(f"❌ Error: {results['error']}")
        else:
            print(json.dumps(results, indent=2, default=str))
    
    return 0 if "error" not in results else 1


if __name__ == "__main__":
    sys.exit(main())

