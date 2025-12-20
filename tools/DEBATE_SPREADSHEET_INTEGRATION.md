# Debate System → Spreadsheet Integration

## Overview

Complete integration between debate system and spreadsheet automation workflow.

## Integration Points

### 1. Execution Tracker Updates

**When agents complete debate tasks:**
```bash
python tools/debate_execution_tracker_hook.py \
  --update \
  --topic orientation_system \
  --agent Agent-7 \
  --status completed \
  --artifact tools/agent_orient.py \
  --commit abc123def \
  --pr-url https://github.com/owner/repo/pull/123 \
  --evidence "Tool created and tested"
```

**Updates:**
- `workflow_states/{topic}_execution.json`
- Appends artifact paths
- Records commit hash
- Stores PR URL
- Marks agent task as completed

### 2. Debate Tasks → Spreadsheet

**Convert debate trackers to spreadsheet tasks:**
```bash
python tools/debate_execution_tracker_hook.py \
  --to-spreadsheet debate_tasks.csv \
  --include-completed false
```

**Output:** CSV with all pending debate tasks ready for automation

### 3. Dashboard Integration

**Project dashboard automatically includes debate metrics:**
```bash
python tools/project_metrics_to_spreadsheet.py --output dashboard.csv
```

**Includes:**
- Debate execution status in summary
- Pending debate tasks in tasks CSV
- Active debates count
- Completed debates count

## Complete Workflow

### Step 1: Debate Decision → Execution Tracker
```
Debate concludes → activate_debate_decision() →
Creates workflow_states/{topic}_execution.json →
Sends S2A DEBATE_CYCLE messages to agents
```

### Step 2: Agent Execution
```
Agent receives DEBATE_CYCLE message →
Executes assigned slice →
Updates tracker with artifacts/commits →
Marks task complete
```

### Step 3: Tracker → Spreadsheet
```
workflow_states/{topic}_execution.json →
debate_trackers_to_spreadsheet_tasks() →
debate_tasks.csv (ready for automation)
```

### Step 4: Spreadsheet Automation
```
debate_tasks.csv →
spreadsheet_github_adapter.py →
Creates PRs for debate outcomes →
Updates tracker with PR URLs
```

## Integration Hooks

### Hook 1: Agent Completion
```python
from tools.debate_execution_tracker_hook import update_execution_tracker

# When agent completes debate task
update_execution_tracker(
    topic="orientation_system",
    agent_id="Agent-7",
    status="completed",
    artifact_paths=["tools/agent_orient.py"],
    commit_hash="abc123def",
    pr_url="https://github.com/owner/repo/pull/123"
)
```

### Hook 2: Dashboard Generation
```python
# Automatically includes debate metrics
metrics = collect_project_metrics()
# metrics["debate_execution"] contains:
# - active_debates
# - completed_debates
# - pending_tasks
# - total_trackers
```

### Hook 3: Task Generation
```python
# Pulls actual debate tasks into spreadsheet
debate_tasks = debate_trackers_to_spreadsheet_tasks(
    output_file="debate_tasks.csv",
    include_completed=False
)
# Returns list of tasks ready for spreadsheet adapter
```

## Benefits

✅ **Seamless Flow** - Debate → Execution → Spreadsheet → Automation  
✅ **Complete Tracking** - Artifacts, commits, PRs all tracked  
✅ **Dashboard Visibility** - Debate status in project dashboard  
✅ **Automated Execution** - Debate tasks can be batch-processed via spreadsheet  
✅ **Evidence-Based** - All outcomes tracked with artifacts and commits  

## Example: Complete Cycle

1. **Debate concludes** → `activate_debate_decision()` called
2. **Execution tracker created** → `workflow_states/orientation_system_execution.json`
3. **Agents receive S2A messages** → Execute assigned slices
4. **Agents update tracker** → `update_execution_tracker()` with artifacts
5. **Dashboard generated** → Includes debate metrics
6. **Tasks exported** → `debate_trackers_to_spreadsheet_tasks()` → CSV
7. **PRs created** → `spreadsheet_github_adapter.py` processes CSV
8. **Tracker updated** → PR URLs added to execution tracker

---

**Author:** Agent-8 (SSOT & System Integration Specialist)  
**Date:** 2025-12-07


