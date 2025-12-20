#!/usr/bin/env python3
"""
Check Stuck Messages
====================

Checks for messages stuck in PROCESSING status and optionally resets them.

Usage:
    python tools/check_stuck_messages.py [--reset]

Author: Agent-6
Date: 2025-12-13
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.message_queue_error_monitor import MessageQueueErrorMonitor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Check for stuck messages and optionally reset them."""
    parser = argparse.ArgumentParser(description='Check for stuck messages in queue')
    parser.add_argument('--reset', action='store_true', help='Reset stuck messages to PENDING')
    parser.add_argument('--all-checks', action='store_true', help='Run all monitoring checks')
    args = parser.parse_args()
    
    print("🔍 Checking for Stuck Messages")
    print("=" * 50)
    
    monitor = MessageQueueErrorMonitor()
    
    if args.all_checks:
        # Run all checks
        results = monitor.run_checks()
        
        print(f"\n📊 Monitoring Results:")
        print(f"   Timestamp: {results['timestamp']}")
        print(f"   Stuck Messages: {len(results['stuck_messages'])}")
        print(f"   Total Alerts: {len(results['alerts'])}")
        
        if results['stuck_messages']:
            print(f"\n⚠️  Stuck Messages Found:")
            for msg in results['stuck_messages']:
                severity_icon = "🚨" if msg['severity'] == 'critical' else "⚠️"
                print(f"   {severity_icon} {msg['queue_id'][:20]}...")
                print(f"      Recipient: {msg['recipient']}")
                print(f"      Stuck Duration: {msg['stuck_duration_seconds']:.1f}s")
                print(f"      Severity: {msg['severity']}")
        
        if results['alerts']:
            print(f"\n📢 Alerts:")
            for alert in results['alerts']:
                severity_icon = "🚨" if alert['severity'] == 'critical' else "⚠️" if alert['severity'] == 'warning' else "ℹ️"
                print(f"   {severity_icon} [{alert['severity'].upper()}] {alert['alert_type']}: {alert['message']}")
        
        # Reset if requested
        if args.reset and results['stuck_messages']:
            reset_count = monitor.reset_stuck_messages()
            print(f"\n✅ Reset {reset_count} stuck messages to PENDING")
        
    else:
        # Just check stuck messages
        stuck_alerts = monitor.check_stuck_messages()
        
        if not stuck_alerts:
            print("✅ No stuck messages found")
            return 0
        
        print(f"\n⚠️  Found {len(stuck_alerts)} stuck message(s):")
        for alert in stuck_alerts:
            severity_icon = "🚨" if alert.severity == 'critical' else "⚠️"
            print(f"   {severity_icon} {alert.queue_id[:20]}...")
            print(f"      Recipient: {alert.recipient}")
            print(f"      Stuck Duration: {alert.stuck_duration_seconds:.1f}s")
            print(f"      Severity: {alert.severity}")
        
        if args.reset:
            reset_count = monitor.reset_stuck_messages(stuck_alerts)
            print(f"\n✅ Reset {reset_count} stuck messages to PENDING")
        else:
            print(f"\n💡 Tip: Use --reset to automatically reset stuck messages")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())





