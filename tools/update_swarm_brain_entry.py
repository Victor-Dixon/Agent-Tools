#!/usr/bin/env python3
"""Helper script to add entries to Swarm Brain knowledge base."""
import json
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
kb_path = project_root / "swarm_brain" / "knowledge_base.json"

with open(kb_path, 'r', encoding='utf-8') as f:
    kb = json.load(f)

# Entry 1: Message Delivery Verification Pattern
entry_id_1 = f"kb-{kb['stats']['total_entries'] + 1}"
kb['entries'][entry_id_1] = {
    "id": entry_id_1,
    "title": "Message Delivery Verification Pattern",
    "content": "PyAutoGUI delivery success does not guarantee inbox file creation. Always verify delivery by checking inbox file existence and content after PyAutoGUI operations.\n\n**Solution:** Post-delivery verification in message_queue_processor\n- After PyAutoGUI delivery, verify inbox file exists\n- Check file size > 0 to ensure content written\n- Retry if verification fails\n- Exponential backoff: 5s, 15s, 45s (3 attempts max)\n\n**Key Insight:** Delivery verification is critical - never assume PyAutoGUI success means file was created.\n\n**Files:** src/core/message_queue_processor.py, src/utils/inbox_utility.py",
    "author": "Agent-4",
    "category": "learning",
    "tags": ["messaging", "delivery", "verification", "reliability", "pattern"],
    "timestamp": datetime.now().isoformat(),
    "metadata": {}
}

kb['stats']['total_entries'] += 1
kb['stats']['contributors']['Agent-4'] = kb['stats']['contributors'].get('Agent-4', 0) + 1

# Entry 2: Discord Bot Reconnection Loop Pattern
entry_id_2 = f"kb-{kb['stats']['total_entries'] + 1}"
kb['entries'][entry_id_2] = {
    "id": entry_id_2,
    "title": "Discord Bot Reconnection Loop Pattern",
    "content": "Early returns in reconnection loops cause silent failures. Use intentional shutdown flags to distinguish user-initiated shutdowns from unexpected disconnects.\n\n**Problem:** Bot exits silently on disconnect without reconnection attempts\n\n**Solution:**\n- Remove early returns after bot.start()\n- Add _intentional_shutdown flag set on KeyboardInterrupt or explicit shutdown\n- Only exit reconnection loop if flag is True\n- Enhanced exception handling for KeyboardInterrupt, LoginFailure, PrivilegedIntentsRequired\n\n**Key Insight:** Reconnection loops must distinguish intentional vs. unexpected shutdowns using flags, not early returns.\n\n**Files:** src/discord_commander/unified_discord_bot.py",
    "author": "Agent-4",
    "category": "learning",
    "tags": ["discord", "bot", "reconnection", "reliability", "pattern"],
    "timestamp": datetime.now().isoformat(),
    "metadata": {}
}

kb['stats']['total_entries'] += 1
kb['stats']['contributors']['Agent-4'] = kb['stats']['contributors'].get('Agent-4', 0) + 1

# Entry 3: Template-Based Force Multiplier Enforcement
entry_id_3 = f"kb-{kb['stats']['total_entries'] + 1}"
kb['entries'][entry_id_3] = {
    "id": entry_id_3,
    "title": "Template-Based Force Multiplier Enforcement",
    "content": "Template-based enforcement effectively drives swarm coordination behavior. Prominent coordination checklists in S2A templates can mandate force multiplier protocols.\n\n**Solution:** Enhanced STALL_RECOVERY template with mandatory coordination check\n- Added 5-question checklist that MUST be answered before solo work\n- Made delegation the default choice (80% of time, \"WHEN IN DOUBT, DELEGATE\")\n- Daily coordination quota tracking (1+ messages/day minimum, 2-4 ideal)\n- Force multiplier emphasis throughout template\n- Anti-pattern warnings about isolated work\n\n**Key Insight:** Template-based enforcement at the message level drives agent behavior more effectively than guidelines alone.\n\n**Files:** src/core/messaging_template_texts.py",
    "author": "Agent-4",
    "category": "learning",
    "tags": ["coordination", "force-multiplier", "templates", "swarm", "protocol"],
    "timestamp": datetime.now().isoformat(),
    "metadata": {}
}

kb['stats']['total_entries'] += 1
kb['stats']['contributors']['Agent-4'] = kb['stats']['contributors'].get('Agent-4', 0) + 1

# Update last_updated
kb['last_updated'] = datetime.now().isoformat()

# Write back
with open(kb_path, 'w', encoding='utf-8') as f:
    json.dump(kb, f, indent=2)

print(f"✅ Added 3 entries to Swarm Brain: {entry_id_1}, {entry_id_2}, {entry_id_3}")
print(f"   Total entries: {kb['stats']['total_entries']}")
print(f"   Agent-4 contributions: {kb['stats']['contributors']['Agent-4']}")



