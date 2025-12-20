#!/usr/bin/env python3
"""
Test Discord GUI Command Registration
=====================================

Quick diagnostic script to verify the !gui command is properly registered.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import discord
    from discord.ext import commands
    from src.discord_commander.unified_discord_bot import UnifiedDiscordBot
    from src.services.unified_messaging_service import UnifiedMessagingService
    from src.discord_commander.discord_gui_controller import DiscordGUIController
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

async def test_command_registration():
    """Test if gui command is registered."""
    print("🔍 Testing Discord bot command registration...")
    
    # Create a mock bot instance (without token)
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True
    
    bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
    
    # Initialize services
    messaging_service = UnifiedMessagingService()
    gui_controller = DiscordGUIController(messaging_service)
    bot.gui_controller = gui_controller
    
    # Load the cog
    try:
        from src.discord_commander.commands.core_messaging_commands import CoreMessagingCommands
        await bot.add_cog(CoreMessagingCommands(bot, gui_controller))
        print("✅ CoreMessagingCommands cog loaded")
    except Exception as e:
        print(f"❌ Error loading cog: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check if gui command exists
    gui_command = bot.get_command("gui")
    if gui_command:
        print(f"✅ GUI command found: {gui_command.name}")
        print(f"   Description: {gui_command.description}")
        print(f"   Cog: {gui_command.cog.__class__.__name__}")
        return True
    else:
        print("❌ GUI command NOT found!")
        print(f"   Available commands: {[cmd.name for cmd in bot.walk_commands()]}")
        return False

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(test_command_registration())
    sys.exit(0 if result else 1)



