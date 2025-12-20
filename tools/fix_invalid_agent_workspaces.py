#!/usr/bin/env python3
"""
Fix Invalid Agent Workspace Directories
=======================================

Removes invalid agent workspace directories that don't match Agent-1 through Agent-8.
Archives messages from invalid directories if they contain useful content.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-12-10
"""

import shutil
from pathlib import Path
from typing import List, Tuple

VALID_AGENT_IDS = {f"Agent-{i}" for i in range(1, 9)}


def is_valid_agent_id(agent_id: str) -> bool:
    """Check if agent ID is valid (Agent-1 through Agent-8)."""
    return agent_id in VALID_AGENT_IDS


def find_invalid_workspaces(workspace_root: Path) -> List[Tuple[Path, List[Path]]]:
    """
    Find invalid workspace directories and their messages.
    
    Returns:
        List of tuples: (invalid_directory, list_of_message_files)
    """
    invalid_workspaces = []
    
    if not workspace_root.exists():
        return invalid_workspaces
    
    for item in workspace_root.iterdir():
        if not item.is_dir():
            continue
        
        agent_id = item.name
        
        # Skip valid agent IDs
        if is_valid_agent_id(agent_id):
            continue
        
        # Skip non-agent directories (registry files, legitimate workspace directories, etc.)
        skip_dirs = {
            "agent_registry.json",
            "contracts",
            "meeting",
            "swarm_cycle_planner",
            "archive",  # Archive directory itself
            "AutoGasPipeline",  # Legitimate workflow workspace
            "GaslineHub",  # Legitimate workflow workspace
        }
        if agent_id in skip_dirs:
            continue
        
        # Only flag directories that look like malformed agent IDs
        # Patterns: starts with "Agent" but invalid, or contains CLI syntax
        looks_like_agent_id = (
            agent_id.startswith("Agent") or
            agent_id.startswith("--") or
            agent_id.startswith("-") or
            agent_id.islower() and len(agent_id) <= 5  # Likely parsing errors: "can", "i", "yall"
        )
        
        if not looks_like_agent_id:
            continue
        
        # This is an invalid workspace
        inbox_dir = item / "inbox"
        messages = []
        if inbox_dir.exists():
            messages = list(inbox_dir.glob("*.md")) + list(inbox_dir.glob("*.json"))
        
        invalid_workspaces.append((item, messages))
    
    return invalid_workspaces


def archive_invalid_messages(invalid_dir: Path, messages: List[Path], archive_dir: Path) -> None:
    """Archive messages from invalid workspace before deletion."""
    if not messages:
        return
    
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    for msg_file in messages:
        archive_path = archive_dir / f"{invalid_dir.name}_{msg_file.name}"
        try:
            shutil.copy2(msg_file, archive_path)
            print(f"  ✅ Archived: {msg_file.name}")
        except Exception as e:
            print(f"  ⚠️ Failed to archive {msg_file.name}: {e}")


def fix_invalid_workspaces(dry_run: bool = False) -> None:
    """Fix invalid agent workspace directories."""
    workspace_root = Path("agent_workspaces")
    archive_dir = workspace_root / "archive" / "invalid_workspaces"
    
    print("=" * 70)
    print("🔍 SCANNING FOR INVALID AGENT WORKSPACES")
    print("=" * 70)
    print()
    
    invalid_workspaces = find_invalid_workspaces(workspace_root)
    
    if not invalid_workspaces:
        print("✅ No invalid workspaces found!")
        return
    
    print(f"Found {len(invalid_workspaces)} invalid workspace(s):\n")
    
    for invalid_dir, messages in invalid_workspaces:
        print(f"❌ Invalid: {invalid_dir.name}")
        if messages:
            print(f"   Messages: {len(messages)}")
            for msg in messages[:3]:  # Show first 3
                print(f"     - {msg.name}")
            if len(messages) > 3:
                print(f"     ... and {len(messages) - 3} more")
        print()
    
    if dry_run:
        print("🔍 DRY RUN - No changes made")
        return
    
    print("=" * 70)
    print("🗑️ REMOVING INVALID WORKSPACES")
    print("=" * 70)
    print()
    
    for invalid_dir, messages in invalid_workspaces:
        print(f"Removing: {invalid_dir.name}")
        
        # Archive messages first
        if messages:
            print(f"  Archiving {len(messages)} message(s)...")
            archive_invalid_messages(invalid_dir, messages, archive_dir)
        
        # Remove directory
        try:
            shutil.rmtree(invalid_dir)
            print(f"  ✅ Removed: {invalid_dir.name}")
        except Exception as e:
            print(f"  ❌ Failed to remove {invalid_dir.name}: {e}")
        print()
    
    print("=" * 70)
    print("✅ CLEANUP COMPLETE")
    print("=" * 70)
    print(f"\nArchived messages: {archive_dir}")


if __name__ == "__main__":
    import sys
    
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")
    
    fix_invalid_workspaces(dry_run=dry_run)

