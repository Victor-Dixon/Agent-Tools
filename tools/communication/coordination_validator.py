#!/usr/bin/env python3
"""
Unified Coordination Validator
================================

Consolidates coordination system validation and tracker SSOT validation.
Combines functionality from coordination_validator.py and validate_trackers.py.

Features:
- Coordination system validation
- Tracker SSOT validation
- Coordination pattern validation

V2 Compliance: ≤300 lines, ≤200 lines/class, ≤30 lines/function
Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-03
Task: Phase 2 Tools Consolidation - Communication Validation
"""

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.utils.validation_utils import print_validation_report


@dataclass
class TrackerSnapshot:
    """Snapshot of tracker state for comparison."""
    repos_before: Optional[int] = None
    repos_after: Optional[int] = None
    repos_reduction: Optional[int] = None
    batch1_complete: bool = False
    batch2_complete: bool = False
    phase0_complete: bool = False
    skipped_repos: List[str] = field(default_factory=list)
    source_file: str = ""


class CoordinationValidator:
    """Unified coordination and tracker validation."""

    def __init__(self):
        """Initialize validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_coordination_system(self, system_data: Dict[str, Any]) -> bool:
        """Validate coordination system configuration."""
        valid = True
        if "agents" in system_data:
            agent_data = system_data["agents"]
            for agent_id, agent_info in agent_data.items():
                if not isinstance(agent_info, dict):
                    self.errors.append(
                        f"Invalid agent configuration for {agent_id}"
                    )
                    valid = False
                    continue
                required_fields = ["description", "coords"]
                for field in required_fields:
                    if field not in agent_info:
                        self.errors.append(
                            f"Missing required field '{field}' for agent {agent_id}"
                        )
                        valid = False
        return valid

    def validate_message_structure(self, message_data: Dict[str, Any]) -> bool:
        """Validate message structure."""
        valid = True
        required_fields = ["content", "sender", "recipient"]
        for field in required_fields:
            if field not in message_data:
                self.errors.append(f"Missing required field: {field}")
                valid = False
        if "content" in message_data and not isinstance(
            message_data["content"], str
        ):
            self.errors.append("Message content must be a string")
            valid = False
        return valid

    def parse_tracker_file(self, file_path: Path) -> TrackerSnapshot:
        """Parse consolidation tracker markdown file."""
        content = file_path.read_text(encoding="utf-8")
        snapshot = TrackerSnapshot(source_file=file_path.name)

        repos_before_match = re.search(
            r'before.*consolidation[:\s]+(\d+)\s+repositor', content, re.IGNORECASE
        )
        if repos_before_match:
            snapshot.repos_before = int(repos_before_match.group(1))

        repos_after_match = re.search(
            r'(?:current count|after.*progress)[:\s]+(\d+)\s+repositor',
            content, re.IGNORECASE
        )
        if repos_after_match:
            snapshot.repos_after = int(repos_after_match.group(1))

        batch1_match = re.search(
            r'batch\s*1[:\s]+.*?100%?\s+complete', content, re.IGNORECASE
        )
        snapshot.batch1_complete = bool(batch1_match)

        batch2_match = re.search(
            r'batch\s*2[:\s]+.*?100%?\s+complete', content, re.IGNORECASE
        )
        snapshot.batch2_complete = bool(batch2_match)

        phase0_match = re.search(
            r'phase\s*0[:\s]+.*?(?:100%?\s+complete|effectively\s+100%)',
            content, re.IGNORECASE
        )
        snapshot.phase0_complete = bool(phase0_match)

        skipped_match = re.search(
            r'Skipped`?.*?:(.+?)(?:---|\Z)', content, re.DOTALL | re.IGNORECASE
        )
        if skipped_match:
            skipped_list = skipped_match.group(1)
            snapshot.skipped_repos = re.findall(
                r'✅\s*(.+?)\s*→', skipped_list
            )

        return snapshot

    def validate_trackers_consistency(
        self, tracker1_path: Path, tracker2_path: Path
    ) -> bool:
        """Validate consistency between two tracker files."""
        snapshot1 = self.parse_tracker_file(tracker1_path)
        snapshot2 = self.parse_tracker_file(tracker2_path)
        valid = True

        if snapshot1.repos_before != snapshot2.repos_before:
            self.errors.append(
                f"Repo 'before' count mismatch: "
                f"{snapshot1.repos_before} vs {snapshot2.repos_before}"
            )
            valid = False

        if snapshot1.repos_after != snapshot2.repos_after:
            self.errors.append(
                f"Repo 'current' count mismatch: "
                f"{snapshot1.repos_after} vs {snapshot2.repos_after}"
            )
            valid = False

        if snapshot1.batch1_complete != snapshot2.batch1_complete:
            self.errors.append(
                f"Batch 1 completion mismatch: "
                f"{snapshot1.source_file} vs {snapshot2.source_file}"
            )
            valid = False

        skipped1 = set(snapshot1.skipped_repos)
        skipped2 = set(snapshot2.skipped_repos)
        if skipped1 != skipped2:
            if skipped1 - skipped2:
                self.errors.append(
                    f"Skipped repos in {snapshot1.source_file} but not in "
                    f"{snapshot2.source_file}: {', '.join(skipped1 - skipped2)}"
                )
                valid = False

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
        """Print validation report using SSOT utility."""
        print_validation_report(
            errors=self.errors,
            warnings=self.warnings,
        )


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Unified coordination validator"
    )
    parser.add_argument(
        "--coordination", type=Path, help="JSON file with coordination system data"
    )
    parser.add_argument(
        "--tracker1", type=Path, help="First tracker file for consistency check"
    )
    parser.add_argument(
        "--tracker2", type=Path, help="Second tracker file for consistency check"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    validator = CoordinationValidator()

    valid = True
    if args.coordination:
        with open(args.coordination, "r", encoding="utf-8") as f:
            data = json.load(f)
        valid = validator.validate_coordination_system(data)
    elif args.tracker1 and args.tracker2:
        valid = validator.validate_trackers_consistency(args.tracker1, args.tracker2)
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


