#!/usr/bin/env python3
"""
Unified Coordination Pattern Validator
=======================================

Consolidates coordination pattern and workflow validation tools.
Validates coordination patterns, workflows, and session transitions.

Features:
- Coordination pattern validation
- Workflow validation
- Session transition validation
- Pattern compliance checking

V2 Compliance: ≤300 lines, ≤200 lines/class, ≤30 lines/function
Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-03
Task: Phase 2 Tools Consolidation - Communication Validation
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class CoordinationPatternValidator:
    """Unified coordination pattern validation."""

    def __init__(self):
        """Initialize validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_coordination_pattern(self, pattern_data: Dict[str, Any]) -> bool:
        """Validate coordination pattern structure."""
        valid = True
        required_fields = ["pattern_type", "agents", "workflow"]
        for field in required_fields:
            if field not in pattern_data:
                self.errors.append(f"Missing required field: {field}")
                valid = False

        if "agents" in pattern_data:
            agents = pattern_data["agents"]
            if not isinstance(agents, list) or len(agents) == 0:
                self.errors.append("Agents must be a non-empty list")
                valid = False

        if "workflow" in pattern_data:
            workflow = pattern_data["workflow"]
            if not isinstance(workflow, list) or len(workflow) == 0:
                self.errors.append("Workflow must be a non-empty list")
                valid = False

        return valid

    def validate_workflow(self, workflow_data: List[Dict[str, Any]]) -> bool:
        """Validate workflow structure."""
        valid = True
        if not workflow_data:
            self.errors.append("Workflow cannot be empty")
            return False

        for i, step in enumerate(workflow_data):
            if not isinstance(step, dict):
                self.errors.append(f"Workflow step {i} must be a dictionary")
                valid = False
                continue

            if "action" not in step:
                self.errors.append(f"Workflow step {i} missing 'action' field")
                valid = False

        return valid

    def validate_session_transition(self, agent_id: str, workspace_root: Path) -> bool:
        """Validate session transition requirements."""
        agent_workspace = workspace_root / "agent_workspaces" / agent_id
        valid = True

        passdown_file = agent_workspace / "passdown.json"
        if not passdown_file.exists():
            self.warnings.append(f"{agent_id}: passdown.json not found")
        else:
            try:
                with open(passdown_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                required_fields = [
                    "agent_id", "session_date", "session_summary",
                    "completed_tasks", "key_insights"
                ]
                for field in required_fields:
                    if field not in data:
                        self.warnings.append(
                            f"{agent_id}: passdown.json missing field '{field}'"
                        )
            except Exception as e:
                self.warnings.append(f"{agent_id}: Error reading passdown.json: {e}")

        status_file = agent_workspace / "status.json"
        if not status_file.exists():
            self.errors.append(f"{agent_id}: status.json not found")
            valid = False

        return valid

    def validate_pattern_compliance(
        self, pattern_data: Dict[str, Any], rules: Dict[str, Any]
    ) -> bool:
        """Validate pattern compliance with rules."""
        valid = True
        pattern_type = pattern_data.get("pattern_type")

        if pattern_type in rules:
            pattern_rules = rules[pattern_type]
            for rule_name, rule_value in pattern_rules.items():
                if rule_name in pattern_data:
                    actual_value = pattern_data[rule_name]
                    if actual_value != rule_value:
                        self.warnings.append(
                            f"Pattern {pattern_type}: {rule_name} mismatch "
                            f"(expected {rule_value}, got {actual_value})"
                        )

        return valid

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
        """Print validation report."""
        from src.core.utils.validation_utils import print_validation_report
        print_validation_report(
            errors=self.errors,
            warnings=self.warnings,
        )


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Unified coordination pattern validator"
    )
    parser.add_argument(
        "--pattern", type=Path, help="JSON file with pattern data"
    )
    parser.add_argument(
        "--workflow", type=Path, help="JSON file with workflow data"
    )
    parser.add_argument(
        "--session", help="Validate session transition for agent"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )

    args = parser.parse_args()
    validator = CoordinationPatternValidator()
    workspace_root = Path(__file__).parent.parent.parent

    valid = True
    if args.pattern:
        with open(args.pattern, 'r', encoding='utf-8') as f:
            pattern_data = json.load(f)
        valid = validator.validate_coordination_pattern(pattern_data)
    elif args.workflow:
        with open(args.workflow, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        valid = validator.validate_workflow(workflow_data)
    elif args.session:
        valid = validator.validate_session_transition(args.session, workspace_root)
    else:
        parser.print_help()
        return 1

    if args.json:
        summary = validator.get_summary()
        print(json.dumps(summary, indent=2))
        return 0 if summary["valid"] else 1
    else:
        validator.print_report()
        return 0 if valid else 1


if __name__ == "__main__":
    sys.exit(main())


