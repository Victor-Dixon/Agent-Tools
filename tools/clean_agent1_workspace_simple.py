#!/usr/bin/env python3
"""
Simple Agent-1 Workspace Cleanup
=================================

Direct cleanup: Archive old inbox messages and completed coordinations.

Author: Agent-1
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import shutil

project_root = Path(__file__).resolve().parent.parent
agent1_inbox = project_root / "agent_workspaces" / "Agent-1" / "inbox"
agent1_archive = project_root / "agent_workspaces" / "Agent-1" / "archive" / "inbox_processed"
agent1_archive.mkdir(parents=True, exist_ok=True)

# Archive files older than 2 days
threshold = datetime.now() - timedelta(days=2)


def should_archive(file_path: Path) -> bool:
    """Determine if file should be archived."""
    name = file_path.name
    
    # Archive old inbox/captain messages
    if name.startswith(("INBOX_MESSAGE_", "CAPTAIN_MESSAGE_")):
        try:
            file_date = datetime.fromtimestamp(file_path.stat().st_mtime)
            return file_date < threshold
        except:
            return False
    
    # Archive completed coordinations (older than 2 days)
    completed_patterns = [
        "_ACK", "_ack", "_RESPONSE", "_response", "_COMPLETE", 
        "_complete", "_VERIFIED", "_verified", "_RESOLVED"
    ]
    
    if any(pattern in name for pattern in completed_patterns):
        try:
            file_date = datetime.fromtimestamp(file_path.stat().st_mtime)
            return file_date < threshold
        except:
            return False
    
    return False


def main():
    """Main execution."""
    if not agent1_inbox.exists():
        print("❌ Inbox directory not found")
        return 1
    
    archived = []
    errors = []
    
    for file_path in agent1_inbox.iterdir():
        if file_path.is_file() and should_archive(file_path):
            try:
                archive_path = agent1_archive / file_path.name
                # Handle duplicates
                counter = 1
                while archive_path.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    archive_path = agent1_archive / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                shutil.move(str(file_path), str(archive_path))
                archived.append(file_path.name)
            except Exception as e:
                errors.append(f"{file_path.name}: {e}")
    
    print(f"✅ Archived {len(archived)} files")
    if archived:
        print("\nArchived files:")
        for name in archived[:20]:
            print(f"  - {name}")
        if len(archived) > 20:
            print(f"  ... and {len(archived) - 20} more")
    
    if errors:
        print(f"\n❌ {len(errors)} errors:")
        for error in errors[:5]:
            print(f"  - {error}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

