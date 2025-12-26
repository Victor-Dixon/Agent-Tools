#!/usr/bin/env python3
"""
MCP Server for CI/CD Helper
Monitor and manage CI/CD pipelines: status checks, logs, retries, and workflow management.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def _run_command(cmd: List[str], cwd: str = ".") -> Dict[str, Any]:
    """Run a command and return result."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=120
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _get_current_branch(cwd: str = ".") -> str:
    """Get current git branch."""
    result = _run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd)
    if result.get("success"):
        return result.get("stdout", "").strip()
    return "main"


def check_ci_status(
    branch: Optional[str] = None,
    commit: Optional[str] = None,
    cwd: str = "."
) -> Dict[str, Any]:
    """
    Get CI status for current branch or commit.
    
    Args:
        branch: Branch name (default: current branch)
        commit: Specific commit SHA (overrides branch)
        cwd: Working directory
    """
    ref = commit
    if not ref:
        branch = branch or _get_current_branch(cwd)
        ref = branch
    
    # Get check runs using gh CLI
    cmd = ["gh", "api", f"repos/:owner/:repo/commits/{ref}/check-runs", "--jq", ".check_runs"]
    result = _run_command(cmd, cwd)
    
    if not result.get("success"):
        # Try using gh pr checks if check-runs fails
        cmd = ["gh", "pr", "checks", "--json", "name,state,conclusion,link"]
        result = _run_command(cmd, cwd)
        
        if result.get("success") and result.get("stdout"):
            try:
                checks = json.loads(result["stdout"])
                return {
                    "success": True,
                    "ref": ref,
                    "checks": checks,
                    "summary": {
                        "total": len(checks),
                        "passed": sum(1 for c in checks if c.get("conclusion") == "success"),
                        "failed": sum(1 for c in checks if c.get("conclusion") == "failure"),
                        "pending": sum(1 for c in checks if c.get("state") == "pending")
                    }
                }
            except json.JSONDecodeError:
                pass
        
        return {"success": False, "error": result.get("stderr", "Failed to get CI status")}
    
    try:
        checks = json.loads(result.get("stdout", "[]"))
        check_list = []
        for check in checks:
            check_list.append({
                "name": check.get("name"),
                "status": check.get("status"),
                "conclusion": check.get("conclusion"),
                "started_at": check.get("started_at"),
                "completed_at": check.get("completed_at"),
                "url": check.get("html_url"),
                "run_id": check.get("id")
            })
        
        return {
            "success": True,
            "ref": ref,
            "checks": check_list,
            "summary": {
                "total": len(check_list),
                "passed": sum(1 for c in check_list if c.get("conclusion") == "success"),
                "failed": sum(1 for c in check_list if c.get("conclusion") == "failure"),
                "pending": sum(1 for c in check_list if c.get("status") == "in_progress" or c.get("status") == "queued")
            }
        }
    except json.JSONDecodeError:
        return {"success": False, "error": "Failed to parse CI status response"}


def get_failed_logs(
    run_id: Optional[int] = None,
    job_name: Optional[str] = None,
    limit_lines: int = 100,
    cwd: str = "."
) -> Dict[str, Any]:
    """
    Fetch logs from failed CI jobs.
    
    Args:
        run_id: Specific workflow run ID (default: latest failed)
        job_name: Filter by job name
        limit_lines: Max lines to return per job
        cwd: Working directory
    """
    # Get failed run if not specified
    if not run_id:
        cmd = ["gh", "run", "list", "--status", "failure", "--limit", "1", "--json", "databaseId,displayTitle,conclusion,headBranch"]
        result = _run_command(cmd, cwd)
        
        if result.get("success") and result.get("stdout"):
            try:
                runs = json.loads(result["stdout"])
                if runs:
                    run_id = runs[0].get("databaseId")
            except json.JSONDecodeError:
                pass
    
    if not run_id:
        return {"success": False, "error": "No failed runs found"}
    
    # Get job logs
    cmd = ["gh", "run", "view", str(run_id), "--log-failed"]
    result = _run_command(cmd, cwd)
    
    if not result.get("success"):
        # Try getting all logs
        cmd = ["gh", "run", "view", str(run_id), "--log"]
        result = _run_command(cmd, cwd)
    
    if result.get("success"):
        logs = result.get("stdout", "")
        
        # Parse logs by job
        jobs = {}
        current_job = "unknown"
        for line in logs.split("\n"):
            # Job headers look like: "jobname\tstepname\tlogline"
            parts = line.split("\t")
            if len(parts) >= 2:
                current_job = parts[0]
                if current_job not in jobs:
                    jobs[current_job] = []
                jobs[current_job].append("\t".join(parts[1:]))
            else:
                if current_job not in jobs:
                    jobs[current_job] = []
                jobs[current_job].append(line)
        
        # Filter by job name if specified
        if job_name:
            jobs = {k: v for k, v in jobs.items() if job_name.lower() in k.lower()}
        
        # Limit lines
        jobs = {k: v[-limit_lines:] for k, v in jobs.items()}
        
        return {
            "success": True,
            "run_id": run_id,
            "jobs": jobs,
            "job_count": len(jobs),
            "filtered_by": job_name
        }
    
    return {"success": False, "error": result.get("stderr", "Failed to get logs")}


def retry_failed_job(
    run_id: Optional[int] = None,
    job_id: Optional[int] = None,
    failed_only: bool = True,
    cwd: str = "."
) -> Dict[str, Any]:
    """
    Retry a failed CI job or workflow.
    
    Args:
        run_id: Workflow run ID to retry
        job_id: Specific job ID to retry (requires run_id)
        failed_only: Only retry failed jobs
        cwd: Working directory
    """
    if not run_id:
        # Get latest failed run
        cmd = ["gh", "run", "list", "--status", "failure", "--limit", "1", "--json", "databaseId"]
        result = _run_command(cmd, cwd)
        
        if result.get("success") and result.get("stdout"):
            try:
                runs = json.loads(result["stdout"])
                if runs:
                    run_id = runs[0].get("databaseId")
            except json.JSONDecodeError:
                pass
    
    if not run_id:
        return {"success": False, "error": "No run ID specified and no failed runs found"}
    
    # Retry the run
    if failed_only:
        cmd = ["gh", "run", "rerun", str(run_id), "--failed"]
    else:
        cmd = ["gh", "run", "rerun", str(run_id)]
    
    result = _run_command(cmd, cwd)
    
    if result.get("success"):
        return {
            "success": True,
            "run_id": run_id,
            "job_id": job_id,
            "failed_only": failed_only,
            "message": f"Successfully triggered retry for run {run_id}"
        }
    
    return {"success": False, "error": result.get("stderr", "Failed to retry")}


def list_workflows(
    status: Optional[str] = None,
    branch: Optional[str] = None,
    workflow: Optional[str] = None,
    limit: int = 10,
    cwd: str = "."
) -> Dict[str, Any]:
    """
    List recent workflow runs.
    
    Args:
        status: Filter by status (success, failure, pending, in_progress)
        branch: Filter by branch name
        workflow: Filter by workflow name/file
        limit: Max number of runs to return
        cwd: Working directory
    """
    cmd = ["gh", "run", "list", "--limit", str(limit), "--json", 
           "databaseId,displayTitle,status,conclusion,headBranch,event,createdAt,updatedAt,url,workflowName"]
    
    if status:
        cmd.extend(["--status", status])
    if branch:
        cmd.extend(["--branch", branch])
    if workflow:
        cmd.extend(["--workflow", workflow])
    
    result = _run_command(cmd, cwd)
    
    if result.get("success"):
        try:
            runs = json.loads(result.get("stdout", "[]"))
            
            return {
                "success": True,
                "runs": [{
                    "id": r.get("databaseId"),
                    "title": r.get("displayTitle"),
                    "workflow": r.get("workflowName"),
                    "status": r.get("status"),
                    "conclusion": r.get("conclusion"),
                    "branch": r.get("headBranch"),
                    "event": r.get("event"),
                    "created_at": r.get("createdAt"),
                    "updated_at": r.get("updatedAt"),
                    "url": r.get("url")
                } for r in runs],
                "count": len(runs),
                "filters": {
                    "status": status,
                    "branch": branch,
                    "workflow": workflow
                }
            }
        except json.JSONDecodeError:
            pass
    
    return {"success": False, "error": result.get("stderr", "Failed to list workflows")}


def cancel_workflow(
    run_id: int,
    cwd: str = "."
) -> Dict[str, Any]:
    """
    Cancel a running workflow.
    
    Args:
        run_id: Workflow run ID to cancel
        cwd: Working directory
    """
    cmd = ["gh", "run", "cancel", str(run_id)]
    result = _run_command(cmd, cwd)
    
    if result.get("success"):
        return {
            "success": True,
            "run_id": run_id,
            "message": f"Successfully cancelled workflow run {run_id}"
        }
    
    return {"success": False, "error": result.get("stderr", "Failed to cancel workflow")}


def get_workflow_artifacts(
    run_id: int,
    download: bool = False,
    artifact_name: Optional[str] = None,
    cwd: str = "."
) -> Dict[str, Any]:
    """
    List or download artifacts from a workflow run.
    
    Args:
        run_id: Workflow run ID
        download: Whether to download artifacts
        artifact_name: Specific artifact to download
        cwd: Working directory
    """
    # List artifacts
    cmd = ["gh", "api", f"repos/:owner/:repo/actions/runs/{run_id}/artifacts", "--jq", ".artifacts"]
    result = _run_command(cmd, cwd)
    
    if not result.get("success"):
        return {"success": False, "error": result.get("stderr", "Failed to get artifacts")}
    
    try:
        artifacts = json.loads(result.get("stdout", "[]"))
        artifact_list = [{
            "id": a.get("id"),
            "name": a.get("name"),
            "size_bytes": a.get("size_in_bytes"),
            "expired": a.get("expired"),
            "created_at": a.get("created_at"),
            "expires_at": a.get("expires_at")
        } for a in artifacts]
        
        if download:
            # Download artifacts
            download_cmd = ["gh", "run", "download", str(run_id)]
            if artifact_name:
                download_cmd.extend(["--name", artifact_name])
            
            dl_result = _run_command(download_cmd, cwd)
            
            return {
                "success": dl_result.get("success"),
                "run_id": run_id,
                "artifacts": artifact_list,
                "downloaded": dl_result.get("success"),
                "download_error": dl_result.get("stderr") if not dl_result.get("success") else None
            }
        
        return {
            "success": True,
            "run_id": run_id,
            "artifacts": artifact_list,
            "count": len(artifact_list)
        }
    except json.JSONDecodeError:
        return {"success": False, "error": "Failed to parse artifacts response"}


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
                            "check_ci_status": {
                                "description": "Get CI status for current branch or commit",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "branch": {
                                            "type": "string",
                                            "description": "Branch name (default: current branch)"
                                        },
                                        "commit": {
                                            "type": "string",
                                            "description": "Specific commit SHA"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "default": ".",
                                            "description": "Working directory"
                                        }
                                    }
                                }
                            },
                            "get_failed_logs": {
                                "description": "Fetch logs from failed CI jobs",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "run_id": {
                                            "type": "integer",
                                            "description": "Workflow run ID (default: latest failed)"
                                        },
                                        "job_name": {
                                            "type": "string",
                                            "description": "Filter by job name"
                                        },
                                        "limit_lines": {
                                            "type": "integer",
                                            "default": 100,
                                            "description": "Max lines per job"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "default": ".",
                                            "description": "Working directory"
                                        }
                                    }
                                }
                            },
                            "retry_failed_job": {
                                "description": "Retry a failed CI job or workflow",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "run_id": {
                                            "type": "integer",
                                            "description": "Workflow run ID to retry"
                                        },
                                        "job_id": {
                                            "type": "integer",
                                            "description": "Specific job ID to retry"
                                        },
                                        "failed_only": {
                                            "type": "boolean",
                                            "default": True,
                                            "description": "Only retry failed jobs"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "default": ".",
                                            "description": "Working directory"
                                        }
                                    }
                                }
                            },
                            "list_workflows": {
                                "description": "List recent workflow runs",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {
                                            "type": "string",
                                            "enum": ["success", "failure", "pending", "in_progress", "cancelled"],
                                            "description": "Filter by status"
                                        },
                                        "branch": {
                                            "type": "string",
                                            "description": "Filter by branch"
                                        },
                                        "workflow": {
                                            "type": "string",
                                            "description": "Filter by workflow name"
                                        },
                                        "limit": {
                                            "type": "integer",
                                            "default": 10,
                                            "description": "Max runs to return"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "default": ".",
                                            "description": "Working directory"
                                        }
                                    }
                                }
                            },
                            "cancel_workflow": {
                                "description": "Cancel a running workflow",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "run_id": {
                                            "type": "integer",
                                            "description": "Workflow run ID to cancel"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "default": ".",
                                            "description": "Working directory"
                                        }
                                    },
                                    "required": ["run_id"]
                                }
                            },
                            "get_workflow_artifacts": {
                                "description": "List or download workflow artifacts",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "run_id": {
                                            "type": "integer",
                                            "description": "Workflow run ID"
                                        },
                                        "download": {
                                            "type": "boolean",
                                            "default": False,
                                            "description": "Download artifacts"
                                        },
                                        "artifact_name": {
                                            "type": "string",
                                            "description": "Specific artifact to download"
                                        },
                                        "cwd": {
                                            "type": "string",
                                            "default": ".",
                                            "description": "Working directory"
                                        }
                                    },
                                    "required": ["run_id"]
                                }
                            }
                        }
                    },
                    "serverInfo": {"name": "cicd-helper-server", "version": "1.0.0"}
                }
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

                if tool_name == "check_ci_status":
                    result = check_ci_status(**arguments)
                elif tool_name == "get_failed_logs":
                    result = get_failed_logs(**arguments)
                elif tool_name == "retry_failed_job":
                    result = retry_failed_job(**arguments)
                elif tool_name == "list_workflows":
                    result = list_workflows(**arguments)
                elif tool_name == "cancel_workflow":
                    result = cancel_workflow(**arguments)
                elif tool_name == "get_workflow_artifacts":
                    result = get_workflow_artifacts(**arguments)
                else:
                    result = {"success": False, "error": f"Unknown tool: {tool_name}"}

                print(
                    json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
                        }
                    )
                )
        except Exception as e:
            print(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {"code": -32603, "message": str(e)}
                    }
                )
            )


if __name__ == "__main__":
    main()
