#!/usr/bin/env python3
"""
DEPRECATED:
This script is deprecated. Prefer using the canonical messaging CLI instead.

Equivalent CLI command (send to individual agents):
  python -m src.services.messaging_cli --agent <agent_id> -m "**🚨 RESUME DIRECTIVE - [your message]**" --type text --category a2c --priority urgent
  # Or use bulk mode:
  python -m src.services.messaging_cli --bulk -m "[your message]" --priority urgent

For A2A/A2C message formatting and reply instructions, see:
  src/core/messaging_template_texts.py (MessageCategory.A2A / MessageCategory.A2C templates)

This script is kept for backward compatibility only. New workflows should use messaging_cli.

---

Send Resume Directives to All Agents
Forces status updates and reactivates all agents

Mode-aware: Uses current agent mode to determine which agents to resume.
"""

from src.core.agent_mode_manager import get_active_agents
from pathlib import Path
from datetime import datetime
import uuid
import sys

# Add project root to path for imports
WORKSPACE_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

# Mode-aware: Get active agents from agent mode manager

RESUME_TEMPLATE = """# 🚨 CAPTAIN MESSAGE - RESUME DIRECTIVE

**From**: Captain Agent-4
**To**: {agent_id}
**Priority**: urgent
**Message ID**: {message_id}
**Timestamp**: {timestamp}

---

🚨 **RESUME DIRECTIVE - IMMEDIATE ACTION REQUIRED**

**Priority**: URGENT
**Status**: STATUS UPDATE + RESUME OPERATIONS

**{agent_id} - IMMEDIATE ACTION REQUIRED:**

**STEP 1: UPDATE STATUS.JSON** (DO THIS FIRST)
1. Open your `agent_workspaces/{agent_id}/status.json`
2. Update `last_updated` to current timestamp: `{current_time}`
3. Update `current_tasks` with your active work
4. Save the file

**STEP 2: RESUME OPERATIONS** (DO THIS SECOND)
1. Check your inbox for new assignments
2. Review your current tasks
3. Resume autonomous execution
4. Post devlog to Discord if you completed work

**STEP 3: POST DEVLOG** (IF YOU HAVE COMPLETED WORK)
```bash
python tools/devlog_manager.py post --agent {agent_id} --file <your_devlog_file>
```

**CRITICAL REQUIREMENTS:**
✅ Update status.json NOW (within 5 minutes)
✅ Resume autonomous operations
✅ Check inbox for assignments
✅ Post devlog if work completed

**WE. ARE. SWARM. AUTONOMOUS. POWERFUL. 🐝⚡🔥🚀**

---
*Message delivered via Unified Messaging Service*
"""


def send_resume_directive(agent_id: str) -> bool:
    """Send resume directive directly to agent inbox."""
    # Validate agent ID
    valid_agent_ids = {f"Agent-{i}" for i in range(1, 9)}
    if agent_id not in valid_agent_ids:
        print(
            f"❌ Invalid agent ID: '{agent_id}'. Must be one of: {', '.join(sorted(valid_agent_ids))}")
        return False

    inbox_dir = WORKSPACE_ROOT / "agent_workspaces" / agent_id / "inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)

    message_id = f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    timestamp = datetime.now().isoformat()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    message_content = RESUME_TEMPLATE.format(
        agent_id=agent_id,
        message_id=message_id,
        timestamp=timestamp,
        current_time=current_time
    )

    inbox_file = inbox_dir / \
        f"CAPTAIN_MESSAGE_RESUME_{timestamp.replace(':', '-').replace('.', '-')}_{message_id}.md"

    try:
        inbox_file.write_text(message_content, encoding='utf-8')
        print(f"✅ Resume directive sent to {agent_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to send to {agent_id}: {e}")
        return False


def main():
    """Send resume directives to all active agents (mode-aware)."""
    # Get active agents from current agent mode
    active_agents = get_active_agents()

    print("=" * 60)
    print("🚨 CAPTAIN RESUME DIRECTIVE DEPLOYMENT (MODE-AWARE)")
    print("=" * 60)
    print(
        f"Current Mode: Active agents ({len(active_agents)}): {', '.join(active_agents)}")
    print()

    results = {}
    for agent_id in active_agents:
        results[agent_id] = send_resume_directive(agent_id)

    print()
    print("=" * 60)
    print("📊 SUMMARY:")
    successful = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"   ✅ Successful: {successful}/{total}")
    print(f"   ❌ Failed: {total - successful}/{total}")

    if successful == total:
        print()
        print("🎉 ALL RESUME DIRECTIVES DEPLOYED!")
        print("🐝 WE. ARE. SWARM. AUTONOMOUS. POWERFUL. ⚡🔥🚀")

    return successful == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
