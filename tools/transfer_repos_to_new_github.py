#!/usr/bin/env python3
"""
Transfer repositories to new GitHub account.

This tool helps migrate repositories from the old GitHub account to the new
FG Professional Development Account by:
1. Creating new repositories on the new account
2. Pushing code to the new repositories
3. Updating local git remotes
4. Optionally archiving/deleting old repositories
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("❌ requests library required. Install with: pip install requests")

from dotenv import load_dotenv
load_dotenv()

# Try to use SSOT github_utils if available
try:
    from src.core.utils.github_utils import get_github_token as get_github_token_ssot
    USE_SSOT = True
except ImportError:
    USE_SSOT = False

project_root = Path(__file__).parent.parent


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment or .env file."""
    # Use SSOT utility (handles priority: new account token → standard token → .env)
    if USE_SSOT:
        try:
            token = get_github_token_ssot(project_root)
            if token:
                return token
        except Exception:
            pass
    
    # Fallback to direct reading
    token = os.getenv("FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN")
    if token:
        return token
    
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return token
    
    env_file = project_root / ".env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    
    return None


def get_github_username(token: str) -> Optional[str]:
    """Get GitHub username from token."""
    headers = {"Authorization": f"token {token}"}
    response = requests.get("https://api.github.com/user", headers=headers)
    if response.status_code == 200:
        return response.json().get("login")
    return None


def create_repository(
    token: str,
    repo_name: str,
    description: str = "",
    private: bool = False,
    auto_init: bool = False
) -> Optional[Dict]:
    """Create a new repository on GitHub."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "name": repo_name,
        "description": description,
        "private": private,
        "auto_init": auto_init
    }
    
    response = requests.post("https://api.github.com/user/repos", headers=headers, json=data)
    
    if response.status_code == 201:
        return response.json()
    else:
        error_msg = response.json().get("message", "Unknown error")
        print(f"❌ Failed to create repository '{repo_name}': {error_msg}")
        if response.status_code == 422:
            print("   → Repository might already exist")
        return None


def get_local_repo_info(repo_path: Path) -> Optional[Dict]:
    """Get information about a local git repository."""
    if not (repo_path / ".git").exists():
        return None
    
    try:
        # Get remote URL
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        remote_url = result.stdout.strip()
        
        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        current_branch = result.stdout.strip()
        
        # Extract repo name from URL
        repo_name = None
        if "github.com" in remote_url:
            parts = remote_url.rstrip(".git").split("/")
            if len(parts) >= 2:
                repo_name = parts[-1]
        
        return {
            "path": str(repo_path),
            "remote_url": remote_url,
            "current_branch": current_branch,
            "repo_name": repo_name
        }
    except subprocess.CalledProcessError:
        return None


def update_remote_url(repo_path: Path, new_username: str, new_repo_name: str) -> bool:
    """Update git remote URL to point to new account."""
    new_url = f"https://github.com/{new_username}/{new_repo_name}.git"
    
    try:
        subprocess.run(
            ["git", "remote", "set-url", "origin", new_url],
            cwd=repo_path,
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to update remote URL: {e}")
        return False


def push_to_new_repo(repo_path: Path, branch: str = "main") -> bool:
    """Push code to new repository."""
    try:
        # Try main first, then master
        for branch_name in [branch, "main", "master"]:
            try:
                subprocess.run(
                    ["git", "push", "-u", "origin", branch_name],
                    cwd=repo_path,
                    check=True,
                    capture_output=True
                )
                print(f"✅ Pushed {branch_name} branch to new repository")
                return True
            except subprocess.CalledProcessError:
                continue
        
        print("❌ Failed to push to new repository")
        return False
    except Exception as e:
        print(f"❌ Error pushing: {e}")
        return False


def transfer_single_repo(
    repo_path: Path,
    token: str,
    new_username: str,
    private: bool = False,
    description: str = ""
) -> bool:
    """Transfer a single repository to new GitHub account."""
    print(f"\n{'='*60}")
    print(f"📦 TRANSFERRING: {repo_path.name}")
    print(f"{'='*60}")
    
    # Get local repo info
    repo_info = get_local_repo_info(repo_path)
    if not repo_info:
        print(f"❌ Not a git repository: {repo_path}")
        return False
    
    repo_name = repo_info.get("repo_name") or repo_path.name
    current_branch = repo_info.get("current_branch", "main")
    
    print(f"   Local path: {repo_path}")
    print(f"   Current remote: {repo_info.get('remote_url')}")
    print(f"   Current branch: {current_branch}")
    print(f"   New repo name: {repo_name}")
    
    # Create new repository
    print(f"\n🔨 Creating repository '{repo_name}' on new account...")
    new_repo = create_repository(token, repo_name, description, private)
    
    if not new_repo:
        print(f"❌ Failed to create repository")
        return False
    
    print(f"✅ Repository created: {new_repo.get('html_url')}")
    
    # Update remote URL
    print(f"\n🔗 Updating remote URL...")
    if not update_remote_url(repo_path, new_username, repo_name):
        return False
    print(f"✅ Remote URL updated")
    
    # Push code
    print(f"\n📤 Pushing code to new repository...")
    if not push_to_new_repo(repo_path, current_branch):
        return False
    
    print(f"\n✅ Repository transfer complete!")
    print(f"   New URL: {new_repo.get('html_url')}")
    return True


def list_local_repos(base_path: Path) -> List[Path]:
    """Find all local git repositories."""
    repos = []
    
    for item in base_path.iterdir():
        if item.is_dir() and (item / ".git").exists():
            repos.append(item)
    
    return repos


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Transfer repositories to new GitHub account"
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        help="Path to repository to transfer (default: current directory)"
    )
    parser.add_argument(
        "--list-repos",
        action="store_true",
        help="List all local repositories in current directory"
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create private repositories (default: public)"
    )
    parser.add_argument(
        "--description",
        default="",
        help="Repository description"
    )
    parser.add_argument(
        "--new-name",
        help="New repository name (default: same as current)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 GITHUB REPOSITORY TRANSFER TOOL")
    print("=" * 60)
    print()
    
    # Get token
    token = get_github_token()
    if not token:
        print("❌ GitHub token not found")
        print()
        print("💡 Setup options:")
        print("   1. Set FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN")
        print("   2. Set GITHUB_TOKEN")
        print("   3. Add token to .env file")
        return 1
    
    # Get username
    print("🔍 Getting GitHub username...")
    username = get_github_username(token)
    if not username:
        print("❌ Failed to get GitHub username. Check token permissions.")
        return 1
    
    print(f"✅ Authenticated as: {username}")
    print()
    
    # List repos mode
    if args.list_repos:
        print("📋 LOCAL REPOSITORIES:")
        print()
        base_path = Path(args.repo_path) if args.repo_path else Path.cwd()
        repos = list_local_repos(base_path)
        
        if not repos:
            print("   No git repositories found")
        else:
            for repo in repos:
                info = get_local_repo_info(repo)
                if info:
                    print(f"   📦 {repo.name}")
                    print(f"      Path: {repo}")
                    print(f"      Remote: {info.get('remote_url', 'N/A')}")
                    print(f"      Branch: {info.get('current_branch', 'N/A')}")
                    print()
        return 0
    
    # Transfer mode
    if not args.repo_path:
        repo_path = Path.cwd()
    else:
        repo_path = Path(args.repo_path)
    
    if not repo_path.exists():
        print(f"❌ Path not found: {repo_path}")
        return 1
    
    repo_name = args.new_name or None
    if repo_name:
        # Custom name provided
        description = args.description or f"Transferred from old account"
        success = transfer_single_repo(
            repo_path,
            token,
            username,
            args.private,
            description
        )
        # Rename after creation (would need to delete and recreate)
        print("⚠️  Note: Custom names require manual repository creation")
    else:
        success = transfer_single_repo(
            repo_path,
            token,
            username,
            args.private,
            args.description
        )
    
    if success:
        print("\n" + "=" * 60)
        print("✅ TRANSFER COMPLETE!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ TRANSFER FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

