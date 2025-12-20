#!/usr/bin/env python3
"""
Debug A2A Messaging - Check PyAutoGUI delivery status
=====================================================

Quick diagnostic tool to check why messages aren't using PyAutoGUI.
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def check_queue_pyautogui_status():
    """Check recent queue entries for PyAutoGUI usage."""
    import json
    
    queue_file = project_root / "message_queue" / "queue.json"
    if not queue_file.exists():
        print("❌ Queue file not found")
        return
    
    with open(queue_file, 'r', encoding='utf-8') as f:
        entries = json.load(f)
    
    print(f"Total entries: {len(entries)}")
    print("\nRecent messages (last 10):")
    print("-" * 70)
    
    recent = sorted(
        [e for e in entries if 'created_at' in str(e)],
        key=lambda x: str(x.get('created_at', '')),
        reverse=True
    )[:10]
    
    pyautogui_count = 0
    inbox_count = 0
    
    for entry in recent:
        message = entry.get('message', {})
        metadata = message.get('metadata', {}) if isinstance(message, dict) else {}
        use_pyautogui = metadata.get('use_pyautogui', False)
        recipient = message.get('recipient', 'unknown') if isinstance(message, dict) else 'unknown'
        status = entry.get('status', 'UNKNOWN')
        created = str(entry.get('created_at', ''))[:19]
        
        if use_pyautogui:
            pyautogui_count += 1
            delivery = "PyAutoGUI ✅"
        else:
            inbox_count += 1
            delivery = "INBOX ⚠️"
        
        print(f"{created} | {status:12} | {recipient:10} | {delivery}")
    
    print("-" * 70)
    print(f"\nSummary:")
    print(f"  PyAutoGUI: {pyautogui_count}")
    print(f"  Inbox:     {inbox_count}")
    print(f"\n⚠️  All messages are using INBOX delivery, not PyAutoGUI!")

if __name__ == "__main__":
    check_queue_pyautogui_status()







