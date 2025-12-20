#!/usr/bin/env python3
"""
GitHub Create Repository and Push Tool
======================================

Creates a new GitHub repository and pushes local code to it.
Uses GitHub API to create repo, then pushes code via git.

Author: Agent-3 (Infrastructure & DevOps Specialist)
Created: 2025-11-22
V2 Compliant: <400 lines, type hints, documented
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


def get_github_token() -> Optional[str]:
    """Get GitHub token from environment or .env file."""
    # Check environment variable
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if token:
        return token
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        try:
            with open(env_file, "r") as f:
                for line in f:
                    if line.startswith("GITHUB_TOKEN=") or line.startswith("GH_TOKEN="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    
    return None


def create_github_repo(
    repo_name: str,
    description: str = "",
    private: bool = False,
    token: Optional[str] = None,
) -> Optional[dict]:
    """
    Create a new GitHub repository using GitHub API.
    
    Args:
        repo_name: Name of the repository
        description: Repository description
        private: Whether repository should be private
        token: GitHub personal access token
        
    Returns:
        Repository info dict with clone_url, or None if failed
    """
    if not REQUESTS_AVAILABLE:
        print("❌ Error: 'requests' library not installed")
        print("   Install with: pip install requests")
        return None
    
    token = token or get_github_token()
    if not token:
        print("❌ Error: GitHub token not found")
        print("   Set GITHUB_TOKEN environment variable or add to .env file")
        return None
    
    # Get username from token or API
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    # Get authenticated user
    user_response = requests.get("https://api.github.com/user", headers=headers)
    if user_response.status_code != 200:
        print(f"❌ Error: Failed to authenticate with GitHub API")
        print(f"   Status: {user_response.status_code}")
        return None
    
    user_data = user_response.json()
    username = user_data.get("login")
    
    # Create repository
    repo_data = {
        "name": repo_name,
        "description": description,
        "private": private,
        "auto_init": False,
    }
    
    print(f"🔨 Creating repository '{repo_name}' on GitHub...")
    create_response = requests.post(
        f"https://api.github.com/user/repos",
        headers=headers,
        json=repo_data,
    )
    
    if create_response.status_code == 201:
        repo_info = create_response.json()
        print(f"✅ Repository created successfully!")
        print(f"   URL: {repo_info['html_url']}")
        print(f"   Clone URL: {repo_info['clone_url']}")
        return repo_info
    elif create_response.status_code == 422:
        error_data = create_response.json()
        if "already exists" in str(error_data).lower():
            print(f"⚠️ Repository '{repo_name}' already exists")
            # Try to get existing repo info
            get_response = requests.get(
                f"https://api.github.com/repos/{username}/{repo_name}",
                headers=headers,
            )
            if get_response.status_code == 200:
                repo_info = get_response.json()
                print(f"✅ Using existing repository")
                print(f"   URL: {repo_info['html_url']}")
                print(f"   Clone URL: {repo_info['clone_url']}")
                return repo_info
        print(f"❌ Error: {error_data}")
        return None
    else:
        print(f"❌ Error: Failed to create repository")
        print(f"   Status: {create_response.status_code}")
        print(f"   Response: {create_response.text}")
        return None


def push_to_github(
    repo_url: str,
    branch: str = "main",
    force: bool = False,
    remote_name: str = "origin",
) -> bool:
    """
    Push local code to GitHub repository.
    
    Args:
        repo_url: GitHub repository URL (HTTPS or SSH)
        branch: Branch name to push
        force: Whether to force push
        remote_name: Remote name
        
    Returns:
        True if successful, False otherwise
    """
    repo_path = Path.cwd()
    
    # Check if git repo exists
    if not (repo_path / ".git").exists():
        print("⚠️ Not a git repository. Initializing...")
        try:
            subprocess.run(["git", "init"], check=True, capture_output=True)
            print("✅ Git repository initialized")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error initializing git: {e}")
            return False
    
    # Add remote
    try:
        # Remove existing remote if it exists
        subprocess.run(
            ["git", "remote", "remove", remote_name],
            capture_output=True,
        )
    except Exception:
        pass
    
    try:
        subprocess.run(
            ["git", "remote", "add", remote_name, repo_url],
            check=True,
            capture_output=True,
        )
        print(f"✅ Remote '{remote_name}' added: {repo_url}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error adding remote: {e}")
        return False
    
    # Add all files
    try:
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        print("✅ Files staged")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error staging files: {e}")
        return False
    
    # Commit
    try:
        subprocess.run(
            ["git", "commit", "-m", "Initial commit: Agent-3 workspace cleanup and infrastructure work"],
            check=True,
            capture_output=True,
        )
        print("✅ Changes committed")
    except subprocess.CalledProcessError as e:
        # Might fail if no changes
        if "nothing to commit" in str(e):
            print("ℹ️ No changes to commit")
        else:
            print(f"⚠️ Commit warning: {e}")
    
    # Create branch if needed
    try:
        subprocess.run(
            ["git", "checkout", "-b", branch],
            capture_output=True,
        )
    except Exception:
        # Branch might already exist
        try:
            subprocess.run(
                ["git", "checkout", branch],
                capture_output=True,
            )
        except Exception:
            pass
    
    # Push
    push_cmd = ["git", "push", remote_name, branch]
    if force:
        push_cmd.append("--force")
    
    try:
        print(f"📤 Pushing to {remote_name}/{branch}...")
        result = subprocess.run(
            push_cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        print("✅ Push successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error pushing: {e}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create GitHub repository and push code"
    )
    parser.add_argument(
        "repo_name",
        help="Name of the repository to create",
    )
    parser.add_argument(
        "--description",
        "-d",
        default="Agent-3 Infrastructure & DevOps Repository",
        help="Repository description",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create private repository",
    )
    parser.add_argument(
        "--branch",
        "-b",
        default="main",
        help="Branch name to push (default: main)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force push (overwrites remote branch)",
    )
    parser.add_argument(
        "--token",
        "-t",
        help="GitHub personal access token (or set GITHUB_TOKEN env var)",
    )
    parser.add_argument(
        "--skip-create",
        action="store_true",
        help="Skip repository creation (only push to existing repo)",
    )
    parser.add_argument(
        "--repo-url",
        help="Existing repository URL (if --skip-create)",
    )
    
    args = parser.parse_args()
    
    # Create repository
    repo_info = None
    if not args.skip_create:
        repo_info = create_github_repo(
            args.repo_name,
            description=args.description,
            private=args.private,
            token=args.token,
        )
        if not repo_info:
            return 1
        repo_url = repo_info["clone_url"]
    else:
        if not args.repo_url:
            print("❌ Error: --repo-url required when using --skip-create")
            return 1
        repo_url = args.repo_url
    
    # Push code
    success = push_to_github(
        repo_url,
        branch=args.branch,
        force=args.force,
    )
    
    if success:
        print("\n✅ Repository created and code pushed successfully!")
        if repo_info:
            print(f"🌐 View at: {repo_info['html_url']}")
        return 0
    else:
        print("\n❌ Failed to push code")
        return 1


if __name__ == "__main__":
    sys.exit(main())


