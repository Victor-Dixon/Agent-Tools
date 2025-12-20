# Migration Guide - Deprecated Validation Tools

**Date**: 2025-12-06  
**Author**: Agent-7 (Web Development Specialist)  
**Status**: ✅ Migration Guides Created

---

## 📋 **OVERVIEW**

This guide documents the migration from deprecated validation tools to `unified_validator.py`.

**Deprecated Tools**:
- `file_refactor_detector.py` → Use `unified_validator.py --category refactor`
- `session_transition_helper.py` → Use `unified_validator.py --category session`
- `tracker_status_validator.py` → Use `unified_validator.py --category tracker`

**Target Tool**: `tools/unified_validator.py`

---

## 🚀 **MIGRATION PATHS**

### **1. file_refactor_detector.py → unified_validator.py**

#### **Old Usage**:
```bash
python tools/file_refactor_detector.py src/core/shared_utilities.py
python tools/file_refactor_detector.py --scan src/services/
python tools/file_refactor_detector.py --check-author "Agent-1"
```

#### **New Usage**:
```bash
# Single file check
python tools/unified_validator.py --category refactor --file src/core/shared_utilities.py

# Directory scan
python tools/unified_validator.py --category refactor --dir src/services/

# Check specific author
python tools/unified_validator.py --category refactor --file <path> --author "Agent-1"
```

#### **What Changed**:
- **Method**: `RefactorDetector.detect()` → `UnifiedValidator.validate_refactor_status()`
- **CLI**: Same functionality, unified command structure
- **Output**: JSON format with validation results

#### **Migration Steps**:
1. Replace `file_refactor_detector.py` calls with `unified_validator.py --category refactor`
2. Update `--scan` flag to `--dir` flag
3. Use `--author` flag for author filtering
4. Update scripts/tooling that call this tool

---

### **2. session_transition_helper.py → unified_validator.py**

#### **Old Usage**:
```bash
python tools/session_transition_helper.py --agent Agent-8
python tools/session_transition_helper.py --agent Agent-8 --devlog-only
python tools/session_transition_helper.py --agent Agent-8 --checklist
```

#### **New Usage**:
```bash
# Full session transition validation
python tools/unified_validator.py --category session --agent Agent-8

# Devlog-only validation
python tools/unified_validator.py --category session --agent Agent-8 --devlog-only

# Checklist validation
python tools/unified_validator.py --category session --agent Agent-8 --checklist
```

#### **What Changed**:
- **Method**: `SessionTransitionHelper.validate()` → `UnifiedValidator.validate_session_transition()`
- **CLI**: Same flags maintained (`--agent`, `--devlog-only`, `--checklist`)
- **Output**: Enhanced JSON format with detailed validation results

#### **Migration Steps**:
1. Replace `session_transition_helper.py` calls with `unified_validator.py --category session`
2. Flags remain the same: `--agent`, `--devlog-only`, `--checklist`
3. Update any automation scripts that use this tool

---

### **3. tracker_status_validator.py → unified_validator.py**

#### **Old Usage**:
```bash
python tools/tracker_status_validator.py
```

#### **New Usage**:
```bash
# Tracker validation
python tools/unified_validator.py --category tracker
```

#### **What Changed**:
- **Method**: `TrackerValidator.validate()` → `UnifiedValidator.validate_tracker_status()`
- **CLI**: Simplified to single command
- **Output**: JSON format with validation results

#### **Migration Steps**:
1. Replace `tracker_status_validator.py` calls with `unified_validator.py --category tracker`
2. Update CI/CD pipelines that use this tool
3. Update documentation references

---

## 📊 **FULL VALIDATION SUITE**

### **All Validation Categories**:

```bash
# SSOT Config Validation
python tools/unified_validator.py --category ssot_config

# Import Validation
python tools/unified_validator.py --category imports --file <path>

# Code-Documentation Alignment
python tools/unified_validator.py --category alignment --file <path>

# Queue Behavior Validation
python tools/unified_validator.py --category queue

# Session Transition Validation
python tools/unified_validator.py --category session --agent <agent_id>

# Refactor Status Validation
python tools/unified_validator.py --category refactor --file <path>

# Tracker Status Validation
python tools/unified_validator.py --category tracker

# Consolidation Validation
python tools/unified_validator.py --category consolidation

# Run All Validations
python tools/unified_validator.py --all
```

---

## 🔧 **COMMAND-LINE REFERENCE**

### **Common Flags**:
- `--category <category>` - Validation category (required)
- `--file <path>` - Single file to validate
- `--dir <path>` - Directory to validate
- `--agent <agent_id>` - Agent ID (for session validation)
- `--all` - Run all validations
- `--json` - Output in JSON format
- `--verbose` - Verbose output

### **Category-Specific Flags**:
- `--author <author>` - Author filter (refactor category)
- `--devlog-only` - Devlog-only validation (session category)
- `--checklist` - Checklist validation (session category)

---

## ✅ **BENEFITS OF MIGRATION**

1. **Unified Interface**: Single tool for all validation needs
2. **Consistent Output**: JSON format across all validations
3. **Better Maintainability**: One tool to maintain instead of three
4. **Enhanced Features**: Additional validation categories available
5. **CLI Consistency**: Standardized command structure

---

## 📝 **EXAMPLES**

### **Example 1: Check if file was refactored**
```bash
# Old
python tools/file_refactor_detector.py src/core/shared_utilities.py

# New
python tools/unified_validator.py --category refactor --file src/core/shared_utilities.py
```

### **Example 2: Validate session transition**
```bash
# Old
python tools/session_transition_helper.py --agent Agent-7

# New
python tools/unified_validator.py --category session --agent Agent-7
```

### **Example 3: Validate tracker status**
```bash
# Old
python tools/tracker_status_validator.py

# New
python tools/unified_validator.py --category tracker
```

---

## 🔄 **AUTOMATION SCRIPTS**

If you have automation scripts using deprecated tools, update them:

```python
# Old
subprocess.run(["python", "tools/file_refactor_detector.py", file_path])

# New
subprocess.run(["python", "tools/unified_validator.py", "--category", "refactor", "--file", file_path])
```

---

## 📚 **ADDITIONAL RESOURCES**

- **Reference Document**: `agent_workspaces/Agent-8/TOOLS_CONSOLIDATION_BATCH2_3_COMPLETE.md`
- **Unified Validator**: `tools/unified_validator.py`
- **Toolbelt Registry**: `tools/toolbelt_registry.py`

---

## ⚠️ **DEPRECATION NOTICE**

The following tools are **DEPRECATED** and will be removed in a future release:
- `file_refactor_detector.py` - Migrate to `unified_validator.py --category refactor`
- `session_transition_helper.py` - Migrate to `unified_validator.py --category session`
- `tracker_status_validator.py` - Migrate to `unified_validator.py --category tracker`

Please migrate your workflows to use `unified_validator.py` as soon as possible.

---

## 📦 **ARCHIVING STATUS**

### **Deprecated - Archive Pending** (3 tools):
- ⚠️ `file_refactor_detector.py` - Deprecated, archive pending
- ⚠️ `session_transition_helper.py` - Deprecated, archive pending
- ⚠️ `tracker_status_validator.py` - Deprecated, archive pending

**Note**: These tools will be moved to `tools/deprecated/` after migration period. See `tools/ARCHIVED_TOOLS_MIGRATION_GUIDE.md` for complete archived tools documentation.

---

**Migration Status**: ✅ Guides Created  
**Next Steps**: Update automation scripts, CI/CD pipelines, and documentation references

🐝 **WE. ARE. SWARM. ⚡🔥🚀**


