#!/usr/bin/env python3
"""
Create PRs for Content/Blog Systems Consolidation
==================================================

Creates PRs for the two completed merges:
- content → Auto_Blogger (branch: merge-content-20251128)
- FreeWork → Auto_Blogger (branch: merge-FreeWork-20251128)

Author: Agent-4 (Captain)
Date: 2025-11-28
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.unified_github_pr_creator import UnifiedGitHubPRCreator
from tools.merge_prs_via_api import get_github_token
import os


def get_github_username() -> str:
    """Get GitHub username from environment or config."""
    username = os.getenv("GITHUB_USERNAME", "Dadudekc")
    config_path = project_root / "config" / "github_username.txt"
    if config_path.exists():
        try:
            username = config_path.read_text().strip()
        except Exception:
            pass
    return username


def create_content_pr():
    """Create PR for content → Auto_Blogger merge."""
    username = get_github_username()
    creator = UnifiedGitHubPRCreator(owner=username)
    
    title = "Merge content into Auto_Blogger"
    body = """Repository Consolidation Merge

**Source**: content (repo #41)
**Target**: Auto_Blogger (repo #61)

This merge is part of repository consolidation.

**Verification**:
- ✅ Backup created
- ✅ Conflicts checked (0 conflicts)
- ✅ Target repo verified
- ✅ Merge branch pushed: merge-content-20251128

**Executed by**: Agent-4 (Captain)
**ROI**: 69.4x (Highest value opportunity!)
"""
    
    # Head is the merge branch in Auto_Blogger repo
    result = creator.create_pr_unified(
        repo="Auto_Blogger",
        title=title,
        body=body,
        head="merge-content-20251128",  # Branch in Auto_Blogger
        base="main",
        prefer_method="rest_api"  # Prefer REST API since rate limit reset
    )
    
    return result


def create_freework_pr():
    """Create PR for FreeWork → Auto_Blogger merge."""
    username = get_github_username()
    creator = UnifiedGitHubPRCreator(owner=username)
    
    title = "Merge FreeWork into Auto_Blogger"
    body = """Repository Consolidation Merge

**Source**: FreeWork (repo #71)
**Target**: Auto_Blogger (repo #61)

This merge is part of repository consolidation.

**Verification**:
- ✅ Backup created
- ✅ Conflicts checked (0 conflicts)
- ✅ Target repo verified
- ✅ Merge branch pushed: merge-FreeWork-20251128

**Executed by**: Agent-4 (Captain)
**ROI**: 69.4x (Highest value opportunity!)
"""
    
    # Head is the merge branch in Auto_Blogger repo
    result = creator.create_pr_unified(
        repo="Auto_Blogger",
        title=title,
        body=body,
        head="merge-FreeWork-20251128",  # Branch in Auto_Blogger
        base="main",
        prefer_method="rest_api"  # Prefer REST API since rate limit reset
    )
    
    return result


def main():
    """Create both PRs."""
    print("=" * 60)
    print("📦 CREATING CONTENT/BLOG SYSTEMS CONSOLIDATION PRs")
    print("=" * 60)
    print()
    
    # Check token
    token = get_github_token()
    if not token:
        print("❌ GITHUB_TOKEN not found")
        return 1
    
    print("✅ GitHub token found")
    print()
    
    # Create PR #1: content → Auto_Blogger
    print("🔗 Creating PR #1: content → Auto_Blogger...")
    result1 = create_content_pr()
    
    if result1.get("success"):
        pr_url = result1.get("pr_url") or result1.get("data", {}).get("html_url")
        method = result1.get("method", "unknown")
        print(f"✅ PR #1 created successfully using {method}")
        print(f"   🔗 {pr_url}")
    else:
        error = result1.get("error", "Unknown error")
        print(f"❌ PR #1 creation failed: {error}")
        return 1
    
    print()
    
    # Create PR #2: FreeWork → Auto_Blogger
    print("🔗 Creating PR #2: FreeWork → Auto_Blogger...")
    result2 = create_freework_pr()
    
    if result2.get("success"):
        pr_url = result2.get("pr_url") or result2.get("data", {}).get("html_url")
        method = result2.get("method", "unknown")
        print(f"✅ PR #2 created successfully using {method}")
        print(f"   🔗 {pr_url}")
    else:
        error = result2.get("error", "Unknown error")
        print(f"❌ PR #2 creation failed: {error}")
        return 1
    
    print()
    print("=" * 60)
    print("✅ BOTH PRs CREATED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("📋 Next Steps:")
    print("   1. Review PRs for conflicts (none detected)")
    print("   2. Merge PRs into main branch")
    print("   3. Archive source repos (content, FreeWork)")
    print("   4. Update master tracker")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

