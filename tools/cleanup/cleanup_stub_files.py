#!/usr/bin/env python3
"""
Automated Cleanup Script for Empty Stub Files
Moves identified empty/stub files to archive before deletion
Based on comprehensive field analysis
"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Archive directory
ARCHIVE_DIR = Path("archive/stub_files_cleanup")

# Empty/stub files identified in field analysis
EMPTY_FILES = [
    # Utils Directory (7 files)
    "src/utils/config_consolidator.py",
    "src/utils/config_core.py",
    "src/utils/confirm.py",
    "src/utils/file_utils.py",
    "src/utils/backup.py",
    "src/utils/logger.py",
    "src/utils/unified_utilities.py",

    # Infrastructure Layer (6 files)
    "src/infrastructure/logging/std_logger.py",
    "src/infrastructure/persistence/sqlite_agent_repo.py",
    "src/infrastructure/persistence/sqlite_task_repo.py",
    "src/infrastructure/time/system_clock.py",

    # Domain Layer (9 files)
    "src/domain/domain_events.py",
    "src/domain/entities/agent.py",
    "src/domain/entities/task.py",
    "src/domain/ports/agent_repository.py",
    "src/domain/ports/task_repository.py",
    "src/domain/ports/logger.py",
    "src/domain/ports/message_bus.py",

    # Application Layer (2 files)
    "src/application/use_cases/assign_task_uc.py",
    "src/application/use_cases/complete_task_uc.py",

    # Architecture Layer (3 files)
    "src/architecture/design_patterns.py",
    "src/architecture/system_integration.py",
    "src/architecture/unified_architecture_core.py",

    # Scripts & Tools (5+ files)
    "scripts/cleanup_v2_compliance.py",
    "scripts/index_v2_refactoring.py",
    "tools/agent_checkin.py",
    "tools/audit_cleanup.py",
    "tools/projectscanner.py",
]

def count_lines(file_path: Path) -> int:
    """Count lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except Exception as e:
        logger.warning(f"Could not read {file_path}: {e}")
        return -1

def is_empty_or_stub(file_path: Path) -> bool:
    """Check if file is empty or contains only stubs."""
    if not file_path.exists():
        return False

    line_count = count_lines(file_path)
    if line_count == 0:
        return True

    # Check if file contains only comments, imports, or basic structure
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        # Empty after removing comments and whitespace
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        if not lines:
            return True

        # Check for stub patterns
        stub_patterns = [
            'pass',
            'NotImplemented',
            'raise NotImplementedError',
            '...',
            'TODO',
            'FIXME'
        ]

        # If file only contains basic structure without real implementation
        if len(lines) <= 5 and any(pattern.lower() in content.lower() for pattern in stub_patterns):
            return True

        # Files with no functions/classes (tools directory)
        if 'tools/' in str(file_path) and 'def ' not in content and 'class ' not in content:
            return True

    except Exception as e:
        logger.warning(f"Could not analyze {file_path}: {e}")

    return False

def create_archive_structure() -> None:
    """Create archive directory structure."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created archive directory: {ARCHIVE_DIR}")

def archive_file(file_path: Path) -> bool:
    """Move file to archive with original directory structure."""
    if not file_path.exists():
        logger.warning(f"File does not exist: {file_path}")
        return False

    # Create relative archive path
    relative_path = file_path.relative_to(Path.cwd())
    archive_path = ARCHIVE_DIR / relative_path

    # Create parent directories in archive
    archive_path.parent.mkdir(parents=True, exist_ok=True)

    # Move file to archive
    try:
        shutil.move(str(file_path), str(archive_path))
        logger.info(f"Archived: {file_path} -> {archive_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to archive {file_path}: {e}")
        return False

def cleanup_empty_directories() -> int:
    """Remove empty directories after file cleanup."""
    cleaned = 0
    for dir_path in Path("src").rglob("*"):
        if dir_path.is_dir() and not any(dir_path.rglob("*")):
            try:
                dir_path.rmdir()
                logger.info(f"Removed empty directory: {dir_path}")
                cleaned += 1
            except Exception as e:
                logger.warning(f"Could not remove empty directory {dir_path}: {e}")
    return cleaned

def main():
    """Main cleanup execution."""
    logger.info("🚀 Starting automated cleanup of empty stub files")
    logger.info("=" * 60)

    # Create archive structure
    create_archive_structure()

    # Analyze and archive files
    archived_count = 0
    skipped_count = 0
    error_count = 0

    logger.info(f"📋 Processing {len(EMPTY_FILES)} identified files...")

    for file_str in EMPTY_FILES:
        file_path = Path(file_str)

        if not file_path.exists():
            logger.warning(f"⚠️  File not found: {file_path}")
            skipped_count += 1
            continue

        # Verify it's actually empty/stub
        if is_empty_or_stub(file_path):
            if archive_file(file_path):
                archived_count += 1
            else:
                error_count += 1
        else:
            logger.info(f"📝 File not empty/stub, keeping: {file_path} ({count_lines(file_path)} lines)")
            skipped_count += 1

    # Cleanup empty directories
    logger.info("\n🗂️  Cleaning up empty directories...")
    empty_dirs_cleaned = cleanup_empty_directories()

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("✅ CLEANUP COMPLETE - SUMMARY")
    logger.info("=" * 60)
    logger.info(f"📦 Files archived: {archived_count}")
    logger.info(f"⏭️  Files skipped: {skipped_count}")
    logger.info(f"❌ Errors: {error_count}")
    logger.info(f"🗂️  Empty directories removed: {empty_dirs_cleaned}")
    logger.info(f"📂 Archive location: {ARCHIVE_DIR}")

    if archived_count > 0:
        logger.info("\n🔄 Files can be restored from archive if needed")
        logger.info("🗑️  Run 'rm -rf archive' to permanently delete archived files")

    logger.info("\n🎯 Ready for Phase 2 consolidation!")

    return archived_count, skipped_count, error_count, empty_dirs_cleaned

if __name__ == "__main__":
    archived, skipped, errors, dirs_cleaned = main()

    # Exit with appropriate code
    if errors > 0:
        exit(1)
    elif archived == 0:
        exit(2)  # No files archived
    else:
        exit(0)  # Success
