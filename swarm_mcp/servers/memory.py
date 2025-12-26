#!/usr/bin/env python3
"""
MCP Server for Swarm Brain (Memory)
Exposes Swarm Brain knowledge base operations via Model Context Protocol
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from swarm_mcp.core.brain import SwarmBrain
    HAS_CORE = True
except ImportError:
    HAS_CORE = False

def share_learning(agent_id: str, title: str, content: str, category: str = "general", tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Share a learning to Swarm Brain."""
    if not HAS_CORE:
        return {"success": False, "error": "Swarm Core not available"}

    try:
        brain = SwarmBrain()
        learning = brain.share_learning(
            agent_id=agent_id,
            category=category,
            title=title,
            content=content,
            tags=tags or []
        )
        return {
            "success": True,
            "id": learning.id,
            "title": title
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def record_decision(agent_id: str, title: str, decision: str, rationale: str, outcome: Optional[str] = None, success: Optional[bool] = None) -> Dict[str, Any]:
    """Record a decision to Swarm Brain."""
    if not HAS_CORE:
        return {"success": False, "error": "Swarm Core not available"}

    try:
        brain = SwarmBrain()
        # Note: 'title' is not in SwarmBrain.record_decision, but was in the old server. 
        # The new one has 'context'. I'll map 'title' + 'rationale' to 'context' or just 'rationale' -> 'context'.
        # Actually record_decision has (agent_id, decision, context, outcome, success, learnings)
        
        dec = brain.record_decision(
            agent_id=agent_id,
            decision=decision,
            context=f"{title}: {rationale}",
            outcome=outcome,
            success=success
        )
        return {
            "success": True,
            "id": dec.id,
            "decision": decision
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_knowledge(agent_id: str, query: str, category: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
    """Search Swarm Brain knowledge base."""
    if not HAS_CORE:
        return {"success": False, "error": "Swarm Core not available"}

    try:
        brain = SwarmBrain()
        results = brain.search(query=query, category=category, limit=limit)
        
        return {
            "success": True,
            "query": query,
            "count": len(results),
            "results": [
                {
                    "id": r.id,
                    "title": r.title,
                    "content": r.content,
                    "category": r.category,
                    "tags": r.tags,
                    "author": r.agent_id
                }
                for r in results
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
                            "share_learning": {
                                "description": "Share a learning to Swarm Brain",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {"type": "string"},
                                        "title": {"type": "string"},
                                        "content": {"type": "string"},
                                        "category": {"type": "string", "default": "general"},
                                        "tags": {"type": "array", "items": {"type": "string"}},
                                    },
                                    "required": ["agent_id", "title", "content"],
                                },
                            },
                            "record_decision": {
                                "description": "Record a decision to Swarm Brain",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {"type": "string"},
                                        "title": {"type": "string"},
                                        "decision": {"type": "string"},
                                        "rationale": {"type": "string"},
                                        "outcome": {"type": "string"},
                                        "success": {"type": "boolean"},
                                    },
                                    "required": ["agent_id", "title", "decision", "rationale"],
                                },
                            },
                            "search_knowledge": {
                                "description": "Search Swarm Brain knowledge base",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {"type": "string"},
                                        "query": {"type": "string"},
                                        "category": {"type": "string"},
                                        "limit": {"type": "integer", "default": 10},
                                    },
                                    "required": ["agent_id", "query"],
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "swarm-memory", "version": "1.0.0"},
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

                if tool_name == "share_learning":
                    result = share_learning(**arguments)
                elif tool_name == "record_decision":
                    result = record_decision(**arguments)
                elif tool_name == "search_knowledge":
                    result = search_knowledge(**arguments)
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
