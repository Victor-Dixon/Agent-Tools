# Unified Monitoring Tool - User Guide

**Date**: 2025-12-06  
**Author**: Agent-7 (Web Development Specialist)  
**Version**: Phase 2 Complete  
**Status**: ✅ **USER GUIDE COMPLETE**

---

## 📋 **OVERVIEW**

`unified_monitor.py` is a comprehensive monitoring tool that consolidates 33+ individual monitoring tools into a single unified system. It provides monitoring capabilities for queues, services, agents, workspaces, disk usage, and test coverage.

---

## 🚀 **QUICK START**

### **Basic Usage**

```bash
# Run all monitoring checks
python tools/unified_monitor.py --category all

# Monitor specific category
python tools/unified_monitor.py --category agents

# Get JSON output
python tools/unified_monitor.py --category all --json
```

---

## 📊 **MONITORING CATEGORIES**

### **1. Queue Health** (`--category queue`)

Monitors deferred push queue health and statistics.

**Output**:
- Queue status: `HEALTHY`, `DEGRADED`, `UNHEALTHY`
- Health score: 0-100
- Statistics: total, pending, failed entries

**Example**:
```bash
python tools/unified_monitor.py --category queue
```

---

### **2. Message Queue File** (`--category message_queue_file`)

Checks message queue file (`message_queue/queue.json`) status.

**Output**:
- File existence and accessibility
- JSON validity
- File size and last modified time
- Read/write permissions

**Status Values**:
- `HEALTHY` - File exists, readable, writable, valid JSON
- `MISSING` - File does not exist
- `INVALID_JSON` - File exists but contains invalid JSON
- `NOT_READABLE` - File exists but cannot be read
- `NOT_WRITABLE` - File exists but cannot be written

**Example**:
```bash
python tools/unified_monitor.py --category message_queue_file
```

---

### **3. Service Health** (`--category service --service <name>`)

Monitors specific service health by checking if process is running.

**Supported Services**:
- `github_pusher`
- `discord`
- `ci_cd`
- Any service name (searches process command line)

**Example**:
```bash
# Check Discord service
python tools/unified_monitor.py --category service --service discord

# Check GitHub pusher
python tools/unified_monitor.py --category service --service github_pusher
```

**Output**:
- Service status: `RUNNING`, `STOPPED`, `UNKNOWN`
- Running boolean flag
- Timestamp

---

### **4. Disk Usage** (`--category disk`)

Monitors disk usage for specified paths (defaults to C:/ and D:/).

**Output**:
- Total and free space (GB)
- Used percentage
- Status: `OK` (<90%), `WARNING` (90-95%), `CRITICAL` (>95%)

**Example**:
```bash
python tools/unified_monitor.py --category disk
```

---

### **5. Agent Status** (`--category agents`)

Monitors all agent statuses from `status.json` files.

**Output**:
- Total agents count
- Active agents count
- Individual agent statuses (agent_id, status, last_updated, current_mission preview)

**Example**:
```bash
python tools/unified_monitor.py --category agents
```

---

### **6. Workspace Health** (`--category workspace [--agent <id>]`) - Phase 2

Monitors agent workspace health (inbox, status files, organization).

**Consolidated From**: `workspace_health_monitor.py` (Phase 2 - Agent-1)

**Features**:
- Inbox message counts (total, unprocessed, old messages >7 days)
- Archive, devlogs, reports counts
- Status file existence and currency (<24 hours = current)
- Status consistency checks
- Health score (0-100) with detailed breakdown
- Actionable recommendations for improvements
- Unprocessed message tracking
- Workspace organization metrics

**Example**:
```bash
# All workspaces
python tools/unified_monitor.py --category workspace

# Specific agent workspace
python tools/unified_monitor.py --category workspace --agent Agent-7
```

**Health Score Factors**:
- Inbox organization (unprocessed messages, old messages)
- Status file currency (<24 hours = current)
- Status consistency
- File organization

---

### **7. Test Coverage** (`--category coverage`)

Monitors test coverage tracking.

**Output**:
- Total test files count
- Test file locations
- Coverage statistics

**Example**:
```bash
python tools/unified_monitor.py --category coverage
```

---

### **8. Resume Trigger** (`--category resume [--agent <id>] [--force]`)

Triggers status monitor resume for agents.

**Options**:
- `--agent <id>` - Trigger resume for specific agent (default: all agents)
- `--force` - Force immediate resume (skip checks)

**Example**:
```bash
# Trigger resume for all agents
python tools/unified_monitor.py --category resume

# Trigger resume for specific agent
python tools/unified_monitor.py --category resume --agent Agent-7

# Force immediate resume
python tools/unified_monitor.py --category resume --agent Agent-7 --force
```

---

### **9. All Categories** (`--category all`)

Runs all monitoring checks in sequence.

**Example**:
```bash
python tools/unified_monitor.py --category all
```

**Includes**:
- Queue health
- Message queue file
- Service health (GitHub pusher, Discord)
- Disk usage
- Agent status
- Workspace health (all)
- Test coverage

---

## 🎯 **CLI OPTIONS**

### **Required Options**

- `--category`, `-c` - Monitoring category (queue, message_queue_file, service, disk, agents, workspace, coverage, resume, all)

### **Optional Options**

- `--service` - Service name (required for `service` category)
- `--agent` - Agent ID (optional for `workspace` and `resume` categories)
- `--force` - Force immediate action (for `resume` category)
- `--json` - Output in JSON format (for automation)
- `--help`, `-h` - Show help message

---

## 📤 **OUTPUT FORMATS**

### **Human-Readable Output** (Default)

Provides formatted, color-coded output with icons:
- ✅ Healthy/OK
- ⚠️ Warning/Degraded
- ❌ Error/Unhealthy

**Example**:
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

Provides structured JSON output for automation and integration.

**Example**:
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
      },
      "timestamp": "2025-12-06T00:30:00"
    },
    "agents": {
      "category": "agents",
      "total_agents": 8,
      "active_agents": 6,
      "agent_statuses": [
        {
          "agent_id": "Agent-7",
          "status": "ACTIVE_AGENT_MODE",
          "last_updated": "2025-12-06 00:25:00",
          "current_mission": "Loop 2 Completion - Wire remaining 13 files..."
        }
      ],
      "timestamp": "2025-12-06T00:30:00"
    }
  }
}
```

---

## 🔧 **USAGE EXAMPLES**

### **Daily Monitoring**

```bash
# Full system check
python tools/unified_monitor.py --category all
```

### **Agent Health Check**

```bash
# Check all agent workspaces
python tools/unified_monitor.py --category workspace

# Check specific agent
python tools/unified_monitor.py --category workspace --agent Agent-7
```

### **Service Monitoring**

```bash
# Check Discord service
python tools/unified_monitor.py --category service --service discord

# Check GitHub pusher
python tools/unified_monitor.py --category service --service github_pusher
```

### **Automation Integration**

```bash
# JSON output for scripts
python tools/unified_monitor.py --category all --json > monitoring_results.json
```

### **Resume Stalled Agents**

```bash
# Resume all agents
python tools/unified_monitor.py --category resume

# Resume specific agent
python tools/unified_monitor.py --category resume --agent Agent-7

# Force immediate resume
python tools/unified_monitor.py --category resume --agent Agent-7 --force
```

---

## 🎯 **BEST PRACTICES**

### **1. Regular Monitoring**

Schedule regular full monitoring checks:
```bash
# Daily full check
python tools/unified_monitor.py --category all
```

### **2. Focused Checks**

Use specific categories for targeted monitoring:
```bash
# Queue monitoring
python tools/unified_monitor.py --category queue

# Workspace health
python tools/unified_monitor.py --category workspace
```

### **3. Automation**

Use JSON output for automation and alerting:
```bash
python tools/unified_monitor.py --category all --json | jq '.checks.queue.status'
```

### **4. Agent-Specific Monitoring**

Monitor specific agents when investigating issues:
```bash
python tools/unified_monitor.py --category workspace --agent Agent-7
```

---

## 🚨 **TROUBLESHOOTING**

### **Issue: Service Not Found**

**Problem**: Service health check returns `STOPPED` or `UNKNOWN`

**Solutions**:
- Verify service name matches process command line
- Check if `psutil` is installed: `pip install psutil`
- Verify service is actually running

### **Issue: Workspace Health Low Score**

**Problem**: Workspace health score < 60

**Solutions**:
- Check for old messages (>7 days) in inbox
- Archive old messages
- Update status.json files
- Process unprocessed messages

### **Issue: JSON Parse Error**

**Problem**: JSON output cannot be parsed

**Solutions**:
- Check for Python errors in output
- Verify JSON structure matches expected format
- Use `--category all` to get complete structure

---

## 📚 **REFERENCES**

- **Migration Guide**: `tools/MIGRATION_GUIDE_DEPRECATED_MONITORING_TOOLS.md`
- **Capabilities**: `tools/UNIFIED_MONITORING_CAPABILITIES.md`
- **Source Code**: `tools/unified_monitor.py`

---

**Status**: ✅ **USER GUIDE COMPLETE**  
**Version**: Phase 2 Complete

🐝 **WE. ARE. SWARM. ⚡🔥🚀**

