#!/usr/bin/env python3
"""
Test New Tools - Quick Test Script
===================================

Test the new message history, activity tracking, queue monitoring,
Discord profile, system datetime, and check-in tools.

Author: Agent-4 (Captain)
Date: 2025-01-27
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools_v2.toolbelt_core import ToolbeltCore


def test_system_datetime():
    """Test system.datetime tool."""
    print("\n" + "="*70)
    print("Testing: system.datetime")
    print("="*70)
    
    toolbelt = ToolbeltCore()
    result = toolbelt.run("system.datetime", {})
    
    print(f"Success: {result.success}")
    if result.success:
        print(f"Output: {result.output}")
    else:
        print(f"Error: {result.error_message}")
    
    return result.success


def test_queue_status():
    """Test queue.status tool."""
    print("\n" + "="*70)
    print("Testing: queue.status")
    print("="*70)
    
    toolbelt = ToolbeltCore()
    result = toolbelt.run("queue.status", {})
    
    print(f"Success: {result.success}")
    if result.success:
        print(f"Output: {result.output}")
    else:
        print(f"Error: {result.error_message}")
    
    return result.success


def test_agent_activity():
    """Test agent_activity.track tool."""
    print("\n" + "="*70)
    print("Testing: agent_activity.track")
    print("="*70)
    
    toolbelt = ToolbeltCore()
    result = toolbelt.run("agent_activity.track", {"check_all": True})
    
    print(f"Success: {result.success}")
    if result.success:
        print(f"Output keys: {list(result.output.keys()) if result.output else 'None'}")
        if result.output:
            for agent, activity in list(result.output.items())[:3]:
                print(f"  {agent}: {activity.get('status', 'unknown')}")
    else:
        print(f"Error: {result.error_message}")
    
    return result.success


def test_message_history_view():
    """Test message_history.view tool."""
    print("\n" + "="*70)
    print("Testing: message_history.view")
    print("="*70)
    
    toolbelt = ToolbeltCore()
    result = toolbelt.run("message_history.view", {"limit": 5})
    
    print(f"Success: {result.success}")
    if result.success:
        print(f"Total messages: {result.output.get('total', 0) if result.output else 0}")
    else:
        print(f"Error: {result.error_message}")
    
    return result.success


def test_checkin():
    """Test system.checkin tool."""
    print("\n" + "="*70)
    print("Testing: system.checkin")
    print("="*70)
    
    toolbelt = ToolbeltCore()
    result = toolbelt.run("system.checkin", {
        "agent_id": "Agent-4",
        "status": "active",
        "note": "Testing new check-in system"
    })
    
    print(f"Success: {result.success}")
    if result.success:
        print(f"Message: {result.output.get('message', 'No message') if result.output else 'No output'}")
    else:
        print(f"Error: {result.error_message}")
    
    return result.success


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTING NEW TOOLS")
    print("="*70)
    
    results = []
    results.append(("system.datetime", test_system_datetime()))
    results.append(("queue.status", test_queue_status()))
    results.append(("agent_activity.track", test_agent_activity()))
    results.append(("message_history.view", test_message_history_view()))
    results.append(("system.checkin", test_checkin()))
    
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    for tool_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {tool_name}")
    
    all_passed = all(success for _, success in results)
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")




