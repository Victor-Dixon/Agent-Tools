#!/usr/bin/env python3
"""
MCP Server for Mission Control (Pack Coordinator)
Exposes Captain's coordination and mission assignment tools
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from swarm_mcp.core.coordinator import PackCoordinator, Prey
    HAS_CORE = True
except ImportError:
    HAS_CORE = False

# Default configuration
DEFAULT_WOLVES = ["Agent-1", "Agent-2", "Agent-8", "Captain"]
DEFAULT_DEN = "./agent_workspaces" # Or workspace root

def get_coordinator() -> PackCoordinator:
    """Get coordinator instance."""
    # We might need to persist this or re-init each time.
    # Since MCP is stateless between calls (unless we keep process alive), we re-init.
    # PackCoordinator is file-based so it's fine.
    return PackCoordinator(wolves=DEFAULT_WOLVES, den=DEFAULT_DEN)

def check_pack_status() -> Dict[str, Any]:
    """Check status of all agents."""
    if not HAS_CORE:
        return {"success": False, "error": "Swarm Core not available"}
        
    try:
        coord = get_coordinator()
        status = coord.roll_call()
        
        # Convert dataclasses to dicts
        result = {}
        for wolf, stat in status.items():
            result[wolf] = {
                "role": stat.role,
                "status": stat.status,
                "current_hunt": stat.current_hunt,
                "kills": stat.kills,
                "last_howl": stat.last_howl.isoformat()
            }
            
        return {"success": True, "pack_status": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

def assign_hunt(agent_id: str, task: str, difficulty: int = 3) -> Dict[str, Any]:
    """Assign a task (hunt) to an agent."""
    if not HAS_CORE:
        return {"success": False, "error": "Swarm Core not available"}

    try:
        coord = get_coordinator()
        success = coord.assign_hunt(wolf_id=agent_id, prey=task, difficulty=difficulty)
        
        return {
            "success": success,
            "agent_id": agent_id,
            "task": task,
            "status": "assigned"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def scout_territory(path: str = ".") -> Dict[str, Any]:
    """Scout for TODOs and FIXMEs."""
    if not HAS_CORE:
        return {"success": False, "error": "Swarm Core not available"}

    try:
        coord = get_coordinator()
        prey_list = coord.scout_territory(path)
        
        return {
            "success": True,
            "count": len(prey_list),
            "prey": [
                {
                    "id": p.prey_id,
                    "description": p.description,
                    "location": p.location,
                    "difficulty": p.difficulty
                }
                for p in prey_list[:50] # Limit output
            ]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

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
                            "check_pack_status": {
                                "description": "Check status of all agents in the pack",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                            "assign_hunt": {
                                "description": "Assign a task (hunt) to an agent",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {"type": "string"},
                                        "task": {"type": "string"},
                                        "difficulty": {"type": "integer", "default": 3},
                                    },
                                    "required": ["agent_id", "task"],
                                },
                            },
                            "scout_territory": {
                                "description": "Scan codebase for TODOs and FIXMEs",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "path": {"type": "string", "default": "."},
                                    },
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "swarm-control", "version": "1.0.0"},
                },
            }
        )
    )

    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})

            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name == "check_pack_status":
                    result = check_pack_status()
                elif tool_name == "assign_hunt":
                    result = assign_hunt(**arguments)
                elif tool_name == "scout_territory":
                    result = scout_territory(**arguments)
                else:
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}

                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
                }))
        except Exception as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32603, "message": str(e)}
            }))

if __name__ == "__main__":
    main()
