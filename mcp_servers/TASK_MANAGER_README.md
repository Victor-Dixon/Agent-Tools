# Task Manager MCP Server

MCP server for managing the MASTER_TASK_LOG.md system. Enables agents to update task status, add tasks, and track work.

## Configuration

Add to your MCP settings (e.g., Claude Desktop config):

```json
{
  "mcpServers": {
    "task-manager": {
      "command": "python",
      "args": [
        "D:/Agent_Cellphone_V2_Repository/mcp_servers/task_manager_server.py"
      ]
    }
  }
}
```

## Available Tools

### 1. `add_task_to_inbox`
Add a task to the INBOX section of MASTER_TASK_LOG.md

**Parameters:**
- `task` (required): Task description to add
- `agent_id` (optional): Agent ID reporting this task

**Example:**
```json
{
  "name": "add_task_to_inbox",
  "arguments": {
    "task": "Review FreeRideInvestor funnel performance",
    "agent_id": "Agent-1"
  }
}
```

### 2. `mark_task_complete`
Mark a task as complete by changing `[ ]` to `[x]`

**Parameters:**
- `task_description` (required): Task description to mark complete
- `section` (optional): Section where task is located ("THIS WEEK" or "INBOX", default: "THIS WEEK")

**Example:**
```json
{
  "name": "mark_task_complete",
  "arguments": {
    "task_description": "Prototype Kiki's site theme",
    "section": "THIS WEEK"
  }
}
```

### 3. `move_task_to_waiting`
Move a task to WAITING ON section

**Parameters:**
- `task_description` (required): Task description to move
- `reason` (required): Reason why task is waiting (e.g., "blocked on X", "waiting for Y")
- `agent_id` (optional): Agent ID reporting this

**Example:**
```json
{
  "name": "move_task_to_waiting",
  "arguments": {
    "task_description": "Follow up with Merlin Worm",
    "reason": "waiting for Merlin reply on Firebase collab",
    "agent_id": "Agent-1"
  }
}
```

### 4. `get_tasks`
Get tasks from MASTER_TASK_LOG.md

**Parameters:**
- `section` (optional): Specific section to get tasks from ("INBOX", "THIS WEEK", "WAITING ON", "PARKED"). If not provided, returns all sections.

**Example:**
```json
{
  "name": "get_tasks",
  "arguments": {
    "section": "THIS WEEK"
  }
}
```

## Integration with Agent Operating Cycle

### CYCLE START
- Check MASTER_TASK_LOG for assigned tasks using `get_tasks`
- Review THIS WEEK section for priorities

### DURING CYCLE
- If new task identified → `add_task_to_inbox(task, agent_id)`
- If task blocked → `move_task_to_waiting(task_description, reason, agent_id)`

### CYCLE END (MANDATORY)
- If task completed → `mark_task_complete(task_description, section="THIS WEEK")`
- If task blocked → `move_task_to_waiting(task_description, reason, agent_id)`
- If new task identified → `add_task_to_inbox(task, agent_id)`

## Usage in Agent Messages

Agents should update MASTER_TASK_LOG at cycle end:

```
✅ UPDATE MASTER_TASK_LOG (MANDATORY):
- Use MCP tool: task_manager_server
- If task completed → mark_task_complete(task_description, section="THIS WEEK")
- If task blocked → move_task_to_waiting(task_description, reason="blocked on X", agent_id="{agent_id}")
- If new task identified → add_task_to_inbox(task="description", agent_id="{agent_id}")
- Location: MASTER_TASK_LOG.md (repository root)
- Reference: QUICK_START_GUIDE.md
```

## Benefits

1. **Central Task Tracking**: All tasks in one place, no task loss
2. **Delegation Surface**: Clear ownership via DELEGATION_BOARD.md
3. **Agent Accountability**: Agents report task status automatically
4. **CEO Visibility**: Victor can see all tasks and their status
5. **Swarm Coordination**: Tasks can be assigned to specific agents

## Related Documents

- `MASTER_TASK_LOG.md` - The task log file
- `DELEGATION_BOARD.md` - Task ownership assignments
- `SWARM_TASK_PACKETS.md` - Swarm execution directives
- `QUICK_START_GUIDE.md` - How to use the system
- `OWNERSHIP_DECISION_MATRIX.md` - Decision guide for task ownership

