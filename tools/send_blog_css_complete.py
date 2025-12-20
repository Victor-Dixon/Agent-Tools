#!/usr/bin/env python3
"""
DEPRECATED:
This script is deprecated. Prefer using the canonical messaging CLI instead.

Equivalent CLI command (A2A self-report or A2C to Agent-4):
  python -m src.services.messaging_cli --agent Agent-2 -m "**✅ Blog CSS Enhancement Complete - [your message]**" --type text --category a2a
  # OR to Agent-4:
  python -m src.services.messaging_cli --agent Agent-4 -m "[your message]" --type text --category a2c

For A2A/A2C message formatting and reply instructions, see:
  src/core/messaging_template_texts.py (MessageCategory.A2A / MessageCategory.A2C templates)

This script is kept for backward compatibility only. New workflows should use messaging_cli.
"""

"""Send blog CSS enhancement completion summary."""

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


msg = """**✅ Blog CSS Enhancement Complete**

**Improvements:**
• Enhanced WordPress blog CSS with dark theme support
• Added CSS variables for theme management
• Improved typography: 17px font, 1.8 line height
• Better contrast: Primary #e8e8e8, secondary #b8b8b8
• Blue accent (#4a9eff) for H2 headings
• Enhanced code blocks, blockquotes, tables
• Light theme fallback support
• Mobile-responsive improvements

**Files Updated:**
• docs/blog/dadudekc_blog_css_for_theme.css (cleaned + enhanced)
• temp_repos/Auto_Blogger/autoblogger/templates/blog_template.html
• CSS added to WordPress Customizer

**Status:** ✅ Complete - Enhanced CSS committed"""

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
