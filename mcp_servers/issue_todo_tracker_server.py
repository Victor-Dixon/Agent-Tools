#!/usr/bin/env python3
"""
Issue/TODO Tracker Server - MCP server for code-to-issue automation.

Tools:
- extract_todos: Find all TODOs/FIXMEs in code
- create_issue_from_todo: Create GitHub issue from TODO
- link_todo_to_issue: Update TODO with issue number
- list_stale_issues: Find old unresolved issues
- close_completed: Auto-close issues for merged PRs
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# TODO patterns to match
TODO_PATTERNS = [
    # Standard TODO/FIXME patterns
    r'(?P<type>TODO|FIXME|HACK|XXX|BUG|NOTE|OPTIMIZE|REFACTOR)[\s:]+(?P<text>[^\n]+)',
    # With author: TODO(author): text
    r'(?P<type>TODO|FIXME|HACK|XXX|BUG)[\s]*\((?P<author>[^)]+)\)[\s:]+(?P<text>[^\n]+)',
    # With issue reference: TODO #123: text
    r'(?P<type>TODO|FIXME)[\s]*#(?P<issue>\d+)[\s:]+(?P<text>[^\n]+)',
]

EXCLUDED_DIRS = {'node_modules', '.git', 'vendor', 'venv', '.venv', '__pycache__', 'dist', 'build', '.next', 'coverage'}
CODE_EXTENSIONS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.rb', '.php', '.swift', '.kt', '.scala', '.sh', '.bash', '.zsh'}


def extract_todos(
    project_path: str = ".",
    types: list[str] | None = None,
    include_extensions: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
    max_results: int = 100
) -> dict[str, Any]:
    """Find all TODOs/FIXMEs in the codebase."""
    project_path = Path(project_path).resolve()
    
    if not project_path.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    
    types = types or ["TODO", "FIXME", "HACK", "XXX", "BUG", "NOTE", "OPTIMIZE", "REFACTOR"]
    extensions = set(include_extensions) if include_extensions else CODE_EXTENSIONS
    exclude_patterns = exclude_patterns or []
    
    todos = []
    files_scanned = 0
    
    # Build combined pattern
    type_pattern = '|'.join(types)
    combined_pattern = rf'(?P<type>{type_pattern})[\s]*(?:\((?P<author>[^)]+)\))?[\s]*(?:#(?P<issue>\d+))?[\s:]+(?P<text>[^\n]+)'
    
    for file_path in project_path.rglob('*'):
        if not file_path.is_file():
            continue
        
        # Skip excluded directories
        if any(excluded in file_path.parts for excluded in EXCLUDED_DIRS):
            continue
        
        # Check extension
        if file_path.suffix.lower() not in extensions:
            continue
        
        # Check exclude patterns
        rel_path = str(file_path.relative_to(project_path))
        skip = False
        for pattern in exclude_patterns:
            if Path(rel_path).match(pattern):
                skip = True
                break
        if skip:
            continue
        
        try:
            content = file_path.read_text(errors='ignore')
            files_scanned += 1
            
            for match in re.finditer(combined_pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                
                todo = {
                    "file": rel_path,
                    "line": line_num,
                    "type": match.group("type").upper(),
                    "text": match.group("text").strip(),
                    "author": match.group("author") if match.group("author") else None,
                    "issue": int(match.group("issue")) if match.group("issue") else None
                }
                todos.append(todo)
                
                if len(todos) >= max_results:
                    break
                    
        except Exception:
            continue
        
        if len(todos) >= max_results:
            break
    
    # Sort by file, then by line
    todos.sort(key=lambda x: (x["file"], x["line"]))
    
    # Group by type for summary
    by_type = {}
    for todo in todos:
        t = todo["type"]
        by_type[t] = by_type.get(t, 0) + 1
    
    return {
        "success": True,
        "todos": todos,
        "total": len(todos),
        "files_scanned": files_scanned,
        "by_type": by_type,
        "linked_to_issues": len([t for t in todos if t["issue"]]),
        "truncated": len(todos) >= max_results
    }


def create_issue_from_todo(
    todo_file: str,
    todo_line: int,
    todo_text: str,
    project_path: str = ".",
    labels: list[str] | None = None,
    assignee: str | None = None,
    add_code_context: bool = True
) -> dict[str, Any]:
    """Create a GitHub issue from a TODO comment."""
    project_path = Path(project_path).resolve()
    
    # Verify gh CLI is available
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except:
        return {"success": False, "error": "GitHub CLI (gh) not found or not authenticated"}
    
    # Generate issue title from TODO text
    title = todo_text[:80]
    if len(todo_text) > 80:
        title = title.rsplit(' ', 1)[0] + "..."
    
    # Build issue body
    body_parts = [
        f"## TODO from code",
        f"",
        f"**File:** `{todo_file}`",
        f"**Line:** {todo_line}",
        f"",
        f"### Description",
        f"",
        f"{todo_text}",
        f"",
    ]
    
    # Add code context if requested
    if add_code_context:
        file_path = project_path / todo_file
        if file_path.exists():
            try:
                lines = file_path.read_text().split('\n')
                start = max(0, todo_line - 4)
                end = min(len(lines), todo_line + 3)
                
                # Get file extension for syntax highlighting
                ext = file_path.suffix.lstrip('.')
                lang = {'py': 'python', 'js': 'javascript', 'ts': 'typescript', 'rb': 'ruby', 'go': 'go', 'rs': 'rust'}.get(ext, ext)
                
                code_context = '\n'.join(lines[start:end])
                body_parts.extend([
                    f"### Code Context",
                    f"",
                    f"```{lang}",
                    code_context,
                    f"```",
                    f"",
                ])
            except:
                pass
    
    body_parts.extend([
        f"---",
        f"_Created from TODO comment by Issue/TODO Tracker_"
    ])
    
    body = '\n'.join(body_parts)
    
    # Build gh command
    cmd = ["gh", "issue", "create", "--title", title, "--body", body]
    
    if labels:
        for label in labels:
            cmd.extend(["--label", label])
    
    if assignee:
        cmd.extend(["--assignee", assignee])
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Parse issue URL from output
            issue_url = result.stdout.strip()
            issue_number = None
            if issue_url:
                match = re.search(r'/issues/(\d+)', issue_url)
                if match:
                    issue_number = int(match.group(1))
            
            return {
                "success": True,
                "issue_url": issue_url,
                "issue_number": issue_number,
                "title": title
            }
        else:
            return {
                "success": False,
                "error": result.stderr
            }
            
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}


def link_todo_to_issue(
    file_path: str,
    line_number: int,
    issue_number: int,
    project_path: str = "."
) -> dict[str, Any]:
    """Update a TODO comment to include the issue number reference."""
    project_path = Path(project_path).resolve()
    full_path = project_path / file_path
    
    if not full_path.exists():
        return {"success": False, "error": f"File not found: {file_path}"}
    
    try:
        lines = full_path.read_text().split('\n')
        
        if line_number < 1 or line_number > len(lines):
            return {"success": False, "error": f"Invalid line number: {line_number}"}
        
        line_idx = line_number - 1
        original_line = lines[line_idx]
        
        # Check if line contains a TODO
        if not re.search(r'\b(TODO|FIXME|HACK|XXX|BUG)\b', original_line, re.IGNORECASE):
            return {"success": False, "error": "Line does not contain a TODO/FIXME"}
        
        # Check if already has an issue reference
        if re.search(r'#\d+', original_line):
            return {"success": False, "error": "Line already has an issue reference"}
        
        # Add issue reference after TODO/FIXME keyword
        updated_line = re.sub(
            r'\b(TODO|FIXME|HACK|XXX|BUG)\b(\s*:?\s*)',
            rf'\1 #{issue_number}\2',
            original_line,
            count=1,
            flags=re.IGNORECASE
        )
        
        lines[line_idx] = updated_line
        full_path.write_text('\n'.join(lines))
        
        return {
            "success": True,
            "file": file_path,
            "line": line_number,
            "original": original_line,
            "updated": updated_line,
            "issue_number": issue_number
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_stale_issues(
    project_path: str = ".",
    days: int = 30,
    state: str = "open",
    labels: list[str] | None = None,
    max_results: int = 50
) -> dict[str, Any]:
    """Find old unresolved issues."""
    project_path = Path(project_path).resolve()
    
    # Build gh command
    cmd = ["gh", "issue", "list", "--state", state, "--json", 
           "number,title,createdAt,updatedAt,labels,assignees,url"]
    
    if labels:
        for label in labels:
            cmd.extend(["--label", label])
    
    cmd.extend(["--limit", str(max_results * 2)])  # Get more to filter
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return {"success": False, "error": result.stderr}
        
        issues = json.loads(result.stdout)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        stale_issues = []
        for issue in issues:
            updated_at = datetime.fromisoformat(issue["updatedAt"].replace("Z", "+00:00"))
            if updated_at.replace(tzinfo=None) < cutoff_date:
                days_stale = (datetime.now() - updated_at.replace(tzinfo=None)).days
                stale_issues.append({
                    "number": issue["number"],
                    "title": issue["title"],
                    "url": issue["url"],
                    "created_at": issue["createdAt"],
                    "updated_at": issue["updatedAt"],
                    "days_stale": days_stale,
                    "labels": [l["name"] for l in issue.get("labels", [])],
                    "assignees": [a["login"] for a in issue.get("assignees", [])]
                })
        
        # Sort by staleness
        stale_issues.sort(key=lambda x: x["days_stale"], reverse=True)
        stale_issues = stale_issues[:max_results]
        
        return {
            "success": True,
            "stale_issues": stale_issues,
            "total": len(stale_issues),
            "threshold_days": days,
            "oldest_days": stale_issues[0]["days_stale"] if stale_issues else 0
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Failed to parse response: {e}"}


def close_completed(
    project_path: str = ".",
    check_branch: str | None = None,
    dry_run: bool = True
) -> dict[str, Any]:
    """Auto-close issues that have been fixed by merged PRs."""
    project_path = Path(project_path).resolve()
    
    # Keywords that indicate an issue is fixed
    fix_keywords = ["fixes", "fixed", "fix", "closes", "close", "closed", "resolves", "resolved", "resolve"]
    
    try:
        # Get list of open issues
        issues_result = subprocess.run(
            ["gh", "issue", "list", "--state", "open", "--json", "number,title,url", "--limit", "100"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if issues_result.returncode != 0:
            return {"success": False, "error": issues_result.stderr}
        
        open_issues = json.loads(issues_result.stdout)
        issue_numbers = {i["number"] for i in open_issues}
        
        # Get merged PRs
        prs_cmd = ["gh", "pr", "list", "--state", "merged", "--json", "number,title,body,mergedAt", "--limit", "50"]
        if check_branch:
            prs_cmd.extend(["--base", check_branch])
        
        prs_result = subprocess.run(
            prs_cmd,
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if prs_result.returncode != 0:
            return {"success": False, "error": prs_result.stderr}
        
        merged_prs = json.loads(prs_result.stdout)
        
        issues_to_close = []
        
        for pr in merged_prs:
            # Check PR title and body for issue references
            text = f"{pr.get('title', '')} {pr.get('body', '')}"
            
            # Find patterns like "fixes #123" or "closes #456"
            for keyword in fix_keywords:
                pattern = rf'\b{keyword}\s+#(\d+)\b'
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    issue_num = int(match)
                    if issue_num in issue_numbers:
                        issues_to_close.append({
                            "issue_number": issue_num,
                            "fixed_by_pr": pr["number"],
                            "pr_merged_at": pr["mergedAt"]
                        })
        
        # Deduplicate
        seen = set()
        unique_issues = []
        for item in issues_to_close:
            if item["issue_number"] not in seen:
                seen.add(item["issue_number"])
                unique_issues.append(item)
        
        closed_issues = []
        errors = []
        
        if not dry_run:
            for item in unique_issues:
                try:
                    close_result = subprocess.run(
                        ["gh", "issue", "close", str(item["issue_number"]), 
                         "--comment", f"Automatically closed - fixed by PR #{item['fixed_by_pr']}"],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=15
                    )
                    
                    if close_result.returncode == 0:
                        closed_issues.append(item)
                    else:
                        errors.append({
                            "issue": item["issue_number"],
                            "error": close_result.stderr
                        })
                except Exception as e:
                    errors.append({
                        "issue": item["issue_number"],
                        "error": str(e)
                    })
        
        return {
            "success": True,
            "dry_run": dry_run,
            "issues_to_close" if dry_run else "closed_issues": unique_issues if dry_run else closed_issues,
            "total": len(unique_issues),
            "errors": errors if not dry_run else []
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Failed to parse response: {e}"}


# MCP Server Implementation
TOOLS = [
    {
        "name": "extract_todos",
        "description": "Find all TODO, FIXME, HACK, XXX, BUG comments in the codebase",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Types of comments to find (TODO, FIXME, HACK, XXX, BUG, NOTE, OPTIMIZE, REFACTOR)"
                },
                "include_extensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "File extensions to include (e.g., ['.py', '.js'])"
                },
                "exclude_patterns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Glob patterns for files to exclude"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 100
                }
            }
        }
    },
    {
        "name": "create_issue_from_todo",
        "description": "Create a GitHub issue from a TODO comment",
        "inputSchema": {
            "type": "object",
            "properties": {
                "todo_file": {
                    "type": "string",
                    "description": "File path containing the TODO"
                },
                "todo_line": {
                    "type": "integer",
                    "description": "Line number of the TODO"
                },
                "todo_text": {
                    "type": "string",
                    "description": "Text of the TODO comment"
                },
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Labels to apply to the issue"
                },
                "assignee": {
                    "type": "string",
                    "description": "GitHub username to assign"
                },
                "add_code_context": {
                    "type": "boolean",
                    "description": "Include surrounding code context",
                    "default": True
                }
            },
            "required": ["todo_file", "todo_line", "todo_text"]
        }
    },
    {
        "name": "link_todo_to_issue",
        "description": "Update a TODO comment to include the issue number reference",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "File path containing the TODO"
                },
                "line_number": {
                    "type": "integer",
                    "description": "Line number of the TODO"
                },
                "issue_number": {
                    "type": "integer",
                    "description": "GitHub issue number to link"
                },
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                }
            },
            "required": ["file_path", "line_number", "issue_number"]
        }
    },
    {
        "name": "list_stale_issues",
        "description": "Find old unresolved issues that haven't been updated",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days without update to consider stale",
                    "default": 30
                },
                "state": {
                    "type": "string",
                    "description": "Issue state to filter (open, closed, all)",
                    "default": "open"
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by labels"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 50
                }
            }
        }
    },
    {
        "name": "close_completed",
        "description": "Auto-close issues that have been fixed by merged PRs",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {
                    "type": "string",
                    "description": "Path to the project directory",
                    "default": "."
                },
                "check_branch": {
                    "type": "string",
                    "description": "Base branch to check merged PRs against"
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "Only report issues that would be closed without actually closing them",
                    "default": True
                }
            }
        }
    }
]


def handle_tool_call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Route tool calls to appropriate functions."""
    if name == "extract_todos":
        return extract_todos(**arguments)
    elif name == "create_issue_from_todo":
        return create_issue_from_todo(**arguments)
    elif name == "link_todo_to_issue":
        return link_todo_to_issue(**arguments)
    elif name == "list_stale_issues":
        return list_stale_issues(**arguments)
    elif name == "close_completed":
        return close_completed(**arguments)
    else:
        return {"error": f"Unknown tool: {name}"}


def main():
    """Main MCP server loop."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            method = request.get("method")
            request_id = request.get("id")
            
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {"listChanged": True}},
                        "serverInfo": {
                            "name": "issue-todo-tracker-server",
                            "version": "1.0.0"
                        }
                    }
                }
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": TOOLS}
                }
            elif method == "tools/call":
                tool_name = request.get("params", {}).get("name")
                tool_args = request.get("params", {}).get("arguments", {})
                result = handle_tool_call(tool_name, tool_args)
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                    }
                }
            elif method == "notifications/initialized":
                continue
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
            
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
