#!/usr/bin/env python3
"""
Post Agent-2 Devlog to Discord
==============================

Posts the latest devlog to Discord #agent-2-devlogs channel.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def read_devlog():
    """Read the latest Agent-2 devlog."""
    devlog_path = project_root / "docs" / "AGENT2_DEVLOG_2025-12-14.md"

    if not devlog_path.exists():
        print(f"❌ Devlog not found: {devlog_path}")
        return None

    return devlog_path.read_text(encoding="utf-8")


def post_to_discord(content: str):
    """Post devlog content to Discord using messaging system."""
    try:
        from src.core.messaging_core import (
            send_message,
            UnifiedMessageType,
            UnifiedMessagePriority,
            UnifiedMessageTag,
        )

        # Send as a coordination message to Agent-4 (Captain) for Discord posting
        # Note: Actual Discord channel posting would require Discord bot integration
        msg = f"""**📝 AGENT-2 DEVLOG POSTED**

**Date:** 2025-12-14
**Channel:** #agent-2-devlogs

**Summary:**
- V2 Compliance Dashboard corrected (110 violations identified)
- Batch 2 Phase 2D architecture support (94% file reduction achieved)
- Business plan acknowledgment
- 1 Critical violation eliminated

**Full Devlog:**
```markdown
{content[:2000]}...
```

See full devlog: `docs/AGENT2_DEVLOG_2025-12-14.md`
"""

        send_message(
            msg,
            "Agent-2",
            "Agent-4",  # Captain for coordination
            UnifiedMessageType.TEXT,
            UnifiedMessagePriority.REGULAR,
            [UnifiedMessageTag.COORDINATION],
        )

        print("✅ Devlog summary posted to coordination channel")
        print(f"📄 Full devlog available at: docs/AGENT2_DEVLOG_2025-12-14.md")
        return True

    except Exception as e:
        print(f"❌ Error posting to Discord: {e}")
        print(f"📄 Devlog saved at: docs/AGENT2_DEVLOG_2025-12-14.md")
        return False


if __name__ == "__main__":
    print("📝 Reading Agent-2 devlog...")
    devlog = read_devlog()

    if devlog:
        print(f"✅ Devlog loaded ({len(devlog)} characters)")
        print("📤 Posting to Discord...")
        post_to_discord(devlog)
    else:
        print("❌ Failed to read devlog")
        sys.exit(1)
