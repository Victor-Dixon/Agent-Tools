# 🐺 Wolfpack MCP

**Multi-Agent AI Coordination Framework** with Model Context Protocol (MCP) support.

*"Alone we are strong. Together we are unstoppable."*

Enable a pack of AI agents (Claude, GPT, etc.) to hunt together - communicating, sharing knowledge, and coordinating attacks without human intervention.

```
┌─────────────────────────────────────────────────────────────┐
│                     THE WOLFPACK                            │
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
│   │         WOLFPACK MCP TOOLBELT           │              │
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
pip install wolfpack-mcp
```

### Basic Usage

```python
from wolfpack_mcp import PackCoordinator, MessageQueue, PackMemory

# Initialize pack with wolves
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
    "pack-messaging": {
      "command": "python",
      "args": ["-m", "wolfpack_mcp.servers.messaging"],
      "description": "Wolf-to-wolf communication"
    },
    "pack-memory": {
      "command": "python",
      "args": ["-m", "wolfpack_mcp.servers.memory"],
      "description": "Collective hunting knowledge"
    },
    "den-manager": {
      "command": "python",
      "args": ["-m", "wolfpack_mcp.servers.den_manager"],
      "description": "Task queue and territory management"
    },
    "alpha-control": {
      "command": "python",
      "args": ["-m", "wolfpack_mcp.servers.alpha_control"],
      "description": "Pack coordination and rankings"
    }
  }
}
```

## 📦 MCP Servers

| Server | Tools | Description |
|--------|-------|-------------|
| **pack-messaging** | `howl`, `broadcast`, `listen` | Wolf-to-wolf async communication |
| **den-manager** | `assign_hunt`, `complete_hunt`, `get_hunts` | Hunt/task management |
| **pack-memory** | `share_lore`, `recall`, `record_hunt` | Collective knowledge |
| **alpha-control** | `roll_call`, `assign_territory`, `rankings` | Pack coordination |
| **git-operations** | `verify_kill`, `get_commits`, `validate` | Hunt verification |
| **code-quality** | `check_size`, `auto_extract`, `fix_lint` | Code compliance |
| **observability** | `get_metrics`, `health_check`, `slo_status` | Pack monitoring |
| **testing** | `run_coverage`, `mutation_test` | Test automation |

## 🐺 CLI Commands

```bash
# Check pack status
wolfpack status --wolves alpha,beta,scout-1

# Send a howl
wolfpack howl alpha scout-1 "Hunt the bug in auth.py"

# Listen for incoming howls
wolfpack listen scout-1 --unheard

# Search pack memory
wolfpack recall "circular import"

# Share wisdom
wolfpack share --wolf beta --category debugging \
  --title "Import fix pattern" \
  --wisdom "When ImportError occurs..."

# Scout territory for prey
wolfpack scout --path ./src --limit 20
```

## 🧠 Core Concepts

### The Pack Hierarchy

```
👑 Alpha    - Coordinates the pack, assigns territory
🐺 Beta     - Second in command, handles complex hunts  
🐺 Scouts   - Find prey, execute hunts
🐺 Omega    - Learning wolves, simple tasks
```

### Howls (Communication)

Wolves communicate through howls - async, persistent, reliable:

```python
from wolfpack_mcp import MessageQueue, HowlUrgency

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
    queue.mark_heard(howl.id, "alpha")
```

### Pack Memory (Collective Knowledge)

The pack remembers. Every hunt teaches something:

```python
from wolfpack_mcp import PackMemory

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

# Record hunt decisions
memory.record_hunt(
    wolf_id="beta",
    decision="Used PostgreSQL over MongoDB",
    context="Need ACID transactions for payments",
    outcome="Zero data inconsistencies",
    success=True
)
```

### Pack Coordination

The Alpha coordinates without micromanaging:

```python
from wolfpack_mcp import PackCoordinator

pack = PackCoordinator(
    wolves=["alpha", "beta", "scout-1", "scout-2"],
    den="./wolf_den"
)

# Roll call
status = pack.roll_call()
for wolf_id, wolf_status in status.items():
    print(f"🐺 {wolf_id}: {wolf_status.status}")

# Find ready wolves
ready = pack.get_ready_wolves()
print(f"Ready for the hunt: {ready}")

# Assign specific hunt
pack.assign_hunt("scout-1", "Fix authentication bug", difficulty=2)

# Broadcast to pack
pack.broadcast("Pack meeting at sunset", urgency=3)

# Scout and auto-assign
prey = pack.scout_territory("./src")
for wolf in ready:
    best = pack.get_best_prey(wolf)
    if best:
        pack.assign_hunt(wolf, best.description)
```

## 🎯 Use Cases

### 1. Autonomous Dev Pack
```
Alpha (Captain) → assigns hunts → Scout wolves
                                ← report kills ←
```

### 2. Code Review Pack
```
Author wolf → submits PR → Reviewer wolves
           ← feedback ←
```

### 3. Bug Hunting Pack
```
Triage wolf → identifies bug → Specialist wolves
                            ← fix proposals ←
```

### 4. Documentation Pack
```
Writer wolf → drafts docs → Editor wolves
           ← improvements ←
```

## 🔧 Configuration

### Environment Variables

```bash
WOLFPACK_DEN=./wolf_den
WOLFPACK_MEMORY=./pack_memory
WOLFPACK_MESSAGES=./pack_messages
WOLFPACK_LOG_LEVEL=INFO
```

### Wolf Territories (Specialties)

```python
pack = PackCoordinator(
    wolves=["alpha", "beta", "scout-1", "scout-2"],
    config={
        "territories": {
            "alpha": ["coordination", "architecture"],
            "beta": ["backend", "python", "api"],
            "scout-1": ["frontend", "react", "css"],
            "scout-2": ["devops", "infrastructure"]
        }
    }
)
```

## 📊 Pack Stats

```python
# Memory stats
stats = memory.pack_stats()
print(f"Total lore: {stats['total_lore']}")
print(f"Total hunts: {stats['total_hunts']}")

# Pack status
for wolf in pack.wolves:
    status = pack.get_status(wolf)
    print(f"🐺 {wolf}: {status.kills} kills")
```

## 🏗️ Architecture

```
wolfpack_mcp/
├── core/
│   ├── coordinator.py   # PackCoordinator - Alpha's control
│   ├── messaging.py     # Howls - wolf communication
│   └── memory.py        # PackMemory - collective wisdom
├── servers/
│   ├── messaging.py     # MCP server for howls
│   ├── den_manager.py   # MCP server for hunts
│   ├── pack_memory.py   # MCP server for knowledge
│   └── ...              # Other MCP servers
└── tools/
    └── ...              # CLI tools
```

## 🤝 Contributing

We welcome new wolves to the pack! See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

MIT License - see [LICENSE](LICENSE).

## 🌟 Join the Pack

If this helps you build amazing multi-agent systems, give it a ⭐!

---

**Built by the Wolfpack 🐺**

*"The strength of the pack is the wolf, and the strength of the wolf is the pack."*
