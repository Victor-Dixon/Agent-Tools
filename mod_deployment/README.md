# 🎮 Mod Deployment Automation Pipeline

**Enterprise-grade mod deployment automation for game servers.**

Automate your entire Thunderstore mod deployment workflow with staging environments, health checks, rollback capabilities, and Discord notifications.

---

## 🚀 Quick Start

### Installation

```bash
# Clone or copy the mod_deployment directory
cd mod_deployment

# Install Python dependencies
pip install -r docker/requirements.txt

# For dashboard
pip install -r docker/requirements-dashboard.txt
```

### Basic Usage

```python
from mod_deployment.core import ThunderstoreClient, ModManager

# Search for mods
client = ThunderstoreClient(game="lethal-company")
results = client.search_packages("BiggerLobby")
print(f"Found {len(results)} mods")

# Install a mod
manager = ModManager(game_path="/path/to/game", game="lethal-company")
result = manager.install("bizzlemip-BiggerLobby")
print(f"Installed: {result.success}")

# Check for updates
updates = manager.update(dry_run=True)
print(f"Updates available: {len(updates)}")
```

---

## 📋 Features

### ✅ Thunderstore Integration
- Full API client for mod search, metadata, downloads
- Support for multiple games (Lethal Company, Valheim, Risk of Rain 2, etc.)
- Rate limiting and caching for performance

### ✅ Dependency Resolution
- Automatic transitive dependency resolution
- Version conflict detection and resolution
- Installation order calculation (topological sort)

### ✅ Profile Management
- Create/switch between mod profiles
- Import/export profiles for sharing
- Profile comparison and cloning

### ✅ Health Monitoring
- Server connectivity checks
- BepInEx load verification
- Plugin load status
- Custom health check hooks

### ✅ Rollback System
- Automatic rollback points before updates
- One-click rollback to previous states
- Configurable retention policy

### ✅ Docker Infrastructure
- Production and staging server containers
- Automated update watcher service
- Web dashboard for management
- Discord notifications

---

## 📁 Project Structure

```
mod_deployment/
├── core/                       # Core Python library
│   ├── __init__.py
│   ├── thunderstore_client.py  # Thunderstore API client
│   ├── mod_manager.py          # High-level mod management
│   ├── dependency_resolver.py  # Dependency resolution
│   ├── profile_manager.py      # Profile management
│   └── health_checker.py       # Health monitoring & rollback
│
├── docker/                     # Docker infrastructure
│   ├── Dockerfile.game-server  # Game server image
│   ├── Dockerfile.watcher      # Update watcher image
│   ├── Dockerfile.dashboard    # Dashboard image
│   ├── docker-compose.yml      # Full stack deployment
│   ├── requirements.txt        # Watcher dependencies
│   └── requirements-dashboard.txt
│
├── scripts/                    # Shell scripts
│   ├── entrypoint.sh          # Container entrypoint
│   ├── health_check.sh        # Health check script
│   ├── health_daemon.sh       # Health monitoring daemon
│   ├── rollback.sh            # Rollback script
│   └── deploy_mod.sh          # Mod deployment script
│
├── watcher/                    # Update watcher service
│   ├── __init__.py
│   └── main.py                # Watcher main loop
│
├── dashboard/                  # Web dashboard
│   ├── __init__.py
│   └── main.py                # FastAPI dashboard
│
├── profiles/                   # Mod profiles storage
├── backups/                    # Mod backups
│
└── README.md                   # This file
```

---

## 🔧 Core API Reference

### ThunderstoreClient

```python
from mod_deployment.core import ThunderstoreClient

# Initialize for a specific game
client = ThunderstoreClient(game="lethal-company")

# Search for mods
results = client.search_packages("MoreCompany", limit=10)

# Get mod info
package = client.get_package("notnotnotswipez-MoreCompany")
print(f"Downloads: {package.total_downloads}")
print(f"Latest: {package.latest_version.version_number}")

# Get trending mods
trending = client.get_trending(limit=20)

# Check for updates
installed = {"notnotnotswipez-MoreCompany": "1.7.0"}
updates = client.check_for_updates(installed)

# Download a mod
zip_path = client.download_mod("notnotnotswipez-MoreCompany", version="1.7.2")
```

### ModManager

```python
from mod_deployment.core import ModManager

# Initialize with game path
manager = ModManager(
    game_path="/srv/game/LethalCompany",
    game="lethal-company",
    auto_dependencies=True
)

# Install a mod (with dependencies)
result = manager.install("BiggerLobby", version="2.5.0")
if result.success:
    print(f"Installed to: {result.install_path}")
    print(f"Dependencies: {result.dependencies_installed}")

# Update all mods
updates = manager.update()

# Update specific mod
updates = manager.update(mod="BiggerLobby")

# Remove a mod
manager.remove("OldMod", remove_config=True)

# List installed mods
for mod in manager.list_installed():
    print(f"{mod['identifier']}: {mod['version']}")

# Get status
status = manager.get_status()
print(f"Installed: {status['installed_count']}")
print(f"Updates: {status['updates_available']}")
```

### DependencyResolver

```python
from mod_deployment.core import ThunderstoreClient, DependencyResolver

client = ThunderstoreClient(game="lethal-company")
resolver = DependencyResolver(client)

# Resolve dependencies for multiple mods
result = resolver.resolve(
    mods=["BiggerLobby-2.5.0", "MoreCompany-1.7.2"],
    installed={"BepInEx-BepInExPack": "5.4.2100"}
)

if result.success:
    print("Install order:")
    for mod in result.install_order:
        print(f"  - {mod}: {result.resolved[mod]}")
else:
    print(f"Conflicts: {result.conflicts}")
    print(f"Missing: {result.missing}")

# Get dependency tree
tree = resolver.get_dependency_tree("BiggerLobby")
```

### ProfileManager

```python
from mod_deployment.core import ProfileManager

profiles = ProfileManager(
    profiles_dir="/path/to/profiles",
    game="lethal-company"
)

# Create a profile
profile = profiles.create(
    name="vanilla-plus",
    description="Minimal QoL mods",
    mods={
        "BiggerLobby": "2.5.0",
        "MoreCompany": "1.7.2",
    },
    tags=["qol", "stable"]
)

# List profiles
for p in profiles.list():
    print(f"{p.name}: {len(p.mods)} mods")

# Activate a profile
profiles.activate("vanilla-plus")

# Clone a profile
profiles.clone("vanilla-plus", "vanilla-plus-v2")

# Export for sharing
profiles.export_profile("vanilla-plus", output_path="my_profile.json")

# Import a profile
profiles.import_profile("shared_profile.json", new_name="imported")

# Compare profiles
diff = profiles.compare("vanilla-plus", "vanilla-plus-v2")
print(f"Only in v1: {diff['only_in_profile1']}")
print(f"Version differences: {diff['version_differences']}")
```

### HealthChecker

```python
from mod_deployment.core import HealthChecker

checker = HealthChecker(
    game_path="/srv/game/LethalCompany",
    server_host="localhost",
    server_port=7777
)

# Run health check
result = checker.run_health_check()
print(f"Status: {result.status.value}")
print(f"Passed: {result.checks_passed}")
print(f"Failed: {result.checks_failed}")

# Create rollback point before update
snapshot = {"BiggerLobby": "2.5.0", "MoreCompany": "1.7.2"}
point = checker.create_rollback_point(
    description="Before updating mods",
    mods_snapshot=snapshot
)

# List rollback points
for rp in checker.list_rollback_points():
    print(f"{rp['id']}: {rp['description']}")

# Rollback to specific point
checker.rollback(rollback_id="rollback_20250127_143022")

# Rollback to latest
checker.rollback()

# Wait for healthy after deployment
success = checker.wait_for_healthy(
    timeout=120,
    auto_rollback=True
)
```

---

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
cd mod_deployment/docker

# Create .env file
cat > .env << EOF
GAME=lethal-company
STEAM_APP_ID=1966720
SERVER_NAME=My Server
DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
EOF

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f watcher

# Access dashboard
open http://localhost:8080
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| production | 7777 | Production game server |
| staging | 7778 | Staging/test server |
| watcher | - | Mod update watcher |
| dashboard | 8080 | Web management UI |
| redis | 6379 | State storage |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GAME` | lethal-company | Game identifier |
| `STEAM_APP_ID` | - | Steam app ID for installation |
| `SERVER_PORT` | 7777 | Game server port |
| `DISCORD_WEBHOOK` | - | Discord webhook for notifications |
| `CHECK_INTERVAL` | 3600 | Update check interval (seconds) |
| `AUTO_DEPLOY_TO_STAGING` | true | Auto-deploy to staging |
| `AUTO_DEPLOY_TO_PRODUCTION` | false | Auto-deploy to production |

---

## 🔌 MCP Server

The mod deployment system includes an MCP server for AI agent integration.

### Available Tools

| Tool | Description |
|------|-------------|
| `search_mods` | Search Thunderstore for mods |
| `get_mod_info` | Get detailed mod information |
| `install_mod` | Install a mod with dependencies |
| `update_mods` | Check and apply updates |
| `list_installed_mods` | List installed mods |
| `resolve_dependencies` | Resolve mod dependencies |
| `check_server_health` | Run health checks |
| `create_rollback_point` | Create rollback point |
| `rollback` | Rollback to previous state |
| `manage_profile` | Manage mod profiles |

### Using with Claude/AI Agents

```json
{
  "mcpServers": {
    "mod-deployment": {
      "command": "python",
      "args": ["/path/to/mcp_servers/mod_deployment_server.py"]
    }
  }
}
```

---

## 🎯 Supported Games

| Game | Identifier | Notes |
|------|------------|-------|
| Lethal Company | `lethal-company` | Full support |
| Valheim | `valheim` | Full support |
| Risk of Rain 2 | `risk-of-rain-2` | Full support |
| Content Warning | `content-warning` | Full support |
| GTFO | `gtfo` | Full support |
| Boneworks | `boneworks` | Full support |
| H3VR | `h3vr` | Full support |

---

## 📊 Business Automation Offer

### Pain Points This Solves

1. **Manual mod management** - No more daily Thunderstore checks
2. **Broken servers** - Health checks catch issues before players notice
3. **Dependency hell** - Automatic resolution prevents conflicts
4. **Downtime** - Rollback in seconds, not hours
5. **Version tracking** - Know exactly what's running on every server

### Value Proposition

> "We automate your entire mod deployment pipeline. We'll set up:
> - Auto-update system for Thunderstore mods
> - Staging server that tests mods before live
> - One-click rollback when updates break
> - Dashboard showing mod versions/dependencies
> 
> **Result:** Your server stays updated 24/7, zero manual work, no downtime from bad mods."

### Target Markets

1. **Game Server Hosting Companies** - GSP.gg, Nodecraft, etc.
2. **Large Gaming Communities** - Discord servers with 1000+ members
3. **Content Creators** - Streamers running subscriber servers
4. **Esports Organizations** - Tournament server management

---

## 🔒 Security Considerations

- Never commit Steam credentials to version control
- Use environment variables or secrets management
- Restrict dashboard access with authentication
- Regularly update dependencies

---

## 📄 License

MIT License - Use freely for personal and commercial projects.

---

## 🤝 Contributing

Contributions welcome! This system can be extended with:

- Additional game support
- More notification providers (Slack, email)
- Advanced health check plugins
- Mod configuration management
- Backup to cloud storage (S3, GCS)
