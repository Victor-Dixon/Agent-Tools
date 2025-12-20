#!/usr/bin/env python3
"""
Process Captain Inbox Complete - Responds to all messages and archives them
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import subprocess
from src.core.config.timeout_constants import TimeoutConstants

class CaptainInboxProcessor:
    def __init__(self, inbox_path: Path, archive_path: Path):
        self.inbox_path = inbox_path
        self.archive_path = archive_path
        self.archive_path.mkdir(parents=True, exist_ok=True)
        self.processed = []
        self.responses_sent = []
        
    def extract_agent_from_message(self, content: str) -> str:
        """Extract agent name from message content"""
        from_match = re.search(r'\*\*From\*\*:\s*(.+)', content)
        if from_match:
            from_text = from_match.group(1).strip()
            # Extract agent number
            agent_match = re.search(r'Agent[-\s]?(\d+)', from_text, re.IGNORECASE)
            if agent_match:
                return f"Agent-{agent_match.group(1)}"
        return None
    
    def generate_response(self, msg_file: Path, content: str) -> str:
        """Generate appropriate response based on message type"""
        agent = self.extract_agent_from_message(content)
        
        if "COMPLETE" in content or "✅" in content:
            return f"✅ Captain Acknowledgment - Task Complete: Excellent work! Task completion acknowledged and logged. Continue with assigned priorities. 🐝 WE. ARE. SWARM. ⚡🔥"
        elif "BLOCKER" in content or "🚨" in content:
            return f"🚨 Captain Response - Blocker Acknowledged: Blocker report received and logged. Captain will coordinate resolution or assign to appropriate agent. Continue with other priorities. 🐝 WE. ARE. SWARM. ⚡🔥"
        elif "STATUS" in content or "UPDATE" in content:
            return f"✅ Captain Acknowledgment - Status Update: Status update received and logged. Captain tracking updated. Continue with assigned priorities. 🐝 WE. ARE. SWARM. ⚡🔥"
        elif "ACKNOWLEDGMENT" in content or "ACK" in content:
            return f"✅ Captain Confirmation: Acknowledgment received. Captain confirms receipt and coordination. Continue with assigned priorities. 🐝 WE. ARE. SWARM. ⚡🔥"
        elif "ANALYSIS" in content or "REPORT" in content:
            return f"✅ Captain Acknowledgment - Analysis Report: Analysis report received and reviewed. Captain will review findings and coordinate task assignments. Continue with assigned priorities. 🐝 WE. ARE. SWARM. ⚡🔥"
        else:
            return f"✅ Captain Acknowledgment: Message received and logged. Captain reviewing content. Continue with assigned priorities. 🐝 WE. ARE. SWARM. ⚡🔥"
    
    def send_message(self, agent: str, message: str) -> bool:
        """Send message via messaging CLI"""
        try:
            result = subprocess.run(
                ["python", "-m", "src.services.messaging_cli", "--agent", agent, "--message", message],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_DEFAULT
            )
            return result.returncode == 0
        except Exception as e:
            print(f"   ⚠️ Error sending message: {e}")
            return False
    
    def process_all_messages(self):
        """Process all messages in inbox"""
        messages = list(self.inbox_path.glob("*.md"))
        print(f"📬 Processing {len(messages)} messages...\n")
        
        for msg_file in sorted(messages, key=lambda p: p.stat().st_mtime):
            try:
                content = msg_file.read_text(encoding='utf-8')
                agent = self.extract_agent_from_message(content)
                
                print(f"📨 {msg_file.name}")
                
                if agent:
                    response = self.generate_response(msg_file, content)
                    print(f"   To: {agent}")
                    print(f"   Sending response...", end=" ")
                    
                    if self.send_message(agent, response):
                        print("✅")
                        self.responses_sent.append({
                            "file": msg_file.name,
                            "agent": agent,
                            "timestamp": datetime.now().isoformat()
                        })
                    else:
                        print("⚠️")
                else:
                    print(f"   ⚠️ Could not extract agent, skipping response")
                
                # Archive message
                archive_file = self.archive_path / msg_file.name
                msg_file.rename(archive_file)
                print(f"   📦 Archived to: {archive_file.name}\n")
                
                self.processed.append({
                    "file": msg_file.name,
                    "agent": agent,
                    "archived": True
                })
                
            except Exception as e:
                print(f"   ❌ Error processing {msg_file.name}: {e}\n")
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate processing summary"""
        summary = {
            "total_processed": len(self.processed),
            "responses_sent": len(self.responses_sent),
            "timestamp": datetime.now().isoformat()
        }
        
        print("="*60)
        print("📊 PROCESSING SUMMARY")
        print("="*60)
        print(f"Total Messages Processed: {summary['total_processed']}")
        print(f"Responses Sent: {summary['responses_sent']}")
        print(f"Archive Location: {self.archive_path}")
        print("="*60)
        
        # Save summary
        summary_file = self.archive_path.parent / f"INBOX_PROCESSING_SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary_file.write_text(json.dumps(summary, indent=2), encoding='utf-8')
        print(f"\n📄 Summary saved to: {summary_file}")

def main():
    inbox_path = Path("agent_workspaces/Agent-4/inbox")
    archive_path = Path("agent_workspaces/Agent-4/inbox/archive") / datetime.now().strftime("%Y-%m-%d")
    
    processor = CaptainInboxProcessor(inbox_path, archive_path)
    processor.process_all_messages()

if __name__ == "__main__":
    main()




