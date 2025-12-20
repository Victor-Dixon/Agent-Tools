#!/usr/bin/env python3
"""
Unified Discord - Consolidated Discord Operations Tool
======================================================

<!-- SSOT Domain: communication -->

Consolidates all Discord operations into a single unified tool.
Replaces 14+ individual Discord tools with modular Discord system.

Discord Categories:
- system - System operations (start, stop, restart)
- test - Testing operations
- verify - Verification operations
- upload - File upload operations

Author: Agent-5 (Business Intelligence Specialist) - Executing Agent-8's Consolidation Plan
Date: 2025-12-06
V2 Compliant: Yes
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedDiscord:
    """Unified Discord operations system consolidating all Discord capabilities."""
    
    def __init__(self):
        """Initialize unified Discord."""
        self.project_root = project_root
    
    def system_start(self) -> Dict[str, Any]:
        """Start Discord system (bot + message queue processor)."""
        try:
            from tools.start_discord_system import start_discord_system
            
            result = start_discord_system()
            return {
                "category": "system",
                "action": "start",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Discord system start failed: {e}")
            return {
                "category": "system",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def system_restart(self) -> Dict[str, Any]:
        """Restart Discord system."""
        try:
            from tools.restart_discord_bot import restart_bot
            
            result = restart_bot()
            return {
                "category": "system",
                "action": "restart",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Discord system restart failed: {e}")
            return {
                "category": "system",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_commands(self) -> Dict[str, Any]:
        """Test Discord commands."""
        try:
            from tools.test_discord_commands import main as test_commands_main
            
            # Run test commands (may print to stdout)
            test_commands_main()
            return {
                "category": "test",
                "action": "commands",
                "result": "Test commands executed",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Discord commands test failed: {e}")
            return {
                "category": "test",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_bot_debug(self) -> Dict[str, Any]:
        """Test Discord bot debugging."""
        try:
            from tools.test_discord_bot_debug import start_debug_bot
            
            result = start_debug_bot()
            return {
                "category": "test",
                "action": "bot_debug",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Discord bot debug test failed: {e}")
            return {
                "category": "test",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def test_channels(self) -> Dict[str, Any]:
        """Test all agent Discord channels."""
        try:
            from tools.test_all_agent_discord_channels import main as test_channels_main
            
            # Run channel tests (may print to stdout)
            test_channels_main()
            return {
                "category": "test",
                "action": "channels",
                "result": "Channel tests executed",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Discord channels test failed: {e}")
            return {
                "category": "test",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def verify_buttons(self) -> Dict[str, Any]:
        """Verify Discord buttons."""
        try:
            from tools.verify_discord_buttons import ButtonVerifier
            
            verifier = ButtonVerifier()
            result = verifier.verify_all_buttons()
            return {
                "category": "verify",
                "action": "buttons",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Discord buttons verification failed: {e}")
            return {
                "category": "verify",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def verify_running(self) -> Dict[str, Any]:
        """Verify Discord bot is running."""
        try:
            from tools.check_discord_running import check_discord_running
            
            result = check_discord_running()
            return {
                "category": "verify",
                "action": "running",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Discord running verification failed: {e}")
            return {
                "category": "verify",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def upload_file(self, file_path: str, channel_id: str = None) -> Dict[str, Any]:
        """Upload file to Discord."""
        try:
            from tools.upload_file_to_discord import upload_file_to_discord
            
            result = upload_file_to_discord(file_path, channel_id)
            return {
                "category": "upload",
                "action": "file",
                "file_path": file_path,
                "channel_id": channel_id,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Discord file upload failed: {e}")
            return {
                "category": "upload",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def main():
    """CLI entry point for unified Discord tool."""
    parser = argparse.ArgumentParser(
        description="Unified Discord Operations Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m tools.unified_discord system start
  python -m tools.unified_discord system restart
  python -m tools.unified_discord test commands
  python -m tools.unified_discord test bot-debug
  python -m tools.unified_discord test channels
  python -m tools.unified_discord verify buttons
  python -m tools.unified_discord verify running
  python -m tools.unified_discord upload file --file path/to/file.txt --channel 123456789
        """
    )
    
    parser.add_argument(
        "category",
        choices=["system", "test", "verify", "upload"],
        help="Discord operation category"
    )
    
    parser.add_argument(
        "action",
        help="Action to perform within category"
    )
    
    parser.add_argument("--file", help="File path for upload")
    parser.add_argument("--channel", help="Discord channel ID")
    
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    discord = UnifiedDiscord()
    results = {}
    
    # Route to appropriate category method
    if args.category == "system":
        if args.action == "start":
            results = discord.system_start()
        elif args.action == "restart":
            results = discord.system_restart()
        else:
            results = {"error": f"Unknown system action: {args.action}"}
    
    elif args.category == "test":
        if args.action == "commands":
            results = discord.test_commands()
        elif args.action == "bot-debug":
            results = discord.test_bot_debug()
        elif args.action == "channels":
            results = discord.test_channels()
        else:
            results = {"error": f"Unknown test action: {args.action}"}
    
    elif args.category == "verify":
        if args.action == "buttons":
            results = discord.verify_buttons()
        elif args.action == "running":
            results = discord.verify_running()
        else:
            results = {"error": f"Unknown verify action: {args.action}"}
    
    elif args.category == "upload":
        if args.action == "file" and args.file:
            results = discord.upload_file(args.file, args.channel)
        else:
            results = {"error": "File path required for upload"}
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        if "error" in results:
            print(f"❌ Error: {results['error']}")
        else:
            print(json.dumps(results, indent=2, default=str))
    
    return 0 if "error" not in results else 1


if __name__ == "__main__":
    sys.exit(main())

