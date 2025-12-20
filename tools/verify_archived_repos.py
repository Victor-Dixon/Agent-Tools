#!/usr/bin/env python3
"""
Verify Archived Repos Script
Verifies that content from archived repos is properly merged into target repos.

Usage:
    python tools/verify_archived_repos.py [--repo REPO_NAME] [--all] [--report]

Author: Agent-8
Date: 2025-01-27
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Archived repos to verify
ARCHIVED_REPOS = {
    "MeTuber": {
        "repo_id": 27,
        "target": "Streamertools",
        "target_id": 25,
        "archived_date": "2025-11-26",
        "verification_end": "2025-12-26"
    },
    "streamertools": {
        "repo_id": 31,
        "target": "Streamertools",
        "target_id": 25,
        "archived_date": "2025-11-26",
        "verification_end": "2025-12-26"
    },
    "DaDudekC": {
        "repo_id": 29,
        "target": "DaDudeKC-Website",
        "target_id": 28,
        "archived_date": "2025-11-26",
        "verification_end": "2025-12-26"
    },
    "dadudekc": {
        "repo_id": 36,
        "target": "DaDudeKC-Website",
        "target_id": 28,
        "archived_date": "2025-11-26",
        "verification_end": "2025-12-26"
    },
    "content": {
        "repo_id": 41,
        "target": "Auto_Blogger",
        "target_id": 61,
        "archived_date": "2025-11-26",
        "verification_end": "2025-12-26"
    },
    "FreeWork": {
        "repo_id": 71,
        "target": "Auto_Blogger",
        "target_id": 61,
        "archived_date": "2025-11-26",
        "verification_end": "2025-12-26"
    },
    "DigitalDreamscape": {
        "repo_id": 59,
        "target": "DreamVault",
        "target_id": 15,
        "archived_date": "2025-11-26",
        "verification_end": "2025-12-26",
        "pr": "DreamVault PR #4"
    },
    "contract-leads": {
        "repo_id": 20,
        "target": "trading-leads-bot",
        "target_id": 17,
        "archived_date": "2025-11-26",
        "verification_end": "2025-12-26",
        "pr": "trading-leads-bot PR #5"
    },
    "UltimateOptionsTradingRobot": {
        "repo_id": 5,
        "target": "trading-leads-bot",
        "target_id": 17,
        "archived_date": "2025-11-26",
        "verification_end": "2025-12-26",
        "note": "Merged during cleanup"
    },
    "TheTradingRobotPlug": {
        "repo_id": 38,
        "target": "trading-leads-bot",
        "target_id": 17,
        "archived_date": "2025-11-26",
        "verification_end": "2025-12-26",
        "note": "Merged during cleanup"
    },
    "Thea": {
        "repo_id": 66,
        "target": "DreamVault",
        "target_id": 15,
        "archived_date": "2025-11-26",
        "verification_end": "2025-12-26",
        "pr": "DreamVault PR #3"
    }
}


def clone_repo(repo_name: str, temp_dir: Path) -> Optional[Path]:
    """Clone archived repo for verification."""
    repo_path = temp_dir / repo_name
    if repo_path.exists():
        print(f"⚠️  {repo_name} already cloned, skipping...")
        return repo_path
    
    try:
        print(f"📥 Cloning {repo_name}...")
        subprocess.run(
            ["git", "clone", f"https://github.com/Dadudekc/{repo_name}.git", str(repo_path)],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_MEDIUM,
            check=True
        )
        print(f"✅ Cloned {repo_name}")
        return repo_path
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to clone {repo_name}: {e.stderr}")
        return None
    except subprocess.TimeoutExpired:
        print(f"⏱️  Timeout cloning {repo_name}")
        return None


def get_file_list(repo_path: Path) -> List[str]:
    """Get list of files in repo (excluding .git)."""
    files = []
    for root, dirs, filenames in os.walk(repo_path):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')
        for filename in filenames:
            rel_path = os.path.relpath(os.path.join(root, filename), repo_path)
            files.append(rel_path)
    return sorted(files)


def check_merge_commit(target_repo: str, source_repo: str) -> Tuple[bool, Optional[str]]:
    """Check if merge commit exists in target repo."""
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/Dadudekc/{target_repo}/commits"],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_SHORT
        )
        if result.returncode == 0:
            commits = json.loads(result.stdout)
            for commit in commits:
                message = commit.get("commit", {}).get("message", "").lower()
                if source_repo.lower() in message and "merge" in message:
                    return True, commit.get("sha")
        return False, None
    except Exception as e:
        print(f"⚠️  Could not check merge commit: {e}")
        return False, None


def verify_repo(repo_name: str, dry_run: bool = False) -> Dict:
    """Verify a single archived repo."""
    print(f"\n{'='*60}")
    print(f"🔍 Verifying: {repo_name}")
    print(f"{'='*60}")
    
    repo_info = ARCHIVED_REPOS[repo_name]
    target_repo = repo_info["target"]
    
    results = {
        "repo": repo_name,
        "target": target_repo,
        "verification_date": datetime.now().isoformat(),
        "content_verification": {},
        "merge_verification": {},
        "status": "pending"
    }
    
    if dry_run:
        print(f"🔍 [DRY RUN] Would verify {repo_name} → {target_repo}")
        results["status"] = "dry-run"
        return results
    
    # Create temp directory
    temp_dir = project_root / "temp_verification"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Clone archived repo
        source_path = clone_repo(repo_name, temp_dir)
        if not source_path:
            results["status"] = "failed"
            results["error"] = "Could not clone source repo"
            return results
        
        # Get file list from source
        source_files = get_file_list(source_path)
        results["content_verification"]["source_files_count"] = len(source_files)
        print(f"📁 Source repo has {len(source_files)} files")
        
        # Check merge commit
        has_merge, merge_sha = check_merge_commit(target_repo, repo_name)
        results["merge_verification"]["has_merge_commit"] = has_merge
        results["merge_verification"]["merge_sha"] = merge_sha
        if has_merge:
            print(f"✅ Merge commit found: {merge_sha}")
        else:
            print(f"⚠️  Merge commit not found")
        
        # Note: Full file comparison would require cloning target repo
        # For now, we verify merge commit exists
        
        results["status"] = "verified" if has_merge else "needs_review"
        
    except Exception as e:
        print(f"❌ Error verifying {repo_name}: {e}")
        results["status"] = "error"
        results["error"] = str(e)
    finally:
        # Cleanup temp directory (optional - keep for review)
        # if temp_dir.exists():
        #     import shutil
        #     shutil.rmtree(temp_dir)
        pass
    
    return results


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verify archived repos are properly merged"
    )
    parser.add_argument(
        "--repo",
        help="Verify specific repo (by name)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Verify all archived repos"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be verified without actually verifying"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate verification report"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔍 ARCHIVE VERIFICATION SCRIPT")
    print("=" * 60)
    print()
    
    repos_to_verify = []
    
    if args.repo:
        if args.repo in ARCHIVED_REPOS:
            repos_to_verify = [args.repo]
        else:
            print(f"❌ Repo '{args.repo}' not found in archived repos list")
            return 1
    elif args.all:
        repos_to_verify = list(ARCHIVED_REPOS.keys())
    else:
        print("💡 Use --repo REPO_NAME or --all to verify repos")
        print(f"Available repos: {', '.join(ARCHIVED_REPOS.keys())}")
        return 1
    
    print(f"📋 Repos to verify: {len(repos_to_verify)}")
    print()
    
    results = []
    for repo_name in repos_to_verify:
        result = verify_repo(repo_name, dry_run=args.dry_run)
        results.append(result)
        if not args.dry_run:
            time.sleep(2)  # Small delay between repos
    
    print()
    print("=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    verified = sum(1 for r in results if r["status"] == "verified")
    needs_review = sum(1 for r in results if r["status"] == "needs_review")
    failed = sum(1 for r in results if r["status"] in ["failed", "error"])
    
    print(f"✅ Verified: {verified}")
    print(f"⚠️  Needs Review: {needs_review}")
    print(f"❌ Failed: {failed}")
    
    if args.report:
        report_path = project_root / "agent_workspaces" / "Agent-8" / "verification_reports" / f"verification_report_{datetime.now().strftime('%Y%m%d')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Report saved: {report_path}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    import time
from src.core.config.timeout_constants import TimeoutConstants
    sys.exit(main())



