#!/usr/bin/env python3
"""
Resolve Merge Conflicts with 'Ours' Strategy
Resolves conflicts in a merge branch by keeping target repo (ours) versions.
"""

import os
import subprocess
import sys
import tempfile
import shutil
import time
import stat
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.config.timeout_constants import TimeoutConstants

from src.core.utils.file_utils import ensure_directory_removed

def resolve_conflicts_with_ours(target_repo: str, source_repo: str, merge_branch: str) -> bool:
    """Resolve conflicts in merge branch using 'ours' strategy (keep target repo versions)."""
    try:
        github_token = os.getenv("GITHUB_TOKEN")
        username = os.getenv("GITHUB_USERNAME", "Dadudekc")
        
        # Create temp directory on D: drive to avoid C: drive space issues
        # Use D: drive temp directory if available, otherwise fall back to system temp
        d_temp_base = Path("D:/Temp")
        if d_temp_base.exists() or d_temp_base.parent.exists():
            # Create D:/Temp if it doesn't exist
            d_temp_base.mkdir(exist_ok=True)
            timestamp = int(time.time() * 1000000)
            temp_base = d_temp_base / f"resolve_conflicts_{timestamp}_{os.urandom(8).hex()}"
            temp_base.mkdir(parents=True, exist_ok=True)
        else:
            # Fallback to system temp (may fail if C: drive is full)
            timestamp = int(time.time() * 1000000)
            temp_base = Path(tempfile.mkdtemp(prefix=f"resolve_conflicts_{timestamp}_"))
        target_dir = temp_base / "target" / target_repo
        source_dir = temp_base / "source" / source_repo
        
        # Use SSOT utility for directory removal
        ensure_directory_removed(target_dir, "target")
        ensure_directory_removed(source_dir, "source")
        
        # Prepare git environment
        git_env = os.environ.copy()
        if github_token:
            git_env["GITHUB_TOKEN"] = github_token
            target_url = f"https://{github_token}@github.com/{username}/{target_repo}.git"
            source_url = f"https://{github_token}@github.com/{username}/{source_repo}.git"
        else:
            target_url = f"https://github.com/{username}/{target_repo}.git"
            source_url = f"https://github.com/{username}/{source_repo}.git"
        
        # Clone target repo with shallow clone to save disk space
        print(f"📥 Cloning target repository: {target_repo} (shallow clone)...")
        clone_result = subprocess.run(
            ["git", "clone", "--depth", "1", target_url, str(target_dir)],
            capture_output=True, text=True, check=False, timeout=TimeoutConstants.HTTP_LONG, env=git_env
        )
        
        if clone_result.returncode != 0:
            error_msg = clone_result.stderr or clone_result.stdout or "Unknown error"
            if "already exists" in error_msg:
                ensure_dir_removed(target_dir, "target")
                clone_result = subprocess.run(
                    ["git", "clone", target_url, str(target_dir)],
                    capture_output=True, text=True, check=False, timeout=TimeoutConstants.HTTP_LONG, env=git_env
                )
            if clone_result.returncode != 0:
                print(f"❌ Failed to clone target repo: {error_msg}")
                return False
        
        # Checkout merge branch if it exists, otherwise create it
        print(f"🔍 Checking for merge branch: {merge_branch}...")
        branch_check = subprocess.run(
            ["git", "branch", "-r"],
            cwd=target_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if merge_branch in branch_check.stdout:
            print(f"✅ Merge branch exists, checking out...")
            subprocess.run(["git", "fetch", "origin", merge_branch], cwd=target_dir, check=True, timeout=TimeoutConstants.HTTP_DEFAULT)
            subprocess.run(["git", "checkout", "-b", merge_branch, f"origin/{merge_branch}"], 
                         cwd=target_dir, check=True, timeout=TimeoutConstants.HTTP_DEFAULT)
        else:
            print(f"📝 Creating new merge branch: {merge_branch}...")
            subprocess.run(["git", "checkout", "-b", merge_branch], cwd=target_dir, check=True, timeout=TimeoutConstants.HTTP_DEFAULT)
        
        # Add source as remote if not already added
        remotes = subprocess.run(["git", "remote"], cwd=target_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT)
        if "source-merge" not in remotes.stdout:
            # Clone source repo
            print(f"📥 Cloning source repository: {source_repo}...")
            clone_result = subprocess.run(
                ["git", "clone", source_url, str(source_dir)],
                capture_output=True, text=True, check=False, timeout=TimeoutConstants.HTTP_LONG, env=git_env
            )
            
            if clone_result.returncode != 0:
                error_msg = clone_result.stderr or clone_result.stdout or "Unknown error"
                if "already exists" in error_msg:
                    ensure_dir_removed(source_dir, "source")
                    clone_result = subprocess.run(
                        ["git", "clone", source_url, str(source_dir)],
                        capture_output=True, text=True, check=False, timeout=TimeoutConstants.HTTP_LONG, env=git_env
                    )
                if clone_result.returncode != 0:
                    print(f"❌ Failed to clone source repo: {error_msg}")
                    return False
            
            # Add source as remote
            print(f"🔗 Adding source repo as remote...")
            subprocess.run(["git", "remote", "add", "source-merge", str(source_dir)], 
                         cwd=target_dir, check=True, timeout=TimeoutConstants.HTTP_DEFAULT)
        
        # Fetch from source
        subprocess.run(["git", "fetch", "source-merge"], cwd=target_dir, check=True, timeout=TimeoutConstants.HTTP_MEDIUM)
        
        # Check merge status
        merge_status = subprocess.run(
            ["git", "status"],
            cwd=target_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if "Unmerged paths" in merge_status.stdout or "both modified" in merge_status.stdout:
            print(f"🔧 Resolving conflicts using 'ours' strategy...")
            
            # Get list of conflicted files
            conflicted_files = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                cwd=target_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT
            )
            
            if conflicted_files.returncode == 0 and conflicted_files.stdout.strip():
                files = [f.strip() for f in conflicted_files.stdout.strip().split('\n') if f.strip()]
                print(f"📋 Found {len(files)} conflicted file(s): {', '.join(files)}")
                
                # Resolve each conflict using 'ours' strategy (keep target repo version)
                for file in files:
                    print(f"  🔧 Resolving {file} using 'ours' strategy...")
                    # Use checkout --ours to keep target repo version
                    subprocess.run(
                        ["git", "checkout", "--ours", file],
                        cwd=target_dir, check=True, timeout=TimeoutConstants.HTTP_DEFAULT
                    )
                    # Stage the resolved file
                    subprocess.run(
                        ["git", "add", file],
                        cwd=target_dir, check=True, timeout=TimeoutConstants.HTTP_DEFAULT
                    )
                    print(f"  ✅ Resolved {file}")
                
                # Commit the merge
                print(f"💾 Committing merge with resolved conflicts...")
                commit_result = subprocess.run(
                    ["git", "commit", "-m", f"Merge {source_repo} into {target_repo} - Conflicts resolved using 'ours' strategy"],
                    cwd=target_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT
                )
                
                if commit_result.returncode == 0:
                    print(f"✅ Conflicts resolved and committed!")
                    
                    # Push merge branch
                    print(f"📤 Pushing merge branch...")
                    push_result = subprocess.run(
                        ["git", "push", "-u", "origin", merge_branch],
                        cwd=target_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_MEDIUM, env=git_env
                    )
                    
                    if push_result.returncode == 0:
                        print(f"✅ Merge branch pushed successfully!")
                        return True
                    else:
                        print(f"❌ Push failed: {push_result.stderr}")
                        return False
                else:
                    print(f"❌ Commit failed: {commit_result.stderr}")
                    return False
            else:
                print(f"⚠️ No conflicted files found - merge may already be resolved")
                return True
        else:
            # Try to merge if not already merged
            print(f"🔀 Attempting merge...")
            merge_result = subprocess.run(
                ["git", "merge", "source-merge/main", "--allow-unrelated-histories", "--no-edit", "-m", f"Merge {source_repo} into {target_repo}"],
                cwd=target_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_LONG
            )
            
            if merge_result.returncode != 0:
                # Try master branch
                merge_result = subprocess.run(
                    ["git", "merge", "source-merge/master", "--allow-unrelated-histories", "--no-edit", "-m", f"Merge {source_repo} into {target_repo}"],
                    cwd=target_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_LONG
                )
            
            if merge_result.returncode != 0:
                error_msg = merge_result.stderr or merge_result.stdout or "Unknown error"
                if "CONFLICT" in error_msg or "conflict" in error_msg.lower():
                    # Conflicts detected, resolve them using 'ours' strategy
                    print(f"⚠️ Conflicts detected during merge, resolving using 'ours' strategy...")
                    
                    # Get list of conflicted files
                    conflicted_files = subprocess.run(
                        ["git", "diff", "--name-only", "--diff-filter=U"],
                        cwd=target_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT
                    )
                    
                    if conflicted_files.returncode == 0 and conflicted_files.stdout.strip():
                        files = [f.strip() for f in conflicted_files.stdout.strip().split('\n') if f.strip()]
                        print(f"📋 Found {len(files)} conflicted file(s): {', '.join(files)}")
                        
                        # Resolve each conflict using 'ours' strategy (keep target repo version)
                        for file in files:
                            print(f"  🔧 Resolving {file} using 'ours' strategy...")
                            subprocess.run(
                                ["git", "checkout", "--ours", file],
                                cwd=target_dir, check=True, timeout=TimeoutConstants.HTTP_DEFAULT
                            )
                            subprocess.run(
                                ["git", "add", file],
                                cwd=target_dir, check=True, timeout=TimeoutConstants.HTTP_DEFAULT
                            )
                            print(f"  ✅ Resolved {file}")
                        
                        # Commit the merge
                        print(f"💾 Committing merge with resolved conflicts...")
                        commit_result = subprocess.run(
                            ["git", "commit", "-m", f"Merge {source_repo} into {target_repo} - Conflicts resolved using 'ours' strategy"],
                            cwd=target_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_DEFAULT
                        )
                        
                        if commit_result.returncode == 0:
                            print(f"✅ Conflicts resolved and committed!")
                            
                            # Push merge branch (force push if remote exists with different commits)
                            print(f"📤 Pushing merge branch...")
                            push_result = subprocess.run(
                                ["git", "push", "-u", "origin", merge_branch],
                                cwd=target_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_MEDIUM, env=git_env
                            )
                            
                            if push_result.returncode == 0:
                                print(f"✅ Merge branch pushed successfully!")
                                return True
                            else:
                                # If push failed due to remote changes, force push
                                if "rejected" in push_result.stderr or "fetch first" in push_result.stderr:
                                    print(f"⚠️ Remote branch has different commits, force pushing resolved conflicts...")
                                    push_result = subprocess.run(
                                        ["git", "push", "-u", "--force", "origin", merge_branch],
                                        cwd=target_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_MEDIUM, env=git_env
                                    )
                                    if push_result.returncode == 0:
                                        print(f"✅ Merge branch force-pushed successfully!")
                                        return True
                                print(f"❌ Push failed: {push_result.stderr}")
                                return False
                        else:
                            print(f"❌ Commit failed: {commit_result.stderr}")
                            return False
                    else:
                        print(f"⚠️ No conflicted files found - merge may already be resolved")
                        return True
                else:
                    print(f"❌ Merge failed: {error_msg}")
                    return False
            else:
                print(f"✅ Merge completed without conflicts!")
                # Push merge branch
                push_result = subprocess.run(
                    ["git", "push", "-u", "origin", merge_branch],
                    cwd=target_dir, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_MEDIUM, env=git_env
                )
                
                if push_result.returncode == 0:
                    print(f"✅ Merge branch pushed successfully!")
                    return True
                else:
                    print(f"❌ Push failed: {push_result.stderr}")
                    return False
        
    except Exception as e:
        print(f"❌ Error resolving conflicts: {e}")
        return False
    finally:
        # Cleanup temp directory
        if 'temp_base' in locals() and temp_base.exists():
            shutil.rmtree(temp_base, ignore_errors=True)

def main():
    """Resolve Merge #1 conflicts."""
    if len(sys.argv) < 3:
        print("Usage: python resolve_merge_conflicts.py <target_repo> <source_repo> [merge_branch]")
        print("Example: python resolve_merge_conflicts.py DreamVault DreamBank merge-DreamBank-20251124")
        return 1
    
    target_repo = sys.argv[1]
    source_repo = sys.argv[2]
    merge_branch = sys.argv[3] if len(sys.argv) > 3 else f"merge-{source_repo}-{datetime.now().strftime('%Y%m%d')}"
    
    print(f"🔧 Resolving conflicts for {source_repo} → {target_repo}")
    print(f"📋 Merge branch: {merge_branch}")
    print(f"🎯 Strategy: 'ours' (keep {target_repo} versions)")
    print("="*70)
    
    success = resolve_conflicts_with_ours(target_repo, source_repo, merge_branch)
    
    if success:
        print("\n✅ CONFLICT RESOLUTION COMPLETE!")
        print(f"✅ Merge branch {merge_branch} pushed successfully")
        print(f"✅ Ready to create PR or merge")
        return 0
    else:
        print("\n❌ CONFLICT RESOLUTION FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())

