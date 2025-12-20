# Spreadsheet → GitHub Adapter - Swarm Integration

## Overview

The `spreadsheet_github_adapter.py` tool enables spreadsheet-driven GitHub automation using the swarm's existing unified GitHub tools.

**Key Features:**
- ✅ Uses swarm's `unified_github.py` and `unified_github_pr_creator.py`
- ✅ Processes CSV or JSON spreadsheet files
- ✅ Supports: `create_issue`, `update_file`, `open_pr`
- ✅ Auto-generates branches, commits, and PRs
- ✅ Returns results in spreadsheet-compatible format

## Integration with Swarm Tools

This adapter leverages:
- **`unified_github.py`** - Consolidated GitHub operations
- **`unified_github_pr_creator.py`** - PR creation with GraphQL/REST fallback
- **`github_utils.py`** - GitHub token management (SSOT)

## Usage

### Single Task (CLI)

```bash
# Create a PR
python tools/spreadsheet_github_adapter.py \
  --task-type open_pr \
  --task-payload "Append timestamped line to demo.txt" \
  --repo owner/repo-name \
  --branch feature/auto-update

# Create an issue
python tools/spreadsheet_github_adapter.py \
  --task-type create_issue \
  --task-payload "Fix bug in authentication" \
  --repo owner/repo-name \
  --title "Authentication Bug Fix"
```

### Batch Processing (Spreadsheet File)

**CSV Format:**
```csv
task_type,task_payload,run_github,status,result_url,error_msg,updated_at
open_pr,Append timestamped line to demo.txt,true,pending,,,
open_pr,Update README with new features,true,pending,,,
```

**JSON Format:**
```json
[
  {
    "task_type": "open_pr",
    "task_payload": "Append timestamped line to demo.txt",
    "run_github": "true",
    "status": "pending",
    "repo": "owner/repo-name"
  }
]
```

**Process file:**
```bash
python tools/spreadsheet_github_adapter.py \
  --file tasks.csv \
  --repo owner/repo-name \
  --output results.json
```

## Spreadsheet Columns

| Column | Required | Description |
|--------|----------|-------------|
| `task_type` | Yes | `create_issue` \| `update_file` \| `open_pr` |
| `task_payload` | Yes | Natural language instruction |
| `run_github` | Yes | `true` \| `run` to trigger execution |
| `status` | Auto | `pending` → `running` → `done`/`error` |
| `result_url` | Auto | PR/issue URL (populated by tool) |
| `error_msg` | Auto | Error message if status = error |
| `repo` | Optional | Override default repo |
| `branch` | Optional | Branch name (auto-generated if not provided) |
| `file_path` | Optional | File path for `update_file` tasks |
| `title` | Optional | Override auto-generated title |
| `body` | Optional | Override auto-generated body |

## Task Types

### `open_pr`
Creates a PR with changes:
- Auto-generates branch name if not provided
- Uses `unified_github_pr_creator.py` for PR creation
- Returns PR URL in `result_url`

### `create_issue`
Creates a GitHub issue:
- Uses `task_payload` as issue body
- Returns issue URL in `result_url`
- **Note:** Currently placeholder - needs GitHub API implementation

### `update_file`
Updates a file and creates PR:
- Creates branch, updates file, commits, opens PR
- **Note:** Currently delegates to `open_pr` - needs file update implementation

## Output Format

Results are returned in JSON format:

```json
{
  "status": "done",
  "result_url": "https://github.com/owner/repo/pull/123",
  "error_msg": "",
  "updated_at": "2025-12-07T21:00:00.000000",
  "meta": {
    "pr_number": 123,
    "branch": "auto-20251207-210000",
    "title": "Append timestamped line to demo.txt"
  }
}
```

## Integration with Spreadsheet Platforms

### Google Sheets
1. Export sheet as CSV
2. Process with adapter
3. Import results back to sheet

### Excel
1. Save as CSV
2. Process with adapter
3. Import results JSON

### Future: Direct API Integration
- Google Sheets API integration
- Excel Online API integration
- Real-time webhook triggers

## Examples

### Example 1: Batch PR Creation

**Input CSV:**
```csv
task_type,task_payload,run_github,repo
open_pr,Add new feature X,true,owner/repo
open_pr,Fix bug Y,true,owner/repo
```

**Command:**
```bash
python tools/spreadsheet_github_adapter.py --file tasks.csv --repo owner/repo
```

**Output:** Creates 2 PRs, returns URLs for both

### Example 2: Single PR with Custom Branch

```bash
python tools/spreadsheet_github_adapter.py \
  --task-type open_pr \
  --task-payload "Update documentation" \
  --repo owner/repo \
  --branch docs/update-2025-12-07 \
  --title "Documentation Update" \
  --body "Updated README and API docs"
```

## Future Enhancements

- [ ] Direct Google Sheets API integration
- [ ] Real-time webhook triggers
- [ ] File update implementation (git operations)
- [ ] Issue creation via GitHub API
- [ ] Batch processing with rate limit handling
- [ ] Status polling and auto-retry
- [ ] Integration with swarm's task system

## Dependencies

- `unified_github.py` - GitHub operations
- `unified_github_pr_creator.py` - PR creation
- `github_utils.py` - Token management
- Python standard library (json, csv, logging)

---

**Author:** Agent-8 (SSOT & System Integration Specialist)  
**Date:** 2025-12-07  
**V2 Compliant:** Yes


