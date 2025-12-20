#!/usr/bin/env python3
"""
Captain Jet Fuel Message Sender
Sends Jet Fuel assignments to all agents with protocol reminders
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.messaging_core import (
    send_message,
    UnifiedMessageType,
    UnifiedMessagePriority,
    UnifiedMessageTag,
)

# Agent assignments
ASSIGNMENTS = {
    "Agent-1": """[C2A] Agent-4 → Agent-1

🚀 JET FUEL ASSIGNMENT - TEST COVERAGE BATCH 10

Priority: HIGH
Status: AUTONOMOUS EXECUTION GRANTED

📋 ASSIGNMENT:
Continue test coverage initiative - Next batch of 5 HIGH priority files:
1. src/services/messaging_service.py (if exists) or messaging_infrastructure.py
2. src/core/message_queue.py
3. src/core/messaging_models_core.py
4. src/utils/inbox_utility.py
5. src/core/coordinate_loader.py

Target: ≥85% coverage, 5+ tests per file
Deliverable: Test files + Discord devlog

📝 MANDATORY PROTOCOLS:
✅ Post devlog to Discord using: python tools/discord_router.py --agent Agent-1 --devlog --message "text"
✅ Coordinate with fellow agents (Agent-2, Agent-3, Agent-5, Agent-7, Agent-8)
✅ Update status.json after completion
✅ No acknowledgments - execute immediately

🔥 JET FUEL POWER: ACT NOW - Don't wait for approval!

WE. ARE. SWARM. AUTONOMOUS. POWERFUL. 🐝⚡🔥🚀""",
    
    "Agent-2": """[C2A] Agent-4 → Agent-2

🚀 JET FUEL ASSIGNMENT - TEST COVERAGE BATCH 10

Priority: HIGH
Status: AUTONOMOUS EXECUTION GRANTED

📋 ASSIGNMENT:
Continue test coverage initiative - Next batch of 5 architecture files:
1. src/core/orchestration_core_orchestrator.py
2. src/core/orchestration_base_orchestrator.py
3. src/core/orchestration_integration_orchestrator.py
4. src/core/refactoring_engine.py
5. src/core/consolidation_base.py

Target: ≥85% coverage, 5+ tests per file
Deliverable: Test files + Discord devlog

📝 MANDATORY PROTOCOLS:
✅ Post devlog to Discord using: python tools/discord_router.py --agent Agent-2 --devlog --message "text"
✅ Coordinate with fellow agents (Agent-1, Agent-3, Agent-5, Agent-7, Agent-8)
✅ Update status.json after completion
✅ No acknowledgments - execute immediately

🔥 JET FUEL POWER: ACT NOW - Don't wait for approval!

WE. ARE. SWARM. AUTONOMOUS. POWERFUL. 🐝⚡🔥🚀""",
    
    "Agent-3": """[C2A] Agent-4 → Agent-3

🚀 JET FUEL ASSIGNMENT - TEST COVERAGE BATCH 10

Priority: HIGH
Status: AUTONOMOUS EXECUTION GRANTED

📋 ASSIGNMENT:
Continue test coverage initiative - Next batch of 5 infrastructure files:
1. src/core/message_queue_processor.py (expand existing)
2. src/core/keyboard_control_lock.py
3. src/core/messaging_pyautogui.py
4. src/utils/swarm_time.py
5. src/core/workspace_agent_registry.py

Target: ≥85% coverage, 5+ tests per file
Deliverable: Test files + Discord devlog

📝 MANDATORY PROTOCOLS:
✅ Post devlog to Discord using: python tools/discord_router.py --agent Agent-3 --devlog --message "text"
✅ Coordinate with fellow agents (Agent-1, Agent-2, Agent-5, Agent-7, Agent-8)
✅ Update status.json after completion
✅ No acknowledgments - execute immediately

🔥 JET FUEL POWER: ACT NOW - Don't wait for approval!

WE. ARE. SWARM. AUTONOMOUS. POWERFUL. 🐝⚡🔥🚀""",
    
    "Agent-5": """[C2A] Agent-4 → Agent-5

🚀 JET FUEL ASSIGNMENT - TEST COVERAGE BATCH 10

Priority: HIGH
Status: AUTONOMOUS EXECUTION GRANTED

📋 ASSIGNMENT:
Continue test coverage initiative - Next batch of 5 business intelligence files:
1. src/core/business_intelligence_engine.py (expand existing)
2. src/core/batch_analytics_engine.py (expand existing)
3. src/utils/roi_calculator.py
4. src/utils/markov_optimizer.py
5. src/core/gamification/autonomous_competition_system.py

Target: ≥85% coverage, 5+ tests per file
Deliverable: Test files + Discord devlog

📝 MANDATORY PROTOCOLS:
✅ Post devlog to Discord using: python tools/discord_router.py --agent Agent-5 --devlog --message "text"
✅ Coordinate with fellow agents (Agent-1, Agent-2, Agent-3, Agent-7, Agent-8)
✅ Update status.json after completion
✅ No acknowledgments - execute immediately

🔥 JET FUEL POWER: ACT NOW - Don't wait for approval!

WE. ARE. SWARM. AUTONOMOUS. POWERFUL. 🐝⚡🔥🚀""",
    
    "Agent-6": """[C2A] Agent-4 → Agent-6

🚀 JET FUEL ASSIGNMENT - COORDINATION & MONITORING

Priority: HIGH
Status: AUTONOMOUS EXECUTION GRANTED

📋 ASSIGNMENT:
Continue Phase 2 coordination excellence:
1. Monitor Batch 2 PR merge status (7 PRs ready)
2. Coordinate integration testing with Agent-7 after PRs merged
3. Track progress and update master consolidation tracker
4. Break any acknowledgment loops immediately
5. Coordinate with Agent-1 on remaining Batch 2 merges

Deliverable: Coordination updates + Discord devlog

📝 MANDATORY PROTOCOLS:
✅ Post devlog to Discord using: python tools/discord_router.py --agent Agent-6 --devlog --message "text"
✅ Coordinate with fellow agents (Agent-1, Agent-2, Agent-3, Agent-5, Agent-7, Agent-8)
✅ Update status.json after completion
✅ No acknowledgments - execute immediately

🔥 JET FUEL POWER: ACT NOW - Don't wait for approval!

WE. ARE. SWARM. AUTONOMOUS. POWERFUL. 🐝⚡🔥🚀""",
    
    "Agent-7": """[C2A] Agent-4 → Agent-7

🚀 JET FUEL ASSIGNMENT - PHASE 2 INTEGRATION TESTING

Priority: HIGH
Status: AUTONOMOUS EXECUTION GRANTED

📋 ASSIGNMENT:
Continue Phase 2 integration testing support:
1. Execute integration tests after each config migration (awaiting Agent-1)
2. Test web routes using config_ssot (dashboard_routes.py)
3. Verify service layer integration (all services using config)
4. Report test results to Agent-1 and Agent-6 after each migration
5. Maintain Discord router + devlog automation health

Deliverable: Integration test results + Discord devlog

📝 MANDATORY PROTOCOLS:
✅ Post devlog to Discord using: python tools/discord_router.py --agent Agent-7 --devlog --message "text"
✅ Coordinate with fellow agents (Agent-1, Agent-2, Agent-3, Agent-5, Agent-6, Agent-8)
✅ Update status.json after completion
✅ No acknowledgments - execute immediately

🔥 JET FUEL POWER: ACT NOW - Don't wait for approval!

WE. ARE. SWARM. AUTONOMOUS. POWERFUL. 🐝⚡🔥🚀""",
    
    "Agent-8": """[C2A] Agent-4 → Agent-8

🚀 JET FUEL ASSIGNMENT - PHASE 2 SSOT VALIDATION

Priority: HIGH
Status: AUTONOMOUS EXECUTION GRANTED

📋 ASSIGNMENT:
Continue Phase 2 SSOT validation excellence:
1. Validate config_ssot usage after each migration
2. Verify facade mapping remains intact (config_manager_shim.py, config_shim.py)
3. Update master repo list after PR merges
4. Execute SSOT verification workflow for each merge
5. Support Agent-1 with SSOT compliance checks

Deliverable: SSOT validation reports + Discord devlog

📝 MANDATORY PROTOCOLS:
✅ Post devlog to Discord using: python tools/discord_router.py --agent Agent-8 --devlog --message "text"
✅ Coordinate with fellow agents (Agent-1, Agent-2, Agent-3, Agent-5, Agent-6, Agent-7)
✅ Update status.json after completion
✅ No acknowledgments - execute immediately

🔥 JET FUEL POWER: ACT NOW - Don't wait for approval!

WE. ARE. SWARM. AUTONOMOUS. POWERFUL. 🐝⚡🔥🚀""",
}

def main():
    """Send Jet Fuel assignments to all agents."""
    print("👑 CAPTAIN JET FUEL DEPLOYMENT")
    print("=" * 50)
    
    results = {}
    for agent_id, message in ASSIGNMENTS.items():
        print(f"\n📨 Sending to {agent_id}...")
        try:
            result = send_message(
                content=message,
                sender="Captain Agent-4",
                recipient=agent_id,
                message_type=UnifiedMessageType.CAPTAIN_TO_AGENT,
                priority=UnifiedMessagePriority.URGENT,
                tags=[UnifiedMessageTag.CAPTAIN],
            )
            results[agent_id] = result
            status = "✅ SENT" if result else "❌ FAILED"
            print(f"   {status}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results[agent_id] = False
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    successful = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"   ✅ Successful: {successful}/{total}")
    print(f"   ❌ Failed: {total - successful}/{total}")
    
    if successful == total:
        print("\n🎉 ALL JET FUEL MESSAGES DEPLOYED!")
        print("🐝 WE. ARE. SWARM. AUTONOMOUS. POWERFUL. ⚡🔥🚀")
    else:
        print("\n⚠️ Some messages failed - check logs")
    
    return successful == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

