#!/usr/bin/env python3
"""
Achievement Documentation Templates
====================================

Template generators for milestone and enhancement request documentation.

Used by: tools/devops/documentation_assistant.py
"""

from datetime import datetime


def create_milestone_template(agent_id: str, achievement: str) -> str:
    """Generate an agent milestone documentation template.

    Args:
        agent_id: The agent identifier (e.g., Agent-7)
        achievement: Description of the achievement

    Returns:
        Formatted markdown template string
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_only = datetime.now().strftime("%Y-%m-%d")

    return f"""# 🏆 Agent Milestone: {agent_id}

**Achievement:** {achievement}
**Date:** {timestamp}

## Summary

{agent_id} has achieved a significant milestone: **{achievement}**

## Achievement Details

| Field | Value |
|-------|-------|
| Agent | {agent_id} |
| Achievement | {achievement} |
| Date Achieved | {date_only} |
| Verified By | _Verification pending_ |

## Context

_Describe the context and significance of this achievement_

## Impact

- **Team Impact:** _How this benefits the swarm_
- **Project Impact:** _How this advances project goals_
- **Technical Impact:** _Technical improvements achieved_

## Related Work

- Related missions: _Link to missions_
- Related PRs: _Link to pull requests_
- Related documentation: _Link to docs_

## Recognition

🎉 Congratulations to {agent_id} for this outstanding achievement!

---
🐝 WE. ARE. SWARM. ⚡🔥
"""


def create_enhancement_request_template(name: str, priority: str = "MEDIUM") -> str:
    """Generate an enhancement request documentation template.

    Args:
        name: Name of the proposed enhancement
        priority: Priority level (LOW, MEDIUM, HIGH)

    Returns:
        Formatted markdown template string
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_only = datetime.now().strftime("%Y-%m-%d")

    # Priority emoji mapping
    priority_emoji = {
        "LOW": "🟢",
        "MEDIUM": "🟡",
        "HIGH": "🔴"
    }
    emoji = priority_emoji.get(priority.upper(), "🟡")

    return f"""# Enhancement Request: {name}

**Requested:** {timestamp}
**Priority:** {emoji} {priority.upper()}
**Status:** 📋 Proposed

## Summary

_Brief description of the enhancement_

## Enhancement Details

| Field | Value |
|-------|-------|
| Name | {name} |
| Priority | {priority.upper()} |
| Requested Date | {date_only} |
| Requested By | _Agent ID_ |
| Target Version | _TBD_ |

## Problem Statement

_Describe the problem this enhancement solves_

## Proposed Solution

_Describe the proposed solution in detail_

## Benefits

- **Benefit 1:** _Description_
- **Benefit 2:** _Description_
- **Benefit 3:** _Description_

## Implementation Considerations

### Technical Requirements
- _Requirement 1_
- _Requirement 2_

### Dependencies
- _Dependency 1_
- _Dependency 2_

### Estimated Effort
- **Complexity:** _Low/Medium/High_
- **Estimated Time:** _TBD_

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Alternative 1 | _Pros_ | _Cons_ | Not selected |
| Alternative 2 | _Pros_ | _Cons_ | Not selected |

## Acceptance Criteria

- [ ] Criterion 1: _Define success criteria_
- [ ] Criterion 2: _Define success criteria_
- [ ] Criterion 3: _Define success criteria_

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Risk 1 | _Low/Med/High_ | _Low/Med/High_ | _Mitigation strategy_ |

---
🐝 WE. ARE. SWARM. ⚡🔥
"""
