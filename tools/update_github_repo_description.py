#!/usr/bin/env python3
"""
Update GitHub Repository Description Tool
=========================================

Updates repository description and other metadata for repositories
in the Victor-Dixon GitHub account using GitHub API.

Author: Agent-3 (Infrastructure & DevOps Specialist)
Created: 2025-12-20
V2 Compliant: Yes (<400 lines, type hints, documented)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.core.utils.github_utils import get_github_token
    GITHUB_UTILS_AVAILABLE = True
except ImportError:
    GITHUB_UTILS_AVAILABLE = False


def get_github_token_fallback() -> Optional[str]:
    """Fallback token getter if github_utils not available."""
    import os
    token = os.getenv("FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN") or \
            os.getenv("GITHUB_TOKEN") or \
            os.getenv("GH_TOKEN")
    return token


def update_repository_description(
    owner: str,
    repo: str,
    description: str,
    token: Optional[str] = None,
    homepage: Optional[str] = None,
    private: Optional[bool] = None,
) -> Optional[Dict[str, Any]]:
    """
    Update repository description and metadata using GitHub API.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
        description: New repository description
        token: GitHub personal access token
        homepage: Optional homepage URL
        private: Optional privacy setting
        
    Returns:
        Updated repository info dict, or None if failed
    """
    if not REQUESTS_AVAILABLE:
        print("❌ Error: 'requests' library not installed")
        print("   Install with: pip install requests")
        return None
    
    # Get token
    if GITHUB_UTILS_AVAILABLE:
        token = token or get_github_token()
    else:
        token = token or get_github_token_fallback()
    
    if not token:
        print("❌ Error: GitHub token not found")
        print("   Set GITHUB_TOKEN or FG_PROFESSIONAL_DEVELOPMENT_ACCOUNT_GITHUB_TOKEN environment variable")
        return None
    
    # Prepare update payload
    update_data: Dict[str, Any] = {
        "description": description,
    }
    
    if homepage is not None:
        update_data["homepage"] = homepage
    if private is not None:
        update_data["private"] = private
    
    # GitHub API endpoint for updating repository
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    # Send PATCH request
    response = requests.patch(url, headers=headers, json=update_data)
    
    if response.status_code == 200:
        repo_data = response.json()
        print(f"✅ Updated repository: {owner}/{repo}")
        print(f"   Description: {repo_data.get('description', 'N/A')}")
        return repo_data
    else:
        error_msg = response.json().get("message", "Unknown error")
        print(f"❌ Failed to update repository '{owner}/{repo}': {error_msg}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 404:
            print("   → Repository not found or no access")
        elif response.status_code == 403:
            print("   → Token may not have write access to repository")
        return None


def update_multiple_repos(
    repos_config: Dict[str, Dict[str, str]],
    token: Optional[str] = None,
) -> Dict[str, bool]:
    """
    Update multiple repositories from configuration.
    
    Args:
        repos_config: Dict mapping repo keys to {owner, repo, description, ...}
        token: GitHub token
        
    Returns:
        Dict mapping repo keys to success status
    """
    results = {}
    
    for repo_key, repo_info in repos_config.items():
        owner = repo_info.get("owner")
        repo = repo_info.get("repo")
        description = repo_info.get("description", "")
        homepage = repo_info.get("homepage")
        private = repo_info.get("private")
        
        if not owner or not repo:
            print(f"⚠️  Skipping {repo_key}: missing owner or repo")
            results[repo_key] = False
            continue
        
        # Convert private string to bool if provided
        private_bool = None
        if private:
            private_bool = private.lower() in ("true", "1", "yes")
        
        success = update_repository_description(
            owner=owner,
            repo=repo,
            description=description,
            token=token,
            homepage=homepage,
            private=private_bool,
        ) is not None
        
        results[repo_key] = success
        print()  # Blank line between repos
    
    return results


def load_config_from_json(config_path: Path) -> Optional[Dict[str, Dict[str, str]]]:
    """Load repository configuration from JSON file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading config from {config_path}: {e}")
        return None


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Update GitHub repository descriptions and metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update single repository
  python tools/update_github_repo_description.py \\
    --owner Victor-Dixon \\
    --repo Dream.os \\
    --description "Multi-agent AI system for automated development and coordination"
  
  # Update multiple repositories from JSON config
  python tools/update_github_repo_description.py \\
    --config repos_descriptions.json
  
  # Update with homepage
  python tools/update_github_repo_description.py \\
    --owner Victor-Dixon \\
    --repo Dream.os \\
    --description "Description here" \\
    --homepage "https://dream.os"
        """
    )
    
    parser.add_argument(
        "--owner",
        help="Repository owner (username or organization)"
    )
    parser.add_argument(
        "--repo",
        help="Repository name"
    )
    parser.add_argument(
        "--description",
        help="Repository description"
    )
    parser.add_argument(
        "--homepage",
        help="Repository homepage URL"
    )
    parser.add_argument(
        "--private",
        choices=["true", "false"],
        help="Repository privacy (true/false)"
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="JSON config file with multiple repositories (format: {\"key\": {\"owner\": \"...\", \"repo\": \"...\", \"description\": \"...\"}})"
    )
    parser.add_argument(
        "--token",
        help="GitHub personal access token (optional, uses env vars if not provided)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.config:
        # Load from config file
        config = load_config_from_json(args.config)
        if not config:
            return 1
        
        print(f"📝 Updating {len(config)} repositories from config...")
        print()
        results = update_multiple_repos(config, token=args.token)
        
        # Summary
        success_count = sum(1 for v in results.values() if v)
        print(f"\n{'='*60}")
        print(f"Summary: {success_count}/{len(results)} repositories updated successfully")
        
        return 0 if success_count == len(results) else 1
    
    elif args.owner and args.repo and args.description:
        # Single repository update
        private_bool = None
        if args.private:
            private_bool = args.private.lower() == "true"
        
        result = update_repository_description(
            owner=args.owner,
            repo=args.repo,
            description=args.description,
            token=args.token,
            homepage=args.homepage,
            private=private_bool,
        )
        
        return 0 if result else 1
    
    else:
        parser.print_help()
        print("\n❌ Error: Either provide --config OR --owner, --repo, and --description")
        return 1


if __name__ == "__main__":
    sys.exit(main())
