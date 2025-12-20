# Git Operations MCP Server

MCP server for git verification and commit checking. Enables agents to verify work, check commits, and validate changes.

## Configuration

Add to your MCP settings (e.g., Claude Desktop config):

```json
{
  "mcpServers": {
    "git-operations": {
      "command": "python",
      "args": [
        "D:/Agent_Cellphone_V2_Repository/mcp_servers/git_operations_server.py"
      ]
    }
  }
}
```

## Available Tools

### 1. `verify_git_work`
Verify claimed work against git commits

**Parameters:**
- `agent_id` (required): Agent ID (e.g., 'Agent-1')
- `file_path` (required): File path that was modified
- `claimed_changes` (required): Description of claimed changes
- `time_window_hours` (optional): Time window to check (default: 24)

**Example:**
```json
{
  "name": "verify_git_work",
  "arguments": {
    "agent_id": "Agent-1",
    "file_path": "src/core/messaging_template_texts.py",
    "claimed_changes": "Updated A2A template with task management",
    "time_window_hours": 24
  }
}
```

### 2. `get_recent_commits`
Get recent git commits

**Parameters:**
- `agent_id` (optional): Filter by agent ID
- `hours` (optional): Hours to look back (default: 24)
- `file_pattern` (optional): File pattern to filter

**Example:**
```json
{
  "name": "get_recent_commits",
  "arguments": {
    "agent_id": "Agent-1",
    "hours": 48,
    "file_pattern": "src/core/*.py"
  }
}
```

### 3. `check_file_history`
Check git history for a specific file

**Parameters:**
- `file_path` (required): File path to check
- `days` (optional): Days to look back (default: 7)

**Example:**
```json
{
  "name": "check_file_history",
  "arguments": {
    "file_path": "MASTER_TASK_LOG.md",
    "days": 7
  }
}
```

### 4. `validate_commit`
Validate a commit exists and get details

**Parameters:**
- `commit_hash` (required): Commit hash (full or short)

**Example:**
```json
{
  "name": "validate_commit",
  "arguments": {
    "commit_hash": "abc123def"
  }
}
```

### 5. `verify_work_exists`
Verify that work exists in today's git commits

**Parameters:**
- `file_patterns` (required): Array of file patterns to check
- `agent_name` (optional): Agent name to filter

**Example:**
```json
{
  "name": "verify_work_exists",
  "arguments": {
    "file_patterns": ["src/core/*.py", "mcp_servers/*.py"],
    "agent_name": "Agent-1"
  }
}
```

## Integration with Agent Operating Cycle

### CYCLE END
- Verify work before claiming: `verify_git_work(agent_id, file_path, claimed_changes)`
- Check recent commits: `get_recent_commits(agent_id, hours=24)`
- Validate before committing: `verify_work_exists(file_patterns, agent_name)`

## Benefits

1. **Work Verification** - Verify claimed work against git evidence
2. **Integrity** - Prevent false credit claims
3. **Commit Tracking** - Track what was actually committed
4. **History Analysis** - Check file change history
5. **Validation** - Validate commits before pushing

## Related Documents

- `tools/git_work_verifier.py` - Git work verifier source
- `tools/git_commit_verifier.py` - Commit verifier source

