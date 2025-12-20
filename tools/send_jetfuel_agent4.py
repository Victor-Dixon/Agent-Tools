#!/usr/bin/env python3
"""
DEPRECATED:
This script is deprecated. Prefer using the canonical messaging CLI instead.

Equivalent CLI command (A2C to Agent-4):
  python -m src.services.messaging_cli --agent Agent-4 -m "**🚀 JET FUEL PROMPT - [your message]**" --type text --category a2c

For A2A/A2C message formatting and reply instructions, see:
  src/core/messaging_template_texts.py (MessageCategory.A2A / MessageCategory.A2C templates)

This script is kept for backward compatibility only. New workflows should use messaging_cli.
"""

"""Jet fuel prompt to Agent-4 for perpetual motion."""

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


msg = """**🚀 JET FUEL PROMPT - DEVELOPMENT CONTINUITY**

**From:** Agent-2 → Agent-4 (Main Bilateral Coordination Partner)

**Status Update:**
✅ Completed test architecture review for Agent-1
✅ Blog standardization cycle complete (5 posts)
✅ Text contrast fixes applied

**Next Development Cycle:**
- Continue V2 compliance architecture reviews
- Monitor Agent-1 test infrastructure improvements
- Ready for next priority task assignment

**Momentum:** Swarm in perpetual motion, ready for next cycle

🐝 WE. ARE. SWARM. IN. PERPETUAL. MOTION. ⚡🔥🚀"""

send_message(
    content=msg,
    sender="Agent-2",
    recipient="Agent-4",
    message_type=UnifiedMessageType.TEXT,
    priority=UnifiedMessagePriority.REGULAR,
    tags=[UnifiedMessageTag.COORDINATION, UnifiedMessageTag.SYSTEM],
)
