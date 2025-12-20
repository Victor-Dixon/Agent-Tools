#!/usr/bin/env python3
"""
Verify Batch 1 Merge Commits - Check if merges are already in main branch
Checks for merge commits in main branch history that indicate Batch 1 merges are complete.
"""

import os
import requests
import sys
from pathlib import Path
from datetime import datetime
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

def get_branch_sha(owner: str, repo: str, branch: str, token: str) -> str | None:
    """Get the SHA of a branch."""
    url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=TimeoutConstants.HTTP_DEFAULT)
        if response.status_code == 200:
            return response.json()['commit']['sha']
        elif response.status_code == 404:
            return None  # Branch doesn't exist
        else:
            print(f"❌ Failed to get SHA for {repo}/{branch}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting SHA for {repo}/{branch}: {e}")
        return None

def get_merge_commits(owner: str, repo: str, branch: str, token: str, limit: int = 50) -> list:
    """Get recent commits from a branch, looking for merge commits."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "sha": branch,
        "per_page": limit
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=TimeoutConstants.HTTP_DEFAULT)
        if response.status_code == 200:
            commits = response.json()
            merge_commits = [c for c in commits if len(c.get('parents', [])) > 1]
            return merge_commits
        else:
            print(f"❌ Failed to get commits for {repo}/{branch}: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error getting commits for {repo}/{branch}: {e}")
        return []

def check_merge_commit_for_repo(owner: str, repo: str, source_repo: str, token: str) -> dict:
    """Check if a merge commit exists in main branch for a specific source repo."""
    main_sha = get_branch_sha(owner, repo, "main", token)
    if not main_sha:
        return {"exists": False, "error": "Main branch not found"}
    
    merge_commits = get_merge_commits(owner, repo, "main", token, limit=100)
    
    # Look for merge commits that mention the source repo
    relevant_merges = []
    for commit in merge_commits:
        message = commit.get('commit', {}).get('message', '').lower()
        if source_repo.lower() in message or f"merge {source_repo.lower()}" in message:
            relevant_merges.append({
                "sha": commit['sha'][:8],
                "message": commit.get('commit', {}).get('message', '')[:100],
                "date": commit.get('commit', {}).get('author', {}).get('date', ''),
                "author": commit.get('commit', {}).get('author', {}).get('name', '')
            })
    
    return {
        "main_sha": main_sha[:8] if main_sha else None,
        "merge_commits_found": len(relevant_merges),
        "relevant_merges": relevant_merges,
        "total_merge_commits": len(merge_commits)
    }

def main():
    """Verify Batch 1 merge commits in main branches."""
    token = get_github_token()
    if not token:
        return 1
    
    owner = "Dadudekc"
    
    # Batch 1 merges: source → target
    batch1_merges = [
        {"target_repo": "Streamertools", "source_repo": "streamertools", "merge_branch": "merge-streamertools-20251124"},
        {"target_repo": "DaDudekC", "source_repo": "dadudekc", "merge_branch": "merge-dadudekc-20251124"},
        {"target_repo": "LSTMmodel_trainer", "source_repo": "LSTMmodel_trainer", "merge_branch": "merge-LSTMmodel_trainer-20251124"},
        {"target_repo": "FocusForge", "source_repo": "focusforge", "merge_branch": "merge-focusforge-20251124"},
        {"target_repo": "TBOWTactics", "source_repo": "tbowtactics", "merge_branch": "merge-tbowtactics-20251124"},
        {"target_repo": "projectscanner", "source_repo": "projectscanner", "merge_branch": "merge-projectscanner-20251124"},
        {"target_repo": "TROOP", "source_repo": "TROOP", "merge_branch": "merge-TROOP-20251124"}
    ]
    
    print("🔍 Verifying Batch 1 merge commits in main branches...")
    print("="*70)
    
    all_verified = True
    results = []
    
    for merge_info in batch1_merges:
        target_repo = merge_info['target_repo']
        source_repo = merge_info['source_repo']
        merge_branch = merge_info['merge_branch']
        
        print(f"\n📦 Checking {target_repo}...")
        
        # Check if merge branch exists
        merge_branch_sha = get_branch_sha(owner, target_repo, merge_branch, token)
        if merge_branch_sha:
            print(f"  ✅ Merge branch exists: {merge_branch} (SHA: {merge_branch_sha[:8]}...)")
        else:
            print(f"  ⚠️ Merge branch does not exist: {merge_branch}")
        
        # Check main branch for merge commits
        main_sha = get_branch_sha(owner, target_repo, "main", token)
        if not main_sha:
            print(f"  ❌ Main branch not found for {target_repo}")
            all_verified = False
            results.append({"repo": target_repo, "status": "error", "main_sha": None})
            continue
        
        print(f"  ✅ Main branch exists (SHA: {main_sha[:8]}...)")
        
        # Check if main and merge branch are identical
        if merge_branch_sha and main_sha == merge_branch_sha:
            print(f"  ✅ CONFIRMED: Main and merge branch are IDENTICAL (same SHA)")
            print(f"  ✅ This confirms merge is already complete!")
            results.append({"repo": target_repo, "status": "complete", "main_sha": main_sha[:8], "merge_branch_sha": merge_branch_sha[:8], "identical": True})
        else:
            print(f"  ⚠️ Main and merge branch are DIFFERENT")
            if merge_branch_sha:
                print(f"  📊 Main SHA: {main_sha[:8]}...")
                print(f"  📊 Merge SHA: {merge_branch_sha[:8]}...")
            
            # Check for merge commits
            merge_info_result = check_merge_commit_for_repo(owner, target_repo, source_repo, token)
            if merge_info_result.get("relevant_merges"):
                print(f"  ✅ Found {len(merge_info_result['relevant_merges'])} relevant merge commit(s):")
                for merge in merge_info_result['relevant_merges']:
                    print(f"    - {merge['sha']}: {merge['message'][:60]}... ({merge['date'][:10]})")
                results.append({"repo": target_repo, "status": "merged", "main_sha": main_sha[:8], "merge_commits": merge_info_result['relevant_merges']})
            else:
                print(f"  ⚠️ No merge commits found mentioning '{source_repo}'")
                print(f"  📊 Total merge commits in main: {merge_info_result.get('total_merge_commits', 0)}")
                results.append({"repo": target_repo, "status": "unknown", "main_sha": main_sha[:8]})
                all_verified = False
    
    print("\n" + "="*70)
    print("📊 VERIFICATION SUMMARY")
    print("="*70)
    
    complete_count = sum(1 for r in results if r.get("status") == "complete" or r.get("identical"))
    merged_count = sum(1 for r in results if r.get("status") == "merged")
    unknown_count = sum(1 for r in results if r.get("status") == "unknown" or r.get("status") == "error")
    
    print(f"✅ Complete (identical branches): {complete_count}/7")
    print(f"✅ Merged (merge commits found): {merged_count}/7")
    print(f"⚠️ Unknown/Error: {unknown_count}/7")
    
    if complete_count == 7:
        print("\n✅ VERIFICATION: All 7 Batch 1 merges are COMPLETE (main = merge branch)")
        print("✅ Batch 1 blocker is RESOLVED")
        print("✅ Can proceed with Batch 2")
        return 0
    elif complete_count + merged_count == 7:
        print("\n✅ VERIFICATION: All 7 Batch 1 merges are COMPLETE (merge commits found)")
        print("✅ Batch 1 blocker is RESOLVED")
        print("✅ Can proceed with Batch 2")
        return 0
    else:
        print("\n⚠️ VERIFICATION: Some Batch 1 merges may not be complete")
        print("⚠️ Re-evaluate Batch 1 status before proceeding with Batch 2")
        return 1

if __name__ == "__main__":
    sys.exit(main())

