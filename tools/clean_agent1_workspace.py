#!/usr/bin/env python3
"""
Clean Agent-1 Workspace and Inbox
==================================

Archives old inbox messages, cycle planner tasks, and completed coordination files.
Organizes workspace by moving completed/old items to archive.

Author: Agent-1
V2 Compliant: <300 lines
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import shutil
import json

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

agent1_workspace = project_root / "agent_workspaces" / "Agent-1"
agent1_inbox = agent1_workspace / "inbox"
agent1_archive = agent1_workspace / "archive"
agent1_archive_inbox = agent1_archive / "inbox_processed"

# Create archive directories if they don't exist
agent1_archive_inbox.mkdir(parents=True, exist_ok=True)

# Threshold: Archive messages older than 3 days (more aggressive cleanup)
ARCHIVE_THRESHOLD_DAYS = 3
threshold_date = datetime.now() - timedelta(days=ARCHIVE_THRESHOLD_DAYS)


def get_file_date(file_path: Path) -> datetime:
    """Get file modification date."""
    try:
        return datetime.fromtimestamp(file_path.stat().st_mtime)
    except Exception:
        return datetime.now()


def is_completed_coordination(file_path: Path) -> bool:
    """Check if file represents a completed coordination."""
    name_lower = file_path.name.lower()
    
    # Completed indicators
    completed_keywords = [
        "_complete", "_completed", "_ack", "_acknowledgment", 
        "_acknowledged", "_response", "_verified", "_resolved",
        "_handoff", "_ready", "_status", "_update", "_coordination",
        "agent3_", "agent5_", "agent6_", "agent8_", "captain_"
    ]
    
    # Skip only very recent coordination (last 2 days)
    skip_keywords = [
        "2025-12-19", "2025-12-20"
    ]
    
    # Check if it's a completed coordination
    if any(keyword in name_lower for keyword in completed_keywords):
        # But skip if it's very recent
        if not any(skip in name_lower for skip in skip_keywords):
            file_date = get_file_date(file_path)
            # Archive if older than threshold
            if file_date < threshold_date:
                return True
    
    return False


def is_old_inbox_message(file_path: Path) -> bool:
    """Check if inbox message is old enough to archive."""
    # Archive all INBOX_MESSAGE files older than threshold
    if file_path.name.startswith("INBOX_MESSAGE_"):
        file_date = get_file_date(file_path)
        return file_date < threshold_date
    
    # Also archive old CAPTAIN_MESSAGE files
    if file_path.name.startswith("CAPTAIN_MESSAGE_"):
        file_date = get_file_date(file_path)
        # Archive captain messages older than 5 days
        if file_date < datetime.now() - timedelta(days=5):
            return True
    
    return False


def archive_file(file_path: Path, archive_dir: Path, reason: str):
    """Move file to archive directory."""
    try:
        archive_path = archive_dir / file_path.name
        
        # Handle duplicates
        counter = 1
        while archive_path.exists():
            stem = file_path.stem
            suffix = file_path.suffix
            archive_path = archive_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        
        shutil.move(str(file_path), str(archive_path))
        return True, str(archive_path)
    except Exception as e:
        return False, str(e)


def clean_cycle_planner_tasks():
    """Archive old cycle planner task files."""
    archived = []
    errors = []
    
    for task_file in agent1_workspace.glob("cycle_planner_tasks_*.json"):
        file_date = get_file_date(task_file)
        
        # Archive tasks older than 3 days
        if file_date < datetime.now() - timedelta(days=3):
            success, result = archive_file(
                task_file, 
                agent1_archive,
                "old cycle planner task"
            )
            if success:
                archived.append(task_file.name)
            else:
                errors.append(f"{task_file.name}: {result}")
    
    return archived, errors


def clean_inbox():
    """Clean inbox directory - archive old and completed messages."""
    archived = []
    errors = []
    kept = []
    
    if not agent1_inbox.exists():
        return archived, errors, kept
    
    for inbox_file in agent1_inbox.iterdir():
        if inbox_file.is_dir():
            continue
        
        should_archive = False
        reason = ""
        
        # Archive old inbox messages
        if is_old_inbox_message(inbox_file):
            should_archive = True
            reason = "old inbox message"
        
        # Archive completed coordination messages (older than threshold)
        elif is_completed_coordination(inbox_file):
            file_date = get_file_date(inbox_file)
            if file_date < threshold_date:
                should_archive = True
                reason = "completed coordination"
        
        if should_archive:
            success, result = archive_file(
                inbox_file,
                agent1_archive_inbox,
                reason
            )
            if success:
                archived.append(f"{inbox_file.name} ({reason})")
            else:
                errors.append(f"{inbox_file.name}: {result}")
        else:
            kept.append(inbox_file.name)
    
    return archived, errors, kept


def clean_temporary_files():
    """Remove temporary and cache files."""
    removed = []
    errors = []
    
    # Remove __pycache__ directories
    for pycache in agent1_workspace.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache)
            removed.append(f"__pycache__: {pycache.relative_to(agent1_workspace)}")
        except Exception as e:
            errors.append(f"__pycache__ {pycache}: {e}")
    
    # Remove .pyc files
    for pyc_file in agent1_workspace.rglob("*.pyc"):
        try:
            pyc_file.unlink()
            removed.append(f".pyc: {pyc_file.name}")
        except Exception as e:
            errors.append(f".pyc {pyc_file.name}: {e}")
    
    return removed, errors


def main():
    """Main execution."""
    print("🧹 Cleaning Agent-1 Workspace and Inbox")
    print("=" * 60)
    print()
    
    # Dry run check
    if "--execute" not in sys.argv:
        print("⚠️  DRY RUN MODE - No files will be moved")
        print("   Use --execute flag to actually clean files")
        print()
    
    # Clean inbox
    print("📬 Cleaning inbox...")
    archived_inbox, errors_inbox, kept_inbox = clean_inbox()
    
    # Clean cycle planner tasks
    print("📅 Cleaning cycle planner tasks...")
    archived_tasks, errors_tasks = clean_cycle_planner_tasks()
    
    # Clean temporary files
    print("🗑️  Cleaning temporary files...")
    removed_temp, errors_temp = clean_temporary_files()
    
    # Summary
    print()
    print("=" * 60)
    print("📊 CLEANUP SUMMARY")
    print("=" * 60)
    
    print(f"\n📬 Inbox:")
    print(f"   Archived: {len(archived_inbox)}")
    print(f"   Kept: {len(kept_inbox)}")
    if archived_inbox:
        print(f"   Archived files:")
        for item in archived_inbox[:10]:  # Show first 10
            print(f"      - {item}")
        if len(archived_inbox) > 10:
            print(f"      ... and {len(archived_inbox) - 10} more")
    
    print(f"\n📅 Cycle Planner Tasks:")
    print(f"   Archived: {len(archived_tasks)}")
    if archived_tasks:
        for task in archived_tasks:
            print(f"      - {task}")
    
    print(f"\n🗑️  Temporary Files:")
    print(f"   Removed: {len(removed_temp)}")
    if removed_temp:
        for item in removed_temp[:10]:  # Show first 10
            print(f"      - {item}")
        if len(removed_temp) > 10:
            print(f"      ... and {len(removed_temp) - 10} more")
    
    # Errors
    all_errors = errors_inbox + errors_tasks + errors_temp
    if all_errors:
        print(f"\n❌ Errors: {len(all_errors)}")
        for error in all_errors[:5]:
            print(f"      - {error}")
        if len(all_errors) > 5:
            print(f"      ... and {len(all_errors) - 5} more")
    
    if "--execute" not in sys.argv:
        print()
        print("⚠️  DRY RUN - No files were actually moved")
        print("   Run with --execute to perform cleanup")
        return 0
    
    print()
    print("✅ Cleanup complete!")
    print(f"   Total items processed: {len(archived_inbox) + len(archived_tasks) + len(removed_temp)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

