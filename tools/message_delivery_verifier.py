#!/usr/bin/env python3
"""
Message Delivery Verifier Tool
===============================

A tool I wished I had during messaging system debugging:
- Verify message delivery status across queue and inbox
- Check for stuck/failed messages
- Verify inbox file creation and content
- Diagnose delivery issues
- Report delivery statistics

Usage:
    python tools/message_delivery_verifier.py --recipient Agent-7 --message-id msg_123
    python tools/message_delivery_verifier.py --check-queue
    python tools/message_delivery_verifier.py --stats
    python tools/message_delivery_verifier.py --verify-all

Author: Agent-4 (Captain)
Date: 2025-12-13
V2 Compliant: <400 lines
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.message_queue import MessageQueue, QueueConfig
from src.core.message_queue_persistence import QueueEntry


def verify_inbox_file(recipient: str, message_id: str) -> Dict:
    """Verify inbox file exists and has content."""
    inbox_path = Path(f"agent_workspaces/{recipient}/inbox/")
    if not inbox_path.exists():
        return {
            "status": "error",
            "message": f"Inbox directory does not exist: {inbox_path}",
        }

    # Search for message file (may have timestamp prefix)
    matching_files = list(inbox_path.glob(f"*{message_id}*"))
    if not matching_files:
        return {
            "status": "not_found",
            "message": f"No inbox file found for message_id: {message_id}",
            "inbox_path": str(inbox_path),
        }

    file_path = matching_files[0]
    try:
        file_size = file_path.stat().st_size
        if file_size == 0:
            return {
                "status": "error",
                "message": f"Inbox file is empty: {file_path}",
                "file_path": str(file_path),
            }

        # Check file age
        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        age_seconds = (datetime.now() - file_mtime).total_seconds()

        return {
            "status": "verified",
            "message": f"Inbox file verified: {file_path}",
            "file_path": str(file_path),
            "file_size": file_size,
            "created_at": file_mtime.isoformat(),
            "age_seconds": age_seconds,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error reading inbox file: {e}",
            "file_path": str(file_path),
        }


def check_queue_status() -> Dict:
    """Check message queue status."""
    queue = MessageQueue()
    config = QueueConfig()

    try:
        entries = queue.persistence.load_entries()
        total = len(entries)
        pending = sum(1 for e in entries if getattr(e, 'status', None) == "PENDING")
        processing = sum(1 for e in entries if getattr(e, 'status', None) == "PROCESSING")
        delivered = sum(1 for e in entries if getattr(e, 'status', None) == "DELIVERED")
        failed = sum(1 for e in entries if getattr(e, 'status', None) == "FAILED")

        # Check for stuck messages (processing > 1 hour)
        now = datetime.now()
        stuck = []
        for entry in entries:
            if getattr(entry, 'status', None) == "PROCESSING":
                metadata = getattr(entry, 'metadata', {}) or {}
                message = getattr(entry, 'message', {}) or {}
                recipient = message.get("recipient") if isinstance(message, dict) else getattr(message, 'recipient', 'unknown')
                if "processing_started_at" in metadata:
                    try:
                        started_at = datetime.fromisoformat(
                            metadata["processing_started_at"]
                        )
                        if (now - started_at).total_seconds() > 3600:
                            stuck.append(
                                {
                                    "queue_id": getattr(entry, 'queue_id', 'unknown'),
                                    "recipient": recipient,
                                    "stuck_for_seconds": int(
                                        (now - started_at).total_seconds()
                                    ),
                                }
                            )
                    except (ValueError, KeyError):
                        pass

        # Check failed messages with retry attempts
        failed_with_retries = []
        for entry in entries:
            if getattr(entry, 'status', None) == "FAILED":
                metadata = getattr(entry, 'metadata', {}) or {}
                message = getattr(entry, 'message', {}) or {}
                recipient = message.get("recipient") if isinstance(message, dict) else getattr(message, 'recipient', 'unknown')
                attempts = metadata.get("delivery_attempts", 0)
                if attempts > 0:
                    failed_with_retries.append(
                        {
                            "queue_id": getattr(entry, 'queue_id', 'unknown'),
                            "recipient": recipient,
                            "attempts": attempts,
                            "last_retry": metadata.get("last_retry_time"),
                            "next_retry": metadata.get("next_retry_time"),
                        }
                    )

        return {
            "status": "success",
            "summary": {
                "total": total,
                "pending": pending,
                "processing": processing,
                "delivered": delivered,
                "failed": failed,
            },
            "issues": {
                "stuck_messages": stuck,
                "failed_with_retries": failed_with_retries,
            },
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking queue: {e}",
        }


def verify_message_delivery(recipient: str, message_id: str) -> Dict:
    """Verify message delivery by checking both queue and inbox."""
    result = {
        "recipient": recipient,
        "message_id": message_id,
        "queue_status": None,
        "inbox_status": None,
        "delivery_verified": False,
    }

    # Check queue
    queue = MessageQueue()
    try:
        entries = queue.persistence.load_entries()
        matching_entries = []
        for e in entries:
            msg = getattr(e, 'message', {}) or {}
            recipient_match = False
            if isinstance(msg, dict):
                recipient_match = msg.get("recipient") == recipient
            else:
                recipient_match = getattr(msg, 'recipient', None) == recipient
            
            metadata = getattr(e, 'metadata', {}) or {}
            msg_id = metadata.get("message_id", "")
            if recipient_match and message_id in str(msg_id):
                matching_entries.append(e)

        if matching_entries:
            entry = matching_entries[0]
            metadata = getattr(entry, 'metadata', {}) or {}
            result["queue_status"] = {
                "status": getattr(entry, 'status', 'unknown'),
                "queue_id": getattr(entry, 'queue_id', 'unknown'),
                "created_at": getattr(entry, 'created_at', 'unknown'),
                "attempts": metadata.get("delivery_attempts", 0),
                "last_retry": metadata.get("last_retry_time"),
            }
        else:
            result["queue_status"] = {
                "status": "not_found",
                "message": "Message not found in queue",
            }
    except Exception as e:
        result["queue_status"] = {
            "status": "error",
            "message": str(e),
        }

    # Check inbox
    result["inbox_status"] = verify_inbox_file(recipient, message_id)

    # Overall verification
    if (
        result["queue_status"].get("status") == "DELIVERED"
        and result["inbox_status"]["status"] == "verified"
    ):
        result["delivery_verified"] = True

    return result


def get_delivery_stats() -> Dict:
    """Get delivery statistics."""
    queue = MessageQueue()
    try:
        entries = queue.persistence.load_entries()
        now = datetime.now()
        last_24h = now - timedelta(hours=24)

        recent_entries = [
            e
            for e in entries
            if datetime.fromisoformat(e.created_at) >= last_24h
        ]

        delivered = [e for e in recent_entries if getattr(e, 'status', None) == "DELIVERED"]
        failed = [e for e in recent_entries if getattr(e, 'status', None) == "FAILED"]

        # Calculate delivery rate
        total_recent = len(recent_entries)
        delivery_rate = (
            (len(delivered) / total_recent * 100) if total_recent > 0 else 0
        )

        # Average delivery attempts
        avg_attempts = 0
        if delivered:
            total_attempts = sum(
                (getattr(e, 'metadata', {}) or {}).get("delivery_attempts", 1) for e in delivered
            )
            avg_attempts = total_attempts / len(delivered)

        return {
            "status": "success",
            "last_24h": {
                "total": total_recent,
                "delivered": len(delivered),
                "failed": len(failed),
                "delivery_rate_percent": round(delivery_rate, 2),
                "avg_attempts": round(avg_attempts, 2),
            },
            "all_time": {
                "total": len(entries),
                "delivered": sum(1 for e in entries if getattr(e, 'status', None) == "DELIVERED"),
                "failed": sum(1 for e in entries if getattr(e, 'status', None) == "FAILED"),
            },
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


def verify_all_recipients() -> Dict:
    """Verify inbox files for all agents."""
    agents = [
        "Agent-1",
        "Agent-2",
        "Agent-3",
        "Agent-5",
        "Agent-6",
        "Agent-7",
        "Agent-8",
        "Agent-4",
    ]

    results = {}
    for agent in agents:
        inbox_path = Path(f"agent_workspaces/{agent}/inbox/")
        if inbox_path.exists():
            files = list(inbox_path.glob("*.md"))
            results[agent] = {
                "inbox_exists": True,
                "file_count": len(files),
                "latest_file": (
                    max(files, key=lambda p: p.stat().st_mtime).name
                    if files
                    else None
                ),
            }
        else:
            results[agent] = {
                "inbox_exists": False,
                "file_count": 0,
            }

    return {"status": "success", "agents": results}


def main():
    parser = argparse.ArgumentParser(
        description="Verify message delivery status and diagnose issues"
    )
    parser.add_argument(
        "--recipient", "-r", help="Recipient agent ID (e.g., Agent-7)"
    )
    parser.add_argument("--message-id", "-m", help="Message ID to verify")
    parser.add_argument(
        "--check-queue", action="store_true", help="Check queue status"
    )
    parser.add_argument("--stats", action="store_true", help="Get delivery statistics")
    parser.add_argument(
        "--verify-all", action="store_true", help="Verify all agent inboxes"
    )

    args = parser.parse_args()

    if args.check_queue:
        result = check_queue_status()
        print(json.dumps(result, indent=2))
        return 0

    if args.stats:
        result = get_delivery_stats()
        print(json.dumps(result, indent=2))
        return 0

    if args.verify_all:
        result = verify_all_recipients()
        print(json.dumps(result, indent=2))
        return 0

    if args.recipient and args.message_id:
        result = verify_message_delivery(args.recipient, args.message_id)
        print(json.dumps(result, indent=2))
        return 0 if result["delivery_verified"] else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

