#!/usr/bin/env python3
"""
MCP Server for Task Management System
Exposes MASTER_TASK_LOG operations via Model Context Protocol
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Locate MASTER_TASK_LOG.md relative to workspace root
TASK_LOG_PATH = Path(__file__).parent.parent.parent / "MASTER_TASK_LOG.md"

def read_task_log() -> str:
    """Read the current MASTER_TASK_LOG.md file."""
    if not TASK_LOG_PATH.exists():
        return ""
    return TASK_LOG_PATH.read_text(encoding="utf-8")

def write_task_log(content: str) -> bool:
    """Write content to MASTER_TASK_LOG.md."""
    try:
        TASK_LOG_PATH.write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        return False

def add_to_inbox(task: str, agent_id: Optional[str] = None) -> Dict[str, Any]:
    """Add a task to the INBOX section."""
    try:
        content = read_task_log()
        
        # If file doesn't exist or is empty, maybe create it? 
        # For now assume it exists or fail gracefully if section missing.
        
        inbox_pattern = r"(## 📥 INBOX.*?\n\n)(.*?)(\n---)"
        match = re.search(inbox_pattern, content, re.DOTALL)

        if not match:
            return {"success": False, "error": "INBOX section not found in MASTER_TASK_LOG.md"}

        prefix = match.group(1)
        existing_tasks = match.group(2).strip()
        suffix = match.group(3)

        agent_note = f" (from {agent_id})" if agent_id else ""
        new_task = f"- [ ] {task}{agent_note}\n"
        
        updated_tasks = existing_tasks + "\n" + new_task if existing_tasks else new_task
        
        new_content = content[:match.start()] + prefix + updated_tasks + "\n" + suffix + content[match.end():]
        
        # Update timestamp
        new_content = re.sub(
            r"\*\*Last Updated:\*\* \d{4}-\d{2}-\d{2}",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}",
            new_content
        )

        if write_task_log(new_content):
            return {"success": True, "task": task, "location": "INBOX"}
        else:
            return {"success": False, "error": "Failed to write task log"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def mark_task_complete(task_description: str, section: str = "THIS WEEK") -> Dict[str, Any]:
    """Mark a task as complete."""
    try:
        content = read_task_log()
        
        section_patterns = {
            "THIS WEEK": r"(## 🎯 THIS WEEK.*?\n\n)(.*?)(\n---)",
            "INBOX": r"(## 📥 INBOX.*?\n\n)(.*?)(\n---)",
        }
        
        pattern = section_patterns.get(section)
        if not pattern:
            return {"success": False, "error": f"Unknown section: {section}"}
            
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            return {"success": False, "error": f"{section} section not found"}
            
        tasks_text = match.group(2)
        
        # Escape regex characters in task description
        escaped_desc = re.escape(task_description)
        # Look for [ ] followed by description
        task_pattern = rf"(- \[ \] .*?{escaped_desc}.*?\n)"
        
        if not re.search(task_pattern, tasks_text):
             return {"success": False, "error": f"Task not found: {task_description}"}
             
        replacement = r"- [x] " + task_description + "\n"
        new_tasks_text = re.sub(task_pattern, replacement, tasks_text)
        
        new_content = content[:match.start()] + match.group(1) + new_tasks_text + match.group(3) + content[match.end():]
        
        new_content = re.sub(
            r"\*\*Last Updated:\*\* \d{4}-\d{2}-\d{2}",
            f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}",
            new_content
        )

        if write_task_log(new_content):
            return {"success": True, "task": task_description, "section": section}
        else:
            return {"success": False, "error": "Failed to write task log"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_tasks(section: Optional[str] = None) -> Dict[str, Any]:
    """Get tasks from specified section or all sections."""
    try:
        content = read_task_log()
        
        sections_map = {
            "INBOX": r"## 📥 INBOX.*?\n\n(.*?)\n---",
            "THIS WEEK": r"## 🎯 THIS WEEK.*?\n\n(.*?)\n---",
            "WAITING ON": r"## ⏳ WAITING ON.*?\n\n(.*?)\n---",
            "PARKED": r"## 🧊 PARKED.*?\n\n(.*?)\n---",
        }

        if section:
            pattern = sections_map.get(section)
            if not pattern:
                return {"success": False, "error": f"Unknown section: {section}"}
            
            match = re.search(pattern, content, re.DOTALL)
            tasks = []
            if match:
                tasks_text = match.group(1).strip()
                tasks = [line.strip() for line in tasks_text.split("\n") if line.strip().startswith("-")]
            return {"success": True, "section": section, "tasks": tasks}
        else:
            results = {}
            for sec_name, pattern in sections_map.items():
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    tasks_text = match.group(1).strip()
                    results[sec_name] = [line.strip() for line in tasks_text.split("\n") if line.strip().startswith("-")]
            return {"success": True, "sections": results}
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
                            "add_task_to_inbox": {
                                "description": "Add a task to the INBOX",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "task": {"type": "string"},
                                        "agent_id": {"type": "string"},
                                    },
                                    "required": ["task"],
                                },
                            },
                            "mark_task_complete": {
                                "description": "Mark a task as complete",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "task_description": {"type": "string"},
                                        "section": {
                                            "type": "string",
                                            "enum": ["THIS WEEK", "INBOX"],
                                            "default": "THIS WEEK"
                                        },
                                    },
                                    "required": ["task_description"],
                                },
                            },
                            "get_tasks": {
                                "description": "Get tasks from log",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "section": {
                                            "type": "string",
                                            "enum": ["INBOX", "THIS WEEK", "WAITING ON", "PARKED"],
                                        },
                                    },
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "swarm-tasks", "version": "1.0.0"},
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

                if tool_name == "add_task_to_inbox":
                    result = add_to_inbox(**arguments)
                elif tool_name == "mark_task_complete":
                    result = mark_task_complete(**arguments)
                elif tool_name == "get_tasks":
                    result = get_tasks(**arguments)
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
