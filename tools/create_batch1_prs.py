#!/usr/bin/env python3
"""
Create Batch 1 Pull Requests
=============================

Creates PRs for all Batch 1 merges using GitHub API with GITHUB_TOKEN.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-01-27
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import requests
    from src.core.config.timeout_constants import TimeoutConstants
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    TimeoutConstants = None
    print("⚠️ requests library not available. Install with: pip install requests")


def get_github_token() -> Optional[str]:
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
) -> Optional[Dict[str, Any]]:
    """Create a pull request using GitHub API."""
    if not REQUESTS_AVAILABLE:
        print(f"❌ Cannot create PR for {repo}: requests library not available")
        return None
    
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
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
            # PR might already exist
            error_data = response.json()
            if "already exists" in str(error_data).lower():
                print(f"⚠️ PR already exists for {repo}: {head} → {base}")
                # Check for existing PR using SSOT utility
                from src.core.utils.github_utils import check_existing_pr
                timeout = TimeoutConstants.HTTP_DEFAULT if TimeoutConstants else 30
                existing_pr = check_existing_pr(owner, repo, head, token, timeout)
                if existing_pr:
                    print(f"✅ Found existing PR: {existing_pr.get('html_url')}")
                    return existing_pr
            else:
                print(f"❌ PR creation failed for {repo}: {error_data}")
        else:
            print(f"❌ PR creation failed for {repo}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating PR for {repo}: {e}")
        return None


def main():
    """Create PRs for all Batch 1 merges."""
    token = get_github_token()
    if not token:
        print("❌ GITHUB_TOKEN not found. Set it in .env file or environment variable.")
        return 1
    
    owner = "Dadudekc"
    
    # Batch 1 merges with branch names
    batch1_merges = [
        {
            "repo": "Streamertools",
            "branch": "merge-streamertools-20251124",
            "title": "Merge streamertools into Streamertools",
            "body": "Repository consolidation merge - Case variation merge from Batch 1."
        },
        {
            "repo": "DaDudekC",
            "branch": "merge-dadudekc-20251124",
            "title": "Merge dadudekc into DaDudekC",
            "body": "Repository consolidation merge - Case variation merge from Batch 1."
        },
        {
            "repo": "LSTMmodel_trainer",
            "branch": "merge-LSTMmodel_trainer-20251124",
            "title": "Merge LSTMmodel_trainer into LSTMmodel_trainer",
            "body": "Repository consolidation merge - Case variation merge from Batch 1."
        },
        {
            "repo": "FocusForge",
            "branch": "merge-focusforge-20251124",
            "title": "Merge focusforge into FocusForge",
            "body": "Repository consolidation merge - Goldmine merge from Batch 1."
        },
        {
            "repo": "TBOWTactics",
            "branch": "merge-tbowtactics-20251124",
            "title": "Merge tbowtactics into TBOWTactics",
            "body": "Repository consolidation merge - Goldmine merge from Batch 1."
        },
        {
            "repo": "projectscanner",
            "branch": "merge-projectscanner-20251124",
            "title": "Merge projectscanner into projectscanner",
            "body": "Repository consolidation merge - Goldmine merge from Batch 1."
        },
        {
            "repo": "TROOP",
            "branch": "merge-TROOP-20251124",
            "title": "Merge TROOP into TROOP",
            "body": "Repository consolidation merge - Goldmine merge from Batch 1."
        }
    ]
    
    print(f"🚀 Creating PRs for {len(batch1_merges)} Batch 1 merges...\n")
    
    results = []
    for merge in batch1_merges:
        print(f"📝 Creating PR for {merge['repo']}...")
        pr = create_pr(
            token=token,
            owner=owner,
            repo=merge["repo"],
            title=merge["title"],
            body=merge["body"],
            head=merge["branch"],
            base="main"
        )
        results.append({
            "repo": merge["repo"],
            "branch": merge["branch"],
            "success": pr is not None,
            "pr_url": pr.get("html_url") if pr else None
        })
        print()
    
    # Summary
    print("\n" + "="*60)
    print("📊 BATCH 1 PR CREATION SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    print()
    
    if successful > 0:
        print("✅ Successful PRs:")
        for r in results:
            if r["success"]:
                print(f"  - {r['repo']}: {r['pr_url']}")
        print()
    
    if failed > 0:
        print("❌ Failed PRs:")
        for r in results:
            if not r["success"]:
                print(f"  - {r['repo']} ({r['branch']})")
        print()
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

