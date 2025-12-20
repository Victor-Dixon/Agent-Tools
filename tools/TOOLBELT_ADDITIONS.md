# Toolbelt Registry Additions

## Priority Signal Tools to Add

### Agent Orientation

**ID**: `agent-orient`

**Module**: `tools.agent_orient`

**Flags**: --agent-orient, --orient

**Description**: Agent orientation and onboarding

```python
"agent-orient": {
    "name": "Agent Orientation",
    "module": "tools.agent_orient",
    "main_function": "main",
    "description": "Agent orientation and onboarding",
    "flags": ['--agent-orient', '--orient'],
    "args_passthrough": True,
},
```

### Agent Task Finder

**ID**: `agent-task-finder`

**Module**: `tools.agent_task_finder`

**Flags**: --agent-task-finder, --find-tasks

**Description**: Find tasks assigned to agents

```python
"agent-task-finder": {
    "name": "Agent Task Finder",
    "module": "tools.agent_task_finder",
    "main_function": "main",
    "description": "Find tasks assigned to agents",
    "flags": ['--agent-task-finder', '--find-tasks'],
    "args_passthrough": True,
},
```

### Captain Status Check

**ID**: `captain-status-check`

**Module**: `tools.captain_check_agent_status`

**Flags**: --captain-status, --cap-status

**Description**: Captain check agent status

```python
"captain-status-check": {
    "name": "Captain Status Check",
    "module": "tools.captain_check_agent_status",
    "main_function": "main",
    "description": "Captain check agent status",
    "flags": ['--captain-status', '--cap-status'],
    "args_passthrough": True,
},
```

### Find Idle Agents

**ID**: `captain-find-idle`

**Module**: `tools.captain_find_idle_agents`

**Flags**: --find-idle, --idle-agents

**Description**: Find agents that are idle

```python
"captain-find-idle": {
    "name": "Find Idle Agents",
    "module": "tools.captain_find_idle_agents",
    "main_function": "main",
    "description": "Find agents that are idle",
    "flags": ['--find-idle', '--idle-agents'],
    "args_passthrough": True,
},
```

### Captain Next Task Picker

**ID**: `captain-next-task`

**Module**: `tools.captain_next_task_picker`

**Flags**: --next-task, --pick-task

**Description**: Pick next task for agents

```python
"captain-next-task": {
    "name": "Captain Next Task Picker",
    "module": "tools.captain_next_task_picker",
    "main_function": "main",
    "description": "Pick next task for agents",
    "flags": ['--next-task', '--pick-task'],
    "args_passthrough": True,
},
```

### Captain ROI Calculator

**ID**: `captain-roi-calc`

**Module**: `tools.captain_roi_quick_calc`

**Flags**: --roi-calc, --roi

**Description**: Quick ROI calculation for tasks

```python
"captain-roi-calc": {
    "name": "Captain ROI Calculator",
    "module": "tools.captain_roi_quick_calc",
    "main_function": "main",
    "description": "Quick ROI calculation for tasks",
    "flags": ['--roi-calc', '--roi'],
    "args_passthrough": True,
},
```

### Repo Overlap Analyzer

**ID**: `repo-overlap`

**Module**: `tools.repo_overlap_analyzer`

**Flags**: --repo-overlap, --overlap

**Description**: Analyze repository overlaps for consolidation

```python
"repo-overlap": {
    "name": "Repo Overlap Analyzer",
    "module": "tools.repo_overlap_analyzer",
    "main_function": "main",
    "description": "Analyze repository overlaps for consolidation",
    "flags": ['--repo-overlap', '--overlap'],
    "args_passthrough": True,
},
```

### Consolidation Executor

**ID**: `consolidation-executor`

**Module**: `tools.consolidation_executor`

**Flags**: --consolidation-exec, --consolidate

**Description**: Execute repository consolidations

```python
"consolidation-executor": {
    "name": "Consolidation Executor",
    "module": "tools.consolidation_executor",
    "main_function": "main",
    "description": "Execute repository consolidations",
    "flags": ['--consolidation-exec', '--consolidate'],
    "args_passthrough": True,
},
```

### Verify Phase 1 Repos

**ID**: `verify-phase1`

**Module**: `tools.verify_phase1_repos`

**Flags**: --verify-phase1, --phase1-verify

**Description**: Verify Phase 1 consolidation repos

```python
"verify-phase1": {
    "name": "Verify Phase 1 Repos",
    "module": "tools.verify_phase1_repos",
    "main_function": "main",
    "description": "Verify Phase 1 consolidation repos",
    "flags": ['--verify-phase1', '--phase1-verify'],
    "args_passthrough": True,
},
```

### Start Discord System

**ID**: `discord-start`

**Module**: `tools.start_discord_system`

**Flags**: --discord-start, --start-discord

**Description**: Start Discord bot system

```python
"discord-start": {
    "name": "Start Discord System",
    "module": "tools.start_discord_system",
    "main_function": "main",
    "description": "Start Discord bot system",
    "flags": ['--discord-start', '--start-discord'],
    "args_passthrough": True,
},
```

### Discord Status Dashboard

**ID**: `discord-status`

**Module**: `tools.discord_status_dashboard`

**Flags**: --discord-status, --discord-dash

**Description**: Discord status dashboard

```python
"discord-status": {
    "name": "Discord Status Dashboard",
    "module": "tools.discord_status_dashboard",
    "main_function": "main",
    "description": "Discord status dashboard",
    "flags": ['--discord-status', '--discord-dash'],
    "args_passthrough": True,
},
```

### Verify Discord Running

**ID**: `discord-verify`

**Module**: `tools.verify_discord_running`

**Flags**: --discord-verify, --verify-discord

**Description**: Verify Discord bot is running

```python
"discord-verify": {
    "name": "Verify Discord Running",
    "module": "tools.verify_discord_running",
    "main_function": "main",
    "description": "Verify Discord bot is running",
    "flags": ['--discord-verify', '--verify-discord'],
    "args_passthrough": True,
},
```

### Start Message Queue Processor

**ID**: `queue-start`

**Module**: `tools.start_message_queue_processor`

**Flags**: --queue-start, --start-queue

**Description**: Start message queue processor

```python
"queue-start": {
    "name": "Start Message Queue Processor",
    "module": "tools.start_message_queue_processor",
    "main_function": "main",
    "description": "Start message queue processor",
    "flags": ['--queue-start', '--start-queue'],
    "args_passthrough": True,
},
```

### Diagnose Queue

**ID**: `queue-diagnose`

**Module**: `tools.diagnose_queue`

**Flags**: --queue-diagnose, --diagnose-queue

**Description**: Diagnose message queue issues

```python
"queue-diagnose": {
    "name": "Diagnose Queue",
    "module": "tools.diagnose_queue",
    "main_function": "main",
    "description": "Diagnose message queue issues",
    "flags": ['--queue-diagnose', '--diagnose-queue'],
    "args_passthrough": True,
},
```

### Queue Status

**ID**: `queue-status`

**Module**: `tools.check_queue_status`

**Flags**: --queue-status, --q-status

**Description**: Check message queue status

```python
"queue-status": {
    "name": "Queue Status",
    "module": "tools.check_queue_status",
    "main_function": "main",
    "description": "Check message queue status",
    "flags": ['--queue-status', '--q-status'],
    "args_passthrough": True,
},
```

### Fix Stuck Message

**ID**: `fix-stuck-message`

**Module**: `tools.fix_stuck_message`

**Flags**: --fix-stuck, --unstuck

**Description**: Fix stuck messages in queue

```python
"fix-stuck-message": {
    "name": "Fix Stuck Message",
    "module": "tools.fix_stuck_message",
    "main_function": "main",
    "description": "Fix stuck messages in queue",
    "flags": ['--fix-stuck', '--unstuck'],
    "args_passthrough": True,
},
```

### Workspace Health Checker

**ID**: `workspace-health`

**Module**: `tools.workspace_health_checker`

**Flags**: --workspace-health, --health

**Description**: Check workspace health

```python
"workspace-health": {
    "name": "Workspace Health Checker",
    "module": "tools.workspace_health_checker",
    "main_function": "main",
    "description": "Check workspace health",
    "flags": ['--workspace-health', '--health'],
    "args_passthrough": True,
},
```

### Workspace Health Monitor

**ID**: `workspace-monitor`

**Module**: `tools.workspace_health_monitor`

**Flags**: --workspace-monitor, --monitor

**Description**: Monitor workspace health

```python
"workspace-monitor": {
    "name": "Workspace Health Monitor",
    "module": "tools.workspace_health_monitor",
    "main_function": "main",
    "description": "Monitor workspace health",
    "flags": ['--workspace-monitor', '--monitor'],
    "args_passthrough": True,
},
```

### Git Work Verifier

**ID**: `git-work-verify`

**Module**: `tools.git_work_verifier`

**Flags**: --git-work-verify, --verify-work

**Description**: Verify work in git history

```python
"git-work-verify": {
    "name": "Git Work Verifier",
    "module": "tools.git_work_verifier",
    "main_function": "main",
    "description": "Verify work in git history",
    "flags": ['--git-work-verify', '--verify-work'],
    "args_passthrough": True,
},
```

### GitHub Create and Push Repo

**ID**: `github-create-repo`

**Module**: `tools.github_create_and_push_repo`

**Flags**: --github-create, --create-repo

**Description**: Create and push GitHub repository

```python
"github-create-repo": {
    "name": "GitHub Create and Push Repo",
    "module": "tools.github_create_and_push_repo",
    "main_function": "main",
    "description": "Create and push GitHub repository",
    "flags": ['--github-create', '--create-repo'],
    "args_passthrough": True,
},
```

### Architectural Pattern Analyzer

**ID**: `arch-pattern-analyzer`

**Module**: `tools.architectural_pattern_analyzer`

**Flags**: --arch-pattern, --arch-analyze

**Description**: Analyze architectural patterns

```python
"arch-pattern-analyzer": {
    "name": "Architectural Pattern Analyzer",
    "module": "tools.architectural_pattern_analyzer",
    "main_function": "main",
    "description": "Analyze architectural patterns",
    "flags": ['--arch-pattern', '--arch-analyze'],
    "args_passthrough": True,
},
```

### Integration Pattern Analyzer

**ID**: `integration-pattern`

**Module**: `tools.integration_pattern_analyzer`

**Flags**: --integration-pattern, --int-pattern

**Description**: Analyze integration patterns

```python
"integration-pattern": {
    "name": "Integration Pattern Analyzer",
    "module": "tools.integration_pattern_analyzer",
    "main_function": "main",
    "description": "Analyze integration patterns",
    "flags": ['--integration-pattern', '--int-pattern'],
    "args_passthrough": True,
},
```

### Comprehensive Project Analyzer

**ID**: `comprehensive-analyzer`

**Module**: `tools.comprehensive_project_analyzer`

**Flags**: --comprehensive-analyze, --full-analyze

**Description**: Comprehensive project analysis

```python
"comprehensive-analyzer": {
    "name": "Comprehensive Project Analyzer",
    "module": "tools.comprehensive_project_analyzer",
    "main_function": "main",
    "description": "Comprehensive project analysis",
    "flags": ['--comprehensive-analyze', '--full-analyze'],
    "args_passthrough": True,
},
```

### Refactoring CLI

**ID**: `refactor-cli`

**Module**: `tools.refactoring_cli`

**Flags**: --refactor-cli, --refactor

**Description**: Refactoring command-line interface

```python
"refactor-cli": {
    "name": "Refactoring CLI",
    "module": "tools.refactoring_cli",
    "main_function": "main",
    "description": "Refactoring command-line interface",
    "flags": ['--refactor-cli', '--refactor'],
    "args_passthrough": True,
},
```

### Find File Size Violations

**ID**: `file-size-violations`

**Module**: `tools.find_file_size_violations`

**Flags**: --file-size-violations, --size-violations

**Description**: Find files violating size limits

```python
"file-size-violations": {
    "name": "Find File Size Violations",
    "module": "tools.find_file_size_violations",
    "main_function": "main",
    "description": "Find files violating size limits",
    "flags": ['--file-size-violations', '--size-violations'],
    "args_passthrough": True,
},
```

### Infrastructure Automation Suite

**ID**: `infra-automation`

**Module**: `tools.infrastructure_automation_suite`

**Flags**: --infra-automation, --infra-auto

**Description**: Infrastructure automation suite

```python
"infra-automation": {
    "name": "Infrastructure Automation Suite",
    "module": "tools.infrastructure_automation_suite",
    "main_function": "main",
    "description": "Infrastructure automation suite",
    "flags": ['--infra-automation', '--infra-auto'],
    "args_passthrough": True,
},
```

### Infrastructure Health Dashboard

**ID**: `infra-health-dashboard`

**Module**: `tools.infrastructure_health_dashboard`

**Flags**: --infra-health, --infra-dash

**Description**: Infrastructure health dashboard

```python
"infra-health-dashboard": {
    "name": "Infrastructure Health Dashboard",
    "module": "tools.infrastructure_health_dashboard",
    "main_function": "main",
    "description": "Infrastructure health dashboard",
    "flags": ['--infra-health', '--infra-dash'],
    "args_passthrough": True,
},
```

