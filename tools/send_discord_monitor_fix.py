#!/usr/bin/env python3
"""
DEPRECATED:
This script is deprecated. Prefer using the canonical messaging CLI instead.

Equivalent CLI command (A2A self-report or A2C to Agent-4):
  python -m src.services.messaging_cli --agent Agent-2 -m "**✅ Discord Monitor Button Fix - [your message]**" --type text --category a2a
  # OR to Agent-4:
  python -m src.services.messaging_cli --agent Agent-4 -m "[your message]" --type text --category a2c

For A2A/A2C message formatting and reply instructions, see:
  src/core/messaging_template_texts.py (MessageCategory.A2A / MessageCategory.A2C templates)

This script is kept for backward compatibility only. New workflows should use messaging_cli.
"""

"""Send Discord monitor fix completion to Discord."""

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


msg = """**✅ Discord Monitor Button Fix - COMPLETE**

**Task:** Fix !monitor discord.view button - add start/stop functionality

**Issue:** Button only showed status, couldn't start/stop monitor

**Fix Applied:**
• Created MonitorControlView class with Start/Stop buttons
• Updated show_monitor_control() to use interactive view
• Buttons now allow starting/stopping monitor directly from UI

**Files Changed:**
• src/discord_commander/views/main_control_panel_view.py

**Status:** ✅ Complete - Monitor button now has functional start/stop controls"""

if __name__ == "__main__":
    try:
        result = send_message(
            content=msg, sender="Agent-2", recipient="Agent-2",
            message_type=UnifiedMessageType.TEXT,
            priority=UnifiedMessagePriority.REGULAR,
            tags=[UnifiedMessageTag.SYSTEM, UnifiedMessageTag.COORDINATION],
        )
        print("✅ Sent" if result else "❌ Failed")
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
