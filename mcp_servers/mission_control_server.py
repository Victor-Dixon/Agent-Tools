#!/usr/bin/env python3
"""
MCP Server for Mission Control
Exposes Captain's coordination, mission assignment, and integrity tools
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root and tools folders to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "tools_v2"))

try:
    from tools_v2.categories.captain_tools import (
        StatusCheckTool,
        MissionAssignTool,
        IntegrityCheckTool,
        LeaderboardUpdateTool,
        PointsCalculatorTool,
        MarkovOptimizerTool
    )
    HAS_TOOLS = True
except ImportError:
    HAS_TOOLS = False


def check_agent_status(agents: Optional[List[str]] = None, threshold_hours: int = 24) -> Dict[str, Any]:
    """Check all agent status files to detect idle agents."""
    if not HAS_TOOLS:
        return {"success": False, "error": "Captain tools not available"}

    try:
        tool = StatusCheckTool()
        result = tool.execute({"agents": agents, "threshold_hours": threshold_hours})
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": str(e)}


def assign_mission(
    agent_id: str,
    mission_title: str,
    mission_description: str,
    points: int = 0,
    roi: float = 0.0,
    complexity: str = "medium",
    priority: str = "regular",
    dependencies: List[str] = []
) -> Dict[str, Any]:
    """Create structured mission file in agent inbox."""
    if not HAS_TOOLS:
        return {"success": False, "error": "Captain tools not available"}

    try:
        tool = MissionAssignTool()
        result = tool.execute({
            "agent_id": agent_id,
            "mission_title": mission_title,
            "mission_description": mission_description,
            "points": points,
            "roi": roi,
            "complexity": complexity,
            "priority": priority,
            "dependencies": dependencies
        })
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_integrity(agent_id: str, claimed_work: str, search_terms: List[str] = []) -> Dict[str, Any]:
    """Verify work claims with git history (Entry #025)."""
    if not HAS_TOOLS:
        return {"success": False, "error": "Captain tools not available"}

    try:
        tool = IntegrityCheckTool()
        result = tool.execute({
            "agent_id": agent_id,
            "claimed_work": claimed_work,
            "search_terms": search_terms
        })
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": str(e)}


def update_leaderboard(
    agent_id: Optional[str] = None,
    points: int = 0,
    achievement: Optional[str] = None,
    updates: Optional[Dict[str, int]] = None
) -> Dict[str, Any]:
    """Update agent leaderboard with points and achievements."""
    if not HAS_TOOLS:
        return {"success": False, "error": "Captain tools not available"}

    try:
        tool = LeaderboardUpdateTool()
        params = {}
        if updates:
            params["updates"] = updates
        else:
            params["agent_id"] = agent_id
            params["points"] = points
            if achievement:
                params["achievement"] = achievement
        
        result = tool.execute(params)
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": str(e)}


def calculate_points(
    task_type: str,
    impact: str = "medium",
    complexity: str = "medium",
    time_saved: float = 0,
    custom_multiplier: float = 1.0
) -> Dict[str, Any]:
    """Calculate points based on ROI metrics."""
    if not HAS_TOOLS:
        return {"success": False, "error": "Captain tools not available"}

    try:
        tool = PointsCalculatorTool()
        result = tool.execute({
            "task_type": task_type,
            "impact": impact,
            "complexity": complexity,
            "time_saved": time_saved,
            "custom_multiplier": custom_multiplier
        })
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": str(e)}


# MCP Server Protocol
def main():
    """MCP server main loop."""
    print(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "initialize",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "check_agent_status": {
                                "description": "Check all agent status files to detect idle agents",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agents": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Optional list of agents to check",
                                        },
                                        "threshold_hours": {
                                            "type": "integer",
                                            "default": 24,
                                            "description": "Hours before considering agent idle",
                                        },
                                    },
                                },
                            },
                            "assign_mission": {
                                "description": "Create structured mission file in agent inbox",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {"type": "string"},
                                        "mission_title": {"type": "string"},
                                        "mission_description": {"type": "string"},
                                        "points": {"type": "integer"},
                                        "roi": {"type": "number"},
                                        "complexity": {"type": "string"},
                                        "priority": {"type": "string"},
                                        "dependencies": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                    },
                                    "required": ["agent_id", "mission_title", "mission_description"],
                                },
                            },
                            "check_integrity": {
                                "description": "Verify work claims with git history",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {"type": "string"},
                                        "claimed_work": {"type": "string"},
                                        "search_terms": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                    },
                                    "required": ["agent_id", "claimed_work"],
                                },
                            },
                            "update_leaderboard": {
                                "description": "Update agent leaderboard with points",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {"type": "string"},
                                        "points": {"type": "integer"},
                                        "achievement": {"type": "string"},
                                        "updates": {
                                            "type": "object",
                                            "additionalProperties": {"type": "integer"}
                                        },
                                    },
                                },
                            },
                            "calculate_points": {
                                "description": "Calculate task points based on ROI metrics",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "task_type": {"type": "string"},
                                        "impact": {"type": "string"},
                                        "complexity": {"type": "string"},
                                        "time_saved": {"type": "number"},
                                        "custom_multiplier": {"type": "number"},
                                    },
                                    "required": ["task_type"],
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "mission-control-server", "version": "1.0.0"},
                },
            }
        )
    )

    # Handle tool calls
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})

            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name == "check_agent_status":
                    result = check_agent_status(**arguments)
                elif tool_name == "assign_mission":
                    result = assign_mission(**arguments)
                elif tool_name == "check_integrity":
                    result = check_integrity(**arguments)
                elif tool_name == "update_leaderboard":
                    result = update_leaderboard(**arguments)
                elif tool_name == "calculate_points":
                    result = calculate_points(**arguments)
                else:
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}

                print(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
                        }
                    )
                )
        except Exception as e:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32603, "message": str(e)},
                    }
                )
            )


if __name__ == "__main__":
    main()
