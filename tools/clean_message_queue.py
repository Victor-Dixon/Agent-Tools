#!/usr/bin/env python3
"""
Clean Message Queue - Remove System Messages and Release Pending
================================================================

Removes system messages (SYSTEM sender or S2A stall recovery messages) 
from the queue and sets all remaining messages to PENDING status.

Author: Agent-6 (Coordination & Communication)
Date: 2025-12-13
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def is_system_message(entry):
    """Identify system messages that should be removed."""
    message = entry.get('message', {})
    
    if not isinstance(message, dict):
        return False
    
    sender = message.get('sender', '').upper()
    content = message.get('content', '')
    
    # Remove messages from SYSTEM sender
    if sender == 'SYSTEM':
        return True
    
    # Remove S2A stall recovery messages (from CAPTAIN or SYSTEM)
    if 'S2A STALL RECOVERY' in content.upper() or 'DO NOT REPLY' in content.upper():
        if '[HEADER]' in content or sender == 'SYSTEM':
            return True
    
    return False

def clean_queue(queue_file_path):
    """Clean the message queue by removing system messages and releasing pending."""
    print("=" * 70)
    print("MESSAGE QUEUE CLEANUP")
    print("=" * 70)
    print(f"\nQueue file: {queue_file_path}")
    
    if not queue_file_path.exists():
        print("❌ Queue file does not exist!")
        return
    
    # Load queue
    try:
        with open(queue_file_path, 'r', encoding='utf-8') as f:
            entries = json.load(f)
        
        if not isinstance(entries, list):
            print(f"❌ Queue file is not a JSON array! Type: {type(entries)}")
            return
        
        print(f"\nTotal entries: {len(entries)}")
        
        # Count by status
        status_counts = {}
        system_messages = []
        non_system_messages = []
        
        for entry in entries:
            status = entry.get('status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if is_system_message(entry):
                system_messages.append(entry)
            else:
                non_system_messages.append(entry)
        
        print(f"\nStatus distribution (before cleanup):")
        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count}")
        
        print(f"\nSystem messages to remove: {len(system_messages)}")
        print(f"Non-system messages to keep: {len(non_system_messages)}")
        
        # Set all non-system messages to PENDING status
        for entry in non_system_messages:
            entry['status'] = 'PENDING'
            entry['updated_at'] = datetime.now().isoformat()
        
        # Create backup
        backup_path = queue_file_path.parent / f"queue_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        print(f"\n📦 Creating backup: {backup_path.name}")
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False, default=str)
        
        # Save cleaned queue (only non-system messages)
        print(f"\n💾 Saving cleaned queue with {len(non_system_messages)} messages...")
        with open(queue_file_path, 'w', encoding='utf-8') as f:
            json.dump(non_system_messages, f, indent=2, ensure_ascii=False, default=str)
        
        # Status distribution after cleanup
        print(f"\nStatus distribution (after cleanup):")
        after_status_counts = {}
        for entry in non_system_messages:
            status = entry.get('status', 'UNKNOWN')
            after_status_counts[status] = after_status_counts.get(status, 0) + 1
        
        for status, count in sorted(after_status_counts.items()):
            print(f"  {status}: {count}")
        
        print(f"\n✅ Cleanup complete!")
        print(f"   - Removed {len(system_messages)} system messages")
        print(f"   - Kept {len(non_system_messages)} messages (all set to PENDING)")
        print(f"   - Backup saved to: {backup_path.name}")
        
        # Show sample of removed messages
        if system_messages:
            print(f"\n📋 Sample removed system messages:")
            for msg in system_messages[:5]:
                queue_id = msg.get('queue_id', 'unknown')[:20]
                sender = msg.get('message', {}).get('sender', 'unknown') if isinstance(msg.get('message'), dict) else 'unknown'
                recipient = msg.get('message', {}).get('recipient', 'unknown') if isinstance(msg.get('message'), dict) else 'unknown'
                print(f"   - ID: {queue_id}... From: {sender} To: {recipient}")
        
    except json.JSONDecodeError as e:
        print(f"❌ Queue file is corrupted (JSON decode error): {e}")
        return
    except Exception as e:
        print(f"❌ Error cleaning queue: {e}")
        import traceback
        traceback.print_exc()
        return

def main():
    """Main entry point."""
    queue_file = project_root / "message_queue" / "queue.json"
    clean_queue(queue_file)

if __name__ == "__main__":
    main()







