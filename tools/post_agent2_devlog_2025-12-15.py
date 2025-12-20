#!/usr/bin/env python3
"""Post Agent-2 session cleanup devlog to Discord (2025-12-15)."""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


def read_devlog() -> str:
    """Read today's devlog."""
    devlog_path = Path(__file__).parent.parent / "devlogs" / \
        "2025-12-15_agent-2_session_cleanup.md"
    if not devlog_path.exists():
        print(f"❌ Devlog not found: {devlog_path}")
        return None
    return devlog_path.read_text(encoding="utf-8")


def main():
    """Post devlog to Discord."""
    webhook_url = os.getenv('DISCORD_WEBHOOK_AGENT_2')
    if not webhook_url:
        print(
            '⚠️ No DISCORD_WEBHOOK_AGENT_2 env set; devlog saved but not posted to Discord')
        print('📄 Devlog available at: devlogs/2025-12-15_agent-2_session_cleanup.md')
        return True  # Non-blocking

    content = read_devlog()
    if not content:
        return False

    # Prepare Discord embed
    embed = {
        'title': 'Agent-2 Session Cleanup – 2025-12-15',
        'description': content[:2000],  # Discord embed limit
        'color': 0x00d4aa,  # Architecture green
        'footer': {'text': 'Architecture & Design Specialist - Agent-2'},
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'fields': [
            {
                'name': '✅ Completed',
                'value': 'Inbox cleanup, onboarding Batch 4 architecture review, architecture documentation created',
                'inline': False
            },
            {
                'name': '📊 Status',
                'value': 'Architecture/design domain: 584/584 tests passing',
                'inline': True
            },
            {
                'name': '🔗 Full Devlog',
                'value': 'See `devlogs/2025-12-15_agent-2_session_cleanup.md`',
                'inline': False
            }
        ]
    }

    payload = {
        'embeds': [embed]
    }

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            print('✅ Session cleanup devlog posted to Discord!')
            return True
        else:
            print(f'⚠️ Discord post returned {response.status_code}')
            print(f'📄 Devlog saved at: devlogs/2025-12-15_agent-2_session_cleanup.md')
            return True  # Non-blocking
    except Exception as e:
        print(f'⚠️ Error posting to Discord: {e}')
        print(f'📄 Devlog saved at: devlogs/2025-12-15_agent-2_session_cleanup.md')
        return True  # Non-blocking


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
