#!/usr/bin/env python3
"""
Unified Multi-Agent Validator
==============================

Consolidates multi-agent validation tools.
Wraps src/core/multi_agent_request_validator.py and provides CLI interface.

Features:
- Multi-agent request validation
- Response tracking validation
- Request/response compliance checking

V2 Compliance: ≤300 lines, ≤200 lines/class, ≤30 lines/function
Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-03
Task: Phase 2 Tools Consolidation - Communication Validation
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.utils.validation_utils import print_validation_report

try:
    from src.core.multi_agent_request_validator import (
        get_multi_agent_validator,
        MultiAgentRequestValidator
    )
except ImportError:
    # Fallback if import fails
    MultiAgentRequestValidator = None


class MultiAgentValidator:
    """Unified multi-agent validation tool."""

    def __init__(self):
        """Initialize validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        if MultiAgentRequestValidator:
            self.validator = get_multi_agent_validator()
        else:
            self.validator = None

    def check_pending_request(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Check if agent has pending multi-agent request."""
        if not self.validator:
            self.errors.append("Multi-agent validator not available")
            return None
        try:
            return self.validator.check_pending_request(agent_id)
        except Exception as e:
            self.errors.append(f"Error checking pending request: {e}")
            return None

    def validate_agent_can_send(
        self, agent_id: str, target_recipient: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Validate agent can send message."""
        if not self.validator:
            return False, "Multi-agent validator not available", None
        try:
            return self.validator.validate_agent_can_send_message(
                agent_id, target_recipient
            )
        except Exception as e:
            self.errors.append(f"Error validating send permission: {e}")
            return False, str(e), None

    def validate_all_agents(self) -> Dict[str, Any]:
        """Validate all agents for pending requests."""
        from src.core.constants.agent_constants import AGENT_LIST
        agents = AGENT_LIST
        results = {}
        agents_with_pending = []

        for agent_id in agents:
            pending = self.check_pending_request(agent_id)
            if pending:
                agents_with_pending.append(agent_id)
                results[agent_id] = {
                    "has_pending": True,
                    "request_id": pending.get("request_id"),
                    "sender": pending.get("sender"),
                    "responses_received": pending.get("responses_received"),
                    "recipient_count": pending.get("recipient_count"),
                }
            else:
                results[agent_id] = {"has_pending": False}

        return {
            "total_agents": len(agents),
            "agents_with_pending": len(agents_with_pending),
            "agents_with_pending_list": agents_with_pending,
            "results": results,
            "valid": len(agents_with_pending) == 0,
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "valid": len(self.errors) == 0,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def print_report(self) -> None:
        """Print validation report using SSOT utility."""
        print_validation_report(
            errors=self.errors,
            warnings=self.warnings,
        )


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Unified multi-agent validator"
    )
    parser.add_argument(
        "--agent", help="Check specific agent for pending requests"
    )
    parser.add_argument(
        "--all", action="store_true", help="Check all agents"
    )
    parser.add_argument(
        "--can-send", help="Check if agent can send message"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )

    args = parser.parse_args()
    validator = MultiAgentValidator()

    if args.agent:
        pending = validator.check_pending_request(args.agent)
        if args.json:
            result = {"agent": args.agent, "has_pending": pending is not None}
            if pending:
                result["pending_request"] = pending
            print(json.dumps(result, indent=2, default=str))
        else:
            if pending:
                print(f"⚠️  {args.agent} has pending request:")
                print(f"   From: {pending.get('sender')}")
                print(f"   Request ID: {pending.get('request_id')}")
            else:
                print(f"✅ {args.agent} has no pending requests")
        return 0 if pending is None else 1

    elif args.can_send:
        can_send, error_msg, pending_info = validator.validate_agent_can_send(
            args.can_send
        )
        if args.json:
            result = {
                "agent": args.can_send,
                "can_send": can_send,
                "error": error_msg,
            }
            if pending_info:
                result["pending_request"] = pending_info
            print(json.dumps(result, indent=2, default=str))
        else:
            if can_send:
                print(f"✅ {args.can_send} can send messages")
            else:
                print(f"❌ {args.can_send} cannot send messages")
                if error_msg:
                    print(f"   {error_msg}")
        return 0 if can_send else 1

    elif args.all:
        results = validator.validate_all_agents()
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            if results["agents_with_pending"] > 0:
                print(f"⚠️  {results['agents_with_pending']} agents have pending requests:")
                for agent_id in results["agents_with_pending_list"]:
                    print(f"  • {agent_id}")
            else:
                print("✅ All agents are clear (no pending requests)")
        return 0 if results["valid"] else 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())


