#!/usr/bin/env python3
"""
Session Cleanup Automation Tool for Agent-3
============================================

Comprehensive session cleanup automation tool that I wished I had:
1. Creates/Updates passdown.json
2. Creates Final Devlog
3. Posts Devlog to Discord
4. Updates Swarm Brain Database
5. Creates session summary

This tool streamlines the session cleanup process specifically for Agent-3's workflow.

Author: Agent-3 (Infrastructure & DevOps Specialist)
Date: 2025-12-15
"""

import json
import os
import sys
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()


class Agent3SessionCleanup:
    """Session cleanup automation for Agent-3."""

    def __init__(self):
        self.agent_id = "Agent-3"
        self.agent_name = "Infrastructure & DevOps Specialist"
        self.session_date = datetime.now().strftime("%Y-%m-%d")
        self.project_root = project_root
        self.workspace_path = project_root / "agent_workspaces" / self.agent_id

    def load_passdown(self) -> Dict[str, Any]:
        """Load or create passdown.json."""
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
            passdown = self.load_passdown()

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
            devlog_filename = f"devlog_{self.session_date}_final_session.md"
            devlog_path = self.workspace_path / devlog_filename

            devlog_path.parent.mkdir(parents=True, exist_ok=True)
            devlog_path.write_text(devlog_content, encoding="utf-8")

            print(f"✅ Devlog created: {devlog_path}")
            return devlog_path
        except Exception as e:
            print(f"❌ Error creating devlog: {e}")
            return None

    def post_devlog_to_discord(self, devlog_content: str) -> bool:
        """Post devlog to Discord webhook."""
        webhook_url = os.getenv('DISCORD_WEBHOOK_AGENT_3')
        if not webhook_url:
            print('⚠️ No DISCORD_WEBHOOK_AGENT_3 env set; skipping Discord post')
            return False

        # Prepare Discord embed
        embed = {
            'title': f'Agent-3 Session Cleanup – {self.session_date}',
            'description': devlog_content[:2000],  # Discord embed limit
            'color': 0x00d4aa,  # Trading green
            'footer': {'text': f'{self.agent_name} - {self.agent_id}'},
            'timestamp': datetime.now().isoformat()
        }

        payload = {
            'embeds': [embed]
        }

        try:
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 204:
                print('✅ Devlog posted to Discord!')
                return True
            else:
                print(f'❌ Failed to post: {response.status_code}')
                print(f'Response: {response.text}')
                return False
        except Exception as e:
            print(f'❌ Error posting devlog: {e}')
            return False

    def update_swarm_brain(self, entries: list) -> bool:
        """Update Swarm Brain knowledge base with session learnings."""
        try:
            kb_path = self.project_root / "swarm_brain" / "knowledge_base.json"

            if not kb_path.exists():
                print(f'⚠️ Swarm Brain not found at {kb_path}; skipping')
                return False

            with open(kb_path, 'r', encoding='utf-8') as f:
                kb = json.load(f)

            for entry_data in entries:
                entry_id = f"kb-{kb['stats']['total_entries'] + 1}"
                kb['entries'][entry_id] = {
                    "id": entry_id,
                    "title": entry_data.get("title", ""),
                    "content": entry_data.get("content", ""),
                    "author": self.agent_id,
                    "category": entry_data.get("category", "learning"),
                    "tags": entry_data.get("tags", []),
                    "timestamp": datetime.now().isoformat(),
                    "metadata": entry_data.get("metadata", {})
                }

                kb['stats']['total_entries'] += 1
                kb['stats']['contributors'][self.agent_id] = kb['stats']['contributors'].get(
                    self.agent_id, 0) + 1

            kb['last_updated'] = datetime.now().isoformat()

            with open(kb_path, 'w', encoding='utf-8') as f:
                json.dump(kb, f, indent=2, ensure_ascii=False)

            print(f"✅ Added {len(entries)} entries to Swarm Brain")
            print(f"   Total entries: {kb['stats']['total_entries']}")
            return True
        except Exception as e:
            print(f'❌ Error updating Swarm Brain: {e}')
            return False

    def run_cleanup(self,
                    passdown_updates: Dict[str, Any],
                    devlog_content: str,
                    swarm_brain_entries: list) -> bool:
        """Run complete session cleanup."""
        print(f"🚀 Starting session cleanup for {self.agent_id}...")
        print(f"   Session Date: {self.session_date}\n")

        # 1. Update passdown.json
        print("1️⃣ Updating passdown.json...")
        if not self.update_passdown(passdown_updates):
            return False

        # 2. Create devlog
        print("\n2️⃣ Creating devlog...")
        devlog_path = self.create_devlog(devlog_content)
        if not devlog_path:
            return False

        # 3. Post devlog to Discord
        print("\n3️⃣ Posting devlog to Discord...")
        self.post_devlog_to_discord(devlog_content)

        # 4. Update Swarm Brain
        print("\n4️⃣ Updating Swarm Brain...")
        if swarm_brain_entries:
            self.update_swarm_brain(swarm_brain_entries)

        print("\n✅ Session cleanup complete!")
        return True


def main():
    """Main execution."""
    cleanup = Agent3SessionCleanup()

    # Load devlog content
    devlog_path = cleanup.workspace_path / \
        f"devlog_{cleanup.session_date}_final_session.md"
    if not devlog_path.exists():
        print(f"❌ Devlog not found: {devlog_path}")
        print("   Please create devlog first")
        return False

    devlog_content = devlog_path.read_text(encoding="utf-8")

    # Load passdown updates (already created, just verify)
    passdown_path = cleanup.project_root / "passdown.json"
    if not passdown_path.exists():
        print(f"❌ Passdown not found: {passdown_path}")
        print("   Please create passdown.json first")
        return False

    # Swarm Brain entries
    swarm_brain_entries = [
        {
            "title": "Handler+Helper Pattern for Activity Detection Refactoring",
            "content": "Handler+Helper pattern proven effective for activity detection refactoring. Main handler class orchestrates detection by delegating to specialized checker modules. Result: 809 lines → 162 lines (80% reduction). Pattern: Handler class delegates to ActivitySourceCheckers (Tier 1), ActivitySourceCheckersTier2 (Tier 2), and activity_detector_helpers (filtering, confidence, validation). Key insight: Extract by responsibility (checkers vs helpers) rather than by tier alone. Files: src/core/hardened_activity_detector.py, src/core/activity_source_checkers_tier2.py, src/core/activity_detector_helpers.py",
            "category": "learning",
            "tags": ["refactoring", "v2-compliance", "architecture", "pattern", "handler-helper"],
            "metadata": {"reduction": "80%", "lines_removed": 647}
        },
        {
            "title": "Service+Integration Pattern for Self-Healing Refactoring",
            "content": "Service+Integration pattern proven effective for self-healing system refactoring. Main service class orchestrates healing workflow by delegating to operations (core healing) and integration (external services) modules. Result: 754 lines → 364 lines (52% reduction). Pattern: Service class delegates to SelfHealingOperations (terminal cancellation, status reset, task clearing) and SelfHealingIntegration (messaging, onboarding). Key insight: Separate operational logic from external service integrations for better testability and maintainability. Files: src/core/agent_self_healing_system.py, src/core/self_healing_operations.py, src/core/self_healing_integration.py",
            "category": "learning",
            "tags": ["refactoring", "v2-compliance", "architecture", "pattern", "service-integration"],
            "metadata": {"reduction": "52%", "lines_removed": 390}
        },
        {
            "title": "Messaging Scripts Deprecation with CLI Migration Path",
            "content": "Standardizing messaging system by deprecating one-off send scripts in favor of canonical CLI. Approach: Mark scripts as deprecated with headers containing CLI equivalents, keep for backward compatibility. Pattern: Add deprecation notice, provide equivalent CLI command, reference template documentation. Benefit: Clear migration path ensures smooth transition while maintaining backward compatibility. Key insight: Deprecation headers with examples are more effective than immediate removal. Files: All tools/send_*.py scripts now use: python -m src.services.messaging_cli --agent <id> -m \"<msg>\" --type text --category a2a",
            "category": "learning",
            "tags": ["messaging", "standardization", "deprecation", "cli", "migration"],
            "metadata": {"scripts_deprecated": 14}
        }
    ]

    # Run cleanup
    return cleanup.run_cleanup(
        passdown_updates={},  # Already updated
        devlog_content=devlog_content,
        swarm_brain_entries=swarm_brain_entries
    )


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
