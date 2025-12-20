# Integration Health Checker - Usage Guide

**Tool**: `tools/integration_health_checker.py`  
**Author**: Agent-2 (Architecture & Design Specialist)  
**Date**: 2025-11-26  
**V2 Compliance**: ✅ <400 lines

---

## 🎯 **PURPOSE**

Quick health check for integration work readiness:
- Verifies tool availability
- Checks documentation availability
- Validates repository state (optional)
- Reports overall integration health

---

## 🚀 **USAGE**

### **Basic Usage** (Check tools and docs):
```bash
python tools/integration_health_checker.py
```

### **With Repository Check**:
```bash
python tools/integration_health_checker.py <repo_path>
```

### **Example**:
```bash
python tools/integration_health_checker.py src/discord_commander
```

---

## 📊 **OUTPUT**

### **Console Output**:
- Tool availability count
- Documentation availability count
- Repository state (if provided)
- Report file location

### **Report File**: `integration_health_report.md`
- Tools availability (✅/❌)
- Documentation availability (✅/❌)
- Repository state (if checked)
- Overall health percentage
- Health status (🟢🟡🟠🔴)

---

## ✅ **CHECKS PERFORMED**

### **Tools** (5 tools):
- `detect_venv_files.py`
- `enhanced_duplicate_detector.py`
- `pattern_analyzer.py`
- `check_integration_issues.py`
- `verify_integration_tools.py`

### **Documentation** (5 key docs):
- `INTEGRATION_QUICK_START.md`
- `STAGE1_INTEGRATION_METHODOLOGY.md`
- `INTEGRATION_BEST_PRACTICES.md`
- `INTEGRATION_PATTERNS_CATALOG.md`
- `TOOL_USAGE_GUIDE.md`

### **Repository State** (if path provided):
- Exists
- Is git repo
- Has Python files
- Has test files
- Has venv files (warning)

---

## 🎯 **HEALTH STATUS**

- **🟢 Excellent** (≥90%): Ready for integration work
- **🟡 Good** (≥70%): Minor gaps, ready for integration
- **🟠 Fair** (≥50%): Some gaps, review needed
- **🔴 Poor** (<50%): Significant gaps, setup needed

---

## 💡 **USE CASES**

1. **Pre-Integration Check**: Verify readiness before starting integration
2. **Tool Verification**: Ensure all tools are available
3. **Documentation Check**: Verify key docs are present
4. **Repository Assessment**: Quick check of repository state
5. **Health Monitoring**: Track integration readiness over time

---

**Status**: ✅ **READY FOR USE**  
**Swarm Value**: Quick health check for integration readiness




