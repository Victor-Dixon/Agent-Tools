#!/usr/bin/env python3
"""
Complete Merge into Main
========================

Merges a merge branch into the main/master branch, resolving any conflicts
using the 'ours' strategy (keep main branch versions).

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-01-27
"""

import os
import subprocess
import sys
import tempfile
import shutil
import time
import stat
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.config.timeout_constants import TimeoutConstants

def complete_merge_into_main(repo: str, merge_branch: str, base_branch: str = "master") -> bool:
    """Merge merge branch into main/master branch."""
    try:
        github_token = os.getenv("GITHUB_TOKEN")
        username = os.getenv("GITHUB_USERNAME", "Dadudekc")
        
        # Create temp directory
        timestamp = int(time.time() * 1000000)
        temp_base = Path(tempfile.mkdtemp(prefix=f"complete_merge_{timestamp}_"))
        repo_dir = temp_base / repo
        
        # Use SSOT utility for directory removal
        from src.core.utils.file_utils import ensure_directory_removed
        ensure_directory_removed(repo_dir, "repo")
        
        # Prepare git environment
        git_env = os.environ.copy()
        if github_token:
            git_env["GITHUB_TOKEN"] = github_token
            repo_url = f"https://{github_token}@github.com/{username}/{repo}.git"
        else:
            repo_url = f"https://github.com/{username}/{repo}.git"
        
        # Clone repo with shallow clone
        print(f"📥 Cloning repository: {repo} (shallow clone)...")
        clone_result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(repo_dir)],
            capture_output=True, text=True, check=False, timeout=TimeoutConstants.HTTP_LONG, env=git_env
        )
        
        if clone_result.returncode != 0:
            error_msg = clone_result.stderr or clone_result.stdout or "Unknown error"
            if "already exists" in error_msg:
                ensure_dir_removed(repo_dir, "repo")
                clone_result = subprocess.run(
                    ["git", "clone", "--depth", "1", repo_url, str(repo_dir)],
                    capture_output=True, text=True, check=False, timeout=TimeoutConstants.HTTP_LONG, env=git_env
                )
            if clone_result.returncode != 0:
                print(f"❌ Failed to clone repo: {error_msg}")
                return False
        
        # Fetch merge branch (need to fetch it since we did shallow clone)
        print(f"📥 Fetching merge branch: {merge_branch}...")
        fetch_result = subprocess.run(
            ["git", "fetch", "origin", f"{merge_branch}:{merge_branch}"],
            cwd=repo_dir, capture_output=True, text=True, check=False, timeout=TimeoutConstants.HTTP_MEDIUM, env=git_env
        )
        
        if fetch_result.returncode != 0:
            print(f"⚠️ Failed to fetch merge branch, trying without depth limit...")
            # Re-clone without depth limit to get merge branch
            ensure_dir_removed(repo_dir, "repo")
            clone_result = subprocess.run(
                ["git", "clone", repo_url, str(repo_dir)],
                capture_output=True, text=True, check=False, timeout=TimeoutConstants.HTTP_LONG, env=git_env
            )
            if clone_result.returncode != 0:
                print(f"❌ Failed to clone repo: {clone_result.stderr}")
                return False
        
        # Checkout base branch
        print(f"🔀 Checking out base branch: {base_branch}...")
        checkout_result = subprocess.run(
            ["git", "checkout", base_branch],
            cwd=repo_dir, capture_output=True, text=True, check=False, timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if checkout_result.returncode != 0:
            print(f"⚠️ {base_branch} not found, trying main...")
            base_branch = "main"
            checkout_result = subprocess.run(
                ["git", "checkout", base_branch],
                cwd=repo_dir, capture_output=True, text=True, check=False, timeout=TimeoutConstants.HTTP_DEFAULT
            )
            if checkout_result.returncode != 0:
                print(f"❌ Failed to checkout base branch: {checkout_result.stderr}")
                return False
        
        # Merge merge branch into base branch
        print(f"🔀 Merging {merge_branch} into {base_branch}...")
        merge_result = subprocess.run(
            ["git", "merge", merge_branch, "--allow-unrelated-histories", "--no-edit", "-m", f"Merge {merge_branch} into {base_branch}"],
            cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_LONG
        )
        
        if merge_result.returncode != 0:
            error_msg = merge_result.stderr or merge_result.stdout or "Unknown error"
            if "CONFLICT" in error_msg or "conflict" in error_msg.lower():
                print(f"⚠️ Conflicts detected during merge into {base_branch}, resolving using 'ours' strategy...")
                
                # Get list of conflicted files
                conflicted_files = subprocess.run(
                    ["git", "diff", "--name-only", "--diff-filter=U"],
                    cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT
                )
                
                if conflicted_files.returncode == 0 and conflicted_files.stdout.strip():
                    files = [f.strip() for f in conflicted_files.stdout.strip().split('\n') if f.strip()]
                    print(f"📋 Found {len(files)} conflicted file(s): {', '.join(files)}")
                    
                    # Resolve each conflict using 'ours' strategy (keep base branch version)
                    for file in files:
                        print(f"  🔧 Resolving {file} using 'ours' strategy...")
                        subprocess.run(
                            ["git", "checkout", "--ours", file],
                            cwd=repo_dir, check=True, timeout=TimeoutConstants.HTTP_DEFAULT
                        )
                        subprocess.run(
                            ["git", "add", file],
                            cwd=repo_dir, check=True, timeout=TimeoutConstants.HTTP_DEFAULT
                        )
                        print(f"  ✅ Resolved {file}")
                    
                    # Commit the merge
                    print(f"💾 Committing merge with resolved conflicts...")
                    commit_result = subprocess.run(
                        ["git", "commit", "-m", f"Merge {merge_branch} into {base_branch} - Conflicts resolved using 'ours' strategy"],
                        cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT
                    )
                    
                    if commit_result.returncode == 0:
                        print(f"✅ Conflicts resolved and committed!")
                    else:
                        print(f"❌ Commit failed: {commit_result.stderr}")
                        return False
                else:
                    print(f"⚠️ No conflicted files found - merge may already be resolved")
            else:
                print(f"❌ Merge failed: {error_msg}")
                return False
        else:
            print(f"✅ Merge completed without conflicts!")
        
        # Push merged base branch
        print(f"📤 Pushing merged {base_branch} branch...")
        push_result = subprocess.run(
            ["git", "push", "origin", base_branch],
            cwd=repo_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_MEDIUM, env=git_env
        )
        
        if push_result.returncode == 0:
            print(f"✅ Merged {base_branch} branch pushed successfully!")
            return True
        else:
            print(f"❌ Push failed: {push_result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error completing merge: {e}")
        return False
    finally:
        # Cleanup temp directory
        if 'temp_base' in locals() and temp_base.exists():
            shutil.rmtree(temp_base, ignore_errors=True)

def main():
    """Complete Merge #1 by merging merge branch into main."""
    if len(sys.argv) < 3:
        print("Usage: python complete_merge_into_main.py <repo> <merge_branch> [base_branch]")
        print("Example: python complete_merge_into_main.py DreamVault merge-DreamBank-20251124 master")
        return 1
    
    repo = sys.argv[1]
    merge_branch = sys.argv[2]
    base_branch = sys.argv[3] if len(sys.argv) > 3 else "master"
    
    print(f"🔧 Completing merge: {merge_branch} → {base_branch}")
    print(f"📋 Repository: {repo}")
    print("="*70)
    
    success = complete_merge_into_main(repo, merge_branch, base_branch)
    
    if success:
        print("\n✅ MERGE COMPLETE!")
        print(f"✅ {merge_branch} merged into {base_branch} successfully")
        return 0
    else:
        print("\n❌ MERGE FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())

