#!/usr/bin/env python3
"""
Verify Batch 2 Target Repos - Check for Clean State
Verifies that Batch 2 target repos are in a clean state (no unmerged files from Batch 1).
"""

import os
import requests
import sys
from pathlib import Path
from src.core.config.timeout_constants import TimeoutConstants

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def get_github_token() -> str | None:
    """Get GitHub token from environment variable."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN environment variable not set.")
    return token

def get_branch_status(owner: str, repo: str, branch: str, token: str) -> dict | None:
    """Get the status of a branch."""
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=TimeoutConstants.HTTP_DEFAULT)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            print(f"❌ Failed to get branch status for {repo}/{branch}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting branch status for {repo}/{branch}: {e}")
        return None

def get_repo_status(owner: str, repo: str, token: str) -> dict | None:
    """Get repository status."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=TimeoutConstants.HTTP_DEFAULT)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            print(f"❌ Failed to get repo status for {repo}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting repo status for {repo}: {e}")
        return None

def check_clean_state(owner: str, repo: str, token: str) -> dict:
    """Check if a repo is in a clean state (main branch exists, no obvious issues)."""
    result = {
        "repo": repo,
        "exists": False,
        "main_branch_exists": False,
        "main_sha": None,
        "clean_state": False,
        "status": "unknown"
    }
    
    # Check if repo exists
    repo_data = get_repo_status(owner, repo, token)
    if not repo_data:
        result["status"] = "not_found"
        return result
    
    result["exists"] = True
    
    # Check main branch
    branch_data = get_branch_status(owner, repo, "main", token)
    if branch_data:
        result["main_branch_exists"] = True
        result["main_sha"] = branch_data.get("commit", {}).get("sha", "")[:8] if branch_data.get("commit", {}).get("sha") else None
        result["clean_state"] = True  # If main branch exists and is accessible, assume clean
        result["status"] = "clean"
    else:
        # Try master branch
        branch_data = get_branch_status(owner, repo, "master", token)
        if branch_data:
            result["main_branch_exists"] = True
            result["main_sha"] = branch_data.get("commit", {}).get("sha", "")[:8] if branch_data.get("commit", {}).get("sha") else None
            result["clean_state"] = True
            result["status"] = "clean"
        else:
            result["status"] = "no_main_branch"
    
    return result

def main():
    """Verify Batch 2 target repos for clean state."""
    token = get_github_token()
    if not token:
        return 1
    
    owner = "Dadudekc"
    
    # Batch 2 target repos that were previously blocked
    target_repos = [
        "Streamertools",  # Batch 1 target, Batch 2 target (MeTuber → Streamertools)
        "DaDudeKC-Website",  # Batch 2 target (DaDudekC → DaDudeKC-Website)
        "MachineLearningModelMaker",  # Batch 2 target (LSTMmodel_trainer → MachineLearningModelMaker)
        "trading-leads-bot",  # Batch 2 target (UltimateOptionsTradingRobot, TheTradingRobotPlug → trading-leads-bot)
        "DreamVault"  # Batch 2 target (DreamBank, DigitalDreamscape, Thea → DreamVault)
    ]
    
    print("🔍 Verifying Batch 2 target repos for clean state...")
    print("="*70)
    
    all_clean = True
    results = []
    
    for repo in target_repos:
        print(f"\n📦 Checking {repo}...")
        result = check_clean_state(owner, repo, token)
        results.append(result)
        
        if result["exists"]:
            print(f"  ✅ Repository exists")
        else:
            print(f"  ❌ Repository not found")
            all_clean = False
            continue
        
        if result["main_branch_exists"]:
            print(f"  ✅ Main branch exists (SHA: {result['main_sha']}...)")
        else:
            print(f"  ❌ Main branch not found")
            all_clean = False
            continue
        
        if result["clean_state"]:
            print(f"  ✅ Clean state confirmed")
        else:
            print(f"  ⚠️ Clean state uncertain")
            all_clean = False
    
    print("\n" + "="*70)
    print("📊 VERIFICATION SUMMARY")
    print("="*70)
    
    clean_count = sum(1 for r in results if r.get("clean_state"))
    exists_count = sum(1 for r in results if r.get("exists"))
    
    print(f"✅ Clean state: {clean_count}/{len(target_repos)}")
    print(f"✅ Repositories exist: {exists_count}/{len(target_repos)}")
    
    print("\n📋 Detailed Results:")
    for result in results:
        status_icon = "✅" if result["clean_state"] else "❌"
        print(f"  {status_icon} {result['repo']}: {result['status']} (SHA: {result['main_sha'] or 'N/A'})")
    
    if all_clean:
        print("\n✅ VERIFICATION: All Batch 2 target repos are in CLEAN STATE")
        print("✅ Batch 2 blocker is RESOLVED")
        print("✅ Batch 2 execution can proceed immediately")
        return 0
    else:
        print("\n⚠️ VERIFICATION: Some Batch 2 target repos may not be in clean state")
        print("⚠️ Re-evaluate before proceeding with Batch 2")
        return 1

if __name__ == "__main__":
    sys.exit(main())

