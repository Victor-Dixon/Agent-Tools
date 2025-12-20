# Archived Tools Migration Guide

**Date**: 2025-12-06  
**Author**: Agent-7 (Web Development Specialist)  
**Status**: ✅ **MIGRATION GUIDE COMPLETE**  
**Support**: Agent-3 (Infrastructure & DevOps Specialist) - Archiving Work

---

## 📋 **OVERVIEW**

This guide documents tools that have been archived (moved to `tools/deprecated/`) and provides migration paths to their replacements. Archiving is a final step after deprecation when tools are no longer needed.

**Archive Location**: `tools/deprecated/`  
**Support**: See migration guides for replacement tools

---

## 🔄 **ARCHIVED TOOLS**

### **Phase 1: Consolidated Tools** (2025-12-05)

#### **1. `aria_active_response.py`** ✅ ARCHIVED

**Status**: Archived to `tools/deprecated/`  
**Reason**: Functionality consolidated into unified systems  
**Migration**: Use appropriate unified tool for active response functionality

**Location**: `tools/deprecated/aria_active_response.py`

---

#### **2. `test_chat_presence_import.py`** ✅ ARCHIVED

**Status**: Archived to `tools/deprecated/`  
**Reason**: Test utility no longer needed  
**Migration**: Use standard testing frameworks for chat presence testing

**Location**: `tools/deprecated/test_chat_presence_import.py`

---

#### **3. `captain_check_agent_status.py`** ✅ ARCHIVED (Consolidated 2025-12-05)

**Status**: Archived to `tools/deprecated/consolidated_2025-12-05/`  
**Reason**: Consolidated into `unified_monitor.py`  
**Replacement**: `unified_monitor.py --category agents`

**Migration Path**:
```bash
# Old
python tools/captain_check_agent_status.py

# New
python tools/unified_monitor.py --category agents
```

**Location**: `tools/deprecated/consolidated_2025-12-05/captain_check_agent_status.py`  
**Reference**: See `tools/MIGRATION_GUIDE_DEPRECATED_MONITORING_TOOLS.md`

---

### **Phase 2: Deprecated Tools** (Awaiting Archive)

These tools have deprecation notices and are scheduled for archiving after migration period:

#### **1. `file_refactor_detector.py`** ⚠️ DEPRECATED (Archive Pending)

**Status**: Deprecated, archive pending  
**Replacement**: `unified_validator.py --category refactor`  
**Migration**: See `tools/MIGRATION_GUIDE_DEPRECATED_VALIDATION_TOOLS.md`

**Location**: `tools/file_refactor_detector.py` (will be moved to `tools/deprecated/`)

---

#### **2. `session_transition_helper.py`** ⚠️ DEPRECATED (Archive Pending)

**Status**: Deprecated, archive pending  
**Replacement**: `unified_validator.py --category session`  
**Migration**: See `tools/MIGRATION_GUIDE_DEPRECATED_VALIDATION_TOOLS.md`

**Location**: `tools/session_transition_helper.py` (will be moved to `tools/deprecated/`)

---

#### **3. `tracker_status_validator.py`** ⚠️ DEPRECATED (Archive Pending)

**Status**: Deprecated, archive pending  
**Replacement**: `unified_validator.py --category tracker`  
**Migration**: See `tools/MIGRATION_GUIDE_DEPRECATED_VALIDATION_TOOLS.md`

**Location**: `tools/tracker_status_validator.py` (will be moved to `tools/deprecated/`)

---

## 📚 **MIGRATION GUIDES**

### **For Monitoring Tools**:
- **Guide**: `tools/MIGRATION_GUIDE_DEPRECATED_MONITORING_TOOLS.md`
- **Archived Tools**: `captain_check_agent_status.py`
- **Replacement**: `unified_monitor.py`

### **For Validation Tools**:
- **Guide**: `tools/MIGRATION_GUIDE_DEPRECATED_VALIDATION_TOOLS.md`
- **Deprecated Tools**: `file_refactor_detector.py`, `session_transition_helper.py`, `tracker_status_validator.py`
- **Replacement**: `unified_validator.py`

---

## 🔍 **ARCHIVE DIRECTORY STRUCTURE**

```
tools/deprecated/
├── aria_active_response.py                          # Phase 1 archived
├── test_chat_presence_import.py                     # Phase 1 archived
└── consolidated_2025-12-05/
    └── captain_check_agent_status.py                # Phase 2 consolidated
```

---

## ✅ **ARCHIVING CHECKLIST**

When archiving a tool:

- [ ] Add deprecation notice to tool file
- [ ] Update migration guide with archive information
- [ ] Move tool to `tools/deprecated/` directory
- [ ] Update toolbelt registry (remove from active tools)
- [ ] Update documentation index
- [ ] Notify dependent scripts/pipelines
- [ ] Create archive date directory if grouping by date

---

## 📊 **ARCHIVE STATUS**

### **Fully Archived** (3 tools):
1. ✅ `aria_active_response.py`
2. ✅ `test_chat_presence_import.py`
3. ✅ `captain_check_agent_status.py` (2025-12-05)

### **Deprecated - Archive Pending** (3 tools):
1. ⚠️ `file_refactor_detector.py`
2. ⚠️ `session_transition_helper.py`
3. ⚠️ `tracker_status_validator.py`

---

## 🎯 **BEST PRACTICES**

### **Before Archiving**:
1. Ensure migration path exists
2. Update all documentation
3. Notify users/agents
4. Provide migration window

### **During Archiving**:
1. Move to `tools/deprecated/`
2. Add archive date directory if grouping
3. Keep deprecation notice in file
4. Update toolbelt registry

### **After Archiving**:
1. Monitor for any breakages
2. Update CI/CD pipelines
3. Update automation scripts
4. Document in migration guides

---

## 📚 **REFERENCES**

- **Monitoring Migration**: `tools/MIGRATION_GUIDE_DEPRECATED_MONITORING_TOOLS.md`
- **Validation Migration**: `tools/MIGRATION_GUIDE_DEPRECATED_VALIDATION_TOOLS.md`
- **Toolbelt Registry**: `tools/toolbelt_registry.py`
- **Archive Directory**: `tools/deprecated/`

---

## 🔗 **SUPPORT**

For questions about archived tools:
- **Monitoring Tools**: See `tools/UNIFIED_MONITORING_USER_GUIDE.md`
- **Validation Tools**: See `tools/MIGRATION_GUIDE_DEPRECATED_VALIDATION_TOOLS.md`
- **Archiving Process**: Contact Agent-3 (Infrastructure & DevOps Specialist)

---

**Status**: ✅ **ARCHIVED TOOLS DOCUMENTED**  
**Support**: Agent-3's archiving work documented and supported

🐝 **WE. ARE. SWARM. ⚡🔥🚀**


