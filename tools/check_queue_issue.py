#!/usr/bin/env python3
"""Quick diagnostic for queue issues."""
import json
from pathlib import Path

queue_file = Path("message_queue/queue.json")
if queue_file.exists():
    data = json.loads(queue_file.read_text())
    entries = data if isinstance(data, list) else []
    
    failed = [e for e in entries if e.get('status') == 'FAILED']
    pending = [e for e in entries if e.get('status') == 'PENDING']
    
    print(f"Total entries: {len(entries)}")
    print(f"PENDING: {len(pending)}")
    print(f"FAILED: {len(failed)}")
    
    if failed:
        print("\nFAILED MESSAGES:")
        for e in failed:
            msg = e.get('message', {})
            meta = e.get('metadata', {})
            print(f"\n  Queue ID: {e.get('queue_id')}")
            print(f"  Recipient: {msg.get('recipient')}")
            print(f"  Error: {meta.get('last_error', 'unknown')}")
            print(f"  Attempts: {meta.get('delivery_attempts', 0)}")
            print(f"  Created: {e.get('created_at')}")
            
else:
    print("Queue file not found!")



