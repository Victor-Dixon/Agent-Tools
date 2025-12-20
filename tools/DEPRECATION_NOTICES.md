# Deprecation Notices for Archived Tools

**Date**: 2025-12-06  
**Author**: Agent-7 (Web Development Specialist)  
**Status**: ✅ **DEPRECATION NOTICES CREATED**  
**Support**: Agent-3 (Infrastructure & DevOps Specialist) - Archiving Work

---

## 📋 **OVERVIEW**

This document provides deprecation notices for tools that have been archived or are scheduled for archiving. These notices should be included in tool files and referenced in migration guides.

**Archive Location**: `tools/deprecated/`  
**Migration Guides**: See respective migration documentation

---

## 🚨 **DEPRECATION NOTICES**

### **1. aria_active_response.py** ✅ ARCHIVED

**Status**: Archived  
**Location**: `tools/deprecated/aria_active_response.py`  
**Archive Date**: Unknown (pre-2025-12-05)

**Deprecation Notice**:
```
⚠️ DEPRECATED: This tool has been archived.
Location: tools/deprecated/aria_active_response.py
Functionality has been consolidated into unified systems.
Please use appropriate unified tool for active response functionality.
```

---

### **2. captain_check_agent_status.py** ✅ ARCHIVED

**Status**: Archived (Consolidated 2025-12-05)  
**Location**: `tools/deprecated/consolidated_2025-12-05/captain_check_agent_status.py`  
**Archive Date**: 2025-12-05

**Deprecation Notice**:
```
⚠️ DEPRECATED: This tool has been consolidated into unified_monitor.py
Use: python tools/unified_monitor.py --category agents

Location: tools/deprecated/consolidated_2025-12-05/captain_check_agent_status.py
Migration Guide: tools/MIGRATION_GUIDE_DEPRECATED_MONITORING_TOOLS.md
```

**Replacement**:
```bash
# Old
python tools/captain_check_agent_status.py

# New
python tools/unified_monitor.py --category agents
```

---

### **3. file_refactor_detector.py** ⚠️ DEPRECATED (Archive Pending)

**Status**: Deprecated, archive pending  
**Location**: `tools/file_refactor_detector.py`  
**Replacement**: `unified_validator.py --category refactor`

**Deprecation Notice**:
```
⚠️ DEPRECATED: This tool has been consolidated into unified_validator.py
Use: python tools/unified_validator.py --category refactor --file <path>

Migration Guide: tools/MIGRATION_GUIDE_DEPRECATED_VALIDATION_TOOLS.md
This tool will be archived after migration period.
```

**Replacement**:
```bash
# Old
python tools/file_refactor_detector.py src/core/shared_utilities.py

# New
python tools/unified_validator.py --category refactor --file src/core/shared_utilities.py
```

---

### **4. session_transition_helper.py** ⚠️ DEPRECATED (Archive Pending)

**Status**: Deprecated, archive pending  
**Location**: `tools/session_transition_helper.py`  
**Replacement**: `unified_validator.py --category session`

**Deprecation Notice**:
```
⚠️ DEPRECATED: This tool has been consolidated into unified_validator.py
Use: python tools/unified_validator.py --category session --agent <agent_id>

Migration Guide: tools/MIGRATION_GUIDE_DEPRECATED_VALIDATION_TOOLS.md
This tool will be archived after migration period.
```

**Replacement**:
```bash
# Old
python tools/session_transition_helper.py --agent Agent-8

# New
python tools/unified_validator.py --category session --agent Agent-8
```

---

### **5. tracker_status_validator.py** ⚠️ DEPRECATED (Archive Pending)

**Status**: Deprecated, archive pending  
**Location**: `tools/tracker_status_validator.py`  
**Replacement**: `unified_validator.py --category tracker`

**Deprecation Notice**:
```
⚠️ DEPRECATED: This tool has been consolidated into unified_validator.py
Use: python tools/unified_validator.py --category tracker

Migration Guide: tools/MIGRATION_GUIDE_DEPRECATED_VALIDATION_TOOLS.md
This tool will be archived after migration period.
```

**Replacement**:
```bash
# Old
python tools/tracker_status_validator.py

# New
python tools/unified_validator.py --category tracker
```

---

### **6. workspace_health_monitor.py** ⚠️ DEPRECATED (Archive Pending - Phase 2)

**Status**: Deprecated, archive pending (Phase 2 consolidation)  
**Location**: `tools/workspace_health_monitor.py`  
**Replacement**: `unified_monitor.py --category workspace`

**Deprecation Notice**:
```
⚠️ DEPRECATED: This tool has been consolidated into unified_monitor.py
Use: python tools/unified_monitor.py --category workspace

Location: Will be moved to tools/deprecated/ after Phase 2 completion
Migration Guide: tools/MIGRATION_GUIDE_DEPRECATED_MONITORING_TOOLS.md
```

**Replacement**:
```bash
# Old
python tools/workspace_health_monitor.py

# New
python tools/unified_monitor.py --category workspace
```

---

## 📚 **DEPRECATION NOTICE TEMPLATE**

For future deprecated tools, use this template:

```python
"""
⚠️ DEPRECATED: This tool has been consolidated into [REPLACEMENT_TOOL]
Use: python tools/[REPLACEMENT_TOOL] [REPLACEMENT_FLAGS]

Location: tools/[CURRENT_LOCATION] (will be moved to tools/deprecated/)
Migration Guide: tools/[MIGRATION_GUIDE_PATH]
[ADDITIONAL_CONTEXT]
"""
```

---

## 🔄 **ARCHIVING WORKFLOW**

### **Step 1: Add Deprecation Notice**
- Add deprecation notice to tool file header
- Update tool to print deprecation warning when executed
- Document replacement tool and migration path

### **Step 2: Create Migration Guide**
- Document old usage patterns
- Document new usage patterns
- Provide migration examples
- List what changed (functionality, CLI, output)

### **Step 3: Archive Tool**
- Move tool to `tools/deprecated/`
- Optionally create date-based subdirectory
- Update this deprecation notices document
- Update archived tools migration guide

### **Step 4: Update Registry**
- Remove from toolbelt registry if registered
- Update documentation references
- Update CI/CD pipelines if needed

---

## 📊 **ARCHIVE STATUS SUMMARY**

### **Fully Archived** (3 tools):
1. ✅ `aria_active_response.py` - Archived
2. ✅ `test_chat_presence_import.py` - Archived (if exists)
3. ✅ `captain_check_agent_status.py` - Archived (2025-12-05)

### **Deprecated - Archive Pending** (4 tools):
1. ⚠️ `file_refactor_detector.py` - Deprecated, archive pending
2. ⚠️ `session_transition_helper.py` - Deprecated, archive pending
3. ⚠️ `tracker_status_validator.py` - Deprecated, archive pending
4. ⚠️ `workspace_health_monitor.py` - Deprecated, archive pending (Phase 2)

---

## 🔗 **REFERENCES**

- **Archived Tools Guide**: `tools/ARCHIVED_TOOLS_MIGRATION_GUIDE.md`
- **Monitoring Migration**: `tools/MIGRATION_GUIDE_DEPRECATED_MONITORING_TOOLS.md`
- **Validation Migration**: `tools/MIGRATION_GUIDE_DEPRECATED_VALIDATION_TOOLS.md`
- **Archive Directory**: `tools/deprecated/`
- **Toolbelt Registry**: `tools/toolbelt_registry.py`

---

## ✅ **CHECKLIST FOR NEW DEPRECATIONS**

When deprecating a new tool:

- [ ] Add deprecation notice to tool file header
- [ ] Update tool to print warning when executed
- [ ] Create migration guide entry
- [ ] Update this deprecation notices document
- [ ] Update archived tools migration guide
- [ ] Notify dependent scripts/pipelines
- [ ] Set archive date (if known)
- [ ] Update toolbelt registry (if registered)

---

**Status**: ✅ **DEPRECATION NOTICES DOCUMENTED**  
**Support**: Agent-3's archiving work documented and supported

🐝 **WE. ARE. SWARM. ⚡🔥🚀**
