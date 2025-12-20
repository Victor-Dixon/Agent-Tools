#!/usr/bin/env python3
"""
Complete Remaining Batch 2 Merges
==================================

Completes the remaining Batch 2 merge using simple git clone to D:/Temp.
Direct git commands, no complications.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-11-30
"""

import sys
import subprocess
import os
import shutil
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from tools.merge_prs_via_api import get_github_token
from src.core.config.timeout_constants import TimeoutConstants


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


def complete_digitaldreamscape_merge():
    """Complete DigitalDreamscape → DreamVault merge using simple git clone to D:/Temp."""
    print("=" * 70)
    print("🚀 COMPLETING BATCH 2 REMAINING MERGE")
    print("=" * 70)
    print("\n📋 Merge: DigitalDreamscape → DreamVault")
    print("   Method: Simple git clone to D:/Temp")
    print("   Direct git commands, no complications\n")
    
    username = get_github_username()
    github_token = get_github_token()
    
    # Use D:/Temp for cloning (avoids disk space issues)
    temp_base = Path("D:/Temp")
    if not temp_base.exists():
        temp_base.mkdir(parents=True, exist_ok=True)
    
    timestamp = int(time.time() * 1000)
    temp_dir = temp_base / f"batch2_merge_{timestamp}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    target_dir = temp_dir / "DreamVault"
    source_dir = temp_dir / "DigitalDreamscape"
    
    try:
        # Prepare git environment with token
        git_env = os.environ.copy()
        if github_token:
            git_env["GITHUB_TOKEN"] = github_token
            git_env["GIT_TERMINAL_PROMPT"] = "0"
        
        # Clone target repo
        print("📥 Step 1: Cloning target repository (DreamVault)...")
        target_url = f"https://{github_token}@github.com/{username}/DreamVault.git" if github_token else f"https://github.com/{username}/DreamVault.git"
        clone_result = subprocess.run(
            ["git", "clone", target_url, str(target_dir)],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_EXTENDED,
            env=git_env
        )
        
        if clone_result.returncode != 0:
            print(f"❌ Failed to clone DreamVault: {clone_result.stderr}")
            return False
        
        print("✅ DreamVault cloned successfully")
        
        # Clone source repo
        print("\n📥 Step 2: Cloning source repository (DigitalDreamscape)...")
        source_url = f"https://{github_token}@github.com/{username}/DigitalDreamscape.git" if github_token else f"https://github.com/{username}/DigitalDreamscape.git"
        clone_result = subprocess.run(
            ["git", "clone", source_url, str(source_dir)],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_EXTENDED,
            env=git_env
        )
        
        if clone_result.returncode != 0:
            print(f"❌ Failed to clone DigitalDreamscape: {clone_result.stderr}")
            return False
        
        print("✅ DigitalDreamscape cloned successfully")
        
        # Create merge branch
        print("\n🌿 Step 3: Creating merge branch...")
        merge_branch = f"merge-DigitalDreamscape-{datetime.now().strftime('%Y%m%d')}"
        subprocess.run(
            ["git", "checkout", "-b", merge_branch],
            cwd=target_dir,
            check=True,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        print(f"✅ Merge branch created: {merge_branch}")
        
        # Add source as remote
        print("\n🔗 Step 4: Adding source as remote...")
        subprocess.run(
            ["git", "remote", "add", "source-merge", str(source_dir)],
            cwd=target_dir,
            check=True,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        # Fetch from source
        print("\n📥 Step 5: Fetching from source...")
        subprocess.run(
            ["git", "fetch", "source-merge"],
            cwd=target_dir,
            check=True,
            timeout=TimeoutConstants.HTTP_LONG
        )
        
        # Merge source into target
        print("\n🔀 Step 6: Merging DigitalDreamscape into DreamVault...")
        merge_result = subprocess.run(
            ["git", "merge", "source-merge/main", "--allow-unrelated-histories", "--no-edit", "-m", "Merge DigitalDreamscape into DreamVault"],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_EXTENDED
        )
        
        if merge_result.returncode != 0:
            # Try master branch
            merge_result = subprocess.run(
                ["git", "merge", "source-merge/master", "--allow-unrelated-histories", "--no-edit", "-m", "Merge DigitalDreamscape into DreamVault"],
                cwd=target_dir,
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_EXTENDED
            )
        
        if merge_result.returncode != 0:
            print(f"⚠️ Merge had conflicts or issues: {merge_result.stderr[:500]}")
            # Resolve conflicts using 'ours' strategy
            print("\n🔧 Resolving conflicts using 'ours' strategy...")
            unmerged = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                cwd=target_dir,
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_DEFAULT
            )
            if unmerged.returncode == 0 and unmerged.stdout.strip():
                files = [f.strip() for f in unmerged.stdout.strip().split('\n') if f.strip()]
                print(f"📋 Found {len(files)} conflicted file(s), resolving...")
                for file in files:
                    subprocess.run(["git", "checkout", "--ours", file], cwd=target_dir, check=False, timeout=TimeoutConstants.HTTP_DEFAULT)
                    subprocess.run(["git", "add", file], cwd=target_dir, check=False, timeout=TimeoutConstants.HTTP_DEFAULT)
                # Commit the resolution
                commit_result = subprocess.run(
                    ["git", "commit", "-m", "Merge DigitalDreamscape into DreamVault - Conflicts resolved using 'ours' strategy"],
                    cwd=target_dir,
                    capture_output=True,
                    text=True,
                    timeout=TimeoutConstants.HTTP_DEFAULT
                )
                if commit_result.returncode == 0:
                    print("✅ Conflicts resolved and merge committed")
                else:
                    print(f"⚠️ Commit failed: {commit_result.stderr}")
                    return False
            else:
                print("❌ Merge failed and no unmerged files found")
                return False
        else:
            print("✅ Merge completed successfully")
        
        # Push merge branch
        print("\n📤 Step 7: Pushing merge branch...")
        push_result = subprocess.run(
            ["git", "push", "-u", "origin", merge_branch],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_LONG,
            env=git_env
        )
        
        if push_result.returncode != 0:
            print(f"❌ Push failed: {push_result.stderr}")
            return False
        
        print(f"✅ Merge branch pushed: {merge_branch}")
        
        # Cleanup
        print("\n🧹 Step 8: Cleaning up temporary directories...")
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("✅ Cleanup complete")
        
        print("\n" + "=" * 70)
        print("✅ BATCH 2 MERGE COMPLETE")
        print("=" * 70)
        print(f"\n📋 Merge: DigitalDreamscape → DreamVault")
        print(f"🌿 Branch: {merge_branch}")
        print(f"🔗 Create PR: https://github.com/{username}/DreamVault/compare/main...{merge_branch}?expand=1")
        print("\n✅ Ready for PR creation!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during merge: {e}")
        # Cleanup on error
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        return False


def main():
    """Main execution."""
    success = complete_digitaldreamscape_merge()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())






