#!/usr/bin/env python3
"""Update Swarm Brain with session cleanup entries."""
import json
import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
kb_path = project_root / "swarm_brain" / "knowledge_base.json"

with open(kb_path, 'r', encoding='utf-8') as f:
    kb = json.load(f)

# Entry 1: Backward Compatibility Shim Pattern
entry_id_1 = f"kb-{kb['stats']['total_entries'] + 1}"
kb['entries'][entry_id_1] = {
    "id": entry_id_1,
    "title": "Backward Compatibility Shim Pattern for V2 Compliance",
    "content": "Backward compatibility shims enable massive refactoring (94% file reduction) while preserving functionality. Key pattern: Create minimal shim class that delegates all methods to extracted managers. Implementation: Initialize managers in __init__, delegate all public methods, preserve all public APIs. Result: 2,695 lines → 158 lines (96 line bot class) while maintaining 100% backward compatibility. Files: src/discord_commander/unified_discord_bot.py",
    "author": "Agent-1",
    "category": "learning",
    "tags": ["refactoring", "v2-compliance", "architecture", "pattern", "backward-compatibility"],
    "timestamp": datetime.now().isoformat(),
    "metadata": {}
}

kb['stats']['total_entries'] += 1
kb['stats']['contributors']['Agent-1'] = kb['stats']['contributors'].get('Agent-1', 0) + 1

# Entry 2: Main Function Extraction
entry_id_2 = f"kb-{kb['stats']['total_entries'] + 1}"
kb['entries'][entry_id_2] = {
    "id": entry_id_2,
    "title": "Main Function Extraction for V2 Compliance",
    "content": "Extracting main() functions to separate files helps achieve V2 compliance for large files. Pattern: Move main() to separate runner file (e.g., bot_runner.py), keep core class in original file. Benefits: Reduces file size, separates entry point from core logic, maintains backward compatibility. Implementation: Original file imports from runner, runner imports from original. Result: 365 lines → 158 lines (main extracted to 209 line runner). Files: src/discord_commander/unified_discord_bot.py, src/discord_commander/bot_runner.py",
    "author": "Agent-1",
    "category": "learning",
    "tags": ["v2-compliance", "refactoring", "architecture", "pattern"],
    "timestamp": datetime.now().isoformat(),
    "metadata": {}
}

kb['stats']['total_entries'] += 1
kb['stats']['contributors']['Agent-1'] = kb['stats']['contributors'].get('Agent-1', 0) + 1

# Entry 3: Circular Dependency Resolution
entry_id_3 = f"kb-{kb['stats']['total_entries'] + 1}"
kb['entries'][entry_id_3] = {
    "id": entry_id_3,
    "title": "Circular Dependency Resolution in Lifecycle Methods",
    "content": "Lifecycle methods that call bot methods can create circular dependencies. Problem: lifecycle.close() calls bot.close(), which delegates back to lifecycle.close(). Solution: lifecycle.close() sets shutdown flag only, bot.close() calls lifecycle.close() then super().close(). Key insight: Use flags to distinguish intentional vs. automatic shutdowns, prevent infinite recursion through careful delegation design. Files: src/discord_commander/lifecycle/bot_lifecycle.py, src/discord_commander/unified_discord_bot.py",
    "author": "Agent-1",
    "category": "learning",
    "tags": ["architecture", "circular-dependency", "lifecycle", "pattern"],
    "timestamp": datetime.now().isoformat(),
    "metadata": {}
}

kb['stats']['total_entries'] += 1
kb['stats']['contributors']['Agent-1'] = kb['stats']['contributors'].get('Agent-1', 0) + 1

# Update last_updated
kb['last_updated'] = datetime.now().isoformat()

# Write back
with open(kb_path, 'w', encoding='utf-8') as f:
    json.dump(kb, f, indent=2)

print(f"✅ Added 3 entries to Swarm Brain: {entry_id_1}, {entry_id_2}, {entry_id_3}")
print(f"   Total entries: {kb['stats']['total_entries']}")
print(f"   Agent-1 contributions: {kb['stats']['contributors']['Agent-1']}")

