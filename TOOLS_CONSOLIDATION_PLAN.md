# 🗂️ Tools & Tools_v2 Consolidation Plan

**Date**: 2025-12-26  
**Status**: Planning Phase  
**Goal**: Consolidate `tools/` and `tools_v2/` into a unified, V2-compliant architecture

---

## 📊 Current State Analysis

### `tools/` Directory
- **Structure**: Flat organization with domain subdirectories
- **Count**: ~158 tools (after previous consolidation from 709)
- **Registry**: `toolbelt_registry.py` - Maps CLI flags to tool modules
- **Architecture**: Direct module imports, no adapter pattern
- **V2 Compliance**: Mixed (some files >400 lines)

### `tools_v2/` Directory
- **Structure**: Category-based with adapter pattern
- **Count**: 23+ tools registered
- **Registry**: `tool_registry.py` + `tool_registry.lock.json`
- **Architecture**: Adapter pattern (`IToolAdapter`), V2 compliant
- **V2 Compliance**: 100% (all files ≤400 lines)

### Key Differences

| Aspect | `tools/` | `tools_v2/` |
|--------|----------|-------------|
| **Organization** | Domain-based (monitoring/, validation/, etc.) | Category-based (categories/*.py) |
| **Interface** | Direct function calls | Adapter pattern (IToolAdapter) |
| **Registry** | Python dict in `toolbelt_registry.py` | JSON lock file + dynamic loading |
| **V2 Compliance** | Partial | 100% |
| **CLI Access** | Via `toolbelt_registry.py` | Via `toolbelt_core.py` |
| **Type Safety** | Partial | Complete (type hints) |

---

## 🎯 Consolidation Strategy

### Phase 0A: Organization & Planning (P0) - **START HERE**
- [ ] [ORG][P0] Create comprehensive tool inventory system
- [ ] [ORG][P0] Document current architecture and dependencies
- [ ] [ORG][P0] Establish tracking and progress monitoring
- [ ] [ORG][P0] Define success criteria and metrics
- [ ] [ORG][P0] Create risk assessment and mitigation plans
- [ ] [ORG][P0] Set up testing framework for validation
- [ ] [ORG][P0] Establish rollback procedures

### Phase 1: Analysis & Mapping (P0)
- [ ] [ANALYSIS][P0] Inventory all tools in `tools/` directory
- [ ] [ANALYSIS][P0] Map `tools/` tools to `tools_v2/` categories
- [ ] [ANALYSIS][P0] Identify duplicate tools between directories
- [ ] [ANALYSIS][P0] Identify tools that need migration vs. deletion
- [ ] [ANALYSIS][P0] Create migration priority list

### Phase 2: Unified Tools Migration (P0)
- [ ] [MIGRATE][P0] Migrate unified tools to `tools_v2/`:
  - [ ] `unified_monitor.py` → `categories/monitoring_tools.py`
  - [ ] `unified_validator.py` → `categories/validation_tools.py`
  - [ ] `unified_analyzer.py` → `categories/analysis_tools.py`
  - [ ] `unified_security_scanner.py` → `categories/security_tools.py`
  - [ ] `unified_debugger.py` → `categories/debug_tools.py`
  - [ ] `unified_environment.py` → `categories/environment_tools.py`
  - [ ] `unified_captain.py` → `categories/captain_tools.py`
  - [ ] `unified_agent.py` → `categories/agent_ops_tools.py`

### Phase 3: Domain Tools Migration (P1)
- [ ] [MIGRATE][P1] Migrate domain-specific tools:
  - [ ] `tools/github/` → `categories/github_tools.py`
  - [ ] `tools/wordpress/` → `categories/web_tools.py` (extend existing)
  - [ ] `tools/discord/` → `categories/discord_tools.py` (extend existing)
  - [ ] `tools/communication/` → `categories/communication_tools.py` (extend existing)
  - [ ] `tools/testing/` → `categories/testing_tools.py` (extend existing)
  - [ ] `tools/security/` → `categories/security_tools.py` (extend existing)
  - [ ] `tools/devops/` → `categories/infrastructure_tools.py` (extend existing)

### Phase 4: Adapter Pattern Conversion (P1)
- [ ] [CONVERT][P1] Convert all migrated tools to `IToolAdapter` interface
- [ ] [CONVERT][P1] Ensure all tools have:
  - [ ] `get_spec()` method returning `ToolSpec`
  - [ ] `validate()` method for parameter validation
  - [ ] `execute()` method for tool execution
  - [ ] Complete type hints
- [ ] [CONVERT][P1] Update `tool_registry.lock.json` with all new tools

### Phase 5: Registry Unification (P1)
- [ ] [REGISTRY][P1] Create unified registry that:
  - [ ] Supports both old `toolbelt_registry.py` format (backward compatibility)
  - [ ] Supports new `tool_registry.py` format (adapter pattern)
  - [ ] Provides migration path for existing CLI commands
- [ ] [REGISTRY][P1] Update `toolbelt_core.py` to handle both registries
- [ ] [REGISTRY][P1] Create adapter layer for old-style tools

### Phase 6: Duplicate Removal (P1)
- [ ] [CLEAN][P1] Delete duplicate tools identified in analysis:
  - [ ] `tools/projectscanner.py` (keep `projectscanner_modular_reports.py` → migrate to v2)
  - [ ] `tools/captain_workspace_cleanup.py` (keep `auto_workspace_cleanup.py` → migrate to v2)
  - [ ] `tools/duplication_analyzer.py` (keep `duplication_checker.py` → migrate to v2)
  - [ ] `tools/unified_validator.py` (if migrated to v2)
- [ ] [CLEAN][P1] Archive deprecated tools to `tools/deprecated/consolidated_v2/`

### Phase 7: Testing & Validation (P1)
- [ ] [TEST][P1] Test all migrated tools via `toolbelt_core.py`
- [ ] [TEST][P1] Verify backward compatibility with existing CLI commands
- [ ] [TEST][P1] Run V2 compliance check on all migrated tools
- [ ] [TEST][P1] Update test suite for new tool structure
- [ ] [TEST][P1] Integration tests for registry unification

### Phase 8: Documentation & Cleanup (P2)
- [ ] [DOCS][P2] Update `tools_v2/README.md` with consolidated tool list
- [ ] [DOCS][P2] Create migration guide for agents using old tools
- [ ] [DOCS][P2] Update `MASTER_TASK_LIST.md` with consolidation status
- [ ] [DOCS][P2] Document new unified registry architecture
- [ ] [CLEAN][P2] Remove empty directories from `tools/`
- [ ] [CLEAN][P2] Update all import statements across codebase

---

## 📋 Detailed Migration Checklist

### Unified Tools (Priority: P0)

#### 1. Unified Monitor
- **Source**: `tools/monitoring/unified_monitor.py`
- **Target**: `tools_v2/categories/monitoring_tools.py`
- **Status**: ⏳ Pending
- **Tasks**:
  - [ ] Create `MonitoringTools` adapter class
  - [ ] Implement `MonitorQueueTool`, `MonitorServiceTool`, `MonitorDiskTool`, etc.
  - [ ] Register in `tool_registry.lock.json`
  - [ ] Test via `toolbelt_core.py`

#### 2. Unified Validator
- **Source**: `tools/validation/unified_validator.py`
- **Target**: `tools_v2/categories/validation_tools.py` (extend existing)
- **Status**: ⏳ Pending
- **Tasks**:
  - [ ] Review existing `validation_tools.py`
  - [ ] Add unified validator methods as new tools
  - [ ] Register in `tool_registry.lock.json`
  - [ ] Test via `toolbelt_core.py`

#### 3. Unified Analyzer
- **Source**: `tools/analysis/unified_analyzer.py`
- **Target**: `tools_v2/categories/analysis_tools.py` (extend existing)
- **Status**: ⏳ Pending
- **Tasks**:
  - [ ] Review existing `analysis_tools.py`
  - [ ] Add unified analyzer methods as new tools
  - [ ] Register in `tool_registry.lock.json`
  - [ ] Test via `toolbelt_core.py`

#### 4. Unified Security Scanner
- **Source**: `tools/security/unified_security_scanner.py`
- **Target**: `tools_v2/categories/security_tools.py` (new)
- **Status**: ⏳ Pending
- **Tasks**:
  - [ ] Create `security_tools.py` category file
  - [ ] Implement security scanning tools as adapters
  - [ ] Register in `tool_registry.lock.json`
  - [ ] Test via `toolbelt_core.py`

#### 5. Unified Debugger
- **Source**: `tools/debug/unified_debugger.py`
- **Target**: `tools_v2/categories/debug_tools.py` (new)
- **Status**: ⏳ Pending
- **Tasks**:
  - [ ] Create `debug_tools.py` category file
  - [ ] Implement debugging tools as adapters
  - [ ] Register in `tool_registry.lock.json`
  - [ ] Test via `toolbelt_core.py`

#### 6. Unified Environment
- **Source**: `tools/devops/unified_environment.py`
- **Target**: `tools_v2/categories/environment_tools.py` (new)
- **Status**: ⏳ Pending
- **Tasks**:
  - [ ] Create `environment_tools.py` category file
  - [ ] Implement environment checking tools as adapters
  - [ ] Register in `tool_registry.lock.json`
  - [ ] Test via `toolbelt_core.py`

### Domain Tools (Priority: P1)

#### GitHub Tools
- **Source**: `tools/github/` directory
- **Target**: `tools_v2/categories/github_tools.py` (new)
- **Status**: ⏳ Pending
- **Key Tools to Migrate**:
  - [ ] `unified_github.py`
  - [ ] `repo_safe_merge.py`
  - [ ] `github_pr_debugger.py`
  - [ ] Others as needed

#### WordPress Tools
- **Source**: `tools/wordpress/` directory
- **Target**: `tools_v2/categories/web_tools.py` (extend existing)
- **Status**: ⏳ Pending
- **Key Tools to Migrate**:
  - [ ] `unified_wordpress.py`
  - [ ] `wordpress_manager.py`
  - [ ] Others as needed

#### Discord Tools
- **Source**: `tools/discord/` directory
- **Target**: `tools_v2/categories/discord_tools.py` (extend existing)
- **Status**: ⏳ Pending
- **Key Tools to Migrate**:
  - [ ] `unified_discord.py`
  - [ ] `discord_startup_listener.py`
  - [ ] Others as needed

---

## 🔄 Registry Unification Strategy

### Current State
- **Old Registry**: `tools/toolbelt_registry.py` - Dict-based, direct module imports
- **New Registry**: `tools_v2/tool_registry.py` - JSON-based, adapter pattern

### Unified Registry Design
```python
# Unified registry that supports both patterns
class UnifiedToolRegistry:
    def __init__(self):
        self.v2_registry = ToolRegistry()  # New adapter-based
        self.v1_registry = ToolRegistryV1()  # Old module-based
        self.migration_map = {}  # Maps old tools to new tools
    
    def get_tool(self, tool_name: str):
        # Try v2 first, fall back to v1
        # Log migration warnings for v1 usage
        pass
```

### Backward Compatibility
- [ ] [COMPAT][P1] Maintain `toolbelt_registry.py` for existing CLI commands
- [ ] [COMPAT][P1] Create adapter wrapper for old-style tools
- [ ] [COMPAT][P1] Add deprecation warnings for old registry usage
- [ ] [COMPAT][P1] Provide migration script for agents

---

## 📊 Success Metrics

### Quantitative
- [ ] **Tool Count**: Reduce from 158+ tools to ~50-80 consolidated tools
- [ ] **V2 Compliance**: 100% of tools in `tools_v2/` ≤400 lines
- [ ] **Registry Coverage**: All tools accessible via unified registry
- [ ] **Test Coverage**: >80% test coverage for migrated tools

### Qualitative
- [ ] **Architecture**: All tools use adapter pattern
- [ ] **Type Safety**: Complete type hints coverage
- [ ] **Documentation**: All tools documented in `tools_v2/README.md`
- [ ] **Backward Compatibility**: Existing CLI commands still work

---

## 🚨 Risks & Mitigation

### Risk 1: Breaking Changes
- **Mitigation**: Maintain backward compatibility layer, gradual migration
- **Mitigation**: Comprehensive testing before removal of old tools

### Risk 2: Lost Functionality
- **Mitigation**: Detailed analysis phase, careful mapping of features
- **Mitigation**: Test each migrated tool before deletion

### Risk 3: Registry Conflicts
- **Mitigation**: Clear naming conventions, namespace separation
- **Mitigation**: Migration map to handle conflicts

### Risk 4: V2 Compliance Violations
- **Mitigation**: Automated V2 compliance checks
- **Mitigation**: Refactor large tools into smaller adapters

---

## 📅 Timeline Estimate

| Phase | Duration | Priority |
|-------|----------|----------|
| Phase 1: Analysis | 1-2 days | P0 |
| Phase 2: Unified Tools | 2-3 days | P0 |
| Phase 3: Domain Tools | 3-5 days | P1 |
| Phase 4: Adapter Conversion | 2-3 days | P1 |
| Phase 5: Registry Unification | 2-3 days | P1 |
| Phase 6: Duplicate Removal | 1 day | P1 |
| Phase 7: Testing | 2-3 days | P1 |
| Phase 8: Documentation | 1-2 days | P2 |
| **Total** | **14-22 days** | |

---

## 🎯 Next Steps

1. **Immediate (Today)**:
   - [ ] Review this consolidation plan
   - [ ] Start Phase 1: Analysis & Mapping
   - [ ] Create detailed tool inventory

2. **This Week**:
   - [ ] Complete Phase 1 analysis
   - [ ] Begin Phase 2: Unified tools migration
   - [ ] Migrate first unified tool as proof of concept

3. **Next Week**:
   - [ ] Complete Phase 2 & 3 migrations
   - [ ] Begin Phase 4: Adapter conversion
   - [ ] Start Phase 5: Registry unification

---

## 📝 Notes

- This consolidation maintains backward compatibility where possible
- Tools will be migrated incrementally, not all at once
- Old `tools/` directory will remain until all tools are migrated and tested
- Final structure: `tools_v2/` becomes the single source of truth
- `tools/` becomes a legacy/deprecated directory (eventually removed)

---

**🐺 WE ARE SWARM**

*"The strength of the pack is the wolf, and the strength of the wolf is the pack."*

