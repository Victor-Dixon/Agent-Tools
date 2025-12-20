#!/usr/bin/env python3
"""
Message Compression Automation Tool
====================================

Automates message history compression following the compression plan.
Compresses messages based on age while preserving learning value.

Compression Levels:
- Level 1 (0-7 days): Full detail
- Level 2 (7-30 days): Truncated content
- Level 3 (30+ days): Aggregated statistics

<!-- SSOT Domain: infrastructure -->

Author: Agent-3 (Infrastructure & DevOps) - JET FUEL AUTONOMOUS MODE
Created: 2025-01-27
Priority: CRITICAL
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageCompressionAutomation:
    """Automated message compression system."""

    def __init__(self, history_file: str = "data/message_history.json"):
        """Initialize compression automation."""
        self.history_file = Path(history_file)
        self.archive_dir = self.history_file.parent / "message_history_archive"
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def compress_message(self, message: dict[str, Any], age_days: int) -> dict[str, Any] | None:
        """
        Compress message based on age.
        
        Args:
            message: Message dictionary
            age_days: Age of message in days
            
        Returns:
            Compressed message dict or None if should be aggregated
        """
        if age_days <= 7:
            # Level 1: Full detail
            return message
        
        elif age_days <= 30:
            # Level 2: Truncated content
            content = str(message.get("content", ""))
            compressed = {
                "from": message.get("from") or message.get("sender", "UNKNOWN"),
                "to": message.get("to") or message.get("recipient", "UNKNOWN"),
                "timestamp": message.get("timestamp", ""),
                "queue_id": message.get("queue_id"),
                "message_type": message.get("message_type") or message.get("type", "text"),
                "priority": message.get("priority", "regular"),
                "content_preview": content[:200] if len(content) > 200 else content,
                "content_length": len(content),
                "compressed_at": datetime.now().isoformat(),
            }
            return compressed
        
        else:
            # Level 3: Will be aggregated
            return None

    def aggregate_messages(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Aggregate messages into statistics.
        
        Args:
            messages: List of messages to aggregate
            
        Returns:
            Aggregated statistics dictionary
        """
        if not messages:
            return {}
        
        # Get date from first message
        first_timestamp = messages[0].get("timestamp", "")
        date = first_timestamp[:10] if len(first_timestamp) >= 10 else datetime.now().date().isoformat()
        
        stats = {
            "date": date,
            "total_messages": len(messages),
            "by_sender": {},
            "by_recipient": {},
            "by_type": {},
            "by_priority": {},
            "aggregated_at": datetime.now().isoformat(),
        }
        
        for msg in messages:
            # Count by sender
            sender = msg.get("from") or msg.get("sender", "UNKNOWN")
            stats["by_sender"][sender] = stats["by_sender"].get(sender, 0) + 1
            
            # Count by recipient
            recipient = msg.get("to") or msg.get("recipient", "UNKNOWN")
            stats["by_recipient"][recipient] = stats["by_recipient"].get(recipient, 0) + 1
            
            # Count by type
            msg_type = msg.get("message_type") or msg.get("type", "unknown")
            stats["by_type"][msg_type] = stats["by_type"].get(msg_type, 0) + 1
            
            # Count by priority
            priority = msg.get("priority", "regular")
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
        
        return stats

    def calculate_age_days(self, timestamp_str: str) -> int:
        """Calculate age of message in days."""
        try:
            msg_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            now = datetime.now(msg_time.tzinfo) if msg_time.tzinfo else datetime.now()
            age = (now - msg_time).days
            return max(0, age)
        except (ValueError, AttributeError):
            return 0

    def compress_history(self, dry_run: bool = False) -> dict[str, Any]:
        """
        Compress message history.
        
        Args:
            dry_run: If True, don't save changes
            
        Returns:
            Compression statistics
        """
        if not self.history_file.exists():
            logger.warning(f"History file not found: {self.history_file}")
            return {"error": "History file not found"}
        
        # Load history
        try:
            with open(self.history_file, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            return {"error": str(e)}
        
        messages = data.get("messages", [])
        original_count = len(messages)
        now = datetime.now()
        
        # Separate messages by age
        level1_messages = []  # 0-7 days: Full
        level2_messages = []  # 7-30 days: Compressed
        level3_messages = []  # 30+ days: Aggregated
        
        for msg in messages:
            timestamp = msg.get("timestamp", "")
            age_days = self.calculate_age_days(timestamp)
            
            if age_days <= 7:
                level1_messages.append(msg)
            elif age_days <= 30:
                compressed = self.compress_message(msg, age_days)
                if compressed:
                    level2_messages.append(compressed)
            else:
                level3_messages.append(msg)
        
        # Aggregate level 3 messages by date
        daily_aggregates = {}
        for msg in level3_messages:
            timestamp = msg.get("timestamp", "")
            date = timestamp[:10] if len(timestamp) >= 10 else datetime.now().date().isoformat()
            
            if date not in daily_aggregates:
                daily_aggregates[date] = []
            daily_aggregates[date].append(msg)
        
        # Create aggregated statistics
        aggregated_stats = []
        for date, date_messages in daily_aggregates.items():
            stats = self.aggregate_messages(date_messages)
            aggregated_stats.append(stats)
        
        # Save aggregated statistics
        if aggregated_stats and not dry_run:
            for stats in aggregated_stats:
                date = stats.get("date", datetime.now().date().isoformat())
                archive_file = self.archive_dir / f"daily_aggregate_{date}.json"
                with open(archive_file, "w", encoding="utf-8") as f:
                    json.dump(stats, f, indent=2, ensure_ascii=False)
        
        # Combine compressed messages
        compressed_messages = level1_messages + level2_messages
        
        # Update history
        if not dry_run:
            data["messages"] = compressed_messages
            data["metadata"] = data.get("metadata", {})
            data["metadata"]["last_compressed"] = datetime.now().isoformat()
            data["metadata"]["compression_stats"] = {
                "original_count": original_count,
                "compressed_count": len(compressed_messages),
                "aggregated_count": len(level3_messages),
                "level1_count": len(level1_messages),
                "level2_count": len(level2_messages),
            }
            
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Calculate compression ratio
        original_size = self.history_file.stat().st_size if self.history_file.exists() else 0
        if not dry_run:
            compressed_size = self.history_file.stat().st_size
        else:
            # Estimate compressed size
            compressed_size = int(original_size * 0.3)  # Rough estimate
        
        stats = {
            "original_count": original_count,
            "compressed_count": len(compressed_messages),
            "aggregated_count": len(level3_messages),
            "level1_count": len(level1_messages),
            "level2_count": len(level2_messages),
            "aggregated_files": len(aggregated_stats),
            "original_size_bytes": original_size,
            "compressed_size_bytes": compressed_size,
            "compression_ratio": f"{(1 - compressed_size / original_size) * 100:.1f}%" if original_size > 0 else "0%",
            "dry_run": dry_run,
        }
        
        logger.info(f"✅ Compression complete: {stats}")
        return stats

    def run_automated_compression(self) -> dict[str, Any]:
        """Run automated compression (main entry point)."""
        logger.info("🚀 Starting automated message compression...")
        return self.compress_history(dry_run=False)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Message Compression Automation")
    parser.add_argument("--dry-run", action="store_true", help="Preview compression without saving")
    parser.add_argument("--history-file", default="data/message_history.json", help="Path to message history file")
    
    args = parser.parse_args()
    
    automation = MessageCompressionAutomation(history_file=args.history_file)
    stats = automation.compress_history(dry_run=args.dry_run)
    
    print(json.dumps(stats, indent=2))
    
    if args.dry_run:
        print("\n💡 This was a dry run. Use without --dry-run to apply compression.")


if __name__ == "__main__":
    main()




