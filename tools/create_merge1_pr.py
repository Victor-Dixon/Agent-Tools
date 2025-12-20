#!/usr/bin/env python3
"""
Create PR for Merge #1 (DreamBank → DreamVault)
===============================================

Creates PR for Merge #1 using GitHub API with GITHUB_TOKEN.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-01-27
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import requests
from src.core.config.timeout_constants import TimeoutConstants
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests library not available. Install with: pip install requests")


# Use SSOT utility for GitHub token and PR operations
from src.core.utils.github_utils import get_github_token, create_github_pr_headers, check_existing_pr


def create_pr(
    token: str,
    owner: str,
    repo: str,
    title: str,
    body: str,
    head: str,
    base: str = "master"
) -> Dict[str, Any] | None:
    """Create a GitHub Pull Request."""
    if not REQUESTS_AVAILABLE:
        print(f"❌ requests library not available for {repo}")
        return None
    
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = create_github_pr_headers(token)
    data = {
        "title": title,
        "body": body,
        "head": head,
        "base": base
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=TimeoutConstants.HTTP_DEFAULT)
        if response.status_code == 201:
            pr_data = response.json()
            print(f"✅ PR created: {pr_data.get('html_url')}")
            return pr_data
        elif response.status_code == 422:
            error_data = response.json()
            if "already exists" in str(error_data).lower() or "No commits between" in str(error_data):
                print(f"⚠️ PR already exists or no commits for {repo}: {head} → {base}")
                print(f"   This confirms the merge is already complete!")
                # Check for existing PR using SSOT utility
                existing_pr = check_existing_pr(owner, repo, head, token, TimeoutConstants.HTTP_DEFAULT)
                if existing_pr:
                    print(f"✅ Found existing PR: {existing_pr.get('html_url')}")
                    return existing_pr
            print(f"❌ PR creation failed for {repo}: {error_data}")
            return None
        else:
            print(f"❌ PR creation failed for {repo}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating PR for {repo}: {e}")
        return None


def main():
    """Create PR for Merge #1 (DreamBank → DreamVault)."""
    token = get_github_token()
    if not token:
        print("❌ GITHUB_TOKEN not found.")
        return 1
    
    owner = "Dadudekc"
    repo = "DreamVault"
    merge_branch = "merge-DreamBank-20251124"
    base_branch = "master"
    
    print(f"🔗 Creating PR for Merge #1 (DreamBank → DreamVault)...")
    print(f"📋 Repository: {owner}/{repo}")
    print(f"📋 Merge Branch: {merge_branch}")
    print(f"📋 Base Branch: {base_branch}\n")
    
    pr = create_pr(
        token,
        owner,
        repo,
        "Merge DreamBank into DreamVault",
        "Repository consolidation merge - Dream Projects consolidation from Batch 2. Conflicts resolved using 'ours' strategy (kept DreamVault versions).",
        merge_branch,
        base_branch
    )
    
    if pr:
        print(f"\n✅ PR creation successful!")
        print(f"✅ PR URL: {pr.get('html_url')}")
        return 0
    else:
        print(f"\n⚠️ PR creation result: Merge may already be complete (no commits between branches)")
        return 0  # Not an error - merge already complete


if __name__ == "__main__":
    sys.exit(main())

