#!/usr/bin/env python3
"""
Chat Presence CLI
=================

Command-line interface for starting chat presence system.

Usage:
    python tools/chat_presence_cli.py --twitch --obs
    python tools/chat_presence_cli.py --twitch-only
    python tools/chat_presence_cli.py --obs-only
"""

import asyncio
import argparse
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env file if available
try:
    from dotenv import load_dotenv, dotenv_values
    env_vars = dotenv_values(".env")
    for key, value in env_vars.items():
        if value and key not in os.environ:
            os.environ[key] = value
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, skip

from src.services.chat_presence import ChatPresenceOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def load_config() -> dict:
    """Load configuration from environment or config file."""
    config = {
        "twitch": {},
        "obs": {},
    }

    # Load from proper OAuth setup (recommended)
    access_token = os.getenv("TWITCH_ACCESS_TOKEN")
    channel = os.getenv("TWITCH_CHANNEL")
    
    if access_token and channel:
        # Get username from token validation or use channel as username
        username = os.getenv("TWITCH_BOT_USERNAME") or channel
        config["twitch"] = {
            "username": username,
            "oauth_token": access_token,
            "channel": channel,
        }
    
    # Legacy: Check for TWITCH_SWARM_VOICE (single env var format)
    elif os.getenv("TWITCH_SWARM_VOICE"):
        swarm_voice = os.getenv("TWITCH_SWARM_VOICE")
        parts = swarm_voice.split("|")
        if len(parts) == 3:
            username, oauth_token, channel = [p.strip() for p in parts]
            config["twitch"] = {
                "username": username,
                "oauth_token": oauth_token,
                "channel": channel,
            }
    
    # Legacy: Load from individual environment variables
    elif os.getenv("TWITCH_BOT_USERNAME") or os.getenv("TWITCH_OAUTH_TOKEN"):
        config["twitch"] = {
            "username": os.getenv("TWITCH_BOT_USERNAME", ""),
            "oauth_token": os.getenv("TWITCH_OAUTH_TOKEN", ""),
            "channel": os.getenv("TWITCH_CHANNEL", ""),
        }

    if os.getenv("OBS_WEBSOCKET_HOST"):
        config["obs"] = {
            "host": os.getenv("OBS_WEBSOCKET_HOST", "localhost"),
            "port": int(os.getenv("OBS_WEBSOCKET_PORT", "4455")),
            "password": os.getenv("OBS_WEBSOCKET_PASSWORD") or None,
        }

    # Load from config file if exists
    config_path = Path("config/chat_presence.json")
    if config_path.exists():
        import json

        with open(config_path) as f:
            file_config = json.load(f)
            config.update(file_config)

    return config


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Chat Presence System - Twitch/Discord + OBS Integration"
    )
    parser.add_argument(
        "--twitch",
        action="store_true",
        help="Enable Twitch chat presence",
    )
    parser.add_argument(
        "--obs",
        action="store_true",
        help="Enable OBS caption listening",
    )
    parser.add_argument(
        "--twitch-only",
        action="store_true",
        help="Only enable Twitch (no OBS)",
    )
    parser.add_argument(
        "--obs-only",
        action="store_true",
        help="Only enable OBS (no Twitch)",
    )

    args = parser.parse_args()

    # Determine which systems to enable
    enable_twitch = args.twitch or args.twitch_only
    enable_obs = args.obs or args.obs_only

    if not enable_twitch and not enable_obs:
        logger.error("❌ Must enable at least one system (--twitch or --obs)")
        parser.print_help()
        return

    # Load configuration
    config = load_config()

    # Build orchestrator config
    twitch_config = config.get("twitch", {}) if enable_twitch else None
    obs_config = config.get("obs", {}) if enable_obs else None

    if enable_twitch and not twitch_config:
        logger.error("❌ Twitch enabled but no configuration found")
        logger.info("Set TWITCH_BOT_USERNAME, TWITCH_OAUTH_TOKEN, TWITCH_CHANNEL")
        return

    if enable_obs and not obs_config:
        logger.warning("⚠️ OBS enabled but no configuration, using defaults")
        obs_config = {"host": "localhost", "port": 4455, "password": None}

    # Create orchestrator
    logger.info("🚀 Starting Chat Presence Orchestrator...")
    orchestrator = ChatPresenceOrchestrator(
        twitch_config=twitch_config,
        obs_config=obs_config,
    )

    # Start system
    success = await orchestrator.start()

    if not success:
        logger.error("❌ Failed to start orchestrator")
        return

    logger.info("✅ Chat Presence System running")
    logger.info("Press Ctrl+C to stop")

    try:
        # Keep running
        while orchestrator.running:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down...")
        await orchestrator.stop()
        logger.info("✅ Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())


