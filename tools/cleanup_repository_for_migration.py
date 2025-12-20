#!/usr/bin/env python3
"""
Repository Cleanup Script for Professional GitHub Migration
============================================================

Removes internal coordination artifacts from git tracking while preserving
files locally. Designed for professional repository migration.

Usage:
    python tools/cleanup_repository_for_migration.py --dry-run
    python tools/cleanup_repository_for_migration.py --execute
    python tools/cleanup_repository_for_migration.py --restore-backup backup_2025-12-11_12-00-00.json

Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-11
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Directories to exclude from professional repository
EXCLUDE_DIRS = [
    "devlogs/",
    "agent_workspaces/",
    "swarm_brain/",
    "docs/organization/",
    "artifacts/",
    "runtime/",
    "data/",
]

# Exceptions: Keep these even if parent directory is excluded
KEEP_PATTERNS = [
    "data/templates/",
    "data/examples/",
    "runtime/**/*.config.json",
    "runtime/**/*.template.json",
    # SSOT documentation preservation (after migration to docs/architecture/ssot/)
    "docs/architecture/ssot/",
    "docs/architecture/ssot-domains/",
    "docs/architecture/ssot-standards/",
    "docs/architecture/ssot-audits/",
    "docs/architecture/ssot-remediation/",
]


def run_git_command(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run git command and return result."""
    try:
        result = subprocess.run(
            ["git"] + cmd,
            capture_output=True,
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {' '.join(['git'] + cmd)}")
        logger.error(f"Error: {e.stderr}")
        raise


def get_tracked_files() -> Set[str]:
    """Get all currently tracked files."""
    result = run_git_command(["ls-files"])
    return set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()


def should_exclude_file(filepath: str) -> bool:
    """Check if file should be excluded from professional repository."""
    # Check keep patterns FIRST (preservation takes priority)
    for keep_pattern in KEEP_PATTERNS:
        pattern_clean = keep_pattern.replace("**/", "").rstrip("/")
        if pattern_clean in filepath:
            return False  # Preserve this file
    
    # Check if file matches any exclude directory
    for exclude_dir in EXCLUDE_DIRS:
        if filepath.startswith(exclude_dir):
            return True  # Exclude this file
    return False  # Keep this file (not in excluded directories)


def find_files_to_remove() -> List[str]:
    """Find all tracked files that should be removed."""
    tracked = get_tracked_files()
    to_remove = [f for f in tracked if should_exclude_file(f)]
    return sorted(to_remove)


def create_backup(files_to_remove: List[str]) -> Path:
    """Create backup manifest of files to be removed."""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = backup_dir / f"cleanup_backup_{timestamp}.json"
    
    backup_data = {
        "timestamp": timestamp,
        "created_at": datetime.now().isoformat(),
        "files_removed": files_to_remove,
        "file_count": len(files_to_remove),
        "exclude_dirs": EXCLUDE_DIRS,
        "keep_patterns": KEEP_PATTERNS,
    }
    
    backup_file.write_text(
        json.dumps(backup_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    
    logger.info(f"✅ Backup created: {backup_file}")
    return backup_file


def update_gitignore() -> bool:
    """Update .gitignore to ensure exclusions are present."""
    gitignore_path = Path(".gitignore")
    
    if not gitignore_path.exists():
        logger.warning("⚠️  .gitignore not found, creating new file")
        gitignore_path.write_text("", encoding="utf-8")
    
    content = gitignore_path.read_text(encoding="utf-8")
    
    # Check if internal artifacts section exists
    marker = "# INTERNAL COORDINATION ARTIFACTS"
    if marker in content:
        logger.info("✅ .gitignore already has internal artifacts section")
        return False
    
    # Add internal artifacts section
    additions = [
        "",
        "# ============================================================================",
        "# INTERNAL COORDINATION ARTIFACTS (Not for professional repository)",
        "# ============================================================================",
        "# These directories contain internal swarm coordination artifacts and should",
        "# NOT be included in professional GitHub repository migration.",
        "",
        "# Agent coordination artifacts",
        "devlogs/",
        "agent_workspaces/",
        "swarm_brain/",
        "docs/organization/",
        "artifacts/",
        "",
        "# Runtime data (exceptions below)",
        "runtime/",
        "data/",
        "",
        "# Exceptions: Keep templates and examples",
        "!data/templates/",
        "!data/examples/",
        "!runtime/**/*.config.json",
        "!runtime/**/*.template.json",
        "",
    ]
    
    gitignore_path.write_text(
        content + "\n" + "\n".join(additions),
        encoding="utf-8"
    )
    
    logger.info("✅ Updated .gitignore with internal artifacts exclusions")
    return True


def dry_run_cleanup() -> Dict:
    """Perform dry-run analysis without making changes."""
    logger.info("🔍 DRY RUN MODE - No changes will be made")
    
    files_to_remove = find_files_to_remove()
    
    # Group by directory
    by_directory: Dict[str, List[str]] = {}
    for filepath in files_to_remove:
        dir_path = str(Path(filepath).parent) + "/"
        if dir_path not in by_directory:
            by_directory[dir_path] = []
        by_directory[dir_path].append(filepath)
    
    # Print summary
    logger.info(f"\n📊 DRY RUN SUMMARY")
    logger.info(f"   Files to remove: {len(files_to_remove):,}")
    logger.info(f"   Directories affected: {len(by_directory)}")
    
    logger.info(f"\n📁 BREAKDOWN BY DIRECTORY:")
    for directory, files in sorted(by_directory.items()):
        logger.info(f"   {directory}: {len(files):,} files")
    
    # Show sample files
    logger.info(f"\n📄 SAMPLE FILES (first 10):")
    for filepath in files_to_remove[:10]:
        logger.info(f"   - {filepath}")
    if len(files_to_remove) > 10:
        logger.info(f"   ... and {len(files_to_remove) - 10:,} more")
    
    return {
        "files_to_remove": files_to_remove,
        "file_count": len(files_to_remove),
        "by_directory": {k: len(v) for k, v in by_directory.items()},
    }


def execute_cleanup(dry_run_data: Dict) -> Path:
    """Execute cleanup by removing files from git tracking."""
    files_to_remove = dry_run_data["files_to_remove"]
    
    if not files_to_remove:
        logger.info("✅ No files to remove - repository already clean")
        return None
    
    # Create backup
    backup_file = create_backup(files_to_remove)
    
    # Update .gitignore
    gitignore_updated = update_gitignore()
    
    # Remove files from tracking (keep locally)
    logger.info(f"\n🗑️  Removing {len(files_to_remove):,} files from git tracking...")
    
    # Process in batches to avoid command line length limits
    batch_size = 1000
    total_batches = (len(files_to_remove) + batch_size - 1) // batch_size
    
    for i in range(0, len(files_to_remove), batch_size):
        batch = files_to_remove[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        logger.info(f"   Processing batch {batch_num}/{total_batches} ({len(batch)} files)...")
        
        try:
            run_git_command(["rm", "--cached"] + batch)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to remove batch {batch_num}")
            logger.error(f"   Error: {e.stderr}")
            raise
    
    logger.info(f"✅ Removed {len(files_to_remove):,} files from git tracking")
    
    if gitignore_updated:
        logger.info("✅ Updated .gitignore")
    
    logger.info(f"✅ Backup saved to: {backup_file}")
    
    return backup_file


def restore_backup(backup_file: Path) -> None:
    """Restore files from backup manifest."""
    if not backup_file.exists():
        logger.error(f"❌ Backup file not found: {backup_file}")
        return
    
    backup_data = json.loads(backup_file.read_text(encoding="utf-8"))
    files_to_restore = backup_data["files_removed"]
    
    logger.info(f"📦 Restoring {len(files_to_restore):,} files from backup...")
    
    # Add files back to git tracking
    batch_size = 1000
    for i in range(0, len(files_to_restore), batch_size):
        batch = files_to_restore[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        
        logger.info(f"   Restoring batch {batch_num} ({len(batch)} files)...")
        
        try:
            run_git_command(["add"] + batch)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to restore batch {batch_num}")
            logger.error(f"   Error: {e.stderr}")
            raise
    
    logger.info(f"✅ Restored {len(files_to_restore):,} files to git tracking")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Clean repository for professional GitHub migration",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform dry-run analysis without making changes"
    )
    
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute cleanup (removes files from git tracking)"
    )
    
    parser.add_argument(
        "--restore-backup",
        type=str,
        help="Restore files from backup manifest (path to backup JSON file)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if sum([args.dry_run, args.execute, bool(args.restore_backup)]) != 1:
        parser.error("Must specify exactly one of: --dry-run, --execute, or --restore-backup")
    
    try:
        if args.dry_run:
            dry_run_cleanup()
            logger.info("\n✅ Dry run complete - use --execute to apply changes")
            return 0
        
        elif args.execute:
            logger.info("🚀 EXECUTE MODE - Changes will be made")
            dry_run_data = dry_run_cleanup()
            
            # Confirm before proceeding
            response = input("\n⚠️  Proceed with cleanup? (yes/no): ")
            if response.lower() != "yes":
                logger.info("❌ Cleanup cancelled by user")
                return 1
            
            backup_file = execute_cleanup(dry_run_data)
            logger.info("\n✅ Cleanup complete!")
            logger.info(f"   Next step: Review changes with 'git status'")
            logger.info(f"   Commit with: git commit -m 'chore: remove internal artifacts from professional repository'")
            return 0
        
        elif args.restore_backup:
            restore_backup(Path(args.restore_backup))
            logger.info("\n✅ Restore complete!")
            return 0
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

