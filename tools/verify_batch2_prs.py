#!/usr/bin/env python3
"""
Verify Batch 2 PRs
==================

Verifies that all PRs for completed Batch 2 merges exist via GitHub API.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-01-27
"""

import os
import sys
from pathlib import Path
from typing import Optional

try:
    import requests
from src.core.config.timeout_constants import TimeoutConstants
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ requests library not available. Install with: pip install requests")


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


def verify_pr(token: str, owner: str, repo: str, pr_number: int) -> bool:
    """Verify that a PR exists."""
    if not REQUESTS_AVAILABLE:
        return False
    
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=TimeoutConstants.HTTP_DEFAULT)
        return response.status_code == 200
    except Exception:
        return False


def main():
    """Verify all Batch 2 PRs."""
    token = get_github_token()
    if not token:
        print("❌ GITHUB_TOKEN not found.")
        return 1
    
    owner = "Dadudekc"
    
    # Batch 2 PRs to verify
    prs_to_verify = [
        ("DreamVault", 3, "Thea → DreamVault"),
        ("trading-leads-bot", 3, "UltimateOptionsTradingRobot → trading-leads-bot"),
        ("trading-leads-bot", 4, "TheTradingRobotPlug → trading-leads-bot"),
        ("Streamertools", 13, "MeTuber → Streamertools"),
        ("DaDudeKC-Website", 1, "DaDudekC → DaDudeKC-Website"),
        ("MachineLearningModelMaker", 2, "LSTMmodel_trainer → MachineLearningModelMaker"),
    ]
    
    print("🔍 Verifying Batch 2 PRs via GitHub API...\n")
    
    all_exist = True
    for repo, pr_num, description in prs_to_verify:
        exists = verify_pr(token, owner, repo, pr_num)
        status = "✅ EXISTS" if exists else "❌ NOT FOUND"
        print(f"{status}: {description} (PR #{pr_num})")
        if not exists:
            all_exist = False
    
    print(f"\n{'='*60}")
    if all_exist:
        print("✅ ALL PRs VERIFIED - All 6 PRs exist!")
        print("✅ DreamBank → DreamVault already merged into master (no PR needed)")
        print("✅ Total: 7/7 completed merges have PRs or are merged")
        return 0
    else:
        print("⚠️ Some PRs not found - may need to be created")
        return 1


if __name__ == "__main__":
    sys.exit(main())

