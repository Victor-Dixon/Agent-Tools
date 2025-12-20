#!/usr/bin/env python3
"""
Clean Agent-2 Workspace and Inbox
==================================

Archives old inbox messages, cycle planner tasks, and completed coordination files.
Organizes workspace by moving completed/old items to archive.

Author: Agent-2
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

agent2_workspace = project_root / "agent_workspaces" / "Agent-2"
agent2_inbox = agent2_workspace / "inbox"
agent2_archive = agent2_workspace / "archive"
agent2_archive_inbox = agent2_archive / "inbox_processed"
agent2_archive_workspace = agent2_archive / "workspace_files"

# Create archive directories if they don't exist
agent2_archive_inbox.mkdir(parents=True, exist_ok=True)
agent2_archive_workspace.mkdir(parents=True, exist_ok=True)

# Threshold: Archive messages older than 3 days
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
        "_acknowledged", "_resolved", "_done", "_finished",
        "_handoff", "_handed_off", "_sent", "_delivered"
    ]

    return any(keyword in name_lower for keyword in completed_keywords)


def should_keep_file(file_path: Path) -> bool:
    """Determine if file should be kept in workspace."""
    name = file_path.name

    # Always keep status.json
    if name == "status.json":
        return True

    # Keep recent cycle planner tasks (last 7 days)
    if name.startswith("cycle_planner_tasks_"):
        file_date = get_file_date(file_path)
        if file_date > datetime.now() - timedelta(days=7):
            return True
        return False

    # Keep coordination plans and active documentation
    keep_patterns = [
        "AGENT2_PERPETUAL_MOTION_COORDINATION_PLAN",
        "AGENT2_AGENT3_INFRASTRUCTURE_ARCHITECTURE_SUPPORT",
        "COORDINATION_PLAN",
        "ARCHITECTURE_REVIEW",
        "GUIDANCE",
        "REVIEW",
    ]

    if any(pattern in name.upper() for pattern in keep_patterns):
        file_date = get_file_date(file_path)
        # Keep if modified in last 30 days
        if file_date > datetime.now() - timedelta(days=30):
            return True

    # Archive old completed files
    if is_completed_coordination(file_path):
        return False

    # Archive old files (older than 30 days)
    file_date = get_file_date(file_path)
    if file_date < datetime.now() - timedelta(days=30):
        return False

    return True


def clean_inbox():
    """Clean inbox directory."""
    archived_count = 0

    if not agent2_inbox.exists():
        print("  ℹ️  Inbox directory does not exist")
        return archived_count

    # Archive old inbox messages
    for file_path in agent2_inbox.iterdir():
        if file_path.is_file():
            # Skip archive directories
            if file_path.name.startswith("archive_") or file_path.name.startswith("processed_"):
                continue

            # Archive old messages (older than threshold)
            file_date = get_file_date(file_path)
            if file_date < threshold_date:
                try:
                    archive_path = agent2_archive_inbox / file_path.name
                    if archive_path.exists():
                        # Add timestamp if duplicate
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        archive_path = agent2_archive_inbox / \
                            f"{file_path.stem}_{timestamp}{file_path.suffix}"
                    shutil.move(str(file_path), str(archive_path))
                    archived_count += 1
                except Exception as e:
                    print(f"    ⚠️  Error archiving {file_path.name}: {e}")

    # Move existing processed directories to archive
    for item in agent2_inbox.iterdir():
        if item.is_dir() and (item.name.startswith("archive_") or item.name.startswith("processed_")):
            try:
                archive_dir = agent2_archive_inbox / item.name
                if archive_dir.exists():
                    # Merge contents
                    for subitem in item.iterdir():
                        subitem_dest = archive_dir / subitem.name
                        if subitem_dest.exists():
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            subitem_dest = archive_dir / \
                                f"{subitem.stem}_{timestamp}{subitem.suffix}"
                        shutil.move(str(subitem), str(subitem_dest))
                    item.rmdir()
                else:
                    shutil.move(str(item), str(archive_dir))
            except Exception as e:
                print(f"    ⚠️  Error archiving directory {item.name}: {e}")

    return archived_count


def clean_workspace():
    """Clean workspace root directory."""
    archived_count = 0

    if not agent2_workspace.exists():
        print("  ℹ️  Workspace directory does not exist")
        return archived_count

    # Files to always keep
    keep_files = {"status.json", "status_backup_20251123_033509.json"}

    # Archive old workspace files
    for file_path in agent2_workspace.iterdir():
        if file_path.is_file() and file_path.name not in keep_files:
            if not should_keep_file(file_path):
                try:
                    archive_path = agent2_archive_workspace / file_path.name
                    if archive_path.exists():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        archive_path = agent2_archive_workspace / \
                            f"{file_path.stem}_{timestamp}{file_path.suffix}"
                    shutil.move(str(file_path), str(archive_path))
                    archived_count += 1
                except Exception as e:
                    print(f"    ⚠️  Error archiving {file_path.name}: {e}")

    return archived_count


def main():
    """Main entry point."""
    print("🧹 Cleaning Agent-2 workspace and inbox...")

    # Clean inbox
    print("\n📥 Cleaning inbox...")
    inbox_archived = clean_inbox()
    print(f"  ✅ Archived {inbox_archived} inbox files")

    # Clean workspace
    print("\n📁 Cleaning workspace...")
    workspace_archived = clean_workspace()
    print(f"  ✅ Archived {workspace_archived} workspace files")

    # Summary
    total_archived = inbox_archived + workspace_archived
    print(f"\n✅ Cleanup complete!")
    print(f"  - Total files archived: {total_archived}")
    print(f"  - Inbox: {inbox_archived}")
    print(f"  - Workspace: {workspace_archived}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
