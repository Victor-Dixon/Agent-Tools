#!/usr/bin/env python3
"""
Verify OAuth Token Format
=========================

Checks if the OAuth token has proper format and no hidden characters.
"""

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

print("=" * 60)
print("🔍 OAUTH TOKEN FORMAT VERIFICATION")
print("=" * 60)
print()

# Get raw token
raw_token = os.getenv("TWITCH_ACCESS_TOKEN", "")

print(f"Raw token length: {len(raw_token)}")
print(f"Raw token repr: {repr(raw_token[:50])}...")
print()

# Check for issues
issues = []
if not raw_token:
    issues.append("❌ Token is empty or not set")
else:
    # Check for newlines
    newline_chars = ['\n', '\r']
    newline_positions = [i for i, c in enumerate(
        raw_token) if c in newline_chars]
    if newline_positions:
        issues.append(f"❌ Token contains newline characters (\\n or \\r)")
        print(f"   Found at positions: {newline_positions}")

    # Check for quotes
    if raw_token.startswith('"') or raw_token.startswith("'") or raw_token.endswith('"') or raw_token.endswith("'"):
        issues.append("❌ Token is wrapped in quotes")

    # Check for spaces
    if ' ' in raw_token:
        issues.append("⚠️  Token contains spaces")

    # Check prefix
    token_stripped = raw_token.strip().strip('"').strip("'")
    if not token_stripped.startswith('oauth:'):
        issues.append("⚠️  Token doesn't start with 'oauth:' prefix")
        print(f"   Current start: {repr(token_stripped[:20])}")
    else:
        print("✅ Token has 'oauth:' prefix")

    # Show cleaned version
    token_clean = token_stripped.replace('\n', '').replace('\r', '')
    if token_clean != raw_token:
        print()
        print("🔧 Cleaned token would be:")
        print(f"   {token_clean[:30]}...")
        print(f"   Length: {len(token_clean)} (was {len(raw_token)})")
    else:
        print("✅ Token is already clean")

print()
if issues:
    print("⚠️  Issues found:")
    for issue in issues:
        print(f"   {issue}")
    print()
    print("💡 Fix: Update .env file with cleaned token (no quotes, no newlines)")
else:
    print("✅ Token format looks good!")

print()
