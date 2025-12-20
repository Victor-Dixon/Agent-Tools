"""
GitHub PR Debugger - Diagnose and Fix PR Creation Issues
========================================================

Comprehensive debugging tool for GitHub PR creation problems.
Identifies authentication, rate limit, branch, and API issues.

Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-05
Priority: CRITICAL - PR System Debugging
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.config.timeout_constants import TimeoutConstants

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# SSOT imports
try:
    from src.core.utils.github_utils import get_github_token
    from src.core.config.timeout_constants import TimeoutConstants
    SSOT_AVAILABLE = True
except ImportError:
    SSOT_AVAILABLE = False
    TimeoutConstants = None


class GitHubPRDebugger:
    """Comprehensive GitHub PR debugging and fixing tool."""

    def __init__(self, owner: str = "Dadudekc"):
        """Initialize debugger."""
        self.owner = owner
        self.issues_found: List[Dict[str, Any]] = []
        self.fixes_applied: List[str] = []

    def check_github_cli_installed(self) -> Tuple[bool, str]:
        """Check if GitHub CLI is installed."""
        try:
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_QUICK
            )
            if result.returncode == 0:
                version = result.stdout.strip().split("\n")[0]
                return True, version
            return False, "GitHub CLI not found"
        except FileNotFoundError:
            return False, "GitHub CLI not installed"
        except Exception as e:
            return False, f"Error checking GitHub CLI: {e}"

    def check_github_cli_auth(self) -> Tuple[bool, Dict[str, Any]]:
        """Check GitHub CLI authentication status."""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_SHORT
            )
            
            auth_info = {
                "authenticated": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
            }
            
            if result.returncode == 0:
                # Parse auth status
                if "Logged in" in result.stdout:
                    auth_info["status"] = "authenticated"
                    # Extract account info
                    for line in result.stdout.split("\n"):
                        if "Logged in as" in line:
                            auth_info["account"] = line.split("Logged in as")[-1].strip()
                else:
                    auth_info["status"] = "not_authenticated"
            else:
                auth_info["status"] = "not_authenticated"
                if "not logged in" in result.stderr.lower():
                    auth_info["error"] = "Not logged in to GitHub CLI"
            
            return auth_info["authenticated"], auth_info
        except Exception as e:
            return False, {"error": str(e), "status": "error"}

    def check_github_token(self) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Check GitHub token availability and validity."""
        token_info = {
            "sources_checked": [],
            "token_found": False,
            "token_valid": False,
            "token_length": 0,
            "error": None,
        }
        
        # Check SSOT utility first
        if SSOT_AVAILABLE:
            token_info["sources_checked"].append("SSOT (github_utils)")
            try:
                token = get_github_token(project_root)
                if token:
                    token_info["token_found"] = True
                    token_info["token_length"] = len(token)
                    token_info["token_source"] = "SSOT"
                    # Validate token
                    if self._validate_token(token):
                        token_info["token_valid"] = True
                        return True, token, token_info
            except Exception as e:
                token_info["error"] = f"SSOT error: {e}"
        
        # Check environment variables
        token_info["sources_checked"].append("environment")
        token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        if token:
            token_info["token_found"] = True
            token_info["token_length"] = len(token)
            token_info["token_source"] = "environment"
            if self._validate_token(token):
                token_info["token_valid"] = True
                return True, token, token_info
        
        # Check .env file
        token_info["sources_checked"].append(".env file")
        env_file = project_root / ".env"
        if env_file.exists():
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GITHUB_TOKEN=") or line.startswith("GH_TOKEN="):
                            token = line.split("=", 1)[1].strip().strip('"').strip("'")
                            token_info["token_found"] = True
                            token_info["token_length"] = len(token)
                            token_info["token_source"] = ".env file"
                            if self._validate_token(token):
                                token_info["token_valid"] = True
                                return True, token, token_info
            except Exception as e:
                token_info["error"] = f".env read error: {e}"
        
        return False, None, token_info

    def _validate_token(self, token: str) -> bool:
        """Validate GitHub token by making a test API call."""
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = requests.get(
                "https://api.github.com/user",
                headers=headers,
                timeout=TimeoutConstants.HTTP_QUICK
            )
            return response.status_code == 200
        except Exception:
            return False

    def check_rate_limits(self, token: Optional[str] = None) -> Dict[str, Any]:
        """Check GitHub API rate limits."""
        rate_limits = {
            "rest_api": {"available": False, "remaining": 0, "limit": 0},
            "graphql": {"available": False, "remaining": 0, "limit": 0},
            "gh_cli": {"available": False, "remaining": 0, "limit": 0},
        }
        
        if not token:
            token = get_github_token(project_root) if SSOT_AVAILABLE else None
        
        # Check REST API rate limit
        if token and REQUESTS_AVAILABLE:
            try:
                headers = {
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                response = requests.get(
                    "https://api.github.com/rate_limit",
                    headers=headers,
                    timeout=TimeoutConstants.HTTP_QUICK
                )
                if response.status_code == 200:
                    data = response.json()
                    core = data.get("resources", {}).get("core", {})
                    rate_limits["rest_api"] = {
                        "available": True,
                        "remaining": core.get("remaining", 0),
                        "limit": core.get("limit", 0),
                        "reset_at": core.get("reset", 0),
                    }
            except Exception as e:
                rate_limits["rest_api"]["error"] = str(e)
        
        # Check GitHub CLI rate limit
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
                rate_limits["gh_cli"] = {
                    "available": True,
                    "remaining": core.get("remaining", 0),
                    "limit": core.get("limit", 0),
                    "reset_at": core.get("reset", 0),
                }
        except Exception as e:
            rate_limits["gh_cli"]["error"] = str(e)
        
        return rate_limits

    def check_branch_exists(
        self, repo: str, branch: str, token: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if branch exists in repository."""
        branch_info = {
            "exists": False,
            "sha": None,
            "error": None,
        }
        
        if not token:
            token = get_github_token(project_root) if SSOT_AVAILABLE else None
        
        if not token or not REQUESTS_AVAILABLE:
            branch_info["error"] = "Token or requests library not available"
            return False, branch_info
        
        try:
            url = f"https://api.github.com/repos/{self.owner}/{repo}/git/ref/heads/{branch}"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = requests.get(url, headers=headers, timeout=TimeoutConstants.HTTP_QUICK)
            
            if response.status_code == 200:
                data = response.json()
                branch_info["exists"] = True
                branch_info["sha"] = data.get("object", {}).get("sha")
                return True, branch_info
            elif response.status_code == 404:
                branch_info["error"] = "Branch not found"
                return False, branch_info
            else:
                branch_info["error"] = f"HTTP {response.status_code}: {response.text[:200]}"
                return False, branch_info
        except Exception as e:
            branch_info["error"] = str(e)
            return False, branch_info

    def check_pr_exists(
        self, repo: str, head: str, base: str = "main", token: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Check if PR already exists."""
        if not token:
            token = get_github_token(project_root) if SSOT_AVAILABLE else None
        
        if not token or not REQUESTS_AVAILABLE:
            return False, None
        
        try:
            url = f"https://api.github.com/repos/{self.owner}/{repo}/pulls"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            params = {
                "head": f"{self.owner}:{head}",
                "base": base,
                "state": "all"  # Check all states (open, closed, merged)
            }
            response = requests.get(url, headers=headers, params=params, timeout=TimeoutConstants.HTTP_QUICK)
            
            if response.status_code == 200:
                prs = response.json()
                if prs:
                    return True, prs[0]  # Return first matching PR
                return False, None
            else:
                return False, None
        except Exception:
            return False, None

    def diagnose_pr_creation_issue(
        self, repo: str, head: str, base: str = "main"
    ) -> Dict[str, Any]:
        """Comprehensive diagnosis of PR creation issues."""
        diagnosis = {
            "repo": repo,
            "head": head,
            "base": base,
            "timestamp": datetime.now().isoformat(),
            "issues": [],
            "fixes": [],
            "status": "unknown",
        }
        
        # 1. Check GitHub CLI
        cli_installed, cli_info = self.check_github_cli_installed()
        diagnosis["github_cli_installed"] = cli_installed
        if not cli_installed:
            diagnosis["issues"].append({
                "type": "github_cli_missing",
                "severity": "high",
                "message": f"GitHub CLI not installed: {cli_info}",
                "fix": "Install GitHub CLI: https://cli.github.com/",
            })
        
        # 2. Check GitHub CLI auth
        if cli_installed:
            cli_auth, auth_info = self.check_github_cli_auth()
            diagnosis["github_cli_auth"] = cli_auth
            if not cli_auth:
                diagnosis["issues"].append({
                    "type": "github_cli_not_authenticated",
                    "severity": "critical",
                    "message": "GitHub CLI not authenticated",
                    "fix": "Run: gh auth login",
                    "details": auth_info,
                })
        
        # 3. Check GitHub token
        token_available, token, token_info = self.check_github_token()
        diagnosis["github_token_available"] = token_available
        diagnosis["github_token_valid"] = token_info.get("token_valid", False)
        
        if not token_available:
            diagnosis["issues"].append({
                "type": "github_token_missing",
                "severity": "critical",
                "message": "GitHub token not found",
                "fix": "Set GITHUB_TOKEN in .env file or environment",
                "sources_checked": token_info.get("sources_checked", []),
            })
        elif not token_info.get("token_valid", False):
            diagnosis["issues"].append({
                "type": "github_token_invalid",
                "severity": "critical",
                "message": "GitHub token found but invalid",
                "fix": "Update GITHUB_TOKEN with valid token",
                "token_length": token_info.get("token_length", 0),
            })
        
        # 4. Check rate limits
        rate_limits = self.check_rate_limits(token)
        diagnosis["rate_limits"] = rate_limits
        
        if rate_limits["rest_api"].get("remaining", 0) == 0:
            diagnosis["issues"].append({
                "type": "rate_limit_exceeded",
                "severity": "high",
                "message": "REST API rate limit exceeded",
                "fix": "Wait for rate limit reset or use GitHub CLI",
                "reset_at": rate_limits["rest_api"].get("reset_at"),
            })
        
        # 5. Check branch exists
        branch_exists, branch_info = self.check_branch_exists(repo, head, token)
        diagnosis["branch_exists"] = branch_exists
        
        if not branch_exists:
            diagnosis["issues"].append({
                "type": "branch_not_found",
                "severity": "critical",
                "message": f"Branch '{head}' not found in {repo}",
                "fix": f"Create branch or check branch name: {head}",
                "error": branch_info.get("error"),
            })
        
        # 6. Check if PR already exists
        pr_exists, existing_pr = self.check_pr_exists(repo, head, base, token)
        diagnosis["pr_exists"] = pr_exists
        
        if pr_exists:
            diagnosis["issues"].append({
                "type": "pr_already_exists",
                "severity": "info",
                "message": f"PR already exists: {existing_pr.get('html_url')}",
                "fix": "Use existing PR or close it first",
                "pr_url": existing_pr.get("html_url"),
                "pr_number": existing_pr.get("number"),
                "pr_state": existing_pr.get("state"),
            })
        
        # Determine overall status
        critical_issues = [i for i in diagnosis["issues"] if i["severity"] == "critical"]
        high_issues = [i for i in diagnosis["issues"] if i["severity"] == "high"]
        
        if critical_issues:
            diagnosis["status"] = "blocked"
        elif high_issues:
            diagnosis["status"] = "degraded"
        elif diagnosis["issues"]:
            diagnosis["status"] = "warnings"
        else:
            diagnosis["status"] = "healthy"
        
        return diagnosis

    def print_diagnosis(self, diagnosis: Dict[str, Any]):
        """Print formatted diagnosis report."""
        print("\n" + "=" * 80)
        print("🔍 GITHUB PR CREATION DIAGNOSIS")
        print("=" * 80)
        
        print(f"\n📋 Repository: {diagnosis['repo']}")
        print(f"   Head Branch: {diagnosis['head']}")
        print(f"   Base Branch: {diagnosis['base']}")
        
        print(f"\n📊 Status: {diagnosis['status'].upper()}")
        
        # GitHub CLI
        print(f"\n🔧 GitHub CLI:")
        print(f"   Installed: {'✅' if diagnosis.get('github_cli_installed') else '❌'}")
        if diagnosis.get('github_cli_installed'):
            print(f"   Authenticated: {'✅' if diagnosis.get('github_cli_auth') else '❌'}")
        
        # GitHub Token
        print(f"\n🔑 GitHub Token:")
        print(f"   Available: {'✅' if diagnosis.get('github_token_available') else '❌'}")
        print(f"   Valid: {'✅' if diagnosis.get('github_token_valid') else '❌'}")
        
        # Rate Limits
        print(f"\n⏱️  Rate Limits:")
        rate_limits = diagnosis.get("rate_limits", {})
        rest = rate_limits.get("rest_api", {})
        if rest.get("available"):
            print(f"   REST API: {rest.get('remaining', 0)}/{rest.get('limit', 0)} remaining")
        else:
            print(f"   REST API: ❌ Not available")
        
        gh_cli = rate_limits.get("gh_cli", {})
        if gh_cli.get("available"):
            print(f"   GitHub CLI: {gh_cli.get('remaining', 0)}/{gh_cli.get('limit', 0)} remaining")
        else:
            print(f"   GitHub CLI: ❌ Not available")
        
        # Branch
        print(f"\n🌿 Branch Status:")
        print(f"   Branch Exists: {'✅' if diagnosis.get('branch_exists') else '❌'}")
        
        # PR Status
        print(f"\n📝 PR Status:")
        print(f"   PR Exists: {'✅' if diagnosis.get('pr_exists') else '❌'}")
        if diagnosis.get('pr_exists'):
            existing_pr = diagnosis.get('existing_pr')
            if existing_pr:
                print(f"   PR URL: {existing_pr.get('html_url')}")
                print(f"   PR State: {existing_pr.get('state')}")
        
        # Issues
        issues = diagnosis.get("issues", [])
        if issues:
            print(f"\n🚨 ISSUES FOUND ({len(issues)}):")
            for i, issue in enumerate(issues, 1):
                severity_icon = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "info": "ℹ️",
                }.get(issue["severity"], "⚪")
                
                print(f"\n   {i}. {severity_icon} {issue['type'].replace('_', ' ').title()}")
                print(f"      Message: {issue['message']}")
                print(f"      Fix: {issue.get('fix', 'N/A')}")
                if issue.get("details"):
                    print(f"      Details: {issue['details']}")
        else:
            print(f"\n✅ No issues found! PR creation should work.")
        
        print("\n" + "=" * 80)

    def generate_fix_script(self, diagnosis: Dict[str, Any]) -> str:
        """Generate fix script based on diagnosis."""
        fixes = []
        
        for issue in diagnosis.get("issues", []):
            if issue["severity"] in ["critical", "high"]:
                fix = issue.get("fix", "")
                if fix:
                    fixes.append(fix)
        
        if not fixes:
            return "# No fixes needed - system is healthy!"
        
        script = "# GitHub PR Fix Script\n"
        script += "# Generated by GitHub PR Debugger\n\n"
        
        for i, fix in enumerate(set(fixes), 1):
            script += f"# Fix {i}: {fix}\n"
        
        return script


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="GitHub PR Debugger - Diagnose and Fix PR Creation Issues"
    )
    parser.add_argument(
        "--repo",
        help="Repository name (e.g., Streamertools)",
    )
    parser.add_argument(
        "--head",
        help="Head branch name (e.g., merge-MeTuber-20251124)",
    )
    parser.add_argument(
        "--base",
        default="main",
        help="Base branch name (default: main)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix common issues (clears GH_TOKEN, checks auth)",
    )
    
    args = parser.parse_args()
    
    # Auto-fix mode
    if args.fix:
        print("🔧 Auto-fixing GitHub PR issues...\n")
        
        # Clear GH_TOKEN
        if "GH_TOKEN" in os.environ:
            del os.environ["GH_TOKEN"]
            print("✅ Cleared GH_TOKEN")
        
        # Check auth
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_QUICK
            )
            if result.returncode == 0 and "Logged in" in result.stdout:
                print("✅ GitHub CLI authenticated")
            else:
                print("❌ GitHub CLI not authenticated - run 'gh auth login'")
        except Exception:
            print("❌ GitHub CLI not available")
        
        # Check token
        from src.core.utils.github_utils import get_github_token
        project_root = Path(__file__).resolve().parent.parent
        token = get_github_token(project_root)
        if token:
            print("✅ GitHub token found")
        else:
            print("❌ GitHub token not found - add to .env")
        
        print("\n✅ Auto-fix complete!")
        return
    
    # Diagnosis mode
    if not args.repo or not args.head:
        parser.print_help()
        print("\n💡 Quick fix: python tools/github_pr_debugger.py --fix")
        sys.exit(1)
    
    debugger = GitHubPRDebugger()
    
    print("🔍 Diagnosing GitHub PR creation issues...")
    diagnosis = debugger.diagnose_pr_creation_issue(
        args.repo, args.head, args.base
    )
    
    debugger.print_diagnosis(diagnosis)
    
    # Exit with error code if blocked
    if diagnosis["status"] == "blocked":
        sys.exit(1)
    elif diagnosis["status"] == "degraded":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

