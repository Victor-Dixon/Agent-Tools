#!/usr/bin/env python3
"""
Agent Activity Detector
=======================

Detects agent activity for status monitoring and inactivity detection.
Wraps EnhancedAgentActivityDetector for use in status_change_monitor.

V2 Compliance: <300 lines, single responsibility.

Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-17
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class ActivitySummary:
    """Summary of agent activity detection."""
    is_active: bool
    inactivity_duration_minutes: float
    latest_activity_timestamp: Optional[float] = None
    activity_sources: list = field(default_factory=list)
    last_activity: Optional[datetime] = None

    def __post_init__(self):
        # Convert timestamp to datetime if timestamp exists
        if self.latest_activity_timestamp and not self.last_activity:
            self.last_activity = datetime.fromtimestamp(
                self.latest_activity_timestamp)


class AgentActivityDetector:
    """
    Detects agent activity for status monitoring.

    Provides simple interface for status_change_monitor to check agent activity.
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize activity detector."""
        self.workspace_root = workspace_root or Path(__file__).parent.parent
        self.agent_workspaces = self.workspace_root / "agent_workspaces"
        self.devlogs_dir = self.workspace_root / "devlogs"

    def detect_agent_activity(
        self,
        agent_id: str,
        lookback_minutes: int = 60
    ) -> ActivitySummary:
        """
        Detect agent activity within lookback window.

        Args:
            agent_id: Agent identifier (e.g., "Agent-1")
            lookback_minutes: How far back to check for activity

        Returns:
            ActivitySummary with is_active and inactivity_duration_minutes
        """
        current_time = time.time()
        lookback_seconds = lookback_minutes * 60
        latest_activity = None
        activity_sources = []

        # Check status.json modification time
        status_file = self.agent_workspaces / agent_id / "status.json"
        if status_file.exists():
            try:
                mtime = status_file.stat().st_mtime
                if mtime > (current_time - lookback_seconds):
                    if latest_activity is None or mtime > latest_activity:
                        latest_activity = mtime
                    activity_sources.append("status.json")
            except Exception:
                pass

        # Check devlogs directory for recent files
        if self.devlogs_dir.exists():
            try:
                for devlog_file in self.devlogs_dir.glob(f"*{agent_id.lower()}*"):
                    if devlog_file.is_file():
                        mtime = devlog_file.stat().st_mtime
                        if mtime > (current_time - lookback_seconds):
                            if latest_activity is None or mtime > latest_activity:
                                latest_activity = mtime
                            if "devlogs" not in activity_sources:
                                activity_sources.append("devlogs")
            except Exception:
                pass

        # Check inbox directory
        inbox_dir = self.agent_workspaces / agent_id / "inbox"
        if inbox_dir.exists():
            try:
                for inbox_file in inbox_dir.glob("*"):
                    if inbox_file.is_file():
                        mtime = inbox_file.stat().st_mtime
                        if mtime > (current_time - lookback_seconds):
                            if latest_activity is None or mtime > latest_activity:
                                latest_activity = mtime
                            if "inbox" not in activity_sources:
                                activity_sources.append("inbox")
            except Exception:
                pass

        # Calculate inactivity duration
        if latest_activity:
            inactivity_seconds = current_time - latest_activity
            inactivity_minutes = inactivity_seconds / 60.0
            is_active = inactivity_minutes < lookback_minutes
        else:
            # No activity found - assume inactive for full lookback period
            inactivity_minutes = float(lookback_minutes)
            is_active = False

        # Convert timestamp to datetime for last_activity
        last_activity_dt = None
        if latest_activity:
            last_activity_dt = datetime.fromtimestamp(latest_activity)

        return ActivitySummary(
            is_active=is_active,
            inactivity_duration_minutes=inactivity_minutes,
            latest_activity_timestamp=latest_activity,
            activity_sources=activity_sources,
            last_activity=last_activity_dt
        )
