#!/usr/bin/env python3
"""
MCP Server for Swarm Messaging System
Exposes messaging capabilities via Model Context Protocol.
Updated to use Swarm MCP Core (File-based Messaging).
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from swarm_mcp.core.messaging import get_queue, HowlUrgency, HowlType
    from swarm_mcp.core.coordinator import PackCoordinator
except ImportError:
    # Fallback/Mock for verification environments without full setup
    class MockQueue:
        def send(self, *args, **kwargs): return True
    def get_queue(): return MockQueue()
    class PackCoordinator:
        def __init__(self, wolves, den): pass
        def roll_call(self): return {}

def send_agent_message(agent_id: str, message: str, priority: str = "regular") -> dict:
    """Send message to agent via Swarm Messaging."""
    try:
        urgency = (
            HowlUrgency.URGENT
            if priority.lower() == "urgent"
            else HowlUrgency.NORMAL
        )

        queue = get_queue()
        howl = queue.send(
            sender="MCP_SERVER",
            recipient=agent_id,
            content=message,
            urgency=urgency,
            howl_type=HowlType.WOLF_TO_WOLF
        )

        return {
            "success": True,
            "agent": agent_id,
            "message_sent": message,
            "priority": priority,
            "howl_id": howl.id
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def broadcast_message(message: str, priority: str = "regular") -> dict:
    """Broadcast message to all agents."""
    try:
        urgency = (
            HowlUrgency.URGENT
            if priority.lower() == "urgent"
            else HowlUrgency.NORMAL
        )
        
        # Discover agents via directory structure or config
        # Ideally we'd use PackCoordinator, but we need to know the wolves list
        # For now, let's just use a hardcoded list or scan directories
        # We'll use the queue's territory to find inboxes
        queue = get_queue()
        agents = [d.name for d in queue.territory.iterdir() if d.is_dir()]
        
        if not agents:
            # Fallback
            agents = ["Agent-1", "Agent-2", "Agent-3", "Agent-4", "Agent-5"]

        results = {}
        success_count = 0
        
        for agent_id in agents:
            try:
                queue.send(
                    sender="MCP_SERVER",
                    recipient=agent_id,
                    content=message,
                    urgency=urgency,
                    howl_type=HowlType.PACK_HOWL
                )
                results[agent_id] = True
                success_count += 1
            except Exception:
                results[agent_id] = False

        return {
            "success": True,
            "total_agents": len(agents),
            "successful": success_count,
            "results": results,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_agent_status() -> dict:
    """Get status for all agents."""
    try:
        queue = get_queue()
        agents = [d.name for d in queue.territory.iterdir() if d.is_dir()]
        
        # Basic status based on inbox
        statuses = {}
        for agent in agents:
            unheard = queue.count_unheard(agent)
            statuses[agent] = {
                "active": True,
                "unheard_messages": unheard,
                "description": f"Agent {agent}"
            }
            
        return {"success": True, "agents": statuses}
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
                            "send_agent_message": {
                                "description": "Send message to a specific agent via Swarm Messaging",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {
                                            "type": "string",
                                            "description": "Agent ID (e.g., Agent-1)",
                                        },
                                        "message": {
                                            "type": "string",
                                            "description": "Message content",
                                        },
                                        "priority": {
                                            "type": "string",
                                            "enum": ["regular", "urgent"],
                                            "default": "regular",
                                        },
                                    },
                                    "required": ["agent_id", "message"],
                                },
                            },
                            "broadcast_message": {
                                "description": "Broadcast message to all agents",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {
                                            "type": "string",
                                            "description": "Message content",
                                        },
                                        "priority": {
                                            "type": "string",
                                            "enum": ["regular", "urgent"],
                                            "default": "regular",
                                        },
                                    },
                                    "required": ["message"],
                                },
                            },
                            "get_agent_status": {
                                "description": "Get status for all agents",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                        }
                    },
                    "serverInfo": {"name": "swarm-messaging-server", "version": "2.0.0"},
                },
            }
        )
    )
    sys.stdout.flush()

    # Handle tool calls
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})

            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                result = {}
                if tool_name == "send_agent_message":
                    result = send_agent_message(**arguments)
                elif tool_name == "broadcast_message":
                    result = broadcast_message(**arguments)
                elif tool_name == "get_agent_status":
                    result = get_agent_status()
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
                sys.stdout.flush()
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
            sys.stdout.flush()


if __name__ == "__main__":
    main()
