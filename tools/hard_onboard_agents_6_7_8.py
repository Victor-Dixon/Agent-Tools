#!/usr/bin/env python3
"""
Hard Onboard Agents 6, 7, 8
============================

Hard onboard agents 6, 7, and 8 with fresh mission directives.

Author: Agent-4 (Captain)
Date: 2025-11-28
"""

import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def hard_onboard_agent(agent_id: str, message: str) -> bool:
    """Hard onboard a single agent."""
    print(f"\n{'='*60}")
    print(f"🚨 HARD ONBOARDING {agent_id}")
    print(f"{'='*60}")
    
    cmd = [
        "python",
        "-m",
        "src.services.messaging_cli",
        "--hard-onboarding",
        "--agent",
        agent_id,
        "--message",
        message,
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False, check=False)
        if result.returncode == 0:
            print(f"✅ {agent_id} hard onboarded successfully!")
            return True
        else:
            print(f"❌ {agent_id} hard onboarding failed (exit code: {result.returncode})")
            return False
    except Exception as e:
        print(f"❌ Error hard onboarding {agent_id}: {e}")
        return False


def main():
    """Hard onboard agents 6, 7, and 8."""
    print("=" * 60)
    print("🚨 HARD ONBOARDING AGENTS 6, 7, 8")
    print("=" * 60)
    print()
    
    # Agent-6: Coordination & Communication Specialist
    agent6_message = """Execute your core mission: Coordination & Communication

**Primary Focus**:
- Coordinate multi-agent workflows
- Facilitate communication between agents
- Track consolidation progress
- Manage execution tracking

**Current Priority**: Continue consolidation tracking and coordination work.

**Action Required**: Check inbox, review current tasks, execute highest priority work, post devlog."""
    
    # Agent-7: Web Development Specialist
    agent7_message = """Execute your core mission: Web Development

**Primary Focus**:
- Web development and frontend work
- React/TypeScript development
- UI/UX improvements
- Web infrastructure

**Current Priority**: Continue web development work and V2 compliance.

**Action Required**: Check inbox, review current tasks, execute highest priority work, post devlog."""
    
    # Agent-8: SSOT & System Integration Specialist
    agent8_message = """Execute your core mission: SSOT & System Integration

**Primary Focus**:
- Maintain single source of truth (SSOT)
- System integration and consolidation
- Architecture compliance
- Code quality enforcement

**Current Priority**: Continue SSOT consolidation and system integration work.

**Action Required**: Check inbox, review current tasks, execute highest priority work, post devlog."""
    
    agents = [
        ("Agent-6", agent6_message),
        ("Agent-7", agent7_message),
        ("Agent-8", agent8_message),
    ]
    
    results = []
    for agent_id, message in agents:
        success = hard_onboard_agent(agent_id, message)
        results.append((agent_id, success))
    
    print()
    print("=" * 60)
    print("📊 HARD ONBOARDING SUMMARY")
    print("=" * 60)
    
    for agent_id, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"  {agent_id}: {status}")
    
    all_success = all(success for _, success in results)
    
    if all_success:
        print()
        print("✅ ALL AGENTS HARD ONBOARDED SUCCESSFULLY!")
        return 0
    else:
        print()
        print("⚠️ SOME AGENTS FAILED TO HARD ONBOARD")
        return 1


if __name__ == "__main__":
    sys.exit(main())

