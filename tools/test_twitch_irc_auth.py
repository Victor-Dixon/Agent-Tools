#!/usr/bin/env python3
"""
Test Twitch IRC Authentication Format
====================================

Tests the exact IRC authentication format to see what Twitch expects.
"""

import re
import os
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
    """Extract channel name from URL or channel name."""
    if not channel_value:
        return ""
    channel_value = channel_value.strip()
    url_pattern = r'(?:https?://)?(?:www\.)?twitch\.tv/([^/?]+)'
    match = re.search(url_pattern, channel_value, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    if channel_value.startswith('#'):
        channel_value = channel_value[1:]
    return channel_value.lower().strip()


def normalize_oauth_token(token: str) -> str:
    """Normalize OAuth token format."""
    if not token:
        return ""
    token = token.strip()
    if not token.startswith('oauth:'):
        return f"oauth:{token}"
    return token


# Test IRC connection directly
try:
    import irc.client
    import irc.bot
except ImportError:
    print("❌ IRC library not installed. Install with: pip install irc")
    sys.exit(1)

# Get config
access_token = os.getenv("TWITCH_ACCESS_TOKEN", "").strip()
channel_raw = os.getenv("TWITCH_CHANNEL", "").strip()
username_raw = os.getenv("TWITCH_BOT_USERNAME", "").strip()

channel_fixed = extract_channel_name(channel_raw) if channel_raw else ""
oauth_token_fixed = normalize_oauth_token(access_token) if access_token else ""
username_fixed = username_raw.lower().strip() if username_raw else channel_fixed

print("=" * 60)
print("🔍 TWITCH IRC AUTHENTICATION TEST")
print("=" * 60)
print()
print(f"Username: {username_fixed}")
print(f"Channel: {channel_fixed}")
print(f"OAuth Token: {oauth_token_fixed[:20]}...")
print()

# Test 1: Check token format
print("Test 1: OAuth Token Format")
print("-" * 60)
if not oauth_token_fixed.startswith("oauth:"):
    print(f"❌ Token doesn't start with 'oauth:' prefix")
    print(f"   Current: {oauth_token_fixed[:30]}...")
    print(f"   Should be: oauth:xxxxx...")
else:
    print(f"✅ Token format looks correct: {oauth_token_fixed[:20]}...")
print()

# Test 2: Create connection and check password attribute
print("Test 2: IRC Connection Password Attribute")
print("-" * 60)
try:
    reactor = irc.client.IRC()
    server = irc.client.ServerSpec("irc.chat.twitch.tv", 6667)
    connection = reactor.server()

    print(f"Connection object created: {connection}")
    print(f"Has password attribute: {hasattr(connection, 'password')}")

    # Try setting password
    connection.password = oauth_token_fixed
    print(f"✅ Password set: {connection.password[:20]}...")
    print(f"   Password type: {type(connection.password)}")
    print(f"   Password length: {len(connection.password)}")

    # Check if password has newlines or other issues
    if '\n' in connection.password or '\r' in connection.password:
        print("❌ WARNING: Password contains newline characters!")
    if ' ' in connection.password:
        print("⚠️  WARNING: Password contains spaces!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("💡 DIAGNOSIS")
print("=" * 60)
print()
print("The error 'Improperly formatted auth' suggests:")
print("1. The PASS command isn't being sent at all")
print("2. The password value has extra characters (newlines, spaces)")
print("3. The password isn't being set before connection")
print()
print("To fix:")
print("- Ensure password is set BEFORE _connect() is called")
print("- Verify password has no extra whitespace")
print("- Check that IRC library sends PASS command with the password")
print()
