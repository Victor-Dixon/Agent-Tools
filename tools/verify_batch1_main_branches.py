#!/usr/bin/env python3
"""
Verify Batch 1 Main Branches
=============================

Checks if Batch 1 merged content is actually in main branches.

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


def get_main_branch_sha(token: str, owner: str, repo: str) -> Optional[str]:
    """Get the SHA of the main branch."""
    if not REQUESTS_AVAILABLE:
        return None
    
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/main"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=TimeoutConstants.HTTP_DEFAULT)
        if response.status_code == 200:
            branch_data = response.json()
            return branch_data.get("commit", {}).get("sha")
        elif response.status_code == 404:
            # Try master branch
            url = f"https://api.github.com/repos/{owner}/{repo}/branches/master"
            response = requests.get(url, headers=headers, timeout=TimeoutConstants.HTTP_DEFAULT)
            if response.status_code == 200:
                branch_data = response.json()
                return branch_data.get("commit", {}).get("sha")
    except Exception as e:
        print(f"  ⚠️ Error getting main branch: {e}")
    
    return None


def get_merge_branch_sha(token: str, owner: str, repo: str, branch: str) -> Optional[str]:
    """Get the SHA of a merge branch."""
    if not REQUESTS_AVAILABLE:
        return None
    
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=TimeoutConstants.HTTP_DEFAULT)
        if response.status_code == 200:
            branch_data = response.json()
            return branch_data.get("commit", {}).get("sha")
    except Exception as e:
        print(f"  ⚠️ Error getting merge branch: {e}")
    
    return None


def main():
    """Verify Batch 1 main branches."""
    token = get_github_token()
    if not token:
        print("❌ GITHUB_TOKEN not found.")
        return 1
    
    owner = "Dadudekc"
    
    batch1_merges = [
        {"repo": "Streamertools", "branch": "merge-streamertools-20251124", "source": "streamertools"},
        {"repo": "DaDudekC", "branch": "merge-dadudekc-20251124", "source": "dadudekc"},
        {"repo": "LSTMmodel_trainer", "branch": "merge-LSTMmodel_trainer-20251124", "source": "LSTMmodel_trainer"},
        {"repo": "FocusForge", "branch": "merge-focusforge-20251124", "source": "focusforge"},
        {"repo": "TBOWTactics", "branch": "merge-tbowtactics-20251124", "source": "tbowtactics"},
        {"repo": "projectscanner", "branch": "merge-projectscanner-20251124", "source": "projectscanner"},
        {"repo": "TROOP", "branch": "merge-TROOP-20251124", "source": "TROOP"}
    ]
    
    print(f"🔍 Verifying Batch 1 main branches (checking if merged content is in main)...\n")
    
    all_complete = True
    for merge in batch1_merges:
        print(f"📝 Checking {merge['repo']}...")
        
        main_sha = get_main_branch_sha(token, owner, merge["repo"])
        merge_sha = get_merge_branch_sha(token, owner, merge["repo"], merge["branch"])
        
        if main_sha and merge_sha:
            if main_sha == merge_sha:
                print(f"  ✅ Main and merge branch are IDENTICAL (SHA: {main_sha[:8]}...)")
                print(f"  ✅ CONFIRMED: Merge is complete - content is in main")
            else:
                print(f"  ⚠️ Main and merge branch DIFFER")
                print(f"  📌 Main SHA: {main_sha[:8]}...")
                print(f"  📌 Merge SHA: {merge_sha[:8]}...")
                print(f"  ⚠️ Merge may NOT be complete")
                all_complete = False
        elif not main_sha:
            print(f"  ❌ Could not get main branch SHA")
            all_complete = False
        elif not merge_sha:
            print(f"  ❌ Could not get merge branch SHA")
            all_complete = False
        
        print()
    
    print("="*60)
    if all_complete:
        print("✅ VERIFICATION: All Batch 1 merges are COMPLETE (main = merge branch)")
        print("✅ Batch 1 blocker is RESOLVED")
        print("✅ Can proceed with Batch 2")
    else:
        print("⚠️ VERIFICATION: Some Batch 1 merges may NOT be complete")
        print("⚠️ Need to investigate further")
    print("="*60)
    
    return 0 if all_complete else 1


if __name__ == "__main__":
    sys.exit(main())

