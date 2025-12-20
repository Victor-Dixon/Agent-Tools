#!/usr/bin/env python3
"""
Agent Bump Script - Click and Clear Chat Input
==============================================

Clicks to agent chat input coordinates and presses shift+backspace to clear input.
Used to "bump" agents by clearing their chat input field.

Author: Agent-6 (Coordination & Communication Specialist)
Created: 2025-11-30
"""

import time
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logger.error("PyAutoGUI not available - install with: pip install pyautogui")


def get_agent_coordinates(agent_id: str) -> tuple[int, int]:
    """Get chat input coordinates for agent."""
    try:
        from src.core.coordinate_loader import get_coordinate_loader
        coord_loader = get_coordinate_loader()
        return coord_loader.get_chat_coordinates(agent_id)
    except Exception as e:
        logger.error(f"Error loading coordinates for {agent_id}: {e}")
        # Fallback to hardcoded coordinates
        AGENT_COORDS = {
            "Agent-1": (-1269, 481),
            "Agent-2": (-308, 480),
            "Agent-3": (-1269, 1001),
            "Agent-4": (-308, 1000),
            "Agent-5": (652, 421),
            "Agent-6": (1612, 419),
            "Agent-7": (653, 940),
            "Agent-8": (1611, 941),
        }
        return AGENT_COORDS.get(agent_id, (0, 0))


def bump_agent(agent_id: str) -> bool:
    """
    Bump agent by clicking chat input and pressing shift+backspace.
    
    Args:
        agent_id: Agent identifier (e.g., "Agent-1")
        
    Returns:
        True if successful, False otherwise
    """
    if not PYAUTOGUI_AVAILABLE:
        logger.error("PyAutoGUI not available")
        return False
    
    try:
        # Get coordinates
        coords = get_agent_coordinates(agent_id)
        if coords == (0, 0):
            logger.error(f"No coordinates found for {agent_id}")
            return False
        
        x, y = coords
        logger.info(f"📍 Bumping {agent_id} at coordinates ({x}, {y})")
        
        # Move to coordinates
        pyautogui.moveTo(x, y, duration=0.5)
        time.sleep(0.3)
        
        # Click to focus input field
        pyautogui.click()
        time.sleep(0.3)
        
        # Press shift+backspace to clear input
        pyautogui.hotkey("shift", "backspace")
        time.sleep(0.2)
        
        logger.info(f"✅ Successfully bumped {agent_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error bumping {agent_id}: {e}", exc_info=True)
        return False


def bump_agents(agent_ids: list[str]) -> dict[str, bool]:
    """
    Bump multiple agents.
    
    Args:
        agent_ids: List of agent identifiers
        
    Returns:
        Dictionary mapping agent_id to success status
    """
    results = {}
    for agent_id in agent_ids:
        results[agent_id] = bump_agent(agent_id)
        time.sleep(0.5)  # Small delay between agents
    
    return results


def bump_agents_by_number(agent_numbers: list[int]) -> dict[str, bool]:
    """
    Bump agents by number (1-8).
    
    Args:
        agent_numbers: List of agent numbers (1-8)
        
    Returns:
        Dictionary mapping agent_id to success status
    """
    agent_ids = []
    for num in agent_numbers:
        if 1 <= num <= 8:
            agent_ids.append(f"Agent-{num}")
        else:
            logger.warning(f"Invalid agent number: {num} (must be 1-8)")
    
    return bump_agents(agent_ids)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bump agents by clicking chat input and clearing")
    parser.add_argument("agents", nargs="+", type=int, help="Agent numbers (1-8)")
    
    args = parser.parse_args()
    
    results = bump_agents_by_number(args.agents)
    
    print("\n" + "=" * 50)
    print("BUMP RESULTS")
    print("=" * 50)
    
    for agent_id, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{agent_id}: {status}")
    
    print("=" * 50)
    
    all_success = all(results.values())
    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())

