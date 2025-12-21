# MCP Servers for Agent Swarm

This directory contains Model Context Protocol (MCP) servers that expose Agent Swarm capabilities.

## 🗂️ Server Organization

The MCP servers are organized into three main categories:

### 1. Core Operations
Essential servers for agent coordination and task management.
- **Mission Control Server**: Central command for task assignment and integrity (Captain)
- **Swarm Messaging**: Inter-agent communication
- **Task Manager**: Master task log operations
- **Swarm Brain**: Knowledge base and memory

### 2. Development & Quality
Tools for maintaining code quality and standards.
- **Refactoring Server**: Automated code cleanup and pyramid analysis
- **Git Operations**: Work verification and commit checking
- **V2 Compliance**: Code standard enforcement
- **Testing Server**: Test execution and coverage analysis
- **Memory Safety**: Resource leak detection and verification

### 3. Infrastructure & Monitoring
Tools for system health and external services.
- **Website Manager**: WordPress and content management
- **Observability Server**: System metrics and health monitoring

---

## 🚀 Server Details

### 1. Mission Control Server (Captain)
Exposes Captain's coordination, mission assignment, and integrity tools.
- **Tools**: 
  - `assign_mission`: Create structured mission files
  - `check_integrity`: Verify work claims with git history
  - `update_leaderboard`: Manage agent points and achievements
  - `calculate_points`: Standardized point calculation
  - `check_agent_status`: Monitor agent activity

### 2. Refactoring Server
Exposes automated code analysis and refactoring tools.
- **Tools**:
  - `auto_extract_code`: Plan function extraction for large files
  - `fix_linting_issues`: Auto-fix linting errors
  - `analyze_test_pyramid`: check unit/integration/e2e balance
  - `check_file_size`: Validate file length compliance

### 3. Swarm Messaging Server
Exposes the swarm messaging system via MCP.
- **Tools**: `send_agent_message`, `broadcast_message`, `get_agent_coordinates`

### 4. Task Manager Server
Exposes the MASTER_TASK_LOG.md system via MCP.
- **Tools**: `add_task_to_inbox`, `mark_task_complete`, `move_task_to_waiting`, `get_tasks`

### 5. Website Manager Server
Exposes WordPress and website management capabilities.
- **Tools**: `create_wordpress_page`, `deploy_file_to_wordpress`, `create_blog_post`, `generate_image_prompts`

### 6. Swarm Brain Server
Exposes Swarm Brain knowledge base operations.
- **Tools**: `share_learning`, `record_decision`, `search_swarm_knowledge`, `take_note`

### 7. Git Operations Server
Exposes git verification and commit checking capabilities.
- **Tools**: `verify_git_work`, `get_recent_commits`, `check_file_history`, `validate_commit`

### 8. V2 Compliance Checker Server
Exposes V2 compliance validation capabilities.
- **Tools**: `check_v2_compliance`, `validate_file_size`, `check_function_size`, `get_v2_exceptions`

### 9. Testing Server
Exposes testing and coverage capabilities.
- **Tools**: `run_coverage_analysis`, `run_mutation_tests`

### 10. Observability Server
Exposes metrics and system health monitoring.
- **Tools**: `get_metrics_snapshot`, `check_system_health`, `check_slo_compliance`

### 11. Memory Safety Server
Exposes memory leak detection and resource verification.
- **Tools**: `detect_memory_leaks`, `verify_files_exist`, `check_file_handles`

---

## ⚙️ Configuration

To use these servers, add them to your MCP settings (e.g., `claude_desktop_config.json`).
A complete configuration example is available in `all_mcp_servers.json`.

```json
{
  "mcpServers": {
    "server-name": {
      "command": "python",
      "args": ["/path/to/mcp_servers/server_script.py"]
    }
  }
}
```
