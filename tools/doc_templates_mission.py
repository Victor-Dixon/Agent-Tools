#!/usr/bin/env python3
"""
Mission Documentation Templates
===============================

Template generators for mission tracking and completion reports.

Used by: tools/devops/documentation_assistant.py
"""

from datetime import datetime


def create_mission_tracking_template(mission_name: str) -> str:
    """Generate a mission tracking document template.

    Args:
        mission_name: The mission identifier (e.g., C-057)

    Returns:
        Formatted markdown template string
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_only = datetime.now().strftime("%Y-%m-%d")

    return f"""# Mission Tracking: {mission_name}

**Created:** {timestamp}
**Status:** 🟡 In Progress

## Mission Overview

| Field | Value |
|-------|-------|
| Mission ID | {mission_name} |
| Start Date | {date_only} |
| Target Completion | TBD |
| Assigned Agents | TBD |

## Objectives

- [ ] Objective 1: _Define primary goal_
- [ ] Objective 2: _Define secondary goal_
- [ ] Objective 3: _Define tertiary goal_

## Progress Log

### {date_only}
- Mission initiated
- Initial planning phase

## Blockers & Risks

| Blocker | Severity | Status | Resolution |
|---------|----------|--------|------------|
| None identified | - | - | - |

## Resources

- Related documentation: _Link here_
- Dependencies: _List dependencies_

## Notes

_Add mission-specific notes here_

---
🐝 WE. ARE. SWARM. ⚡🔥
"""


def create_completion_report_template(mission_name: str) -> str:
    """Generate a mission completion report template.

    Args:
        mission_name: The mission identifier (e.g., C-057)

    Returns:
        Formatted markdown template string
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_only = datetime.now().strftime("%Y-%m-%d")

    return f"""# Mission Completion Report: {mission_name}

**Completed:** {timestamp}
**Status:** ✅ Complete

## Executive Summary

Mission {mission_name} has been successfully completed.

## Objectives Achieved

- [x] Objective 1: _Describe achievement_
- [x] Objective 2: _Describe achievement_
- [x] Objective 3: _Describe achievement_

## Key Deliverables

| Deliverable | Status | Notes |
|-------------|--------|-------|
| Deliverable 1 | ✅ Complete | _Details_ |
| Deliverable 2 | ✅ Complete | _Details_ |

## Metrics & Results

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Metric 1 | TBD | TBD | ✅ |
| Metric 2 | TBD | TBD | ✅ |

## Lessons Learned

### What Worked Well
- _List successes_

### What Could Be Improved
- _List improvements_

## Follow-up Actions

- [ ] Action 1: _Describe follow-up_
- [ ] Action 2: _Describe follow-up_

## Agent Contributions

| Agent | Role | Contribution |
|-------|------|--------------|
| Agent-X | Lead | _Describe_ |

## Timeline

| Milestone | Date | Status |
|-----------|------|--------|
| Mission Start | {date_only} | ✅ |
| Mission Complete | {date_only} | ✅ |

---
🐝 WE. ARE. SWARM. ⚡🔥
"""
