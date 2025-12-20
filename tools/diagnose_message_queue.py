#!/usr/bin/env python3
"""
Message Queue Diagnostic Tool
=============================

Diagnoses issues with the message queue system, including:
- Silent failures in queue processing
- Stuck messages
- File locking issues
- Corrupted queue files

Author: Agent-2 (Architecture & Design)
Date: 2025-12-13
"""

import json
import sys
from pathlib import Path
from collections import Counter
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def analyze_queue_file():
    """Analyze the queue.json file for issues."""
    queue_file = project_root / "message_queue" / "queue.json"
    
    print("=" * 70)
    print("MESSAGE QUEUE DIAGNOSTIC REPORT")
    print("=" * 70)
    print(f"\nQueue file: {queue_file}")
    print(f"Exists: {queue_file.exists()}")
    
    if not queue_file.exists():
        print("❌ Queue file does not exist!")
        return
    
    print(f"Size: {queue_file.stat().st_size:,} bytes")
    
    # Check for lock files
    lock_files = [
        "delivered.json.lock",
        "failed.json.lock",
        "pending.json.lock",
        "processing.json.lock"
    ]
    queue_dir = queue_file.parent
    print(f"\nLock files:")
    for lock_file in lock_files:
        lock_path = queue_dir / lock_file
        if lock_path.exists():
            print(f"  ⚠️  {lock_file} exists (may indicate stuck process)")
        else:
            print(f"  ✅ {lock_file} not present")
    
    # Load and analyze entries
    try:
        with open(queue_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print(f"\n❌ Queue file is not a JSON array! Type: {type(data)}")
            return
        
        print(f"\nTotal entries: {len(data)}")
        
        # Status distribution
        statuses = Counter(e.get('status', 'UNKNOWN') for e in data)
        print(f"\nStatus distribution:")
        for status, count in statuses.most_common():
            print(f"  {status}: {count}")
        
        # Find stuck messages (PROCESSING for > 5 minutes)
        now = datetime.now()
        stuck_messages = []
        for entry in data:
            if entry.get('status') == 'PROCESSING':
                updated_at = entry.get('updated_at')
                if updated_at:
                    try:
                        if isinstance(updated_at, str):
                            updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                        else:
                            updated = datetime.fromisoformat(str(updated_at))
                        
                        age_seconds = (now - updated.replace(tzinfo=None)).total_seconds()
                        if age_seconds > 300:  # 5 minutes
                            stuck_messages.append({
                                'queue_id': entry.get('queue_id', 'unknown'),
                                'age_seconds': age_seconds,
                                'recipient': entry.get('message', {}).get('recipient', 'unknown') if isinstance(entry.get('message'), dict) else 'unknown'
                            })
                    except Exception as e:
                        stuck_messages.append({
                            'queue_id': entry.get('queue_id', 'unknown'),
                            'age_seconds': 'unknown',
                            'error': str(e)
                        })
        
        if stuck_messages:
            print(f"\n⚠️  STUCK MESSAGES (PROCESSING > 5 minutes): {len(stuck_messages)}")
            for msg in stuck_messages[:10]:  # Show first 10
                print(f"  - ID: {msg['queue_id'][:20]}... Recipient: {msg.get('recipient', 'unknown')} Age: {msg.get('age_seconds', 'unknown')}s")
        else:
            print(f"\n✅ No stuck messages found")
        
        # Find failed messages
        failed = [e for e in data if e.get('status') == 'FAILED']
        if failed:
            print(f"\n⚠️  FAILED MESSAGES: {len(failed)}")
            error_reasons = Counter(e.get('metadata', {}).get('last_error', 'unknown') for e in failed)
            print("  Error reasons:")
            for reason, count in error_reasons.most_common(10):
                print(f"    {reason}: {count}")
        
        # Check for entries with missing required fields
        invalid_entries = []
        for entry in data:
            issues = []
            if not entry.get('queue_id'):
                issues.append('missing queue_id')
            if not entry.get('message'):
                issues.append('missing message')
            elif isinstance(entry.get('message'), dict):
                if not entry['message'].get('recipient'):
                    issues.append('missing recipient')
                if not entry['message'].get('content'):
                    issues.append('missing content')
            
            if issues:
                invalid_entries.append({
                    'queue_id': entry.get('queue_id', 'unknown'),
                    'issues': issues
                })
        
        if invalid_entries:
            print(f"\n⚠️  INVALID ENTRIES: {len(invalid_entries)}")
            for entry in invalid_entries[:10]:
                print(f"  - ID: {entry['queue_id'][:20]}... Issues: {', '.join(entry['issues'])}")
        else:
            print(f"\n✅ All entries have required fields")
        
        # Recent entries
        recent = sorted(
            [e for e in data if 'created_at' in e],
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )[:5]
        
        print(f"\nMost recent 5 entries:")
        for e in recent:
            print(f"  - ID: {e.get('queue_id', 'unknown')[:20]}... Status: {e.get('status')} Created: {e.get('created_at', 'unknown')[:19]}")
        
    except json.JSONDecodeError as e:
        print(f"\n❌ Queue file is corrupted (JSON decode error): {e}")
        print(f"   Position: {e.pos if hasattr(e, 'pos') else 'unknown'}")
    except Exception as e:
        print(f"\n❌ Error analyzing queue file: {e}")
        import traceback
        traceback.print_exc()

def check_queue_processor_logs():
    """Check queue processor logs for errors."""
    log_file = project_root / "logs" / "queue_processor.log"
    
    print("\n" + "=" * 70)
    print("QUEUE PROCESSOR LOG ANALYSIS")
    print("=" * 70)
    print(f"\nLog file: {log_file}")
    print(f"Exists: {log_file.exists()}")
    
    if not log_file.exists():
        print("⚠️  Log file does not exist - queue processor may not be running")
        return
    
    print(f"Size: {log_file.stat().st_size:,} bytes")
    
    # Read last 50 lines
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"\nTotal log lines: {len(lines)}")
        print(f"\nLast 20 log lines:")
        for line in lines[-20:]:
            print(f"  {line.rstrip()}")
        
        # Count errors
        error_count = sum(1 for line in lines if 'ERROR' in line or '❌' in line)
        warning_count = sum(1 for line in lines if 'WARNING' in line or '⚠️' in line)
        
        print(f"\nError summary:")
        print(f"  Errors: {error_count}")
        print(f"  Warnings: {warning_count}")
        
        # Find specific error patterns
        file_not_found_errors = [line for line in lines if 'No such file or directory' in line or 'FileNotFoundError' in line]
        if file_not_found_errors:
            print(f"\n⚠️  File not found errors: {len(file_not_found_errors)}")
            for error in file_not_found_errors[-5:]:
                print(f"  {error.strip()}")
        
        permission_errors = [line for line in lines if 'PermissionError' in line or 'File locked' in line]
        if permission_errors:
            print(f"\n⚠️  Permission/file lock errors: {len(permission_errors)}")
            for error in permission_errors[-5:]:
                print(f"  {error.strip()}")
        
    except Exception as e:
        print(f"\n❌ Error reading log file: {e}")

def main():
    """Run diagnostic checks."""
    analyze_queue_file()
    check_queue_processor_logs()
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print("""
1. If stuck messages found:
   - Restart the queue processor: python tools/start_message_queue_processor.py
   - Reset stuck messages to PENDING status

2. If file locking errors:
   - Check for multiple queue processor instances running
   - Ensure message_queue directory has proper permissions

3. If queue file corruption:
   - Backup corrupted file from message_queue/backups/
   - Queue will auto-recover on next save

4. If queue processor not running:
   - Start it: python tools/start_message_queue_processor.py
   - Check logs/logs/queue_processor.log for errors
    """)

if __name__ == "__main__":
    main()

