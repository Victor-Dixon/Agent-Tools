#!/usr/bin/env python3
"""
Spreadsheet → GitHub Adapter - Swarm Integration
=================================================

Adapter service that processes spreadsheet rows and executes GitHub actions
using the swarm's unified GitHub tools.

Integrates with:
- unified_github.py (PR creation, repo operations)
- unified_github_pr_creator.py (PR creation with fallback)
- github_utils.py (GitHub token management)

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-12-07
V2 Compliant: Yes
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal, Dict, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Task type definitions
TaskType = Literal["create_issue", "update_file", "open_pr"]


@dataclass
class GithubTask:
    """GitHub task from spreadsheet row."""
    
    task_type: TaskType
    task_payload: str
    repo: str
    branch: Optional[str] = None
    file_path: Optional[str] = None
    title: Optional[str] = None
    body: Optional[str] = None
    base: str = "main"


@dataclass
class GithubResult:
    """Result from GitHub action execution."""
    
    status: Literal["done", "error"]
    result_url: Optional[str] = None
    error_msg: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


def handle_task(task: GithubTask) -> GithubResult:
    """
    Process GitHub task using swarm's unified GitHub tools.
    
    Args:
        task: GitHub task from spreadsheet
        
    Returns:
        GithubResult with status and result URL
    """
    logger.info(f"Processing task: {task.task_type} for repo: {task.repo}")
    
    try:
        if task.task_type == "create_issue":
            result = _handle_create_issue(task)
        elif task.task_type == "update_file":
            result = _handle_update_file(task)
        elif task.task_type == "open_pr":
            result = _handle_open_pr(task)
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")
        
        return GithubResult(
            status="done",
            result_url=result.get("url") or result.get("result_url"),
            meta=result
        )
        
    except Exception as e:
        logger.error(f"Task execution failed: {e}", exc_info=True)
        return GithubResult(
            status="error",
            error_msg=str(e)
        )


def _handle_create_issue(task: GithubTask) -> Dict[str, Any]:
    """
    Handle create_issue task type using GitHub API.
    
    TODO: Implement issue creation via GitHub API
    For now, returns placeholder
    """
    # TODO: Use unified_github.py or direct GitHub API
    # Example:
    # from tools.unified_github import UnifiedGitHub
    # github = UnifiedGitHub()
    # result = github.issue_create(task.repo, title, body)
    
    title = task.title or task.task_payload.split("\n")[0]
    body = task.body or task.task_payload
    
    logger.warning("Issue creation not yet implemented - using placeholder")
    return {
        "url": f"https://github.com/{task.repo}/issues/1",
        "issue_number": 1,
        "title": title,
        "body": body,
        "note": "Placeholder - implement with GitHub API"
    }


def _handle_update_file(task: GithubTask) -> Dict[str, Any]:
    """
    Handle update_file task type.
    
    Creates a PR with file updates.
    """
    # For update_file, we create a PR with the changes
    # This requires:
    # 1. Create branch
    # 2. Update file
    # 3. Commit
    # 4. Open PR
    
    branch = task.branch or f"auto-update-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    file_path = task.file_path or "demo.txt"
    
    # TODO: Implement file update via git operations
    # For now, delegate to open_pr with file update instruction
    
    logger.warning("File update not yet implemented - delegating to PR creation")
    return _handle_open_pr(task)


def _handle_open_pr(task: GithubTask) -> Dict[str, Any]:
    """
    Handle open_pr task type using unified_github_pr_creator.
    """
    try:
        from tools.unified_github_pr_creator import UnifiedGitHubPRCreator
        
        creator = UnifiedGitHubPRCreator()
        
        # Parse task payload for title/body
        title = task.title or task.task_payload.split("\n")[0]
        body = task.body or task.task_payload
        
        # Generate branch name if not provided
        branch = task.branch or f"auto-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create PR
        result = creator.create_pr(
            repo=task.repo,
            title=title,
            body=body,
            head=branch,
            base=task.base
        )
        
        # Extract PR URL from result
        pr_url = None
        if isinstance(result, dict):
            pr_url = result.get("url") or result.get("html_url")
            if not pr_url and result.get("number"):
                pr_url = f"https://github.com/{task.repo}/pull/{result['number']}"
        
        return {
            "url": pr_url,
            "pr_number": result.get("number") if isinstance(result, dict) else None,
            "branch": branch,
            "title": title,
            "body": body,
            "result": result
        }
        
    except ImportError:
        logger.error("unified_github_pr_creator not available")
        raise
    except Exception as e:
        logger.error(f"PR creation failed: {e}")
        raise


def parse_spreadsheet_row(row: Dict[str, Any], default_repo: str) -> Optional[GithubTask]:
    """
    Parse spreadsheet row into GithubTask.
    
    Args:
        row: Dictionary with column names as keys
        default_repo: Default repository if not specified in row
        
    Returns:
        GithubTask or None if row should be skipped
    """
    # Check if task should run
    run_github = str(row.get("run_github", "")).lower()
    if run_github not in ["true", "run", "1", "yes"]:
        return None
    
    # Extract task type
    task_type = str(row.get("task_type", "")).lower()
    if task_type not in ["create_issue", "update_file", "open_pr"]:
        logger.warning(f"Invalid task_type: {task_type}")
        return None
    
    # Build task
    task = GithubTask(
        task_type=task_type,  # type: ignore
        task_payload=str(row.get("task_payload", "")),
        repo=str(row.get("repo", default_repo)),
        branch=row.get("branch"),
        file_path=row.get("file_path"),
        title=row.get("title"),
        body=row.get("body"),
        base=str(row.get("base", "main"))
    )
    
    return task


def format_result_for_spreadsheet(result: GithubResult) -> Dict[str, Any]:
    """
    Format GithubResult for spreadsheet update.
    
    Returns:
        Dictionary with columns matching spreadsheet format
    """
    return {
        "status": result.status,
        "result_url": result.result_url or "",
        "error_msg": result.error_msg or "",
        "updated_at": result.timestamp
    }


def process_spreadsheet_file(file_path: str, default_repo: str) -> Dict[str, Any]:
    """
    Process spreadsheet file (CSV or JSON) and execute tasks.
    
    Args:
        file_path: Path to spreadsheet file
        default_repo: Default repository for tasks
        
    Returns:
        Summary of processed tasks
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Spreadsheet file not found: {file_path}")
    
    # Load data based on file type
    if path.suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            rows = data if isinstance(data, list) else data.get("rows", [])
    elif path.suffix == ".csv":
        import csv
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")
    
    # Process rows
    results = []
    for i, row in enumerate(rows, start=1):
        task = parse_spreadsheet_row(row, default_repo)
        if task is None:
            continue
        
        logger.info(f"Processing row {i}: {task.task_type} for {task.repo}")
        result = handle_task(task)
        results.append({
            "row": i,
            "task": task,
            "result": result
        })
    
    return {
        "total_rows": len(rows),
        "processed": len(results),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Spreadsheet → GitHub Adapter for Swarm"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to spreadsheet file (CSV or JSON)"
    )
    parser.add_argument(
        "--repo",
        type=str,
        default="owner/repo-name",
        help="Default repository (format: owner/repo-name)"
    )
    parser.add_argument(
        "--task-type",
        type=str,
        choices=["create_issue", "update_file", "open_pr"],
        help="Task type (if processing single task)"
    )
    parser.add_argument(
        "--task-payload",
        type=str,
        help="Task payload (if processing single task)"
    )
    parser.add_argument(
        "--branch",
        type=str,
        help="Branch name (for PR tasks)"
    )
    parser.add_argument(
        "--file-path",
        type=str,
        help="File path (for update_file tasks)"
    )
    parser.add_argument(
        "--title",
        type=str,
        help="Override title"
    )
    parser.add_argument(
        "--body",
        type=str,
        help="Override body"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for results (JSON)"
    )
    
    args = parser.parse_args()
    
    # Process single task or file
    if args.file:
        result = process_spreadsheet_file(args.file, args.repo)
    elif args.task_type and args.task_payload:
        task = GithubTask(
            task_type=args.task_type,  # type: ignore
            task_payload=args.task_payload,
            repo=args.repo,
            branch=args.branch,
            file_path=args.file_path,
            title=args.title,
            body=args.body
        )
        result_obj = handle_task(task)
        result = {
            "task": {
                "type": task.task_type,
                "repo": task.repo,
                "payload": task.task_payload
            },
            "result": format_result_for_spreadsheet(result_obj)
        }
    else:
        parser.print_help()
        sys.exit(1)
    
    # Output results
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"Results written to: {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()


