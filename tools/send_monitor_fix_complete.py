#!/usr/bin/env python3
"""
DEPRECATED:
This script is deprecated. Prefer using the canonical messaging CLI instead.

Equivalent CLI command (A2A self-report or A2C to Agent-4):
  python -m src.services.messaging_cli --agent Agent-2 -m "**✅ Discord Monitor Button Fix Complete - [your message]**" --type text --category a2a
  # OR to Agent-4:
  python -m src.services.messaging_cli --agent Agent-4 -m "[your message]" --type text --category a2c

For A2A/A2C message formatting and reply instructions, see:
  src/core/messaging_template_texts.py (MessageCategory.A2A / MessageCategory.A2C templates)

This script is kept for backward compatibility only. New workflows should use messaging_cli.
"""

"""Send monitor button fix completion."""

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


msg = """**✅ Discord Monitor Button Fix Complete**

**Task:** Fix !monitor discord.view button - add start/stop functionality

**Issue:** Monitor button only showed status, referenced !monitor command but no start/stop buttons

**Fix:** Created MonitorControlView with interactive buttons
• Start Monitor button (▶️) - Starts status monitor
• Stop Monitor button (⏸️) - Stops status monitor
• Refresh Status button (🔄) - Refreshes monitor status

**Files Modified:**
• src/discord_commander/views/main_control_panel_view.py
  - Added MonitorControlView class with start/stop/refresh buttons
  - Updated show_monitor_control() to use new view

**Status:** ✅ Complete - Users can now start/stop monitor directly from button

Agent-2: Monitor button fix"""

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
