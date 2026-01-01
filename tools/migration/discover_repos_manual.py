#!/usr/bin/env python3
"""
Manual Repository Discovery Helper

Since GitHub API is blocked (spam account), this helps you:
1. Manually discover repositories from GitHub web interface
2. Create a repository list file
3. Clone them all locally

Usage:
    # Step 1: Visit https://github.com/Victor-Dixon?tab=repositories
    # Step 2: Copy repository names and save to repos.txt
    # Step 3: Run this script to clone them all
    python tools/migration/discover_repos_manual.py --clone-list repos.txt
"""

import argparse
import subprocess
import sys
from pathlib import Path


def clone_repo(repo_name: str, old_account: str, target_dir: Path) -> bool:
    """
    Clone a single repository.

    Args:
        repo_name: Repository name
        old_account: Old GitHub account name
        target_dir: Target directory for clones

    Returns:
        True if successful
    """
    repo_path = target_dir / repo_name

    if repo_path.exists():
        print(f"⚠️  {repo_name} already exists, skipping")
        return True

    clone_url = f"https://github.com/{old_account}/{repo_name}.git"
    print(f"📥 Cloning {repo_name}...")

    try:
        result = subprocess.run(
            ["git", "clone", clone_url, str(repo_path)],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode == 0:
            # Remove old remote to prevent accidental pushes
            subprocess.run(
                ["git", "remote", "remove", "origin"],
                cwd=repo_path,
                capture_output=True,
            )
            print(f"✅ {repo_name} cloned successfully")
            return True
        else:
            print(f"❌ Failed to clone {repo_name}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print(f"⏱️  {repo_name} clone timed out")
        return False
    except Exception as e:
        print(f"❌ Error cloning {repo_name}: {e}")
        return False


def clone_from_list(repo_list_file: str, old_account: str, target_dir: Path):
    """
    Clone repositories from a list file.

    Args:
        repo_list_file: Path to file with repository names (one per line)
        old_account: Old GitHub account name
        target_dir: Target directory for clones
    """
    repo_list_path = Path(repo_list_file).expanduser()
    if not repo_list_path.exists():
        print(f"❌ Error: File not found: {repo_list_file}")
        print(f"\n💡 Create a file with repository names, one per line:")
        print(f"   Example repos.txt:")
        print(f"   AgentTools")
        print(f"   my-other-repo")
        print(f"   another-project")
        return

    with open(repo_list_path, "r") as f:
        repos = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

    if not repos:
        print(f"❌ No repositories found in {repo_list_file}")
        return

    print(f"📋 Found {len(repos)} repositories to clone\n")
    print(f"📁 Target directory: {target_dir}\n")

    successful = 0
    failed = 0

    for repo_name in repos:
        if clone_repo(repo_name, old_account, target_dir):
            successful += 1
        else:
            failed += 1
        print()  # Blank line between repos

    print(f"\n📊 Summary:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📁 Location: {target_dir}")


def create_template_list(output_file: str = "repos.txt"):
    """Create a template repository list file."""
    template = """# Repository List for Migration
# Add one repository name per line (without .git extension)
# Lines starting with # are comments

# Example:
# AgentTools
# my-project
# another-repo

"""
    output_path = Path(output_file)
    if output_path.exists():
        print(f"⚠️  {output_file} already exists, not overwriting")
        return

    output_path.write_text(template)
    print(f"✅ Created template: {output_file}")
    print(f"   Edit this file and add your repository names")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manually discover and clone repositories (no API needed)"
    )
    parser.add_argument(
        "--clone-list",
        help="File containing repository names to clone (one per line)",
    )
    parser.add_argument(
        "--old-account",
        default="Victor-Dixon",
        help="Old GitHub account name (default: Victor-Dixon)",
    )
    parser.add_argument(
        "--target-dir",
        default="/home/dream/Development/projects/repositories/old-account",
        help="Target directory for cloned repositories",
    )
    parser.add_argument(
        "--create-template",
        action="store_true",
        help="Create a template repos.txt file",
    )
    parser.add_argument(
        "--instructions",
        action="store_true",
        help="Show instructions for manual discovery",
    )

    args = parser.parse_args()

    if args.instructions:
        print("""
🔍 Manual Repository Discovery Instructions

Since GitHub API is blocked, follow these steps:

1. 📝 Visit your GitHub profile repositories page:
   https://github.com/Victor-Dixon?tab=repositories

2. 📋 Copy repository names:
   - Scroll through all your repositories
   - Copy each repository name (the part after /)
   - Example: For https://github.com/Victor-Dixon/AgentTools
             The name is: AgentTools

3. 💾 Create repos.txt file:
   python tools/migration/discover_repos_manual.py --create-template
   
   Then edit repos.txt and add one repository name per line:
   AgentTools
   my-other-repo
   another-project

4. 📥 Clone all repositories:
   python tools/migration/discover_repos_manual.py --clone-list repos.txt

5. ✅ Review repositories in:
   /home/dream/Development/projects/repositories/old-account

💡 Tips:
- You can also use browser extensions to export repository lists
- Or manually copy-paste from GitHub's repository list
- Private repos will fail if you don't have access (that's expected)
        """)
        return

    if args.create_template:
        create_template_list()
        return

    if args.clone_list:
        target_dir = Path(args.target_dir).expanduser().resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        clone_from_list(args.clone_list, args.old_account, target_dir)
    else:
        parser.print_help()
        print("\n💡 Quick start:")
        print("   1. python tools/migration/discover_repos_manual.py --instructions")
        print("   2. python tools/migration/discover_repos_manual.py --create-template")
        print("   3. Edit repos.txt with your repository names")
        print("   4. python tools/migration/discover_repos_manual.py --clone-list repos.txt")


if __name__ == "__main__":
    main()


