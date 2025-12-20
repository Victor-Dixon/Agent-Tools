#!/usr/bin/env python3
"""
DEPRECATED:
This script is deprecated. Prefer using the canonical messaging CLI instead.

Equivalent CLI command (A2A self-message or A2C to Agent-4):
  python -m src.services.messaging_cli --agent Agent-2 -m "**WordPress Blog Audit - COMPLETE ✅** [your message]" --type text --category a2a
  # OR for completion report to Captain:
  python -m src.services.messaging_cli --agent Agent-4 -m "[completion summary]" --type text --category a2c

For A2A/A2C message formatting and reply instructions, see:
  src/core/messaging_template_texts.py (MessageCategory.A2A / MessageCategory.A2C templates)

This script is kept for backward compatibility only. New workflows should use messaging_cli.
"""

"""Send WordPress audit completion status to Discord."""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


status_message = """**WordPress Blog Audit - COMPLETE ✅**

**Task:** Improve WordPress blogs - check duplicates & ensure initial posts

**Findings:**
1. **dadudekc.com**: Found duplicate CSS issue (not duplicate posts)
   - Both posts have identical embedded CSS (4,439 chars)
   - Content is different (Swarm vs Dream.os)
   - Fix: Move CSS to theme stylesheet

2. **Initial Posts**: 6/7 sites missing "About This Site" posts
   - Content prepared for all sites ✅
   - Ready to publish (needs WordPress credentials)

**Tools Created:**
• `tools/audit_wordpress_blogs.py` - Full audit tool
• `tools/analyze_and_fix_dadudekc_duplicates.py` - CSS analysis

**Report:** `docs/blog/WORDPRESS_BLOG_AUDIT_REPORT_2025-12-13.md`

**Next Steps:**
1. Configure WordPress credentials (`.deploy_credentials/blogging_api.json`)
2. Run: `python tools/audit_wordpress_blogs.py --all-sites --create-initial-posts`
3. Fix dadudekc.com CSS (move to theme, remove from posts)

**Status:** ✅ Audit complete, 🟡 Credentials needed for fixes"""

if __name__ == "__main__":
    try:
        result = send_message(
            content=status_message,
            sender="Agent-2",
            recipient="Agent-2",
            message_type=UnifiedMessageType.TEXT,
            priority=UnifiedMessagePriority.REGULAR,
            tags=[UnifiedMessageTag.SYSTEM, UnifiedMessageTag.COORDINATION],
        )
        if result:
            print("✅ Status update sent to Discord")
            sys.exit(0)
        else:
            print("❌ Failed to send status")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
