#!/usr/bin/env python3
"""
MCP Server for Git Operations
Exposes git verification and commit checking capabilities via Model Context Protocol
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

try:
    from tools.git_work_verifier import GitWorkVerifier, VerificationResult
    HAS_GIT_VERIFIER = True
except ImportError:
    HAS_GIT_VERIFIER = False
    GitWorkVerifier = None

try:
    from tools.git_commit_verifier import check_commits_today, verify_work_exists
    HAS_COMMIT_VERIFIER = True
except ImportError:
    HAS_COMMIT_VERIFIER = False


def verify_git_work(
    agent_id: str, file_path: str, claimed_changes: str, time_window_hours: int = 24
) -> Dict[str, Any]:
    """Verify claimed work against git commits."""
    if not HAS_GIT_VERIFIER:
        return {"success": False, "error": "Git verifier not available"}

    try:
        verifier = GitWorkVerifier(repo_path=".")
        result = verifier.verify_claim(
            agent=agent_id,
            file_path=file_path,
            claimed_changes=claimed_changes,
            time_window_hours=time_window_hours,
        )

        return {
            "success": True,
            "verified": result.verified,
            "confidence": result.confidence,
            "reasoning": result.reasoning,
            "agent_id": agent_id,
            "file_path": file_path,
            "evidence": {
                "commit_hash": result.evidence.commit_hash if result.evidence else None,
                "author": result.evidence.author if result.evidence else None,
                "timestamp": result.evidence.timestamp.isoformat() if result.evidence and hasattr(result.evidence.timestamp, 'isoformat') else str(result.evidence.timestamp) if result.evidence else None,
                "files_changed": result.evidence.files_changed if result.evidence else [],
                "commit_message": result.evidence.commit_message if result.evidence else None,
            } if result.evidence else None,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_recent_commits(
    agent_id: Optional[str] = None, hours: int = 24, file_pattern: Optional[str] = None
) -> Dict[str, Any]:
    """Get recent git commits."""
    try:
        since = datetime.now() - timedelta(hours=hours)
        since_str = since.strftime("%Y-%m-%d %H:%M:%S")

        cmd = ["git", "log", f"--since={since_str}",
               "--pretty=format:%H|%an|%ai|%s", "--name-only"]
        if file_pattern:
            cmd.extend(["--", file_pattern])

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

        if result.returncode != 0:
            return {"success": False, "error": f"Git command failed: {result.stderr}"}

        commits = []
        current_commit = None

        for line in result.stdout.split("\n"):
            if "|" in line:
                # Commit line
                parts = line.split("|", 3)
                if len(parts) == 4:
                    hash_val, author, date, subject = parts
                    current_commit = {
                        "hash": hash_val,
                        "hash_short": hash_val[:8],
                        "author": author,
                        "date": date,
                        "subject": subject,
                        "files": [],
                    }
                    # Filter by agent if specified
                    if not agent_id or agent_id.lower() in author.lower():
                        commits.append(current_commit)
            elif line.strip() and current_commit:
                # File line
                current_commit["files"].append(line.strip())

        return {
            "success": True,
            "agent_id": agent_id,
            "hours": hours,
            "commits_count": len(commits),
            "commits": commits,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_file_history(file_path: str, days: int = 7) -> Dict[str, Any]:
    """Check git history for a specific file."""
    try:
        since = datetime.now() - timedelta(days=days)
        since_str = since.strftime("%Y-%m-%d")

        cmd = [
            "git",
            "log",
            f"--since={since_str}",
            "--pretty=format:%H|%an|%ai|%s",
            "--",
            file_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

        if result.returncode != 0:
            return {"success": False, "error": f"Git command failed: {result.stderr}"}

        commits = []
        for line in result.stdout.split("\n"):
            if "|" in line:
                parts = line.split("|", 3)
                if len(parts) == 4:
                    hash_val, author, date, subject = parts
                    commits.append({
                        "hash": hash_val,
                        "hash_short": hash_val[:8],
                        "author": author,
                        "date": date,
                        "subject": subject,
                    })

        return {
            "success": True,
            "file_path": file_path,
            "days": days,
            "commits_count": len(commits),
            "commits": commits,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def validate_commit(commit_hash: str) -> Dict[str, Any]:
    """Validate a commit exists and get details."""
    try:
        cmd = ["git", "show", "--pretty=format:%H|%an|%ai|%s",
               "--stat", "--no-patch", commit_hash]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

        if result.returncode != 0:
            return {"success": False, "error": f"Commit not found: {commit_hash}"}

        lines = result.stdout.split("\n")
        header = lines[0] if lines else ""

        if "|" in header:
            parts = header.split("|", 3)
            if len(parts) == 4:
                hash_val, author, date, subject = parts

                # Parse stats
                files_changed = 0
                insertions = 0
                deletions = 0

                for line in lines[1:]:
                    if "file" in line.lower() and "changed" in line.lower():
                        # Extract numbers from "X files changed, Y insertions(+), Z deletions(-)"
                        import re
                        match = re.search(r"(\d+)\s+files?\s+changed", line)
                        if match:
                            files_changed = int(match.group(1))
                        match = re.search(r"(\d+)\s+insertions?", line)
                        if match:
                            insertions = int(match.group(1))
                        match = re.search(r"(\d+)\s+deletions?", line)
                        if match:
                            deletions = int(match.group(1))

                return {
                    "success": True,
                    "commit_hash": hash_val,
                    "hash_short": hash_val[:8],
                    "author": author,
                    "date": date,
                    "subject": subject,
                    "files_changed": files_changed,
                    "insertions": insertions,
                    "deletions": deletions,
                }

        return {"success": False, "error": "Could not parse commit details"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def verify_work_exists_mcp(file_patterns: List[str], agent_name: Optional[str] = None) -> Dict[str, Any]:
    """Verify that work exists in git history (today's commits)."""
    if not HAS_COMMIT_VERIFIER:
        return {"success": False, "error": "Commit verifier not available"}

    try:
        verified = verify_work_exists(file_patterns, agent_name)

        # Get commits for details
        commits = []
        for pattern in file_patterns:
            pattern_commits = check_commits_today(pattern)
            commits.extend(pattern_commits)

        return {
            "success": True,
            "verified": verified,
            "agent_name": agent_name,
            "file_patterns": file_patterns,
            "commits_found": len(commits),
            "commits": commits,
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
                            "verify_git_work": {
                                "description": "Verify claimed work against git commits",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {
                                            "type": "string",
                                            "description": "Agent ID (e.g., 'Agent-1')",
                                        },
                                        "file_path": {
                                            "type": "string",
                                            "description": "File path that was modified",
                                        },
                                        "claimed_changes": {
                                            "type": "string",
                                            "description": "Description of claimed changes",
                                        },
                                        "time_window_hours": {
                                            "type": "integer",
                                            "default": 24,
                                            "description": "Time window to check (default: 24 hours)",
                                        },
                                    },
                                    "required": ["agent_id", "file_path", "claimed_changes"],
                                },
                            },
                            "get_recent_commits": {
                                "description": "Get recent git commits",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "agent_id": {
                                            "type": "string",
                                            "description": "Optional: Filter by agent ID",
                                        },
                                        "hours": {
                                            "type": "integer",
                                            "default": 24,
                                            "description": "Hours to look back (default: 24)",
                                        },
                                        "file_pattern": {
                                            "type": "string",
                                            "description": "Optional: File pattern to filter",
                                        },
                                    },
                                },
                            },
                            "check_file_history": {
                                "description": "Check git history for a specific file",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "file_path": {
                                            "type": "string",
                                            "description": "File path to check",
                                        },
                                        "days": {
                                            "type": "integer",
                                            "default": 7,
                                            "description": "Days to look back (default: 7)",
                                        },
                                    },
                                    "required": ["file_path"],
                                },
                            },
                            "validate_commit": {
                                "description": "Validate a commit exists and get details",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "commit_hash": {
                                            "type": "string",
                                            "description": "Commit hash (full or short)",
                                        },
                                    },
                                    "required": ["commit_hash"],
                                },
                            },
                            "verify_work_exists": {
                                "description": "Verify that work exists in today's git commits",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "file_patterns": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "File patterns to check",
                                        },
                                        "agent_name": {
                                            "type": "string",
                                            "description": "Optional: Agent name to filter",
                                        },
                                    },
                                    "required": ["file_patterns"],
                                },
                            },
                        }
                    },
                    "serverInfo": {"name": "git-operations-server", "version": "1.0.0"},
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

                if tool_name == "verify_git_work":
                    result = verify_git_work(**arguments)
                elif tool_name == "get_recent_commits":
                    result = get_recent_commits(**arguments)
                elif tool_name == "check_file_history":
                    result = check_file_history(**arguments)
                elif tool_name == "validate_commit":
                    result = validate_commit(**arguments)
                elif tool_name == "verify_work_exists":
                    result = verify_work_exists_mcp(**arguments)
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

