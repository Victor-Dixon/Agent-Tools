#!/usr/bin/env python3
"""
Discord Bot Troubleshooting Tool
=================================

Quick diagnostics for Discord bot issues.

<!-- SSOT Domain: infrastructure -->

Author: Agent-3 (Infrastructure & DevOps)
Date: 2025-01-27
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed")

print("=" * 70)
print("🔍 DISCORD BOT TROUBLESHOOTING")
print("=" * 70)
print()

# 1. Check Discord token
print("1️⃣  Checking Discord Bot Token...")
token = os.getenv("DISCORD_BOT_TOKEN")
if token:
    print(f"   ✅ Token found (length: {len(token)})")
    if len(token) < 50:
        print("   ⚠️  Token appears too short - may be invalid")
else:
    print("   ❌ DISCORD_BOT_TOKEN not set!")
    print("   💡 Set it with: $env:DISCORD_BOT_TOKEN='your_token'")
print()

# 2. Check Discord library
print("2️⃣  Checking discord.py library...")
try:
    import discord
    print(f"   ✅ discord.py installed (version: {discord.__version__})")
except ImportError:
    print("   ❌ discord.py not installed!")
    print("   💡 Install with: pip install discord.py")
    sys.exit(1)
print()

# 3. Check bot file
print("3️⃣  Checking bot file...")
bot_file = project_root / "src" / "discord_commander" / "unified_discord_bot.py"
if bot_file.exists():
    print(f"   ✅ Bot file exists: {bot_file}")
else:
    print(f"   ❌ Bot file not found: {bot_file}")
    sys.exit(1)
print()

# 4. Check for running processes
print("4️⃣  Checking for running processes...")
try:
    import psutil
    discord_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'unified_discord_bot' in cmdline or 'start_discord' in cmdline:
                discord_processes.append({
                    'pid': proc.info['pid'],
                    'cmdline': cmdline[:100]
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if discord_processes:
        print(f"   ⚠️  Found {len(discord_processes)} running Discord bot process(es):")
        for p in discord_processes:
            print(f"      PID {p['pid']}: {p['cmdline']}")
    else:
        print("   ✅ No running Discord bot processes found")
except ImportError:
    print("   ⚠️  psutil not installed - cannot check processes")
except Exception as e:
    print(f"   ⚠️  Error checking processes: {e}")
print()

# 5. Check error logs
print("5️⃣  Checking error logs...")
log_dir = project_root / "logs"
error_log = log_dir / "discord_bot_errors.log"
if error_log.exists():
    print(f"   ✅ Error log found: {error_log}")
    try:
        with open(error_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                print(f"   📄 Last {min(10, len(lines))} error lines:")
                for line in lines[-10:]:
                    print(f"      {line.rstrip()}")
            else:
                print("   ✅ Error log is empty (no errors!)")
    except Exception as e:
        print(f"   ⚠️  Could not read error log: {e}")
else:
    print("   ℹ️  No error log found (this is OK if bot hasn't run)")
print()

# 6. Check queue processor
print("6️⃣  Checking message queue...")
queue_file = project_root / "message_queue" / "queue.json"
if queue_file.exists():
    print(f"   ✅ Queue file exists: {queue_file}")
    try:
        import json
        with open(queue_file, 'r', encoding='utf-8') as f:
            queue_data = json.load(f)
            # Queue format is a JSON array (list), not dict
            if isinstance(queue_data, list):
                pending = len([m for m in queue_data if m.get('status') == 'PENDING'])
                processing = len([m for m in queue_data if m.get('status') == 'PROCESSING'])
                delivered = len([m for m in queue_data if m.get('status') == 'DELIVERED'])
                failed = len([m for m in queue_data if m.get('status') == 'FAILED'])
                total = len(queue_data)
                print(f"   📊 Queue status: {pending} pending, {processing} processing, {delivered} delivered, {failed} failed, {total} total messages")
            elif isinstance(queue_data, dict):
                # Handle dict format if it has messages key
                messages = queue_data.get('messages', [])
                pending = len([m for m in messages if m.get('status') == 'PENDING' or m.get('status') == 'pending'])
                total = len(messages)
                print(f"   📊 Queue status: {pending} pending, {total} total messages (dict format)")
            else:
                print(f"   ⚠️  Unexpected queue file format: {type(queue_data)}")
    except Exception as e:
        print(f"   ⚠️  Could not read queue file: {e}")
        import traceback
        traceback.print_exc()
else:
    print("   ℹ️  Queue file not found (will be created on first message)")
print()

# 7. Test imports
print("7️⃣  Testing imports...")
try:
    from src.discord_commander.unified_discord_bot import UnifiedDiscordBot
    print("   ✅ UnifiedDiscordBot imports successfully")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
print()

# 8. Check channel ID
print("8️⃣  Checking Discord Channel ID...")
channel_id = os.getenv("DISCORD_CHANNEL_ID")
if channel_id:
    print(f"   ✅ Channel ID found: {channel_id}")
else:
    print("   ⚠️  DISCORD_CHANNEL_ID not set (optional, but recommended)")
print()

print("=" * 70)
print("✅ TROUBLESHOOTING COMPLETE")
print("=" * 70)
print()
print("💡 To start the bot:")
print("   python tools/start_discord_system.py")
print()
print("💡 Or directly:")
print("   python -m src.discord_commander.unified_discord_bot")
print()

