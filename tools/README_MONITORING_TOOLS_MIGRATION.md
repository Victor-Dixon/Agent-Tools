# Monitoring Tools Migration - Quick Reference

**Date**: 2025-12-06  
**Author**: Agent-7 (Web Development Specialist)  
**Status**: ✅ **QUICK REFERENCE COMPLETE**

---

## 🚀 **QUICK START**

**Old Tool** → **New Command**

```bash
# discord_bot_infrastructure_check.py
python tools/unified_monitor.py --category message_queue_file

# manually_trigger_status_monitor_resume.py
python tools/unified_monitor.py --category resume --agent Agent-7

# workspace_health_monitor.py
python tools/unified_monitor.py --category workspace --agent Agent-7

# captain_check_agent_status.py
python tools/unified_monitor.py --category agents
```

---

## 📋 **MIGRATION TABLE**

| Deprecated Tool | Unified Monitor Category | Example |
|----------------|-------------------------|---------|
| `discord_bot_infrastructure_check.py` | `message_queue_file` | `--category message_queue_file` |
| `manually_trigger_status_monitor_resume.py` | `resume` | `--category resume --agent Agent-7` |
| `workspace_health_monitor.py` (Phase 2) | `workspace` | `--category workspace --agent Agent-7` |
| `captain_check_agent_status.py` | `agents` | `--category agents` |

---

## 🎯 **COMMON COMMANDS**

```bash
# Full monitoring
python tools/unified_monitor.py --category all

# Agent workspace health
python tools/unified_monitor.py --category workspace --agent Agent-7

# Service health
python tools/unified_monitor.py --category service --service discord

# JSON output
python tools/unified_monitor.py --category all --json
```

---

## 📚 **FULL DOCUMENTATION**

- **Migration Guide**: `MIGRATION_GUIDE_DEPRECATED_MONITORING_TOOLS.md`
- **User Guide**: `UNIFIED_MONITORING_USER_GUIDE.md`
- **Capabilities**: `UNIFIED_MONITORING_CAPABILITIES.md`

🐝 **WE. ARE. SWARM. ⚡🔥🚀**

