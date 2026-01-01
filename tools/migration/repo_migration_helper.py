#!/usr/bin/env python3
"""
Repository Migration Helper - Local Review Workflow

Helps migrate repositories from old GitHub account to local storage
for review before publishing to new account.

This script:
1. Clones repositories locally (no push to new account)
2. Organizes them in a review directory
3. Tracks review status
4. Helps prepare for selective publication

Usage:
    python tools/migration/repo_migration_helper.py --clone-list repos.txt
    python tools/migration/repo_migration_helper.py --status
    python tools/migration/repo_migration_helper.py --ready-to-publish
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class RepoMigrationHelper:
    """Helps manage repository migration and review workflow."""

    def __init__(self, review_dir: str = "/home/dream/Development/projects/repositories/old-account", old_account: str = "Victor-Dixon"):
        """
        Initialize migration helper.

        Args:
            review_dir: Directory to store repositories for review
            old_account: Old GitHub account name
        """
        self.review_dir = Path(review_dir).expanduser().resolve()
        self.review_dir.mkdir(parents=True, exist_ok=True)
        self.status_file = self.review_dir / "migration_status.json"
        self.old_account = old_account
        self.status = self._load_status()

    def _load_status(self) -> Dict:
        """Load migration status from file."""
        if self.status_file.exists():
            try:
                with open(self.status_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"repos": {}}
        return {"repos": {}}

    def _save_status(self):
        """Save migration status to file."""
        with open(self.status_file, "w") as f:
            json.dump(self.status, f, indent=2)

    def clone_repo(self, repo_name: str, clone_url: Optional[str] = None) -> bool:
        """
        Clone a repository locally for review.

        Args:
            repo_name: Repository name
            clone_url: Optional full clone URL (if not provided, constructs from old_account)

        Returns:
            True if successful, False otherwise
        """
        if not clone_url:
            if not self.old_account:
                print(f"Error: Need old_account or clone_url for {repo_name}")
                return False
            clone_url = f"https://github.com/{self.old_account}/{repo_name}.git"

        repo_path = self.review_dir / repo_name

        if repo_path.exists():
            print(f"⚠️  {repo_name} already exists, skipping clone")
            return True

        print(f"📥 Cloning {repo_name}...")
        try:
            subprocess.run(
                ["git", "clone", clone_url, str(repo_path)],
                check=True,
                capture_output=True,
                text=True,
            )

            # Update remote to remove old account reference
            subprocess.run(
                ["git", "remote", "remove", "origin"],
                cwd=repo_path,
                capture_output=True,
            )

            # Initialize status
            if "repos" not in self.status:
                self.status["repos"] = {}

            self.status["repos"][repo_name] = {
                "cloned_at": datetime.now().isoformat(),
                "status": "cloned",
                "review_status": "pending",
                "ready_for_publication": False,
                "notes": "",
                "path": str(repo_path),
            }
            self._save_status()

            print(f"✅ {repo_name} cloned successfully")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clone {repo_name}: {e.stderr}")
            return False

    def clone_from_list(self, repo_list_file: str):
        """
        Clone multiple repositories from a list file.

        Args:
            repo_list_file: Path to file with repository names/URLs (one per line)
        """
        repo_list_path = Path(repo_list_file).expanduser()
        if not repo_list_path.exists():
            print(f"Error: File not found: {repo_list_file}")
            return

        with open(repo_list_path, "r") as f:
            repos = [line.strip() for line in f if line.strip() and not line.startswith("#")]

        print(f"📋 Found {len(repos)} repositories to clone\n")

        for repo_line in repos:
            # Handle both formats: "repo-name" or "https://github.com/account/repo.git"
            if repo_line.startswith("http"):
                # Extract repo name from URL
                repo_name = repo_line.split("/")[-1].replace(".git", "")
                self.clone_repo(repo_name, repo_line)
            else:
                self.clone_repo(repo_line)

    def update_review_status(
        self, repo_name: str, status: str, notes: str = "", ready: bool = False
    ):
        """
        Update review status for a repository.

        Args:
            repo_name: Repository name
            status: Review status (pending, reviewing, needs-work, ready, archived)
            notes: Review notes
            ready: Whether ready for publication
        """
        if repo_name not in self.status.get("repos", {}):
            print(f"⚠️  {repo_name} not found in status. Cloning first...")
            self.clone_repo(repo_name)

        self.status["repos"][repo_name]["review_status"] = status
        self.status["repos"][repo_name]["notes"] = notes
        self.status["repos"][repo_name]["ready_for_publication"] = ready
        self.status["repos"][repo_name]["updated_at"] = datetime.now().isoformat()
        self._save_status()

        print(f"✅ Updated {repo_name}: {status}")

    def list_status(self):
        """List all repositories and their review status."""
        repos = self.status.get("repos", {})
        if not repos:
            print("No repositories in review queue.")
            return

        print(f"\n📊 Repository Review Status ({len(repos)} total)\n")
        print(f"{'Repository':<40} {'Status':<15} {'Ready':<8} {'Notes'}")
        print("-" * 100)

        for repo_name, info in sorted(repos.items()):
            status = info.get("review_status", "unknown")
            ready = "✅" if info.get("ready_for_publication") else "❌"
            notes = info.get("notes", "")[:40]
            print(f"{repo_name:<40} {status:<15} {ready:<8} {notes}")

    def list_ready_to_publish(self):
        """List repositories ready for publication."""
        repos = self.status.get("repos", {})
        ready_repos = {
            name: info
            for name, info in repos.items()
            if info.get("ready_for_publication", False)
        }

        if not ready_repos:
            print("No repositories marked as ready for publication.")
            return

        print(f"\n✅ Repositories Ready for Publication ({len(ready_repos)} total)\n")
        for repo_name, info in sorted(ready_repos.items()):
            print(f"  • {repo_name}")
            print(f"    Path: {info.get('path')}")
            if info.get("notes"):
                print(f"    Notes: {info.get('notes')}")
            print()

    def generate_publish_script(self, output_file: str = "publish_ready_repos.sh"):
        """Generate a script to publish ready repositories to new account."""
        repos = self.status.get("repos", {})
        ready_repos = {
            name: info
            for name, info in repos.items()
            if info.get("ready_for_publication", False)
        }

        if not ready_repos:
            print("No repositories ready for publication.")
            return

        script_path = Path(output_file)
        with open(script_path, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Auto-generated script to publish ready repositories\n")
            f.write("# Review and update NEW_ACCOUNT before running\n\n")
            f.write("NEW_ACCOUNT=\"your-new-github-account\"\n\n")

            for repo_name, info in sorted(ready_repos.items()):
                repo_path = info.get("path", "")
                f.write(f"# Publishing {repo_name}\n")
                f.write(f"cd {repo_path}\n")
                f.write(f"gh repo create $NEW_ACCOUNT/{repo_name} --private --source=. --remote=new-origin\n")
                f.write(f"git push new-origin --all\n")
                f.write(f"git push new-origin --tags\n")
                f.write(f"echo \"✅ {repo_name} published\"\n\n")

        script_path.chmod(0o755)
        print(f"✅ Generated publish script: {script_path}")
        print(f"   Review and update NEW_ACCOUNT before running")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Repository migration helper for local review workflow"
    )
    parser.add_argument(
        "--clone-list",
        help="File containing list of repositories to clone (one per line)",
    )
    parser.add_argument(
        "--clone",
        help="Clone a single repository (provide name or full URL)",
    )
    parser.add_argument(
        "--review-dir",
        default="~/repo_review",
        help="Directory to store repositories for review (default: ~/repo_review)",
    )
    parser.add_argument(
        "--old-account",
        default="",
        help="Old GitHub account name (for constructing clone URLs)",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show review status of all repositories",
    )
    parser.add_argument(
        "--ready",
        action="store_true",
        help="List repositories ready for publication",
    )
    parser.add_argument(
        "--mark-ready",
        help="Mark a repository as ready for publication",
    )
    parser.add_argument(
        "--mark-status",
        nargs=3,
        metavar=("REPO", "STATUS", "NOTES"),
        help="Update review status: REPO STATUS 'NOTES'",
    )
    parser.add_argument(
        "--generate-publish-script",
        action="store_true",
        help="Generate script to publish ready repositories",
    )

    args = parser.parse_args()

    helper = RepoMigrationHelper(
        review_dir=args.review_dir, old_account=args.old_account
    )

    if args.clone_list:
        helper.clone_from_list(args.clone_list)
    elif args.clone:
        helper.clone_repo(args.clone)
    elif args.status:
        helper.list_status()
    elif args.ready:
        helper.list_ready_to_publish()
    elif args.mark_ready:
        helper.update_review_status(args.mark_ready, "ready", ready=True)
    elif args.mark_status:
        repo, status, notes = args.mark_status
        helper.update_review_status(repo, status, notes)
    elif args.generate_publish_script:
        helper.generate_publish_script()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

