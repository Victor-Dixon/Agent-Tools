#!/usr/bin/env python3
"""
MCP Server for Swarm Brain
Exposes Swarm Brain knowledge base operations via Model Context Protocol
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.swarm_brain.swarm_memory import SwarmMemory
    HAS_SWARM_BRAIN = True
except ImportError:
    HAS_SWARM_BRAIN = False
    SwarmMemory = None


def share_learning(
    agent_id: str, title: str, content: str, tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Share a learning to Swarm Brain."""
    if not HAS_SWARM_BRAIN:
        return {"success": False, "error": "Swarm Brain not available"}

    try:
        memory = SwarmMemory(agent_id=agent_id)
        entry_id = memory.share_learning(
            title=title,
            content=content,
            tags=tags or [],
        )

        return {
            "success": True,
            "agent_id": agent_id,
            "entry_id": entry_id,
            "title": title,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def record_decision(
    agent_id: str, title: str, decision: str, rationale: str, participants: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Record a decision to Swarm Brain."""
    if not HAS_SWARM_BRAIN:
        return {"success": False, "error": "Swarm Brain not available"}

    try:
        memory = SwarmMemory(agent_id=agent_id)
        memory.record_decision(
            title=title,
            decision=decision,
            rationale=rationale,
        )

        return {
            "success": True,
            "agent_id": agent_id,
            "title": title,
            "decision": decision,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_swarm_knowledge(agent_id: str, query: str, limit: int = 10) -> Dict[str, Any]:
    """Search Swarm Brain knowledge base."""
    if not HAS_SWARM_BRAIN:
        return {"success": False, "error": "Swarm Brain not available"}

    try:
        memory = SwarmMemory(agent_id=agent_id)
        results = memory.search_swarm_knowledge(query)

        # Convert KnowledgeEntry objects to dicts
        results_dict = []
        for entry in results[:limit]:
            results_dict.append({
                "id": entry.id,
                "title": entry.title,
                "content": entry.content,
                "author": entry.author,
                "category": entry.category,
                "tags": entry.tags,
                "timestamp": entry.timestamp.isoformat() if hasattr(entry.timestamp, 'isoformat') else str(entry.timestamp),
            })

        return {
            "success": True,
            "agent_id": agent_id,
            "query": query,
            "results_count": len(results_dict),
            "results": results_dict,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def take_note(agent_id: str, content: str, note_type: str = "important") -> Dict[str, Any]:
    """Take a personal note."""
    if not HAS_SWARM_BRAIN:
        return {"success": False, "error": "Swarm Brain not available"}

    try:
        from src.swarm_brain.agent_notes import NoteType

        # Map string to NoteType
        type_map = {
            "important": NoteType.IMPORTANT,
            "learning": NoteType.LEARNING,
            "todo": NoteType.TODO,
            "general": NoteType.GENERAL,
        }

        memory = SwarmMemory(agent_id=agent_id)
        memory.take_note(
            content=content,
            note_type=type_map.get(note_type.lower(), NoteType.IMPORTANT),
        )

        return {
            "success": True,
            "agent_id": agent_id,
            "content": content,
            "note_type": note_type,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_agent_notes(agent_id: str, note_type: Optional[str] = None) -> Dict[str, Any]:
    """Get agent's personal notes."""
    if not HAS_SWARM_BRAIN:
        return {"success": False, "error": "Swarm Brain not available"}

    try:
        from src.swarm_brain.agent_notes import NoteType

        memory = SwarmMemory(agent_id=agent_id)

        if note_type:
            type_map = {
                "important": NoteType.IMPORTANT,
                "learning": NoteType.LEARNING,
                "todo": NoteType.TODO,
                "general": NoteType.GENERAL,
            }
            notes = memory.get_my_notes(type_map.get(note_type.lower()))
        else:
            notes = memory.get_my_notes()

        return {
            "success": True,
            "agent_id": agent_id,
            "notes_count": len(notes),
            "notes": notes,
        }
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
                            "share_learning": {
                                "description": "Share a learning to Swarm Brain knowledge base",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {
                                            "type": "string",
                                            "description": "Agent ID (e.g., 'Agent-1')",
                                        },
                                        "title": {
                                            "type": "string",
                                            "description": "Learning title",
                                        },
                                        "content": {
                                            "type": "string",
                                            "description": "Learning content (markdown supported)",
                                        },
                                        "tags": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Optional: Tags for categorization",
                                        },
                                    },
                                    "required": ["agent_id", "title", "content"],
                                },
                            },
                            "record_decision": {
                                "description": "Record a decision to Swarm Brain",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {
                                            "type": "string",
                                            "description": "Agent ID",
                                        },
                                        "title": {
                                            "type": "string",
                                            "description": "Decision title",
                                        },
                                        "decision": {
                                            "type": "string",
                                            "description": "What was decided",
                                        },
                                        "rationale": {
                                            "type": "string",
                                            "description": "Why this decision was made",
                                        },
                                        "participants": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Optional: List of participating agents",
                                        },
                                    },
                                    "required": ["agent_id", "title", "decision", "rationale"],
                                },
                            },
                            "search_swarm_knowledge": {
                                "description": "Search Swarm Brain knowledge base",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {
                                            "type": "string",
                                            "description": "Agent ID",
                                        },
                                        "query": {
                                            "type": "string",
                                            "description": "Search query",
                                        },
                                        "limit": {
                                            "type": "integer",
                                            "default": 10,
                                            "description": "Maximum number of results (default: 10)",
                                        },
                                    },
                                    "required": ["agent_id", "query"],
                                },
                            },
                            "take_note": {
                                "description": "Take a personal note (agent-specific, not shared)",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {
                                            "type": "string",
                                            "description": "Agent ID",
                                        },
                                        "content": {
                                            "type": "string",
                                            "description": "Note content",
                                        },
                                        "note_type": {
                                            "type": "string",
                                            "enum": ["important", "learning", "todo", "general"],
                                            "default": "important",
                                            "description": "Type of note",
                                        },
                                    },
                                    "required": ["agent_id", "content"],
                                },
                            },
                            "get_agent_notes": {
                                "description": "Get agent's personal notes",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {
                                            "type": "string",
                                            "description": "Agent ID",
                                        },
                                        "note_type": {
                                            "type": "string",
                                            "enum": ["important", "learning", "todo", "general"],
                                            "description": "Optional: Filter by note type",
                                        },
                                    },
                                    "required": ["agent_id"],
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "swarm-brain-server", "version": "1.0.0"},
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

                if tool_name == "share_learning":
                    result = share_learning(**arguments)
                elif tool_name == "record_decision":
                    result = record_decision(**arguments)
                elif tool_name == "search_swarm_knowledge":
                    result = search_swarm_knowledge(**arguments)
                elif tool_name == "take_note":
                    result = take_note(**arguments)
                elif tool_name == "get_agent_notes":
                    result = get_agent_notes(**arguments)
                else:
                    result = {"success": False,
                              "error": f"Unknown tool: {tool_name}"}

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

