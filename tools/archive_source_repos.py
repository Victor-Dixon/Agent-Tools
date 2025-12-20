#!/usr/bin/env python3
"""
Archive Source Repos Script
Archives GitHub repositories after PRs are merged to reduce repo count.

Usage:
    python tools/archive_source_repos.py [--dry-run] [--wait-for-rate-limit]

Author: Agent-8
Date: 2025-01-27
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Repos ready to archive (already merged)
REPOS_READY_TO_ARCHIVE = [
    "Dadudekc/MeTuber",
    "Dadudekc/streamertools",
    "Dadudekc/DaDudekC",
    "Dadudekc/dadudekc",
    "Dadudekc/content",
    "Dadudekc/FreeWork",
    "Dadudekc/DigitalDreamscape",  # PR #4 merged
    "Dadudekc/contract-leads",     # PR #5 merged
    "Dadudekc/Thea",               # PR #3 merged
]

# Repos waiting for PR merge
REPOS_WAITING_FOR_PR = [
    "Dadudekc/UltimateOptionsTradingRobot",  # PR #3 pending
    "Dadudekc/TheTradingRobotPlug",          # PR #4 pending
    "Dadudekc/LSTMmodel_trainer",            # PR #2 pending
]


def check_rate_limit() -> bool:
    """Check if GitHub API rate limit is available."""
    try:
        result = subprocess.run(
            ["gh", "api", "rate_limit"],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_SHORT
        )
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            remaining = data.get("resources", {}).get("core", {}).get("remaining", 0)
            return remaining > 0
    except Exception as e:
        print(f"⚠️  Could not check rate limit: {e}")
    return False


def archive_repo(repo: str, dry_run: bool = False) -> Tuple[bool, str]:
    """Archive a GitHub repository."""
    if dry_run:
        print(f"🔍 [DRY RUN] Would archive: {repo}")
        return True, "dry-run"
    
    try:
        result = subprocess.run(
            ["gh", "repo", "archive", repo, "--yes"],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if result.returncode == 0:
            print(f"✅ Archived: {repo}")
            return True, "success"
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            if "rate limit" in error_msg.lower():
                return False, "rate_limit"
            print(f"❌ Failed to archive {repo}: {error_msg}")
            return False, error_msg
    except subprocess.TimeoutExpired:
        print(f"⏱️  Timeout archiving {repo}")
        return False, "timeout"
    except Exception as e:
        print(f"❌ Error archiving {repo}: {e}")
        return False, str(e)


def wait_for_rate_limit(max_wait: int = 3600) -> bool:
    """Wait for GitHub API rate limit to reset."""
    print("⏳ Waiting for GitHub API rate limit to reset...")
    print("   (This may take up to 1 hour)")
    
    start_time = time.time()
    check_interval = 300  # Check every 5 minutes
    
    while time.time() - start_time < max_wait:
        if check_rate_limit():
            print("✅ Rate limit reset! Proceeding with archiving...")
            return True
        elapsed = int(time.time() - start_time)
        print(f"   Still waiting... ({elapsed}s elapsed)")
        time.sleep(check_interval)
    
    print("⏱️  Max wait time exceeded")
    return False


def main():
    """Main execution function."""
    import argparse
from src.core.config.timeout_constants import TimeoutConstants
    
    parser = argparse.ArgumentParser(
        description="Archive source repos after PRs merged"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be archived without actually archiving"
    )
    parser.add_argument(
        "--wait-for-rate-limit",
        action="store_true",
        help="Wait for API rate limit to reset before archiving"
    )
    parser.add_argument(
        "--only-ready",
        action="store_true",
        help="Only archive repos that are ready (skip waiting repos)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📦 ARCHIVE SOURCE REPOS SCRIPT")
    print("=" * 60)
    print()
    
    # Check rate limit
    if not args.dry_run and not check_rate_limit():
        print("⚠️  GitHub API rate limit exceeded")
        if args.wait_for_rate_limit:
            if not wait_for_rate_limit():
                print("❌ Rate limit did not reset in time")
                return 1
        else:
            print("💡 Use --wait-for-rate-limit to wait for reset")
            print("💡 Or use --dry-run to see what would be archived")
            return 1
    
    # Archive ready repos
    repos_to_archive = REPOS_READY_TO_ARCHIVE if args.only_ready else REPOS_READY_TO_ARCHIVE
    
    print(f"📋 Repos to archive: {len(repos_to_archive)}")
    print()
    
    success_count = 0
    failed_count = 0
    rate_limited = False
    
    for repo in repos_to_archive:
        success, status = archive_repo(repo, dry_run=args.dry_run)
        if success:
            success_count += 1
        else:
            failed_count += 1
            if status == "rate_limit":
                rate_limited = True
                print("⚠️  Rate limit hit. Stopping archiving.")
                break
        time.sleep(1)  # Small delay between requests
    
    print()
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully archived: {success_count}")
    print(f"❌ Failed: {failed_count}")
    
    if rate_limited:
        print()
        print("⚠️  Rate limit exceeded. Some repos not archived.")
        print("💡 Run again later or use --wait-for-rate-limit")
    
    if args.dry_run:
        print()
        print("💡 This was a dry run. Use without --dry-run to actually archive.")
    
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())



