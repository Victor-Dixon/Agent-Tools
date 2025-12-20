# Unified Monitoring Tool - Capabilities Documentation

**Date**: 2025-12-06  
**Author**: Agent-7 (Web Development Specialist)  
**Version**: Phase 2 Complete  
**Status**: ✅ **CAPABILITIES DOCUMENTED**

---

## 📋 **OVERVIEW**

`unified_monitor.py` consolidates 33+ monitoring tools into a single unified system. This document details all monitoring capabilities, methods, and features.

---

## 🏗️ **ARCHITECTURE**

### **Class: UnifiedMonitor**

**Location**: `tools/unified_monitor.py`

**Initialization**:
```python
from tools.unified_monitor import UnifiedMonitor
monitor = UnifiedMonitor()
```

---

## 📊 **MONITORING CAPABILITIES**

### **1. Queue Health Monitoring**

**Method**: `monitor_queue_health()`

**Capabilities**:
- Monitors deferred push queue statistics
- Calculates health score (0-100)
- Reports queue status (HEALTHY, DEGRADED, UNHEALTHY)
- Tracks pending, failed, and total entries

**Output Structure**:
```python
{
    "category": "queue",
    "status": "HEALTHY" | "DEGRADED" | "UNHEALTHY" | "ERROR",
    "score": 0-100,
    "stats": {
        "total": int,
        "pending": int,
        "failed": int
    },
    "timestamp": "ISO8601"
}
```

**Health Score Calculation**:
- 100 if queue is empty
- 100 - failure_rate if entries exist
- Failure rate = (failed / total) * 100

**Status Thresholds**:
- HEALTHY: score >= 80
- DEGRADED: 50 <= score < 80
- UNHEALTHY: score < 50

---

### **2. Message Queue File Monitoring**

**Method**: `check_message_queue_file()`

**Capabilities**:
- Checks file existence
- Validates file readability
- Validates file writability
- Validates JSON format
- Reports file size and last modified time

**Output Structure**:
```python
{
    "category": "message_queue_file",
    "exists": bool,
    "readable": bool,
    "writable": bool,
    "size": int,
    "last_modified": str,
    "valid_json": bool,
    "status": "HEALTHY" | "MISSING" | "INVALID_JSON" | "NOT_READABLE" | "NOT_WRITABLE" | "ERROR",
    "timestamp": "ISO8601"
}
```

**File Location**: `message_queue/queue.json`

---

### **3. Service Health Monitoring**

**Method**: `monitor_service_health(service_name: str)`

**Capabilities**:
- Checks if service process is running
- Searches process command lines for service name
- Reports service status (RUNNING, STOPPED, UNKNOWN)
- Requires `psutil` package

**Output Structure**:
```python
{
    "category": "service",
    "service": str,
    "status": "RUNNING" | "STOPPED" | "UNKNOWN" | "ERROR",
    "running": bool,
    "timestamp": "ISO8601"
}
```

**Supported Services**:
- `github_pusher`
- `discord`
- `ci_cd`
- Any service name (searches process command line)

**Dependencies**: `psutil` package

---

### **4. Disk Usage Monitoring**

**Method**: `monitor_disk_usage(paths: List[str] = None)`

**Capabilities**:
- Monitors disk usage for specified paths
- Defaults to C:/ and D:/ if no paths specified
- Calculates total, free, and used space
- Reports usage percentage and status

**Output Structure**:
```python
{
    "category": "disk",
    "disks": [
        {
            "path": str,
            "total_gb": float,
            "free_gb": float,
            "used_percent": float,
            "status": "OK" | "WARNING" | "CRITICAL" | "ERROR"
        }
    ],
    "timestamp": "ISO8601"
}
```

**Status Thresholds**:
- OK: < 90% used
- WARNING: 90-95% used
- CRITICAL: > 95% used

---

### **5. Agent Status Monitoring**

**Method**: `monitor_agent_status()`

**Capabilities**:
- Reads all agent `status.json` files
- Reports agent status, last updated, current mission
- Counts active vs total agents
- Handles missing/invalid status files gracefully

**Output Structure**:
```python
{
    "category": "agents",
    "total_agents": int,
    "active_agents": int,
    "agent_statuses": [
        {
            "agent_id": str,
            "status": str,
            "last_updated": str,
            "current_mission": str  # First 100 chars
        }
    ],
    "timestamp": "ISO8601"
}
```

**Workspace Location**: `agent_workspaces/<agent_id>/status.json`

---

### **6. Workspace Health Monitoring** (Phase 2 - Consolidated from workspace_health_monitor.py)

**Method**: `monitor_workspace_health(agent_id: Optional[str] = None)`

**Consolidation**: Migrated from `workspace_health_monitor.py` in Phase 2 (Agent-1)

**Capabilities**:
- Monitors inbox organization (total, unprocessed, old messages)
- Tracks archive, devlogs, reports counts
- Checks status file existence and currency (<24 hours = current)
- Validates status consistency
- Calculates health score (0-100) with detailed metrics
- Provides actionable recommendations for improvements
- Old message detection (>7 days cutoff)
- Unprocessed message tracking
- Workspace organization metrics

**Output Structure** (Single Agent):
```python
{
    "category": "workspace",
    "agent_id": str,
    "inbox_count": int,
    "unprocessed_count": int,
    "old_messages": int,
    "archive_count": int,
    "devlogs_count": int,
    "reports_count": int,
    "status_file_exists": bool,
    "status_file_current": bool,
    "status_consistency": str,
    "issues_found": int,
    "health_score": float,  # 0-100
    "recommendations": [str],
    "timestamp": "ISO8601"
}
```

**Output Structure** (All Agents):
```python
{
    "category": "workspace",
    "workspaces_checked": int,
    "average_health_score": float,
    "workspaces": [
        {
            "agent_id": str,
            "health_score": float,
            "issues_found": int,
            ...
        }
    ],
    "timestamp": "ISO8601"
}
```

**Health Score Factors**:
- Inbox organization (unprocessed messages penalty)
- Old messages penalty (>7 days)
- Status file currency (<24 hours = current)
- Status consistency
- File organization

**Cutoff Date**: Messages older than 7 days are considered "old"

---

### **7. Test Coverage Monitoring**

**Method**: `monitor_test_coverage()`

**Capabilities**:
- Counts total test files
- Tracks test file locations
- Provides coverage statistics

**Output Structure**:
```python
{
    "category": "coverage",
    "total_test_files": int,
    "test_files": [str],  # File paths
    "timestamp": "ISO8601"
}
```

---

### **8. Resume Trigger**

**Method**: `trigger_status_monitor_resume(agent_id: Optional[str] = None, force: bool = False)`

**Capabilities**:
- Triggers status monitor resume for agents
- Supports single agent or all agents
- Force mode for immediate triggers
- Async execution with status reporting

**Output Structure**:
```python
{
    "category": "resume_trigger",
    "agent_id": str | None,
    "status": "SUCCESS" | "ERROR",
    "triggered": bool,
    "message": str,
    "timestamp": "ISO8601"
}
```

**Behavior**:
- Without `force`: Checks conditions before triggering
- With `force`: Triggers immediately without checks

---

### **9. Full Monitoring Suite**

**Method**: `run_full_monitoring()`

**Capabilities**:
- Runs all monitoring checks in sequence
- Returns consolidated results
- Includes: queue, message_queue_file, services, disk, agents, workspace, coverage

**Output Structure**:
```python
{
    "timestamp": "ISO8601",
    "checks": {
        "queue": {...},
        "message_queue_file": {...},
        "github_pusher": {...},
        "discord": {...},
        "disk": {...},
        "agents": {...},
        "workspace": {...},
        "coverage": {...}
    }
}
```

---

## 🎨 **REPORTING**

### **Formatted Report**

**Method**: `print_monitoring_report(results: Dict[str, Any])`

**Capabilities**:
- Formats monitoring results for human-readable output
- Uses icons for status indication:
  - ✅ Healthy/OK
  - ⚠️ Warning/Degraded
  - ❌ Error/Unhealthy
- Groups related information
- Provides summary statistics

---

## 🔧 **CLI INTERFACE**

### **Command Structure**

```bash
python tools/unified_monitor.py [OPTIONS]
```

### **Options**

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--category` | `-c` | Yes | Monitoring category |
| `--service` | | Conditional | Service name (for service category) |
| `--agent` | | Optional | Agent ID (for workspace/resume categories) |
| `--force` | | Optional | Force immediate action (for resume) |
| `--json` | | Optional | Output in JSON format |
| `--help` | `-h` | Optional | Show help |

### **Categories**

- `queue` - Queue health monitoring
- `message_queue_file` - Message queue file status
- `service` - Service health (requires `--service`)
- `disk` - Disk usage monitoring
- `agents` - Agent status monitoring
- `workspace` - Workspace health (optional `--agent`)
- `coverage` - Test coverage monitoring
- `resume` - Resume trigger (optional `--agent`, optional `--force`)
- `all` - Run all monitoring checks

---

## 🔄 **CONSOLIDATED TOOLS**

The following tools have been consolidated into `unified_monitor.py`:

1. ✅ `discord_bot_infrastructure_check.py` → `check_message_queue_file()`
2. ✅ `manually_trigger_status_monitor_resume.py` → `trigger_status_monitor_resume()`
3. ✅ `workspace_health_monitor.py` → `monitor_workspace_health()` (Phase 2)
4. ✅ `captain_check_agent_status.py` → `monitor_agent_status()` (Phase 2)

**Total Consolidated**: 33+ monitoring tools → 1 unified tool

---

## 📈 **PERFORMANCE**

- **Execution Time**: < 5 seconds for full monitoring suite
- **Memory Usage**: Minimal (process-based service checks)
- **Dependencies**: `psutil` (optional, for service monitoring)

---

## 🔒 **ERROR HANDLING**

All methods include comprehensive error handling:
- Try-catch blocks for all operations
- Graceful degradation on missing dependencies
- Error status reporting in output
- Detailed error messages in logs

---

## 📚 **REFERENCES**

- **Migration Guide**: `tools/MIGRATION_GUIDE_DEPRECATED_MONITORING_TOOLS.md`
- **User Guide**: `tools/UNIFIED_MONITORING_USER_GUIDE.md`
- **Source Code**: `tools/unified_monitor.py`

---

**Status**: ✅ **CAPABILITIES DOCUMENTED**  
**Version**: Phase 2 Complete

🐝 **WE. ARE. SWARM. ⚡🔥🚀**

