#!/usr/bin/env python3
"""
Fix Message Queue - Reset Stuck Messages and Clear Locks
========================================================

Fixes common message queue issues:
1. Clears lock files
2. Resets stuck PROCESSING messages to PENDING
3. Prepares queue for restart

Author: Agent-3 (Infrastructure & DevOps Specialist)
Date: 2025-12-14
Priority: CRITICAL
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def clear_lock_files():
    """Clear all lock files."""
    queue_dir = project_root / "message_queue"
    lock_files = [
        "delivered.json.lock",
        "failed.json.lock",
        "pending.json.lock",
        "processing.json.lock"
    ]
    
    cleared = []
    for lock_file in lock_files:
        lock_path = queue_dir / lock_file
        if lock_path.exists():
            try:
                lock_path.unlink()
                cleared.append(lock_file)
                print(f"✅ Cleared lock file: {lock_file}")
            except Exception as e:
                print(f"❌ Failed to clear {lock_file}: {e}")
    
    if not cleared:
        print("✅ No lock files found to clear")
    
    return len(cleared)

def reset_stuck_messages():
    """Reset stuck PROCESSING messages to PENDING."""
    queue_file = project_root / "message_queue" / "queue.json"
    
    if not queue_file.exists():
        print("❌ Queue file not found!")
        return 0
    
    # Load queue
    try:
        with open(queue_file, 'r', encoding='utf-8') as f:
            entries = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load queue file: {e}")
        return 0
    
    if not isinstance(entries, list):
        print("❌ Queue file is not a JSON array!")
        return 0
    
    # Find stuck messages (PROCESSING for > 5 minutes)
    now = datetime.now()
    reset_count = 0
    
    for entry in entries:
        if entry.get('status') == 'PROCESSING':
            updated_at = entry.get('updated_at')
            if updated_at:
                try:
                    if isinstance(updated_at, str):
                        # Handle ISO format
                        updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    else:
                        updated = datetime.fromisoformat(str(updated_at))
                    
                    # Remove timezone for comparison
                    if updated.tzinfo:
                        updated = updated.replace(tzinfo=None)
                    
                    age_seconds = (now - updated).total_seconds()
                    
                    # Reset if stuck for > 5 minutes
                    if age_seconds > 300:
                        entry['status'] = 'PENDING'
                        entry['updated_at'] = datetime.now().isoformat()
                        # Clear retry count
                        if 'metadata' in entry:
                            entry['metadata']['retry_count'] = 0
                        reset_count += 1
                        
                        recipient = 'unknown'
                        if isinstance(entry.get('message'), dict):
                            recipient = entry.get('message', {}).get('recipient', 'unknown')
                        
                        print(f"✅ Reset stuck message: {entry.get('queue_id', 'unknown')[:20]}... → {recipient} (stuck for {int(age_seconds)}s)")
                except Exception as e:
                    print(f"⚠️  Error processing entry {entry.get('queue_id', 'unknown')}: {e}")
                    # Reset anyway if we can't parse the date
                    entry['status'] = 'PENDING'
                    entry['updated_at'] = datetime.now().isoformat()
                    reset_count += 1
    
    # Save updated queue
    if reset_count > 0:
        try:
            # Create backup
            backup_file = queue_file.parent / f"queue_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(entries, f, indent=2)
            print(f"✅ Backup created: {backup_file.name}")
            
            # Save updated queue
            with open(queue_file, 'w', encoding='utf-8') as f:
                json.dump(entries, f, indent=2)
            print(f"✅ Queue file updated: {reset_count} messages reset to PENDING")
        except Exception as e:
            print(f"❌ Failed to save queue file: {e}")
            return 0
    
    return reset_count

def main():
    """Main fix routine."""
    print("=" * 70)
    print("MESSAGE QUEUE FIX")
    print("=" * 70)
    print()
    
    # Step 1: Clear lock files
    print("Step 1: Clearing lock files...")
    locks_cleared = clear_lock_files()
    print()
    
    # Step 2: Reset stuck messages
    print("Step 2: Resetting stuck messages...")
    messages_reset = reset_stuck_messages()
    print()
    
    # Summary
    print("=" * 70)
    print("FIX SUMMARY")
    print("=" * 70)
    print(f"Lock files cleared: {locks_cleared}")
    print(f"Messages reset: {messages_reset}")
    print()
    
    if locks_cleared > 0 or messages_reset > 0:
        print("✅ Queue fixed! You can now restart the queue processor:")
        print("   python tools/start_message_queue_processor.py")
    else:
        print("✅ No issues found - queue appears healthy")
    
    print()

if __name__ == "__main__":
    main()


