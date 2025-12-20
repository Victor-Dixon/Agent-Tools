#!/usr/bin/env python3
"""
Repository Chronology Tool - Chronological Blog Journey
========================================================

Fetches creation dates from GitHub API and orders all 75 repos chronologically.
Groups by time periods (Year 1, Year 2, Year 3) for blog journey planning.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-01-27
Priority: HIGH
Mission: Chronological Blog Journey
"""

import json
import os
import sys
from datetime import datetime, timedelta
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
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token
    
    config_path = Path("config/github_token.txt")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return f.read().strip()
    
    return None


def get_github_owner() -> str:
    """Get GitHub owner/username from config or environment."""
    owner = os.getenv("GITHUB_OWNER")
    if owner:
        return owner
    
    try:
        import subprocess
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_QUICK,
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            if "github.com" in url:
                parts = url.replace(".git", "").split("/")
                if len(parts) >= 2:
                    return parts[-2]
    except Exception:
        pass
    
    return "dadudekc"  # Default fallback


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
            return None
        elif response.status_code == 403:
            if not token:
                print(f"  ⚠️  Rate limit - consider setting GITHUB_TOKEN")
            return None
        else:
            return None
    
    except Exception:
        return None


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
                if not token:
                    print(f"  ⚠️  Rate limit - consider setting GITHUB_TOKEN")
                break
            else:
                break
        
    except Exception:
        pass
    
    return all_repos


def load_master_list() -> dict[str, Any]:
    """Load the master list of repos."""
    master_list_path = Path("data/github_75_repos_master_list.json")
    if not master_list_path.exists():
        raise FileNotFoundError(f"Master list not found: {master_list_path}")
    
    with open(master_list_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_repo_chronology(owner: str, token: Optional[str] = None) -> dict[str, Any]:
    """Get chronological ordering of all repos with creation dates."""
    print("Loading master list...")
    master_list = load_master_list()
    master_repos = {r.get("num"): r for r in master_list.get("repos", [])}
    
    print(f"Listing all repositories from GitHub ({owner})...")
    all_repos = list_all_repos(owner, token)
    print(f"Found {len(all_repos)} total repositories")
    
    # Create mapping of repo names to GitHub data
    repo_map = {}
    for repo in all_repos:
        repo_name = repo.get("name", "").lower()
        repo_map[repo_name] = repo
    
    print()
    print("Matching master list repos with GitHub repos...")
    
    chronology_data = []
    matched_count = 0
    unmatched_count = 0
    
    for repo_num, master_repo in master_repos.items():
        master_name = master_repo.get("name", "").strip()
        
        if not master_name or master_name.lower() == "unknown":
            chronology_data.append({
                "repo_num": repo_num,
                "name": "Unknown",
                "created_at": None,
                "created_at_iso": None,
                "matched": False,
                "master_list_name": None,
            })
            unmatched_count += 1
            continue
        
        # Try to find matching repo
        repo_lower = master_name.lower()
        github_repo = repo_map.get(repo_lower)
        
        if github_repo:
            created_at_str = github_repo.get("created_at")
            created_at = None
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                except Exception:
                    pass
            
            chronology_data.append({
                "repo_num": repo_num,
                "name": github_repo.get("name"),
                "full_name": github_repo.get("full_name"),
                "created_at": created_at.isoformat() if created_at else None,
                "created_at_iso": created_at_str,
                "description": github_repo.get("description"),
                "language": github_repo.get("language"),
                "url": github_repo.get("html_url"),
                "matched": True,
                "master_list_name": master_name,
            })
            matched_count += 1
        else:
            # Not found in GitHub repos list
            chronology_data.append({
                "repo_num": repo_num,
                "name": master_name,
                "created_at": None,
                "created_at_iso": None,
                "matched": False,
                "master_list_name": master_name,
            })
            unmatched_count += 1
    
    # Sort by creation date (oldest first)
    def sort_key(item):
        created = item.get("created_at")
        if created:
            try:
                return datetime.fromisoformat(created.replace('Z', '+00:00'))
            except Exception:
                pass
        return datetime.max  # Put unmatched at the end
    
    chronology_data.sort(key=sort_key)
    
    # Group by time periods
    now = datetime.now()
    year_1_start = None
    year_2_start = None
    year_3_start = None
    
    year_1_repos = []
    year_2_repos = []
    year_3_repos = []
    unknown_date_repos = []
    
    for repo in chronology_data:
        created = repo.get("created_at")
        if not created:
            unknown_date_repos.append(repo)
            continue
        
        try:
            created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            
            # Determine year boundaries
            if not year_1_start:
                year_1_start = created_dt
                year_2_start = year_1_start + timedelta(days=365)
                year_3_start = year_2_start + timedelta(days=365)
            
            if created_dt < year_2_start:
                year_1_repos.append(repo)
            elif created_dt < year_3_start:
                year_2_repos.append(repo)
            else:
                year_3_repos.append(repo)
        
        except Exception:
            unknown_date_repos.append(repo)
    
    result = {
        "generated_at": datetime.now().isoformat(),
        "total_repos": len(chronology_data),
        "matched_repos": matched_count,
        "unmatched_repos": unmatched_count,
        "chronology": chronology_data,
        "time_periods": {
            "year_1": {
                "start_date": year_1_start.isoformat() if year_1_start else None,
                "end_date": year_2_start.isoformat() if year_2_start else None,
                "repo_count": len(year_1_repos),
                "repos": year_1_repos,
            },
            "year_2": {
                "start_date": year_2_start.isoformat() if year_2_start else None,
                "end_date": year_3_start.isoformat() if year_3_start else None,
                "repo_count": len(year_2_repos),
                "repos": year_2_repos,
            },
            "year_3": {
                "start_date": year_3_start.isoformat() if year_3_start else None,
                "end_date": now.isoformat(),
                "repo_count": len(year_3_repos),
                "repos": year_3_repos,
            },
            "unknown_date": {
                "repo_count": len(unknown_date_repos),
                "repos": unknown_date_repos,
            },
        },
    }
    
    return result


def print_chronology_report(chronology: dict[str, Any]) -> None:
    """Print chronological report."""
    print("=" * 80)
    print("REPOSITORY CHRONOLOGY REPORT")
    print("=" * 80)
    print()
    
    print(f"Total Repos: {chronology['total_repos']}")
    print(f"Matched with GitHub: {chronology['matched_repos']}")
    print(f"Unmatched: {chronology['unmatched_repos']}")
    print()
    
    time_periods = chronology["time_periods"]
    
    print("TIME PERIOD BREAKDOWN:")
    print(f"  Year 1: {time_periods['year_1']['repo_count']} repos")
    if time_periods['year_1']['start_date']:
        print(f"    Period: {time_periods['year_1']['start_date'][:10]} to {time_periods['year_1']['end_date'][:10]}")
    
    print(f"  Year 2: {time_periods['year_2']['repo_count']} repos")
    if time_periods['year_2']['start_date']:
        print(f"    Period: {time_periods['year_2']['start_date'][:10]} to {time_periods['year_2']['end_date'][:10]}")
    
    print(f"  Year 3: {time_periods['year_3']['repo_count']} repos")
    if time_periods['year_3']['start_date']:
        print(f"    Period: {time_periods['year_3']['start_date'][:10]} to {time_periods['year_3']['end_date'][:10]}")
    
    print(f"  Unknown Date: {time_periods['unknown_date']['repo_count']} repos")
    print()
    
    print("CHRONOLOGICAL ORDER (First 10):")
    for i, repo in enumerate(chronology["chronology"][:10], 1):
        created = repo.get("created_at_iso", "Unknown date")
        if created:
            created = created[:10]  # Just the date part
        print(f"  {i}. Repo #{repo['repo_num']}: {repo['name']} - {created}")
    
    if len(chronology["chronology"]) > 10:
        print(f"  ... and {len(chronology['chronology']) - 10} more")
    
    print()
    print("=" * 80)


def main():
    """Main execution."""
    print("=" * 80)
    print("REPOSITORY CHRONOLOGY TOOL")
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
    
    try:
        chronology = get_repo_chronology(owner, token)
        print_chronology_report(chronology)
        
        # Save to file
        output_path = Path("data/repo_chronology.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chronology, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Chronology saved to: {output_path}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
from src.core.config.timeout_constants import TimeoutConstants
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())


