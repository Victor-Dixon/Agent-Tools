#!/usr/bin/env python3
"""
Resolve DreamVault PR #3 Conflicts
===================================

Resolves conflicts in DreamVault PR #3 (Thea) by updating the PR branch.

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

try:
    from dotenv import load_dotenv
from src.core.config.timeout_constants import TimeoutConstants
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


def get_github_token():
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def main():
    token = get_github_token()
    if not token:
        print("❌ GITHUB_TOKEN not found")
        return 1
    
    owner = "Dadudekc"
    repo = "DreamVault"
    pr_number = 3
    head_branch = "merge-Thea-20251124"
    base_branch = "master"
    
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp(prefix=f"resolve_pr3_"))
    repo_dir = temp_dir / repo
    
    try:
        git_env = os.environ.copy()
        git_env["GITHUB_TOKEN"] = token
        repo_url = f"https://{token}@github.com/{owner}/{repo}.git"
        
        print(f"📥 Cloning {repo}...")
        subprocess.run(
            ["git", "clone", repo_url, str(repo_dir)],
            capture_output=True, text=True, timeout=TimeoutConstants.HTTP_LONG, env=git_env, check=True
        )
        
        print(f"📥 Fetching all branches...")
        subprocess.run(
            ["git", "fetch", "origin"],
            cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_MEDIUM, env=git_env, check=True
        )
        
        print(f"🔀 Checking out {head_branch}...")
        subprocess.run(
            ["git", "checkout", head_branch],
            cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env, check=True
        )
        
        print(f"🔀 Merging {base_branch} into {head_branch}...")
        merge_result = subprocess.run(
            ["git", "merge", f"origin/{base_branch}", "--allow-unrelated-histories", "--no-edit"],
            cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_LONG, env=git_env
        )
        
        if merge_result.returncode != 0:
            print(f"⚠️ Conflicts detected, resolving with 'ours' strategy...")
            
            # Get conflicted files
            conflicted = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env
            )
            
            if conflicted.returncode == 0 and conflicted.stdout.strip():
                files = [f.strip() for f in conflicted.stdout.strip().split('\n') if f.strip()]
                print(f"📋 Found {len(files)} conflicted file(s): {', '.join(files)}")
                
                for file in files:
                    print(f"  🔧 Resolving {file} using 'ours' strategy...")
                    subprocess.run(
                        ["git", "checkout", "--ours", file],
                        cwd=repo_dir, check=False, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env
                    )
                    subprocess.run(
                        ["git", "add", file],
                        cwd=repo_dir, check=False, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env
                    )
                
                # Commit the resolution
                print(f"💾 Committing merge with resolved conflicts...")
                commit_result = subprocess.run(
                    ["git", "commit", "-m", "Resolve conflicts in PR #3 using 'ours' strategy (keep DreamVault versions)"],
                    cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT, env=git_env
                )
                
                if commit_result.returncode == 0:
                    print(f"✅ Conflicts resolved and committed")
                else:
                    print(f"⚠️ Commit failed: {commit_result.stderr}")
            else:
                print(f"❌ Merge failed: {merge_result.stderr}")
                return 1
        
        # Push resolved branch
        print(f"📤 Pushing resolved {head_branch}...")
        push_result = subprocess.run(
            ["git", "push", "origin", head_branch, "--force"],
            cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_MEDIUM, env=git_env
        )
        
        if push_result.returncode == 0:
            print(f"✅ Resolved branch pushed successfully")
            print(f"⏳ Waiting for GitHub to update PR status...")
            time.sleep(5)
            
            # Try to merge PR
            print(f"🔄 Attempting to merge PR #{pr_number}...")
            url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/merge"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            data = {"merge_method": "merge"}
            
            response = requests.put(url, headers=headers, json=data, timeout=TimeoutConstants.HTTP_DEFAULT)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ PR #{pr_number} merged successfully!")
                print(f"   SHA: {result.get('sha', 'N/A')}")
                return 0
            else:
                print(f"⚠️ PR merge failed: {response.status_code}")
                print(f"   Response: {response.text}")
                print(f"   PR may need manual review or merge")
                return 1
        else:
            print(f"❌ Push failed: {push_result.stderr}")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())

