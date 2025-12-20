# Complete Integration Workflow - Debate + Cycle V2 + Spreadsheet

## Overview

Complete end-to-end integration connecting:
- **Debate System** → Execution tracking → Spreadsheet
- **Cycle V2** → Validation → Spreadsheet
- **Spreadsheet** → GitHub automation → PR creation

---

## Integration Architecture

```
┌─────────────────┐
│  Debate System  │
│  (decisions)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Execution       │
│ Tracker         │
│ (workflow_states)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Cycle V2       │
│  (status.json)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Spreadsheet    │
│  (CSV tasks)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GitHub         │
│  Automation     │
│  (PR creation)  │
└─────────────────┘
```

---

## 1. Debate → Spreadsheet Flow

### Step 1: Debate Decision
```bash
# Debate concludes, creates execution tracker
workflow_states/orientation_system_execution.json
```

### Step 2: Agent Execution
```bash
# Agent completes task, updates tracker
python tools/debate_execution_tracker_hook.py \
  --update \
  --topic orientation_system \
  --agent Agent-7 \
  --status completed \
  --artifact tools/agent_orient.py \
  --commit abc123def \
  --pr-url https://github.com/owner/repo/pull/123
```

### Step 3: Convert to Spreadsheet
```bash
# Export debate tasks to CSV
python tools/debate_execution_tracker_hook.py \
  --to-spreadsheet debate_tasks.csv
```

**Output:** `debate_tasks.csv` with all pending debate tasks

---

## 2. Cycle V2 → Spreadsheet Flow

### Step 1: Cycle V2 Message
```bash
# Captain sends Cycle V2 message
python -m src.services.messaging_cli \
  --cycle-v2 \
  --agent Agent-7 \
  --mission "Implement feature X" \
  --dod "- Feature works\n- Tests pass" \
  --ssot-constraint "web" \
  --v2-constraint "file <400 lines" \
  --touch-surface "src/web/routes/feature_x.py" \
  --validation "pytest tests/feature_x.py" \
  --handoff "PR ready"
```

### Step 2: Agent Executes Cycle
Agent updates `status.json` with `cycle_v2` section:
- Micro-plan
- DoD
- Execution details
- Validation evidence

### Step 3: Auto-Validate
```bash
# Auto-validate and attach score
python tools/auto_validate_cycle_v2.py --agent Agent-7
```

**Result:** Validation score attached to `status.json`

### Step 4: Convert to Spreadsheet
```bash
# Export Cycle V2 tasks to CSV
python tools/cycle_v2_to_spreadsheet_integration.py \
  --to-spreadsheet cycle_v2_tasks.csv
```

**Output:** `cycle_v2_tasks.csv` with all active Cycle V2 tasks

---

## 3. Unified Dashboard Generation

### Generate Complete Dashboard
```bash
python tools/project_metrics_to_spreadsheet.py --output dashboard.csv
```

**Outputs:**
- `dashboard_summary.csv` - At-a-glance metrics
- `dashboard_tasks.csv` - All actionable tasks (Debate + Cycle V2 + others)

**Includes:**
- Debate execution tasks (from `workflow_states/`)
- Cycle V2 tasks (from `status.json` files)
- V2 compliance tasks
- SSOT remediation tasks
- Tools consolidation tasks
- Test coverage tasks

---

## 4. Spreadsheet → GitHub Automation

### Execute Tasks from Spreadsheet
```bash
# Process all tasks from dashboard
python tools/spreadsheet_github_adapter.py \
  --file dashboard_tasks.csv \
  --repo owner/Agent_Cellphone_V2_Repository
```

**Process:**
1. Reads CSV tasks
2. Filters by `run_github=true`
3. Creates PRs for each task
4. Updates tracker with PR URLs

---

## Complete End-to-End Example

### Scenario: Feature Implementation via Cycle V2

**1. Captain sends Cycle V2:**
```bash
python -m src.services.messaging_cli \
  --cycle-v2 \
  --agent Agent-7 \
  --mission "Add user authentication endpoint" \
  --dod "- Endpoint works\n- Tests pass\n- Documentation updated" \
  --ssot-constraint "web domain" \
  --v2-constraint "file <400 lines" \
  --touch-surface "src/web/routes/auth.py" \
  --validation "pytest tests/auth_test.py && lint" \
  --handoff "PR ready for review"
```

**2. Agent executes:**
- Updates `status.json` with cycle_v2 section
- Implements feature
- Runs validation
- Updates reporting section

**3. Auto-validate:**
```bash
python tools/auto_validate_cycle_v2.py --agent Agent-7
```
**Result:** Score 95% (A) attached to status.json

**4. Update tracker with artifacts:**
```bash
python tools/cycle_v2_to_spreadsheet_integration.py \
  --update \
  --agent Agent-7 \
  --status completed \
  --score 95.0 \
  --artifact src/web/routes/auth.py \
  --artifact tests/auth_test.py \
  --commit abc123def \
  --pr-url https://github.com/owner/repo/pull/456
```

**5. Generate dashboard:**
```bash
python tools/project_metrics_to_spreadsheet.py --output dashboard.csv
```
**Result:** Cycle V2 task appears in `dashboard_tasks.csv`

**6. Execute via spreadsheet (if needed):**
```bash
# If task needs GitHub automation
python tools/spreadsheet_github_adapter.py \
  --file dashboard_tasks.csv \
  --repo owner/Agent_Cellphone_V2_Repository
```

---

## Integration Points

### 1. Debate Execution Tracker
- **Location**: `workflow_states/{topic}_execution.json`
- **Hook**: `tools/debate_execution_tracker_hook.py`
- **Spreadsheet**: `debate_trackers_to_spreadsheet_tasks()`

### 2. Cycle V2 Tracker
- **Location**: `agent_workspaces/{agent}/status.json` → `cycle_v2`
- **Hook**: `tools/cycle_v2_to_spreadsheet_integration.py`
- **Spreadsheet**: `cycle_v2_to_spreadsheet_tasks()`

### 3. Unified Dashboard
- **Location**: `tools/project_metrics_to_spreadsheet.py`
- **Collects**: Debate + Cycle V2 + V2 compliance + SSOT + Tools + Tests
- **Output**: `dashboard_summary.csv` + `dashboard_tasks.csv`

### 4. GitHub Automation
- **Location**: `tools/spreadsheet_github_adapter.py`
- **Input**: CSV tasks with `run_github=true`
- **Output**: PRs created, trackers updated

---

## Benefits

✅ **Unified Workflow** - Debate + Cycle V2 → Spreadsheet → GitHub  
✅ **Complete Tracking** - Artifacts, commits, PRs, validation scores  
✅ **Dashboard Visibility** - All tasks in one place  
✅ **Automated Execution** - Batch PR creation from spreadsheet  
✅ **Evidence-Based** - All outcomes tracked with metrics  

---

## Usage Summary

### Debate Tasks
```bash
# Update tracker
python tools/debate_execution_tracker_hook.py --update --topic X --agent Y

# Export to spreadsheet
python tools/debate_execution_tracker_hook.py --to-spreadsheet debate.csv
```

### Cycle V2 Tasks
```bash
# Send cycle
python -m src.services.messaging_cli --cycle-v2 --agent X --mission Y ...

# Validate
python tools/auto_validate_cycle_v2.py --agent X

# Update tracker
python tools/cycle_v2_to_spreadsheet_integration.py --update --agent X --status completed

# Export to spreadsheet
python tools/cycle_v2_to_spreadsheet_integration.py --to-spreadsheet cycle_v2.csv
```

### Unified Dashboard
```bash
# Generate complete dashboard (includes Debate + Cycle V2)
python tools/project_metrics_to_spreadsheet.py --output dashboard.csv
```

### GitHub Automation
```bash
# Execute tasks from spreadsheet
python tools/spreadsheet_github_adapter.py --file dashboard_tasks.csv --repo owner/repo
```

---

**Author:** Agent-8 (SSOT & System Integration Specialist)  
**Date:** 2025-12-07  
**Status:** ✅ Complete Integration


