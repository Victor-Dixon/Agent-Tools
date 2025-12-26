# MCP Servers for Agent Swarm

This directory contains Model Context Protocol (MCP) servers that expose Agent Swarm capabilities.

## 🗂️ Server Organization

The MCP servers are organized into four main categories:

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
- **Code Quality Server**: Linting, formatting, and type checking

### 3. Infrastructure & Monitoring
Tools for system health and external services.
- **Website Manager**: WordPress and content management
- **Observability Server**: System metrics and health monitoring
- **Performance Profiler**: Identify performance bottlenecks

### 4. DevOps Automation (NEW)
High-value automation servers for development workflows.
- **Dependency Management**: Package maintenance and updates
- **Release Management**: Versioning, changelogs, and releases
- **CI/CD Helper**: Monitor and manage pipelines
- **Environment Setup**: Bootstrap development environments
- **Security Scanner**: Proactive security checks
- **Issue/TODO Tracker**: Code-to-issue automation
- **Documentation Generator**: Keep docs in sync
- **Database Operations**: Database lifecycle management

---

## 🚀 Server Details

### Core Operations

#### 1. Mission Control Server (Captain)
Exposes Captain's coordination, mission assignment, and integrity tools.
- **Tools**: 
  - `assign_mission`: Create structured mission files
  - `check_integrity`: Verify work claims with git history
  - `update_leaderboard`: Manage agent points and achievements
  - `calculate_points`: Standardized point calculation
  - `check_agent_status`: Monitor agent activity

#### 2. Swarm Messaging Server
Exposes the swarm messaging system via MCP.
- **Tools**: `send_agent_message`, `broadcast_message`, `get_agent_coordinates`

#### 3. Task Manager Server
Exposes the MASTER_TASK_LOG.md system via MCP.
- **Tools**: `add_task_to_inbox`, `mark_task_complete`, `move_task_to_waiting`, `get_tasks`

#### 4. Swarm Brain Server
Exposes Swarm Brain knowledge base operations.
- **Tools**: `share_learning`, `record_decision`, `search_swarm_knowledge`, `take_note`

---

### Development & Quality

#### 5. Refactoring Server
Exposes automated code analysis and refactoring tools.
- **Tools**:
  - `auto_extract_code`: Plan function extraction for large files
  - `fix_linting_issues`: Auto-fix linting errors
  - `analyze_test_pyramid`: check unit/integration/e2e balance
  - `check_file_size`: Validate file length compliance

#### 6. Git Operations Server
Exposes git verification and commit checking capabilities.
- **Tools**: `verify_git_work`, `get_recent_commits`, `check_file_history`, `validate_commit`

#### 7. V2 Compliance Checker Server
Exposes V2 compliance validation capabilities.
- **Tools**: `check_v2_compliance`, `validate_file_size`, `check_function_size`, `get_v2_exceptions`

#### 8. Testing Server
Exposes testing and coverage capabilities.
- **Tools**: `run_coverage_analysis`, `run_mutation_tests`

#### 9. Memory Safety Server
Exposes memory leak detection and resource verification.
- **Tools**: `detect_memory_leaks`, `verify_files_exist`, `check_file_handles`

#### 10. Code Quality Server
Automated code improvements and quality checks.
- **Tools**:
  - `run_linter`: Run ESLint/Ruff/etc. and return issues
  - `auto_fix_lint`: Auto-fix linter issues where possible
  - `format_code`: Run Prettier/Black formatters
  - `check_types`: TypeScript/mypy type checking
  - `find_dead_code`: Find unused exports/functions

---

### Infrastructure & Monitoring

#### 11. Website Manager Server
Exposes WordPress and website management capabilities.
- **Tools**: `create_wordpress_page`, `deploy_file_to_wordpress`, `create_blog_post`, `generate_image_prompts`

#### 12. Observability Server
Exposes metrics and system health monitoring.
- **Tools**: `get_metrics_snapshot`, `check_system_health`, `check_slo_compliance`

#### 13. Performance Profiler Server
Identify and analyze performance bottlenecks.
- **Tools**:
  - `profile_startup`: Measure application startup time
  - `find_slow_tests`: Identify slow test cases
  - `analyze_bundle`: Bundle size analysis for JS/TS projects
  - `memory_snapshot`: Memory usage report
  - `benchmark_function`: Run micro-benchmarks

---

### DevOps Automation

#### 14. Dependency Management Server
Automate package maintenance across multiple ecosystems.
- **Tools**:
  - `check_outdated`: Find outdated npm/pip/cargo packages
  - `check_vulnerabilities`: Security audit (npm audit, pip-audit)
  - `update_package`: Safely update a package with lockfile
  - `add_package`: Add package with latest version
  - `remove_unused`: Find and remove unused dependencies

#### 15. Release Management Server
Automate versioning and releases.
- **Tools**:
  - `bump_version`: Semantic versioning (major/minor/patch)
  - `generate_changelog`: Auto-generate from commits
  - `create_release`: GitHub release with notes
  - `tag_version`: Create and push git tags
  - `validate_release`: Pre-release checks

#### 16. CI/CD Helper Server
Monitor and manage CI/CD pipelines.
- **Tools**:
  - `check_ci_status`: Get status of current branch CI
  - `get_failed_logs`: Fetch logs from failed CI jobs
  - `retry_failed_job`: Retry a specific failed job
  - `list_workflows`: List recent workflow runs
  - `cancel_workflow`: Cancel running workflow

#### 17. Environment Setup Server
Bootstrap development environments.
- **Tools**:
  - `install_dependencies`: npm install / pip install
  - `setup_env_file`: Create .env from template
  - `validate_environment`: Check all required tools installed
  - `setup_database`: Run migrations, seed data
  - `health_check`: Verify all services running

#### 18. Security Scanner Server
Proactive security checks.
- **Tools**:
  - `scan_secrets`: Find hardcoded secrets/API keys
  - `check_dependencies`: CVE vulnerability scan
  - `audit_permissions`: File permission issues
  - `check_env_exposure`: Ensure .env not committed
  - `generate_security_report`: Full security audit

#### 19. Issue/TODO Tracker Server
Code-to-issue automation.
- **Tools**:
  - `extract_todos`: Find all TODOs/FIXMEs in code
  - `create_issue_from_todo`: Create GitHub issue from TODO
  - `link_todo_to_issue`: Update TODO with issue number
  - `list_stale_issues`: Find old unresolved issues
  - `close_completed`: Auto-close issues for merged PRs

#### 20. Documentation Generator Server
Keep docs in sync with code.
- **Tools**:
  - `generate_api_docs`: OpenAPI/Swagger from code
  - `update_readme`: Sync README with code changes
  - `generate_type_docs`: TypeDoc/Sphinx generation
  - `check_doc_coverage`: Find undocumented functions
  - `validate_links`: Check for broken doc links

#### 21. Database Operations Server
Database lifecycle management.
- **Tools**:
  - `run_migration`: Execute pending migrations
  - `rollback_migration`: Revert last migration
  - `seed_database`: Load seed/test data
  - `backup_database`: Create backup
  - `reset_database`: Drop and recreate

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

### Quick Start for New Servers

```json
{
  "mcpServers": {
    "dependency-management": {
      "command": "python",
      "args": ["mcp_servers/dependency_management_server.py"]
    },
    "security-scanner": {
      "command": "python",
      "args": ["mcp_servers/security_scanner_server.py"]
    },
    "cicd-helper": {
      "command": "python",
      "args": ["mcp_servers/cicd_helper_server.py"]
    }
  }
}
```

---

## 🔧 Supported Ecosystems

The new DevOps automation servers support multiple language ecosystems:

| Feature | npm/yarn/pnpm | pip/poetry | cargo | go |
|---------|---------------|------------|-------|----|
| Dependency Check | ✅ | ✅ | ✅ | ✅ |
| Vulnerability Scan | ✅ | ✅ | ✅ | - |
| Linting | ESLint, Biome | Ruff, Flake8 | Clippy | golangci-lint |
| Formatting | Prettier | Black, Ruff | rustfmt | gofmt |
| Type Checking | TypeScript | mypy, pyright | - | - |
| Migrations | Prisma, Drizzle, Knex | Alembic, Django | - | golang-migrate |
| Testing | Jest, Vitest | pytest | cargo test | go test |
| Benchmarking | vitest bench | pytest-benchmark | cargo bench | go test -bench |
