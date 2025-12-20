#!/usr/bin/env python3
"""
<!-- SSOT Domain: infrastructure -->
Messaging Delivery Diagnostic Tool
===================================

Diagnoses issues with message delivery system:
- Checks if messages are actually written to inboxes
- Verifies message queue status
- Tests message delivery mechanism
- Identifies delivery failures

Author: Agent-4 (Captain)
Date: 2025-12-12
Priority: HIGH - Debugging messaging system
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessagingDiagnostic:
    """Diagnostic tool for messaging delivery issues."""
    
    def __init__(self, workspace_root: Path = None):
        self.workspace_root = workspace_root or Path(".")
        self.agent_workspaces = self.workspace_root / "agent_workspaces"
        self.message_queue_file = Path("data") / "message_queue.json"
        self.message_history_file = Path("data") / "message_history.json"
    
    def check_recent_messages(self, hours: int = 2) -> Dict[str, List]:
        """Check for recent messages in inboxes."""
        results = {}
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for agent_dir in self.agent_workspaces.iterdir():
            if not agent_dir.is_dir() or not agent_dir.name.startswith("Agent-"):
                continue
            
            agent_id = agent_dir.name
            inbox_dir = agent_dir / "inbox"
            
            if not inbox_dir.exists():
                results[agent_id] = {
                    "status": "no_inbox",
                    "messages": []
                }
                continue
            
            recent_messages = []
            for msg_file in inbox_dir.glob("*.md"):
                try:
                    mtime = datetime.fromtimestamp(msg_file.stat().st_mtime)
                    if mtime >= cutoff_time:
                        # Try to read message ID from file
                        try:
                            content = msg_file.read_text(encoding='utf-8')[:500]
                            msg_id_match = None
                            if "Message ID:" in content:
                                for line in content.split('\n'):
                                    if "Message ID:" in line:
                                        msg_id_match = line.split("Message ID:")[-1].strip()
                                        break
                        except Exception:
                            msg_id_match = None
                        
                        recent_messages.append({
                            "file": msg_file.name,
                            "modified": mtime.isoformat(),
                            "message_id": msg_id_match
                        })
                except Exception as e:
                    logger.warning(f"Error checking {msg_file}: {e}")
            
            results[agent_id] = {
                "status": "ok",
                "message_count": len(recent_messages),
                "messages": recent_messages
            }
        
        return results
    
    def check_message_queue(self) -> Dict:
        """Check message queue status."""
        results = {
            "queue_file_exists": self.message_queue_file.exists(),
            "entries": []
        }
        
        if self.message_queue_file.exists():
            try:
                with open(self.message_queue_file, 'r', encoding='utf-8') as f:
                    queue_data = json.load(f)
                
                entries = queue_data.get("messages", []) or queue_data.get("entries", [])
                results["entry_count"] = len(entries)
                
                # Check recent entries
                cutoff_time = datetime.now() - timedelta(hours=2)
                for entry in entries[-20:]:  # Last 20 entries
                    timestamp_str = entry.get("timestamp") or entry.get("created_at")
                    if timestamp_str:
                        try:
                            if isinstance(timestamp_str, str):
                                entry_time = datetime.fromisoformat(
                                    timestamp_str.replace("Z", "+00:00")
                                ).replace(tzinfo=None)
                            else:
                                entry_time = datetime.fromtimestamp(timestamp_str)
                            
                            if entry_time >= cutoff_time:
                                results["entries"].append({
                                    "message_id": entry.get("message_id") or entry.get("id"),
                                    "recipient": entry.get("recipient"),
                                    "status": entry.get("status"),
                                    "timestamp": entry_time.isoformat()
                                })
                        except Exception:
                            pass
            except Exception as e:
                results["error"] = str(e)
        
        return results
    
    def check_message_history(self) -> Dict:
        """Check message history."""
        results = {
            "history_file_exists": self.message_history_file.exists(),
            "recent_messages": []
        }
        
        if self.message_history_file.exists():
            try:
                with open(self.message_history_file, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                
                messages = history_data.get("messages", [])
                cutoff_time = datetime.now() - timedelta(hours=2)
                
                for msg in messages[-20:]:  # Last 20 messages
                    timestamp_str = msg.get("timestamp")
                    if timestamp_str:
                        try:
                            msg_time = datetime.fromisoformat(
                                timestamp_str.replace("Z", "+00:00")
                            ).replace(tzinfo=None)
                            
                            if msg_time >= cutoff_time:
                                results["recent_messages"].append({
                                    "message_id": msg.get("message_id"),
                                    "sender": msg.get("sender"),
                                    "recipient": msg.get("recipient"),
                                    "timestamp": msg_time.isoformat()
                                })
                        except Exception:
                            pass
            except Exception as e:
                results["error"] = str(e)
        
        return results
    
    def test_message_delivery(self, test_agent: str = "Agent-2") -> Dict:
        """Test message delivery to verify system works."""
        try:
            from src.core.messaging_core import send_message, UnifiedMessageType, UnifiedMessagePriority
            
            test_message = f"TEST MESSAGE - Diagnostic check at {datetime.now().isoformat()}"
            test_id = f"test_{datetime.now().timestamp()}"
            
            result = send_message(
                recipient=test_agent,
                message=test_message,
                sender="Agent-4",
                message_type=UnifiedMessageType.TEXT,
                priority=UnifiedMessagePriority.NORMAL,
                message_id=test_id
            )
            
            # Check if file was created
            inbox_dir = self.agent_workspaces / test_agent / "inbox"
            test_file = None
            if inbox_dir.exists():
                for msg_file in inbox_dir.glob("*.md"):
                    if test_id in msg_file.read_text(encoding='utf-8'):
                        test_file = msg_file.name
                        break
            
            return {
                "success": result.get("success", False),
                "error": result.get("error"),
                "test_file_found": test_file is not None,
                "test_file": test_file,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "test_file_found": False
            }
    
    def generate_diagnostic_report(self) -> str:
        """Generate comprehensive diagnostic report."""
        report = []
        report.append("=" * 80)
        report.append("MESSAGING DELIVERY DIAGNOSTIC REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().isoformat()}\n")
        
        # Check recent messages
        report.append("\n📬 RECENT INBOX MESSAGES (Last 2 Hours):")
        report.append("-" * 80)
        inbox_status = self.check_recent_messages(hours=2)
        for agent_id, status in inbox_status.items():
            report.append(f"\n{agent_id}:")
            report.append(f"  Status: {status.get('status')}")
            report.append(f"  Recent messages: {status.get('message_count', 0)}")
            if status.get('messages'):
                for msg in status['messages'][:3]:  # Show first 3
                    report.append(f"    - {msg['file']} ({msg['modified']})")
        
        # Check message queue
        report.append("\n\n📋 MESSAGE QUEUE STATUS:")
        report.append("-" * 80)
        queue_status = self.check_message_queue()
        report.append(f"Queue file exists: {queue_status.get('queue_file_exists')}")
        report.append(f"Recent entries: {len(queue_status.get('entries', []))}")
        if queue_status.get('entries'):
            for entry in queue_status['entries'][:5]:
                report.append(f"  - {entry.get('recipient')}: {entry.get('status')} ({entry.get('timestamp')})")
        
        # Check message history
        report.append("\n\n📜 MESSAGE HISTORY:")
        report.append("-" * 80)
        history_status = self.check_message_history()
        report.append(f"History file exists: {history_status.get('history_file_exists')}")
        report.append(f"Recent messages: {len(history_status.get('recent_messages', []))}")
        
        # Test delivery
        report.append("\n\n🧪 MESSAGE DELIVERY TEST:")
        report.append("-" * 80)
        test_result = self.test_message_delivery("Agent-2")
        report.append(f"Test success: {test_result.get('success')}")
        report.append(f"Test file found: {test_result.get('test_file_found')}")
        if test_result.get('error'):
            report.append(f"Error: {test_result.get('error')}")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Diagnose messaging delivery issues")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--test", action="store_true", help="Run delivery test")
    
    args = parser.parse_args()
    
    diagnostic = MessagingDiagnostic()
    report = diagnostic.generate_diagnostic_report()
    
    if args.test:
        print("\n🧪 Running delivery test...")
        test_result = diagnostic.test_message_delivery()
        print(f"Success: {test_result.get('success')}")
        print(f"File found: {test_result.get('test_file_found')}")
        if test_result.get('error'):
            print(f"Error: {test_result.get('error')}")
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()



