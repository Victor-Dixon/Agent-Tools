#!/usr/bin/env python3
"""
Resolve PR Conflicts and Merge
==============================

Resolves conflicts in a PR using 'ours' strategy, then merges the PR.

Author: Agent-2 (Architecture & Design Specialist)
Date: 2025-01-27
"""

import os
import sys
import subprocess
import tempfile
import shutil
import time
import requests
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.config.timeout_constants import TimeoutConstants


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


def get_pr_info(token: str, owner: str, repo: str, pr_number: int) -> Optional[dict]:
    """Get PR information."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=TimeoutConstants.HTTP_DEFAULT)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get PR info: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting PR info: {e}")
        return None


def resolve_conflicts_via_git(
    owner: str,
    repo: str,
    pr_number: int,
    head_branch: str,
    base_branch: str = "master"
) -> bool:
    """Resolve conflicts by cloning, merging, and pushing."""
    token = get_github_token()
    if not token:
        print("❌ GITHUB_TOKEN not found")
        return False
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix=f"resolve_pr_{pr_number}_"))
    repo_dir = temp_dir / repo
    
    try:
        # Prepare git environment
        git_env = os.environ.copy()
        git_env["GITHUB_TOKEN"] = token
        
        repo_url = f"https://{token}@github.com/{owner}/{repo}.git"
        
        print(f"📥 Cloning {repo}...")
        clone_result = subprocess.run(
            ["git", "clone", repo_url, str(repo_dir)],
            capture_output=True, text=True, timeout=TimeoutConstants.HTTP_LONG, env=git_env
        )
        
        if clone_result.returncode != 0:
            print(f"❌ Clone failed: {clone_result.stderr}")
            return False
        
        # Fetch all branches
        print(f"📥 Fetching all branches...")
        subprocess.run(
            ["git", "fetch", "origin"],
            cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_MEDIUM, env=git_env
        )
        
        # Checkout base branch
        print(f"🔀 Checking out base branch: {base_branch}...")
        checkout_result = subprocess.run(
            ["git", "checkout", base_branch],
            cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env
        )
        
        if checkout_result.returncode != 0:
            # Try main
            base_branch = "main"
            checkout_result = subprocess.run(
                ["git", "checkout", base_branch],
                cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env
            )
            if checkout_result.returncode != 0:
                print(f"❌ Failed to checkout base branch: {checkout_result.stderr}")
                return False
        
        # Merge head branch
        print(f"🔀 Merging {head_branch} into {base_branch}...")
        merge_result = subprocess.run(
            ["git", "merge", f"origin/{head_branch}", "--allow-unrelated-histories", "--no-edit"],
            cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_LONG, env=git_env
        )
        
        if merge_result.returncode != 0:
            # Check for conflicts
            if "conflict" in merge_result.stderr.lower() or "conflict" in merge_result.stdout.lower():
                print(f"⚠️ Conflicts detected, resolving with 'ours' strategy...")
                
                # Get conflicted files
                conflicted = subprocess.run(
                    ["git", "diff", "--name-only", "--diff-filter=U"],
                    cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env
                )
                
                if conflicted.returncode == 0 and conflicted.stdout.strip():
                    files = [f.strip() for f in conflicted.stdout.strip().split('\n') if f.strip()]
                    print(f"📋 Found {len(files)} conflicted file(s), resolving with 'ours' strategy...")
                    
                    for file in files:
                        subprocess.run(
                            ["git", "checkout", "--ours", file],
                            cwd=repo_dir, check=False, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env
                        )
                        subprocess.run(
                            ["git", "add", file],
                            cwd=repo_dir, check=False, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env
                        )
                    
                    # Commit the resolution
                    commit_result = subprocess.run(
                        ["git", "commit", "-m", f"Resolve conflicts in PR #{pr_number} using 'ours' strategy"],
                        cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env
                    )
                    
                    if commit_result.returncode == 0:
                        print(f"✅ Conflicts resolved and committed")
                    else:
                        print(f"⚠️ Commit failed: {commit_result.stderr}")
            else:
                print(f"❌ Merge failed: {merge_result.stderr}")
                return False
        
        # Checkout head branch and push resolved changes
        print(f"🔀 Checking out {head_branch}...")
        checkout_head = subprocess.run(
            ["git", "checkout", head_branch],
            cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env
        )
        
        if checkout_head.returncode != 0:
            # Create branch if it doesn't exist locally
            subprocess.run(
                ["git", "checkout", "-b", head_branch, f"origin/{head_branch}"],
                cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env
            )
        
        # Merge base into head to get conflicts
        print(f"🔀 Merging {base_branch} into {head_branch} to detect conflicts...")
        merge_base = subprocess.run(
            ["git", "merge", base_branch, "--allow-unrelated-histories", "--no-edit"],
            cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_LONG, env=git_env
        )
        
        if merge_base.returncode != 0:
            # Check for conflicts
            if "conflict" in merge_base.stderr.lower() or "conflict" in merge_base.stdout.lower():
                print(f"⚠️ Conflicts detected, resolving with 'ours' strategy...")
                
                # Get conflicted files
                conflicted = subprocess.run(
                    ["git", "diff", "--name-only", "--diff-filter=U"],
                    cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env
                )
                
                if conflicted.returncode == 0 and conflicted.stdout.strip():
                    files = [f.strip() for f in conflicted.stdout.strip().split('\n') if f.strip()]
                    print(f"📋 Found {len(files)} conflicted file(s), resolving with 'ours' strategy...")
                    
                    for file in files:
                        subprocess.run(
                            ["git", "checkout", "--ours", file],
                            cwd=repo_dir, check=False, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env
                        )
                        subprocess.run(
                            ["git", "add", file],
                            cwd=repo_dir, check=False, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env
                        )
                    
                    # Commit the resolution
                    commit_result = subprocess.run(
                        ["git", "commit", "-m", f"Resolve conflicts in PR #{pr_number} using 'ours' strategy"],
                        cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env
                    )
                    
                    if commit_result.returncode == 0:
                        print(f"✅ Conflicts resolved and committed")
        
        # Push resolved branch
        print(f"📤 Pushing resolved {head_branch}...")
        push_result = subprocess.run(
            ["git", "push", "origin", head_branch, "--force"],
            cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_MEDIUM, env=git_env
        )
        
        if push_result.returncode == 0:
            print(f"✅ Resolved branch pushed successfully")
            return True
        else:
            print(f"❌ Push failed: {push_result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error resolving conflicts: {e}")
        return False
    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def merge_pr(token: str, owner: str, repo: str, pr_number: int) -> bool:
    """Merge a PR using GitHub REST API."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/merge"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    data = {
        "merge_method": "merge"
    }
    
    try:
        response = requests.put(url, headers=headers, json=data, timeout=TimeoutConstants.HTTP_DEFAULT)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ PR #{pr_number} merged successfully!")
            if result.get("merged"):
                print(f"   SHA: {result.get('sha', 'N/A')}")
            return True
        elif response.status_code == 405:
            print(f"❌ PR #{pr_number} cannot be merged (not mergeable)")
            error_data = response.json()
            print(f"   Message: {error_data.get('message', 'Unknown error')}")
            return False
        elif response.status_code == 409:
            print(f"❌ PR #{pr_number} has conflicts or is already merged")
            error_data = response.json()
            print(f"   Message: {error_data.get('message', 'Unknown error')}")
            return False
        else:
            print(f"❌ PR #{pr_number} merge failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error merging PR #{pr_number}: {e}")
        return False


def main():
    """Resolve PR #3 conflicts and merge."""
    token = get_github_token()
    if not token:
        print("❌ GITHUB_TOKEN not found. Set it in .env file or environment variable.")
        return 1
    
    owner = "Dadudekc"
    repo = "DreamVault"
    pr_number = 3
    
    print(f"🚀 Resolving conflicts in {repo} PR #{pr_number}...\n")
    
    # Get PR info
    pr_info = get_pr_info(token, owner, repo, pr_number)
    if not pr_info:
        print("❌ Failed to get PR information")
        return 1
    
    head_branch = pr_info.get("head", {}).get("ref")
    base_branch = pr_info.get("base", {}).get("ref")
    
    print(f"📊 PR Information:")
    print(f"   Head: {head_branch}")
    print(f"   Base: {base_branch}")
    print(f"   Mergeable: {pr_info.get('mergeable')}")
    print(f"   Mergeable State: {pr_info.get('mergeable_state')}")
    print()
    
    if pr_info.get("merged"):
        print("✅ PR is already merged!")
        return 0
    
    if pr_info.get("mergeable") == True:
        print("✅ PR is mergeable, attempting merge...")
        if merge_pr(token, owner, repo, pr_number):
            return 0
        else:
            print("⚠️ Merge failed, trying conflict resolution...")
    
    # Resolve conflicts
    print(f"🔧 Resolving conflicts using 'ours' strategy...")
    if resolve_conflicts_via_git(owner, repo, pr_number, head_branch, base_branch):
        print(f"✅ Conflicts resolved, waiting for GitHub to update PR status...")
        time.sleep(5)  # Wait for GitHub to update PR status
        
        # Retry merge
        print(f"🔄 Retrying merge...")
        if merge_pr(token, owner, repo, pr_number):
            return 0
        else:
            print("⚠️ Merge still failing after conflict resolution")
            return 1
    else:
        print("❌ Failed to resolve conflicts")
        return 1


if __name__ == "__main__":
    sys.exit(main())

