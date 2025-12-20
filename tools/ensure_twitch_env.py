#!/usr/bin/env python3
"""
Quick preflight checker for Twitch bot credentials.

Usage:
    python tools/ensure_twitch_env.py

Checks required environment variables and prints next-step guidance.
"""

import os
import sys
from textwrap import dedent


REQUIRED_VARS = [
    "TWITCH_CHANNEL",
    "TWITCH_ACCESS_TOKEN",  # expected format: oauth:xxxxxxxxxxxx
]

OPTIONAL_VARS = [
    "TWITCH_BOT_USERNAME",  # falls back to channel if missing
]


def main() -> int:
    missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
    warnings = []

    token = os.getenv("TWITCH_ACCESS_TOKEN") or ""
    if token and not token.startswith("oauth:"):
        warnings.append("TWITCH_ACCESS_TOKEN does not start with 'oauth:'")

    if missing:
        print("❌ Missing required Twitch env vars:")
        for var in missing:
            print(f"   - {var}")
        print(
            "\nAdd them to .env (repo root) or set in your shell:\n"
            "  TWITCH_CHANNEL=<channel_name>\n"
            "  TWITCH_ACCESS_TOKEN=oauth:<token>\n"
            "  TWITCH_BOT_USERNAME=<bot_username>  # optional; defaults to channel"
        )
        return 1

    print("✅ Twitch env looks ready:")
    print(f"   TWITCH_CHANNEL       = {os.getenv('TWITCH_CHANNEL')}")
    print(f"   TWITCH_BOT_USERNAME  = {os.getenv('TWITCH_BOT_USERNAME') or '<default: channel>'}")
    print(f"   TWITCH_ACCESS_TOKEN  = {token[:12]}..." if token else "   TWITCH_ACCESS_TOKEN missing")

    if warnings:
        print("\n⚠️ Warnings:")
        for w in warnings:
            print(f" - {w}")
        return 1

    print("\nNext:")
    print("  1) Run: python tools/test_twitch_ping_pong.py")
    print("  2) Then: python tools/START_CHAT_BOT_NOW.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())

