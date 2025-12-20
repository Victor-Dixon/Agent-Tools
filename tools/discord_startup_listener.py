#!/usr/bin/env python3
"""
Discord Startup Listener - Minimal Always-On Starter
=====================================================

Minimal always-on service that listens for !startdiscord command
and launches the Discord bot + queue processor system.

This is a lightweight backup starter that runs independently
of the main bot, allowing remote startup after system boot.

<!-- SSOT Domain: infrastructure -->

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-12-08
Priority: HIGH
"""

import asyncio
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

try:
    import discord
    from discord.ext import commands
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    print("⚠️  discord.py not installed. Install with: pip install discord.py")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
START_SCRIPT = PROJECT_ROOT / "tools" / "start_discord_system.py"
LOCK_FILE = PROJECT_ROOT / "logs" / "discord_startup_listener.lock"


class StartupListenerBot(commands.Bot):
    """Minimal bot that only listens for !startdiscord command."""
    
    def __init__(self, token: str, channel_id: int | None = None):
        """Initialize startup listener bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        
        self.token = token
        self.channel_id = channel_id
        self.logger = logging.getLogger(__name__)
        self.system_running = False
    
    async def setup_hook(self):
        """Setup hook - register startup command."""
        await self.add_cog(StartupCommands(self))
        self.logger.info("✅ Startup listener commands loaded")
    
    async def on_ready(self):
        """Called when bot is ready."""
        self.logger.info(f"✅ Startup listener bot ready: {self.user}")
        if self.channel_id:
            channel = self.get_channel(self.channel_id)
            if channel:
                await channel.send(
                    "🟢 **Startup Listener Active**\n"
                    "Type `!startdiscord` to start the Discord system (bot + queue processor)."
                )
    
    async def close(self):
        """Cleanup on close."""
        self.logger.info("🛑 Shutting down startup listener bot")
        await super().close()


class StartupCommands(commands.Cog):
    """Commands for starting Discord system."""
    
    def __init__(self, bot: StartupListenerBot):
        """Initialize startup commands."""
        self.bot = bot
        self.logger = logging.getLogger(__name__)
    
    @commands.command(name="startdiscord", description="Start Discord bot + queue processor system")
    async def start_discord_system(self, ctx: commands.Context):
        """Start the complete Discord system (bot + queue processor)."""
        try:
            # Check if system is already running
            if self._is_system_running():
                embed = discord.Embed(
                    title="⚠️ System Already Running",
                    description="Discord system (bot + queue processor) is already running.",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)
                return
            
            # Confirm startup
            embed = discord.Embed(
                title="🚀 Starting Discord System",
                description=(
                    "Starting Discord bot + queue processor...\n\n"
                    "This will launch:\n"
                    "• Discord bot (with auto-restart)\n"
                    "• Message queue processor\n\n"
                    "⏳ Please wait..."
                ),
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
            # Start system
            success = self._start_discord_system()
            
            if success:
                embed = discord.Embed(
                    title="✅ System Started",
                    description=(
                        "Discord system started successfully!\n\n"
                        "**Components Running:**\n"
                        "• Discord bot\n"
                        "• Message queue processor\n\n"
                        "System is now active and ready to use."
                    ),
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="❌ Startup Failed",
                    description=(
                        "Failed to start Discord system.\n\n"
                        "**Possible Issues:**\n"
                        "• System already running\n"
                        "• Missing dependencies\n"
                        "• Configuration errors\n\n"
                        "Check logs for details."
                    ),
                    color=discord.Color.red()
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in startdiscord command: {e}", exc_info=True)
            await ctx.send(f"❌ Error: {e}")
    
    def _is_system_running(self) -> bool:
        """Check if Discord system is already running."""
        lock_file = PROJECT_ROOT / "logs" / "discord_system.lock"
        if not lock_file.exists():
            return False
        
        try:
            pid = int(lock_file.read_text().strip())
            # Check if process exists (Windows)
            if sys.platform == 'win32':
                try:
                    os.kill(pid, 0)  # Signal 0 doesn't kill, just checks existence
                    return True
                except (OSError, ProcessLookupError):
                    return False
            else:
                # Unix-like
                try:
                    os.kill(pid, 0)
                    return True
                except (OSError, ProcessLookupError):
                    return False
        except Exception:
            return False
    
    def _start_discord_system(self) -> bool:
        """Start Discord system via start_discord_system.py."""
        try:
            if not START_SCRIPT.exists():
                self.logger.error(f"Start script not found: {START_SCRIPT}")
                return False
            
            # Start in background (Windows)
            if sys.platform == 'win32':
                # Use CREATE_NEW_CONSOLE to run in separate window
                subprocess.Popen(
                    [sys.executable, str(START_SCRIPT)],
                    cwd=str(PROJECT_ROOT),
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                # Unix-like: use nohup or screen
                subprocess.Popen(
                    [sys.executable, str(START_SCRIPT)],
                    cwd=str(PROJECT_ROOT),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            
            # Give it a moment to start
            time.sleep(2)
            
            # Verify it started
            if self._is_system_running():
                self.logger.info("✅ Discord system started successfully")
                return True
            else:
                self.logger.warning("⚠️  Discord system may not have started (check logs)")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting Discord system: {e}", exc_info=True)
            return False


def create_lock():
    """Create lock file for single instance."""
    try:
        lock_dir = LOCK_FILE.parent
        lock_dir.mkdir(parents=True, exist_ok=True)
        LOCK_FILE.write_text(str(os.getpid()))
        return True
    except Exception as e:
        logger.error(f"Failed to create lock file: {e}")
        return False


def cleanup_lock():
    """Remove lock file."""
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except Exception:
        pass


def main():
    """Main entry point."""
    if not DISCORD_AVAILABLE:
        logger.error("❌ discord.py not available - cannot run startup listener")
        return 1
    
    # Check token
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        logger.error("❌ DISCORD_BOT_TOKEN not found in .env file")
        print("\n💡 To fix:")
        print("   1. Create .env file in project root")
        print("   2. Add: DISCORD_BOT_TOKEN=your_token_here")
        print("   3. Run this script again\n")
        return 1
    
    # Create lock
    if not create_lock():
        logger.error("❌ Failed to create lock file")
        return 1
    
    # Register cleanup
    import atexit
    atexit.register(cleanup_lock)
    
    # Get channel ID (optional)
    channel_id = os.getenv("DISCORD_CHANNEL_ID")
    if channel_id:
        try:
            channel_id = int(channel_id)
        except ValueError:
            channel_id = None
    
    # Create and run bot
    logger.info("🚀 Starting Discord startup listener...")
    bot = StartupListenerBot(token=token, channel_id=channel_id)
    
    try:
        bot.run(token)
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}", exc_info=True)
        return 1
    finally:
        cleanup_lock()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


