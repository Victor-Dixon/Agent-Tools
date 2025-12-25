# 🐝 Swarm MCP Toolbelt

**Multi-Agent AI Coordination Framework** with Model Context Protocol (MCP) support.

Enable multiple AI agents (Claude, GPT, etc.) to work together autonomously - communicating, sharing knowledge, and coordinating tasks without human intervention.

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR AI SWARM                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐    messaging     ┌─────────┐                 │
│   │ Claude  │◄────system──────►│  GPT-4  │                 │
│   │ Agent-1 │                  │ Agent-2 │                 │
│   └────┬────┘                  └────┬────┘                 │
│        │         swarm-brain        │                       │
│        └──────────┬─────────────────┘                       │
│                   ▼                                         │
│   ┌─────────────────────────────────────────┐              │
│   │         SWARM MCP TOOLBELT              │              │
│   │  • Messaging    • Task Management       │              │
│   │  • Swarm Brain  • Mission Control       │              │
│   │  • Git Ops      • Code Quality          │              │
│   └─────────────────────────────────────────┘              │
│                   ▲                                         │
│        ┌──────────┴─────────────────┐                       │
│        │                            │                       │
│   ┌─────────┐                  ┌─────────┐                 │
│   │ Claude  │                  │ Gemini  │                 │
│   │ Agent-3 │                  │ Agent-4 │                 │
│   └─────────┘                  └─────────┘                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
pip install swarm-mcp-toolbelt
```

### Basic Usage

```python
from swarm_mcp import SwarmCoordinator, MessageQueue, SwarmBrain

# Initialize swarm with 3 agents
swarm = SwarmCoordinator(
    agents=["agent-1", "agent-2", "agent-3"],
    workspace="./agent_workspaces"
)

# Send message between agents
queue = MessageQueue()
queue.send("agent-1", "agent-2", "Please review PR #42")

# Share knowledge across swarm
brain = SwarmBrain()
brain.share_learning(
    agent_id="agent-1",
    category="debugging",
    title="Circular import fix",
    content="When ImportError occurs, check for circular imports..."
)

# Discover and assign tasks
tasks = swarm.discover_tasks("./src")
idle_agents = swarm.get_idle_agents()
for agent in idle_agents:
    task = swarm.get_optimal_assignment(agent)
    if task:
        swarm.assign_task(agent, task.description)
```

## 🔌 MCP Integration

Add to your Claude Desktop or Cursor config:

```json
{
  "mcpServers": {
    "swarm-messaging": {
      "command": "python",
      "args": ["-m", "swarm_mcp.servers.messaging"],
      "description": "Agent-to-agent communication"
    },
    "swarm-brain": {
      "command": "python",
      "args": ["-m", "swarm_mcp.servers.swarm_brain"],
      "description": "Collective memory and knowledge sharing"
    },
    "task-manager": {
      "command": "python",
      "args": ["-m", "swarm_mcp.servers.task_manager"],
      "description": "Task queue and inbox management"
    },
    "mission-control": {
      "command": "python",
      "args": ["-m", "swarm_mcp.servers.mission_control"],
      "description": "Agent coordination and leaderboard"
    }
  }
}
```

## 📦 MCP Servers

| Server | Tools | Description |
|--------|-------|-------------|
| **swarm-messaging** | `send_message`, `broadcast`, `get_inbox` | Agent-to-agent async communication |
| **task-manager** | `add_task`, `complete_task`, `get_tasks` | Task queue and inbox management |
| **swarm-brain** | `share_learning`, `search`, `record_decision` | Collective memory across agents |
| **mission-control** | `assign_mission`, `get_status`, `leaderboard` | Central coordination |
| **git-operations** | `verify_work`, `get_commits`, `validate` | Work verification |
| **code-quality** | `check_size`, `auto_extract`, `fix_lint` | Code compliance |
| **observability** | `get_metrics`, `health_check`, `slo_status` | System monitoring |
| **testing** | `run_coverage`, `mutation_test` | Test automation |

## 🧠 Core Concepts

### Agent Communication

Agents communicate via file-based message queues - simple, reliable, and works with any LLM:

```python
from swarm_mcp import MessageQueue, MessagePriority

queue = MessageQueue("./messages")

# Regular message
queue.send("agent-1", "agent-2", "Task completed")

# Urgent broadcast
queue.send(
    sender="captain",
    recipient="agent-3",
    content="CRITICAL: Production issue",
    priority=MessagePriority.URGENT
)

# Check inbox
messages = queue.get_inbox("agent-2", unread_only=True)
for msg in messages:
    print(f"From {msg.sender}: {msg.content}")
    queue.mark_read(msg.id, "agent-2")
```

### Swarm Brain (Collective Memory)

Agents share learnings that persist across sessions:

```python
from swarm_mcp import SwarmBrain

brain = SwarmBrain("./swarm_brain")

# Share a learning
brain.share_learning(
    agent_id="agent-1",
    category="performance",
    title="Redis caching pattern",
    content="Use TTL of 3600 for API responses...",
    tags=["caching", "redis", "api"]
)

# Search knowledge
results = brain.search("caching")
for learning in results:
    print(f"{learning.title}: {learning.content[:100]}...")

# Record decisions for future reference
brain.record_decision(
    agent_id="agent-2",
    decision="Used PostgreSQL over MongoDB",
    context="Need ACID transactions for payments",
    outcome="Zero data inconsistencies",
    success=True
)
```

### Task Coordination

Central coordinator manages work distribution:

```python
from swarm_mcp import SwarmCoordinator

swarm = SwarmCoordinator(
    agents=["frontend", "backend", "devops"],
    workspace="./workspaces"
)

# Check who's available
idle = swarm.get_idle_agents()
print(f"Available agents: {idle}")

# Assign specific work
swarm.assign_task("backend", "Implement user auth API", priority=1)

# Auto-discover work from codebase
tasks = swarm.discover_tasks("./src")
print(f"Found {len(tasks)} tasks (TODOs, FIXMEs, etc.)")

# Smart assignment based on skills
for agent in idle:
    best_task = swarm.get_optimal_assignment(agent)
    if best_task:
        swarm.assign_task(agent, best_task.description)
```

## 🏗️ Architecture

```
swarm_mcp/
├── core/
│   ├── coordinator.py   # SwarmCoordinator - central orchestration
│   ├── messaging.py     # MessageQueue - agent communication
│   └── brain.py         # SwarmBrain - collective memory
├── servers/
│   ├── messaging.py     # MCP server for messaging
│   ├── task_manager.py  # MCP server for tasks
│   ├── swarm_brain.py   # MCP server for knowledge
│   └── ...              # Other MCP servers
└── tools/
    └── ...              # CLI tools
```

## 🎯 Use Cases

### 1. Autonomous Development Team
```
Captain Agent → assigns tasks → Worker Agents
                              ← report progress ←
```

### 2. Code Review Swarm
```
Author Agent → submits PR → Reviewer Agents
            ← feedback ←
```

### 3. Debugging Squad
```
Triage Agent → identifies bug → Specialist Agents
                             ← fix proposals ←
```

### 4. Documentation Team
```
Writer Agent → drafts docs → Editor Agents
            ← improvements ←
```

## 🔧 Configuration

### Environment Variables

```bash
SWARM_WORKSPACE=./agent_workspaces
SWARM_BRAIN_DIR=./swarm_brain
SWARM_MESSAGE_DIR=./messages
SWARM_LOG_LEVEL=INFO
```

### Agent Specialties

```python
swarm = SwarmCoordinator(
    agents=["agent-1", "agent-2"],
    config={
        "specialties": {
            "agent-1": ["frontend", "react", "css"],
            "agent-2": ["backend", "python", "api"]
        }
    }
)
```

## 📊 Observability

Monitor your swarm:

```python
# Get brain stats
stats = brain.get_stats()
print(f"Total learnings: {stats['total_learnings']}")
print(f"Total decisions: {stats['total_decisions']}")

# Check agent status
for agent in swarm.agents:
    status = swarm.get_status(agent)
    print(f"{agent}: {status.status} - {status.current_task or 'idle'}")
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🌟 Star History

If this project helps you build amazing multi-agent systems, please give it a ⭐!

---

**Built with 🐝 by the Swarm Team**

*"The future of AI is not one agent - it's many agents working together."*
