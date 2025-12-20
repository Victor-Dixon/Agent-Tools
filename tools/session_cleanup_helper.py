#!/usr/bin/env python3
"""
Session Cleanup Helper Tool
===========================

A comprehensive tool I wished I had - automates session cleanup tasks:
1. Create/Update passdown.json
2. Create Final Devlog
3. Post Devlog to Discord
4. Update Swarm Brain Database
5. Create session summary

This tool streamlines the session cleanup process for all agents.
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SessionCleanupHelper:
    """Helper class for session cleanup automation."""

    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.session_date = datetime.now().strftime("%Y-%m-%d")
        self.project_root = project_root

    def load_passdown_template(self) -> Dict[str, Any]:
        """Load passdown.json template structure."""
        passdown_path = self.project_root / "passdown.json"

        if passdown_path.exists():
            try:
                with open(passdown_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass

        # Return default template
        return {
            "session_date": self.session_date,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "session_summary": "",
            "status": "SESSION_COMPLETE",
            "completed_work": {},
            "tools_created": [],
            "knowledge_transfers": {},
            "active_refactoring": {},
            "next_session_priorities": [],
            "coordination_status": {},
            "metrics": {},
            "lessons_learned": [],
            "blockers": [],
            "notes": ""
        }

    def update_passdown(self, updates: Dict[str, Any]) -> bool:
        """Update passdown.json with session data."""
        try:
            passdown = self.load_passdown_template()

            # Merge updates
            for key, value in updates.items():
                if key in passdown and isinstance(passdown[key], dict) and isinstance(value, dict):
                    passdown[key].update(value)
                else:
                    passdown[key] = value

            # Save
            passdown_path = self.project_root / "passdown.json"
            with open(passdown_path, 'w', encoding='utf-8') as f:
                json.dump(passdown, f, indent=2, ensure_ascii=False)

            print(f"✅ Passdown updated: {passdown_path}")
            return True

        except Exception as e:
            print(f"❌ Error updating passdown: {e}")
            return False

    def create_devlog(self, devlog_content: str) -> Optional[Path]:
        """Create devlog markdown file."""
        try:
            devlog_filename = f"AGENT2_DEVLOG_{self.session_date}.md"
            devlog_path = self.project_root / "docs" / devlog_filename

            devlog_path.parent.mkdir(parents=True, exist_ok=True)
            devlog_path.write_text(devlog_content, encoding="utf-8")

            print(f"✅ Devlog created: {devlog_path}")
            return devlog_path

        except Exception as e:
            print(f"❌ Error creating devlog: {e}")
            return None

    def post_devlog_to_discord(self, devlog_path: Path) -> bool:
        """Post devlog to Discord."""
        try:
            from src.core.messaging_core import (
                send_message,
                UnifiedMessageType,
                UnifiedMessagePriority,
                UnifiedMessageTag,
            )

            devlog_content = devlog_path.read_text(encoding="utf-8")

            # Create summary message
            msg = f"""**📝 {self.agent_id} DEVLOG POSTED**

**Date:** {self.session_date}
**Channel:** #agent-2-devlogs

**Session Summary:**
{self.get_session_summary()}

**Full Devlog:**
```markdown
{devlog_content[:1500]}...
```

See full devlog: `{devlog_path.relative_to(self.project_root)}`
"""

            send_message(
                msg,
                self.agent_id,
                "Agent-4",  # Captain for coordination
                UnifiedMessageType.TEXT,
                UnifiedMessagePriority.REGULAR,
                [UnifiedMessageTag.COORDINATION, UnifiedMessageTag.DEVLOG],
            )

            print(f"✅ Devlog posted to Discord coordination channel")
            return True

        except Exception as e:
            print(f"⚠️  Could not post to Discord: {e}")
            print(f"📄 Devlog available at: {devlog_path}")
            return False

    def update_swarm_brain(self, session_data: Dict[str, Any]) -> bool:
        """Update Swarm Brain Database with session knowledge."""
        try:
            # Create knowledge entry
            knowledge_entry = {
                "agent_id": self.agent_id,
                "session_date": self.session_date,
                "session_summary": session_data.get("session_summary", ""),
                "key_achievements": session_data.get("completed_work", {}),
                "metrics": session_data.get("metrics", {}),
                "lessons_learned": session_data.get("lessons_learned", []),
                "tools_created": session_data.get("tools_created", []),
                "timestamp": datetime.now().isoformat()
            }

            # Save to swarm brain directory
            brain_dir = self.project_root / "docs" / "swarm_brain"
            brain_dir.mkdir(parents=True, exist_ok=True)

            brain_file = brain_dir / \
                f"{self.agent_id}_session_{self.session_date}.json"
            with open(brain_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge_entry, f, indent=2, ensure_ascii=False)

            print(f"✅ Swarm Brain updated: {brain_file}")
            return True

        except Exception as e:
            print(f"⚠️  Could not update Swarm Brain: {e}")
            return False

    def get_session_summary(self) -> str:
        """Get formatted session summary."""
        passdown = self.load_passdown_template()
        summary = passdown.get("session_summary", "Session completed")
        return summary

    def run_full_cleanup(self, session_data: Dict[str, Any], devlog_content: str) -> bool:
        """Run complete session cleanup process."""
        print(f"🧹 Starting session cleanup for {self.agent_id}...")
        print()

        # 1. Update passdown.json
        print("1️⃣  Updating passdown.json...")
        if not self.update_passdown(session_data):
            return False
        print()

        # 2. Create devlog
        print("2️⃣  Creating devlog...")
        devlog_path = self.create_devlog(devlog_content)
        if not devlog_path:
            return False
        print()

        # 3. Post to Discord
        print("3️⃣  Posting devlog to Discord...")
        self.post_devlog_to_discord(devlog_path)
        print()

        # 4. Update Swarm Brain
        print("4️⃣  Updating Swarm Brain Database...")
        self.update_swarm_brain(session_data)
        print()

        # 5. Summary
        print("✅ Session cleanup complete!")
        print(f"📄 Devlog: {devlog_path.relative_to(self.project_root)}")
        print(f"📋 Passdown: passdown.json")
        print(
            f"🧠 Swarm Brain: docs/swarm_brain/{self.agent_id}_session_{self.session_date}.json")

        return True


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python session_cleanup_helper.py <agent_id> <agent_name>")
        print("Example: python session_cleanup_helper.py Agent-2 'Architecture & Design Specialist'")
        sys.exit(1)

    agent_id = sys.argv[1]
    agent_name = sys.argv[2]

    helper = SessionCleanupHelper(agent_id, agent_name)

    # Load session data from passdown if it exists
    session_data = helper.load_passdown_template()

    # Read devlog content if it exists
    devlog_path = project_root / "docs" / \
        f"AGENT2_DEVLOG_{helper.session_date}.md"
    if devlog_path.exists():
        devlog_content = devlog_path.read_text(encoding="utf-8")
    else:
        devlog_content = f"# {agent_id} Devlog - {helper.session_date}\n\nSession cleanup in progress...\n"

    # Run cleanup
    helper.run_full_cleanup(session_data, devlog_content)


if __name__ == "__main__":
    main()
