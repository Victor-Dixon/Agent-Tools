#!/usr/bin/env python3
"""
Push repository to new GitHub account using token authentication.

This tool updates the remote URL to use the new account token and pushes the code.
"""

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

try:
    from src.core.utils.github_utils import get_github_token as get_github_token_ssot
    USE_SSOT = True
except ImportError:
    USE_SSOT = False


def get_token():
    """Get GitHub token for new account."""
    if USE_SSOT:
        try:
            token = get_github_token_ssot(Path(__file__).parent.parent)
            if token:
                return token
        except Exception:
            pass
    
    token = os.getenv("FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN")
    if token:
        return token
    
    token = os.getenv("GITHUB_TOKEN")
    return token


def push_repo(repo_path: Path, new_username: str, repo_name: str, branch: str = None):
    """Push repository to new GitHub account."""
    repo_path = Path(repo_path).resolve()
    
    if not (repo_path / ".git").exists():
        print(f"❌ Not a git repository: {repo_path}")
        return False
    
    # Get token
    token = get_token()
    if not token:
        print("❌ GitHub token not found")
        print("   Set FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN in .env")
        return False
    
    # Get current branch if not specified
    if not branch:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        branch = result.stdout.strip()
    
    # Update remote URL with token
    remote_url = f"https://{token}@github.com/{new_username}/{repo_name}.git"
    
    print(f"🔗 Updating remote URL...")
    subprocess.run(
        ["git", "remote", "set-url", "origin", remote_url],
        cwd=repo_path,
        check=True
    )
    print(f"✅ Remote URL updated")
    
    # Push to new repository
    print(f"\n📤 Pushing {branch} branch to {new_username}/{repo_name}...")
    try:
        subprocess.run(
            ["git", "push", "-u", "origin", branch],
            cwd=repo_path,
            check=True
        )
        print(f"✅ Successfully pushed to new repository!")
        print(f"   URL: https://github.com/{new_username}/{repo_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to push: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python push_to_new_github_account.py <repo_path> <new_username> <repo_name> [branch]")
        print()
        print("Example:")
        print("  python push_to_new_github_account.py d:/MeTuber Victor-Dixon MeTuber v1-enhanced")
        sys.exit(1)
    
    repo_path = Path(sys.argv[1])
    new_username = sys.argv[2]
    repo_name = sys.argv[3]
    branch = sys.argv[4] if len(sys.argv) > 4 else None
    
    success = push_repo(repo_path, new_username, repo_name, branch)
    sys.exit(0 if success else 1)

