#!/usr/bin/env python3
"""
Repository Cleanup Script for Professional GitHub Migration
===========================================================

Removes internal coordination artifacts from git tracking while preserving
files locally. Prepares repository for professional GitHub migration.

<!-- SSOT Domain: infrastructure -->

Author: Agent-2 (Architecture & Design Specialist)
V2 Compliant: <300 lines
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Directories to exclude from professional repository
INTERNAL_DIRECTORIES = [
    "devlogs/",
    "agent_workspaces/",
    "swarm_brain/",
    "docs/organization/",
    "artifacts/",
    "runtime/",
    "data/",
]

# Exceptions: Keep these subdirectories/files
KEEP_PATTERNS = [
    "data/templates/",
    "data/examples/",
    "runtime/**/*.config.json",
    "runtime/**/*.template.json",
]


def check_git_status() -> bool:
    """Check if repository is clean (no uncommitted changes)."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stdout.strip():
            logger.warning("⚠️  Repository has uncommitted changes:")
            logger.warning(result.stdout)
            return False
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error checking git status: {e}")
        return False


def update_gitignore() -> bool:
    """Update .gitignore to exclude internal directories."""
    gitignore_path = Path(".gitignore")
    
    if not gitignore_path.exists():
        logger.error("❌ .gitignore not found")
        return False
    
    content = gitignore_path.read_text(encoding="utf-8")
    
    # Check if exclusions already exist
    has_exclusions = (
        "devlogs/" in content and 
        "agent_workspaces/" in content and
        "# INTERNAL COORDINATION ARTIFACTS" in content
    )
    
    if has_exclusions:
        logger.info("✅ .gitignore already has internal artifact exclusions")
        return True
    
    # Add exclusions section
    exclusion_section = """
# ============================================================================
# INTERNAL COORDINATION ARTIFACTS (Not for professional repository)
# ============================================================================
# These directories contain internal swarm coordination artifacts and should
# NOT be included in professional GitHub repository migration.

# Agent coordination artifacts
devlogs/
agent_workspaces/
swarm_brain/
docs/organization/
artifacts/

# Runtime data (exceptions below)
runtime/
data/

# Exceptions: Keep templates and examples
!data/templates/
!data/examples/
!runtime/**/*.config.json
!runtime/**/*.template.json

"""
    
    # Append if not already present
    if "# INTERNAL COORDINATION ARTIFACTS" not in content:
        content += exclusion_section
        gitignore_path.write_text(content, encoding="utf-8")
        logger.info("✅ Updated .gitignore with internal artifact exclusions")
        return True
    else:
        logger.info("✅ .gitignore already has exclusion section")
        return True


def remove_from_tracking(dry_run: bool = False) -> Tuple[List[str], List[str]]:
    """
    Remove internal directories from git tracking (keep files locally).
    
    Returns:
        Tuple of (successful_removals, failed_removals)
    """
    successful = []
    failed = []
    
    for directory in INTERNAL_DIRECTORIES:
        dir_path = Path(directory)
        
        # Check if directory exists and is tracked
        try:
            result = subprocess.run(
                ["git", "ls-files", "--", directory],
                capture_output=True,
                text=True,
                check=False,
            )
            
            if not result.stdout.strip():
                logger.info(f"⏭️  {directory} not tracked in git, skipping")
                continue
            
            tracked_files = result.stdout.strip().split("\n")
            file_count = len([f for f in tracked_files if f])
            
            if file_count == 0:
                logger.info(f"📦 {directory}: {file_count} files tracked")
            
            if dry_run:
                logger.info(f"🔍 DRY RUN: Would remove {directory} from tracking ({file_count} files)")
                successful.append(directory)
            else:
                # Remove from tracking (keep files locally)
                try:
                    subprocess.run(
                        ["git", "rm", "-r", "--cached", directory],
                        check=True,
                        capture_output=True,
                    )
                    logger.info(f"✅ Removed {directory} from tracking ({file_count} files)")
                    successful.append(directory)
                except subprocess.CalledProcessError as e:
                    logger.error(f"❌ Failed to remove {directory}: {e}")
                    failed.append(directory)
        except Exception as e:
            logger.error(f"❌ Error processing {directory}: {e}")
            failed.append(directory)
    
    return successful, failed


def verify_clean_state() -> bool:
    """Verify that internal artifacts are no longer tracked."""
    logger.info("🔍 Verifying clean repository state...")
    
    all_clean = True
    for directory in INTERNAL_DIRECTORIES:
        try:
            result = subprocess.run(
                ["git", "ls-files", "--", directory],
                capture_output=True,
                text=True,
                check=False,
            )
            
            if result.stdout.strip():
                tracked = result.stdout.strip().split("\n")
                file_count = len([f for f in tracked if f])
                logger.warning(
                    f"⚠️  {directory} still has {file_count} tracked files"
                )
                all_clean = False
            else:
                logger.info(f"✅ {directory} not tracked")
        except Exception as e:
            logger.error(f"❌ Error verifying {directory}: {e}")
            all_clean = False
    
    return all_clean


def get_tracked_file_count() -> int:
    """Get total number of tracked files."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            check=True,
        )
        return len([f for f in result.stdout.strip().split("\n") if f])
    except Exception as e:
        logger.error(f"❌ Error counting tracked files: {e}")
        return 0


def main():
    """Main cleanup execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Clean repository for professional GitHub migration"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without making changes",
    )
    parser.add_argument(
        "--skip-gitignore",
        action="store_true",
        help="Skip .gitignore update",
    )
    parser.add_argument(
        "--skip-verification",
        action="store_true",
        help="Skip verification step",
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🧹 REPOSITORY CLEANUP FOR PROFESSIONAL GITHUB MIGRATION")
    print("="*70 + "\n")
    
    # Check git status
    if not args.dry_run and not check_git_status():
        logger.warning(
            "⚠️  Repository has uncommitted changes."
            " Commit or stash changes before cleanup."
        )
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != "y":
            logger.info("❌ Cleanup cancelled")
            return 1
    
    # Get initial file count
    initial_count = get_tracked_file_count()
    logger.info(f"📊 Initial tracked files: {initial_count}")
    
    # Update .gitignore
    if not args.skip_gitignore:
        logger.info("\n📝 Step 1: Updating .gitignore...")
        if not update_gitignore():
            logger.error("❌ Failed to update .gitignore")
            return 1
    
    # Remove from tracking
    logger.info("\n🗑️  Step 2: Removing internal artifacts from tracking...")
    successful, failed = remove_from_tracking(dry_run=args.dry_run)
    
    if failed:
        logger.error(f"❌ Failed to remove {len(failed)} directories")
        return 1
    
    if args.dry_run:
        logger.info(f"\n🔍 DRY RUN: Would remove {len(successful)} directories")
        logger.info("   Run without --dry-run to execute cleanup")
        return 0
    
    # Verify clean state
    if not args.skip_verification:
        logger.info("\n✅ Step 3: Verifying clean state...")
        if not verify_clean_state():
            logger.warning("⚠️  Some files may still be tracked")
        else:
            logger.info("✅ Repository is clean")
    
    # Get final file count
    final_count = get_tracked_file_count()
    removed_count = initial_count - final_count
    
    print("\n" + "="*70)
    print("📊 CLEANUP SUMMARY")
    print("="*70)
    print(f"Initial tracked files: {initial_count}")
    print(f"Final tracked files: {final_count}")
    print(f"Removed from tracking: {removed_count}")
    print(f"Directories cleaned: {len(successful)}")
    print("\n💡 Next steps:")
    print("   1. Review changes: git status")
    print("   2. Commit cleanup: git commit -m 'chore: remove internal artifacts from tracking'")
    print("   3. Verify fresh clone: git clone <repo> <test-dir>")
    print("   4. Proceed with migration to new GitHub account")
    print("="*70 + "\n")
    
    logger.info("✅ Cleanup complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

