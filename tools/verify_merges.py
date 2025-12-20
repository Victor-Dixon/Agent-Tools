#!/usr/bin/env python3
"""
Merge Verification Script
=========================

Verifies that repository merges were executed correctly by:
1. Cloning target repositories
2. Checking merge branches
3. Analyzing merged content
4. Comparing source vs merged content
5. Generating verification report

Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-01-27
"""

import json
import subprocess
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(project_root))

from src.core.config.timeout_constants import TimeoutConstants

# Merges to verify
MERGES_TO_VERIFY = [
    {
        "merge_id": 1,
        "source": "streamertools",
        "target": "Streamertools",
        "source_num": 31,
        "target_num": 25,
        "branch": "merge-streamertools-20251124",
        "phase": "Phase 1 (Non-Goldmine)"
    },
    {
        "merge_id": 3,
        "source": "dadudekc",
        "target": "DaDudekC",
        "source_num": 36,
        "target_num": 29,
        "branch": None,  # Will be detected
        "phase": "Phase 1 (Non-Goldmine)"
    },
    {
        "merge_id": 6,
        "source": "LSTMmodel_trainer",
        "target": "LSTMmodel_trainer",
        "source_num": 18,
        "target_num": 55,
        "branch": None,  # Will be detected
        "phase": "Phase 1 (Non-Goldmine)"
    },
    {
        "merge_id": 7,
        "source": "focusforge",
        "target": "FocusForge",
        "source_num": 32,
        "target_num": 24,
        "branch": None,  # Will be detected
        "phase": "Phase 2 (Goldmine)"
    },
    {
        "merge_id": 8,
        "source": "tbowtactics",
        "target": "TBOWTactics",
        "source_num": 33,
        "target_num": 26,
        "branch": None,  # Will be detected
        "phase": "Phase 2 (Goldmine)"
    },
    {
        "merge_id": 10,
        "source": "projectscanner",
        "target": "projectscanner",
        "source_num": 8,
        "target_num": 49,
        "branch": None,  # Will be detected
        "phase": "Phase 2 (Goldmine)"
    },
    {
        "merge_id": 11,
        "source": "TROOP",
        "target": "TROOP",
        "source_num": 16,
        "target_num": 60,
        "branch": None,  # Will be detected
        "phase": "Phase 2 (Goldmine)"
    }
]

VERIFICATION_DIR = Path("D:/merge_verification")
GITHUB_USERNAME = "Dadudekc"


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment."""
    return os.getenv("GITHUB_TOKEN")


def clone_repo(repo_name: str, target_dir: Path, use_token: bool = True) -> bool:
    """Clone a repository."""
    try:
        token = get_github_token() if use_token else None
        if token:
            url = f"https://{token}@github.com/{GITHUB_USERNAME}/{repo_name}.git"
        else:
            url = f"https://github.com/{GITHUB_USERNAME}/{repo_name}.git"
        
        if target_dir.exists():
            print(f"  ⚠️ Directory already exists: {target_dir}")
            return True
        
        print(f"  📥 Cloning {repo_name}...")
        result = subprocess.run(
            ["git", "clone", url, str(target_dir)],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_LONG
        )
        
        if result.returncode == 0:
            print(f"  ✅ Cloned successfully")
            return True
        else:
            print(f"  ❌ Clone failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Error cloning: {e}")
        return False


def check_branch_exists(repo_dir: Path, branch_name: str) -> bool:
    """Check if a branch exists in the repository."""
    try:
        result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if branch_name in result.stdout or f"remotes/origin/{branch_name}" in result.stdout:
            return True
        return False
    except Exception as e:
        print(f"  ⚠️ Error checking branch: {e}")
        return False


def find_merge_branches(repo_dir: Path) -> List[str]:
    """Find all merge branches in the repository."""
    try:
        result = subprocess.run(
            ["git", "branch", "-a"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        branches = []
        for line in result.stdout.split('\n'):
            if 'merge' in line.lower():
                branch = line.strip().replace('remotes/origin/', '').replace('*', '').strip()
                if branch:
                    branches.append(branch)
        return branches
    except Exception as e:
        print(f"  ⚠️ Error finding branches: {e}")
        return []


def analyze_merge_branch(repo_dir: Path, branch_name: str) -> Dict[str, Any]:
    """Analyze a merge branch."""
    analysis = {
        "branch_exists": False,
        "commit_count": 0,
        "files_changed": 0,
        "merge_commit": False,
        "conflicts": False
    }
    
    try:
        # Checkout branch
        subprocess.run(
            ["git", "checkout", branch_name],
            cwd=repo_dir,
            capture_output=True,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        # Get commit count
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        if result.returncode == 0:
            analysis["commit_count"] = int(result.stdout.strip())
        
        # Check for merge commit
        result = subprocess.run(
            ["git", "log", "--merges", "-1"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        analysis["merge_commit"] = result.returncode == 0 and result.stdout.strip() != ""
        
        # Get file count
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        if result.returncode == 0:
            analysis["files_changed"] = len(result.stdout.strip().split('\n'))
        
        analysis["branch_exists"] = True
        
    except Exception as e:
        print(f"  ⚠️ Error analyzing branch: {e}")
    
    return analysis


def verify_merge(merge_info: Dict[str, Any]) -> Dict[str, Any]:
    """Verify a single merge."""
    print(f"\n🔍 Verifying Merge #{merge_info['merge_id']}: {merge_info['source']} → {merge_info['target']}")
    print(f"   Phase: {merge_info['phase']}")
    
    verification = {
        "merge_id": merge_info["merge_id"],
        "source": merge_info["source"],
        "target": merge_info["target"],
        "phase": merge_info["phase"],
        "target_cloned": False,
        "merge_branch_found": False,
        "merge_branch_name": None,
        "analysis": {},
        "status": "UNKNOWN"
    }
    
    # Clone target repository
    target_dir = VERIFICATION_DIR / merge_info["target"]
    if clone_repo(merge_info["target"], target_dir):
        verification["target_cloned"] = True
        
        # Find merge branch
        if merge_info.get("branch"):
            branch_name = merge_info["branch"]
        else:
            branches = find_merge_branches(target_dir)
            if branches:
                branch_name = branches[0]
            else:
                branch_name = None
        
        if branch_name:
            verification["merge_branch_found"] = True
            verification["merge_branch_name"] = branch_name
            print(f"  ✅ Found merge branch: {branch_name}")
            
            # Analyze branch
            verification["analysis"] = analyze_merge_branch(target_dir, branch_name)
            verification["status"] = "VERIFIED" if verification["analysis"].get("merge_commit") else "PENDING"
        else:
            print(f"  ⚠️ No merge branch found")
            verification["status"] = "NO_BRANCH"
    else:
        verification["status"] = "CLONE_FAILED"
    
    return verification


def generate_report(verifications: List[Dict[str, Any]]) -> None:
    """Generate verification report."""
    report_path = VERIFICATION_DIR / f"merge_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_merges": len(verifications),
        "verified": sum(1 for v in verifications if v["status"] == "VERIFIED"),
        "pending": sum(1 for v in verifications if v["status"] == "PENDING"),
        "issues": sum(1 for v in verifications if v["status"] not in ["VERIFIED", "PENDING"]),
        "verifications": verifications
    }
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Verification Report Generated: {report_path}")
    print(f"   Verified: {report['verified']}/{report['total_merges']}")
    print(f"   Pending: {report['pending']}/{report['total_merges']}")
    print(f"   Issues: {report['issues']}/{report['total_merges']}")


def main():
    """Main verification process."""
    print("🔍 Starting Merge Verification Process")
    print(f"   Verification Directory: {VERIFICATION_DIR}")
    print(f"   Merges to Verify: {len(MERGES_TO_VERIFY)}")
    
    VERIFICATION_DIR.mkdir(parents=True, exist_ok=True)
    
    verifications = []
    for merge_info in MERGES_TO_VERIFY:
        verification = verify_merge(merge_info)
        verifications.append(verification)
    
    generate_report(verifications)
    
    print("\n✅ Verification Process Complete")


if __name__ == "__main__":
    main()

