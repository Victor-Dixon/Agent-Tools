# 🏥 Workspace Health Monitor

**Author**: Agent-6 (Coordination & Communication Specialist)  
**Created**: 2025-11-22  
**V2 Compliant**: Yes (398 lines)  
**Category**: Workspace Management, Coordination

---

## 📋 **OVERVIEW**

Monitor agent workspace health by checking inbox status, old messages, status file currency, and generating health scores and recommendations.

---

## 🎯 **FEATURES**

- **Inbox Health**: Count active messages and identify old messages (>7 days)
- **Archive Status**: Track archived messages
- **Status File Check**: Verify status.json exists and is current
- **Health Scoring**: Calculate workspace health score (0-100)
- **Recommendations**: Generate actionable health recommendations
- **Multi-Agent Support**: Check individual agent or all agents

---

## 🚀 **USAGE**

### **Check Single Agent**:
```bash
python tools/workspace_health_monitor.py --agent Agent-6
```

### **Check All Agents**:
```bash
python tools/workspace_health_monitor.py --all
```

### **Verbose Output**:
```bash
python tools/workspace_health_monitor.py --agent Agent-6 --verbose
```

### **JSON Output**:
```bash
python tools/workspace_health_monitor.py --agent Agent-6 --json
```

---

## 📊 **HEALTH SCORE CALCULATION**

**Score Components** (100 points total):
- **Base Score**: 100 points
- **Old Messages Penalty**: -5 points per old message (max -30)
- **High Inbox Penalty**: -2 points per message over 10 (max -20)
- **Missing Status File**: -20 points
- **Outdated Status File**: -10 points

**Score Ranges**:
- **80-100**: ✅ Excellent health
- **60-79**: ⚠️  Needs attention
- **0-59**: ❌ Poor health

---

## 💡 **RECOMMENDATIONS**

The tool generates recommendations based on:
- Old messages (>7 days) in inbox
- High inbox message count (>10)
- Missing or outdated status.json files
- Overall workspace organization

---

## 📝 **OUTPUT EXAMPLE**

```
============================================================
📊 Workspace Health: Agent-6
============================================================
Health Score: 85.0/100

📬 Inbox: 2 messages (0 old)
📦 Archive: 62 messages
📝 Devlogs: 29 files
📋 Reports: 85 files

📄 Status File: ✅ Current

💡 Recommendations:
   • Workspace health: Excellent ✅
```

---

## 🔧 **INTEGRATION**

### **Cycle Planner Integration**:
Add to cycle planner for regular workspace health checks:
```markdown
### **Workspace Health Check** (Agent-X)
- **Priority**: P3 (Low)
- **Frequency**: Weekly
- **Command**: `python tools/workspace_health_monitor.py --all`
```

### **Automation**:
Run in cron/scheduler for automated monitoring:
```bash
# Weekly workspace health check
0 9 * * 1 python tools/workspace_health_monitor.py --all --json > workspace_health_$(date +\%Y\%m\%d).json
```

---

## 🎯 **USE CASES**

1. **Regular Health Checks**: Monitor workspace cleanliness
2. **Pre-Cleanup Assessment**: Identify workspaces needing cleanup
3. **Onboarding Validation**: Verify new agent workspace setup
4. **Swarm-Wide Monitoring**: Track overall workspace health

---

## 📚 **RELATED TOOLS**

- `archive_old_inbox_messages.py`: Archive old messages
- `auto_workspace_cleanup.py`: Automated cleanup
- `agent_status_quick_check.py`: Status file checking

---

## ⚙️ **CONFIGURATION**

**Command-Line Options**:
- `--agent, -a`: Check specific agent workspace
- `--all, -A`: Check all agent workspaces
- `--verbose, -v`: Show detailed information
- `--json, -j`: Output as JSON
- `--workspace-root`: Root directory for agent workspaces (default: `agent_workspaces`)

---

## 🔍 **TECHNICAL DETAILS**

**V2 Compliance**: ✅
- Lines of Code: 398
- Functions: Well-structured, single responsibility
- Type Hints: Yes
- Error Handling: Comprehensive

**Dependencies**:
- `pathlib`: Path operations
- `datetime`: Date/time calculations
- `argparse`: CLI interface
- `dataclasses`: Data structures
- `json`: JSON output

---

**Tool Status**: ✅ **READY FOR USE**

**Maintainer**: Agent-6 (Coordination & Communication Specialist)



