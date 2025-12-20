#!/usr/bin/env python3
"""
Clean Agent-1 Inbox by Patterns
=================================

Archive files based on completion patterns and old message formats.

Author: Agent-1
"""

import sys
from pathlib import Path
import shutil

project_root = Path(__file__).resolve().parent.parent
agent1_inbox = project_root / "agent_workspaces" / "Agent-1" / "inbox"
agent1_archive = project_root / "agent_workspaces" / "Agent-1" / "archive" / "inbox_processed"
agent1_archive.mkdir(parents=True, exist_ok=True)

# Patterns to archive (completed/old coordinations)
ARCHIVE_PATTERNS = [
    # Old inbox messages (before December 2025)
    "INBOX_MESSAGE_202511",
    "INBOX_MESSAGE_2025120[0-9]",  # Dec 1-9
    "INBOX_MESSAGE_2025121[0-7]",  # Dec 10-17
    
    # Old captain messages
    "CAPTAIN_MESSAGE_202510",
    "CAPTAIN_MESSAGE_202511",
    "CAPTAIN_MESSAGE_2025120[0-9]",
    "CAPTAIN_MESSAGE_2025121[0-7]",
    
    # Completed coordinations
    "_ACK", "_ack", "_ACKNOWLEDGMENT", "_acknowledgment",
    "_RESPONSE", "_response", "_COORDINATION_RESPONSE",
    "_COMPLETE", "_complete", "_VERIFIED", "_verified",
    "_RESOLVED", "_resolved", "_HANDOFF", "_handoff",
    "_STATUS_UPDATE", "_status_update",
    
    # Agent coordination responses
    "AGENT3_COLLABORATION",
    "AGENT5_FILE_LIST",
    "AGENT6_",
    "AGENT8_",
    "CAPTAIN_DECISION",
    "CAPTAIN_PHASE2",
    "CAPTAIN_STATUS",
    "COORDINATION_RESPONSE",
    "GAS_FROM_CAPTAIN",
    "PHASE1_EXECUTION",
    "PROMPT_",  # Old prompt files
    "SESSION_WRAP_UP",
    "TECHNICAL_DEBT_TODO",
    "TOOLS_DEBATE",
    "TOOLS_RANKING",
]

# Keep these patterns (active/current)
KEEP_PATTERNS = [
    "2025-12-18",
    "2025-12-19",
    "2025-12-20",
    "_PENDING",
    "_IN_PROGRESS",
    "_CURRENT",
    "_ACTIVE",
]


def should_archive(file_path: Path) -> bool:
    """Check if file should be archived."""
    name = file_path.name
    
    # Never archive if it matches keep patterns
    if any(pattern in name for pattern in KEEP_PATTERNS):
        return False
    
    # Archive if it matches archive patterns
    import re
    for pattern in ARCHIVE_PATTERNS:
        if re.search(pattern, name):
            return True
    
    return False


def main():
    """Main execution."""
    if not agent1_inbox.exists():
        print("❌ Inbox directory not found")
        return 1
    
    archived = []
    errors = []
    kept = []
    
    for file_path in agent1_inbox.iterdir():
        if not file_path.is_file():
            continue
        
        if should_archive(file_path):
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
        else:
            kept.append(file_path.name)
    
    print("🧹 Agent-1 Inbox Cleanup")
    print("=" * 60)
    print(f"\n✅ Archived: {len(archived)} files")
    print(f"📬 Kept: {len(kept)} files")
    
    if archived:
        print(f"\n📦 Archived files (first 20):")
        for name in archived[:20]:
            print(f"  - {name}")
        if len(archived) > 20:
            print(f"  ... and {len(archived) - 20} more")
    
    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for error in errors[:5]:
            print(f"  - {error}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

