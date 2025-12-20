#!/usr/bin/env python3
"""
Post Agent-3 Session Cleanup Devlog
====================================

Posts Agent-3's session cleanup devlog to Discord and updates Swarm Brain.
"""

import json
import os
import sys
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

project_root = Path(__file__).parent.parent
workspace_path = project_root / "agent_workspaces" / "Agent-3"
session_date = datetime.now().strftime("%Y-%m-%d")
devlog_path = workspace_path / f"devlog_{session_date}_final_session.md"
kb_path = project_root / "swarm_brain" / "knowledge_base.json"


def post_to_discord(content: str):
    """Post devlog to Discord."""
    webhook_url = os.getenv('DISCORD_WEBHOOK_AGENT_3')
    if not webhook_url:
        print('⚠️ No DISCORD_WEBHOOK_AGENT_3 env set; skipping Discord post')
        return False

    embed = {
        'title': f'Agent-3 Session Cleanup – {session_date}',
        'description': content[:2000],
        'color': 0x00d4aa,
        'footer': {'text': 'Infrastructure & DevOps Specialist - Agent-3'},
        'timestamp': datetime.now().isoformat()
    }

    payload = {'embeds': [embed]}

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            print('✅ Devlog posted to Discord!')
            return True
        else:
            print(f'❌ Failed to post: {response.status_code}')
            return False
    except Exception as e:
        print(f'❌ Error posting devlog: {e}')
        return False


def update_swarm_brain():
    """Update Swarm Brain with session learnings."""
    if not kb_path.exists():
        print(f'⚠️ Swarm Brain not found; skipping')
        return False

    with open(kb_path, 'r', encoding='utf-8') as f:
        kb = json.load(f)

    entries = [
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

    for entry_data in entries:
        entry_id = f"kb-{kb['stats']['total_entries'] + 1}"
        kb['entries'][entry_id] = {
            "id": entry_id,
            "title": entry_data["title"],
            "content": entry_data["content"],
            "author": "Agent-3",
            "category": entry_data["category"],
            "tags": entry_data["tags"],
            "timestamp": datetime.now().isoformat(),
            "metadata": entry_data.get("metadata", {})
        }

        kb['stats']['total_entries'] += 1
        kb['stats']['contributors']['Agent-3'] = kb['stats']['contributors'].get(
            'Agent-3', 0) + 1

    kb['last_updated'] = datetime.now().isoformat()

    with open(kb_path, 'w', encoding='utf-8') as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)

    print(f"✅ Added {len(entries)} entries to Swarm Brain")
    print(f"   Total entries: {kb['stats']['total_entries']}")
    return True


def main():
    """Main execution."""
    print(f"📝 Reading devlog: {devlog_path}")
    if not devlog_path.exists():
        print(f"❌ Devlog not found: {devlog_path}")
        return False

    devlog_content = devlog_path.read_text(encoding="utf-8")
    print(f"✅ Devlog loaded ({len(devlog_content)} characters)")

    print("\n📤 Posting to Discord...")
    post_to_discord(devlog_content)

    print("\n🧠 Updating Swarm Brain...")
    update_swarm_brain()

    print("\n✅ Session cleanup complete!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
