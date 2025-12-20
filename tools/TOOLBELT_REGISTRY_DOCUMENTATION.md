# Toolbelt Registry Documentation

**Date**: 2025-12-06  
**Author**: Agent-7 (Web Development Specialist)  
**Status**: ✅ **TOOLBELT REGISTRY DOCUMENTATION COMPLETE**  
**Reference**: Agent-3's Tools Archiving Work

---

## 📋 **OVERVIEW**

This document provides comprehensive documentation for the toolbelt registry system, including active tools, archived tools, and deprecation status.

**Registry Location**: `tools/toolbelt_registry.py`  
**Documentation**: This file + `tools/README_TOOLBELT.md`

---

## 🎯 **REGISTRY PURPOSE**

The toolbelt registry (`tools/toolbelt_registry.py`) maps tool flags to tool modules, providing:

- **Unified CLI Access**: Single entry point for all tools
- **Flag Mapping**: Maps flags like `--scan`, `--v2-check` to tool modules
- **Tool Discovery**: Lists all available tools
- **Metadata Management**: Stores tool descriptions, flags, and configurations

---

## 📊 **ACTIVE TOOLS REGISTRY**

### **Registry Structure**

```python
TOOLS_REGISTRY = {
    "tool-id": {
        "name": "Tool Display Name",
        "module": "tools.module_name",
        "main_function": "main",
        "description": "Tool description",
        "flags": ["--flag", "-f"],
        "args_passthrough": True/False
    }
}
```

### **Tool Categories**

#### **Core Project Tools**:
- `scan` - Project Scanner
- `v2-check` - V2 Compliance Checker
- `dashboard` - Compliance Dashboard
- `complexity` - Complexity Analyzer
- `refactor` - Refactoring Suggestions
- `duplication` - Duplication Analyzer
- `functionality` - Functionality Verification
- `leaderboard` - Autonomous Leaderboard
- `history` - Compliance History

#### **QA & Validation Tools**:
- `unified-validator` - Unified Validator (consolidates 19+ validation tools)
- `line-count` - Quick Line Counter
- `ssot-validate` - SSOT Validator
- `extract-module` - Module Extractor
- `check-imports` - Import Chain Validator
- `refactor-analyze` - Refactor Analyzer
- `memory-scan` - Memory Leak Scanner
- `git-verify` - Git Commit Verifier
- `test-pyramid` - Test Pyramid Analyzer
- `v2-batch` - V2 Batch Checker
- `coverage-check` - Coverage Validator
- `qa-checklist` - QA Validation Checklist

#### **Analysis Tools**:
- `unified-analyzer` - Unified Analyzer (consolidates multiple analysis tools)
- `repo-batch` - Repository Analyzer
- `test-usage-analyzer` - Test Usage Analyzer

#### **Monitoring Tools**:
- `unified-monitor` - Unified Monitor (consolidates monitoring tools)

#### **Agent & Coordination Tools**:
- `agent-status` - Unified Agent Status Monitor
- `agent-orient` - Agent Orientation
- `agent-task-finder` - Agent Task Finder
- `captain-find-idle` - Find Idle Agents
- `captain-next-task` - Captain Next Task Picker
- `markov-optimize` - Markov Task Optimizer
- `message-history` - Agent Message History
- `verify-complete` - Work Completion Verifier

#### **Integration Tools**:
- `check-integration` - Integration Validator
- `analyze-duplicates` - Analyze Repository Duplicates
- `analyze-dreamvault` - Analyze DreamVault Duplicates
- `resolve-duplicates` - Resolve DreamVault Duplicates
- `review-integration` - Review DreamVault Integration
- `execute-cleanup` - Execute DreamVault Cleanup
- `merge-duplicates` - Merge Duplicate File Functionality
- `verify-cicd` - Verify Merged Repo CI/CD

#### **Consolidation Tools**:
- `repo-overlap` - Repo Overlap Analyzer
- `consolidation-exec` - Consolidation Executor
- `consolidation-status` - Consolidation Status Tracker
- `verify-phase1` - Verify Phase 1 Repos

#### **Discord Tools**:
- `discord-start` - Start Discord System
- `discord-verify` - Verify Discord Running

#### **Queue Tools**:
- `queue-start` - Start Message Queue Processor
- `queue-diagnose` - Diagnose Queue
- `queue-status` - Messaging Infrastructure Validator
- `fix-stuck` - Fix Stuck Message

#### **Workspace Tools**:
- `workspace-health` - Workspace Health Monitor (⚠️ Deprecated - use unified-monitor)
- `workspace-clean` - Workspace Auto-Cleaner

#### **Git Tools**:
- `git-work-verify` - Git Work Verifier

#### **Messaging Tools**:
- `message` - Send Message
- `get-task` - Get Next Task
- `list-tasks` - List Tasks

#### **Swarm Brain Tools**:
- `swarm-brain` - Swarm Brain Update/CLI
- `system-inventory` - Swarm System Inventory

#### **Masterpiece Tools**:
- `orchestrate` - Swarm Autonomous Orchestrator
- `mission-control` - Mission Control - Autonomous Mission Generator

#### **Architecture Tools**:
- `arch-review` - Architecture Review
- `pattern-validator` - Architecture Pattern Validator
- `pattern-extract` - Pattern Extractor
- `pattern-suggest` - Pattern Suggester

#### **Automation Tools**:
- `devlog-post` - Devlog Auto-Poster
- `auto-track` - Progress Auto-Tracker
- `extraction-roadmap` - Extraction Roadmap Generator
- `soft-onboard` - Soft Onboarding

#### **GitHub Tools**:
- `github-pr-debug` - GitHub PR Debugger
- `fix-github-prs` - Fix GitHub PR Issues

---

## 🚨 **ARCHIVED & DEPRECATED TOOLS**

### **Archived Tools** (Removed from Registry)

These tools have been archived and are no longer in the registry:

1. **`aria_active_response.py`** ✅ ARCHIVED
   - **Location**: `tools/deprecated/aria_active_response.py`
   - **Status**: Archived (functionality consolidated)

2. **`captain_check_agent_status.py`** ✅ ARCHIVED
   - **Location**: `tools/deprecated/consolidated_2025-12-05/captain_check_agent_status.py`
   - **Status**: Consolidated into `unified-monitor` (2025-12-05)
   - **Replacement**: `--unified-monitor --category agents`

### **Deprecated Tools** (Still in Registry, but marked for removal)

These tools are deprecated and will be removed from the registry after migration:

1. **`file_refactor_detector.py`** ⚠️ DEPRECATED
   - **Replacement**: `--unified-validator --category refactor`
   - **Status**: Archive pending

2. **`session_transition_helper.py`** ⚠️ DEPRECATED
   - **Replacement**: `--unified-validator --category session`
   - **Status**: Archive pending

3. **`tracker_status_validator.py`** ⚠️ DEPRECATED
   - **Replacement**: `--unified-validator --category tracker`
   - **Status**: Archive pending

4. **`workspace_health_monitor.py`** ⚠️ DEPRECATED (Phase 2)
   - **Replacement**: `--unified-monitor --category workspace`
   - **Status**: Archive pending (Phase 2 consolidation)

---

## 🔧 **ADDING TOOLS TO REGISTRY**

### **Step 1: Add Tool Entry**

Edit `tools/toolbelt_registry.py`:

```python
TOOLS_REGISTRY = {
    # ... existing tools ...
    "your-tool-id": {
        "name": "Your Tool Display Name",
        "module": "tools.your_tool_module",
        "main_function": "main",
        "description": "Clear description of what the tool does",
        "flags": ["--your-tool", "-yt"],
        "args_passthrough": True,  # True if tool accepts CLI args
    }
}
```

### **Step 2: Tool Requirements**

Your tool module must:

1. Have a `main()` function
2. Return exit code (0 = success, 1+ = error)
3. Accept arguments via `sys.argv` if `args_passthrough: True`

### **Step 3: Test Registration**

```bash
# Verify tool is registered
python -m tools.toolbelt --list

# Test tool execution
python -m tools.toolbelt --your-tool
```

---

## 🔄 **REMOVING TOOLS FROM REGISTRY**

When archiving a tool:

1. **Add Deprecation Notice**: Add notice to tool file
2. **Update Documentation**: Update migration guides
3. **Remove from Registry**: Remove tool entry from `TOOLS_REGISTRY`
4. **Move to Archive**: Move tool to `tools/deprecated/`
5. **Update This Doc**: Update archived tools section

### **Example Removal**:

```python
# Before
TOOLS_REGISTRY = {
    "old-tool": {
        "name": "Old Tool",
        # ... config ...
    }
}

# After (removed)
TOOLS_REGISTRY = {
    # old-tool removed
}
```

---

## 📚 **TOOLBELT SYSTEM ARCHITECTURE**

```
tools/
├── toolbelt.py              # Main entry point
├── toolbelt_registry.py     # Tool registry (this file)
├── toolbelt_runner.py       # Execution engine
├── toolbelt_help.py         # Help system
└── __main__.py              # Package entry point
```

### **Component Roles**:

- **`toolbelt.py`**: Parses CLI arguments, discovers tools
- **`toolbelt_registry.py`**: Stores tool metadata and flag mappings
- **`toolbelt_runner.py`**: Executes tools with argument passthrough
- **`toolbelt_help.py`**: Generates help text from registry

---

## ✅ **REGISTRY MAINTENANCE**

### **Regular Maintenance Tasks**:

- [ ] Remove deprecated tools after migration period
- [ ] Update tool descriptions for clarity
- [ ] Verify all tool flags are unique
- [ ] Check for duplicate tool IDs
- [ ] Update archived tools list
- [ ] Document new tool additions

### **Registry Validation**:

```python
# Check for duplicate flags
flags_seen = {}
for tool_id, config in TOOLS_REGISTRY.items():
    for flag in config["flags"]:
        if flag in flags_seen:
            raise ValueError(f"Duplicate flag: {flag}")
        flags_seen[flag] = tool_id
```

---

## 🔗 **REFERENCES**

- **Toolbelt README**: `tools/README_TOOLBELT.md`
- **Archived Tools Guide**: `tools/ARCHIVED_TOOLS_MIGRATION_GUIDE.md`
- **Deprecation Notices**: `tools/DEPRECATION_NOTICES.md`
- **Monitoring Migration**: `tools/MIGRATION_GUIDE_DEPRECATED_MONITORING_TOOLS.md`
- **Validation Migration**: `tools/MIGRATION_GUIDE_DEPRECATED_VALIDATION_TOOLS.md`

---

## 📊 **REGISTRY STATISTICS**

- **Active Tools**: ~80+ tools registered
- **Archived Tools**: 3 tools archived
- **Deprecated Tools**: 4 tools deprecated (archive pending)
- **Consolidated Tools**: Multiple tools consolidated into unified tools

---

**Status**: ✅ **TOOLBELT REGISTRY DOCUMENTATION COMPLETE**  
**Support**: Agent-3's archiving work documented and supported

🐝 **WE. ARE. SWARM. ⚡🔥🚀**

