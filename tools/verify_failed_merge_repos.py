#!/usr/bin/env python3
"""
Verify Failed Merge Repositories
=================================

Checks actual GitHub repository status for failed merge attempts.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set

try:
    import requests
except ImportError:
    print("❌ requests library not installed. Install with: pip install requests")
    sys.exit(1)

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.config.timeout_constants import TimeoutConstants


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment."""
    return os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")


def parse_repo_name(repo_name: str) -> tuple[str, str]:
    """
    Parse repository name into owner and repo.
    
    Handles:
    - "repo" -> ("Dadudekc", "repo")
    - "owner/repo" -> ("owner", "repo")
    """
    if "/" in repo_name:
        owner, repo = repo_name.split("/", 1)
        return owner, repo
    else:
        # Default owner (you may need to adjust this)
        return "Dadudekc", repo_name


def verify_repo_exists(owner: str, repo: str, token: Optional[str] = None) -> Dict:
    """
    Verify repository existence using GitHub API.
    
    Returns:
        Dict with exists (bool), archived (bool), status_code, and details
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        response = requests.get(url, headers=headers, timeout=TimeoutConstants.HTTP_SHORT)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "exists": True,
                "archived": data.get("archived", False),
                "status_code": 200,
                "full_name": data.get("full_name"),
                "html_url": data.get("html_url"),
                "default_branch": data.get("default_branch", "main"),
                "private": data.get("private", False),
                "description": data.get("description", ""),
            }
        elif response.status_code == 404:
            return {
                "exists": False,
                "archived": False,
                "status_code": 404,
                "error": "Repository not found",
            }
        elif response.status_code == 403:
            return {
                "exists": None,  # Unknown (might be private)
                "archived": False,
                "status_code": 403,
                "error": "Access forbidden (may be private or rate-limited)",
            }
        else:
            return {
                "exists": None,
                "archived": False,
                "status_code": response.status_code,
                "error": f"Unexpected status: {response.status_code}",
            }
    except Exception as e:
        return {
            "exists": None,
            "archived": False,
            "status_code": None,
            "error": str(e),
        }


def main():
    """Verify repository status for failed merge attempts."""
    # Load merge failure analysis
    analysis_file = Path("docs/archive/consolidation/merge_failure_analysis.json")
    if not analysis_file.exists():
        print("❌ merge_failure_analysis.json not found")
        print("   Run tools/analyze_merge_failures.py first")
        return 1
    
    analysis = json.loads(analysis_file.read_text(encoding='utf-8'))
    
    # Get GitHub token
    token = get_github_token()
    if not token:
        print("⚠️  GITHUB_TOKEN not set - using public API (rate limited)")
        print("   Set GITHUB_TOKEN environment variable for better results")
    else:
        print("✅ Using GitHub token for API access")
    
    print()
    print("=" * 70)
    print("🔍 VERIFYING FAILED MERGE REPOSITORIES")
    print("=" * 70)
    print()
    
    # Collect unique repo names
    source_repos: Set[str] = set()
    target_repos: Set[str] = set()
    
    for error_type, repos in analysis.get("error_details", {}).items():
        for repo_info in repos:
            source_repos.add(repo_info.get("source_repo", ""))
            target_repos.add(repo_info.get("target_repo", ""))
    
    # Remove empty strings
    source_repos.discard("")
    target_repos.discard("")
    
    print(f"📊 Found {len(source_repos)} unique source repos and {len(target_repos)} unique target repos")
    print()
    
    # Verify source repos
    print("=" * 70)
    print("🔍 VERIFYING SOURCE REPOSITORIES")
    print("=" * 70)
    print()
    
    source_results = {}
    for repo_name in sorted(source_repos):
        owner, repo = parse_repo_name(repo_name)
        print(f"Checking: {repo_name} ({owner}/{repo})...", end=" ", flush=True)
        
        result = verify_repo_exists(owner, repo, token)
        source_results[repo_name] = result
        
        if result["exists"]:
            archived = " (ARCHIVED)" if result.get("archived") else ""
            print(f"✅ EXISTS{archived}")
            if result.get("html_url"):
                print(f"   URL: {result['html_url']}")
        elif result["exists"] is False:
            print("❌ NOT FOUND")
        else:
            print(f"⚠️  UNKNOWN ({result.get('error', 'Unknown error')})")
        
        # Rate limit protection
        time.sleep(0.5)
    
    print()
    
    # Verify target repos
    print("=" * 70)
    print("🔍 VERIFYING TARGET REPOSITORIES")
    print("=" * 70)
    print()
    
    target_results = {}
    for repo_name in sorted(target_repos):
        owner, repo = parse_repo_name(repo_name)
        print(f"Checking: {repo_name} ({owner}/{repo})...", end=" ", flush=True)
        
        result = verify_repo_exists(owner, repo, token)
        target_results[repo_name] = result
        
        if result["exists"]:
            archived = " (ARCHIVED)" if result.get("archived") else ""
            print(f"✅ EXISTS{archived}")
            if result.get("html_url"):
                print(f"   URL: {result['html_url']}")
        elif result["exists"] is False:
            print("❌ NOT FOUND")
        else:
            print(f"⚠️  UNKNOWN ({result.get('error', 'Unknown error')})")
        
        # Rate limit protection
        time.sleep(0.5)
    
    print()
    
    # Summary
    print("=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    print()
    
    source_exists = sum(1 for r in source_results.values() if r.get("exists") is True)
    source_not_found = sum(1 for r in source_results.values() if r.get("exists") is False)
    source_unknown = sum(1 for r in source_results.values() if r.get("exists") is None)
    
    target_exists = sum(1 for r in target_results.values() if r.get("exists") is True)
    target_not_found = sum(1 for r in target_results.values() if r.get("exists") is False)
    target_unknown = sum(1 for r in target_results.values() if r.get("exists") is None)
    
    print("Source Repositories:")
    print(f"   ✅ Exists: {source_exists}")
    print(f"   ❌ Not Found: {source_not_found}")
    print(f"   ⚠️  Unknown: {source_unknown}")
    print()
    
    print("Target Repositories:")
    print(f"   ✅ Exists: {target_exists}")
    print(f"   ❌ Not Found: {target_not_found}")
    print(f"   ⚠️  Unknown: {target_unknown}")
    print()
    
    # Save results
    verification_results = {
        "source_repos": source_results,
        "target_repos": target_results,
        "summary": {
            "source": {
                "exists": source_exists,
                "not_found": source_not_found,
                "unknown": source_unknown,
            },
            "target": {
                "exists": target_exists,
                "not_found": target_not_found,
                "unknown": target_unknown,
            }
        }
    }
    
    results_file = Path("docs/archive/consolidation/repo_verification_results.json")
    results_file.write_text(
        json.dumps(verification_results, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    print(f"📄 Results saved to: {results_file}")
    print()
    
    # Analysis
    print("=" * 70)
    print("💡 ANALYSIS")
    print("=" * 70)
    print()
    
    if source_not_found > 0:
        print(f"⚠️  {source_not_found} source repos NOT FOUND on GitHub")
        print("   This explains 'Source repo not available' errors")
        print("   Possible reasons:")
        print("   - Repos were deleted after being merged")
        print("   - Repos were renamed")
        print("   - Repo names are incorrect")
        print()
    
    if target_not_found > 0:
        print(f"⚠️  {target_not_found} target repos NOT FOUND on GitHub")
        print("   This explains 'Target repo not available' errors")
        print()
    
    if source_exists > 0:
        print(f"✅ {source_exists} source repos DO EXIST")
        print("   These failures may be due to:")
        print("   - Access/permission issues")
        print("   - Rate limiting")
        print("   - Temporary GitHub API issues")
        print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

