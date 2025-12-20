#!/usr/bin/env python3
"""
Create Batch 2 Pull Requests
============================

Creates PRs for all completed Batch 2 merges using GitHub API with GITHUB_TOKEN.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-01-27
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
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
) -> Dict[str, Any] | None:
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
        from src.core.config.timeout_constants import TimeoutConstants
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
                from src.core.config.timeout_constants import TimeoutConstants
                timeout = TimeoutConstants.HTTP_DEFAULT if TimeoutConstants else 30
                existing_pr = check_existing_pr(owner, repo, head, token, timeout=timeout)
                if existing_pr:
                    print(f"✅ Found existing PR: {existing_pr.get('html_url')}")
                    return existing_pr
                # SSOT utility already checked above, no fallback needed
            print(f"❌ PR creation failed for {repo}: {error_data}")
            return None
        else:
            print(f"❌ PR creation failed for {repo}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating PR for {repo}: {e}")
        return None


def main():
    """Create PRs for all completed Batch 2 merges."""
    token = get_github_token()
    if not token:
        print("❌ GITHUB_TOKEN not found.")
        return 1
    
    owner = "Dadudekc"
    
    # Batch 2 completed merges (7 merges)
    batch2_merges = [
        {
            "repo": "DreamVault",
            "branch": "merge-Thea-20251124",
            "title": "Merge Thea into DreamVault",
            "body": "Repository consolidation merge - Dream Projects consolidation from Batch 2. Conflicts resolved using 'ours' strategy (kept DreamVault versions).",
            "base": "master"
        },
        {
            "repo": "trading-leads-bot",
            "branch": "merge-UltimateOptionsTradingRobot-20251124",
            "title": "Merge UltimateOptionsTradingRobot into trading-leads-bot",
            "body": "Repository consolidation merge - Trading Repos consolidation from Batch 2. Conflicts resolved using 'ours' strategy (kept trading-leads-bot versions).",
            "base": "main"
        },
        {
            "repo": "trading-leads-bot",
            "branch": "merge-TheTradingRobotPlug-20251124",
            "title": "Merge TheTradingRobotPlug into trading-leads-bot",
            "body": "Repository consolidation merge - Trading Repos consolidation from Batch 2. Conflicts resolved using 'ours' strategy (kept trading-leads-bot versions).",
            "base": "main"
        },
        {
            "repo": "Streamertools",
            "branch": "merge-MeTuber-20251124",
            "title": "Merge MeTuber into Streamertools",
            "body": "Repository consolidation merge - Streaming & Personal consolidation from Batch 2. Conflicts resolved using 'ours' strategy (kept Streamertools versions).",
            "base": "main"
        },
        {
            "repo": "DaDudeKC-Website",
            "branch": "merge-DaDudekC-20251124",
            "title": "Merge DaDudekC into DaDudeKC-Website",
            "body": "Repository consolidation merge - DaDudekC Projects consolidation from Batch 2. Conflicts resolved using 'ours' strategy (kept DaDudeKC-Website versions).",
            "base": "main"
        },
        {
            "repo": "MachineLearningModelMaker",
            "branch": "merge-LSTMmodel_trainer-20251124",
            "title": "Merge LSTMmodel_trainer into MachineLearningModelMaker",
            "body": "Repository consolidation merge - ML Models consolidation from Batch 2. Conflicts resolved using 'ours' strategy (kept MachineLearningModelMaker versions).",
            "base": "master"  # Try master instead of main due to unrelated histories
        }
    ]
    
    # Note: DreamBank → DreamVault already merged into master, no PR needed
    
    successful_prs = 0
    failed_prs = []
    
    print("🔗 Creating PRs for 6 Batch 2 merges (DreamBank already merged into master).\n")
    
    for merge in batch2_merges:
        print(f"🐝 Creating PR for {merge['repo']} ({merge['branch']})...")
        pr = create_pr(
            token,
            owner,
            merge['repo'],
            merge['title'],
            merge['body'],
            merge['branch'],
            merge['base']
        )
        if pr:
            successful_prs += 1
        else:
            failed_prs.append(merge['repo'])
        print()
    
    print("="*60)
    print("📊 BATCH 2 PR CREATION SUMMARY")
    print("="*60)
    print(f"✅ Successful: {successful_prs}/{len(batch2_merges)}")
    print(f"❌ Failed: {len(failed_prs)}/{len(batch2_merges)}")
    
    if failed_prs:
        print("\n❌ Failed PRs:")
        for repo_name in failed_prs:
            print(f"  - {repo_name}")
    
    print("\n📝 Note: DreamBank → DreamVault merge already completed (merged into master), no PR needed.")
    
    if successful_prs == 0:
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

