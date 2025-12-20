#!/usr/bin/env python3
"""
Quick Message Queue Debug Tool
==============================
Simple tool to check queue status without file locking issues.
"""

import json
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
queue_file = project_root / "message_queue" / "queue.json"

print("=" * 70)
print("MESSAGE QUEUE DEBUG")
print("=" * 70)
print(f"\nQueue file: {queue_file}")
print(f"Exists: {queue_file.exists()}")

if not queue_file.exists():
    print("\n❌ Queue file does not exist!")
    print("   This is normal if no messages have been queued yet.")
    sys.exit(0)

try:
    # Try to read with minimal locking
    with open(queue_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        print(f"\n❌ Queue file is not a JSON array! Type: {type(data)}")
        sys.exit(1)
    
    print(f"✅ Queue file loaded successfully")
    print(f"   Total entries: {len(data)}")
    
    # Status distribution
    statuses = Counter(e.get('status', 'UNKNOWN') for e in data)
    print(f"\n📊 Status Distribution:")
    for status, count in statuses.most_common():
        print(f"   {status}: {count}")
    
    # Check for stuck messages
    now = datetime.now()
    stuck = []
    for entry in data:
        if entry.get('status') == 'PROCESSING':
            updated = entry.get('updated_at')
            if updated:
                try:
                    if isinstance(updated, str):
                        updated_dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
                        if updated_dt.tzinfo:
                            updated_dt = updated_dt.replace(tzinfo=None)
                    else:
                        updated_dt = updated
                    
                    age = (now - updated_dt).total_seconds()
                    if age > 300:  # 5 minutes
                        stuck.append({
                            'id': entry.get('queue_id', 'unknown')[:16],
                            'recipient': entry.get('message', {}).get('recipient', 'unknown') if isinstance(entry.get('message'), dict) else 'unknown',
                            'age_minutes': int(age / 60)
                        })
                except Exception:
                    pass
    
    if stuck:
        print(f"\n⚠️  STUCK MESSAGES: {len(stuck)}")
        for msg in stuck[:5]:
            print(f"   ID: {msg['id']}... → {msg['recipient']} (stuck {msg['age_minutes']} min)")
    else:
        print(f"\n✅ No stuck messages")
    
    # Failed messages
    failed = [e for e in data if e.get('status') == 'FAILED']
    if failed:
        print(f"\n⚠️  FAILED MESSAGES: {len(failed)}")
        errors = Counter(
            e.get('metadata', {}).get('last_error', 'unknown')[:50] 
            for e in failed
        )
        for error, count in errors.most_common(5):
            print(f"   {error}: {count}")
    
    # Recent activity
    recent = sorted(
        [e for e in data if 'created_at' in e],
        key=lambda x: x.get('created_at', ''),
        reverse=True
    )[:3]
    
    if recent:
        print(f"\n📝 Recent Entries:")
        for e in recent:
            status = e.get('status', 'UNKNOWN')
            created = e.get('created_at', 'unknown')[:19] if isinstance(e.get('created_at'), str) else 'unknown'
            recipient = e.get('message', {}).get('recipient', 'unknown') if isinstance(e.get('message'), dict) else 'unknown'
            print(f"   [{status}] → {recipient} ({created})")
    
    # Check for common issues
    print(f"\n🔍 Issue Check:")
    issues = []
    
    # Missing recipients
    missing_recipient = sum(1 for e in data 
                           if isinstance(e.get('message'), dict) 
                           and not e.get('message', {}).get('recipient'))
    if missing_recipient:
        issues.append(f"   ⚠️  {missing_recipient} entries missing recipient")
    
    # Invalid statuses
    valid_statuses = {'PENDING', 'PROCESSING', 'DELIVERED', 'FAILED'}
    invalid_status = sum(1 for e in data if e.get('status') not in valid_statuses)
    if invalid_status:
        issues.append(f"   ⚠️  {invalid_status} entries with invalid status")
    
    if not issues:
        print("   ✅ No obvious issues detected")
    else:
        for issue in issues:
            print(issue)
    
    print("\n" + "=" * 70)
    
except json.JSONDecodeError as e:
    print(f"\n❌ JSON DECODE ERROR: {e}")
    print(f"   Position: {e.pos if hasattr(e, 'pos') else 'unknown'}")
    print(f"   Queue file may be corrupted")
    print(f"   Check message_queue/backups/ for backup files")
    sys.exit(1)
    
except PermissionError as e:
    print(f"\n❌ PERMISSION ERROR: {e}")
    print(f"   File may be locked by another process")
    print(f"   Check if queue processor is running")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

