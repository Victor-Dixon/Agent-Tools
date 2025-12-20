# Project Dashboard Workflow - At-a-Glance Operation

## Overview

Convert project state and scanner results into spreadsheet format for visual overview and actionable automation.

## Workflow

### Step 1: Collect Project Metrics

```bash
# Generate project metrics and dashboard
python tools/project_metrics_to_spreadsheet.py \
  --output project_dashboard.csv \
  --format both
```

This creates:
- `project_dashboard_metrics.json` - Raw metrics data
- `project_dashboard_summary.csv` - At-a-glance dashboard
- `project_dashboard_tasks.csv` - Actionable tasks

### Step 2: Review Dashboard

Open `project_dashboard_summary.csv` to see:
- V2 Compliance status
- SSOT tagging progress
- Tools registration status
- Test coverage percentage
- Consolidation opportunities

### Step 3: Review Actionable Tasks

Open `project_dashboard_tasks.csv` to see:
- Tasks ready for automation
- Priority levels
- Estimated effort
- Agent assignments

### Step 4: Execute Tasks via Spreadsheet

```bash
# Process tasks and create PRs
python tools/spreadsheet_github_adapter.py \
  --file project_dashboard_tasks.csv \
  --repo owner/Agent_Cellphone_V2_Repository \
  --output task_results.json
```

## Integration with Cycle Planner

### Add to Cycle Planner

The spreadsheet adapter can be added as a cycle planner tool:

```json
{
  "contract_id": "A8-SPREADSHEET-AUTOMATION-001",
  "title": "Spreadsheet-Driven Project Automation",
  "description": "Use spreadsheet adapter to automate project tasks from dashboard metrics",
  "priority": "MEDIUM",
  "points": 200,
  "status": "PENDING",
  "tools": [
    "tools/project_metrics_to_spreadsheet.py",
    "tools/spreadsheet_github_adapter.py",
    "tools/generate_tools_consolidation_prs.py"
  ],
  "workflow": [
    "1. Generate project dashboard",
    "2. Review actionable tasks",
    "3. Execute via spreadsheet adapter",
    "4. Track results"
  ]
}
```

## Dashboard Columns

### Summary Sheet
- **Metric**: Metric name
- **Value**: Current value
- **Status**: Visual status (✅/🟡/🔴)
- **Action**: Recommended action

### Tasks Sheet
- **category**: Task category
- **task_type**: `open_pr` | `create_issue` | `update_file`
- **task_payload**: Task description
- **priority**: `HIGH` | `MEDIUM` | `LOW`
- **status**: `pending` | `running` | `done` | `error`
- **run_github**: `true` | `false` (trigger)
- **result_url**: PR/issue URL (auto-populated)
- **estimated_effort**: Time estimate
- **agent**: Assigned agent

## Example: Complete Workflow

### 1. Generate Dashboard
```bash
python tools/project_metrics_to_spreadsheet.py --output dashboard.csv
```

### 2. Review Tasks
Open `dashboard_tasks.csv` and set `run_github = true` for tasks to execute

### 3. Execute Automation
```bash
python tools/spreadsheet_github_adapter.py \
  --file dashboard_tasks.csv \
  --repo owner/repo
```

### 4. Review Results
Check `task_results.json` for PR URLs and status

## Benefits

✅ **At-a-Glance Overview** - See entire project state in one spreadsheet  
✅ **Actionable** - Directly convert metrics to tasks  
✅ **Automated** - Execute tasks via spreadsheet adapter  
✅ **Trackable** - All metrics and tasks in one place  
✅ **Reusable** - Regenerate dashboard anytime  

## Future Enhancements

- [ ] Real-time metrics collection
- [ ] Google Sheets integration
- [ ] Auto-refresh dashboard
- [ ] Webhook triggers
- [ ] Agent status integration
- [ ] Cycle planner integration

---

**Author:** Agent-8 (SSOT & System Integration Specialist)  
**Date:** 2025-12-07


