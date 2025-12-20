"""
Captain's Tool: Quick Log Update
=================================

Quickly update Captain's log with key events.

Usage: python tools/captain_update_log.py --cycle 3 --event "Agent-1 completed task"

Author: Agent-4 (Captain)
Date: 2025-10-13
"""

import argparse
from datetime import datetime
from pathlib import Path


def update_captains_log(cycle: int, event: str, points: int = 0, agent: str = None):
    """Add entry to Captain's log."""

    log_file = Path(f"agent_workspaces/Agent-4/CAPTAINS_LOG_CYCLE_{cycle:03d}.md")

    timestamp = datetime.now().strftime("%H:%M:%S")

    entry = f"\n## [{timestamp}] {event}\n"
    if agent:
        entry += f"**Agent**: {agent}\n"
    if points > 0:
        entry += f"**Points**: {points}\n"
    entry += f"**Logged**: {datetime.now().isoformat()}\n"

    # Append to log
    if log_file.exists():
        with open(log_file, "a") as f:
            f.write(entry)
        print(f"✅ Log updated: {log_file}")
    else:
        print(f"⚠️  Log file not found: {log_file}")
        print("Creating new log...")

        with open(log_file, "w") as f:
            f.write(f"# 📓 CAPTAIN'S LOG - CYCLE {cycle:03d}\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write("**Captain**: Agent-4\n\n")
            f.write(entry)
        print(f"✅ New log created: {log_file}")

    return entry


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Captain's log")
    parser.add_argument("--cycle", "-c", type=int, required=True, help="Cycle number")
    parser.add_argument("--event", "-e", required=True, help="Event description")
    parser.add_argument("--points", "-p", type=int, default=0, help="Points involved")
    parser.add_argument("--agent", "-a", help="Agent involved")

    args = parser.parse_args()

    update_captains_log(args.cycle, args.event, args.points, args.agent)
