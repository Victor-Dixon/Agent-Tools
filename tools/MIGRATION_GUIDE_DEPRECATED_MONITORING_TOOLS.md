# Migration Guide - Deprecated Monitoring Tools

**Date**: 2025-12-06  
**Author**: Agent-7 (Web Development Specialist)  
**Status**: ✅ **MIGRATION GUIDE COMPLETE**

---

## 📋 **OVERVIEW**

This guide documents the migration from deprecated monitoring tools to `unified_monitor.py`, which consolidates 33+ individual monitoring tools into a single unified system.

**Target Tool**: `tools/unified_monitor.py`  
**Phase**: Phase 2 Complete (Agent-1 & Agent-3)

---

## 🔄 **DEPRECATED TOOLS → UNIFIED_MONITOR.PY MAPPING**

**Consolidation Phases**:
- **Phase 1**: Initial consolidation (discord_bot_infrastructure_check, manually_trigger_status_monitor_resume)
- **Phase 2**: Workspace and agent status monitoring (workspace_health_monitor, captain_check_agent_status) - Agent-1

### **1. `discord_bot_infrastructure_check.py`** ✅ CONSOLIDATED

**Deprecated Functionality**: Check message queue file status  
**New Method**: `check_message_queue_file()`

**Before**:
```bash
python tools/discord_bot_infrastructure_check.py
```

**After**:
```bash
python tools/unified_monitor.py --category message_queue_file
# Or for full monitoring:
python tools/unified_monitor.py --category all
```

**What Changed**:
- Checks queue file existence, readability, writability
- Validates JSON format
- Returns file size and last modified time
- Status: `HEALTHY`, `MISSING`, `INVALID_JSON`, `NOT_READABLE`, `NOT_WRITABLE`

---

### **2. `manually_trigger_status_monitor_resume.py`** ✅ CONSOLIDATED

**Deprecated Functionality**: Trigger agent status monitor resume  
**New Method**: `trigger_status_monitor_resume()`

**Before**:
```bash
python tools/manually_trigger_status_monitor_resume.py --agent Agent-7
```

**After**:
```bash
python tools/unified_monitor.py --category resume --agent Agent-7
# Force resume:
python tools/unified_monitor.py --category resume --agent Agent-7 --force
```

**What Changed**:
- Supports both single agent and all agents
- Force flag for immediate triggers
- Async execution with status reporting
- Better error handling and logging

---

### **3. `workspace_health_monitor.py`** ✅ CONSOLIDATED (Phase 2 - Agent-1)

**Deprecated Functionality**: Monitor agent workspace health  
**New Method**: `monitor_workspace_health()`  
**Consolidation Date**: Phase 2 (2025-12-05)  
**Consolidated By**: Agent-1 (Integration & Core Systems Specialist)

**Before**:
```bash
python tools/workspace_health_monitor.py --agent Agent-7
```

**After**:
```bash
python tools/unified_monitor.py --category workspace --agent Agent-7
# All workspaces:
python tools/unified_monitor.py --category workspace
```

**What Changed**:
- ✅ Monitors inbox, archive, devlogs, reports
- ✅ Checks status file consistency and currency
- ✅ Health scoring (0-100) with detailed metrics
- ✅ Recommendations for workspace improvements
- ✅ Old message detection (>7 days cutoff)
- ✅ Status file currency checks (<24 hours = current)
- ✅ Unprocessed message tracking
- ✅ Workspace organization metrics

**Enhanced Capabilities in Unified Monitor**:
- Single agent or all agents monitoring
- Average health score across all workspaces
- Detailed per-workspace breakdown
- Issues found count and categorization
- Actionable recommendations list

---

### **4. `captain_check_agent_status.py`** ✅ CONSOLIDATED (Phase 2)

**Deprecated Functionality**: Check agent status from status.json files  
**New Method**: `monitor_agent_status()`

**Before**:
```bash
python tools/captain_check_agent_status.py
```

**After**:
```bash
python tools/unified_monitor.py --category agents
# Or as part of full monitoring:
python tools/unified_monitor.py --category all
```

**What Changed**:
- Reads all agent status.json files
- Reports active vs total agents
- Includes last updated timestamp
- Mission preview (first 100 chars)
- Better error handling for missing/invalid files

---

## 📚 **CLI MIGRATION EXAMPLES**

### **Single Category Monitoring**

```bash
# Queue health
python tools/unified_monitor.py --category queue

# Message queue file
python tools/unified_monitor.py --category message_queue_file

# Service health (specify service name)
python tools/unified_monitor.py --category service --service discord

# Disk usage
python tools/unified_monitor.py --category disk

# Agent status
python tools/unified_monitor.py --category agents

# Workspace health (all)
python tools/unified_monitor.py --category workspace

# Workspace health (single agent)
python tools/unified_monitor.py --category workspace --agent Agent-7

# Test coverage
python tools/unified_monitor.py --category coverage

# Resume trigger
python tools/unified_monitor.py --category resume --agent Agent-7

# Full monitoring (all categories)
python tools/unified_monitor.py --category all
```

### **JSON Output**

```bash
# Get JSON output for automation
python tools/unified_monitor.py --category all --json
```

### **Resume Operations**

```bash
# Trigger resume for specific agent
python tools/unified_monitor.py --category resume --agent Agent-7

# Force resume (immediate)
python tools/unified_monitor.py --category resume --agent Agent-7 --force

# Trigger resume for all agents
python tools/unified_monitor.py --category resume
```

---

## 🔍 **MONITORING CATEGORIES**

### **Available Categories**:

1. **`queue`** - Deferred push queue health
2. **`message_queue_file`** - Message queue file status
3. **`service`** - Service health (requires `--service` flag)
4. **`disk`** - Disk usage monitoring
5. **`agents`** - Agent status monitoring
6. **`workspace`** - Workspace health (optional `--agent` flag)
7. **`coverage`** - Test coverage tracking
8. **`resume`** - Resume trigger (optional `--agent` flag, optional `--force`)
9. **`all`** - Run all monitoring checks

---

## 📊 **OUTPUT FORMAT**

### **Human-Readable Output** (Default)

```
======================================================================
📊 UNIFIED MONITORING REPORT
======================================================================

✅ Deferred Push Queue: HEALTHY
   Pending: 0, Failed: 0

✅ Message Queue File: HEALTHY
   Size: 1,234 bytes, Valid JSON: True

✅ Github Pusher: RUNNING
✅ Discord: RUNNING

💾 Disk Usage:
   ✅ C:/: 45.2% used (120.5 GB free)
   ✅ D:/: 62.8% used (89.3 GB free)

👥 Agents: 6/8 active

📊 Workspace Health: 85.5/100 avg (8 workspaces)

🧪 Test Files: 247

🕐 Timestamp: 2025-12-06T00:30:00
======================================================================
```

### **JSON Output** (`--json` flag)

```json
{
  "timestamp": "2025-12-06T00:30:00",
  "checks": {
    "queue": {
      "category": "queue",
      "status": "HEALTHY",
      "score": 100,
      "stats": {
        "total": 10,
        "pending": 0,
        "failed": 0
      }
    },
    "agents": {
      "category": "agents",
      "total_agents": 8,
      "active_agents": 6,
      "agent_statuses": [...]
    }
  }
}
```

---

## ✅ **MIGRATION CHECKLIST**

### **Step 1: Update Scripts**
- [ ] Replace deprecated tool calls with `unified_monitor.py`
- [ ] Update category names (`--category` flag)
- [ ] Add service name flag if using service monitoring
- [ ] Add agent flag if monitoring specific agents

### **Step 2: Update Automation**
- [ ] Update CI/CD pipelines
- [ ] Update scheduled jobs
- [ ] Update monitoring dashboards
- [ ] Update alert systems

### **Step 3: Test Migration**
- [ ] Verify output format matches expectations
- [ ] Test JSON output for automation
- [ ] Verify error handling
- [ ] Test all monitoring categories

### **Step 4: Update Documentation**
- [ ] Update runbooks
- [ ] Update monitoring guides
- [ ] Update API documentation
- [ ] Archive deprecated tool documentation

---

## 🎯 **BENEFITS OF MIGRATION**

1. **Consolidation**: Single tool replaces 33+ monitoring tools
2. **Consistency**: Unified output format across all monitoring
3. **Maintainability**: Single codebase for all monitoring
4. **Extensibility**: Easy to add new monitoring categories
5. **JSON Support**: Better integration with automation
6. **Better Error Handling**: Comprehensive error reporting
7. **Performance**: Optimized monitoring execution

---

## 🚨 **TROUBLESHOOTING**

### **Issue: Category Not Found**
**Solution**: Use `--category all` or check available categories in `--help`

### **Issue: Service Not Found**
**Solution**: Ensure `--service` flag is provided for service monitoring

### **Issue: JSON Output Not Parsing**
**Solution**: Check for errors in output, verify JSON structure

### **Issue: Agent Status Missing**
**Solution**: Verify `status.json` exists in agent workspace

---

## 📚 **REFERENCES**

- **Unified Monitor**: `tools/unified_monitor.py`
- **Tool Documentation**: `tools/UNIFIED_MONITORING_USER_GUIDE.md`
- **Capabilities**: `tools/UNIFIED_MONITORING_CAPABILITIES.md`
- **Archived Tools**: `tools/ARCHIVED_TOOLS_MIGRATION_GUIDE.md`

---

## 📦 **ARCHIVING STATUS**

### **Archived Tools**:
- ✅ `captain_check_agent_status.py` - Archived to `tools/deprecated/consolidated_2025-12-05/` (2025-12-05)

**Note**: See `tools/ARCHIVED_TOOLS_MIGRATION_GUIDE.md` for complete archived tools documentation.

---

**Status**: ✅ **MIGRATION GUIDE COMPLETE**  
**Next Steps**: Migrate automation scripts, update CI/CD pipelines

🐝 **WE. ARE. SWARM. ⚡🔥🚀**

