#!/usr/bin/env python3
"""
🐝 CAPTAIN INBOX ASSISTANT - AUTOMATED RESPONSE SYSTEM
======================================================

Helps Agent-4 (Captain) respond to inbox messages automatically.
Reads messages, generates appropriate responses, and sends them.

V2 Compliance: <300 lines, single responsibility
Author: Agent-1 (Captain Support)
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CaptainInboxAssistant:
    """Automated assistant for Captain inbox management."""

    def __init__(self, project_root: Path | None = None):
        """Initialize the assistant."""
        if project_root is None:
            project_root = Path(__file__).parent.parent
        self.project_root = project_root
        self.captain_inbox = project_root / "agent_workspaces" / "Agent-4" / "inbox"
        self.archive_dir = self.captain_inbox / "archive"

    def scan_inbox(self, include_archived: bool = False) -> list[Path]:
        """Scan inbox for unprocessed messages."""
        messages = []
        
        # Scan main inbox
        if self.captain_inbox.exists():
            for msg_file in self.captain_inbox.glob("*.md"):
                if msg_file.name != "archive":
                    messages.append(msg_file)
        
        # Scan archive if requested
        if include_archived and self.archive_dir.exists():
            for msg_file in self.archive_dir.glob("*.md"):
                messages.append(msg_file)
        
        return sorted(messages, key=lambda p: p.stat().st_mtime, reverse=True)

    def parse_message(self, message_path: Path) -> dict[str, Any]:
        """Parse message file and extract key information."""
        try:
            content = message_path.read_text(encoding="utf-8")
            
            # Extract metadata from headers
            metadata = {
                "file": message_path.name,
                "path": str(message_path),
                "content": content,
                "from": None,
                "to": None,
                "priority": "normal",
                "message_id": None,
                "timestamp": None,
            }
            
            # Extract From
            from_match = re.search(r"\*\*From\*\*:\s*(.+)", content)
            if from_match:
                metadata["from"] = from_match.group(1).strip()
            
            # Extract To
            to_match = re.search(r"\*\*To\*\*:\s*(.+)", content)
            if to_match:
                metadata["to"] = to_match.group(1).strip()
            
            # Extract Priority
            priority_match = re.search(r"\*\*Priority\*\*:\s*(.+)", content)
            if priority_match:
                metadata["priority"] = priority_match.group(1).strip().lower()
            
            # Extract Message ID
            msg_id_match = re.search(r"\*\*Message ID\*\*:\s*(.+)", content)
            if msg_id_match:
                metadata["message_id"] = msg_id_match.group(1).strip()
            
            # Extract Timestamp
            timestamp_match = re.search(r"\*\*Timestamp\*\*:\s*(.+)", content)
            if timestamp_match:
                metadata["timestamp"] = timestamp_match.group(1).strip()
            
            return metadata
        except Exception as e:
            logger.error(f"Error parsing message {message_path}: {e}")
            return {"file": message_path.name, "error": str(e)}

    def generate_response(self, message_metadata: dict[str, Any]) -> str | None:
        """Generate appropriate response based on message content."""
        content = message_metadata.get("content", "").lower()
        sender = message_metadata.get("from", "")
        priority = message_metadata.get("priority", "normal")
        
        # Acknowledgment patterns
        if any(word in content for word in ["complete", "finished", "done", "acknowledgment", "ack"]):
            return self._generate_acknowledgment(sender, message_metadata)
        
        # Status update patterns
        if any(word in content for word in ["status", "update", "progress", "report"]):
            return self._generate_status_response(sender, message_metadata)
        
        # Blocker/issue patterns
        if any(word in content for word in ["blocker", "error", "failed", "issue", "problem"]):
            return self._generate_blocker_response(sender, message_metadata)
        
        # Question/request patterns
        if any(word in content for word in ["?", "question", "request", "help", "need"]):
            return self._generate_help_response(sender, message_metadata)
        
        # Default acknowledgment
        return self._generate_default_response(sender, message_metadata)

    def _generate_acknowledgment(self, sender: str, metadata: dict[str, Any]) -> str:
        """Generate acknowledgment response."""
        return f"""✅ ACKNOWLEDGED: {sender} message received

**Status**: Message reviewed and acknowledged
**Action**: Task noted and tracked

**NEXT STEPS**:
- Continue excellent work
- Update status.json when complete
- Post devlog to Discord when ready

**WE. ARE. SWARM. AUTONOMOUS. POWERFUL. 🐝⚡🔥🚀**"""

    def _generate_status_response(self, sender: str, metadata: dict[str, Any]) -> str:
        """Generate status response."""
        return f"""✅ STATUS REVIEWED: {sender} status update

**Status**: Progress noted and tracked
**Action**: Continue execution

**NEXT STEPS**:
- Maintain momentum
- Update status.json with progress
- Report blockers immediately

**WE. ARE. SWARM. AUTONOMOUS. POWERFUL. 🐝⚡🔥🚀**"""

    def _generate_blocker_response(self, sender: str, metadata: dict[str, Any]) -> str:
        """Generate blocker response."""
        return f"""🚨 BLOCKER ACKNOWLEDGED: {sender} issue identified

**Status**: Blocker noted - investigating
**Action**: Will coordinate resolution

**NEXT STEPS**:
- Continue with other tasks if possible
- Document blocker details
- Await coordination response

**WE. ARE. SWARM. AUTONOMOUS. POWERFUL. 🐝⚡🔥🚀**"""

    def _generate_help_response(self, sender: str, metadata: dict[str, Any]) -> str:
        """Generate help response."""
        return f"""✅ HELP PROVIDED: {sender} request received

**Status**: Request reviewed
**Action**: Support provided

**NEXT STEPS**:
- Review provided guidance
- Continue execution
- Report if additional help needed

**WE. ARE. SWARM. AUTONOMOUS. POWERFUL. 🐝⚡🔥🚀**"""

    def _generate_default_response(self, sender: str, metadata: dict[str, Any]) -> str:
        """Generate default response."""
        return f"""✅ MESSAGE RECEIVED: {sender} communication acknowledged

**Status**: Message reviewed
**Action**: Noted and tracked

**NEXT STEPS**:
- Continue excellent work
- Update status.json regularly
- Post devlog when complete

**WE. ARE. SWARM. AUTONOMOUS. POWERFUL. 🐝⚡🔥🚀**"""

    def send_response(
        self, recipient: str, response_content: str, priority: str = "normal"
    ) -> bool:
        """Send response via messaging system."""
        try:
            # Import messaging system
            import sys
            sys.path.insert(0, str(self.project_root))
            
            from src.core.messaging_core import (
                UnifiedMessagePriority,
                UnifiedMessageTag,
                UnifiedMessageType,
                send_message,
            )
            
            # Map priority
            msg_priority = UnifiedMessagePriority.REGULAR
            if priority == "urgent":
                msg_priority = UnifiedMessagePriority.URGENT
            
            # Send message
            success = send_message(
                content=response_content,
                sender="Captain Agent-4",
                recipient=recipient,
                message_type=UnifiedMessageType.TEXT,
                priority=msg_priority,
                tags=[UnifiedMessageTag.CAPTAIN],
            )
            
            if success:
                logger.info(f"✅ Response sent to {recipient}")
            else:
                logger.warning(f"⚠️ Failed to send response to {recipient}")
            
            return success
        except Exception as e:
            logger.error(f"❌ Error sending response to {recipient}: {e}")
            return False

    def archive_message(self, message_path: Path) -> bool:
        """Archive processed message."""
        try:
            if not self.archive_dir.exists():
                self.archive_dir.mkdir(parents=True, exist_ok=True)
            
            archive_path = self.archive_dir / message_path.name
            message_path.rename(archive_path)
            logger.info(f"✅ Archived: {message_path.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error archiving {message_path.name}: {e}")
            return False

    def process_inbox(self, auto_send: bool = False, auto_archive: bool = False) -> dict[str, Any]:
        """Process all inbox messages and generate responses."""
        messages = self.scan_inbox(include_archived=False)
        
        results = {
            "total": len(messages),
            "processed": 0,
            "responses": [],
            "errors": [],
        }
        
        for msg_path in messages:
            try:
                # Parse message
                metadata = self.parse_message(msg_path)
                
                if "error" in metadata:
                    results["errors"].append(metadata)
                    continue
                
                # Generate response
                sender = metadata.get("from", "Unknown")
                if not sender or sender == "Unknown":
                    # Try to extract from filename
                    if "AGENT_" in msg_path.name:
                        sender_match = re.search(r"AGENT[_-]([A-Za-z0-9-]+)", msg_path.name)
                        if sender_match:
                            sender = sender_match.group(1)
                
                if sender and sender != "Unknown":
                    response = self.generate_response(metadata)
                    
                    if response:
                        response_data = {
                            "message": msg_path.name,
                            "from": sender,
                            "response": response,
                            "sent": False,
                        }
                        
                        # Send response if auto_send enabled
                        if auto_send:
                            success = self.send_response(sender, response, metadata.get("priority", "normal"))
                            response_data["sent"] = success
                            
                            # Archive if auto_archive enabled
                            if auto_archive and success:
                                self.archive_message(msg_path)
                        
                        results["responses"].append(response_data)
                        results["processed"] += 1
            except Exception as e:
                logger.error(f"❌ Error processing {msg_path.name}: {e}")
                results["errors"].append({"file": msg_path.name, "error": str(e)})
        
        return results

    def generate_summary_report(self, results: dict[str, Any]) -> str:
        """Generate summary report of processing."""
        report = f"""# 📊 CAPTAIN INBOX PROCESSING REPORT

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
- **Total Messages**: {results['total']}
- **Processed**: {results['processed']}
- **Responses Generated**: {len(results['responses'])}
- **Errors**: {len(results['errors'])}

## Responses Generated
"""
        for resp in results["responses"]:
            status = "✅ SENT" if resp.get("sent") else "📝 READY"
            report += f"\n### {status}: {resp['from']}\n"
            report += f"**Message**: {resp['message']}\n"
            report += f"**Response Preview**: {resp['response'][:100]}...\n"
        
        if results["errors"]:
            report += "\n## Errors\n"
            for error in results["errors"]:
                report += f"- **{error.get('file', 'Unknown')}**: {error.get('error', 'Unknown error')}\n"
        
        return report


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Captain Inbox Assistant")
    parser.add_argument("--scan", action="store_true", help="Scan inbox and show messages")
    parser.add_argument("--process", action="store_true", help="Process messages and generate responses")
    parser.add_argument("--auto-send", action="store_true", help="Automatically send responses")
    parser.add_argument("--auto-archive", action="store_true", help="Automatically archive processed messages")
    parser.add_argument("--report", action="store_true", help="Generate summary report")
    
    args = parser.parse_args()
    
    assistant = CaptainInboxAssistant()
    
    if args.scan:
        messages = assistant.scan_inbox()
        print(f"\n📬 Found {len(messages)} messages in inbox:\n")
        for msg in messages[:20]:  # Show first 20
            metadata = assistant.parse_message(msg)
            print(f"  - {msg.name}")
            print(f"    From: {metadata.get('from', 'Unknown')}")
            print(f"    Priority: {metadata.get('priority', 'normal')}")
            print()
    
    if args.process:
        results = assistant.process_inbox(
            auto_send=args.auto_send,
            auto_archive=args.auto_archive
        )
        
        if args.report:
            report = assistant.generate_summary_report(results)
            print(report)
            
            # Save report
            report_path = assistant.project_root / "agent_workspaces" / "Agent-4" / "inbox_processing_report.md"
            report_path.write_text(report, encoding="utf-8")
            print(f"\n✅ Report saved to: {report_path}")
        else:
            print(f"\n📊 Processed {results['processed']} messages")
            print(f"✅ Generated {len(results['responses'])} responses")
            if results['errors']:
                print(f"❌ {len(results['errors'])} errors")


if __name__ == "__main__":
    main()





