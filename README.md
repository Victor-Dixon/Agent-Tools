# Agent Tools Repository

This repository contains all tools used by the Agent Swarm system for autonomous operations, coordination, and task execution.

## Structure

- **`tools/`** - Legacy tools and individual utility scripts
- **`tools_v2/`** - Modern toolbelt system with categorized tools, adapters, and core infrastructure

## Tool Categories

### Tools V2 System

The `tools_v2/` directory contains the modern toolbelt architecture:

- **`categories/`** - Tool categories organized by domain:
  - `bi_tools.py` - Business Intelligence tools
  - `captain_tools.py` - Captain coordination tools
  - `communication_tools.py` - Messaging and communication
  - `compliance_tools.py` - V2 compliance checking
  - `infrastructure_tools.py` - Infrastructure management
  - `swarm_brain_tools.py` - Swarm knowledge management
  - And many more...

- **`adapters/`** - Tool adapter interfaces
- **`core/`** - Core toolbelt infrastructure
- **`utils/`** - Utility functions

### Legacy Tools

The `tools/` directory contains individual utility scripts for:
- Agent coordination and messaging
- WordPress deployment and management
- Site auditing and health checks
- Content management
- Analysis and reporting
- And more...

## Usage

Tools can be executed directly or through the toolbelt system:

```bash
# Direct execution
python tools/check_toolbelt_health.py

# Through toolbelt
python -m tools_v2.advisor_cli --tool bi.metrics
```

## Contributing

When adding new tools:
1. Place in appropriate category in `tools_v2/categories/`
2. Register in `tools_v2/tool_registry.lock.json`
3. Add tests in `tools_v2/tests/`
4. Update this README if adding new categories

## License

Part of the Agent Swarm system.

