#!/usr/bin/env python3
"""
Process Agent-8 Workspace Messages - Respond, extract info, update state, archive
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import subprocess
from src.core.config.timeout_constants import TimeoutConstants

class Agent8WorkspaceProcessor:
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.inbox_path = workspace_path / "inbox"
        self.archive_path = workspace_path / "archive" / datetime.now().strftime("%Y-%m-%d")
        self.archive_path.mkdir(parents=True, exist_ok=True)
        self.notes_path = workspace_path / "notes"
        self.notes_path.mkdir(parents=True, exist_ok=True)
        self.processed = []
        self.state_updates = []
        
    def extract_info_from_message(self, content: str) -> Dict:
        """Extract key information from message"""
        info = {
            "from": None,
            "to": None,
            "priority": None,
            "type": "UNKNOWN",
            "key_points": [],
            "actions": []
        }
        
        # Extract metadata
        from_match = re.search(r'\*\*From\*\*:\s*(.+)', content)
        to_match = re.search(r'\*\*To\*\*:\s*(.+)', content)
        priority_match = re.search(r'\*\*Priority\*\*:\s*(.+)', content)
        
        if from_match:
            info["from"] = from_match.group(1).strip()
        if to_match:
            info["to"] = to_match.group(1).strip()
        if priority_match:
            info["priority"] = priority_match.group(1).strip()
        
        # Determine type
        if "COMPLETE" in content or "✅" in content:
            info["type"] = "COMPLETION"
        elif "BLOCKER" in content or "🚨" in content:
            info["type"] = "BLOCKER"
        elif "ASSIGNMENT" in content or "TASK" in content:
            info["type"] = "ASSIGNMENT"
        elif "STATUS" in content or "UPDATE" in content:
            info["type"] = "STATUS_UPDATE"
        
        # Extract key points (lines with ✅, ⚠️, 🚨, or **)
        for line in content.split('\n'):
            if any(marker in line for marker in ['✅', '⚠️', '🚨', '**COMPLETE**', '**BLOCKER**']):
                clean_line = re.sub(r'[#*]', '', line).strip()
                if clean_line and len(clean_line) > 10:
                    info["key_points"].append(clean_line[:200])
        
        return info
    
    def generate_response(self, info: Dict) -> str:
        """Generate appropriate response"""
        if info["type"] == "COMPLETION":
            return f"✅ Acknowledged - Task Complete: Excellent work! Completion logged. Continue with assigned priorities. 🐝 WE. ARE. SWARM. ⚡🔥"
        elif info["type"] == "BLOCKER":
            return f"🚨 Blocker Acknowledged: Blocker report received. Will coordinate resolution. Continue with other priorities. 🐝 WE. ARE. SWARM. ⚡🔥"
        elif info["type"] == "ASSIGNMENT":
            return f"✅ Assignment Acknowledged: Task assignment received and logged. Will begin execution. 🐝 WE. ARE. SWARM. ⚡🔥"
        elif info["type"] == "STATUS_UPDATE":
            return f"✅ Status Update Acknowledged: Status update received and logged. Continue with assigned priorities. 🐝 WE. ARE. SWARM. ⚡🔥"
        else:
            return f"✅ Message Acknowledged: Message received and logged. Reviewing content. Continue with assigned priorities. 🐝 WE. ARE. SWARM. ⚡🔥"
    
    def send_response(self, sender: str, response: str) -> bool:
        """Send response via messaging system"""
        # Extract agent number from sender
        agent_match = re.search(r'Agent[-\s]?(\d+)', sender, re.IGNORECASE)
        if agent_match:
            agent = f"Agent-{agent_match.group(1)}"
            try:
                result = subprocess.run(
                    ["python", "-m", "src.services.messaging_cli", "--agent", agent, "--message", response],
                    capture_output=True,
                    text=True,
                    timeout=TimeoutConstants.HTTP_DEFAULT
                )
                return result.returncode == 0
            except:
                return False
        return False
    
    def update_state_notes(self, info: Dict, content: str):
        """Update state notes with message information"""
        note_file = self.notes_path / f"state_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        note_content = f"""# State Update from Message

**Date**: {datetime.now().isoformat()}
**From**: {info.get('from', 'Unknown')}
**Type**: {info['type']}
**Priority**: {info.get('priority', 'NORMAL')}

## Key Points

"""
        for point in info["key_points"][:10]:  # Limit to 10 key points
            note_content += f"- {point}\n"
        
        note_content += f"\n## Full Content\n\n```\n{content[:1000]}...\n```\n"
        
        note_file.write_text(note_content, encoding='utf-8')
        self.state_updates.append(str(note_file))
    
    def process_inbox(self):
        """Process all inbox messages"""
        if not self.inbox_path.exists():
            print("📬 No inbox directory found")
            return
        
        messages = list(self.inbox_path.glob("*.md"))
        print(f"📬 Processing {len(messages)} inbox messages...\n")
        
        for msg_file in sorted(messages, key=lambda p: p.stat().st_mtime):
            try:
                content = msg_file.read_text(encoding='utf-8')
                info = self.extract_info_from_message(content)
                
                print(f"📨 {msg_file.name}")
                print(f"   From: {info.get('from', 'Unknown')}")
                print(f"   Type: {info['type']}")
                
                # Send response if from another agent
                if info.get('from') and 'Agent' in info['from']:
                    response = self.generate_response(info)
                    print(f"   Sending response...", end=" ")
                    if self.send_response(info['from'], response):
                        print("✅")
                    else:
                        print("⚠️")
                
                # Update state notes
                self.update_state_notes(info, content)
                print(f"   📝 State notes updated")
                
                # Archive
                archive_file = self.archive_path / msg_file.name
                msg_file.rename(archive_file)
                print(f"   📦 Archived\n")
                
                self.processed.append({
                    "file": msg_file.name,
                    "type": info['type'],
                    "archived": True
                })
                
            except Exception as e:
                print(f"   ❌ Error: {e}\n")
    
    def process_workspace_messages(self):
        """Process message files in workspace root"""
        message_files = list(self.workspace_path.glob("*MESSAGE*.md")) + \
                       list(self.workspace_path.glob("*CAPTAIN*.md")) + \
                       list(self.workspace_path.glob("*ASSIGNMENT*.md"))
        
        print(f"📬 Processing {len(message_files)} workspace message files...\n")
        
        for msg_file in message_files:
            try:
                content = msg_file.read_text(encoding='utf-8')
                info = self.extract_info_from_message(content)
                
                print(f"📨 {msg_file.name}")
                
                # Update state notes
                self.update_state_notes(info, content)
                print(f"   📝 State notes updated")
                
                # Archive
                archive_file = self.archive_path / msg_file.name
                msg_file.rename(archive_file)
                print(f"   📦 Archived\n")
                
                self.processed.append({
                    "file": msg_file.name,
                    "type": info['type'],
                    "archived": True
                })
                
            except Exception as e:
                print(f"   ❌ Error: {e}\n")
    
    def generate_summary(self):
        """Generate processing summary"""
        print("="*60)
        print("📊 PROCESSING SUMMARY")
        print("="*60)
        print(f"Total Processed: {len(self.processed)}")
        print(f"State Updates: {len(self.state_updates)}")
        print(f"Archive: {self.archive_path}")
        print("="*60)

def main():
    workspace_path = Path("agent_workspaces/Agent-8")
    processor = Agent8WorkspaceProcessor(workspace_path)
    
    processor.process_inbox()
    processor.process_workspace_messages()
    processor.generate_summary()

if __name__ == "__main__":
    main()




