#!/usr/bin/env python3
"""
Unified Swarm Status Validator
================================

Consolidates swarm status validation tools.
Validates swarm status, health, and coordination status.

Features:
- Swarm status validation
- Swarm health monitoring
- Coordination status validation
- Agent status aggregation

V2 Compliance: ≤300 lines, ≤200 lines/class, ≤30 lines/function
Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-03
Task: Phase 2 Tools Consolidation - Communication Validation
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.constants.agent_constants import AGENT_LIST as AGENTS


class SwarmStatusValidator:
    """Unified swarm status validation."""

    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        if workspace_root is None:
            workspace_root = Path(__file__).parent.parent.parent
        self.workspace_root = workspace_root
        self.agent_workspaces = workspace_root / "agent_workspaces"

    def validate_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Validate individual agent status."""
        status_file = self.agent_workspaces / agent_id / "status.json"
        result = {
            "agent_id": agent_id,
            "status_file_exists": status_file.exists(),
            "valid": False,
            "last_updated": None,
            "status": None,
        }

        if not status_file.exists():
            self.errors.append(f"{agent_id}: status.json not found")
            return result

        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                status_data = json.load(f)

            result["status"] = status_data.get("status")
            result["last_updated"] = status_data.get("last_updated")

            if not result["last_updated"]:
                self.warnings.append(f"{agent_id}: No last_updated timestamp")
            else:
                try:
                    last_updated = datetime.strptime(
                        result["last_updated"], "%Y-%m-%d %H:%M:%S"
                    )
                    hours_old = (datetime.now() - last_updated).total_seconds() / 3600
                    if hours_old > 6:
                        self.warnings.append(
                            f"{agent_id}: Status stale ({hours_old:.1f}h old)"
                        )
                except ValueError:
                    self.warnings.append(f"{agent_id}: Invalid timestamp format")

            result["valid"] = True
        except Exception as e:
            self.errors.append(f"{agent_id}: Error reading status.json: {e}")

        return result

    def validate_swarm_status(self) -> Dict[str, Any]:
        """Validate overall swarm status."""
        agent_statuses = {}
        valid_count = 0
        stale_count = 0
        missing_count = 0

        for agent_id in AGENTS:
            agent_status = self.validate_agent_status(agent_id)
            agent_statuses[agent_id] = agent_status

            if agent_status["valid"]:
                valid_count += 1
            elif not agent_status["status_file_exists"]:
                missing_count += 1
            else:
                stale_count += 1

        return {
            "valid": len(self.errors) == 0,
            "total_agents": len(AGENTS),
            "valid_agents": valid_count,
            "stale_agents": stale_count,
            "missing_agents": missing_count,
            "agent_statuses": agent_statuses,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def validate_coordination_status(self) -> bool:
        """Validate coordination system status."""
        valid = True
        # Check for coordination files/directories
        coordination_dirs = [
            "agent_workspaces",
            "docs/organization",
        ]

        for dir_name in coordination_dirs:
            dir_path = self.workspace_root / dir_name
            if not dir_path.exists():
                self.warnings.append(f"Coordination directory not found: {dir_name}")

        return valid

    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        swarm_status = self.validate_swarm_status()
        return {
            "valid": swarm_status["valid"],
            "swarm_status": swarm_status,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def print_report(self) -> None:
        """Print validation report."""
        swarm_status = self.validate_swarm_status()
        print(f"📊 Swarm Status:")
        print(f"  Valid agents: {swarm_status['valid_agents']}/{swarm_status['total_agents']}")
        print(f"  Stale agents: {swarm_status['stale_agents']}")
        print(f"  Missing agents: {swarm_status['missing_agents']}")

        from src.core.utils.validation_utils import print_validation_report
        print_validation_report(
            errors=self.errors,
            warnings=self.warnings,
        )


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Unified swarm status validator"
    )
    parser.add_argument(
        "--agent", help="Validate specific agent status"
    )
    parser.add_argument(
        "--all", action="store_true", help="Validate all agents"
    )
    parser.add_argument(
        "--coordination", action="store_true", help="Validate coordination status"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )

    args = parser.parse_args()
    validator = SwarmStatusValidator()

    if args.agent:
        result = validator.validate_agent_status(args.agent)
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            validator.print_report()
        return 0 if result["valid"] else 1
    elif args.all or args.coordination:
        results = validator.validate_swarm_status()
        if args.coordination:
            validator.validate_coordination_status()
        if args.json:
            summary = validator.get_summary()
            print(json.dumps(summary, indent=2, default=str))
        else:
            validator.print_report()
        return 0 if results["valid"] else 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())


