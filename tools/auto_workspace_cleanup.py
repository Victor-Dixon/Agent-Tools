#!/usr/bin/env python3
"""
Auto-Workspace Cleanup Tool
============================

Automatically cleans agent workspaces by archiving old mission files,
maintaining only active/recent files for optimal workspace efficiency.

<!-- SSOT Domain: infrastructure -->

Created: 2025-10-15
Author: Agent-3 (Infrastructure & Monitoring Engineer)
Purpose: Autonomous efficient development - eliminate manual cleanup

Usage:
    python tools/auto_workspace_cleanup.py --agent Agent-3 --execute
    python tools/auto_workspace_cleanup.py --all-agents --dry-run
"""

import argparse
import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple


class AutoWorkspaceCleanup:
    """Automatically cleans and organizes agent workspaces."""

    def __init__(self, workspace_root: Path = Path("agent_workspaces"), dry_run: bool = True):
        self.workspace_root = workspace_root
        self.dry_run = dry_run
        self.stats = {
            "files_archived": 0,
            "files_kept": 0,
            "space_saved_kb": 0,
            "archives_created": 0,
        }

    def get_file_age(self, file_path: Path) -> int:
        """Get file age in days."""
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        age = (datetime.now() - mtime).days
        return age

    def should_archive(self, file_path: Path, status_data: Dict) -> Tuple[bool, str]:
        """
        Determine if a file should be archived.

        Returns:
            (should_archive, reason)
        """
        file_name = file_path.name
        age_days = self.get_file_age(file_path)

        # Keep critical files
        if file_name in ["status.json", "README.md"]:
            return False, "Critical file"

        # Keep recent files (< 7 days old)
        if age_days < 7:
            return False, f"Recent ({age_days} days old)"

        # Archive old mission files (C-* format)
        if file_name.startswith("C-") and file_name.endswith(".md"):
            if age_days > 14:
                return True, f"Old mission file ({age_days} days)"

        # Archive completed mission indicators
        if "COMPLETE" in file_name and age_days > 7:
            return True, f"Completed mission ({age_days} days)"

        # Archive old status reports
        if "STATUS" in file_name and age_days > 14:
            return True, f"Old status report ({age_days} days)"

        # Archive debate/vote files
        if any(
            keyword in file_name.upper() for keyword in ["DEBATE", "VOTE", "SWARM_PROPOSAL"]
        ):
            if age_days > 30:
                return True, f"Old debate/vote ({age_days} days)"

        # Archive week summaries
        if "WEEK" in file_name or "CYCLE" in file_name:
            if age_days > 21:
                return True, f"Old summary ({age_days} days)"

        # Keep everything else
        return False, "Active or unknown type"

    def cleanup_agent_workspace(self, agent_id: str) -> Dict:
        """
        Clean up a single agent's workspace.

        Returns:
            Cleanup statistics
        """
        agent_workspace = self.workspace_root / agent_id
        if not agent_workspace.exists():
            print(f"❌ Workspace not found: {agent_workspace}")
            return {}

        # Read status.json to understand current state
        status_file = agent_workspace / "status.json"
        status_data = {}
        if status_file.exists():
            try:
                status_data = json.loads(status_file.read_text())
            except Exception as e:
                print(f"⚠️  Could not read status.json: {e}")

        # Create archive directory
        archive_date = datetime.now().strftime("%Y-%m-%d")
        archive_dir = agent_workspace / f"archive_{archive_date}"

        files_to_archive = []
        files_to_keep = []

        # Scan all markdown files
        for md_file in agent_workspace.glob("*.md"):
            should_arch, reason = self.should_archive(md_file, status_data)

            if should_arch:
                files_to_archive.append((md_file, reason))
            else:
                files_to_keep.append((md_file, reason))

        # Execute or simulate
        if files_to_archive:
            if not self.dry_run:
                archive_dir.mkdir(exist_ok=True)
                self.stats["archives_created"] += 1

            print(f"\n🧹 **{agent_id}** - Cleaning workspace...")
            print(f"   Files before: {len(files_to_archive) + len(files_to_keep)}")

            for file_path, reason in files_to_archive:
                file_size_kb = file_path.stat().st_size / 1024

                if not self.dry_run:
                    shutil.move(str(file_path), str(archive_dir / file_path.name))

                self.stats["files_archived"] += 1
                self.stats["space_saved_kb"] += file_size_kb

                action = "Would archive" if self.dry_run else "Archived"
                print(f"   📦 {action}: {file_path.name} ({reason})")

            print(f"   Files after: {len(files_to_keep)}")
            print(
                f"   {'Would archive' if self.dry_run else 'Archived'}: {len(files_to_archive)} files"
            )

            if not self.dry_run:
                print(f"   Archive location: {archive_dir}")

        else:
            print(f"\n✅ **{agent_id}** - Workspace already clean! ({len(files_to_keep)} files)")

        self.stats["files_kept"] += len(files_to_keep)

        return {
            "agent_id": agent_id,
            "files_archived": len(files_to_archive),
            "files_kept": len(files_to_keep),
            "archive_dir": str(archive_dir) if files_to_archive else None,
        }

    def cleanup_all_agents(self) -> List[Dict]:
        """Clean up all agent workspaces."""
        results = []

        agent_dirs = [
            d for d in self.workspace_root.iterdir() if d.is_dir() and d.name.startswith("Agent-")
        ]

        print(f"\n{'=' * 60}")
        print(f"🧹 AUTO-WORKSPACE CLEANUP")
        print(f"{'=' * 60}")
        print(f"Mode: {'DRY-RUN (simulation)' if self.dry_run else 'EXECUTE (real)'}")
        print(f"Agents found: {len(agent_dirs)}")

        for agent_dir in sorted(agent_dirs):
            result = self.cleanup_agent_workspace(agent_dir.name)
            if result:
                results.append(result)

        # Summary
        print(f"\n{'=' * 60}")
        print(f"📊 CLEANUP SUMMARY")
        print(f"{'=' * 60}")
        print(f"Total files archived: {self.stats['files_archived']}")
        print(f"Total files kept: {self.stats['files_kept']}")
        print(f"Space saved: {self.stats['space_saved_kb']:.2f} KB")
        print(f"Archives created: {self.stats['archives_created']}")

        if self.dry_run:
            print(f"\n⚠️  DRY-RUN MODE - No files were actually moved!")
            print(f"   Run with --execute to perform cleanup")
        else:
            print(f"\n✅ CLEANUP COMPLETE!")

        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Auto-cleanup agent workspaces")
    parser.add_argument(
        "--agent", help="Specific agent to clean (e.g., Agent-3)", default=None
    )
    parser.add_argument(
        "--all-agents", action="store_true", help="Clean all agent workspaces"
    )
    parser.add_argument(
        "--execute", action="store_true", help="Execute cleanup (default is dry-run)"
    )
    parser.add_argument(
        "--workspace-root",
        default="agent_workspaces",
        help="Root directory for agent workspaces",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.agent and not args.all_agents:
        parser.error("Must specify either --agent or --all-agents")

    # Create cleanup tool
    cleanup = AutoWorkspaceCleanup(
        workspace_root=Path(args.workspace_root), dry_run=not args.execute
    )

    # Execute cleanup
    if args.all_agents:
        cleanup.cleanup_all_agents()
    elif args.agent:
        cleanup.cleanup_agent_workspace(args.agent)


if __name__ == "__main__":
    main()

