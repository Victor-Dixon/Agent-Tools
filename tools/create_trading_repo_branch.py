#!/usr/bin/env python3
"""
Create Trading Repo Merge Branch
=================================

Creates a merge branch for UltimateOptionsTradingRobot → trading-leads-bot consolidation.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-12-07
Priority: CRITICAL
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.config.timeout_constants import TimeoutConstants
from src.core.utils.github_utils import get_github_token


def create_merge_branch(
    owner: str,
    target_repo: str,
    source_repo: str,
    branch_name: str
) -> bool:
    """
    Create a merge branch for repository consolidation.
    
    Args:
        owner: Repository owner (e.g., "Dadudekc")
        target_repo: Target repository name
        source_repo: Source repository name
        branch_name: Name of the branch to create
    
    Returns:
        True if successful, False otherwise
    """
    temp_dir = None
    try:
        # Create temp directory
        import tempfile
        temp_dir = Path(tempfile.mkdtemp(prefix="repo_merge_"))
        
        target_dir = temp_dir / "target"
        
        print("=" * 60)
        print("🚀 Creating Merge Branch")
        print("=" * 60)
        print(f"Target: {target_repo}")
        print(f"Source: {source_repo}")
        print(f"Branch: {branch_name}")
        print(f"Temp Dir: {temp_dir}")
        print("=" * 60)
        
        # Get GitHub token
        github_token = get_github_token(project_root)
        
        # Prepare URL
        if github_token:
            target_url = f"https://{github_token}@github.com/{owner}/{target_repo}.git"
        else:
            target_url = f"https://github.com/{owner}/{target_repo}.git"
        
        git_env = os.environ.copy()
        git_env["GIT_TERMINAL_PROMPT"] = "0"
        if github_token:
            git_env["GITHUB_TOKEN"] = github_token
        
        # Clone target repository
        print(f"\n📥 Cloning target repository: {target_repo}...")
        clone_result = subprocess.run(
            ["git", "clone", target_url, str(target_dir)],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_LONG,
            check=False,
            env=git_env
        )
        
        if clone_result.returncode != 0:
            error_msg = clone_result.stderr or clone_result.stdout or "Unknown error"
            print(f"❌ Failed to clone target repo: {error_msg}")
            return False
        
        print(f"✅ Target repository cloned")
        
        # Checkout main branch
        print(f"\n🔀 Checking out main branch...")
        checkout_result = subprocess.run(
            ["git", "checkout", "main"],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.SUBPROCESS_DEFAULT,
            check=False
        )
        
        if checkout_result.returncode != 0:
            # Try master branch
            checkout_result = subprocess.run(
                ["git", "checkout", "master"],
                cwd=target_dir,
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.SUBPROCESS_DEFAULT,
                check=False
            )
        
        if checkout_result.returncode != 0:
            print(f"⚠️ Could not checkout main/master, continuing...")
        
        # Create and checkout new branch
        print(f"\n🌿 Creating branch: {branch_name}...")
        branch_result = subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.SUBPROCESS_DEFAULT,
            check=False
        )
        
        if branch_result.returncode != 0:
            error_msg = branch_result.stderr or branch_result.stdout or "Unknown error"
            print(f"❌ Failed to create branch: {error_msg}")
            return False
        
        print(f"✅ Branch created: {branch_name}")
        
        # Add source repo as remote (if not already added)
        print(f"\n📡 Adding source repo as remote...")
        remote_name = "source"
        remote_result = subprocess.run(
            ["git", "remote", "add", remote_name, f"https://github.com/{owner}/{source_repo}.git"],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.SUBPROCESS_DEFAULT,
            check=False
        )
        
        if remote_result.returncode != 0:
            # Remote might already exist, try to update
            remote_result = subprocess.run(
                ["git", "remote", "set-url", remote_name, f"https://github.com/{owner}/{source_repo}.git"],
                cwd=target_dir,
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.SUBPROCESS_DEFAULT,
                check=False
            )
        
        # Fetch source repo
        print(f"\n📥 Fetching source repository...")
        fetch_result = subprocess.run(
            ["git", "fetch", remote_name],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_LONG,
            check=False
        )
        
        if fetch_result.returncode != 0:
            print(f"⚠️ Failed to fetch source repo (may be archived): {fetch_result.stderr}")
            # Continue anyway - branch is created
        
        # Merge source into branch (if fetch succeeded)
        if fetch_result.returncode == 0:
            print(f"\n🔀 Merging source into branch...")
            merge_result = subprocess.run(
                ["git", "merge", f"{remote_name}/main", "--allow-unrelated-histories", "--no-edit"],
                cwd=target_dir,
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.SUBPROCESS_DEFAULT,
                check=False
            )
            
            if merge_result.returncode != 0:
                # Try master branch
                merge_result = subprocess.run(
                    ["git", "merge", f"{remote_name}/master", "--allow-unrelated-histories", "--no-edit"],
                    cwd=target_dir,
                    capture_output=True,
                    text=True,
                    timeout=TimeoutConstants.SUBPROCESS_DEFAULT,
                    check=False
                )
            
            if merge_result.returncode == 0:
                print(f"✅ Source merged into branch")
            else:
                print(f"⚠️ Merge had conflicts or issues: {merge_result.stderr}")
                # Branch is still created, just needs manual merge
        
        # Push branch to remote
        print(f"\n📤 Pushing branch to remote...")
        push_result = subprocess.run(
            ["git", "push", "-u", "origin", branch_name],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_LONG,
            check=False,
            env=git_env
        )
        
        if push_result.returncode != 0:
            error_msg = push_result.stderr or push_result.stdout or "Unknown error"
            print(f"❌ Failed to push branch: {error_msg}")
            return False
        
        print(f"✅ Branch pushed to remote: {branch_name}")
        
        print("\n" + "=" * 60)
        print("✅ MERGE BRANCH CREATED SUCCESSFULLY")
        print("=" * 60)
        print(f"Branch: {branch_name}")
        print(f"Target: {target_repo}")
        print(f"Source: {source_repo}")
        print(f"\nNext: Create PR using GitHub API or web interface")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating merge branch: {e}")
        return False
        
    finally:
        # Cleanup temp directory
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
                print(f"\n🧹 Cleaned up temp directory")
            except Exception as e:
                print(f"⚠️ Failed to cleanup temp directory: {e}")


def main():
    """Create merge branch for UltimateOptionsTradingRobot consolidation."""
    owner = "Dadudekc"
    target_repo = "trading-leads-bot"
    source_repo = "UltimateOptionsTradingRobot"
    branch_name = "merge-Dadudekc/UltimateOptionsTradingRobot-20251205"
    
    print("🚀 Creating merge branch for trading repo consolidation...\n")
    
    success = create_merge_branch(owner, target_repo, source_repo, branch_name)
    
    if success:
        print("\n✅ Branch creation complete!")
        print(f"   Branch: {branch_name}")
        print(f"   Next: Create PR using tools/create_case_variation_prs.py or GitHub API")
        return 0
    else:
        print("\n❌ Branch creation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

