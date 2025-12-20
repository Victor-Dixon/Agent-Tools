#!/usr/bin/env python3
"""
Fix Stuck Queue Messages
=========================

Resets messages stuck in PROCESSING status to PENDING for retry.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-13
"""

import json
from pathlib import Path
from datetime import datetime

def fix_stuck_messages():
    """Reset stuck PROCESSING messages to PENDING."""
    queue_file = Path("message_queue/queue.json")
    
    if not queue_file.exists():
        print("❌ Queue file not found")
        return
    
    # Load queue
    with open(queue_file, 'r', encoding='utf-8') as f:
        queue = json.load(f)
    
    # Find stuck PROCESSING messages
    stuck_messages = []
    reset_count = 0
    
    for entry in queue:
        if entry.get('status') == 'PROCESSING':
            updated_str = entry.get('updated_at', '')
            if updated_str:
                try:
                    # Parse timestamp
                    dt = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
                    if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                        dt = dt.replace(tzinfo=None)
                    
                    # Calculate age
                    age_seconds = (datetime.now() - dt).total_seconds()
                    
                    # Reset if older than 5 minutes
                    if age_seconds > 300:
                        entry['status'] = 'PENDING'
                        reset_count += 1
                        stuck_messages.append({
                            'queue_id': entry.get('queue_id', 'unknown')[:12],
                            'age_seconds': int(age_seconds),
                            'updated_at': updated_str
                        })
                except Exception as e:
                    print(f"⚠️ Error parsing timestamp for entry: {e}")
                    # Reset anyway if we can't parse
                    entry['status'] = 'PENDING'
                    reset_count += 1
    
    # Save queue
    if reset_count > 0:
        with open(queue_file, 'w', encoding='utf-8') as f:
            json.dump(queue, f, indent=2)
        
        print(f"✅ Reset {reset_count} stuck PROCESSING messages to PENDING")
        for msg in stuck_messages:
            print(f"   - {msg['queue_id']}... (age: {msg['age_seconds']}s)")
    else:
        print("✅ No stuck messages found")
    
    # Show current status
    status_counts = {}
    for entry in queue:
        status = entry.get('status', 'UNKNOWN')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\n📊 Current queue status:")
    for status, count in sorted(status_counts.items()):
        print(f"   {status}: {count}")

if __name__ == "__main__":
    fix_stuck_messages()


