#!/usr/bin/env python3
"""
Reset Stuck Messages in Queue
==============================

Resets messages stuck in PROCESSING status back to PENDING for retry,
or marks them as FAILED if they're too old.

<!-- SSOT Domain: infrastructure -->

Author: Agent-7 (Web Development Specialist)
Date: 2025-01-27
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def reset_stuck_messages(reset_to_pending=True, min_age_minutes=5):
    """Reset messages stuck in PROCESSING status."""
    print("🔧 Resetting stuck messages in queue...\n")

    # Load queue
    queue_file = project_root / "message_queue" / "queue.json"
    if not queue_file.exists():
        print("❌ Queue file not found:", queue_file)
        return 1

    with open(queue_file, 'r', encoding='utf-8') as f:
        queue_data = json.load(f)

    # Handle both list and dict formats
    if isinstance(queue_data, list):
        entries = queue_data
    else:
        entries = queue_data.get('entries', [])

    # Find stuck messages
    processing = [e for e in entries if e.get('status') == 'PROCESSING']

    if not processing:
        print("✅ No stuck messages found!")
        return 0

    print(f"⚠️ Found {len(processing)} stuck messages\n")

    # Reset messages
    now = datetime.now()
    reset_count = 0
    failed_count = 0

    for entry in processing:
        created_str = entry.get('created_at', '')
        age_minutes = None

        try:
            if created_str:
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                age = now - created.replace(tzinfo=None) if created.tzinfo else now - created
                age_minutes = age.total_seconds() / 60
        except Exception:
            pass

        # If message is old (>min_age_minutes), mark as FAILED
        # Otherwise reset to PENDING
        if age_minutes and age_minutes > min_age_minutes:
            entry['status'] = 'FAILED'
            entry['error'] = f'Stuck in PROCESSING for {int(age_minutes)} minutes - reset by tool'
            failed_count += 1
            print(f"   ❌ Marked as FAILED: {entry.get('queue_id', 'N/A')[:20]}... (age: {int(age_minutes)} min)")
        elif reset_to_pending:
            entry['status'] = 'PENDING'
            reset_count += 1
            age_str = f"{int(age_minutes)} min" if age_minutes else "unknown"
            print(f"   🔄 Reset to PENDING: {entry.get('queue_id', 'N/A')[:20]}... (age: {age_str})")

    # Save updated queue
    if isinstance(queue_data, list):
        updated_data = entries
    else:
        queue_data['entries'] = entries
        updated_data = queue_data

    # Backup original
    backup_file = queue_file.with_suffix('.json.backup')
    if queue_file.exists():
        import shutil
        shutil.copy2(queue_file, backup_file)
        print(f"\n📦 Backup created: {backup_file}")

    # Write updated queue
    with open(queue_file, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Reset complete:")
    print(f"   🔄 Reset to PENDING: {reset_count}")
    print(f"   ❌ Marked as FAILED: {failed_count}")
    print(f"   📝 Queue file updated: {queue_file}")

    return 0


def main():
    """Main entry point for the tool."""
    import argparse
    parser = argparse.ArgumentParser(description="Reset stuck messages in queue")
    parser.add_argument("--fail-old", action="store_true",
                       help="Mark old messages (>5 min) as FAILED instead of resetting")
    parser.add_argument("--min-age", type=int, default=5,
                       help="Minimum age in minutes to mark as FAILED (default: 5)")
    args = parser.parse_args()

    return reset_stuck_messages(
        reset_to_pending=not args.fail_old,
        min_age_minutes=args.min_age
    )

if __name__ == "__main__":
    sys.exit(main())
