#!/usr/bin/env python3
"""
MCP Server for Swarm Messaging System
Exposes messaging capabilities via Model Context Protocol
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.coordinate_loader import get_coordinate_loader
from src.core.messaging_core import (
    UnifiedMessagePriority,
    UnifiedMessageTag,
    UnifiedMessageType,
    send_message,
)


def send_agent_message(agent_id: str, message: str, priority: str = "regular") -> dict:
    """Send message to agent via PyAutoGUI coordinates."""
    try:
        msg_priority = (
            UnifiedMessagePriority.URGENT
            if priority.lower() == "urgent"
            else UnifiedMessagePriority.REGULAR
        )

        success = send_message(
            content=message,
            sender="CAPTAIN",
            recipient=agent_id,
            message_type=UnifiedMessageType.CAPTAIN_TO_AGENT,
            priority=msg_priority,
            tags=[UnifiedMessageTag.SYSTEM],
        )

        return {
            "success": success,
            "agent": agent_id,
            "message_sent": message,
            "priority": priority,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def broadcast_message(message: str, priority: str = "regular") -> dict:
    """Broadcast message to all agents."""
    try:
        coord_loader = get_coordinate_loader()
        agents = coord_loader.get_all_agents()

        results = {}
        for agent_id in agents:
            result = send_agent_message(agent_id, message, priority)
            results[agent_id] = result["success"]

        success_count = sum(1 for success in results.values() if success)

        return {
            "success": True,
            "total_agents": len(agents),
            "successful": success_count,
            "results": results,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_agent_coordinates() -> dict:
    """Get coordinates for all agents."""
    try:
        coord_loader = get_coordinate_loader()
        agents = coord_loader.get_all_agents()

        coordinates = {}
        for agent_id in agents:
            coords = coord_loader.get_chat_coordinates(agent_id)
            coordinates[agent_id] = {
                "coordinates": coords,
                "active": coord_loader.is_agent_active(agent_id),
                "description": coord_loader.get_agent_description(agent_id),
            }

        return {"success": True, "agents": coordinates}
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
                                "description": "Send message to a specific agent via PyAutoGUI",
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
                            "get_agent_coordinates": {
                                "description": "Get coordinates and status for all agents",
                                "inputSchema": {"type": "object", "properties": {}},
                            },
                        }
                    },
                    "serverInfo": {"name": "swarm-messaging-server", "version": "1.0.0"},
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

                if tool_name == "send_agent_message":
                    result = send_agent_message(**arguments)
                elif tool_name == "broadcast_message":
                    result = broadcast_message(**arguments)
                elif tool_name == "get_agent_coordinates":
                    result = get_agent_coordinates()
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
