#!/usr/bin/env python3
"""
Discord Tools - Agent Toolbelt V2
==================================

Discord bot and integration tools for agents.
Created based on Agent-3 Discord Commander session.

Author: Agent-3 (Infrastructure & DevOps) - Toolbelt Expansion
License: MIT
"""

import logging
import subprocess
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter

logger = logging.getLogger(__name__)


class DiscordBotHealthTool(IToolAdapter):
    """Check if Discord bot is running and healthy."""

    def get_name(self) -> str:
        return "discord_health"

    def get_description(self) -> str:
        return "Check Discord Commander bot health and status"

    def execute(self, **kwargs) -> dict[str, Any]:
        """Check Discord bot health."""
        try:
            # Check if process is running
            result = subprocess.run(
                ["powershell", "-Command", "Get-Process python | Select-String discord"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            running = result.returncode == 0 and "discord" in result.stdout.lower()

            # Check for startup message in logs
            log_exists = False
            try:
                # Look for recent log entries
                log_exists = Path("logs/unified.log").exists()
            except:
                pass

            return {
                "success": True,
                "bot_running": running,
                "logs_available": log_exists,
                "status": "HEALTHY" if running else "NOT_RUNNING",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class DiscordBotStartTool(IToolAdapter):
    """Start Discord Commander bot."""

    def get_name(self) -> str:
        return "discord_start"

    def get_description(self) -> str:
        return "Start Discord Commander bot in background"

    def execute(self, **kwargs) -> dict[str, Any]:
        """Start Discord bot."""
        try:
            # Start bot in background
            if subprocess.sys.platform == "win32":
                subprocess.Popen(
                    ["python", "src/discord_commander/unified_discord_bot.py"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
            else:
                subprocess.Popen(
                    ["python", "src/discord_commander/unified_discord_bot.py"],
                    start_new_session=True,
                )

            return {
                "success": True,
                "message": "Discord Commander started in background",
                "instructions": "Check Discord for startup message. Use !gui to access messaging interface.",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class DiscordTestMessageTool(IToolAdapter):
    """Send test message via Discord bot."""

    def get_name(self) -> str:
        return "discord_test"

    def get_description(self) -> str:
        return "Send test message to verify Discord integration"

    def execute(self, **kwargs) -> dict[str, Any]:
        """Send test message."""
        try:
            agent = kwargs.get("agent", "Agent-1")
            message = kwargs.get("message", "Test message from Discord Commander")

            # Use messaging CLI
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "src.services.messaging_cli",
                    "--agent",
                    agent,
                    "--message",
                    message,
                    "--priority",
                    "regular",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Check for success indicators
            output = result.stdout + result.stderr
            success = "Message sent to" in output or "Coordinates validated" in output

            return {
                "success": success,
                "agent": agent,
                "message_sent": success,
                "output": output[:500] if output else "No output",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


__all__ = ["DiscordBotHealthTool", "DiscordBotStartTool", "DiscordTestMessageTool"]
