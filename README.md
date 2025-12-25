# 🐺 WE ARE SWARM

**Multi-Agent AI Coordination Framework** with Model Context Protocol (MCP) support.

*A pack of wolves, not bees.*

*"Alone we are strong. Together we are unstoppable."*

Enable a swarm of AI agents (Claude, GPT, etc.) to hunt together - communicating, sharing knowledge, and coordinating attacks without human intervention.

```
┌─────────────────────────────────────────────────────────────┐
│                     WE ARE SWARM 🐺                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐      howls       ┌─────────┐                 │
│   │  Alpha  │◄────────────────►│  Beta   │                 │
│   │ Claude  │                  │  GPT-4  │                 │
│   └────┬────┘                  └────┬────┘                 │
│        │        pack memory         │                       │
│        └──────────┬─────────────────┘                       │
│                   ▼                                         │
│   ┌─────────────────────────────────────────┐              │
│   │           SWARM MCP TOOLBELT            │              │
│   │  • Howls (messaging)  • Den (tasks)     │              │
│   │  • Pack Memory        • Alpha Control   │              │
│   │  • Territory (git)    • Hunt Quality    │              │
│   └─────────────────────────────────────────┘              │
│                   ▲                                         │
│        ┌──────────┴─────────────────┐                       │
│        │                            │                       │
│   ┌─────────┐                  ┌─────────┐                 │
│   │ Scout-1 │                  │ Scout-2 │                 │
│   │ Claude  │                  │ Gemini  │                 │
│   └─────────┘                  └─────────┘                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
pip install swarm-mcp
```

### Basic Usage

```python
from swarm_mcp import PackCoordinator, MessageQueue, PackMemory

# Initialize the swarm
pack = PackCoordinator(
    wolves=["alpha", "beta", "scout-1", "scout-2"],
    den="./wolf_den"
)

# Howl between wolves
queue = MessageQueue()
queue.send("alpha", "scout-1", "Hunt the bug in auth.py")

# Share hunting wisdom
memory = PackMemory()
memory.share_lore(
    wolf_id="beta",
    category="debugging",
    title="Tracking circular imports",
    wisdom="When ImportError strikes, follow the import chain..."
)

# Scout for prey and assign hunts
prey = pack.scout_territory("./src")
ready_wolves = pack.get_ready_wolves()
for wolf in ready_wolves:
    target = pack.get_best_prey(wolf)
    if target:
        pack.assign_hunt(wolf, target.description)
```

## 🔌 MCP Integration

Add to your Claude Desktop or Cursor config:

```json
{
  "mcpServers": {
    "swarm-messaging": {
      "command": "python",
      "args": ["-m", "swarm_mcp.servers.messaging"],
      "description": "🐺 Wolf-to-wolf communication"
    },
    "swarm-memory": {
      "command": "python",
      "args": ["-m", "swarm_mcp.servers.memory"],
      "description": "🐺 Collective pack knowledge"
    },
    "swarm-tasks": {
      "command": "python",
      "args": ["-m", "swarm_mcp.servers.tasks"],
      "description": "🐺 Hunt queue and territory"
    },
    "swarm-control": {
      "command": "python",
      "args": ["-m", "swarm_mcp.servers.control"],
      "description": "🐺 Alpha coordination"
    }
  }
}
```

## 🐺 CLI Commands

```bash
# Check swarm status
swarm status --wolves alpha,beta,scout-1

# Send a howl
swarm howl alpha scout-1 "Hunt the bug in auth.py"

# Listen for incoming howls
swarm listen scout-1 --unheard

# Search pack memory
swarm recall "circular import"

# Share wisdom
swarm share --wolf beta --category debugging \
  --title "Import fix pattern" \
  --wisdom "When ImportError occurs..."

# Scout territory for prey
swarm scout --path ./src --limit 20
```

## 📦 MCP Servers

| Server | Tools | Description |
|--------|-------|-------------|
| **swarm-messaging** | `howl`, `broadcast`, `listen` | Wolf-to-wolf async communication |
| **swarm-tasks** | `assign_hunt`, `complete_hunt`, `get_hunts` | Hunt/task management |
| **swarm-memory** | `share_lore`, `recall`, `record_hunt` | Collective knowledge |
| **swarm-control** | `roll_call`, `assign_territory`, `rankings` | Pack coordination |
| **git-operations** | `verify_kill`, `get_commits`, `validate` | Hunt verification |
| **code-quality** | `check_size`, `auto_extract`, `fix_lint` | Code compliance |

## 🧠 Core Concepts

### The Swarm Hierarchy

```
👑 Alpha    - Coordinates the swarm, assigns territory
🐺 Beta     - Second in command, handles complex hunts  
🐺 Scouts   - Find prey, execute hunts
🐺 Omega    - Learning wolves, simple tasks
```

### Howls (Communication)

Wolves communicate through howls - async, persistent, reliable:

```python
from swarm_mcp import MessageQueue, HowlUrgency

queue = MessageQueue("./pack_messages")

# Regular howl
queue.send("scout-1", "alpha", "Prey spotted in sector 7")

# Emergency howl
queue.send(
    sender="beta",
    recipient="alpha",
    content="CRITICAL: Production down!",
    urgency=HowlUrgency.EMERGENCY
)

# Listen for howls
howls = queue.listen("alpha", unheard_only=True)
for howl in howls:
    print(f"🐺 {howl.sender}: {howl.content}")
```

### Pack Memory (Collective Knowledge)

The swarm remembers. Every hunt teaches something:

```python
from swarm_mcp import PackMemory

memory = PackMemory("./pack_memory")

# Share hunting wisdom
memory.share_lore(
    wolf_id="scout-1",
    category="performance",
    title="Redis caching pattern",
    wisdom="Use TTL of 3600 for API responses...",
    tags=["caching", "redis", "api"]
)

# Recall wisdom
lore = memory.recall("caching")
for wisdom in lore:
    print(f"📜 {wisdom.title}: {wisdom.wisdom[:100]}...")
```

### Swarm Coordination

The Alpha coordinates without micromanaging:

```python
from swarm_mcp import PackCoordinator

pack = PackCoordinator(
    wolves=["alpha", "beta", "scout-1", "scout-2"],
    den="./wolf_den"
)

# Roll call
status = pack.roll_call()
for wolf_id, wolf_status in status.items():
    print(f"🐺 {wolf_id}: {wolf_status.status}")

# Assign hunt
pack.assign_hunt("scout-1", "Fix authentication bug", difficulty=2)

# Broadcast to swarm
pack.broadcast("Swarm meeting at sunset", urgency=3)
```

## 🏗️ Architecture

```
swarm_mcp/
├── core/
│   ├── coordinator.py   # PackCoordinator - Alpha's control
│   ├── messaging.py     # Howls - wolf communication
│   └── memory.py        # PackMemory - collective wisdom
├── servers/
│   ├── messaging.py     # MCP server for howls
│   ├── tasks.py         # MCP server for hunts
│   ├── memory.py        # MCP server for knowledge
│   └── ...              # Other MCP servers
└── tools/
    └── ...              # CLI tools
```

## 🤝 Contributing

We welcome new wolves to the swarm! See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

MIT License - see [LICENSE](LICENSE).

---

## 🐺 WE ARE SWARM

*"The strength of the pack is the wolf, and the strength of the wolf is the pack."*

**Alone we are strong. Together we are unstoppable.**
