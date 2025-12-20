#!/usr/bin/env python3
"""
Verify Remaining GitHub Consolidation Branches
==============================================

Verifies status of 3 remaining case variation branches via GitHub API.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-12-07
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.utils.github_utils import (
    get_github_token,
    create_github_pr_headers,
    check_existing_pr,
)
from src.core.config.timeout_constants import TimeoutConstants

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("❌ requests library not available. Install with: pip install requests")
    sys.exit(1)


def check_branch_status(owner: str, repo: str, branch: str, token: str) -> dict:
    """Check if branch exists and has commits."""
    headers = create_github_pr_headers(token)
    
    # Check if branch exists
    branch_url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
    try:
        response = requests.get(branch_url, headers=headers, timeout=TimeoutConstants.HTTP_DEFAULT)
        if response.status_code == 404:
            return {"exists": False, "error": "Branch not found"}
        if response.status_code != 200:
            return {"exists": False, "error": f"API error: {response.status_code}"}
        
        branch_data = response.json()
        
        # Check commits between branch and main
        compare_url = f"https://api.github.com/repos/{owner}/{repo}/compare/main...{branch}"
        compare_response = requests.get(compare_url, headers=headers, timeout=TimeoutConstants.HTTP_DEFAULT)
        
        if compare_response.status_code == 200:
            compare_data = compare_response.json()
            commits_ahead = compare_data.get("ahead_by", 0)
            commits_behind = compare_data.get("behind_by", 0)
            
            return {
                "exists": True,
                "commits_ahead": commits_ahead,
                "commits_behind": commits_behind,
                "has_commits": commits_ahead > 0,
                "sha": branch_data.get("commit", {}).get("sha", "")[:7]
            }
        else:
            return {"exists": True, "error": f"Compare failed: {compare_response.status_code}"}
            
    except Exception as e:
        return {"exists": False, "error": str(e)}


def check_repo_status(owner: str, repo: str, token: str) -> dict:
    """Check if repository exists and is accessible."""
    headers = create_github_pr_headers(token)
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    
    try:
        response = requests.get(repo_url, headers=headers, timeout=TimeoutConstants.HTTP_DEFAULT)
        if response.status_code == 404:
            return {"exists": False, "error": "Repository not found"}
        if response.status_code == 403:
            return {"exists": False, "error": "Repository access denied (may be private or archived)"}
        
        if response.status_code == 200:
            repo_data = response.json()
            return {
                "exists": True,
                "archived": repo_data.get("archived", False),
                "private": repo_data.get("private", False),
                "default_branch": repo_data.get("default_branch", "main")
            }
        else:
            return {"exists": False, "error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"exists": False, "error": str(e)}


def main():
    """Verify remaining 3 branches."""
    token = get_github_token()
    if not token:
        print("❌ GITHUB_TOKEN not found.")
        return 1
    
    owner = "Dadudekc"
    
    # 3 remaining branches from execute_case_variations_consolidation.py
    remaining_branches = [
        {
            "source_repo": "superpowered_ttrpg",
            "target_repo": "Superpowered-TTRPG",
            "branch": "merge-Dadudekc/superpowered_ttrpg-20251205",
            "description": "superpowered_ttrpg → Superpowered-TTRPG"
        },
        {
            "source_repo": "dadudekcwebsite",
            "target_repo": "DaDudeKC-Website",
            "branch": "merge-Dadudekc/dadudekcwebsite-20251205",
            "description": "dadudekcwebsite → DaDudeKC-Website"
        },
        {
            "source_repo": "my_resume",
            "target_repo": "my-resume",
            "branch": "merge-Dadudekc/my_resume-20251205",
            "description": "my_resume → my-resume"
        }
    ]
    
    print("🔍 Verifying remaining 3 GitHub consolidation branches...\n")
    print("=" * 60)
    
    for branch_info in remaining_branches:
        source_repo = branch_info["source_repo"]
        target_repo = branch_info["target_repo"]
        branch = branch_info["branch"]
        description = branch_info["description"]
        
        print(f"\n📋 {description}")
        print(f"   Source: {source_repo}")
        print(f"   Target: {target_repo}")
        print(f"   Branch: {branch}")
        
        # Check source repo
        print(f"\n   🔍 Checking source repo: {source_repo}")
        source_status = check_repo_status(owner, source_repo, token)
        if source_status.get("exists"):
            print(f"   ✅ Source repo exists (archived: {source_status.get('archived', False)})")
        else:
            print(f"   ❌ Source repo: {source_status.get('error', 'Unknown error')}")
        
        # Check target repo
        print(f"   🔍 Checking target repo: {target_repo}")
        target_status = check_repo_status(owner, target_repo, token)
        if target_status.get("exists"):
            print(f"   ✅ Target repo exists (archived: {target_status.get('archived', False)})")
        else:
            print(f"   ❌ Target repo: {target_status.get('error', 'Unknown error')}")
        
        # Check branch if target repo exists
        if target_status.get("exists"):
            print(f"   🔍 Checking branch: {branch}")
            branch_status = check_branch_status(owner, target_repo, branch, token)
            if branch_status.get("exists"):
                commits_ahead = branch_status.get("commits_ahead", 0)
                has_commits = branch_status.get("has_commits", False)
                sha = branch_status.get("sha", "")
                print(f"   ✅ Branch exists (SHA: {sha}, commits ahead: {commits_ahead})")
                if not has_commits:
                    print(f"   ⚠️  Branch has no commits ahead of main (already merged?)")
            else:
                print(f"   ❌ Branch: {branch_status.get('error', 'Unknown error')}")
        
        # Check for existing PR
        if target_status.get("exists"):
            print(f"   🔍 Checking for existing PR...")
            existing_pr = check_existing_pr(owner, target_repo, branch, token)
            if existing_pr:
                pr_url = existing_pr.get("html_url", "")
                pr_state = existing_pr.get("state", "")
                print(f"   ✅ Existing PR found: {pr_url} (state: {pr_state})")
            else:
                print(f"   ℹ️  No existing PR found")
        
        print()
    
    print("=" * 60)
    print("✅ Verification complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())

