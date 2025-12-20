# Tools Consolidation Workflow - Spreadsheet-Driven

## Overview

Use the spreadsheet GitHub adapter to automate PR creation for tools consolidation tasks.

## Workflow

### Step 1: Generate Consolidation Tasks Spreadsheet

```bash
# Auto-generate from known candidates
python tools/generate_tools_consolidation_prs.py \
  --auto-generate \
  --repo owner/repo-name \
  --output tools_consolidation_tasks.csv

# Or load from analysis file
python tools/generate_tools_consolidation_prs.py \
  --analysis-file tools_analysis.json \
  --repo owner/repo-name \
  --output tools_consolidation_tasks.csv
```

This creates a CSV file with PR tasks like:
```csv
task_type,task_payload,run_github,status,result_url,error_msg,updated_at,repo,branch,title,body
open_pr,"Consolidate 3 validation tools into unified_validator.py...",true,pending,,,owner/repo,consolidate/validation-20251207,"Consolidate validation tools → unified_validator.py","Consolidate validation tools into unified_validator.py"
```

### Step 2: Review and Edit Spreadsheet

Open `tools_consolidation_tasks.csv` and:
- Review tasks
- Add/edit task details
- Set `run_github` to `true` for tasks to execute
- Add custom branches, titles, or descriptions

### Step 3: Execute PR Creation

```bash
# Process spreadsheet and create PRs
python tools/spreadsheet_github_adapter.py \
  --file tools_consolidation_tasks.csv \
  --repo owner/repo-name \
  --output consolidation_results.json
```

This will:
1. Read each row with `run_github == true`
2. Create PRs using `unified_github_pr_creator.py`
3. Write results back to CSV (or output JSON)
4. Update `status`, `result_url`, and `updated_at` columns

### Step 4: Review Results

Check `consolidation_results.json` or updated CSV for:
- PR URLs
- Error messages (if any)
- Status of each task

## Example: Batch Tools Consolidation

### Scenario: Consolidate 10 validation tools

**1. Generate tasks:**
```bash
python tools/generate_tools_consolidation_prs.py \
  --auto-generate \
  --repo owner/Agent_Cellphone_V2_Repository \
  --output validation_consolidation.csv
```

**2. Review CSV:**
- 10 rows with `task_type = open_pr`
- Each row targets a different tool group
- All have `run_github = true`

**3. Execute:**
```bash
python tools/spreadsheet_github_adapter.py \
  --file validation_consolidation.csv \
  --repo owner/Agent_Cellphone_V2_Repository \
  --output validation_results.json
```

**4. Result:**
- 10 PRs created automatically
- All PR URLs in `result_url` column
- Status updated to `done` for successful PRs

## Integration with Existing Tools

This workflow integrates with:
- **`unified_analyzer.py`** - Can identify consolidation candidates
- **`unified_validator.py`** - Can validate consolidation readiness
- **`unified_github.py`** - Uses existing PR creation infrastructure
- **`spreadsheet_github_adapter.py`** - Executes PR creation

## Benefits

✅ **Batch Processing** - Create multiple PRs from one spreadsheet  
✅ **Automated** - No manual PR creation needed  
✅ **Trackable** - All tasks in one CSV file  
✅ **Reusable** - Template for future consolidation work  
✅ **Integrated** - Uses swarm's existing GitHub tools  

## Future Enhancements

- [ ] Auto-detect consolidation candidates from codebase
- [ ] Generate PR descriptions from tool analysis
- [ ] Auto-update spreadsheet with PR status
- [ ] Integration with Google Sheets API
- [ ] Webhook triggers for real-time updates

---

**Author:** Agent-8 (SSOT & System Integration Specialist)  
**Date:** 2025-12-07


