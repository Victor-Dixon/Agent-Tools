#!/usr/bin/env python3
"""
Fix Twitch Configuration
========================

Validates and normalizes Twitch configuration from environment variables.
Fixes common issues like:
- Channel name extraction from URLs
- OAuth token prefix normalization
- Username fallback logic

Usage:
    python tools/fix_twitch_config.py
"""

import os
import re
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def extract_channel_name(channel_value: str) -> str:
    """
    Extract channel name from various formats.
    
    Handles:
    - Full URLs: https://www.twitch.tv/digital_dreamscape -> digital_dreamscape
    - Channel names with #: #digital_dreamscape -> digital_dreamscape
    - Plain channel names: digital_dreamscape -> digital_dreamscape
    
    Args:
        channel_value: Channel value from environment
        
    Returns:
        Normalized channel name (lowercase, no #, no URL)
    """
    if not channel_value:
        return ""
    
    # Remove whitespace
    channel_value = channel_value.strip()
    
    # Extract from URL if present
    url_pattern = r'(?:https?://)?(?:www\.)?twitch\.tv/([^/?]+)'
    match = re.search(url_pattern, channel_value, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    
    # Remove # prefix if present
    if channel_value.startswith('#'):
        channel_value = channel_value[1:]
    
    # Return lowercase, no spaces
    return channel_value.lower().strip()


def normalize_oauth_token(token: str) -> str:
    """
    Normalize OAuth token format.
    
    Ensures token starts with 'oauth:' prefix.
    
    Args:
        token: OAuth token string
        
    Returns:
        Normalized token with oauth: prefix
    """
    if not token:
        return ""
    
    token = token.strip()
    
    # Add prefix if missing
    if not token.startswith('oauth:'):
        return f"oauth:{token}"
    
    return token


def validate_and_fix_config() -> dict:
    """
    Validate and fix Twitch configuration.
    
    Returns:
        Fixed configuration dict
    """
    print("=" * 60)
    print("🔧 TWITCH CONFIGURATION FIXER")
    print("=" * 60)
    print()
    
    # Get raw values
    access_token = os.getenv("TWITCH_ACCESS_TOKEN", "").strip()
    channel_raw = os.getenv("TWITCH_CHANNEL", "").strip()
    username_raw = os.getenv("TWITCH_BOT_USERNAME", "").strip()
    
    print("📋 Current Configuration:")
    print(f"  TWITCH_ACCESS_TOKEN: {'✅ Set' if access_token else '❌ Not set'}")
    if access_token:
        masked = access_token[:10] + "..." if len(access_token) > 10 else "***"
        print(f"    Raw value: {masked}")
    
    print(f"  TWITCH_CHANNEL: {'✅ Set' if channel_raw else '❌ Not set'}")
    if channel_raw:
        print(f"    Raw value: {channel_raw}")
    
    print(f"  TWITCH_BOT_USERNAME: {'✅ Set' if username_raw else '❌ Not set'}")
    if username_raw:
        print(f"    Raw value: {username_raw}")
    
    print()
    print("🔧 Fixing Configuration...")
    print()
    
    # Fix channel name
    channel_fixed = extract_channel_name(channel_raw) if channel_raw else ""
    
    # Fix OAuth token
    oauth_token_fixed = normalize_oauth_token(access_token) if access_token else ""
    
    # Determine username (use channel if not set)
    username_fixed = username_raw.lower().strip() if username_raw else channel_fixed
    
    # Build fixed config
    fixed_config = {
        "username": username_fixed,
        "oauth_token": oauth_token_fixed,
        "channel": channel_fixed,
    }
    
    print("✅ Fixed Configuration:")
    print(f"  Username: {fixed_config['username']}")
    print(f"  OAuth Token: {fixed_config['oauth_token'][:15]}... (normalized)")
    print(f"  Channel: {fixed_config['channel']}")
    print()
    
    # Show what changed
    changes = []
    if channel_raw != channel_fixed:
        changes.append(f"Channel: '{channel_raw}' → '{channel_fixed}'")
    if access_token != oauth_token_fixed:
        changes.append("OAuth token: Added 'oauth:' prefix")
    if not username_raw and channel_fixed:
        changes.append(f"Username: Using channel name '{channel_fixed}'")
    
    if changes:
        print("📝 Changes Made:")
        for change in changes:
            print(f"  • {change}")
        print()
    else:
        print("✅ No changes needed - configuration is correct!")
        print()
    
    # Validation
    issues = []
    if not fixed_config['username']:
        issues.append("Username is missing")
    if not fixed_config['oauth_token']:
        issues.append("OAuth token is missing")
    if not fixed_config['channel']:
        issues.append("Channel is missing")
    if fixed_config['oauth_token'] and not fixed_config['oauth_token'].startswith('oauth:'):
        issues.append("OAuth token format is incorrect")
    
    if issues:
        print("⚠️  Remaining Issues:")
        for issue in issues:
            print(f"  • {issue}")
        print()
        return None
    
    print("✅ Configuration is valid!")
    print()
    return fixed_config


def main():
    """Main entry point."""
    fixed_config = validate_and_fix_config()
    
    if not fixed_config:
        print("❌ Configuration cannot be fixed automatically")
        print()
        print("💡 Manual fixes needed:")
        print("  1. Set TWITCH_CHANNEL to channel name only (e.g., 'digital_dreamscape')")
        print("  2. Set TWITCH_ACCESS_TOKEN with 'oauth:' prefix")
        print("  3. Optionally set TWITCH_BOT_USERNAME")
        print()
        sys.exit(1)
    
    print("💡 To use this fixed configuration:")
    print("  1. Update your .env file with the corrected values")
    print("  2. Or set environment variables before running the bot")
    print()
    print("Example .env entries:")
    print(f"  TWITCH_CHANNEL={fixed_config['channel']}")
    print(f"  TWITCH_BOT_USERNAME={fixed_config['username']}")
    print(f"  TWITCH_ACCESS_TOKEN={fixed_config['oauth_token']}")
    print()
    
    sys.exit(0)


if __name__ == "__main__":
    main()

