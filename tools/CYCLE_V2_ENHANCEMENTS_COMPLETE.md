# Cycle V2 Enhancements - Complete ✅

## Summary

All three requested enhancements have been implemented:

1. ✅ **--cycle-v2 flag added to messaging CLI**
2. ✅ **Auto-validation post-cycle with score attachment**
3. ✅ **Cycle V2 metrics in dashboard/tasks CSV**

---

## 1. CLI Flag Implementation

### Usage

```bash
python -m src.services.messaging_cli \
  --cycle-v2 \
  --agent Agent-7 \
  --mission "Implement feature X" \
  --dod "- Feature works\n- Tests pass\n- Documentation updated" \
  --ssot-constraint "web domain" \
  --v2-constraint "file <400 lines" \
  --touch-surface "src/web/routes/feature_x.py" \
  --validation "pytest tests/feature_x.py && lint" \
  --priority-level P1 \
  --handoff "PR ready for review"
```

### Required Fields

- `--mission`: Single sentence mission statement
- `--dod`: Definition of Done (3 bullets, use `\n` for newlines)
- `--ssot-constraint`: SSOT domain constraint
- `--v2-constraint`: V2 compliance constraint
- `--touch-surface`: Files/modules to be changed
- `--validation`: Validation commands required
- `--handoff`: Handoff expectation

### Optional Fields

- `--priority-level`: P0 or P1 (default: P1)
- `--priority`: Message priority (normal/regular/urgent)

### Implementation

- **Location**: `src/services/messaging_infrastructure.py`
- **Handler**: `handle_cycle_v2_message()`
- **Template**: Uses `CYCLE_V2` template from `messaging_models_core.py`
- **Category**: C2A (Captain-to-Agent)

---

## 2. Auto-Validation Post-Cycle

### Usage

```bash
# Auto-validate and attach to status.json
python tools/auto_validate_cycle_v2.py --agent Agent-7

# Validate without attaching
python tools/auto_validate_cycle_v2.py --agent Agent-7 --no-attach

# Save report to file
python tools/auto_validate_cycle_v2.py --agent Agent-7 --output report.json
```

### Features

- **Automatic validation** after cycle completion
- **Score attachment** to `status.json` in `cycle_v2.validation_report`
- **Grading**: A-F based on score percentage
- **Error/warning reporting**

### Status.json Integration

Validation report is automatically attached to:

```json
{
  "cycle_v2": {
    "validation_report": {
      "score": 95.0,
      "max_score": 100.0,
      "score_percent": 95.0,
      "grade": "A",
      "errors_count": 0,
      "warnings_count": 0,
      "errors": [],
      "warnings": [],
      "validated_at": "2025-12-07T21:30:00.000000"
    }
  }
}
```

### Implementation

- **Location**: `tools/auto_validate_cycle_v2.py`
- **Validator**: Uses `CycleV2Validator` from `agent_cycle_v2_report_validator.py`
- **Integration**: Can be called manually or integrated into agent workflow

---

## 3. Dashboard Integration

### Metrics Collected

- **Active cycles**: Number of agents with active cycle_v2
- **Completed cycles**: Number of completed cycles
- **Total cycles**: Total cycle_v2 sections found
- **Average score**: Average validation score across all agents
- **Low scores**: Agents with scores < 70%

### Dashboard Summary

Added to `project_metrics_to_spreadsheet.py`:

```csv
Metric,Value,Status,Action
Cycle V2 Active Cycles,2 active,🟡 Active,Monitor cycle progress
Cycle V2 Average Score,87.5%,✅ Good,None
```

### Tasks CSV

Cycle V2 tasks automatically added:

```csv
category,task_type,task_payload,priority,status,agent,note
Cycle V2,update_file,Monitor 2 active Cycle V2 cycles (avg score: 87.5%),MEDIUM,pending,Agent-4,Active cycles: 2
Cycle V2,update_file,Improve Cycle V2 compliance for Agent-7 (current: 65.0%),MEDIUM,pending,Agent-7,Score: 65.0%
```

### Implementation

- **Location**: `tools/project_metrics_to_spreadsheet.py`
- **Function**: `collect_cycle_v2_metrics()`
- **Integration**: Automatically included in dashboard generation

---

## Complete Workflow

### 1. Send Cycle V2 Message

```bash
python -m src.services.messaging_cli \
  --cycle-v2 \
  --agent Agent-7 \
  --mission "Implement feature" \
  --dod "- Feature works\n- Tests pass" \
  --ssot-constraint "web" \
  --v2-constraint "file <400 lines" \
  --touch-surface "src/web/routes/feature.py" \
  --validation "pytest tests/feature.py" \
  --handoff "PR ready"
```

### 2. Agent Executes Cycle

Agent updates `status.json` with cycle_v2 section:
- Micro-plan
- DoD
- Execution details
- Validation evidence
- Reporting

### 3. Auto-Validate

```bash
python tools/auto_validate_cycle_v2.py --agent Agent-7
```

Score automatically attached to `status.json`.

### 4. Dashboard Generation

```bash
python tools/project_metrics_to_spreadsheet.py --output dashboard.csv
```

Cycle V2 metrics automatically included in:
- `dashboard_summary.csv` (summary metrics)
- `dashboard_tasks.csv` (actionable tasks)

---

## Benefits

✅ **Streamlined CLI** - Single command with all cycle fields  
✅ **Automatic Validation** - No manual validation needed  
✅ **Score Tracking** - Validation scores attached to reports  
✅ **Dashboard Visibility** - Cycle metrics in project dashboard  
✅ **Actionable Tasks** - Low-scoring cycles generate improvement tasks  

---

## Files Modified/Created

### Modified
- `src/services/messaging_infrastructure.py` - Added cycle-v2 handler
- `tools/project_metrics_to_spreadsheet.py` - Added cycle v2 metrics collection

### Created
- `tools/auto_validate_cycle_v2.py` - Auto-validation script
- `tools/CYCLE_V2_ENHANCEMENTS_COMPLETE.md` - This document

---

**Author:** Agent-8 (SSOT & System Integration Specialist)  
**Date:** 2025-12-07  
**Status:** ✅ Complete


