#!/usr/bin/env python3
"""
Unified Agent Status Validator - Enhanced with Multi-Source Activity Detection
==============================================================================

Consolidates agent status validation tools with enhanced activity detection.
Uses multi-source activity detection to reduce false stall detections.

Features:
- Multi-source activity detection (status.json, files, devlogs, git, inbox, etc.)
- Agent status staleness detection (hardened with activity verification)
- Quick status verification
- Status monitor validation
- Health checks

V2 Compliance: ≤300 lines, ≤200 lines/class, ≤30 lines/function
Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-03
Updated: 2025-12-11 - Added multi-source activity detection
Task: Phase 2 Tools Consolidation - Communication Validation
"""

import json
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.constants.agent_constants import AGENT_LIST as AGENTS

logger = logging.getLogger(__name__)

STALE_THRESHOLD_HOURS = 6
RECENT_THRESHOLD_HOURS = 2
ACTIVITY_LOOKBACK_MINUTES = 60  # Check activity within last hour


class AgentStatusValidator:
    """Unified agent status validation with multi-source activity detection."""

    def __init__(self, workspace_root: Optional[Path] = None, use_activity_detection: bool = True):
        """Initialize validator.

        Args:
            workspace_root: Root workspace directory
            use_activity_detection: Enable multi-source activity detection (default: True)
        """
        if workspace_root is None:
            workspace_root = Path(__file__).parent.parent.parent
        self.workspace_root = workspace_root
        self.agent_workspaces = workspace_root / "agent_workspaces"
        self.use_activity_detection = use_activity_detection
        self.errors: List[str] = []
        self.warnings: List[str] = []

        # Initialize activity detector if enabled
        self.activity_detector = None
        if use_activity_detection:
            try:
                from tools.agent_activity_detector import AgentActivityDetector
                self.activity_detector = AgentActivityDetector(workspace_root)
            except ImportError:
                logger.warning(
                    "AgentActivityDetector not available, using status.json only")
                self.use_activity_detection = False

    def check_status_staleness(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Check all agent status files for staleness with multi-source activity verification."""
        stale_agents = []
        current_agents = []

        for agent_id in AGENTS:
            status_file = self.agent_workspaces / agent_id / "status.json"

            if not status_file.exists():
                stale_agents.append({
                    "agent_id": agent_id,
                    "status": "MISSING",
                    "last_updated": None,
                    "hours_old": None,
                    "activity_verified": False
                })
                continue

            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    status = json.load(f)

                last_updated_str = status.get("last_updated", "")
                if not last_updated_str:
                    stale_agents.append({
                        "agent_id": agent_id,
                        "status": "NO_TIMESTAMP",
                        "last_updated": None,
                        "hours_old": None,
                        "activity_verified": False
                    })
                    continue

                last_updated = self._parse_timestamp(last_updated_str)
                if last_updated is None:
                    stale_agents.append({
                        "agent_id": agent_id,
                        "status": "INVALID_TIMESTAMP",
                        "last_updated": last_updated_str,
                        "hours_old": None,
                        "activity_verified": False
                    })
                    continue

                hours_old = (datetime.now() -
                             last_updated).total_seconds() / 3600

                # Enhanced: Check multi-source activity if status appears stale
                is_actually_active = False
                activity_sources = []
                if hours_old > STALE_THRESHOLD_HOURS and self.use_activity_detection:
                    is_actually_active, activity_sources = self._verify_agent_activity(
                        agent_id, last_updated
                    )

                # Only mark as stale if status is old AND no recent activity detected
                if hours_old > STALE_THRESHOLD_HOURS and not is_actually_active:
                    stale_agents.append({
                        "agent_id": agent_id,
                        "status": "STALE",
                        "last_updated": last_updated_str,
                        "hours_old": round(hours_old, 1),
                        "activity_verified": True,
                        "activity_sources": activity_sources
                    })
                else:
                    agent_info = {
                        "agent_id": agent_id,
                        "last_updated": last_updated_str,
                        "hours_old": round(hours_old, 1)
                    }
                    if is_actually_active:
                        agent_info["activity_verified"] = True
                        agent_info["activity_sources"] = activity_sources
                        agent_info["note"] = "Status stale but recent activity detected"
                    current_agents.append(agent_info)

            except Exception as e:
                stale_agents.append({
                    "agent_id": agent_id,
                    "status": "ERROR",
                    "last_updated": None,
                    "hours_old": None,
                    "error": str(e),
                    "activity_verified": False
                })

        return stale_agents, current_agents

    def _verify_agent_activity(
        self, agent_id: str, status_timestamp: datetime
    ) -> Tuple[bool, List[str]]:
        """Verify agent has recent activity from multiple sources.

        Returns:
            Tuple of (is_active, activity_sources)
        """
        if not self.activity_detector:
            return False, []

        try:
            # Check activity within lookback window
            summary = self.activity_detector.detect_agent_activity(
                agent_id,
                lookback_minutes=ACTIVITY_LOOKBACK_MINUTES,
                use_events=True
            )

            # Agent is active if activity detected OR if last activity is more recent than status
            is_active = summary.is_active
            if summary.last_activity and status_timestamp:
                # Also check if activity is more recent than status timestamp
                if summary.last_activity > status_timestamp:
                    is_active = True

            return is_active, summary.activity_sources

        except Exception as e:
            logger.warning(f"Error verifying activity for {agent_id}: {e}")
            return False, []

    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string."""
        formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        return None

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status.json for specific agent."""
        status_path = self.agent_workspaces / agent_id / "status.json"
        if not status_path.exists():
            return None
        try:
            with open(status_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def validate_status_health(self) -> bool:
        """Validate overall status health."""
        stale_agents, current_agents = self.check_status_staleness()
        valid = True

        if stale_agents:
            for agent in stale_agents:
                if agent["status"] == "MISSING":
                    self.errors.append(
                        f"{agent['agent_id']}: status.json missing")
                    valid = False
                elif agent["status"] == "STALE":
                    hours = agent.get("hours_old", 0)
                    self.warnings.append(
                        f"{agent['agent_id']}: Status stale ({hours}h old)"
                    )

        return valid

    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        stale_agents, current_agents = self.check_status_staleness()
        return {
            "valid": len(stale_agents) == 0,
            "stale_count": len(stale_agents),
            "current_count": len(current_agents),
            "stale_agents": stale_agents,
            "current_agents": current_agents,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def print_report(self) -> None:
        """Print validation report."""
        stale_agents, current_agents = self.check_status_staleness()

        if stale_agents:
            print("⚠️  STALE AGENTS:")
            print("=" * 60)
            for agent in stale_agents:
                status = agent["status"]
                hours = agent.get("hours_old", "N/A")
                last_up = agent.get("last_updated", "N/A")
                print(f"  {agent['agent_id']}: {status}")
                if hours != "N/A" and hours is not None:
                    print(f"    Last updated: {last_up} ({hours} hours ago)")
                if agent.get("activity_verified"):
                    sources = agent.get("activity_sources", [])
                    if sources:
                        print(
                            f"    ⚠️  No recent activity from: {', '.join(sources[:3])}")
                    else:
                        print(f"    ⚠️  No recent activity detected from any source")
                if "error" in agent:
                    print(f"    Error: {agent['error']}")
            print()
        else:
            print("✅ All agents have current status files!\n")

        if current_agents:
            print("✅ CURRENT AGENTS:")
            print("=" * 60)
            for agent in current_agents:
                hours = agent["hours_old"]
                note = agent.get("note", "")
                sources = agent.get("activity_sources", [])
                print(
                    f"  {agent['agent_id']}: {agent['last_updated']} ({hours}h ago)")
                if note:
                    print(f"    ℹ️  {note}")
                if sources:
                    print(f"    📊 Activity sources: {', '.join(sources[:5])}")
            print()


def main() -> int:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Unified agent status validator"
    )
    parser.add_argument(
        "--agent", help="Check specific agent status"
    )
    parser.add_argument(
        "--all", action="store_true", help="Check all agents"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )
    parser.add_argument(
        "--no-activity-check", action="store_true",
        help="Disable multi-source activity detection (use status.json only)"
    )

    args = parser.parse_args()
    validator = AgentStatusValidator(
        use_activity_detection=not args.no_activity_check)

    if args.agent:
        status = validator.get_agent_status(args.agent)
        if status:
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                print(f"✅ {args.agent} status found")
                print(f"   Last updated: {status.get('last_updated', 'N/A')}")
        else:
            print(f"❌ {args.agent} status not found")
            return 1
    elif args.all:
        valid = validator.validate_status_health()
        if args.json:
            summary = validator.get_summary()
            print(json.dumps(summary, indent=2))
            return 0 if summary["valid"] else 1
        else:
            validator.print_report()
            return 0 if valid else 1
    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
