#!/usr/bin/env python3
"""
Unified GitHub PR Creator
=========================

Combines GitHub CLI (GraphQL) and REST API methods for PR creation.
Automatically falls back to REST API when GraphQL is rate-limited.

Author: Agent-7 (Web Development Specialist)
Date: 2025-01-27
Priority: HIGH
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# SSOT imports
from src.core.utils.github_utils import get_github_token
from src.core.config.timeout_constants import TimeoutConstants

# Rate limit checking (simplified - tools may be archived)
def check_gh_cli_rate_limit() -> Dict[str, Any]:
    """Check GitHub CLI rate limit."""
    try:
        result = subprocess.run(
            ["gh", "api", "rate_limit"],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_QUICK
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            core = data.get("resources", {}).get("core", {})
            return {
                "status": "✅ Available",
                "remaining": core.get("remaining", 0),
                "limit": core.get("limit", 0),
            }
    except Exception:
        pass
    return {"status": "❌ Not available", "remaining": 0, "limit": 0}

def check_rest_api_rate_limit(token: Optional[str]) -> Dict[str, Any]:
    """Check REST API rate limit."""
    if not token or not REQUESTS_AVAILABLE:
        return {"status": "❌ Not available", "remaining": 0, "limit": 0}
    
    try:
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        response = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=TimeoutConstants.HTTP_QUICK)
        if response.status_code == 200:
            data = response.json()
            core = data.get("resources", {}).get("core", {})
            return {
                "status": "✅ Available",
                "core": {
                    "remaining": core.get("remaining", 0),
                    "limit": core.get("limit", 0),
                }
            }
    except Exception:
        pass
    return {"status": "❌ Not available", "core": {"remaining": 0, "limit": 0}}

def check_graphql_api_rate_limit(token: Optional[str]) -> Dict[str, Any]:
    """Check GraphQL API rate limit."""
    if not token or not REQUESTS_AVAILABLE:
        return {"status": "❌ Not available", "remaining": 0, "limit": 0}
    
    try:
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        response = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=TimeoutConstants.HTTP_QUICK)
        if response.status_code == 200:
            data = response.json()
            graphql = data.get("resources", {}).get("graphql", {})
            return {
                "status": "✅ Available",
                "remaining": graphql.get("remaining", 0),
                "limit": graphql.get("limit", 0),
            }
    except Exception:
        pass
    return {"status": "❌ Not available", "remaining": 0, "limit": 0}


class UnifiedGitHubPRCreator:
    """Unified PR creator with automatic fallback between methods."""
    
    def __init__(self, owner: str = "Dadudekc"):
        """Initialize PR creator."""
        self.owner = owner
        self.token = get_github_token(project_root)
    
    def check_available_methods(self) -> Dict[str, Dict]:
        """Check which methods are available and their rate limits."""
        methods = {}
        
        # Check GitHub CLI (GraphQL)
        gh_result = check_gh_cli_rate_limit()
        methods["gh_cli"] = {
            "available": gh_result.get("status") == "✅ Available",
            "remaining": gh_result.get("remaining", 0),
            "limit": gh_result.get("limit", 0),
            "result": gh_result
        }
        
        # Check REST API
        rest_result = check_rest_api_rate_limit(self.token)
        methods["rest_api"] = {
            "available": rest_result.get("status") == "✅ Available",
            "remaining": rest_result.get("core", {}).get("remaining", 0),
            "limit": rest_result.get("core", {}).get("limit", 0),
            "result": rest_result
        }
        
        # Check GraphQL directly
        graphql_result = check_graphql_api_rate_limit(self.token)
        methods["graphql"] = {
            "available": graphql_result.get("status") == "✅ Available",
            "remaining": graphql_result.get("remaining", 0),
            "limit": graphql_result.get("limit", 0),
            "result": graphql_result
        }
        
        return methods
    
    def create_pr_via_gh_cli(
        self,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> Dict[str, Any]:
        """Create PR using GitHub CLI (GraphQL)."""
        repo_spec = f"{self.owner}/{repo}"
        
        # Try both main and master branches
        for base_branch in [base, "main", "master"]:
            for head_branch in ["main", "master"]:
                cmd = [
                    "gh", "pr", "create",
                    "--repo", repo_spec,
                    "--base", base_branch,
                    "--head", f"{self.owner}/{head}:{head_branch}" if ":" not in head else head,
                    "--title", title,
                    "--body", body
                ]
                
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=TimeoutConstants.HTTP_MEDIUM,
                        check=False
                    )
                    
                    if result.returncode == 0:
                        pr_url = result.stdout.strip()
                        return {
                            "success": True,
                            "method": "gh_cli",
                            "pr_url": pr_url,
                            "base": base_branch,
                            "head": head_branch
                        }
                    elif "rate limit" in result.stderr.lower() or "429" in result.stderr:
                        return {
                            "success": False,
                            "method": "gh_cli",
                            "error": "Rate limit exceeded",
                            "error_details": result.stderr
                        }
                except subprocess.TimeoutExpired:
                    continue
                except Exception as e:
                    continue
        
        return {
            "success": False,
            "method": "gh_cli",
            "error": "All branch combinations failed"
        }
    
    def create_pr_via_rest_api(
        self,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> Dict[str, Any]:
        """Create PR using REST API."""
        if not self.token:
            return {
                "success": False,
                "method": "rest_api",
                "error": "GitHub token required for REST API"
            }
        
        # Format head: owner:repo:branch or repo:branch
        if ":" not in head:
            head_formatted = f"{self.owner}/{head}:main"
        elif head.count(":") == 1:
            # Format: repo:branch -> owner:repo:branch
            parts = head.split(":")
            head_formatted = f"{self.owner}/{parts[0]}:{parts[1]}"
        else:
            head_formatted = head
        
        url = f"https://api.github.com/repos/{self.owner}/{repo}/pulls"
        headers = {
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
            response = requests.post(url, headers=headers, json=payload, timeout=TimeoutConstants.HTTP_DEFAULT)
            
            if response.status_code == 201:
                pr_data = response.json()
                return {
                    "success": True,
                    "method": "rest_api",
                    "pr_url": pr_data.get("html_url"),
                    "pr_number": pr_data.get("number"),
                    "data": pr_data
                }
            elif response.status_code == 422:
                error_data = response.json()
                return {
                    "success": False,
                    "method": "rest_api",
                    "error": error_data.get("message", "Validation failed"),
                    "errors": error_data.get("errors", [])
                }
            elif response.status_code == 403:
                # Rate limit or forbidden
                if "rate limit" in response.text.lower():
                    return {
                        "success": False,
                        "method": "rest_api",
                        "error": "Rate limit exceeded",
                        "error_details": response.text
                    }
                return {
                    "success": False,
                    "method": "rest_api",
                    "error": f"Forbidden: {response.text[:200]}"
                }
            else:
                return {
                    "success": False,
                    "method": "rest_api",
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "method": "rest_api",
                "error": f"Request failed: {str(e)}"
            }
    
    def create_pr_unified(
        self,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        prefer_method: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create PR using best available method with automatic fallback.
        
        Args:
            repo: Target repository name
            title: PR title
            body: PR description
            head: Source branch (format: "repo:branch" or "owner:repo:branch")
            base: Target branch (default: "main")
            prefer_method: Preferred method ("gh_cli" or "rest_api"), None = auto
        
        Returns:
            Result dictionary with success status and PR details
        """
        # Check available methods
        methods = self.check_available_methods()
        
        # Determine method order based on preferences and availability
        method_order = []
        
        if prefer_method == "rest_api":
            method_order = ["rest_api", "gh_cli"]
        elif prefer_method == "gh_cli":
            method_order = ["gh_cli", "rest_api"]
        else:
            # Auto: prefer method with more remaining requests
            gh_remaining = methods.get("gh_cli", {}).get("remaining", 0)
            rest_remaining = methods.get("rest_api", {}).get("remaining", 0)
            
            if gh_remaining > rest_remaining:
                method_order = ["gh_cli", "rest_api"]
            else:
                method_order = ["rest_api", "gh_cli"]
        
        # Try each method in order
        for method in method_order:
            method_info = methods.get(method, {})
            
            # Skip if not available or rate limited
            if not method_info.get("available", False):
                continue
            
            if method_info.get("remaining", 0) == 0:
                continue
            
            # Try creating PR with this method
            if method == "gh_cli":
                result = self.create_pr_via_gh_cli(repo, title, body, head, base)
            elif method == "rest_api":
                result = self.create_pr_via_rest_api(repo, title, body, head, base)
            else:
                continue
            
            # If successful, return result
            if result.get("success"):
                print(f"✅ PR created using {method}")
                return result
            
            # If rate limited, try next method
            if "rate limit" in result.get("error", "").lower():
                print(f"⚠️ {method} rate limited, trying next method...")
                continue
            
            # For other errors, still try next method (might be branch issue)
            print(f"⚠️ {method} failed: {result.get('error')}, trying next method...")
            continue
        
        # All methods failed
        return {
            "success": False,
            "error": "All PR creation methods failed",
            "methods_tried": method_order,
            "method_status": methods
        }


def main():
    """CLI entry point."""
    if len(sys.argv) < 6:
        print("Usage: python tools/unified_github_pr_creator.py <repo> <title> <head> <base> <body_file> [method]")
        print("\nExample:")
        print("  python tools/unified_github_pr_creator.py FocusForge 'Merge focusforge' 'focusforge:main' 'main' body.txt")
        print("\nMethods: 'gh_cli', 'rest_api', or 'auto' (default)")
        sys.exit(1)
    
    repo = sys.argv[1]
    title = sys.argv[2]
    head = sys.argv[3]
    base = sys.argv[4]
    body_file = Path(sys.argv[5])
    prefer_method = sys.argv[6] if len(sys.argv) > 6 else None
    
    if prefer_method == "auto":
        prefer_method = None
    
    if not body_file.exists():
        body = f"Repository consolidation merge: {head}"
    else:
        body = body_file.read_text(encoding="utf-8")
    
    creator = UnifiedGitHubPRCreator()
    
    # Check available methods
    print("🔍 Checking available methods...")
    methods = creator.check_available_methods()
    for method_name, method_info in methods.items():
        if method_info.get("available"):
            remaining = method_info.get("remaining", 0)
            limit = method_info.get("limit", 0)
            print(f"   ✅ {method_name}: {remaining}/{limit} remaining")
        else:
            print(f"   ❌ {method_name}: Not available")
    
    print(f"\n🚀 Creating PR: {head} → {repo} (base: {base})")
    result = creator.create_pr_unified(repo, title, body, head, base, prefer_method)
    
    if result.get("success"):
        pr_url = result.get("pr_url") or result.get("data", {}).get("html_url")
        method_used = result.get("method", "unknown")
        print(f"\n✅ SUCCESS - PR created using {method_used}")
        print(f"   PR URL: {pr_url}")
        if "pr_number" in result:
            print(f"   PR #: {result['pr_number']}")
        sys.exit(0)
    else:
        print(f"\n❌ FAILED - All methods exhausted")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        if "methods_tried" in result:
            print(f"   Methods tried: {', '.join(result['methods_tried'])}")
        sys.exit(1)


if __name__ == "__main__":
    main()

