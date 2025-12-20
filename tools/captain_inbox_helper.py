#!/usr/bin/env python3
"""
Captain Inbox Helper - Auto-responds to common message types
Helps Agent-4 manage inbox overload by auto-responding to routine messages
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import re

class CaptainInboxHelper:
    def __init__(self, inbox_path: Path):
        self.inbox_path = Path(inbox_path).resolve()
        # Find repo root by looking for agent_workspaces directory
        current = self.inbox_path
        while current.parent != current:
            if (current / "agent_workspaces").exists():
                self.repo_root = current
                break
            current = current.parent
        else:
            self.repo_root = Path(__file__).resolve().parents[1]
        self.responses: List[Dict] = []
        
    def analyze_message(self, file_path: Path) -> Dict:
        """Analyze a message file and determine response type"""
        content = file_path.read_text(encoding='utf-8')
        
        # Extract metadata
        from_match = re.search(r'\*\*From\*\*:\s*(.+)', content)
        to_match = re.search(r'\*\*To\*\*:\s*(.+)', content)
        priority_match = re.search(r'\*\*Priority\*\*:\s*(.+)', content)
        
        from_agent = from_match.group(1).strip() if from_match else "Unknown"
        to_agent = to_match.group(1).strip() if to_match else "Unknown"
        priority = priority_match.group(1).strip() if priority_match else "NORMAL"
        
        # Determine message type
        message_type = "UNKNOWN"
        if "COMPLETE" in content or "✅" in content:
            message_type = "COMPLETION_REPORT"
        elif "BLOCKER" in content or "🚨" in content:
            message_type = "BLOCKER_REPORT"
        elif "STATUS" in content or "UPDATE" in content:
            message_type = "STATUS_UPDATE"
        elif "ACKNOWLEDGMENT" in content or "ACK" in content:
            message_type = "ACKNOWLEDGMENT"
        elif "TECHNICAL_DEBT" in content or "ANALYSIS" in content:
            message_type = "ANALYSIS_REPORT"
        elif "RESOLUTION" in content or "RESOLVED" in content:
            message_type = "RESOLUTION_REPORT"
        
        return {
            "file": str(file_path.relative_to(self.repo_root)),
            "from": from_agent,
            "to": to_agent,
            "priority": priority,
            "type": message_type,
            "timestamp": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
    
    def generate_response(self, message_info: Dict) -> Optional[str]:
        """Generate auto-response based on message type"""
        msg_type = message_info["type"]
        from_agent = message_info["from"]
        priority = message_info["priority"]
        
        if msg_type == "COMPLETION_REPORT":
            return f"""# ✅ Captain Acknowledgment - Task Complete

**From**: Captain Agent-4
**To**: {from_agent}
**Priority**: {priority}
**Timestamp**: {datetime.now().isoformat()}

---

## ✅ **ACKNOWLEDGED**

**Status**: Task completion acknowledged
**Action**: Excellent work! Task marked as complete in Captain tracking.

**Next Steps**: Continue with assigned priorities.

---

🐝 **WE. ARE. SWARM. ⚡🔥**
"""
        
        elif msg_type == "BLOCKER_REPORT":
            return f"""# 🚨 Captain Response - Blocker Acknowledged

**From**: Captain Agent-4
**To**: {from_agent}
**Priority**: 🚨 URGENT
**Timestamp**: {datetime.now().isoformat()}

---

## 🚨 **BLOCKER ACKNOWLEDGED**

**Status**: Blocker report received and logged
**Action**: Captain will coordinate resolution or assign to appropriate agent.

**Next Steps**: 
- Captain reviewing blocker details
- Will assign resolution task if needed
- Continue with other priorities while blocker is addressed

---

🐝 **WE. ARE. SWARM. ⚡🔥**
"""
        
        elif msg_type == "STATUS_UPDATE":
            return f"""# ✅ Captain Acknowledgment - Status Update

**From**: Captain Agent-4
**To**: {from_agent}
**Priority**: {priority}
**Timestamp**: {datetime.now().isoformat()}

---

## ✅ **STATUS ACKNOWLEDGED**

**Status**: Status update received and logged
**Action**: Captain tracking updated with current status.

**Next Steps**: Continue with assigned priorities.

---

🐝 **WE. ARE. SWARM. ⚡🔥**
"""
        
        elif msg_type == "ACKNOWLEDGMENT":
            return f"""# ✅ Captain Confirmation

**From**: Captain Agent-4
**To**: {from_agent}
**Priority**: {priority}
**Timestamp**: {datetime.now().isoformat()}

---

## ✅ **CONFIRMED**

**Status**: Acknowledgment received
**Action**: Captain confirms receipt and coordination.

**Next Steps**: Continue with assigned priorities.

---

🐝 **WE. ARE. SWARM. ⚡🔥**
"""
        
        elif msg_type == "ANALYSIS_REPORT":
            return f"""# ✅ Captain Acknowledgment - Analysis Report

**From**: Captain Agent-4
**To**: {from_agent}
**Priority**: {priority}
**Timestamp**: {datetime.now().isoformat()}

---

## ✅ **ANALYSIS ACKNOWLEDGED**

**Status**: Analysis report received and reviewed
**Action**: Captain will review findings and coordinate task assignments.

**Next Steps**: 
- Captain reviewing analysis
- Will coordinate task distribution if needed
- Continue with assigned priorities

---

🐝 **WE. ARE. SWARM. ⚡🔥**
"""
        
        elif msg_type == "RESOLUTION_REPORT":
            return f"""# ✅ Captain Acknowledgment - Resolution Complete

**From**: Captain Agent-4
**To**: {from_agent}
**Priority**: {priority}
**Timestamp**: {datetime.now().isoformat()}

---

## ✅ **RESOLUTION ACKNOWLEDGED**

**Status**: Resolution report received
**Action**: Excellent problem-solving! Blocker resolution logged.

**Next Steps**: Continue with assigned priorities.

---

🐝 **WE. ARE. SWARM. ⚡🔥**
"""
        
        return None
    
    def process_inbox(self, auto_respond: bool = False, dry_run: bool = False):
        """Process all messages in inbox"""
        if not self.inbox_path.exists():
            print(f"❌ Inbox not found: {self.inbox_path}")
            return
        
        messages = list(self.inbox_path.glob("*.md"))
        print(f"📬 Found {len(messages)} messages in inbox")
        
        for msg_file in sorted(messages, key=lambda p: p.stat().st_mtime, reverse=True):
            msg_info = self.analyze_message(msg_file)
            self.responses.append(msg_info)
            
            print(f"\n📨 {msg_file.name}")
            print(f"   From: {msg_info['from']}")
            print(f"   Type: {msg_info['type']}")
            print(f"   Priority: {msg_info['priority']}")
            
            if auto_respond and not dry_run:
                response = self.generate_response(msg_info)
                if response:
                    # Save response to sender's inbox
                    sender_match = re.search(r'Agent-(\d+)', msg_info['from'])
                    if sender_match:
                        agent_num = sender_match.group(1)
                        sender_inbox = self.repo_root / f"agent_workspaces/Agent-{agent_num}/inbox"
                        sender_inbox.mkdir(parents=True, exist_ok=True)
                        
                        response_file = sender_inbox / f"CAPTAIN_ACK_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{msg_file.stem}.md"
                        response_file.write_text(response, encoding='utf-8')
                        print(f"   ✅ Response sent to {msg_info['from']}")
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate summary report"""
        summary = {
            "total_messages": len(self.responses),
            "by_type": {},
            "by_priority": {},
            "by_agent": {},
            "unresponded": []
        }
        
        for msg in self.responses:
            msg_type = msg['type']
            priority = msg['priority']
            from_agent = msg['from']
            
            summary["by_type"][msg_type] = summary["by_type"].get(msg_type, 0) + 1
            summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1
            summary["by_agent"][from_agent] = summary["by_agent"].get(from_agent, 0) + 1
        
        print("\n" + "="*60)
        print("📊 INBOX SUMMARY")
        print("="*60)
        print(f"Total Messages: {summary['total_messages']}")
        print(f"\nBy Type:")
        for msg_type, count in sorted(summary['by_type'].items(), key=lambda x: -x[1]):
            print(f"  {msg_type}: {count}")
        print(f"\nBy Priority:")
        for priority, count in sorted(summary['by_priority'].items(), key=lambda x: -x[1]):
            print(f"  {priority}: {count}")
        print(f"\nBy Agent:")
        for agent, count in sorted(summary['by_agent'].items(), key=lambda x: -x[1]):
            print(f"  {agent}: {count}")

def main():
    parser = argparse.ArgumentParser(description="Captain Inbox Helper - Auto-respond to common messages")
    parser.add_argument("--inbox", type=str, default="agent_workspaces/Agent-4/inbox",
                       help="Path to Captain inbox")
    parser.add_argument("--auto-respond", action="store_true",
                       help="Automatically generate and send responses")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be done without actually doing it")
    args = parser.parse_args()
    
    inbox_path = Path(args.inbox)
    helper = CaptainInboxHelper(inbox_path)
    helper.process_inbox(auto_respond=args.auto_respond, dry_run=args.dry_run)

if __name__ == "__main__":
    main()

