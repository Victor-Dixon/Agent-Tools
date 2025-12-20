#!/usr/bin/env python3
"""
🐝 CAPTAIN MESSAGE PROCESSOR - COMPREHENSIVE WORKSPACE CLEANUP
=============================================================

Processes ALL messages in Agent-4's workspace:
- Responds to messages that need responses
- Extracts insights for project state/cycle planner/swarm brain/notes
- Archives/deletes processed messages

V2 Compliance: <300 lines, single responsibility
Author: Agent-1 (Captain Support)
"""

import json
import logging
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CaptainMessageProcessor:
    """Comprehensive message processor for Captain workspace."""

    def __init__(self, project_root: Path | None = None):
        """Initialize the processor."""
        if project_root is None:
            project_root = Path(__file__).parent.parent
        self.project_root = project_root
        self.captain_workspace = project_root / "agent_workspaces" / "Agent-4"
        self.inbox = self.captain_workspace / "inbox"
        self.archive_dir = self.inbox / "archive" / datetime.now().strftime("%Y-%m-%d")
        self.notes_dir = self.captain_workspace / "notes"
        self.notes_dir.mkdir(exist_ok=True)

    def extract_insights(self, content: str, filename: str) -> dict[str, Any]:
        """Extract insights from message content."""
        insights = {
            "completions": [],
            "blockers": [],
            "tasks": [],
            "status_updates": [],
            "coordination": [],
            "patterns": [],
        }
        
        content_lower = content.lower()
        
        # Extract completions
        completion_patterns = [
            r"✅\s+(.+?)(?:\n|$)",
            r"complete[ed]?\s*:?\s*(.+?)(?:\n|$)",
            r"finished\s*:?\s*(.+?)(?:\n|$)",
        ]
        for pattern in completion_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            insights["completions"].extend([m.strip() for m in matches if m.strip()])
        
        # Extract blockers
        blocker_patterns = [
            r"🚨\s+(.+?)(?:\n|$)",
            r"blocker[ed]?\s*:?\s*(.+?)(?:\n|$)",
            r"blocked\s*:?\s*(.+?)(?:\n|$)",
        ]
        for pattern in blocker_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            insights["blockers"].extend([m.strip() for m in matches if m.strip()])
        
        # Extract tasks
        task_patterns = [
            r"task[s]?\s*:?\s*(.+?)(?:\n|$)",
            r"next\s+action[s]?\s*:?\s*(.+?)(?:\n|$)",
        ]
        for pattern in task_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            insights["tasks"].extend([m.strip() for m in matches if m.strip()])
        
        # Extract status updates
        if any(word in content_lower for word in ["status", "update", "progress", "report"]):
            insights["status_updates"].append(f"Status update from {filename}")
        
        # Extract coordination
        if any(word in content_lower for word in ["coordinate", "assign", "task", "mission"]):
            insights["coordination"].append(f"Coordination item from {filename}")
        
        return insights

    def update_notes(self, insights: dict[str, Any], filename: str):
        """Update notes directory with extracted insights."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notes_file = self.notes_dir / f"{datetime.now().strftime('%Y-%m-%d')}_INSIGHTS.md"
        
        # Read existing notes or create new
        if notes_file.exists():
            notes_content = notes_file.read_text(encoding="utf-8")
        else:
            notes_content = f"# 📝 CAPTAIN INSIGHTS - {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        # Append new insights
        notes_content += f"\n## 📨 {filename} - {timestamp}\n\n"
        
        if insights["completions"]:
            notes_content += "### ✅ Completions\n"
            for comp in insights["completions"][:5]:  # Limit to 5
                notes_content += f"- {comp}\n"
            notes_content += "\n"
        
        if insights["blockers"]:
            notes_content += "### 🚨 Blockers\n"
            for blocker in insights["blockers"][:5]:
                notes_content += f"- {blocker}\n"
            notes_content += "\n"
        
        if insights["tasks"]:
            notes_content += "### 📋 Tasks\n"
            for task in insights["tasks"][:5]:
                notes_content += f"- {task}\n"
            notes_content += "\n"
        
        notes_file.write_text(notes_content, encoding="utf-8")
        logger.info(f"✅ Updated notes: {notes_file.name}")

    def needs_response(self, content: str, filename: str) -> bool:
        """Check if message needs a response."""
        content_lower = content.lower()
        
        # Check for question patterns
        if "?" in content:
            return True
        
        # Check for request patterns
        if any(word in content_lower for word in ["request", "help", "need", "please", "can you"]):
            return True
        
        # Check for status updates that need acknowledgment
        if any(word in content_lower for word in ["status", "update", "complete", "finished"]):
            # Only if from an agent (not system)
            if "AGENT_" in filename.upper() or filename.startswith("C2A_"):
                return True
        
        return False

    def generate_response(self, content: str, filename: str) -> str | None:
        """Generate response if needed."""
        if not self.needs_response(content, filename):
            return None
        
        # Extract sender
        sender_match = re.search(r"\*\*From\*\*:\s*(.+)", content)
        sender = sender_match.group(1).strip() if sender_match else "Unknown"
        
        # Generate acknowledgment
        return f"""✅ CAPTAIN ACKNOWLEDGMENT: {sender} Message Processed

**Status**: Message reviewed and processed
**Action**: Insights extracted and added to notes

**NEXT STEPS**:
- Continue excellent work
- Update status.json regularly
- Post devlog when complete

**WE. ARE. SWARM. AUTONOMOUS. POWERFUL. 🐝⚡🔥🚀**"""

    def send_response(self, recipient: str, response: str) -> bool:
        """Send response via messaging system."""
        try:
            sys.path.insert(0, str(self.project_root))
            
            from src.core.messaging_core import (
                UnifiedMessagePriority,
                UnifiedMessageTag,
                UnifiedMessageType,
                send_message,
            )
            
            success = send_message(
                content=response,
                sender="Captain Agent-4",
                recipient=recipient,
                message_type=UnifiedMessageType.TEXT,
                priority=UnifiedMessagePriority.REGULAR,
                tags=[UnifiedMessageTag.CAPTAIN],
            )
            
            return success
        except Exception as e:
            logger.error(f"❌ Error sending response: {e}")
            return False

    def archive_message(self, message_path: Path) -> bool:
        """Archive processed message."""
        try:
            if not self.archive_dir.exists():
                self.archive_dir.mkdir(parents=True, exist_ok=True)
            
            archive_path = self.archive_dir / message_path.name
            if archive_path.exists():
                # Add timestamp if duplicate
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_path = self.archive_dir / f"{message_path.stem}_{timestamp}{message_path.suffix}"
            
            message_path.rename(archive_path)
            logger.info(f"✅ Archived: {message_path.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error archiving {message_path.name}: {e}")
            return False

    def process_all_messages(self, auto_send: bool = True, auto_archive: bool = True, include_archived: bool = True) -> dict[str, Any]:
        """Process all messages in workspace."""
        results = {
            "total": 0,
            "processed": 0,
            "responded": 0,
            "archived": 0,
            "insights_extracted": 0,
            "errors": [],
        }
        
        # Process inbox messages
        if self.inbox.exists():
            for msg_file in self.inbox.glob("*.md"):
                if msg_file.name == "archive" or msg_file.is_dir():
                    continue
                
                results["total"] += 1
                try:
                    content = msg_file.read_text(encoding="utf-8")
                    
                    # Extract insights
                    insights = self.extract_insights(content, msg_file.name)
                    if insights["completions"] or insights["blockers"] or insights["tasks"]:
                        results["insights_extracted"] += 1
                    
                    # Update notes
                    self.update_notes(insights, msg_file.name)
                    
                    # Generate and send response if needed
                    response = self.generate_response(content, msg_file.name)
                    if response:
                        # Extract recipient
                        sender_match = re.search(r"\*\*From\*\*:\s*(.+)", content)
                        if sender_match:
                            sender = sender_match.group(1).strip()
                            if "Agent-" in sender:
                                recipient = sender.split()[0] if " " in sender else sender
                                if auto_send:
                                    if self.send_response(recipient, response):
                                        results["responded"] += 1
                    
                    # Archive message
                    if auto_archive:
                        if self.archive_message(msg_file):
                            results["archived"] += 1
                    
                    results["processed"] += 1
                except Exception as e:
                    logger.error(f"❌ Error processing {msg_file.name}: {e}")
                    results["errors"].append({"file": msg_file.name, "error": str(e)})
        
        # Process archived messages (extract insights only, no responses)
        if include_archived:
            archive_path = self.inbox / "archive"
            if archive_path.exists() and archive_path.is_dir():
                for msg_file in archive_path.rglob("*.md"):
                    results["total"] += 1
                    try:
                        content = msg_file.read_text(encoding="utf-8")
                        
                        # Extract insights only (already archived)
                        insights = self.extract_insights(content, msg_file.name)
                        if insights["completions"] or insights["blockers"] or insights["tasks"]:
                            results["insights_extracted"] += 1
                            # Update notes with archived message insights
                            self.update_notes(insights, f"[ARCHIVED] {msg_file.name}")
                        
                        results["processed"] += 1
                    except Exception as e:
                        logger.debug(f"Note: Could not process archived {msg_file.name}: {e}")
        
        return results

    def generate_report(self, results: dict[str, Any]) -> str:
        """Generate processing report."""
        report = f"""# 📊 CAPTAIN MESSAGE PROCESSING REPORT

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
- **Total Messages**: {results['total']}
- **Processed**: {results['processed']}
- **Responses Sent**: {results['responded']}
- **Archived**: {results['archived']}
- **Errors**: {len(results['errors'])}

## Notes Updated
Insights extracted and added to: `agent_workspaces/Agent-4/notes/`

"""
        if results["errors"]:
            report += "## Errors\n"
            for error in results["errors"][:10]:  # Limit to 10
                report += f"- **{error.get('file', 'Unknown')}**: {error.get('error', 'Unknown error')}\n"
        
        return report


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Captain Message Processor")
    parser.add_argument("--process", action="store_true", help="Process all messages")
    parser.add_argument("--auto-send", action="store_true", default=True, help="Automatically send responses")
    parser.add_argument("--auto-archive", action="store_true", default=True, help="Automatically archive processed messages")
    parser.add_argument("--report", action="store_true", help="Generate summary report")
    
    args = parser.parse_args()
    
    processor = CaptainMessageProcessor()
    
    if args.process:
        logger.info("🚀 Starting comprehensive message processing...")
        results = processor.process_all_messages(
            auto_send=args.auto_send,
            auto_archive=args.auto_archive
        )
        
        if args.report:
            report = processor.generate_report(results)
            print(report)
            
            # Save report
            report_path = processor.captain_workspace / "message_processing_report.md"
            report_path.write_text(report, encoding="utf-8")
            print(f"\n✅ Report saved to: {report_path}")
        else:
            print(f"\n📊 Processed {results['processed']} messages")
            print(f"✅ Sent {results['responded']} responses")
            print(f"📦 Archived {results['archived']} messages")
            if results['errors']:
                print(f"❌ {len(results['errors'])} errors")


if __name__ == "__main__":
    main()

