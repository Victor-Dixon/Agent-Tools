#!/usr/bin/env python3
"""
Unstick Agent-3 Assignment Script
==================================

DEPRECATED: Use send_agent3_assignment_direct.py instead (direct file write).

This script clicks Agent-3's onboarding coordinates, presses Enter, then sends assignment to chat coordinates.

Usage:
    python tools/unstick_agent3_assignment.py
"""

import time
import pyautogui
import pyperclip
import json
from pathlib import Path

# Safety settings
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True

# Load coordinates from SSOT
COORD_FILE = Path("cursor_agent_coords.json")
if not COORD_FILE.exists():
    raise FileNotFoundError(f"Coordinate file not found: {COORD_FILE}")

coords_data = json.loads(COORD_FILE.read_text(encoding="utf-8"))
agent3_info = coords_data["agents"]["Agent-3"]

# Get coordinates
onboarding_coords = tuple(agent3_info["onboarding_input_coords"])
chat_coords = tuple(agent3_info["chat_input_coordinates"])

print(f"📍 Agent-3 Coordinates:")
print(f"   Onboarding: {onboarding_coords}")
print(f"   Chat: {chat_coords}")

# Assignment message
ASSIGNMENT_MESSAGE = """🚀 JET FUEL - FINAL SESSION TASKS

HIGH PRIORITY:
1. Test Coverage Expansion (< 2 hours)
   - Complete remaining 7 infrastructure files (84.1% → 100%)
   - Target: 100% coverage for all 44 files

2. Simple Git Clone Implementation (< 1 hour)
   - Update tools to use D:/Temp directly
   - Remove complex temp directory management

3. Deferred Queue Monitoring (Ongoing)
   - Monitor GitHub access restoration

Full assignments: docs/organization/SESSION_CLOSE_2025-11-29_TASK_ASSIGNMENTS.md

🐝 WE. ARE. SWARM. ⚡🔥"""

def unstick_agent3():
    """Unstick Agent-3 by clicking onboarding, pressing Enter, then sending assignment."""
    print("\n🚀 UNSTICKING AGENT-3...")
    
    try:
        # Step 1: Click onboarding coordinates
        print(f"1. Clicking onboarding coordinates: {onboarding_coords}")
        pyautogui.moveTo(onboarding_coords[0], onboarding_coords[1], duration=0.5)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(0.5)
        print("   ✅ Clicked onboarding coordinates")
        
        # Step 2: Press Enter to clear/activate
        print("2. Pressing Enter...")
        pyautogui.press('enter')
        time.sleep(1.0)
        print("   ✅ Enter pressed")
        
        # Step 3: Navigate to chat coordinates
        print(f"3. Navigating to chat coordinates: {chat_coords}")
        pyautogui.moveTo(chat_coords[0], chat_coords[1], duration=0.5)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(0.5)
        print("   ✅ Clicked chat coordinates")
        
        # Step 4: Clear any existing content
        print("4. Clearing existing content...")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.5)
        print("   ✅ Content cleared")
        
        # Step 5: Copy assignment to clipboard
        print("5. Copying assignment to clipboard...")
        pyperclip.copy(ASSIGNMENT_MESSAGE)
        time.sleep(0.5)
        print("   ✅ Assignment copied")
        
        # Step 6: Paste assignment
        print("6. Pasting assignment...")
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1.0)
        print("   ✅ Assignment pasted")
        
        # Step 7: Send message (Enter)
        print("7. Sending message...")
        pyautogui.press('enter')
        time.sleep(1.0)
        print("   ✅ Message sent")
        
        print("\n✅ AGENT-3 UNSTUCK SUCCESSFULLY!")
        print(f"   Assignment sent to chat coordinates: {chat_coords}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("AGENT-3 UNSTICK SCRIPT")
    print("=" * 60)
    print("\n⚠️  WARNING: This will click coordinates and send a message.")
    print("   Make sure Cursor is open and visible.")
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    unstick_agent3()
    
    print("\n" + "=" * 60)
    print("✅ COMPLETE")
    print("=" * 60)


Unstick Agent-3 Assignment Script
==================================

DEPRECATED: Use send_agent3_assignment_direct.py instead (direct file write).

This script clicks Agent-3's onboarding coordinates, presses Enter, then sends assignment to chat coordinates.

Usage:
    python tools/unstick_agent3_assignment.py
"""

import time
import pyautogui
import pyperclip
import json
from pathlib import Path

# Safety settings
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True

# Load coordinates from SSOT
COORD_FILE = Path("cursor_agent_coords.json")
if not COORD_FILE.exists():
    raise FileNotFoundError(f"Coordinate file not found: {COORD_FILE}")

coords_data = json.loads(COORD_FILE.read_text(encoding="utf-8"))
agent3_info = coords_data["agents"]["Agent-3"]

# Get coordinates
onboarding_coords = tuple(agent3_info["onboarding_input_coords"])
chat_coords = tuple(agent3_info["chat_input_coordinates"])

print(f"📍 Agent-3 Coordinates:")
print(f"   Onboarding: {onboarding_coords}")
print(f"   Chat: {chat_coords}")

# Assignment message
ASSIGNMENT_MESSAGE = """🚀 JET FUEL - FINAL SESSION TASKS

HIGH PRIORITY:
1. Test Coverage Expansion (< 2 hours)
   - Complete remaining 7 infrastructure files (84.1% → 100%)
   - Target: 100% coverage for all 44 files

2. Simple Git Clone Implementation (< 1 hour)
   - Update tools to use D:/Temp directly
   - Remove complex temp directory management

3. Deferred Queue Monitoring (Ongoing)
   - Monitor GitHub access restoration

Full assignments: docs/organization/SESSION_CLOSE_2025-11-29_TASK_ASSIGNMENTS.md

🐝 WE. ARE. SWARM. ⚡🔥"""

def unstick_agent3():
    """Unstick Agent-3 by clicking onboarding, pressing Enter, then sending assignment."""
    print("\n🚀 UNSTICKING AGENT-3...")
    
    try:
        # Step 1: Click onboarding coordinates
        print(f"1. Clicking onboarding coordinates: {onboarding_coords}")
        pyautogui.moveTo(onboarding_coords[0], onboarding_coords[1], duration=0.5)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(0.5)
        print("   ✅ Clicked onboarding coordinates")
        
        # Step 2: Press Enter to clear/activate
        print("2. Pressing Enter...")
        pyautogui.press('enter')
        time.sleep(1.0)
        print("   ✅ Enter pressed")
        
        # Step 3: Navigate to chat coordinates
        print(f"3. Navigating to chat coordinates: {chat_coords}")
        pyautogui.moveTo(chat_coords[0], chat_coords[1], duration=0.5)
        time.sleep(0.5)
        pyautogui.click()
        time.sleep(0.5)
        print("   ✅ Clicked chat coordinates")
        
        # Step 4: Clear any existing content
        print("4. Clearing existing content...")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.5)
        print("   ✅ Content cleared")
        
        # Step 5: Copy assignment to clipboard
        print("5. Copying assignment to clipboard...")
        pyperclip.copy(ASSIGNMENT_MESSAGE)
        time.sleep(0.5)
        print("   ✅ Assignment copied")
        
        # Step 6: Paste assignment
        print("6. Pasting assignment...")
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1.0)
        print("   ✅ Assignment pasted")
        
        # Step 7: Send message (Enter)
        print("7. Sending message...")
        pyautogui.press('enter')
        time.sleep(1.0)
        print("   ✅ Message sent")
        
        print("\n✅ AGENT-3 UNSTUCK SUCCESSFULLY!")
        print(f"   Assignment sent to chat coordinates: {chat_coords}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("AGENT-3 UNSTICK SCRIPT")
    print("=" * 60)
    print("\n⚠️  WARNING: This will click coordinates and send a message.")
    print("   Make sure Cursor is open and visible.")
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    unstick_agent3()
    
    print("\n" + "=" * 60)
    print("✅ COMPLETE")
    print("=" * 60)
