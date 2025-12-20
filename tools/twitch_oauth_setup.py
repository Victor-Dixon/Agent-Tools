#!/usr/bin/env python3
"""
Twitch OAuth Setup Tool
=======================

Interactive tool to set up Twitch OAuth properly.
No third-party services - uses official Twitch OAuth API.

Usage:
    python tools/twitch_oauth_setup.py
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env file
try:
    from dotenv import load_dotenv, dotenv_values
    env_vars = dotenv_values(".env")
    for key, value in env_vars.items():
        if value and key not in os.environ:
            os.environ[key] = value
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")

from src.services.chat_presence.twitch_oauth import get_oauth_token_interactive


def save_to_env_file(client_id: str, client_secret: str, access_token: str, channel: str):
    """Save credentials to .env file."""
    env_path = Path(".env")
    
    # Read existing .env if it exists
    env_lines = []
    if env_path.exists():
        with open(env_path, "r") as f:
            env_lines = f.readlines()
    
    # Update or add Twitch variables
    updates = {
        "TWITCH_CLIENT_ID": client_id,
        "TWITCH_CLIENT_SECRET": client_secret,
        "TWITCH_ACCESS_TOKEN": access_token,
        "TWITCH_CHANNEL": channel,
    }
    
    # Remove old Twitch entries
    env_lines = [line for line in env_lines if not any(
        line.startswith(f"{key}=") for key in updates.keys()
    )]
    
    # Add new entries
    env_lines.append("\n# Twitch OAuth Configuration\n")
    for key, value in updates.items():
        env_lines.append(f"{key}={value}\n")
    
    # Write back
    with open(env_path, "w") as f:
        f.writelines(env_lines)
    
    print(f"✅ Saved to {env_path}")


def main():
    print("=" * 60)
    print("🔐 TWITCH OAUTH SETUP")
    print("=" * 60)
    print()
    print("This tool will help you set up Twitch OAuth properly.")
    print("No third-party services - uses official Twitch OAuth API.")
    print()
    
    # Check for existing credentials
    client_id = os.getenv("TWITCH_CLIENT_ID")
    client_secret = os.getenv("TWITCH_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("Step 1: Twitch OAuth Application Setup")
        print("-" * 60)
        print("1. Go to: https://dev.twitch.tv/console/apps")
        print("2. Log in and click 'Register Your Application'")
        print("3. Fill in:")
        print("   - Name: Agent Cellphone Chat Bot")
        print("   - OAuth Redirect URLs: http://localhost:3000/callback")
        print("   - Category: Chat Bot")
        print("4. Copy your Client ID and Client Secret")
        print()
        
        client_id = input("Enter Client ID: ").strip()
        client_secret = input("Enter Client Secret: ").strip()
        
        if not client_id or not client_secret:
            print("❌ Client ID and Secret are required!")
            return
    else:
        print("✅ Using existing Twitch credentials from .env")
        print(f"Client ID: {client_id[:10]}...")
    
    print()
    print("Step 2: Channel Configuration")
    print("-" * 60)
    channel = input("Enter your Twitch channel name (without #): ").strip().lower()
    
    if not channel:
        print("❌ Channel name is required!")
        return
    
    print()
    print("Step 3: OAuth Authorization")
    print("-" * 60)
    print("Starting OAuth flow...")
    print()
    
    # Get access token
    access_token = get_oauth_token_interactive(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="http://localhost:3000/callback",
        scopes=["chat:read", "chat:edit", "channel:moderate"]
    )
    
    if not access_token:
        print("❌ Failed to obtain access token")
        return
    
    # Format token for IRC (add oauth: prefix if not present)
    if not access_token.startswith("oauth:"):
        irc_token = f"oauth:{access_token}"
    else:
        irc_token = access_token
    
    print()
    print("Step 4: Save Configuration")
    print("-" * 60)
    
    # Save to .env
    save_to_env_file(client_id, client_secret, irc_token, channel)
    
    print()
    print("=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Your Twitch OAuth is configured!")
    print()
    print("To start the bot, run:")
    print("  python tools/chat_presence_cli.py --twitch-only")
    print()
    print("Test commands in chat:")
    print("  !agent7 hello")
    print("  !team status")
    print()


if __name__ == "__main__":
    main()



