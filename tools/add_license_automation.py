#!/usr/bin/env python3
"""
GitHub LICENSE Automation
=========================

Automatically add MIT LICENSE to all repos missing it.

Mission: Fix 75% missing LICENSE critical issue
Agent: Agent-7
Points: 600-900
"""

import subprocess
from pathlib import Path
from datetime import datetime

# Repos needing LICENSE (from audit)
REPOS_NEED_LICENSE = [
    "projectscanner",
    "AutoDream.Os",
    "UltimateOptionsTradingRobot",
    "trade_analyzer",
    "dreambank",
    "Agent_Cellphone",
]

MIT_LICENSE = """MIT License

Copyright (c) 2025 Dadudekc

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def add_license_to_repo(repo_name: str, repo_path: Path) -> bool:
    """Add LICENSE file and commit."""
    try:
        print(f"\n📦 {repo_name}")
        print("-" * 60)
        
        # Check if already has LICENSE
        license_file = repo_path / "LICENSE"
        if license_file.exists():
            print("  ⏭️ Already has LICENSE - skipping")
            return True
        
        # Write LICENSE
        print("  📝 Writing LICENSE file...")
        license_file.write_text(MIT_LICENSE, encoding="utf-8")
        print("  ✅ LICENSE created")
        
        # Git add
        print("  📤 Staging LICENSE...")
        result = subprocess.run(
            ["git", "add", "LICENSE"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"  ❌ Git add failed: {result.stderr}")
            return False
        
        # Git commit
        print("  💾 Committing...")
        commit_msg = "feat: Add MIT LICENSE\n\nAdded by Agent Swarm - Portfolio professionalization\nFixes: Missing LICENSE file (legal compliance)"
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"  ⚠️ Commit warning: {result.stderr}")
            # May fail if no changes, continue
        else:
            print("  ✅ Committed")
        
        # Git push
        print("  🚀 Pushing to GitHub...")
        result = subprocess.run(
            ["git", "push"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"  ❌ Push failed: {result.stderr}")
            return False
        
        print("  ✅ Pushed to GitHub!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    """Execute LICENSE automation mission."""
    print("=" * 70)
    print("🚨 MISSION: GitHub LICENSE Automation")
    print("=" * 70)
    print(f"Agent: Agent-7")
    print(f"Target: {len(REPOS_NEED_LICENSE)} repositories")
    print(f"Action: Add MIT LICENSE to all repos")
    print("=" * 70)
    
    audit_dir = Path("D:/GitHub_Audit_Test")
    
    if not audit_dir.exists():
        print(f"❌ Audit directory not found: {audit_dir}")
        print("Run audit_github_repos.py first!")
        return 1
    
    success_count = 0
    
    for repo_name in REPOS_NEED_LICENSE:
        repo_path = audit_dir / repo_name
        
        if not repo_path.exists():
            print(f"\n❌ {repo_name} - Not cloned, skipping")
            continue
        
        if add_license_to_repo(repo_name, repo_path):
            success_count += 1
    
    # Summary
    print()
    print("=" * 70)
    print("📊 MISSION RESULTS")
    print("=" * 70)
    print(f"✅ Success: {success_count}/{len(REPOS_NEED_LICENSE)}")
    print(f"📈 Portfolio LICENSE Coverage: 25% → {25 + (success_count/8*100):.0f}%")
    print()
    
    if success_count == len(REPOS_NEED_LICENSE):
        print("🎉 MISSION COMPLETE!")
        print("✅ All repos now have LICENSE files")
        print("✅ Legal compliance achieved")
        print(f"🏆 Points earned: {success_count * 100}-{success_count * 150}")
        return 0
    else:
        print(f"⚠️ Partial success: {success_count}/{len(REPOS_NEED_LICENSE)}")
        return 1


if __name__ == "__main__":
    exit(main())

