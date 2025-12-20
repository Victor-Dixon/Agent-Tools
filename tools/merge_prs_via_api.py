#!/usr/bin/env python3
"""
Merge PRs via GitHub REST API
==============================

Merges PRs using GitHub REST API (bypasses GraphQL rate limit).

Author: Agent-2 (Architecture & Design Specialist)
Date: 2025-01-27
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("❌ requests library not available. Install with: pip install requests")
    sys.exit(1)

# Import TimeoutConstants with fallback
try:
    from src.core.config.timeout_constants import TimeoutConstants
    from src.core.utils.github_utils import create_github_pr_headers, check_existing_pr
except ImportError:
    TimeoutConstants = None
    create_github_pr_headers = None
    check_existing_pr = None


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment or .env file."""
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        return token
    
    env_file = Path(".env")
    if env_file.exists():
        try:
            with open(env_file, "r") as f:
                for line in f:
                    if line.startswith("GITHUB_TOKEN="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    
    return None


def merge_pr(
    token: str,
    owner: str,
    repo: str,
    pr_number: int,
    merge_method: str = "merge"
) -> bool:
    """Merge a PR using GitHub REST API."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/merge"
    headers = create_github_pr_headers(token)
    data = {
        "merge_method": merge_method  # merge, squash, or rebase
    }
    
    try:
        response = requests.put(url, headers=headers, json=data, timeout=TimeoutConstants.HTTP_DEFAULT)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ PR #{pr_number} merged successfully!")
            if result.get("merged"):
                print(f"   SHA: {result.get('sha', 'N/A')}")
            return True
        elif response.status_code == 405:
            print(f"❌ PR #{pr_number} cannot be merged (not mergeable)")
            error_data = response.json()
            print(f"   Message: {error_data.get('message', 'Unknown error')}")
            return False
        elif response.status_code == 409:
            print(f"❌ PR #{pr_number} has conflicts or is already merged")
            error_data = response.json()
            print(f"   Message: {error_data.get('message', 'Unknown error')}")
            return False
        else:
            print(f"❌ PR #{pr_number} merge failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error merging PR #{pr_number}: {e}")
        return False


def create_pr(
    token: str,
    owner: str,
    repo: str,
    title: str,
    body: str,
    head: str,
    base: str = "master"
) -> Optional[Dict[str, Any]]:
    """Create a PR using GitHub REST API."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = create_github_pr_headers(token)
    data = {
        "title": title,
        "body": body,
        "head": head,
        "base": base
    }
    
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
                # Check for existing PR using SSOT utility
                if check_existing_pr:
                    existing_pr = check_existing_pr(owner, repo, head, token, timeout)
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
    """Merge PRs for Agent-2 consolidation."""
    token = get_github_token()
    if not token:
        print("❌ GITHUB_TOKEN not found. Set it in .env file or environment variable.")
        return 1
    
    owner = "Dadudekc"
    
    print("🚀 Merging PRs via GitHub REST API...\n")
    
    # PRs to merge
    prs_to_merge = [
        {
            "repo": "DreamVault",
            "pr_number": 4,
            "description": "DigitalDreamscape → DreamVault"
        },
        {
            "repo": "DreamVault",
            "pr_number": 3,
            "description": "Thea → DreamVault"
        }
    ]
    
    # Create and merge contract-leads PR
    contract_leads_pr = {
        "repo": "trading-leads-bot",
        "head": "merge-contract-leads-20251126",
        "base": "main",
        "title": "Merge contract-leads into trading-leads-bot",
        "body": """Repository Consolidation Merge

**Source**: contract-leads (repo #20)
**Target**: trading-leads-bot (repo #17)

This merge is part of Phase 2 repository consolidation.

**Verification**:
- ✅ Backup created
- ✅ Conflicts checked (3 unmerged files resolved)
- ✅ Target repo verified
- ✅ Merge branch created and pushed

**Executed by**: Agent-2 (Architecture & Design Specialist)"""
    }
    
    results = []
    
    # Merge existing PRs
    for pr_info in prs_to_merge:
        print(f"📝 Merging {pr_info['description']}...")
        success = merge_pr(
            token=token,
            owner=owner,
            repo=pr_info["repo"],
            pr_number=pr_info["pr_number"]
        )
        results.append({
            "repo": pr_info["repo"],
            "pr_number": pr_info["pr_number"],
            "description": pr_info["description"],
            "success": success
        })
        print()
        time.sleep(1)  # Rate limit protection
    
    # Create and merge contract-leads PR
    print(f"📝 Creating PR for contract-leads → trading-leads-bot...")
    pr = create_pr(
        token=token,
        owner=owner,
        repo=contract_leads_pr["repo"],
        title=contract_leads_pr["title"],
        body=contract_leads_pr["body"],
        head=contract_leads_pr["head"],
        base=contract_leads_pr["base"]
    )
    
    if pr:
        pr_number = pr.get("number")
        print(f"✅ PR #{pr_number} created, merging...")
        time.sleep(1)  # Rate limit protection
        success = merge_pr(
            token=token,
            owner=owner,
            repo=contract_leads_pr["repo"],
            pr_number=pr_number
        )
        results.append({
            "repo": contract_leads_pr["repo"],
            "pr_number": pr_number,
            "description": "contract-leads → trading-leads-bot",
            "success": success
        })
    else:
        results.append({
            "repo": contract_leads_pr["repo"],
            "pr_number": None,
            "description": "contract-leads → trading-leads-bot",
            "success": False
        })
    
    # Summary
    print("\n" + "="*60)
    print("📊 PR MERGE SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful
    
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    print()
    
    if successful > 0:
        print("✅ Successfully merged:")
        for r in results:
            if r["success"]:
                print(f"  - {r['description']} (PR #{r['pr_number']})")
        print()
    
    if failed > 0:
        print("❌ Failed:")
        for r in results:
            if not r["success"]:
                print(f"  - {r['description']}")
        print()
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

