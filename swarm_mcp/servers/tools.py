#!/usr/bin/env python3
"""
MCP Server for Swarm Toolbelt
Exposes the Unified CLI Toolbelt to Agents via Model Context Protocol
"""

import json
import sys
import subprocess
import shutil
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path to import tools registry
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from tools.toolbelt_registry import TOOLS_REGISTRY
except ImportError:
    # Fallback if tools directory not found in python path
    TOOLS_REGISTRY = {}

def execute_toolbelt(flag: str, args: List[str] = None) -> Dict[str, Any]:
    """Execute a toolbelt command via subprocess."""
    args = args or []
    
    # Ensure we run from workspace root
    cwd = Path(__file__).parent.parent.parent
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(cwd) + os.pathsep + env.get("PYTHONPATH", "")
    
    cmd = [sys.executable, "-m", "tools.toolbelt", flag] + args
    
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            check=False
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "debug_cwd": str(cwd),
            "debug_pythonpath": env.get("PYTHONPATH"),
            "debug_cmd": str(cmd)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_available_tools() -> Dict[str, Any]:
    """List all available tools in the registry."""
    tools_list = []
    for key, config in TOOLS_REGISTRY.items():
        tools_list.append({
            "name": config["name"],
            "id": key,
            "description": config["description"],
            "flags": config["flags"]
        })
    return {"count": len(tools_list), "tools": tools_list}

def main():
    """MCP server main loop."""
    
    # Generate MCP tool definitions from registry
    mcp_tools = {
        "list_tools": {
            "description": "List all available tools in the Swarm Toolbelt",
            "inputSchema": {"type": "object", "properties": {}},
        },
        "run_tool": {
            "description": "Run a specific tool from the toolbelt",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tool_name": {
                        "type": "string",
                        "description": "The tool ID (e.g. 'monitor', 'analyzer', 'security-scan')",
                        # We could enum this, but dynamic is better for updates
                    },
                    "arguments": {
                        "type": "string",
                        "description": "Additional arguments to pass to the tool (e.g. '--category all')",
                    }
                },
                "required": ["tool_name"]
            }
        }
    }

    # Also expose high-value tools directly for easier discovery
    high_value_mappings = {
        "run_monitor": "monitor",
        "run_analyzer": "analyzer", 
        "run_validator": "validator",
        "run_security_scan": "security-scan",
        "run_debugger": "debugger",
        "run_environment": "environment"
    }

    for mcp_name, tool_id in high_value_mappings.items():
        if tool_id in TOOLS_REGISTRY:
            desc = TOOLS_REGISTRY[tool_id]["description"]
            mcp_tools[mcp_name] = {
                "description": f"Execute {desc}",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "args": {
                            "type": "string",
                            "description": "Optional arguments"
                        }
                    }
                }
            }

    print(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "initialize",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": mcp_tools
                    },
                    "serverInfo": {"name": "swarm-tools", "version": "1.0.0"},
                },
            }
        )
    )
    sys.stdout.flush()

    for line in sys.stdin:
        try:
            if not line.strip():
                continue
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})

            if method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = {}
                
                if tool_name == "list_tools":
                    result = list_available_tools()
                
                elif tool_name == "run_tool":
                    tid = arguments.get("tool_name")
                    extra_args = arguments.get("arguments", "").split() if arguments.get("arguments") else []
                    
                    if tid in TOOLS_REGISTRY:
                        # Use the first flag
                        flag = TOOLS_REGISTRY[tid]["flags"][0]
                        result = execute_toolbelt(flag, extra_args)
                    else:
                        result = {"success": False, "error": f"Tool '{tid}' not found"}

                elif tool_name in high_value_mappings:
                    tid = high_value_mappings[tool_name]
                    extra_args = arguments.get("args", "").split() if arguments.get("args") else []
                    flag = TOOLS_REGISTRY[tid]["flags"][0]
                    result = execute_toolbelt(flag, extra_args)
                
                else:
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}

                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
                }))
                sys.stdout.flush()
                
        except Exception as e:
            # Try to report error if we have an id
            try:
                req_id = request.get("id") if 'request' in locals() else None
                if req_id:
                    print(json.dumps({
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32603, "message": str(e)}
                    }))
                    sys.stdout.flush()
            except:
                pass

if __name__ == "__main__":
    main()
