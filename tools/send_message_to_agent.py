#!/usr/bin/env python3
"""
DEPRECATED:
This script is deprecated. Prefer using the canonical messaging CLI instead.

Equivalent CLI command (for A2A/A2C messages):
  python -m src.services.messaging_cli --agent <agent_id> -m "<your message>" --type text --category a2a
  # For A2C to Captain:
  python -m src.services.messaging_cli --agent Agent-4 -m "<your message>" --type text --category a2c

For A2A/A2C message formatting and reply instructions, see:
  src/core/messaging_template_texts.py (MessageCategory.A2A / MessageCategory.A2C templates)

This script is kept for backward compatibility only. New workflows should use messaging_cli.
"""

"""Quick script to send a message to an agent."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.core.messaging_core import UnifiedMessagingCore, UnifiedMessage, UnifiedMessagePriority, UnifiedMessageType

    def send_message(agent_id: str, message: str):
        """Send message to agent."""
        core = UnifiedMessagingCore()
        msg = UnifiedMessage(
            content=message,
            sender="Agent-3",
            recipient=agent_id,
            message_type=UnifiedMessageType.TEXT,
            priority=UnifiedMessagePriority.NORMAL,
            tags=[],
            metadata={},
        )
        result = core.send_message(msg)
        print(f"Message sent: {result}")
        return result
except Exception as e:
    print(f"Error importing messaging core: {e}")
    print("Using inbox fallback method...")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python send_message_to_agent.py <agent_id> <message>")
        sys.exit(1)

    agent_id = sys.argv[1]
    message = " ".join(sys.argv[2:])

    # Validate agent ID
    valid_agent_ids = {f"Agent-{i}" for i in range(1, 9)}
    if agent_id not in valid_agent_ids:
        print(
            f"❌ Invalid agent ID: '{agent_id}'. Must be one of: {', '.join(sorted(valid_agent_ids))}")
        sys.exit(1)

    try:
        send_message(agent_id, message)
    except Exception as e:
        # Fallback: write to inbox
        print(f"Messaging core failed: {e}")
        print("Writing to inbox as fallback...")
        inbox_path = Path(f"agent_workspaces/{agent_id}/inbox")
        inbox_path.mkdir(parents=True, exist_ok=True)
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        msg_file = inbox_path / \
            f"CAPTAIN_MESSAGE_{timestamp}_agent3_ftp_ready.md"
        msg_file.write_text(f"""# 🚨 CAPTAIN MESSAGE - TEXT

**From**: Agent-3
**To**: {agent_id}
**Priority**: normal
**Message ID**: msg_{timestamp}_ftp_ready
**Timestamp**: {datetime.now().isoformat()}

---

{message}

---

*Message delivered via Unified Messaging Service*
""")
        print(f"✅ Message written to {msg_file}")
