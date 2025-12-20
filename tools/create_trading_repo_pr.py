#!/usr/bin/env python3
"""
Create Trading Repo Pull Request
=================================

Creates PR for UltimateOptionsTradingRobot → trading-leads-bot consolidation.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-12-07
Priority: CRITICAL
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

# Add project root to sys.path for SSOT imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.core.utils.github_utils import (
    get_github_token,
    create_github_pr_headers,
    create_github_pr_url,
    create_pr_data,
    check_existing_pr,
)
from src.core.config.timeout_constants import TimeoutConstants


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
                # Check for existing PR
                existing_pr = check_existing_pr(owner, repo, head, token, timeout=timeout)
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
    """Create PR for UltimateOptionsTradingRobot consolidation."""
    token = get_github_token(project_root)
    if not token:
        print("❌ GITHUB_TOKEN not found.")
        return 1

    owner = "Dadudekc"
    repo = "trading-leads-bot"
    branch = "merge-Dadudekc/UltimateOptionsTradingRobot-20251205"
    title = "Merge UltimateOptionsTradingRobot into trading-leads-bot (Trading Repos Consolidation)"
    body = """Repository consolidation merge - Trading repos consolidation.

**Source**: UltimateOptionsTradingRobot
**Target**: trading-leads-bot

This merge consolidates UltimateOptionsTradingRobot into trading-leads-bot as part of the trading repos consolidation effort.

**Verification**:
- ✅ Source repo archived
- ✅ Branch created successfully
- ✅ Merge completed

**Executed by**: Agent-1 (Integration & Core Systems Specialist)
"""
    base = "main"

    print("🚀 Creating PR for trading repo consolidation...\n")
    print(f"📝 Creating PR for {repo}: {branch} → {base}")
    
    pr_data = create_pr(token, owner, repo, title, body, branch, base)
    
    if pr_data:
        print("\n" + "=" * 60)
        print(f"✅ PR created successfully!")
        print(f"   URL: {pr_data.get('html_url')}")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ PR creation failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

