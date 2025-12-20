#!/usr/bin/env python3
"""
Simple Discord Test Helper - PyAutoGUI Method
==============================================

Simple method to test Discord commands using PyAutoGUI.
Assumes Discord window is already open and focused.

Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-01-27
Status: Simple Discord Test Helper
"""

import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("⚠️  pyautogui not available - install with: pip install pyautogui")


def send_discord_command(command: str, delay: float = 2.0):
    """
    Send a Discord command using PyAutoGUI.
    
    Args:
        command: The command to send (e.g., "!status")
        delay: Delay before sending (default 2 seconds to allow focus)
    """
    if not PYAUTOGUI_AVAILABLE:
        print("❌ PyAutoGUI not available")
        return False
    
    try:
        print(f"\n⏳ Waiting {delay} seconds - please focus Discord window...")
        time.sleep(delay)
        
        print(f"📤 Sending command: {command}")
        
        # Type command
        pyautogui.write(command, interval=0.05)
        time.sleep(0.5)
        
        # Press Enter
        pyautogui.press('enter')
        time.sleep(1)
        
        print(f"✅ Command sent: {command}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending command: {e}")
        return False


def test_commands_interactive():
    """Interactive command testing."""
    print("=" * 60)
    print("🤖 Simple Discord Command Tester (PyAutoGUI)")
    print("=" * 60)
    print("\nInstructions:")
    print("1. Open Discord (web or desktop)")
    print("2. Navigate to your test channel")
    print("3. Focus the message input box")
    print("4. This script will type commands automatically")
    print("\n" + "=" * 60)
    
    if not PYAUTOGUI_AVAILABLE:
        print("\n❌ PyAutoGUI not available!")
        print("   Install with: pip install pyautogui")
        return 1
    
    # Default commands to test
    default_commands = [
        "!help",
        "!control",
        "!status",
        "!gui",
        "!swarm_tasks",
    ]
    
    print("\n📋 Default commands to test:")
    for cmd in default_commands:
        print(f"   - {cmd}")
    
    use_default = input("\nUse default commands? (Y/n): ").strip().lower()
    
    if use_default != 'n':
        commands = default_commands
    else:
        # Custom commands
        print("\nEnter commands to test (one per line, empty line to finish):")
        commands = []
        while True:
            cmd = input("> ").strip()
            if not cmd:
                break
            commands.append(cmd)
    
    print(f"\n🧪 Will test {len(commands)} commands...")
    print("⏳ Starting in 5 seconds - please focus Discord window!\n")
    time.sleep(5)
    
    results = []
    for i, command in enumerate(commands, 1):
        print(f"\n[{i}/{len(commands)}] Testing: {command}")
        success = send_discord_command(command, delay=1.0)
        results.append({"command": command, "success": success})
        time.sleep(3)  # Wait between commands
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"   {status} {result['command']}")
    
    print("=" * 60 + "\n")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    try:
        sys.exit(test_commands_interactive())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)




