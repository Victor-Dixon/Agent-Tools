#!/usr/bin/env python3
"""
Repository Migration Wrapper - Uses github_repo_downloader.py

This wrapper integrates github_repo_downloader.py into the migration workflow
and configures it to download to the review directory.

Usage:
    python tools/migration/migrate_with_downloader.py --account Victor-Dixon
    python tools/migration/migrate_with_downloader.py --account Victor-Dixon --target-dir /path/to/repos
"""

import argparse
import subprocess
import sys
from pathlib import Path


def find_github_repo_downloader() -> Path:
    """Find github_repo_downloader.py in the project."""
    # Common locations to check
    search_paths = [
        Path(__file__).parent.parent.parent,  # Project root
        Path(__file__).parent.parent / "github",
        Path(__file__).parent.parent,
        Path.home() / "Development" / "projects" / "personal" / "AgentTools",
    ]

    for base_path in search_paths:
        # Search recursively
        for pattern in ["**/github_repo_downloader.py", "github_repo_downloader.py"]:
            matches = list(base_path.rglob(pattern)) if base_path.exists() else []
            if matches:
                return matches[0]

    return None


def run_migration(
    account: str,
    target_dir: str = "/home/dream/Development/projects/repositories/old-account",
    downloader_path: str = None,
):
    """
    Run repository migration using github_repo_downloader.py.

    Args:
        account: GitHub account name
        target_dir: Target directory for cloned repositories
        downloader_path: Path to github_repo_downloader.py (auto-detected if None)
    """
    # Find the downloader script
    if not downloader_path:
        downloader = find_github_repo_downloader()
        if not downloader:
            print("❌ Could not find github_repo_downloader.py")
            print("\n💡 Please provide the path:")
            print("   python tools/migration/migrate_with_downloader.py \\")
            print("       --account Victor-Dixon \\")
            print("       --downloader-path /path/to/github_repo_downloader.py")
            return 1
    else:
        downloader = Path(downloader_path)
        if not downloader.exists():
            print(f"❌ github_repo_downloader.py not found at: {downloader_path}")
            return 1

    target_path = Path(target_dir).expanduser().resolve()
    target_path.mkdir(parents=True, exist_ok=True)

    print(f"🔍 Using: {downloader}")
    print(f"📁 Target directory: {target_path}")
    print(f"👤 Account: {account}\n")

    # Check what arguments github_repo_downloader.py accepts
    print("📋 Checking github_repo_downloader.py options...")
    try:
        result = subprocess.run(
            [sys.executable, str(downloader), "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        print(result.stdout)
        print("\n" + "=" * 60 + "\n")
    except Exception as e:
        print(f"⚠️  Could not get help: {e}\n")

    # Run the downloader
    print(f"🚀 Running github_repo_downloader.py...\n")

    # Common argument patterns - adjust based on actual script
    cmd = [
        sys.executable,
        str(downloader),
        "--account",
        account,
        "--output-dir",
        str(target_path),
    ]

    # Add other common options if they exist
    # You may need to adjust these based on your actual script
    try:
        result = subprocess.run(cmd, cwd=target_path.parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Migration interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error running downloader: {e}")
        print(f"\n💡 Try running manually:")
        print(f"   python {downloader} --account {account} --output-dir {target_path}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate repositories using github_repo_downloader.py"
    )
    parser.add_argument(
        "--account",
        default="Victor-Dixon",
        help="GitHub account name (default: Victor-Dixon)",
    )
    parser.add_argument(
        "--target-dir",
        default="/home/dream/Development/projects/repositories/old-account",
        help="Target directory for cloned repositories",
    )
    parser.add_argument(
        "--downloader-path",
        help="Path to github_repo_downloader.py (auto-detected if not provided)",
    )
    parser.add_argument(
        "--find-downloader",
        action="store_true",
        help="Just find and show the path to github_repo_downloader.py",
    )

    args = parser.parse_args()

    if args.find_downloader:
        downloader = find_github_repo_downloader()
        if downloader:
            print(f"✅ Found: {downloader}")
        else:
            print("❌ Not found")
        return 0

    return run_migration(
        account=args.account,
        target_dir=args.target_dir,
        downloader_path=args.downloader_path,
    )


if __name__ == "__main__":
    sys.exit(main())


