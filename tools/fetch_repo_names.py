#!/usr/bin/env python3
"""
Fetch Repo Names via GitHub API - Repo Analysis Improvement Tool
================================================================

Fetches repository names and metadata from GitHub API for Unknown repos.

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-01-27
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

try:
    import requests
except ImportError:
    print("❌ Error: 'requests' library not installed.")
    print("   Install with: pip install requests")
    sys.exit(1)


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment or config."""
    # Try environment variable first
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token
    
    # Try config file
    config_path = Path("config/github_token.txt")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return f.read().strip()
    
    return None


def fetch_repo_info(owner: str, repo_name: str, token: Optional[str] = None) -> Optional[dict[str, Any]]:
    """Fetch repository information from GitHub API."""
    url = f"https://api.github.com/repos/{owner}/{repo_name}"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        response = requests.get(url, headers=headers, timeout=TimeoutConstants.HTTP_SHORT)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"  ⚠️  Repo not found: {owner}/{repo_name}")
            return None
        elif response.status_code == 403:
            print(f"  ⚠️  Rate limit or access denied for: {owner}/{repo_name}")
            if not token:
                print("     Tip: Set GITHUB_TOKEN environment variable for higher rate limits")
            return None
        else:
            print(f"  ⚠️  Error {response.status_code} for: {owner}/{repo_name}")
            return None
    
    except Exception as e:
        print(f"  ❌ Exception fetching {owner}/{repo_name}: {e}")
        return None


def load_master_list() -> dict[str, Any]:
    """Load the master list of repos."""
    master_list_path = Path("data/github_75_repos_master_list.json")
    if not master_list_path.exists():
        raise FileNotFoundError(f"Master list not found: {master_list_path}")
    
    with open(master_list_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_github_owner() -> str:
    """Get GitHub owner/username from config or environment."""
    owner = os.getenv("GITHUB_OWNER")
    if owner:
        return owner
    
    # Try to infer from git remote
    try:
        import subprocess
from src.core.config.timeout_constants import TimeoutConstants
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_QUICK,
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            # Extract owner from git URL
            if "github.com" in url:
                parts = url.replace(".git", "").split("/")
                if len(parts) >= 2:
                    return parts[-2]
    except Exception:
        pass
    
    # Default fallback
    return "dadudekc"  # Based on repo naming patterns


def list_all_repos(owner: str, token: Optional[str] = None) -> list[dict[str, Any]]:
    """List all repositories for the owner using GitHub API."""
    url = f"https://api.github.com/users/{owner}/repos"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    all_repos = []
    page = 1
    per_page = 100
    
    try:
        while True:
            params = {"page": page, "per_page": per_page, "sort": "created", "direction": "asc"}
            response = requests.get(url, headers=headers, params=params, timeout=TimeoutConstants.HTTP_SHORT)
            
            if response.status_code == 200:
                repos = response.json()
                if not repos:
                    break
                all_repos.extend(repos)
                if len(repos) < per_page:
                    break
                page += 1
            elif response.status_code == 403:
                print(f"  ⚠️  Rate limit or access denied. Using unauthenticated requests (lower rate limit).")
                if not token:
                    print("     Tip: Set GITHUB_TOKEN environment variable for higher rate limits")
                break
            else:
                print(f"  ⚠️  Error {response.status_code} listing repos")
                break
        
        print(f"  ✅ Found {len(all_repos)} total repositories for {owner}")
        
    except Exception as e:
        print(f"  ❌ Exception listing repos: {e}")
    
    return all_repos


def fetch_unknown_repos(owner: str, token: Optional[str] = None) -> dict[str, Any]:
    """Fetch information for Unknown repos by listing all repos and matching."""
    data = load_master_list()
    repos = data.get("repos", [])
    
    unknown_repos = [
        r for r in repos
        if not r.get("name") or r.get("name", "").lower() == "unknown"
    ]
    
    results = {
        "total_unknown": len(unknown_repos),
        "fetched": [],
        "failed": [],
        "not_found": [],
        "all_repos_listed": 0,
    }
    
    print(f"Found {len(unknown_repos)} Unknown repos to fetch")
    print(f"GitHub Owner: {owner}")
    print()
    
    # List all repos first for better matching
    print("Listing all repositories from GitHub...")
    all_repos = list_all_repos(owner, token)
    results["all_repos_listed"] = len(all_repos)
    
    # Create mapping of repo names to info
    repo_name_map = {repo.get("name"): repo for repo in all_repos}
    
    print()
    print(f"Matching {len(unknown_repos)} unknown repos against {len(all_repos)} total repos...")
    print()
    
    for repo in unknown_repos:
        repo_num = repo.get("num")
        print(f"Fetching Repo #{repo_num}...")
        
        # Try to match by index (if repos are ordered)
        # This assumes repos might be in the same order as their numbers
        matched = False
        
        # Strategy 1: Try direct name patterns
        possible_names = [
            f"repo-{repo_num}",
            f"repository-{repo_num}",
            f"project-{repo_num}",
        ]
        
        for name in possible_names:
            if name in repo_name_map:
                info = repo_name_map[name]
                results["fetched"].append({
                    "repo_num": repo_num,
                    "name": info.get("name"),
                    "full_name": info.get("full_name"),
                    "description": info.get("description"),
                    "url": info.get("html_url"),
                    "size": info.get("size"),
                    "language": info.get("language"),
                    "topics": info.get("topics", []),
                    "created_at": info.get("created_at"),
                })
                print(f"  ✅ Found: {info.get('name')} - {info.get('description', 'No description')[:60]}")
                matched = True
                break
        
        # Strategy 2: If we have exactly 75 repos and they're in order, try by index
        if not matched and len(all_repos) >= repo_num:
            # Try repos near the expected index (accounting for 0-based indexing)
            indices_to_try = [repo_num - 1]  # Primary guess
            if repo_num > 1:
                indices_to_try.append(repo_num - 2)
            if repo_num < len(all_repos):
                indices_to_try.append(repo_num)
            
            for idx in indices_to_try:
                if 0 <= idx < len(all_repos):
                    candidate = all_repos[idx]
                    # Only suggest if not already matched to another repo
                    candidate_name = candidate.get("name")
                    if candidate_name and candidate_name not in [r.get("name") for r in results["fetched"]]:
                        results["fetched"].append({
                            "repo_num": repo_num,
                            "name": candidate_name,
                            "full_name": candidate.get("full_name"),
                            "description": candidate.get("description"),
                            "url": candidate.get("html_url"),
                            "size": candidate.get("size"),
                            "language": candidate.get("language"),
                            "topics": candidate.get("topics", []),
                            "created_at": candidate.get("created_at"),
                            "match_confidence": "low",  # Flag for manual verification
                        })
                        print(f"  ⚠️  Suggested match (verify manually): {candidate_name}")
                        print(f"      Description: {candidate.get('description', 'No description')[:60]}")
                        matched = True
                        break
        
        if not matched:
            results["failed"].append({
                "repo_num": repo_num,
                "attempted_names": possible_names,
            })
            print(f"  ❌ Could not find repo #{repo_num}")
    
    return results


def main():
    """Main execution."""
    print("=" * 80)
    print("GITHUB REPO NAME FETCHER")
    print("=" * 80)
    print()
    
    token = get_github_token()
    if not token:
        print("⚠️  No GitHub token found. Using unauthenticated requests (lower rate limit).")
        print("   Set GITHUB_TOKEN environment variable for higher rate limits.")
        print()
    
    owner = get_github_owner()
    print(f"GitHub Owner: {owner}")
    print()
    
    results = fetch_unknown_repos(owner, token)
    
    print()
    print("=" * 80)
    print("FETCH RESULTS")
    print("=" * 80)
    print(f"Total Unknown: {results['total_unknown']}")
    print(f"Successfully Fetched: {len(results['fetched'])}")
    print(f"Failed: {len(results['failed'])}")
    print()
    
    if results['fetched']:
        print("Fetched Repos:")
        for repo in results['fetched']:
            print(f"  Repo #{repo['repo_num']}: {repo['name']}")
            print(f"    Description: {repo.get('description', 'N/A')}")
            print(f"    URL: {repo.get('url', 'N/A')}")
            print()
    
    # Save results
    output_path = Path("agent_workspaces/Agent-8/github_repo_fetch_results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Results saved to: {output_path}")
    
    return 0


if __name__ == "__main__":
    exit(main())


