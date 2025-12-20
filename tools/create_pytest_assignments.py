#!/usr/bin/env python3
"""
Create Pytest Debugging Assignments for All Agents
==================================================
Force multiplier - assign pytest debugging tasks based on agent specializations
"""

from src.core.messaging_core import (
    UnifiedMessagingCore,
    UnifiedMessageType,
    UnifiedMessagePriority,
    UnifiedMessageTag
)
import sys
from pathlib import Path
from datetime import datetime

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


AGENT_ASSIGNMENTS = {
    "Agent-1": {
        "focus": "Integration & Core Systems",
        "test_paths": [
            "tests/integration/test_messaging_templates_integration.py",
            "tests/integration/test_analysis_endpoints.py",
            "tests/integration/test_validation_endpoints.py",
            "tests/integration/test_phase2_endpoints.py",
            "tests/unit/services/test_messaging_infrastructure.py",
            "tests/unit/services/test_unified_messaging_service.py"
        ],
        "priority": "HIGH"
    },
    "Agent-2": {
        "focus": "Architecture & Design",
        "test_paths": [
            "tests/unit/core/test_config_ssot.py",
            "tests/unit/core/test_pydantic_config.py",
            "tests/unit/core/engines/test_registry_discovery.py",
            "tests/unit/core/managers/test_core_service_manager.py",
            "tests/unit/domain/test_message_bus_port.py",
            "tests/unit/domain/test_browser_port.py"
        ],
        "priority": "HIGH"
    },
    "Agent-3": {
        "focus": "Infrastructure & DevOps",
        "test_paths": [
            "tests/unit/infrastructure/persistence/*.py",
            "tests/unit/infrastructure/logging/*.py",
            "tests/unit/infrastructure/browser/*.py",
            "tests/unit/infrastructure/time/*.py",
            "tests/unit/infrastructure/test_*.py"
        ],
        "priority": "HIGH"
    },
    "Agent-5": {
        "focus": "Business Intelligence",
        "test_paths": [
            "tests/unit/services/test_extractor_*.py",
            "tests/unit/services/test_contract_manager.py",
            "tests/unit/services/test_session*.py",
            "tests/unit/services/models/test_vector_models.py"
        ],
        "priority": "MEDIUM"
    },
    "Agent-6": {
        "focus": "Coordination & Communication",
        "test_paths": [
            "tests/discord/*.py",
            "tests/services/chat_presence/*.py"
        ],
        "priority": "HIGH"
    },
    "Agent-7": {
        "focus": "Web Development",
        "test_paths": [
            "tests/unit/gui/*.py",
            "tests/unit/infrastructure/browser/unified/*.py",
            "tests/unit/infrastructure/test_unified_browser_service.py"
        ],
        "priority": "HIGH"
    },
    "Agent-8": {
        "focus": "SSOT & System Integration",
        "test_paths": [
            "tests/unit/swarm_brain/*.py",
            "tests/unit/core/test_config_ssot.py",
            "tests/unit/quality/test_proof_ledger.py"
        ],
        "priority": "CRITICAL"
    },
    "Agent-4": {
        "focus": "Captain - Strategic Oversight",
        "test_paths": [
            "tests/unit/services/test_contract_manager.py",
            "tests/integration/test_*.py"
        ],
        "priority": "HIGH"
    }
}


def create_assignment_message(agent_id: str, assignment: dict) -> str:
    """Create assignment message for agent"""
    focus = assignment["focus"]
    test_paths = assignment["test_paths"]
    priority = assignment["priority"]

    message = f"""# 🧪 PYTEST DEBUGGING ASSIGNMENT - {priority} PRIORITY

**Agent**: {agent_id}  
**Focus**: {focus}  
**Priority**: {priority}  
**Assignment Date**: {datetime.utcnow().isoformat()}Z

## 📋 ASSIGNMENT OVERVIEW

You have been assigned pytest debugging tasks in your specialization domain. This is a **force multiplier** initiative to improve test coverage and reliability across the swarm.

## 🎯 YOUR RESPONSIBILITIES

### 1. **Test Discovery & Analysis**
   - Review assigned test files in your domain
   - Identify failing/skipped tests
   - Document test status and failure reasons

### 2. **Debugging & Fixes**
   - Fix failing tests in your assigned paths
   - Improve test coverage where gaps exist
   - Ensure tests follow V2 compliance standards

### 3. **Test Execution**
   - Run: `pytest {agent_id.lower().replace('-', '_')}_domain/ -v`
   - Run: `pytest {' '.join(test_paths[:3])} -v`  # Sample of your paths
   - Document results in your devlog

### 4. **Reporting**
   - Report findings in devlog
   - Update status.json with progress
   - Coordinate with Captain (Agent-4) on blockers

## 📁 YOUR ASSIGNED TEST PATHS

{chr(10).join(f'- `{path}`' for path in test_paths[:6])}
{f'{chr(10)}... and related tests in your domain' if len(test_paths) > 6 else ''}

## ✅ ACCEPTANCE CRITERIA

- [ ] All assigned tests pass
- [ ] Test coverage improved or maintained
- [ ] Tests follow V2 compliance (LOC limits, structure)
- [ ] Documentation updated for any test changes
- [ ] Results reported in devlog and status.json

## 🚀 QUICK START COMMANDS

```bash
# Run your domain tests
pytest tests/unit/{focus.lower().replace(' ', '_')}/ -v --tb=short

# Run specific test file
pytest {test_paths[0] if test_paths else 'tests/'} -v

# Run with coverage
pytest {test_paths[0] if test_paths else 'tests/'} --cov --cov-report=html
```

## 🔗 COORDINATION

- Check with Agent-4 (Captain) if you encounter blockers
- Coordinate with other agents if tests span multiple domains
- Post updates to Discord devlog channel

**Let's make our test suite bulletproof! 🎯**

---
*Assignment delivered via Unified Messaging Service*"""

    return message


def send_assignments():
    """Send pytest debugging assignments to all agents"""
    print("🧪 Creating pytest debugging assignments for all agents...\n")

    for agent_id, assignment in AGENT_ASSIGNMENTS.items():
        try:
            message = create_assignment_message(agent_id, assignment)

            # Send message via inbox
            from src.core.messaging_core import UnifiedMessagingCore
            messaging = UnifiedMessagingCore()

            result = messaging.send_message(
                content=message,
                recipient=agent_id,
                sender="Captain Agent-4",
                message_type=UnifiedMessageType.TEXT,
                priority=UnifiedMessagePriority.URGENT if assignment["priority"] in [
                    "CRITICAL", "HIGH"] else UnifiedMessagePriority.REGULAR,
                tags=[UnifiedMessageTag.CAPTAIN]
            )

            if result:
                print(f"✅ Assignment sent to {agent_id}")
            else:
                print(f"❌ Failed to send assignment to {agent_id}")

        except Exception as e:
            print(f"❌ Error sending to {agent_id}: {e}")

    print(f"\n✅ Assignments sent to {len(AGENT_ASSIGNMENTS)} agents")


if __name__ == "__main__":
    send_assignments()
