#!/usr/bin/env python3
"""
Auto-Inbox Processor
====================

Automatically processes agent inbox messages, categorizes them,
archives processed messages, and generates summary reports.

Created: 2025-10-15
Author: Agent-3 (Infrastructure & Monitoring Engineer)
Purpose: Autonomous efficient development - eliminate manual inbox processing

Usage:
    python tools/auto_inbox_processor.py --agent Agent-3 --execute
    python tools/auto_inbox_processor.py --all-agents --summary-only
"""

import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class AutoInboxProcessor:
    """Automatically processes and organizes agent inbox messages."""

    def __init__(self, workspace_root: Path = Path("agent_workspaces"), dry_run: bool = True):
        self.workspace_root = workspace_root
        self.dry_run = dry_run
        self.stats = {
            "messages_processed": 0,
            "messages_archived": 0,
            "urgent_messages": 0,
            "stale_messages": 0,
        }

    def parse_message_metadata(self, message_path: Path) -> Dict:
        """
        Extract metadata from message file.

        Returns:
            Message metadata dict
        """
        try:
            content = message_path.read_text(encoding="utf-8")

            metadata = {
                "file_name": message_path.name,
                "from": None,
                "to": None,
                "priority": "normal",
                "timestamp": None,
                "type": None,
                "tags": [],
                "content_preview": "",
            }

            # Extract fields using regex
            from_match = re.search(r"\*\*From\*\*:\s*(.+)", content, re.IGNORECASE)
            if from_match:
                metadata["from"] = from_match.group(1).strip()

            to_match = re.search(r"\*\*To\*\*:\s*(.+)", content, re.IGNORECASE)
            if to_match:
                metadata["to"] = to_match.group(1).strip()

            priority_match = re.search(r"\*\*Priority\*\*:\s*(.+)", content, re.IGNORECASE)
            if priority_match:
                metadata["priority"] = priority_match.group(1).strip().lower()

            timestamp_match = re.search(r"\*\*Timestamp\*\*:\s*(.+)", content, re.IGNORECASE)
            if timestamp_match:
                metadata["timestamp"] = timestamp_match.group(1).strip()

            type_match = re.search(r"MESSAGE.*?-\s*(\w+)", content, re.IGNORECASE)
            if type_match:
                metadata["type"] = type_match.group(1).lower()

            tags_match = re.search(r"\*\*Tags\*\*:\s*(.+)", content, re.IGNORECASE)
            if tags_match:
                tags_str = tags_match.group(1).strip()
                metadata["tags"] = [t.strip() for t in tags_str.split(",")]

            # Content preview (first 100 chars after headers)
            lines = content.split("\n")
            content_lines = [
                line for line in lines if line.strip() and not line.startswith("**")
            ]
            if content_lines:
                metadata["content_preview"] = content_lines[0][:100]

            return metadata

        except Exception as e:
            print(f"⚠️  Error parsing {message_path.name}: {e}")
            return {"file_name": message_path.name, "error": str(e)}

    def categorize_message(self, metadata: Dict) -> Tuple[str, str]:
        """
        Categorize message and determine action.

        Returns:
            (category, action)
        """
        file_name = metadata.get("file_name", "")
        priority = metadata.get("priority", "normal")
        timestamp = metadata.get("timestamp")

        # Check if urgent
        if priority in ["urgent", "high", "critical"]:
            return "urgent", "flag"

        # Check if mission assignment
        if "MISSION" in file_name.upper() or "mission" in metadata.get("content_preview", ""):
            return "mission", "process"

        # Check if execution order
        if "EXECUTION_ORDER" in file_name or "C2A_" in file_name:
            return "order", "process"

        # Check if old/stale (based on naming patterns)
        if timestamp:
            try:
                # Try to parse timestamp
                if "2025-10-09" in timestamp or "2025-10-10" in timestamp:
                    return "stale", "archive"
            except:
                pass

        # Check if response (from other agents)
        if metadata.get("from", "").startswith("Agent-"):
            return "a2a_message", "process"

        # Check if acknowledgment/response needed
        if any(
            keyword in file_name.upper()
            for keyword in ["RESPONSE", "ACKNOWLEDGMENT", "REPLY"]
        ):
            return "response", "process"

        # Default
        return "general", "process"

    def process_inbox(self, agent_id: str) -> Dict:
        """
        Process a single agent's inbox.

        Returns:
            Processing statistics
        """
        inbox_dir = self.workspace_root / agent_id / "inbox"
        if not inbox_dir.exists():
            print(f"❌ Inbox not found: {inbox_dir}")
            return {}

        # Create archive directory
        archive_date = datetime.now().strftime("%Y-%m-%d")
        archive_dir = inbox_dir / f"archive_{archive_date}"

        # Scan all messages
        messages = list(inbox_dir.glob("*.md")) + list(inbox_dir.glob("*.txt"))

        if not messages:
            print(f"\n✅ **{agent_id}** - Inbox empty!")
            return {"agent_id": agent_id, "messages": 0}

        print(f"\n📬 **{agent_id}** - Processing inbox...")
        print(f"   Messages found: {len(messages)}")

        categorized = {
            "urgent": [],
            "mission": [],
            "order": [],
            "stale": [],
            "a2a_message": [],
            "response": [],
            "general": [],
        }

        # Process each message
        for msg_path in messages:
            metadata = self.parse_message_metadata(msg_path)
            category, action = self.categorize_message(metadata)

            categorized[category].append(
                {"path": msg_path, "metadata": metadata, "action": action}
            )

            self.stats["messages_processed"] += 1

        # Report findings
        print(f"\n   📊 Categorization:")
        if categorized["urgent"]:
            print(f"      🚨 URGENT: {len(categorized['urgent'])} messages")
            for msg in categorized["urgent"]:
                print(f"         - {msg['metadata']['file_name']}")
            self.stats["urgent_messages"] += len(categorized["urgent"])

        if categorized["mission"] or categorized["order"]:
            total = len(categorized["mission"]) + len(categorized["order"])
            print(f"      📋 Missions/Orders: {total} messages")

        if categorized["a2a_message"]:
            print(f"      🤝 A2A Messages: {len(categorized['a2a_message'])} messages")

        if categorized["stale"]:
            print(f"      📦 Stale (archive): {len(categorized['stale'])} messages")
            self.stats["stale_messages"] += len(categorized["stale"])

        # Archive stale messages
        if categorized["stale"] and not self.dry_run:
            archive_dir.mkdir(exist_ok=True)

            for msg in categorized["stale"]:
                shutil.move(str(msg["path"]), str(archive_dir / msg["path"].name))
                print(f"      📦 Archived: {msg['metadata']['file_name']}")

            self.stats["messages_archived"] += len(categorized["stale"])

        elif categorized["stale"] and self.dry_run:
            print(f"      (Would archive {len(categorized['stale'])} stale messages)")

        # Generate summary
        active_messages = (
            len(categorized["urgent"])
            + len(categorized["mission"])
            + len(categorized["order"])
            + len(categorized["a2a_message"])
            + len(categorized["response"])
            + len(categorized["general"])
        )

        print(f"\n   📊 Summary:")
        print(f"      Total messages: {len(messages)}")
        print(f"      Active: {active_messages}")
        print(f"      Archived: {len(categorized['stale'])}")

        return {
            "agent_id": agent_id,
            "total_messages": len(messages),
            "active_messages": active_messages,
            "archived_messages": len(categorized["stale"]),
            "urgent_count": len(categorized["urgent"]),
            "categorized": {k: len(v) for k, v in categorized.items()},
        }

    def process_all_inboxes(self) -> List[Dict]:
        """Process all agent inboxes."""
        results = []

        agent_dirs = [
            d for d in self.workspace_root.iterdir() if d.is_dir() and d.name.startswith("Agent-")
        ]

        print(f"\n{'=' * 60}")
        print(f"📬 AUTO-INBOX PROCESSOR")
        print(f"{'=' * 60}")
        print(f"Mode: {'DRY-RUN (simulation)' if self.dry_run else 'EXECUTE (real)'}")
        print(f"Agents found: {len(agent_dirs)}")

        for agent_dir in sorted(agent_dirs):
            result = self.process_inbox(agent_dir.name)
            if result:
                results.append(result)

        # Summary
        print(f"\n{'=' * 60}")
        print(f"📊 PROCESSING SUMMARY")
        print(f"{'=' * 60}")
        print(f"Total messages processed: {self.stats['messages_processed']}")
        print(f"Urgent messages flagged: {self.stats['urgent_messages']}")
        print(f"Stale messages found: {self.stats['stale_messages']}")
        print(f"Messages archived: {self.stats['messages_archived']}")

        if self.dry_run:
            print(f"\n⚠️  DRY-RUN MODE - No files were actually moved!")
            print(f"   Run with --execute to process inbox")
        else:
            print(f"\n✅ INBOX PROCESSING COMPLETE!")

        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Auto-process agent inboxes")
    parser.add_argument(
        "--agent", help="Specific agent to process (e.g., Agent-3)", default=None
    )
    parser.add_argument(
        "--all-agents", action="store_true", help="Process all agent inboxes"
    )
    parser.add_argument(
        "--execute", action="store_true", help="Execute processing (default is dry-run)"
    )
    parser.add_argument(
        "--summary-only", action="store_true", help="Show summary without archiving"
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

    # Create processor
    processor = AutoInboxProcessor(
        workspace_root=Path(args.workspace_root), dry_run=not args.execute or args.summary_only
    )

    # Execute processing
    if args.all_agents:
        processor.process_all_inboxes()
    elif args.agent:
        processor.process_inbox(args.agent)


if __name__ == "__main__":
    main()

