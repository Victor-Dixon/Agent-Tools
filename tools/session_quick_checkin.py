#!/usr/bin/env python3
"""
Session Quick Check-in

Broadcasts a short sync request to all agents with a standard template:
status, next_action, blockers, % complete.

Usage:
  python tools/session_quick_checkin.py
  python tools/session_quick_checkin.py --message "Custom message"
"""

import argparse
import subprocess
import sys
from pathlib import Path


AGENTS = ["Agent-1", "Agent-2", "Agent-3", "Agent-5", "Agent-6", "Agent-7", "Agent-8"]

DEFAULT_MESSAGE = (
    "Quick sync check-in: please reply this cycle with (1) current status, "
    "(2) top next_action, (3) blockers, (4) % complete on your primary mission. "
    "Priority: NORMAL. Keep it short (2-3 lines). 🐝⚡"
)


def send_message(agent: str, message: str) -> int:
    cmd = [
        sys.executable,
        "-m",
        "src.services.messaging_cli",
        "-a",
        agent,
        "-m",
        message,
    ]
    try:
        return subprocess.call(cmd, cwd=Path(__file__).resolve().parents[1])
    except Exception as exc:  # pragma: no cover - defensive
        print(f"⚠️ Failed to send to {agent}: {exc}")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Broadcast quick sync check-in to all agents.")
    parser.add_argument("--message", "-m", default=DEFAULT_MESSAGE, help="Custom message to send")
    args = parser.parse_args()

    failures = 0
    for agent in AGENTS:
        rc = send_message(agent, args.message)
        if rc != 0:
            failures += 1

    if failures:
        print(f"Completed with {failures} failures.")
        return 1

    print("✅ Sync check-in broadcast sent to all agents.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

