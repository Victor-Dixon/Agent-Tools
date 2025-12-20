#!/usr/bin/env python3
"""
Git Commit Verifier - Prevent Validation of Non-Existent Work
==============================================================

Verifies that claimed work actually exists in git history.
Prevents validating conversations/planning as actual implementation.

Use before QA validation to ensure work is real!

Author: Agent-8 (Operations & Support Specialist)
Created: 2025-10-13 (learned from integrity correction)
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_git_command(args: list[str], cwd: Path | None = None) -> str:
    """Run git command and return output."""
    try:
        result = subprocess.run(
            ["git"] + args, capture_output=True, text=True, cwd=cwd or Path.cwd()
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Git command failed: {e}")
        return ""


def check_commits_today(file_pattern: str = None) -> list[dict[str, str]]:
    """Check for commits made today."""
    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")

    # Git log for today
    args = ["log", "--since", today,
            "--pretty=format:%H|%an|%s|%ar", "--name-only"]
    if file_pattern:
        args.append("--")
        args.append(file_pattern)

    output = run_git_command(args)

    if not output:
        return []

    commits = []
    current_commit = None

    for line in output.split("\n"):
        if "|" in line:
            # Commit line
            hash_val, author, subject, time = line.split("|", 3)
            current_commit = {
                "hash": hash_val[:8],
                "author": author,
                "subject": subject,
                "time": time,
                "files": [],
            }
            commits.append(current_commit)
        elif line.strip() and current_commit:
            # File line
            current_commit["files"].append(line.strip())

    return commits


def verify_work_exists(file_patterns: list[str], agent_name: str = None) -> bool:
    """Verify that work exists in git history."""
    print("\n" + "=" * 80)
    print("🔍 GIT COMMIT VERIFICATION")
    print("=" * 80)

    if agent_name:
        print(f"\n👤 Agent: {agent_name}")

    print(f"📁 Checking patterns: {', '.join(file_patterns)}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")

    all_commits = []

    for pattern in file_patterns:
        commits = check_commits_today(pattern)
        all_commits.extend(commits)

    if not all_commits:
        print("\n❌ NO COMMITS FOUND FOR THESE FILES TODAY!")
        print("\n⚠️  Possible reasons:")
        print("   - Work was conversation/planning only")
        print("   - Code not yet committed")
        print("   - Files don't match patterns")
        print("\n🚨 DO NOT VALIDATE - No actual work to verify!")
        print("=" * 80 + "\n")
        return False

    print(f"\n✅ FOUND {len(all_commits)} COMMITS TODAY!\n")

    for i, commit in enumerate(all_commits, 1):
        print(f"{i}. {commit['hash']} - {commit['subject']}")
        print(f"   Author: {commit['author']}")
        print(f"   Time: {commit['time']}")
        if commit["files"]:
            print(f"   Files: {len(commit['files'])}")
            for f in commit["files"][:5]:  # Show first 5
                print(f"     - {f}")
            if len(commit["files"]) > 5:
                print(f"     ... and {len(commit['files']) - 5} more")
        print()

    print("✅ WORK VERIFIED - Safe to validate!")
    print("=" * 80 + "\n")
    return True


def check_file_exists(file_path: str) -> bool:
    """Check if file actually exists in working directory."""
    path = Path(file_path)
    exists = path.exists()

    if exists:
        print(f"✅ File exists: {file_path}")
    else:
        print(f"❌ File NOT found: {file_path}")

    return exists


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(
            "Usage: python git_commit_verifier.py <file_pattern> [agent_name]")
        print("\nExamples:")
        print("  python git_commit_verifier.py 'extensions/repository-navigator/*'")
        print("  python git_commit_verifier.py 'src/utils/*.py' Agent-1")
        sys.exit(1)

    pattern = sys.argv[1]
    agent = sys.argv[2] if len(sys.argv) > 2 else None

    verified = verify_work_exists([pattern], agent)

    sys.exit(0 if verified else 1)


if __name__ == "__main__":
    main()
