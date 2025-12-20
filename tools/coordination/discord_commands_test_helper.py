#!/usr/bin/env python3
"""
Discord Bot Commands Test Helper
=================================

Helper script to verify Discord bot commands are properly registered.
Does not require Discord connection - just checks command registration.

Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-01-27
Status: Test Helper Created
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_command_registration():
    """Test that all commands are properly registered."""
    try:
        from src.discord_commander.unified_discord_bot import UnifiedDiscordBot
        
        # Create bot instance (won't actually connect)
        bot = UnifiedDiscordBot(token="TEST_TOKEN", channel_id=None)
        
        # Get all registered commands
        commands = {}
        for command in bot.commands:
            commands[command.name] = {
                "aliases": command.aliases,
                "description": command.description,
            }
        
        print("\n✅ Discord Bot Command Registration Check\n")
        print("=" * 60)
        
        # Group by category
        categories = {
            "Messaging": ["control", "gui", "status", "message", "broadcast", "help"],
            "Swarm Showcase": ["swarm_tasks", "swarm_roadmap", "swarm_excellence", "swarm_overview"],
            "GitHub Book": ["github_book", "goldmines", "book_stats", "book_search", "book_filter"],
            "System": ["shutdown", "restart"],
        }
        
        all_commands = set()
        for cmd_list in categories.values():
            all_commands.update(cmd_list)
        
        found_commands = set(commands.keys())
        missing_commands = all_commands - found_commands
        extra_commands = found_commands - all_commands
        
        print(f"\n📊 Command Summary:")
        print(f"   Total Commands Found: {len(commands)}")
        print(f"   Expected Commands: {len(all_commands)}")
        print(f"   Missing Commands: {len(missing_commands)}")
        print(f"   Extra Commands: {len(extra_commands)}")
        
        if missing_commands:
            print(f"\n❌ Missing Commands: {', '.join(sorted(missing_commands))}")
        else:
            print(f"\n✅ All expected commands found!")
        
        if extra_commands:
            print(f"\n⚠️  Extra Commands: {', '.join(sorted(extra_commands))}")
        
        print("\n" + "=" * 60)
        print("\n📋 Command Details:\n")
        
        for category, cmd_names in categories.items():
            print(f"**{category} Commands:**")
            for cmd_name in cmd_names:
                if cmd_name in commands:
                    cmd_info = commands[cmd_name]
                    aliases_str = f" (aliases: {', '.join(cmd_info['aliases'])})" if cmd_info['aliases'] else ""
                    desc_str = f" - {cmd_info['description']}" if cmd_info['description'] else ""
                    print(f"   ✅ !{cmd_name}{aliases_str}{desc_str}")
                else:
                    print(f"   ❌ !{cmd_name} - NOT FOUND")
            print()
        
        # Check for extra commands
        if extra_commands:
            print("**Other Commands:**")
            for cmd_name in sorted(extra_commands):
                cmd_info = commands[cmd_name]
                aliases_str = f" (aliases: {', '.join(cmd_info['aliases'])})" if cmd_info['aliases'] else ""
                desc_str = f" - {cmd_info['description']}" if cmd_info['description'] else ""
                print(f"   ⚠️  !{cmd_name}{aliases_str}{desc_str}")
            print()
        
        print("=" * 60)
        print("\n✅ Command Registration Check Complete!\n")
        
        return len(missing_commands) == 0
        
    except Exception as e:
        logger.error(f"Error checking command registration: {e}")
        print(f"\n❌ Error: {e}\n")
        return False


def test_cog_loading():
    """Test that all cogs load correctly."""
    print("\n✅ Testing Cog Loading\n")
    print("=" * 60)
    
    cogs_to_check = [
        ("MessagingCommands", "src.discord_commander.unified_discord_bot"),
        ("SwarmShowcaseCommands", "src.discord_commander.swarm_showcase_commands"),
        ("GitHubBookCommands", "src.discord_commander.github_book_viewer"),
    ]
    
    all_loaded = True
    for cog_name, module_path in cogs_to_check:
        try:
            module = __import__(module_path, fromlist=[cog_name])
            cog_class = getattr(module, cog_name)
            print(f"   ✅ {cog_name} - Loaded from {module_path}")
            all_loaded = True
        except ImportError as e:
            print(f"   ❌ {cog_name} - Import Error: {e}")
            all_loaded = False
        except AttributeError as e:
            print(f"   ❌ {cog_name} - Attribute Error: {e}")
            all_loaded = False
    
    print("=" * 60)
    print("\n✅ Cog Loading Check Complete!\n")
    
    return all_loaded


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🧪 Discord Bot Commands Test Helper")
    print("=" * 60)
    
    results = []
    
    # Test command registration
    results.append(("Command Registration", test_command_registration()))
    
    # Test cog loading
    results.append(("Cog Loading", test_cog_loading()))
    
    # Summary
    print("=" * 60)
    print("📊 Test Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✅ All tests passed!\n")
        return 0
    else:
        print("\n❌ Some tests failed. Please review errors above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())




