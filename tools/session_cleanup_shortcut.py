#!/usr/bin/env python3
"""
Session Cleanup Shortcut
========================

Lightweight helper to summarize session cleanup state for Agent-3.

<!-- SSOT Domain: infrastructure -->
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

PASSDOWN_PATH = Path("agent_workspaces/Agent-3/passdown.json")
STATUS_PATH = Path("agent_workspaces/Agent-3/status.json")


def load_json(path: Path) -> Dict[str, Any]:
    """Load JSON with sensible defaults."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def summarize() -> str:
    """Return a concise session cleanup summary."""
    passdown = load_json(PASSDOWN_PATH)
    status = load_json(STATUS_PATH)

    session_date = passdown.get("session_date", "unknown")
    summary_status = passdown.get("status", "unknown")
    missions = passdown.get("session_summary", {}).get("missions_complete", [])
    blockers = passdown.get("blockers", [])
    next_recs = passdown.get("next_session_recommendations", [])
    autonomous_progress = status.get("autonomous_progress", "n/a")

    lines = [
        f"Session date: {session_date} | Status: {summary_status}",
        f"Missions complete ({len(missions)}): " + "; ".join(missions) if missions else "Missions complete: none recorded",
        f"Blockers: {', '.join(blockers) if blockers else 'none'}",
        f"Next recommendations: {', '.join(next_recs[:3]) if next_recs else 'none'}",
        f"Autonomous progress: {autonomous_progress}",
    ]
    return "\n".join(lines)


def main() -> None:
    print("=== Session Cleanup Snapshot (Agent-3) ===")
    print(summarize())
    print("\nChecklist:")
    print("- Passdown updated")
    print("- Devlog written")
    print("- Swarm Brain entry added")
    print("- Discord post (manual if automation unavailable)")


if __name__ == "__main__":
    main()

