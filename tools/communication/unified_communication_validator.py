#!/usr/bin/env python3
"""
Unified Communication Validator
================================

Unified entry point for all communication validation.
Consolidates all communication validation tools into single interface.

Features:
- Comprehensive validation (all validation types)
- Unified interface
- Single entry point for all validations

V2 Compliance: ≤300 lines, ≤200 lines/class, ≤30 lines/function
Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-03
Task: Phase 2 Tools Consolidation - Communication Validation
"""

import sys
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import all validators
from tools.communication.message_validator import MessageValidator
from tools.communication.coordination_validator import CoordinationValidator
from tools.communication.agent_status_validator import AgentStatusValidator
from tools.communication.multi_agent_validator import MultiAgentValidator
from tools.communication.integration_validator import IntegrationValidator
from tools.communication.messaging_infrastructure_validator import (
    MessagingInfrastructureValidator
)
from tools.communication.coordination_pattern_validator import (
    CoordinationPatternValidator
)
from tools.communication.swarm_status_validator import SwarmStatusValidator


class UnifiedCommunicationValidator:
    """Unified entry point for all communication validation."""

    def __init__(self):
        """Initialize unified validator."""
        self.message_validator = MessageValidator()
        self.coordination_validator = CoordinationValidator()
        self.agent_status_validator = AgentStatusValidator()
        self.multi_agent_validator = MultiAgentValidator()
        self.integration_validator = IntegrationValidator()
        self.infrastructure_validator = MessagingInfrastructureValidator()
        self.pattern_validator = CoordinationPatternValidator()
        self.swarm_validator = SwarmStatusValidator()

    def validate_all(self, workspace_root: Path = None) -> Dict[str, Any]:
        """Run all validations."""
        if workspace_root is None:
            workspace_root = Path.cwd()

        results = {
            "message": self.message_validator.get_summary(),
            "coordination": self.coordination_validator.get_summary(),
            "agent_status": self.agent_status_validator.get_summary(),
            "multi_agent": self.multi_agent_validator.get_summary(),
            "integration": self.integration_validator.validate_infrastructure_health(
                workspace_root
            ),
            "infrastructure": self.infrastructure_validator.validate_infrastructure_health(),
            "pattern": self.pattern_validator.get_summary(),
            "swarm": self.swarm_validator.validate_swarm_status(),
        }

        all_valid = all(
            r.get("valid", False) for r in results.values() if isinstance(r, dict)
        )
        total_errors = sum(
            r.get("error_count", 0) for r in results.values() if isinstance(r, dict)
        )
        total_warnings = sum(
            r.get("warning_count", 0) for r in results.values() if isinstance(r, dict)
        )

        return {
            "valid": all_valid,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "results": results,
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get unified validation summary."""
        return self.validate_all()


def main() -> int:
    """CLI entry point."""
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Unified communication validator (all validations)"
    )
    parser.add_argument(
        "--all", action="store_true", help="Run all validations"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )

    args = parser.parse_args()
    validator = UnifiedCommunicationValidator()

    if args.all:
        results = validator.validate_all()
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            print("📊 Unified Communication Validation Results:")
            print(f"  Overall Status: {'✅ VALID' if results['valid'] else '❌ INVALID'}")
            print(f"  Total Errors: {results['total_errors']}")
            print(f"  Total Warnings: {results['total_warnings']}")
            print("\n📋 Validation Breakdown:")
            for name, result in results["results"].items():
                if isinstance(result, dict):
                    status = "✅" if result.get("valid", False) else "❌"
                    print(f"  {status} {name}: {result.get('error_count', 0)} errors, "
                          f"{result.get('warning_count', 0)} warnings")
        return 0 if results["valid"] else 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())


