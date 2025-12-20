#!/usr/bin/env python3
"""
Discord Webhook Management Tools - Agent Toolbelt V2
====================================================

Tools for agents to create, manage, and configure Discord webhooks programmatically.
Enables full Discord server control for automated agent operations.

Author: Agent-7 (Web Development Specialist) - Webhook Management
License: MIT
"""

import logging
import os
from pathlib import Path
from typing import Any, Optional
import json

from ..adapters.base_adapter import IToolAdapter

logger = logging.getLogger(__name__)

# Discord imports (optional)
try:
    import discord
    from discord.ext import commands
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    logger.warning("discord.py not available - webhook tools limited")


class CreateWebhookTool(IToolAdapter):
    """Create a Discord webhook for a specific channel."""

    def get_name(self) -> str:
        return "create_discord_webhook"

    def get_description(self) -> str:
        return "Create a Discord webhook for automated posting to a specific channel"

    def execute(self, **kwargs) -> dict[str, Any]:
        """
        Create Discord webhook.
        
        Args:
            channel_id: Discord channel ID (required)
            webhook_name: Name for the webhook (default: "Agent Webhook")
            avatar_url: Optional avatar URL for webhook
            save_to_config: Save webhook to config file (default: True)
            config_key: Key name in config (default: "DISCORD_WEBHOOK_URL")
        
        Returns:
            dict with webhook_url, webhook_id, and success status
        """
        if not DISCORD_AVAILABLE:
            return {
                "success": False,
                "error": "discord.py not installed. Run: pip install discord.py"
            }

        channel_id = kwargs.get("channel_id")
        webhook_name = kwargs.get("webhook_name", "Agent Webhook")
        avatar_url = kwargs.get("avatar_url")
        save_to_config = kwargs.get("save_to_config", True)
        config_key = kwargs.get("config_key", "DISCORD_WEBHOOK_URL")

        if not channel_id:
            return {"success": False, "error": "channel_id is required"}

        try:
            # This needs to be called from an async context with bot
            # For now, provide manual instructions
            return {
                "success": False,
                "error": "Direct webhook creation requires async bot context",
                "instructions": self._get_creation_instructions(channel_id, webhook_name),
                "alternative": "Use ListWebhooksTool to see existing webhooks or create manually in Discord"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_creation_instructions(self, channel_id: str, webhook_name: str) -> str:
        """Get manual creation instructions."""
        return f"""
To create webhook manually:
1. Right-click on channel (ID: {channel_id})
2. Select 'Edit Channel' → 'Integrations' → 'Webhooks'
3. Click 'New Webhook'
4. Name it: {webhook_name}
5. Copy the webhook URL
6. Use SaveWebhookTool to save it to config

Or use the Discord bot command:
!create_webhook {channel_id} {webhook_name}
"""


class ListWebhooksTool(IToolAdapter):
    """List all webhooks in the Discord server."""

    def get_name(self) -> str:
        return "list_discord_webhooks"

    def get_description(self) -> str:
        return "List all Discord webhooks in the server for discovery and management"

    def execute(self, **kwargs) -> dict[str, Any]:
        """
        List Discord webhooks.
        
        Args:
            channel_id: Optional - filter by specific channel
            show_urls: Include webhook URLs in output (default: False for security)
        
        Returns:
            dict with list of webhooks
        """
        if not DISCORD_AVAILABLE:
            return {
                "success": False,
                "error": "discord.py not installed"
            }

        # Load from config instead
        webhooks = self._load_webhooks_from_config()
        
        return {
            "success": True,
            "webhooks": webhooks,
            "count": len(webhooks),
            "note": "Loaded from local config. Use Discord bot command !list_webhooks for live data"
        }

    def _load_webhooks_from_config(self) -> list[dict]:
        """Load webhooks from config files."""
        webhooks = []
        
        # Check .env file
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if "WEBHOOK" in line and "=" in line:
                        key, value = line.strip().split("=", 1)
                        if value and not value.startswith("#"):
                            webhooks.append({
                                "name": key,
                                "source": ".env",
                                "url_preview": value[:50] + "..." if len(value) > 50 else value
                            })
        
        # Check config files
        config_dir = Path("config")
        if config_dir.exists():
            for config_file in config_dir.glob("*discord*.json"):
                try:
                    with open(config_file) as f:
                        config = json.load(f)
                        # Find webhook URLs in config
                        self._extract_webhooks_from_dict(config, webhooks, config_file.name)
                except:
                    pass
        
        return webhooks

    def _extract_webhooks_from_dict(self, data: dict, webhooks: list, source: str):
        """Recursively extract webhook URLs from config dict."""
        for key, value in data.items():
            if isinstance(value, dict):
                self._extract_webhooks_from_dict(value, webhooks, source)
            elif isinstance(value, str) and "discord.com/api/webhooks/" in value:
                webhooks.append({
                    "name": key,
                    "source": source,
                    "url_preview": value[:50] + "..."
                })


class SaveWebhookTool(IToolAdapter):
    """Save webhook URL to configuration."""

    def get_name(self) -> str:
        return "save_discord_webhook"

    def get_description(self) -> str:
        return "Save a Discord webhook URL to .env or config file for automated use"

    def execute(self, **kwargs) -> dict[str, Any]:
        """
        Save webhook URL to config.
        
        Args:
            webhook_url: Discord webhook URL (required)
            config_key: Environment variable name (default: DISCORD_WEBHOOK_URL)
            target: Where to save - "env" or "config" (default: env)
            config_file: Config file path if target=config
        
        Returns:
            dict with success status and saved location
        """
        webhook_url = kwargs.get("webhook_url")
        config_key = kwargs.get("config_key", "DISCORD_WEBHOOK_URL")
        target = kwargs.get("target", "env")
        config_file = kwargs.get("config_file")

        if not webhook_url:
            return {"success": False, "error": "webhook_url is required"}

        if not webhook_url.startswith("https://discord.com/api/webhooks/"):
            return {"success": False, "error": "Invalid Discord webhook URL format"}

        try:
            if target == "env":
                return self._save_to_env(config_key, webhook_url)
            elif target == "config":
                return self._save_to_config(config_file, config_key, webhook_url)
            else:
                return {"success": False, "error": f"Invalid target: {target}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _save_to_env(self, key: str, webhook_url: str) -> dict[str, Any]:
        """Save webhook to .env file."""
        env_path = Path(".env")
        
        # Read existing .env
        existing_lines = []
        key_exists = False
        
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    if line.strip().startswith(f"{key}="):
                        existing_lines.append(f"{key}={webhook_url}\n")
                        key_exists = True
                    else:
                        existing_lines.append(line)
        
        # Add new key if it doesn't exist
        if not key_exists:
            existing_lines.append(f"\n# Discord Webhook - Added by agent\n")
            existing_lines.append(f"{key}={webhook_url}\n")
        
        # Write back to .env
        with open(env_path, 'w') as f:
            f.writelines(existing_lines)
        
        return {
            "success": True,
            "saved_to": str(env_path),
            "config_key": key,
            "action": "updated" if key_exists else "created",
            "note": "Restart services to load new webhook URL"
        }

    def _save_to_config(self, config_file: Optional[str], key: str, 
                       webhook_url: str) -> dict[str, Any]:
        """Save webhook to JSON config file."""
        if not config_file:
            config_file = "config/discord_config.json"
        
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing config
        config = {}
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
        
        # Update webhook
        config[key] = webhook_url
        
        # Save config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {
            "success": True,
            "saved_to": str(config_path),
            "config_key": key
        }


class TestWebhookTool(IToolAdapter):
    """Test a Discord webhook by sending a test message."""

    def get_name(self) -> str:
        return "test_discord_webhook"

    def get_description(self) -> str:
        return "Test a Discord webhook by sending a test message to verify it works"

    def execute(self, **kwargs) -> dict[str, Any]:
        """
        Test webhook.
        
        Args:
            webhook_url: Discord webhook URL (or config_key to load from env)
            config_key: Load webhook from this env var (default: DISCORD_WEBHOOK_URL)
            test_message: Custom test message (optional)
        
        Returns:
            dict with test result
        """
        import requests
        
        webhook_url = kwargs.get("webhook_url")
        config_key = kwargs.get("config_key", "DISCORD_WEBHOOK_URL")
        test_message = kwargs.get("test_message", "✅ Webhook test successful!")

        # Load from env if not provided
        if not webhook_url:
            webhook_url = os.getenv(config_key)
        
        if not webhook_url:
            return {
                "success": False,
                "error": f"No webhook URL provided or found in {config_key}"
            }

        try:
            # Send test message
            payload = {
                "content": test_message,
                "username": "Webhook Test Bot"
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 204:
                return {
                    "success": True,
                    "message": "Webhook test successful!",
                    "status_code": 204,
                    "webhook_preview": webhook_url[:50] + "..."
                }
            else:
                return {
                    "success": False,
                    "error": f"Webhook returned status {response.status_code}",
                    "response": response.text[:200]
                }

        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class WebhookManagerTool(IToolAdapter):
    """All-in-one webhook management tool."""

    def get_name(self) -> str:
        return "manage_discord_webhooks"

    def get_description(self) -> str:
        return "Complete webhook management: create, list, save, test, and delete webhooks"

    def execute(self, **kwargs) -> dict[str, Any]:
        """
        Manage webhooks.
        
        Args:
            action: "create", "list", "save", "test", or "delete"
            **kwargs: Action-specific parameters
        
        Returns:
            dict with action result
        """
        action = kwargs.get("action")
        
        if not action:
            return {
                "success": False,
                "error": "action is required",
                "available_actions": ["create", "list", "save", "test", "delete"]
            }

        tools = {
            "create": CreateWebhookTool(),
            "list": ListWebhooksTool(),
            "save": SaveWebhookTool(),
            "test": TestWebhookTool(),
        }

        tool = tools.get(action)
        if not tool:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "available_actions": list(tools.keys())
            }

        return tool.execute(**kwargs)


__all__ = [
    "CreateWebhookTool",
    "ListWebhooksTool", 
    "SaveWebhookTool",
    "TestWebhookTool",
    "WebhookManagerTool"
]

