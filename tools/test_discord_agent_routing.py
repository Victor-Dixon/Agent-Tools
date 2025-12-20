#!/usr/bin/env python3
"""
Test Discord Agent Routing for Agents 5-8
==========================================

Diagnostic script to test if Discord messages can route to agents 5-8.
"""

from src.core.messaging_models_core import MessageCategory
from src.services.messaging_infrastructure import MessageCoordinator
from src.discord_commander.discord_agent_communication import AgentCommunicationEngine
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_agent_validation():
    """Test if agents 5-8 are validated correctly."""
    print("=" * 60)
    print("TEST 1: Agent Validation")
    print("=" * 60)

    engine = AgentCommunicationEngine()
    for agent_id in ["Agent-5", "Agent-6", "Agent-7", "Agent-8"]:
        is_valid = engine.is_valid_agent(agent_id)
        print(f"  {agent_id}: {'✅ VALID' if is_valid else '❌ INVALID'}")

    print()


def test_message_coordinator():
    """Test MessageCoordinator routing to agents 5-8."""
    print("=" * 60)
    print("TEST 2: MessageCoordinator Routing")
    print("=" * 60)

    test_message = "Test message from diagnostic script"

    for agent_id in ["Agent-5", "Agent-6", "Agent-7", "Agent-8"]:
        try:
            result = MessageCoordinator.send_to_agent(
                agent=agent_id,
                message=test_message,
                priority="regular",
                use_pyautogui=False,  # Don't actually send via PyAutoGUI
                message_category=MessageCategory.D2A,
            )

            if result and result.get("success"):
                print(f"  {agent_id}: ✅ Message queued successfully")
                print(f"    Queue ID: {result.get('queue_id', 'N/A')[:20]}...")
            else:
                print(f"  {agent_id}: ❌ Failed to queue message")
                print(
                    f"    Error: {result.get('error', 'Unknown error') if result else 'No result'}")
        except Exception as e:
            print(f"  {agent_id}: ❌ Exception: {e}")

    print()


def test_workspace_directories():
    """Test if agent workspace directories exist."""
    print("=" * 60)
    print("TEST 3: Workspace Directories")
    print("=" * 60)

    workspace_root = project_root / "agent_workspaces"

    for agent_id in ["Agent-5", "Agent-6", "Agent-7", "Agent-8"]:
        agent_dir = workspace_root / agent_id
        inbox_dir = agent_dir / "inbox"

        dir_exists = agent_dir.exists()
        inbox_exists = inbox_dir.exists()

        print(f"  {agent_id}:")
        print(f"    Workspace: {'✅ EXISTS' if dir_exists else '❌ MISSING'}")
        print(f"    Inbox: {'✅ EXISTS' if inbox_exists else '❌ MISSING'}")

    print()


def main():
    """Run all diagnostic tests."""
    print("\n🔍 DISCORD AGENT ROUTING DIAGNOSTIC")
    print("=" * 60)
    print()

    test_agent_validation()
    test_workspace_directories()
    test_message_coordinator()

    print("=" * 60)
    print("✅ Diagnostic complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
