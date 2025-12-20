#!/usr/bin/env python3
"""
Agent Mode Switcher - CLI Tool
==============================

Switches between agent operating modes (4-agent, 5-agent, 6-agent, 8-agent).

Usage:
    python tools/switch_agent_mode.py <mode>
    python tools/switch_agent_mode.py --current
    python tools/switch_agent_mode.py --list

Examples:
    python tools/switch_agent_mode.py 4-agent
    python tools/switch_agent_mode.py 8-agent
    python tools/switch_agent_mode.py --current
    python tools/switch_agent_mode.py --list
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.agent_mode_manager import get_mode_manager


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("❌ Usage: python tools/switch_agent_mode.py <mode> | --current | --list")
        print("\nAvailable modes: 4-agent, 5-agent, 6-agent, 8-agent")
        sys.exit(1)
    
    mode_manager = get_mode_manager()
    command = sys.argv[1]
    
    if command == "--current":
        current_mode = mode_manager.get_current_mode()
        mode_info = mode_manager.get_mode_info()
        active_agents = mode_manager.get_active_agents()
        monitor_setup = mode_manager.get_monitor_setup()
        
        print("=" * 70)
        print("CURRENT AGENT MODE")
        print("=" * 70)
        print(f"Mode: {current_mode}")
        print(f"Name: {mode_info.get('name', 'N/A')}")
        print(f"Description: {mode_info.get('description', 'N/A')}")
        print(f"Monitor Setup: {monitor_setup}")
        print(f"Active Agents ({len(active_agents)}): {', '.join(active_agents)}")
        print(f"Processing Order: {' → '.join(mode_manager.get_processing_order())}")
        print("=" * 70)
        sys.exit(0)
    
    if command == "--list":
        available_modes = mode_manager.get_available_modes()
        current_mode = mode_manager.get_current_mode()
        
        print("=" * 70)
        print("AVAILABLE AGENT MODES")
        print("=" * 70)
        for mode_name in available_modes:
            mode_info = mode_manager.get_mode_info(mode_name)
            active_agents = mode_manager.get_active_agents(mode_name)
            monitor_setup = mode_manager.get_monitor_setup(mode_name)
            marker = " ← CURRENT" if mode_name == current_mode else ""
            
            print(f"\n{mode_name}{marker}")
            print(f"  Name: {mode_info.get('name', 'N/A')}")
            print(f"  Description: {mode_info.get('description', 'N/A')}")
            print(f"  Monitor Setup: {monitor_setup}")
            print(f"  Active Agents ({len(active_agents)}): {', '.join(active_agents)}")
        print("\n" + "=" * 70)
        sys.exit(0)
    
    # Switch mode
    mode_name = command
    if mode_name not in mode_manager.get_available_modes():
        print(f"❌ Invalid mode: {mode_name}")
        print(f"Available modes: {', '.join(mode_manager.get_available_modes())}")
        sys.exit(1)
    
    # Show current mode before switching
    old_mode = mode_manager.get_current_mode()
    old_agents = mode_manager.get_active_agents()
    
    # Switch mode
    success = mode_manager.set_mode(mode_name, save=True)
    if not success:
        print(f"❌ Failed to switch to mode: {mode_name}")
        sys.exit(1)
    
    # Show new mode
    new_agents = mode_manager.get_active_agents()
    monitor_setup = mode_manager.get_monitor_setup()
    
    print("=" * 70)
    print("AGENT MODE SWITCHED")
    print("=" * 70)
    print(f"Old Mode: {old_mode} ({len(old_agents)} agents)")
    print(f"New Mode: {mode_name} ({len(new_agents)} agents)")
    print(f"Monitor Setup: {monitor_setup}")
    print(f"Active Agents: {', '.join(new_agents)}")
    print(f"Processing Order: {' → '.join(mode_manager.get_processing_order())}")
    print("=" * 70)
    print("\n✅ Mode switch successful!")
    print("💡 Coordinate loader will now filter by active agents only.")
    print("💡 Restart message queue processor for changes to take full effect.")


if __name__ == "__main__":
    main()


