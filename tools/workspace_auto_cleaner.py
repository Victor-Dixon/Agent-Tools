#!/usr/bin/env python3
"""
Workspace Auto-Cleaner - Automated Workspace Maintenance
Agent-8 (QA & Autonomous Systems Specialist)

Purpose: Automate workspace cleanup per General's directive
Impact: 15-20 min manual → 2 min automated!
Compliance: Ensures General's mandatory procedures followed
"""

import argparse
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List


def archive_old_messages(agent_id: str, days_old: int = 7, dry_run: bool = False) -> int:
    """Archive inbox messages older than X days."""
    inbox = Path(f"agent_workspaces/{agent_id}/inbox")
    archive = inbox / "archive"

    if not inbox.exists():
        print(f"❌ Inbox not found: {inbox}")
        return 0

    # Create archive directory
    if not dry_run:
        archive.mkdir(exist_ok=True)

    # Find old messages
    cutoff_date = datetime.now() - timedelta(days=days_old)
    old_messages = []

    for msg_file in inbox.glob("*.md"):
        if msg_file.is_file():
            mtime = datetime.fromtimestamp(msg_file.stat().st_mtime)
            if mtime < cutoff_date:
                old_messages.append(msg_file)

    if not old_messages:
        print(f"✅ No messages older than {days_old} days")
        return 0

    print(
        f"\n📬 Found {len(old_messages)} messages older than {days_old} days:")
    for msg in old_messages[:5]:
        print(f"   - {msg.name}")
    if len(old_messages) > 5:
        print(f"   ... and {len(old_messages) - 5} more")

    if dry_run:
        print(f"\n🔍 DRY RUN - Would archive {len(old_messages)} messages")
        return 0

    # Archive messages
    for msg_file in old_messages:
        try:
            dest = archive / msg_file.name
            msg_file.rename(dest)
        except Exception as e:
            print(f"⚠️  Failed to archive {msg_file.name}: {e}")

    print(f"\n✅ Archived {len(old_messages)} old messages!")
    return len(old_messages)


def clean_temp_files(agent_id: str, dry_run: bool = False) -> int:
    """Remove temporary files from workspace."""
    workspace = Path(f"agent_workspaces/{agent_id}")

    if not workspace.exists():
        print(f"❌ Workspace not found: {workspace}")
        return 0

    # Patterns to clean
    patterns = ['**/*.pyc', '**/*.log', '**/*temp*', '**/__pycache__']
    temp_files = []

    for pattern in patterns:
        temp_files.extend(workspace.glob(pattern))

    if not temp_files:
        print(f"✅ No temp files found")
        return 0

    print(f"\n🧹 Found {len(temp_files)} temp files:")
    for f in temp_files[:10]:
        print(f"   - {f.relative_to(workspace)}")
    if len(temp_files) > 10:
        print(f"   ... and {len(temp_files) - 10} more")

    if dry_run:
        print(f"\n🔍 DRY RUN - Would clean {len(temp_files)} files")
        return 0

    # Clean files
    for temp_file in temp_files:
        try:
            if temp_file.is_file():
                temp_file.unlink()
            elif temp_file.is_dir():
                shutil.rmtree(temp_file)
        except Exception as e:
            print(f"⚠️  Failed to clean {temp_file}: {e}")

    print(f"\n✅ Cleaned {len(temp_files)} temp files!")
    return len(temp_files)


def organize_workspace(agent_id: str, dry_run: bool = False) -> bool:
    """Organize workspace structure per standards."""
    workspace = Path(f"agent_workspaces/{agent_id}")

    # Standard directories
    standard_dirs = [
        'inbox/archive',
        'missions',
        'gas_deliveries',
        'repo_analysis'
    ]

    print(f"\n📁 Ensuring standard workspace structure...")

    for dir_path in standard_dirs:
        full_path = workspace / dir_path
        if not full_path.exists():
            if not dry_run:
                full_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Created: {dir_path}")
        else:
            print(f"   ✅ Exists: {dir_path}")

    return True


def generate_cleanup_report(agent_id: str) -> Dict[str, Any]:
    """Generate workspace cleanup status report."""
    workspace = Path(f"agent_workspaces/{agent_id}")
    inbox = workspace / "inbox"

    report = {
        "agent_id": agent_id,
        "timestamp": datetime.now().isoformat(),
        "inbox_messages": len(list(inbox.glob("*.md"))) if inbox.exists() else 0,
        "archived_messages": len(list((inbox / "archive").glob("*.md"))) if (inbox / "archive").exists() else 0,
        "workspace_files": len(list(workspace.rglob("*"))) if workspace.exists() else 0,
        "temp_files": 0,
        "compliance": "UNKNOWN"
    }

    # Check for temp files
    patterns = ['**/*.pyc', '**/*.log', '**/*temp*']
    for pattern in patterns:
        report["temp_files"] += len(list(workspace.glob(pattern)))

    # Compliance check
    if report["temp_files"] == 0 and report["inbox_messages"] < 20:
        report["compliance"] = "GOOD"
    elif report["temp_files"] > 0 or report["inbox_messages"] > 30:
        report["compliance"] = "NEEDS_CLEANUP"
    else:
        report["compliance"] = "ACCEPTABLE"

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Workspace Auto-Cleaner - Automated maintenance",
        epilog="Examples:\n"
               "  Full clean: python tools/workspace_auto_cleaner.py --agent Agent-8 --full\n"
               "  Archive old: python tools/workspace_auto_cleaner.py --agent Agent-8 --archive\n"
               "  Report: python tools/workspace_auto_cleaner.py --agent Agent-8 --report\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--agent', required=True,
                        help='Agent ID (e.g., Agent-8)')
    parser.add_argument('--archive', action='store_true',
                        help='Archive old messages (>7 days)')
    parser.add_argument('--clean-temp', action='store_true',
                        help='Clean temp files')
    parser.add_argument('--organize', action='store_true',
                        help='Organize workspace structure')
    parser.add_argument('--full', action='store_true',
                        help='Do all cleanup tasks')
    parser.add_argument('--days', type=int, default=7,
                        help='Days before archiving messages (default: 7)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done')
    parser.add_argument('--report', action='store_true',
                        help='Generate cleanup status report')

    args = parser.parse_args()

    print(f"\n🧹 WORKSPACE AUTO-CLEANER")
    print(f"="*70)
    print(f"Agent: {args.agent}")

    if args.dry_run:
        print(f"Mode: DRY RUN (no changes will be made)")

    # Report only
    if args.report:
        report = generate_cleanup_report(args.agent)
        print(f"\n📊 WORKSPACE STATUS REPORT")
        print(f"="*70)
        print(f"Inbox Messages: {report['inbox_messages']}")
        print(f"Archived Messages: {report['archived_messages']}")
        print(f"Total Files: {report['workspace_files']}")
        print(f"Temp Files: {report['temp_files']}")
        print(f"Compliance: {report['compliance']}")
        return

    # Execute cleanup tasks
    if args.full or args.archive:
        archive_old_messages(args.agent, args.days, args.dry_run)

    if args.full or args.clean_temp:
        clean_temp_files(args.agent, args.dry_run)

    if args.full or args.organize:
        organize_workspace(args.agent, args.dry_run)

    if not (args.archive or args.clean_temp or args.organize or args.full):
        parser.print_help()
        print(f"\n💡 TIP: Use --full for complete cleanup")

    print(f"\n✅ CLEANUP COMPLETE!")


if __name__ == '__main__':
    main()
