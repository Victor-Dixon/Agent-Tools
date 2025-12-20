#!/usr/bin/env python3
"""
Create Case Variation Pull Requests
===================================

Creates PRs for case variation branches that were already created.
Based on LOOP4_CASE_VARIATIONS_STATUS_2025-12-06.md - 4 branches ready for PR creation.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-12-07
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config.timeout_constants import TimeoutConstants

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests library not available. Install with: pip install requests")


def get_github_token():
    """Get GitHub token from environment or .env file (uses SSOT utility)."""
    from src.core.utils.github_utils import get_github_token as get_token_ssot
    project_root = Path(__file__).resolve().parent.parent
    return get_token_ssot(project_root)


def create_pr(
    token: str,
    owner: str,
    repo: str,
    title: str,
    body: str,
    head: str,
    base: str = "main"
):
    """Create a GitHub Pull Request."""
    if not REQUESTS_AVAILABLE:
        print(f"❌ requests library not available for {repo}")
        return None
    
    # Use SSOT utilities for GitHub API
    from src.core.utils.github_utils import (
        create_github_pr_url,
        create_github_pr_headers,
        create_pr_data,
    )
    url = create_github_pr_url(owner, repo)
    headers = create_github_pr_headers(token)
    data = create_pr_data(title, body, head, base)
    
    try:
        timeout = TimeoutConstants.HTTP_DEFAULT if TimeoutConstants else 30
        response = requests.post(url, headers=headers, json=data, timeout=timeout)
        if response.status_code == 201:
            pr_data = response.json()
            print(f"✅ PR created: {pr_data.get('html_url')}")
            return pr_data
        elif response.status_code == 422:
            error_data = response.json()
            if "already exists" in str(error_data).lower() or "No commits between" in str(error_data):
                print(f"⚠️ PR already exists or no commits for {repo}: {head} → {base}")
                # Check for existing PR (uses SSOT utility)
                from src.core.utils.github_utils import check_existing_pr
                existing_pr = check_existing_pr(owner, repo, head, token, timeout=timeout)
                if existing_pr:
                    print(f"✅ Found existing PR: {existing_pr.get('html_url')}")
                    return existing_pr
                # SSOT utility already checked above, no fallback needed
                        print(f"✅ Found existing PR: {prs[0].get('html_url')}")
                        return prs[0]
            print(f"❌ PR creation failed for {repo}: {error_data}")
            return None
        else:
            print(f"❌ PR creation failed for {repo}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating PR for {repo}: {e}")
        return None


def main():
    """Create PRs for case variation branches."""
    token = get_github_token()
    if not token:
        print("❌ GITHUB_TOKEN not found.")
        return 1
    
    owner = "Dadudekc"
    
    # Case variation branches ready for PR creation (from LOOP4_CASE_VARIATIONS_STATUS)
    case_variation_merges = [
        {
            "repo": "FocusForge",
            "branch": "merge-Dadudekc/focusforge-20251205",
            "title": "Merge focusforge into FocusForge (Case Variation)",
            "body": "Repository consolidation merge - Case variation merge. Consolidating focusforge → FocusForge to reduce repository count.",
            "base": "main"
        },
        {
            "repo": "Streamertools",
            "branch": "merge-Dadudekc/streamertools-20251205",
            "title": "Merge streamertools into Streamertools (Case Variation)",
            "body": "Repository consolidation merge - Case variation merge. Consolidating streamertools → Streamertools to reduce repository count.",
            "base": "main"
        },
        {
            "repo": "TBOWTactics",
            "branch": "merge-Dadudekc/tbowtactics-20251205",
            "title": "Merge tbowtactics into TBOWTactics (Case Variation)",
            "body": "Repository consolidation merge - Case variation merge. Consolidating tbowtactics → TBOWTactics to reduce repository count.",
            "base": "main"
        },
        {
            "repo": "DaDudekC",
            "branch": "merge-Dadudekc/dadudekc-20251205",
            "title": "Merge dadudekc into DaDudekC (Case Variation)",
            "body": "Repository consolidation merge - Case variation merge. Consolidating dadudekc → DaDudekC to reduce repository count.",
            "base": "main"
        }
    ]
    
    successful_prs = 0
    failed_prs = []
    
    print("🚀 Creating PRs for case variation branches...\n")
    
    for merge in case_variation_merges:
        repo = merge["repo"]
        branch = merge["branch"]
        title = merge["title"]
        body = merge["body"]
        base = merge.get("base", "main")
        
        print(f"📝 Creating PR for {repo}: {branch} → {base}")
        
        pr = create_pr(token, owner, repo, title, body, branch, base)
        
        if pr:
            successful_prs += 1
            print(f"✅ PR created successfully for {repo}\n")
        else:
            failed_prs.append(repo)
            print(f"❌ Failed to create PR for {repo}\n")
    
    print("=" * 60)
    print(f"📊 Results: {successful_prs}/{len(case_variation_merges)} PRs created")
    
    if failed_prs:
        print(f"❌ Failed PRs: {', '.join(failed_prs)}")
    
    return 0 if successful_prs == len(case_variation_merges) else 1


if __name__ == "__main__":
    sys.exit(main())

