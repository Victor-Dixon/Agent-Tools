# Agent Operating Cycle v2 - Integration Guide

## Overview

Upgraded agent operating cycle for higher throughput, lower drift, and measurable output.

## Components

### 1. Messaging Template (`CYCLE_V2`)

**Location:** `src/core/messaging_models_core.py`

**Usage:**
```python
from src.core.messaging_models_core import format_s2a_message

message = format_s2a_message(
    template_key="CYCLE_V2",
    recipient="Agent-7",
    mission="Implement feature X",
    dod="- Feature works\n- Tests pass\n- Documentation updated",
    ssot_constraint="web domain",
    v2_constraint="file <400 lines",
    touch_surface="src/web/routes/feature_x.py",
    validation_required="pytest tests/feature_x.py && lint",
    priority_level="P1",
    handoff_expectation="PR ready for review with tests passing",
    fallback="Escalate if blocked"
)
```

### 2. Status.json Schema Extension

**Location:** `tools/agent_cycle_v2_status_schema.json`

**Required cycle_v2 fields:**
- `cycle_id`: Unique cycle identifier
- `wip_limit`: Must be 1
- `current_wip`: Current work in progress (max 1)
- `micro_plan`: 3-bullet plan (change target, validation method, exit criteria)
- `dod`: Definition of Done (3 lines max)
- `dod_defined`: Whether DoD was provided or agent wrote it

**Optional but recommended:**
- `ssot_boundaries`: SSOT boundaries confirmed
- `v2_compliance_checked`: V2 compliance gate passed
- `execution_burst`: Execution details
- `mid_cycle_checkpoint`: Mid-cycle validation
- `validation`: Validation evidence
- `reporting`: Report details
- `documentation`: Documentation status
- `escalation`: Escalation details
- `success_metrics`: Success metrics

### 3. Report Validator

**Location:** `tools/agent_cycle_v2_report_validator.py`

**Usage:**
```bash
# Validate agent's status.json
python tools/agent_cycle_v2_report_validator.py \
  --agent Agent-7 \
  --format human

# Output JSON report
python tools/agent_cycle_v2_report_validator.py \
  --agent Agent-7 \
  --format json \
  --output validation_report.json
```

**Scoring:**
- **100 points total**
- Required fields: 2 points each
- Cycle v2 fields: 5-10 points each
- Validation evidence: 10 points
- Reporting completeness: 5 points per field
- Success metrics: 5-10 points each

**Grades:**
- A: 90-100%
- B: 80-89%
- C: 70-79%
- D: 60-69%
- F: <60%

## Messaging CLI Integration

### Sending CYCLE_V2 Messages

**Via messaging CLI (future enhancement):**
```bash
python -m src.services.messaging_cli \
  --agent Agent-7 \
  --cycle-v2 \
  --mission "Implement feature X" \
  --dod "- Feature works\n- Tests pass\n- Documentation updated" \
  --ssot web \
  --v2-constraint "file <400 lines" \
  --touch-surface "src/web/routes/feature_x.py" \
  --validation "pytest tests/feature_x.py && lint" \
  --priority P1 \
  --handoff "PR ready for review"
```

**Current workaround (direct Python):**
```python
from src.core.messaging_templates import render_message
from src.core.messaging_models_core import UnifiedMessage, MessageCategory

msg = UnifiedMessage(
    content="",
    sender="Captain Agent-4",
    recipient="Agent-7",
    message_type=UnifiedMessageType.CAPTAIN_TO_AGENT,
    category=MessageCategory.C2A
)

rendered = render_message(
    msg,
    template_key="CYCLE_V2",
    mission="Implement feature X",
    dod="- Feature works\n- Tests pass\n- Documentation updated",
    ssot_constraint="web domain",
    v2_constraint="file <400 lines",
    touch_surface="src/web/routes/feature_x.py",
    validation_required="pytest tests/feature_x.py && lint",
    priority_level="P1",
    handoff_expectation="PR ready for review with tests passing",
    fallback="Escalate if blocked"
)
```

## Agent Workflow

### 1. Receive CYCLE_V2 Message

Agent receives message with:
- Mission (single sentence)
- DoD (3 bullets max)
- Constraints (SSOT, V2, touch surface)
- Validation required
- Priority
- Handoff expectation

### 2. Start Cycle

**Update status.json:**
```json
{
  "cycle_v2": {
    "cycle_id": "cycle_2025-12-07_001",
    "wip_limit": 1,
    "current_wip": 1,
    "micro_plan": [
      "Change target: Add feature X endpoint",
      "Validation method: pytest + lint",
      "Exit criteria: Tests pass, PR ready"
    ],
    "dod": "- Feature works\n- Tests pass\n- Documentation updated",
    "dod_defined": true,
    "ssot_boundaries": ["web domain"],
    "v2_compliance_checked": true
  }
}
```

### 3. Execute

- Implement smallest viable change
- If scope expands: create subtask, notify Captain
- Keep changes localized

### 4. Mid-Cycle Checkpoint

**Update status.json:**
```json
{
  "cycle_v2": {
    "mid_cycle_checkpoint": {
      "checked": true,
      "aligned_with_dod": true,
      "within_ssot": true,
      "within_v2": true
    }
  }
}
```

### 5. Validate

**Run validation and capture evidence:**
```json
{
  "cycle_v2": {
    "validation": {
      "tests_run": true,
      "lint_run": true,
      "verification_run": true,
      "tests_added": false,
      "evidence": {
        "commands": [
          "pytest tests/feature_x.py",
          "ruff check src/web/routes/feature_x.py"
        ],
        "output_summary": "All tests passed, no lint errors",
        "test_results": "5 passed, 0 failed"
      }
    }
  }
}
```

### 6. Report

**Update reporting section:**
```json
{
  "cycle_v2": {
    "reporting": {
      "artifacts_changed": [
        "src/web/routes/feature_x.py",
        "tests/feature_x_test.py"
      ],
      "validation_evidence": "All tests passed, lint clean",
      "measurable_result": "Feature X endpoint functional, 5 tests passing",
      "next_action": "Create PR for review",
      "blockers": []
    }
  }
}
```

### 7. Document

**Update documentation section:**
```json
{
  "cycle_v2": {
    "documentation": {
      "status_json_updated": true,
      "status_value": "COMPLETE",
      "discord_devlog_posted": true
    }
  }
}
```

### 8. Success Metrics

**Update success metrics:**
```json
{
  "cycle_v2": {
    "success_metrics": {
      "output_delivered": true,
      "validation_evidence_included": true,
      "zero_drift": true,
      "wip_respected": true
    }
  }
}
```

## Validation

**Run validator after cycle:**
```bash
python tools/agent_cycle_v2_report_validator.py --agent Agent-7
```

**Expected output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AGENT CYCLE V2 VALIDATION REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Agent: Agent-7
Status File: agent_workspaces/Agent-7/status.json

SCORE: 95.00 / 100.00 (95.00%)
GRADE: A

Errors: 0
Warnings: 0

✅ No issues found!
```

## Benefits

✅ **Higher Throughput** - Clear DoD, focused execution, timeboxed bursts  
✅ **Lower Drift** - Mid-cycle checkpoints, SSOT boundaries, WIP limits  
✅ **Measurable Output** - Machine-gradable reports, validation evidence, success metrics  
✅ **Fast Unblock** - Clear escalation thresholds, proposed fixes  
✅ **Complete Tracking** - Full cycle lifecycle in status.json  

## Next Steps

1. **Add CLI support** - Enhance messaging CLI with `--cycle-v2` flag
2. **Auto-validation** - Run validator automatically after each cycle
3. **Dashboard integration** - Show cycle v2 metrics in project dashboard
4. **Pattern library** - Store successful cycle patterns in Swarm Brain

---

**Author:** Agent-8 (SSOT & System Integration Specialist)  
**Date:** 2025-12-07


