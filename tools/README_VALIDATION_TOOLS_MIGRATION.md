# Validation Tools Migration Guide

**Date**: 2025-12-06  
**Status**: ✅ Migration Guide Created

---

## 📋 **QUICK REFERENCE**

### **Deprecated Tools → Unified Tool**

| Deprecated Tool | Unified Command |
|----------------|-----------------|
| `file_refactor_detector.py` | `unified_validator.py --category refactor` |
| `session_transition_helper.py` | `unified_validator.py --category session` |
| `tracker_status_validator.py` | `unified_validator.py --category tracker` |

---

## 🚀 **MIGRATION EXAMPLES**

### **1. File Refactor Detection**

**Old**:
```bash
python tools/file_refactor_detector.py src/core/shared_utilities.py
```

**New**:
```bash
python tools/unified_validator.py --category refactor --file src/core/shared_utilities.py
```

### **2. Session Transition Validation**

**Old**:
```bash
python tools/session_transition_helper.py --agent Agent-8
```

**New**:
```bash
python tools/unified_validator.py --category session --agent Agent-8
```

### **3. Tracker Status Validation**

**Old**:
```bash
python tools/tracker_status_validator.py
```

**New**:
```bash
python tools/unified_validator.py --category tracker
```

---

## 📚 **FULL DOCUMENTATION**

See [MIGRATION_GUIDE_DEPRECATED_VALIDATION_TOOLS.md](./MIGRATION_GUIDE_DEPRECATED_VALIDATION_TOOLS.md) for complete migration documentation.

---

**Reference**: `agent_workspaces/Agent-8/TOOLS_CONSOLIDATION_BATCH2_3_COMPLETE.md`

🐝 **WE. ARE. SWARM. ⚡🔥🚀**


