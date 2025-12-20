#!/usr/bin/env python3
"""
Enhanced Unified GitHub Operations
===================================

Auto-switches between REST API and GraphQL API with intelligent queuing.
Handles rate limits gracefully by queuing operations when both APIs exhausted.

Features:
- Auto-selects best API (REST vs GraphQL) based on remaining rate limits
- Queues operations when rate-limited
- Automatic retry when rate limits reset
- Supports PR creation, merging, and status checks

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-12-10
Priority: HIGH
V2 Compliant: Yes
"""

import os
import sys
import subprocess
import requests
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from enum import Enum

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Check for requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests library not available. Install with: pip install requests")

# SSOT imports
try:
    from src.core.utils.github_utils import get_github_token, create_github_pr_headers
    from src.core.config.timeout_constants import TimeoutConstants
    from src.core.deferred_push_queue import DeferredPushQueue, get_deferred_push_queue, PushStatus
except ImportError:
    # Fallback imports
    TimeoutConstants = type('TimeoutConstants', (), {
        'HTTP_QUICK': 10,
        'HTTP_DEFAULT': 30,
        'HTTP_MEDIUM': 60
    })()
    get_github_token = lambda root: os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    create_github_pr_headers = lambda token: {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    DeferredPushQueue = None
    get_deferred_push_queue = None


class OperationType(Enum):
    """Types of GitHub operations."""
    CREATE_PR = "create_pr"
    MERGE_PR = "merge_pr"
    CHECK_PR = "check_pr"
    UPDATE_PR = "update_pr"


class RateLimitStatus:
    """Rate limit status for an API."""
    
    def __init__(self, api_name: str, remaining: int = 0, limit: int = 0, reset_time: int = 0):
        self.api_name = api_name
        self.remaining = remaining
        self.limit = limit
        self.reset_time = reset_time
        self.available = remaining > 0
    
    def reset_in_seconds(self) -> int:
        """Calculate seconds until reset."""
        if self.reset_time > 0:
            return max(0, int(self.reset_time - time.time()))
        return 0
    
    def __repr__(self):
        return f"{self.api_name}: {self.remaining}/{self.limit} (reset in {self.reset_in_seconds()}s)"


class EnhancedUnifiedGitHub:
    """
    Enhanced unified GitHub operations with auto-switching and queuing.
    """
    
    def __init__(self, owner: str = "Dadudekc"):
        """Initialize unified GitHub client."""
        self.owner = owner
        self.token = get_github_token(project_root) if 'project_root' in globals() else os.getenv("GITHUB_TOKEN")
        self.queue = get_deferred_push_queue() if get_deferred_push_queue else None
    
    def check_rate_limits(self) -> Dict[str, RateLimitStatus]:
        """
        Check rate limits for all APIs.
        
        Returns:
            Dictionary mapping API names to RateLimitStatus
        """
        limits = {}
        
        # Check REST API
        rest_limit = self._check_rest_api_rate_limit()
        limits["rest"] = rest_limit
        
        # Check GraphQL API (via rate_limit endpoint)
        graphql_limit = self._check_graphql_api_rate_limit()
        limits["graphql"] = graphql_limit
        
        # Check GitHub CLI (which uses GraphQL)
        gh_cli_limit = self._check_gh_cli_rate_limit()
        limits["gh_cli"] = gh_cli_limit
        
        return limits
    
    def _check_rest_api_rate_limit(self) -> RateLimitStatus:
        """Check REST API rate limit."""
        if not self.token or not REQUESTS_AVAILABLE:
            return RateLimitStatus("rest", 0, 0, 0)
        
        try:
            headers = create_github_pr_headers(self.token) if create_github_pr_headers else {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = requests.get(
                "https://api.github.com/rate_limit",
                headers=headers,
                timeout=getattr(TimeoutConstants, 'HTTP_QUICK', 10)
            )
            if response.status_code == 200:
                data = response.json()
                core = data.get("resources", {}).get("core", {})
                return RateLimitStatus(
                    "rest",
                    core.get("remaining", 0),
                    core.get("limit", 0),
                    core.get("reset", 0)
                )
        except Exception:
            pass
        
        return RateLimitStatus("rest", 0, 0, 0)
    
    def _check_graphql_api_rate_limit(self) -> RateLimitStatus:
        """Check GraphQL API rate limit."""
        if not self.token:
            return RateLimitStatus("graphql", 0, 0, 0)
        
        try:
            headers = create_github_pr_headers(self.token) if create_github_pr_headers else {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = requests.get(
                "https://api.github.com/rate_limit",
                headers=headers,
                timeout=getattr(TimeoutConstants, 'HTTP_QUICK', 10)
            )
            if response.status_code == 200:
                data = response.json()
                graphql = data.get("resources", {}).get("graphql", {})
                return RateLimitStatus(
                    "graphql",
                    graphql.get("remaining", 0),
                    graphql.get("limit", 0),
                    graphql.get("reset", 0)
                )
        except Exception:
            pass
        
        return RateLimitStatus("graphql", 0, 0, 0)
    
    def _check_gh_cli_rate_limit(self) -> RateLimitStatus:
        """Check GitHub CLI rate limit (uses GraphQL)."""
        try:
            result = subprocess.run(
                ["gh", "api", "rate_limit"],
                capture_output=True,
                text=True,
                timeout=getattr(TimeoutConstants, 'HTTP_QUICK', 10)
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                core = data.get("resources", {}).get("core", {})
                graphql = data.get("resources", {}).get("graphql", {})
                # Use GraphQL limit (gh CLI uses GraphQL)
                return RateLimitStatus(
                    "gh_cli",
                    graphql.get("remaining", 0),
                    graphql.get("limit", 0),
                    graphql.get("reset", 0)
                )
        except Exception:
            pass
        
        return RateLimitStatus("gh_cli", 0, 0, 0)
    
    def select_best_api(self, operation_type: OperationType) -> str:
        """
        Select best API for operation based on rate limits.
        
        Args:
            operation_type: Type of operation to perform
        
        Returns:
            API name to use ("rest", "graphql", or "gh_cli")
        """
        limits = self.check_rate_limits()
        
        # Prefer REST API for most operations (more reliable)
        # Prefer GraphQL/CLI for complex queries
        
        # Get available APIs
        available = {
            name: limit for name, limit in limits.items()
            if limit.available and limit.remaining > 10  # Need buffer
        }
        
        if not available:
            # All exhausted - return best option based on reset time
            best = min(limits.values(), key=lambda x: x.reset_time if x.reset_time > 0 else float('inf'))
            return best.api_name
        
        # For PR creation/merging: prefer REST (more reliable)
        if operation_type in [OperationType.CREATE_PR, OperationType.MERGE_PR]:
            if "rest" in available:
                return "rest"
            if "gh_cli" in available:
                return "gh_cli"
            return list(available.keys())[0]
        
        # For queries: prefer GraphQL (more efficient)
        if operation_type == OperationType.CHECK_PR:
            if "gh_cli" in available:
                return "gh_cli"
            if "graphql" in available:
                return "graphql"
            if "rest" in available:
                return "rest"
        
        # Default: use API with most remaining
        best = max(available.values(), key=lambda x: x.remaining)
        return best.api_name
    
    def create_pr(
        self,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        queue_on_failure: bool = True
    ) -> Dict[str, Any]:
        """
        Create PR with auto-switching and queuing.
        
        Args:
            repo: Target repository
            title: PR title
            body: PR description
            head: Source branch
            base: Target branch
            queue_on_failure: Queue operation if rate-limited
        
        Returns:
            Result dictionary
        """
        # Select best API
        selected_api = self.select_best_api(OperationType.CREATE_PR)
        limits = self.check_rate_limits()
        selected_limit = limits.get(selected_api)
        
        # Check if we can proceed
        if not selected_limit or not selected_limit.available:
            if queue_on_failure and self.queue:
                # Queue operation
                entry_id = self._queue_operation(
                    OperationType.CREATE_PR,
                    {
                        "repo": repo,
                        "title": title,
                        "body": body,
                        "head": head,
                        "base": base
                    },
                    reason="rate_limit_exhausted"
                )
                return {
                    "success": False,
                    "queued": True,
                    "queue_id": entry_id,
                    "error": f"All APIs rate-limited. Queued for retry. Reset in {selected_limit.reset_in_seconds()}s"
                }
            return {
                "success": False,
                "error": f"All APIs rate-limited. Reset in {selected_limit.reset_in_seconds()}s"
            }
        
        # Try selected API
        if selected_api == "rest":
            result = self._create_pr_rest(repo, title, body, head, base)
        elif selected_api in ["gh_cli", "graphql"]:
            result = self._create_pr_gh_cli(repo, title, body, head, base)
        else:
            result = {"success": False, "error": f"Unknown API: {selected_api}"}
        
        # If rate-limited, try fallback
        if not result.get("success") and "rate limit" in result.get("error", "").lower():
            fallback_api = "rest" if selected_api != "rest" else "gh_cli"
            if limits.get(fallback_api) and limits[fallback_api].available:
                print(f"⚠️ {selected_api} rate-limited, trying {fallback_api}...")
                if fallback_api == "rest":
                    result = self._create_pr_rest(repo, title, body, head, base)
                else:
                    result = self._create_pr_gh_cli(repo, title, body, head, base)
        
        # If still failed and should queue
        if not result.get("success") and queue_on_failure and self.queue:
            if "rate limit" in result.get("error", "").lower():
                entry_id = self._queue_operation(
                    OperationType.CREATE_PR,
                    {
                        "repo": repo,
                        "title": title,
                        "body": body,
                        "head": head,
                        "base": base
                    },
                    reason="rate_limit_after_attempt"
                )
                result["queued"] = True
                result["queue_id"] = entry_id
        
        return result
    
    def merge_pr(
        self,
        repo: str,
        pr_number: int,
        merge_method: str = "merge",
        queue_on_failure: bool = True
    ) -> Dict[str, Any]:
        """
        Merge PR with auto-switching and queuing.
        
        Args:
            repo: Repository name
            pr_number: PR number
            merge_method: Merge method (merge, squash, rebase)
            queue_on_failure: Queue operation if rate-limited
        
        Returns:
            Result dictionary
        """
        # Select best API
        selected_api = self.select_best_api(OperationType.MERGE_PR)
        limits = self.check_rate_limits()
        selected_limit = limits.get(selected_api)
        
        # Check if we can proceed
        if not selected_limit or not selected_limit.available:
            if queue_on_failure and self.queue:
                entry_id = self._queue_operation(
                    OperationType.MERGE_PR,
                    {
                        "repo": repo,
                        "pr_number": pr_number,
                        "merge_method": merge_method
                    },
                    reason="rate_limit_exhausted"
                )
                return {
                    "success": False,
                    "queued": True,
                    "queue_id": entry_id,
                    "error": f"All APIs rate-limited. Queued for retry."
                }
            return {
                "success": False,
                "error": f"All APIs rate-limited. Reset in {selected_limit.reset_in_seconds()}s"
            }
        
        # Try REST API (most reliable for merging)
        if selected_api == "rest":
            result = self._merge_pr_rest(repo, pr_number, merge_method)
        else:
            # Fallback to REST (merging is REST-only operation)
            result = self._merge_pr_rest(repo, pr_number, merge_method)
        
        # If rate-limited, queue
        if not result.get("success") and "rate limit" in result.get("error", "").lower():
            if queue_on_failure and self.queue:
                entry_id = self._queue_operation(
                    OperationType.MERGE_PR,
                    {
                        "repo": repo,
                        "pr_number": pr_number,
                        "merge_method": merge_method
                    },
                    reason="rate_limit_after_attempt"
                )
                result["queued"] = True
                result["queue_id"] = entry_id
        
        return result
    
    def _create_pr_rest(self, repo: str, title: str, body: str, head: str, base: str) -> Dict[str, Any]:
        """Create PR via REST API."""
        if not self.token:
            return {"success": False, "error": "GitHub token required"}
        
        # Format head branch
        if ":" not in head:
            head_formatted = f"{self.owner}/{head}:main"
        elif head.count(":") == 1:
            parts = head.split(":")
            head_formatted = f"{self.owner}/{parts[0]}:{parts[1]}"
        else:
            head_formatted = head
        
        url = f"https://api.github.com/repos/{self.owner}/{repo}/pulls"
        headers = create_github_pr_headers(self.token) if create_github_pr_headers else {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        payload = {
            "title": title,
            "body": body,
            "head": head_formatted,
            "base": base
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=getattr(TimeoutConstants, 'HTTP_DEFAULT', 30)
            )
            
            if response.status_code == 201:
                pr_data = response.json()
                return {
                    "success": True,
                    "method": "rest",
                    "pr_url": pr_data.get("html_url"),
                    "pr_number": pr_data.get("number"),
                    "data": pr_data
                }
            elif response.status_code == 422:
                error_data = response.json()
                return {
                    "success": False,
                    "method": "rest",
                    "error": error_data.get("message", "Validation failed"),
                    "errors": error_data.get("errors", [])
                }
            elif response.status_code == 403:
                if "rate limit" in response.text.lower():
                    return {
                        "success": False,
                        "method": "rest",
                        "error": "Rate limit exceeded"
                    }
                return {
                    "success": False,
                    "method": "rest",
                    "error": f"Forbidden: {response.text[:200]}"
                }
            else:
                return {
                    "success": False,
                    "method": "rest",
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
        except Exception as e:
            return {
                "success": False,
                "method": "rest",
                "error": f"Request failed: {str(e)}"
            }
    
    def _create_pr_gh_cli(self, repo: str, title: str, body: str, head: str, base: str) -> Dict[str, Any]:
        """Create PR via GitHub CLI (GraphQL)."""
        repo_spec = f"{self.owner}/{repo}"
        
        cmd = [
            "gh", "pr", "create",
            "--repo", repo_spec,
            "--base", base,
            "--head", head if ":" in head else f"{self.owner}/{head}:main",
            "--title", title,
            "--body", body
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=getattr(TimeoutConstants, 'HTTP_MEDIUM', 60),
                check=False
            )
            
            if result.returncode == 0:
                pr_url = result.stdout.strip()
                return {
                    "success": True,
                    "method": "gh_cli",
                    "pr_url": pr_url
                }
            elif "rate limit" in result.stderr.lower() or "429" in result.stderr:
                return {
                    "success": False,
                    "method": "gh_cli",
                    "error": "Rate limit exceeded",
                    "error_details": result.stderr
                }
            else:
                return {
                    "success": False,
                    "method": "gh_cli",
                    "error": result.stderr or "Unknown error"
                }
        except Exception as e:
            return {
                "success": False,
                "method": "gh_cli",
                "error": f"Command failed: {str(e)}"
            }
    
    def _merge_pr_rest(self, repo: str, pr_number: int, merge_method: str) -> Dict[str, Any]:
        """Merge PR via REST API."""
        if not self.token:
            return {"success": False, "error": "GitHub token required"}
        
        url = f"https://api.github.com/repos/{self.owner}/{repo}/pulls/{pr_number}/merge"
        headers = create_github_pr_headers(self.token) if create_github_pr_headers else {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        payload = {"merge_method": merge_method}
        
        try:
            response = requests.put(
                url,
                headers=headers,
                json=payload,
                timeout=getattr(TimeoutConstants, 'HTTP_DEFAULT', 30)
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "method": "rest",
                    "merged": result.get("merged", False),
                    "sha": result.get("sha")
                }
            elif response.status_code == 405:
                error_data = response.json()
                return {
                    "success": False,
                    "method": "rest",
                    "error": error_data.get("message", "PR cannot be merged")
                }
            elif response.status_code == 403:
                if "rate limit" in response.text.lower():
                    return {
                        "success": False,
                        "method": "rest",
                        "error": "Rate limit exceeded"
                    }
                return {
                    "success": False,
                    "method": "rest",
                    "error": f"Forbidden: {response.text[:200]}"
                }
            else:
                return {
                    "success": False,
                    "method": "rest",
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
        except Exception as e:
            return {
                "success": False,
                "method": "rest",
                "error": f"Request failed: {str(e)}"
            }
    
    def _queue_operation(
        self,
        operation_type: OperationType,
        params: Dict[str, Any],
        reason: str = "rate_limit"
    ) -> str:
        """
        Queue operation for later retry.
        
        Args:
            operation_type: Type of operation
            params: Operation parameters
            reason: Reason for queuing
        
        Returns:
            Queue entry ID
        """
        if not self.queue:
            raise ValueError("Queue not available - deferred_push_queue module required")
        
        # For PR operations, we need to store in queue
        # The queue expects repo and branch, so adapt based on operation type
        repo = params.get("repo", "unknown")
        branch = params.get("head", params.get("base", "main"))
        
        # Create metadata for queue entry
        metadata = {
            "action": operation_type.value,
            "params": params
        }
        
        return self.queue.enqueue_push(
            repo=repo,
            branch=branch,
            reason=reason,
            metadata=metadata
        )


def main():
    """CLI entry point for testing."""
    if len(sys.argv) < 2:
        print("Usage: python tools/enhanced_unified_github.py <command> [args...]")
        print("\nCommands:")
        print("  rate-limits  - Check current rate limits")
        print("  create-pr <repo> <title> <head> <base> <body>  - Create PR")
        print("  merge-pr <repo> <pr_number> [method]  - Merge PR")
        sys.exit(1)
    
    command = sys.argv[1]
    github = EnhancedUnifiedGitHub()
    
    if command == "rate-limits":
        print("🔍 Checking rate limits...\n")
        limits = github.check_rate_limits()
        for name, limit in limits.items():
            status = "✅" if limit.available else "❌"
            reset_str = f" (reset in {limit.reset_in_seconds()}s)" if limit.reset_time > 0 else ""
            print(f"{status} {name}: {limit.remaining}/{limit.limit} remaining{reset_str}")
        
        # Select best API for PR creation
        best = github.select_best_api(OperationType.CREATE_PR)
        print(f"\n🎯 Best API for PR creation: {best}")
    
    elif command == "create-pr":
        if len(sys.argv) < 7:
            print("Usage: create-pr <repo> <title> <head> <base> <body>")
            sys.exit(1)
        
        repo = sys.argv[2]
        title = sys.argv[3]
        head = sys.argv[4]
        base = sys.argv[5]
        body = sys.argv[6]
        
        print(f"🚀 Creating PR: {head} → {repo} (base: {base})")
        result = github.create_pr(repo, title, body, head, base)
        
        if result.get("success"):
            print(f"✅ PR created: {result.get('pr_url')}")
        elif result.get("queued"):
            print(f"⏳ Queued for retry: {result.get('queue_id')}")
            print(f"   {result.get('error')}")
        else:
            print(f"❌ Failed: {result.get('error')}")
    
    elif command == "merge-pr":
        if len(sys.argv) < 4:
            print("Usage: merge-pr <repo> <pr_number> [method]")
            sys.exit(1)
        
        repo = sys.argv[2]
        pr_number = int(sys.argv[3])
        merge_method = sys.argv[4] if len(sys.argv) > 4 else "merge"
        
        print(f"🚀 Merging PR #{pr_number} in {repo}")
        result = github.merge_pr(repo, pr_number, merge_method)
        
        if result.get("success"):
            print(f"✅ PR merged: {result.get('sha')}")
        elif result.get("queued"):
            print(f"⏳ Queued for retry: {result.get('queue_id')}")
        else:
            print(f"❌ Failed: {result.get('error')}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()

