#!/usr/bin/env python3
"""
Quick Message Queue Status Check
=================================

Quick check if message queue is working.

Author: Agent-3
Date: 2025-12-14
"""

import json
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def check_queue_status():
    """Check queue status."""
    queue_file = project_root / "message_queue" / "queue.json"
    
    print("📬 Message Queue Status")
    print("=" * 50)
    
    # Check lock files
    queue_dir = queue_file.parent
    lock_files = [
        "delivered.json.lock",
        "failed.json.lock",
        "pending.json.lock",
        "processing.json.lock"
    ]
    
    has_locks = any((queue_dir / lf).exists() for lf in lock_files)
    if has_locks:
        print("⚠️  Lock files present (processor may be running or stuck)")
    else:
        print("✅ No lock files (processor may not be running)")
    
    # Check queue file
    if not queue_file.exists():
        print("❌ Queue file not found!")
        return
    
    try:
        with open(queue_file, 'r', encoding='utf-8') as f:
            entries = json.load(f)
        
        if not isinstance(entries, list):
            print("❌ Queue file is corrupted!")
            return
        
        # Count by status
        statuses = {}
        for entry in entries:
            status = entry.get('status', 'UNKNOWN')
            statuses[status] = statuses.get(status, 0) + 1
        
        print(f"\nTotal messages: {len(entries)}")
        print("\nStatus breakdown:")
        for status, count in sorted(statuses.items()):
            print(f"  {status}: {count}")
        
        # Check for stuck messages
        now = datetime.now()
        stuck = 0
        for entry in entries:
            if entry.get('status') == 'PROCESSING':
                updated_at = entry.get('updated_at')
                if updated_at:
                    try:
                        if isinstance(updated_at, str):
                            updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                        else:
                            updated = datetime.fromisoformat(str(updated_at))
                        if updated.tzinfo:
                            updated = updated.replace(tzinfo=None)
                        age = (now - updated).total_seconds()
                        if age > 300:  # 5 minutes
                            stuck += 1
                    except:
                        stuck += 1
        
        if stuck > 0:
            print(f"\n⚠️  {stuck} stuck message(s) found")
            print("   Run: python tools/fix_message_queue.py")
        else:
            print("\n✅ No stuck messages")
        
        # Check if processor should be running
        pending = statuses.get('PENDING', 0)
        if pending > 0:
            print(f"\n📨 {pending} message(s) waiting to be processed")
            print("   Start processor: python tools/start_message_queue_processor.py")
        else:
            print("\n✅ No pending messages")
            
    except Exception as e:
        print(f"❌ Error reading queue: {e}")

if __name__ == "__main__":
    check_queue_status()


