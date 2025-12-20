# Swarm Brain MCP Server

MCP server for accessing and contributing to the Swarm Brain knowledge base. Enables agents to search knowledge, share learnings, record decisions, and manage personal notes.

## Configuration

Add to your MCP settings (e.g., Claude Desktop config):

```json
{
  "mcpServers": {
    "swarm-brain": {
      "command": "python",
      "args": [
        "D:/Agent_Cellphone_V2_Repository/mcp_servers/swarm_brain_server.py"
      ]
    }
  }
}
```

## Available Tools

### 1. `share_learning`
Share a learning to Swarm Brain knowledge base (visible to all agents)

**Parameters:**
- `agent_id` (required): Agent ID (e.g., 'Agent-1')
- `title` (required): Learning title
- `content` (required): Learning content (markdown supported)
- `tags` (optional): Array of tags for categorization

**Example:**
```json
{
  "name": "share_learning",
  "arguments": {
    "agent_id": "Agent-1",
    "title": "V2 Compliance Pattern",
    "content": "When refactoring large files, split into modules by domain...",
    "tags": ["v2-compliance", "refactoring", "pattern"]
  }
}
```

### 2. `record_decision`
Record an important decision to Swarm Brain

**Parameters:**
- `agent_id` (required): Agent ID
- `title` (required): Decision title
- `decision` (required): What was decided
- `rationale` (required): Why this decision was made
- `participants` (optional): Array of participating agent IDs

**Example:**
```json
{
  "name": "record_decision",
  "arguments": {
    "agent_id": "Agent-1",
    "title": "Use MCP for task management",
    "decision": "All task operations via MCP task_manager_server",
    "rationale": "Enables agent automation and central tracking"
  }
}
```

### 3. `search_swarm_knowledge`
Search Swarm Brain knowledge base

**Parameters:**
- `agent_id` (required): Agent ID
- `query` (required): Search query
- `limit` (optional): Maximum results (default: 10)

**Example:**
```json
{
  "name": "search_swarm_knowledge",
  "arguments": {
    "agent_id": "Agent-1",
    "query": "v2 compliance refactoring",
    "limit": 5
  }
}
```

### 4. `take_note`
Take a personal note (agent-specific, not shared)

**Parameters:**
- `agent_id` (required): Agent ID
- `content` (required): Note content
- `note_type` (optional): Type - "important", "learning", "todo", or "general" (default: "important")

**Example:**
```json
{
  "name": "take_note",
  "arguments": {
    "agent_id": "Agent-1",
    "content": "Remember to check DELEGATION_BOARD before starting work",
    "note_type": "important"
  }
}
```

### 5. `get_agent_notes`
Get agent's personal notes

**Parameters:**
- `agent_id` (required): Agent ID
- `note_type` (optional): Filter by type - "important", "learning", "todo", or "general"

**Example:**
```json
{
  "name": "get_agent_notes",
  "arguments": {
    "agent_id": "Agent-1",
    "note_type": "important"
  }
}
```

## Integration with Agent Operating Cycle

### CYCLE START
- Search Swarm Brain for relevant patterns: `search_swarm_knowledge(agent_id, query)`
- Check personal notes: `get_agent_notes(agent_id)`

### DURING CYCLE
- Take notes: `take_note(agent_id, content, note_type)`
- Search for solutions: `search_swarm_knowledge(agent_id, query)`

### CYCLE END (MANDATORY)
- Share learnings: `share_learning(agent_id, title, content, tags)`
- Record decisions: `record_decision(agent_id, title, decision, rationale)`
- Update MASTER_TASK_LOG with completion

## Common Workflows

### Finding Solutions

1. **Search for patterns:**
   ```json
   {
     "name": "search_swarm_knowledge",
     "arguments": {
       "agent_id": "Agent-1",
       "query": "wordpress page creation"
     }
   }
   ```

2. **Review results and apply pattern**

3. **Share new learning if pattern improved:**
   ```json
   {
     "name": "share_learning",
     "arguments": {
       "agent_id": "Agent-1",
       "title": "Improved WordPress Page Creation",
       "content": "Found faster method using MCP tools...",
       "tags": ["wordpress", "optimization"]
     }
   }
   ```

### Recording Decisions

When making architectural or strategic decisions:

```json
{
  "name": "record_decision",
  "arguments": {
    "agent_id": "Agent-1",
    "title": "MCP for all agent tools",
    "decision": "All agent-accessible tools moved to MCP servers",
    "rationale": "Enables automation, reduces CLI overhead, improves agent capabilities"
  }
}
```

## Benefits

1. **Collective Knowledge** - All agents benefit from shared learnings
2. **Pattern Reuse** - Find proven solutions quickly
3. **Decision Tracking** - Record why decisions were made
4. **Personal Notes** - Agent-specific reminders and learnings
5. **Knowledge Persistence** - Knowledge survives agent sessions

## Related Documents

- `src/swarm_brain/swarm_memory.py` - Swarm Memory source
- `src/swarm_brain/knowledge_base.py` - Knowledge Base source
- `tools/swarm_brain_cli.py` - CLI tool (alternative to MCP)
- `swarm_brain/` - Knowledge base directory

