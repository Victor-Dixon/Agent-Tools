# MCP Servers for Agent Swarm

This directory contains Model Context Protocol (MCP) servers that expose Agent Swarm capabilities.

## Swarm Messaging Server

Exposes the swarm messaging system via MCP, allowing agents and external tools to send messages to agents via PyAutoGUI coordinates.

### Configuration

Add to your MCP settings (e.g., Claude Desktop config):

```json
{
  "mcpServers": {
    "swarm-messaging": {
      "command": "python",
      "args": ["D:/Agent_Cellphone_V2_Repository/mcp_servers/messaging_server.py"]
    }
  }
}
```

### Available Tools

1. **send_agent_message**: Send message to specific agent
   - `agent_id`: Target agent (Agent-1 through Agent-8)
   - `message`: Message content
   - `priority`: "regular" or "urgent"

2. **broadcast_message**: Send message to all agents
   - `message`: Message content
   - `priority`: "regular" or "urgent"

3. **get_agent_coordinates**: Get coordinates and status for all agents
   - Returns: Agent positions, active status, descriptions

### Usage Examples

```python
# Send message to Agent-1
send_agent_message(
    agent_id="Agent-1",
    message="Execute vector consolidation now",
    priority="urgent"
)

# Broadcast to all agents
broadcast_message(
    message="V2 compliance check required",
    priority="regular"
)

# Get agent coordinates
get_agent_coordinates()
```

## Task Manager Server

Exposes the MASTER_TASK_LOG.md system via MCP, allowing agents to update task status, add tasks, and track work.

### Configuration

```json
{
  "mcpServers": {
    "task-manager": {
      "command": "python",
      "args": ["D:/Agent_Cellphone_V2_Repository/mcp_servers/task_manager_server.py"]
    }
  }
}
```

### Available Tools

1. **add_task_to_inbox** - Add task to INBOX
2. **mark_task_complete** - Mark task as done
3. **move_task_to_waiting** - Move task to WAITING ON
4. **get_tasks** - Read tasks from log

See `TASK_MANAGER_README.md` for full documentation.

## Website Manager Server

Exposes WordPress and website management capabilities via MCP, allowing agents to create pages, deploy files, manage menus, create blog posts, and generate image prompts.

### Configuration

```json
{
  "mcpServers": {
    "website-manager": {
      "command": "python",
      "args": ["D:/Agent_Cellphone_V2_Repository/mcp_servers/website_manager_server.py"]
    }
  }
}
```

### Available Tools

1. **WordPress Management:**
   - `create_wordpress_page` - Create new pages
   - `deploy_file_to_wordpress` - Deploy files
   - `add_page_to_menu` - Add pages to menus
   - `list_wordpress_pages` - List all pages
   - `purge_wordpress_cache` - Clear cache

2. **Blog Automation:**
   - `create_blog_post` - Create blog posts
   - `create_report_page` - Create report pages

3. **Image Generation:**
   - `generate_image_prompts` - Generate design prompts

See `WEBSITE_MANAGER_README.md` for full documentation.

## Swarm Brain Server

Exposes Swarm Brain knowledge base operations via MCP, allowing agents to search knowledge, share learnings, record decisions, and manage personal notes.

### Configuration

```json
{
  "mcpServers": {
    "swarm-brain": {
      "command": "python",
      "args": ["D:/Agent_Cellphone_V2_Repository/mcp_servers/swarm_brain_server.py"]
    }
  }
}
```

### Available Tools

1. **Knowledge Sharing:**
   - `share_learning` - Share learning to knowledge base
   - `record_decision` - Record important decision
   - `search_swarm_knowledge` - Search knowledge base

2. **Personal Notes:**
   - `take_note` - Take personal note
   - `get_agent_notes` - Get agent's notes

See `SWARM_BRAIN_README.md` for full documentation.

## Integration with Global MCP

All MCP servers are designed to work with any MCP-compatible client:
- Claude Desktop
- Cursor IDE
- Custom MCP clients
- Other AI tools with MCP support

This enables seamless swarm coordination, website management, and knowledge sharing from any MCP-enabled environment.

## Git Operations Server

Exposes git verification and commit checking capabilities via MCP, allowing agents to verify work, check commits, and validate changes.

### Configuration

```json
{
  "mcpServers": {
    "git-operations": {
      "command": "python",
      "args": ["D:/Agent_Cellphone_V2_Repository/mcp_servers/git_operations_server.py"]
    }
  }
}
```

### Available Tools

1. **Work Verification:**
   - `verify_git_work` - Verify claimed work against git commits
   - `verify_work_exists` - Verify work exists in today's commits

2. **Commit Checking:**
   - `get_recent_commits` - Get recent commits
   - `check_file_history` - Check file git history
   - `validate_commit` - Validate commit details

See `GIT_OPERATIONS_README.md` for full documentation.

## V2 Compliance Checker Server

Exposes V2 compliance validation capabilities via MCP, allowing agents to check files, functions, and get exception lists before committing.

### Configuration

```json
{
  "mcpServers": {
    "v2-compliance": {
      "command": "python",
      "args": ["D:/Agent_Cellphone_V2_Repository/mcp_servers/v2_compliance_server.py"]
    }
  }
}
```

### Available Tools

1. **Compliance Checking:**
   - `check_v2_compliance` - Comprehensive V2 compliance check
   - `validate_file_size` - Check file size against limit
   - `check_function_size` - Check function size against limit
   - `get_v2_exceptions` - Get approved exceptions list

See `V2_COMPLIANCE_README.md` for full documentation.

## MCP Tools Analysis

See `MCP_TOOLS_ANALYSIS.md` for analysis of which tools should be MCP-accessible vs unnecessary.



