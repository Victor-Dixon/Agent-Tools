#!/usr/bin/env python3
"""
MCP Server for Automated Refactoring
Exposes code analysis and automated refactoring tools via Model Context Protocol
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root and tools folders to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "tools_v2"))

try:
    from tools_v2.categories.refactoring_tools import (
        FileSizeCheckTool,
        AutoExtractTool,
        LintFixTool,
        TestPyramidAnalyzerTool
    )
    HAS_TOOLS = True
except ImportError:
    HAS_TOOLS = False


def check_file_size(path: str, threshold: int = 400, recursive: bool = False) -> Dict[str, Any]:
    """Check if files meet V2 compliance size limits."""
    if not HAS_TOOLS:
        return {"success": False, "error": "Refactoring tools not available"}

    try:
        tool = FileSizeCheckTool()
        result = tool.execute({
            "path": path,
            "threshold": threshold,
            "recursive": recursive
        })
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": str(e)}


def auto_extract_code(path: str, target_lines: int = 400, strategy: str = "functions") -> Dict[str, Any]:
    """Automatically plan code extraction to reduce file size."""
    if not HAS_TOOLS:
        return {"success": False, "error": "Refactoring tools not available"}

    try:
        tool = AutoExtractTool()
        # Tool expects 'file' but I used 'path' for consistency, let's map it
        result = tool.execute({
            "file": path,
            "target_lines": target_lines,
            "strategy": strategy
        })
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": str(e)}


def fix_linting_issues(path: str, formatter: str = "ruff") -> Dict[str, Any]:
    """Auto-fix linting issues with ruff or black."""
    if not HAS_TOOLS:
        return {"success": False, "error": "Refactoring tools not available"}

    try:
        tool = LintFixTool()
        result = tool.execute({
            "path": path,
            "formatter": formatter
        })
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": str(e)}


def analyze_test_pyramid(test_dir: str = "tests/") -> Dict[str, Any]:
    """Analyze test pyramid distribution (60/30/10)."""
    if not HAS_TOOLS:
        return {"success": False, "error": "Refactoring tools not available"}

    try:
        tool = TestPyramidAnalyzerTool()
        result = tool.execute({"test_dir": test_dir})
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
                            "check_file_size": {
                                "description": "Check if files meet V2 compliance size limits",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "path": {"type": "string"},
                                        "threshold": {"type": "integer", "default": 400},
                                        "recursive": {"type": "boolean", "default": False},
                                    },
                                    "required": ["path"],
                                },
                            },
                            "auto_extract_code": {
                                "description": "Plan code extraction to reduce file size",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "path": {"type": "string", "description": "File path to analyze"},
                                        "target_lines": {"type": "integer", "default": 400},
                                        "strategy": {"type": "string", "enum": ["functions", "classes"], "default": "functions"},
                                    },
                                    "required": ["path"],
                                },
                            },
                            "fix_linting_issues": {
                                "description": "Auto-fix linting issues with ruff or black",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "path": {"type": "string"},
                                        "formatter": {"type": "string", "enum": ["ruff", "black"], "default": "ruff"},
                                    },
                                    "required": ["path"],
                                },
                            },
                            "analyze_test_pyramid": {
                                "description": "Analyze test pyramid distribution",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "test_dir": {"type": "string", "default": "tests/"},
                                    },
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "refactoring-server", "version": "1.0.0"},
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

                if tool_name == "check_file_size":
                    result = check_file_size(**arguments)
                elif tool_name == "auto_extract_code":
                    result = auto_extract_code(**arguments)
                elif tool_name == "fix_linting_issues":
                    result = fix_linting_issues(**arguments)
                elif tool_name == "analyze_test_pyramid":
                    result = analyze_test_pyramid(**arguments)
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
