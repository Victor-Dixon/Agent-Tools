# 🗂️ Tools Flattening & Organization Plan

**Date**: 2025-12-29  
**Status**: Planning Phase  
**Goal**: Flatten `tools/` and `tools_v2/` into a single unified `tools/` directory with clear organization strategy

---

## 📊 Current State Analysis

### Directory Statistics

| Metric | `tools/` | `tools_v2/` | **Total** |
|--------|----------|------------|-----------|
| **Python Files** | 241 | 88 | **329** |
| **Directories** | 32 | 6 | **38** |
| **Unified Tools** | 19 | 0 | **19** |
| **Registry System** | `toolbelt_registry.py` (39 tools) | `tool_registry.py` + JSON (91 tools) | **130 tools** |
| **V2 Compliance** | ~60% | 100% | **Mixed** |
| **Architecture** | Direct imports | Adapter pattern | **Different** |

### Current Structure

```
tools/
├── agent/              - Agent operations
├── analysis/           - Analysis tools
├── autonomous/          - Autonomous workflows
├── captain/             - Captain tools
├── cleanup/             - Cleanup utilities
├── cli/                 - CLI framework
│   ├── commands/        - Command handlers
│   └── dispatchers/     - Unified dispatcher
├── codemods/            - Code modification tools
├── communication/       - Communication tools
├── consolidation/       - Consolidation utilities
├── coordination/        - Coordination tools
├── coverage/            - Coverage tools
├── debug/               - Debugging tools
├── deprecated/          - Deprecated tools
├── devops/              - DevOps tools
├── discord/             - Discord integration
├── examples/            - Example scripts
├── fixes/               - Fix utilities
├── github/              - GitHub integration
├── monitoring/          - Monitoring tools
├── security/            - Security tools
├── templates/           - Templates
├── thea/                - Thea automation
├── toolbelt/            - Toolbelt core
├── validation/          - Validation tools
├── verification/        - Verification tools
├── wordpress/           - WordPress tools
└── toolbelt_registry.py - Registry (39 tools)

tools_v2/
├── adapters/            - IToolAdapter pattern
│   ├── base_adapter.py  - Base adapter ABC
│   └── error_types.py   - Error hierarchy
├── categories/          - Category-based tools (70+ files)
│   ├── analysis_tools.py
│   ├── agent_ops_tools.py
│   ├── captain_tools.py
│   ├── discord_tools.py
│   ├── infrastructure_tools.py
│   └── ... (70+ category files)
├── core/                - Core utilities
├── tests/                - Test files
├── utils/                - Utility functions
├── tool_registry.py     - Dynamic registry
├── tool_registry.lock.json - Tool lock file (91 tools)
└── toolbelt_core.py     - Core orchestrator
```

---

## 🎯 Flattening Strategy

### Phase 1: Pre-Flattening Analysis (P0)

**Objective**: Understand dependencies, conflicts, and migration requirements before flattening.

#### 1.1 Dependency Mapping
- [ ] [ANALYSIS][P0] Map all imports from `tools/` to `tools_v2/`
- [ ] [ANALYSIS][P0] Map all imports from `tools_v2/` to `tools/`
- [ ] [ANALYSIS][P0] Identify cross-directory dependencies
- [ ] [ANALYSIS][P0] Document external dependencies (swarm_mcp, etc.)
- [ ] [ANALYSIS][P0] Create dependency graph visualization

#### 1.2 Conflict Detection
- [ ] [ANALYSIS][P0] Identify duplicate file names between `tools/` and `tools_v2/`
- [ ] [ANALYSIS][P0] Identify duplicate tool functionality
- [ ] [ANALYSIS][P0] Identify conflicting module names
- [ ] [ANALYSIS][P0] Document naming conflicts

#### 1.3 Registry Analysis
- [ ] [ANALYSIS][P0] Compare `toolbelt_registry.py` vs `tool_registry.lock.json`
- [ ] [ANALYSIS][P0] Identify overlapping tool registrations
- [ ] [ANALYSIS][P0] Document registry differences
- [ ] [ANALYSIS][P0] Plan unified registry structure

#### 1.4 Architecture Analysis
- [ ] [ANALYSIS][P0] Document adapter pattern usage in `tools_v2/`
- [ ] [ANALYSIS][P0] Document direct import pattern in `tools/`
- [ ] [ANALYSIS][P0] Identify tools that need adapter conversion
- [ ] [ANALYSIS][P0] Plan adapter migration strategy

---

### Phase 2: Target Organization Structure (P0)

**Objective**: Design the unified `tools/` directory structure.

#### 2.1 Proposed Structure

```
tools/
├── __init__.py                    # Public API exports
├── core/                          # Core infrastructure
│   ├── __init__.py
│   ├── registry.py                # Unified tool registry
│   ├── dispatcher.py              # Unified CLI dispatcher
│   ├── adapters/                  # Adapter pattern infrastructure
│   │   ├── __init__.py
│   │   ├── base_adapter.py        # IToolAdapter ABC
│   │   ├── error_types.py         # Error hierarchy
│   │   └── legacy_adapter.py      # Adapter for non-V2 tools
│   └── utils/                      # Core utilities
│       ├── __init__.py
│       └── ...
│
├── categories/                    # Category-based tool organization
│   ├── __init__.py                # Category exports
│   ├── analysis_tools.py          # Analysis & scanning
│   ├── agent_ops_tools.py         # Agent operations
│   ├── captain_tools.py           # Captain coordination
│   ├── communication_tools.py     # Messaging & communication
│   ├── discord_tools.py           # Discord integration
│   ├── github_tools.py            # GitHub integration
│   ├── infrastructure_tools.py    # DevOps & infrastructure
│   ├── monitoring_tools.py        # System monitoring
│   ├── security_tools.py          # Security scanning
│   ├── testing_tools.py           # Testing & coverage
│   ├── validation_tools.py        # Validation & verification
│   ├── web_tools.py               # WordPress & web
│   └── ...                        # Additional categories
│
├── unified/                       # Unified domain tools (legacy)
│   ├── __init__.py
│   ├── unified_monitor.py         # System monitoring
│   ├── unified_validator.py       # Validation
│   ├── unified_analyzer.py        # Analysis
│   ├── unified_security_scanner.py
│   ├── unified_debugger.py
│   ├── unified_environment.py
│   ├── unified_captain.py
│   ├── unified_agent.py
│   ├── unified_cleanup.py
│   ├── unified_discord.py
│   ├── unified_github.py
│   ├── unified_verifier.py
│   └── unified_wordpress.py
│
├── domain/                        # Domain-specific tools (specialized)
│   ├── __init__.py
│   ├── thea/                      # Thea automation
│   │   ├── __init__.py
│   │   └── ...
│   ├── codemods/                  # Code modification
│   │   ├── __init__.py
│   │   └── ...
│   └── ...                        # Other specialized domains
│
├── cli/                           # CLI framework
│   ├── __init__.py
│   ├── commands/                  # Command handlers
│   │   ├── __init__.py
│   │   └── registry.py            # Command registry
│   └── dispatchers/               # Dispatchers
│       ├── __init__.py
│       └── unified_dispatcher.py
│
├── deprecated/                    # Deprecated tools (for reference)
│   ├── __init__.py
│   └── ...
│
├── templates/                     # Tool templates
│   ├── __init__.py
│   └── ...
│
├── examples/                      # Example scripts
│   ├── __init__.py
│   └── ...
│
└── tests/                         # Tool tests
    ├── __init__.py
    └── ...
```

#### 2.2 Organization Principles

1. **Category-Based Primary Organization**
   - All tools organized by functional category
   - Categories align with tool domains (analysis, monitoring, etc.)
   - Each category file contains related tools as classes

2. **Unified Tools as Legacy Bridge**
   - Keep `unified_*.py` tools in `unified/` directory
   - These serve as backward compatibility layer
   - Gradually migrate functionality to categories

3. **Domain Tools for Specialized Cases**
   - Highly specialized tools (e.g., Thea automation) in `domain/`
   - These don't fit standard categories
   - Can be converted to categories later if they grow

4. **Core Infrastructure Separate**
   - Registry, dispatcher, adapters in `core/`
   - Reusable utilities in `core/utils/`
   - Clear separation of infrastructure from tools

5. **CLI Framework Isolated**
   - CLI code in `cli/` directory
   - Commands and dispatchers separate from tool logic
   - Maintains clean architecture

---

### Phase 3: Flattening Execution (P0)

**Objective**: Physically move and reorganize files into unified structure.

#### 3.1 Create Target Structure
- [ ] [FLATTEN][P0] Create `tools/core/` directory structure
- [ ] [FLATTEN][P0] Create `tools/categories/` directory
- [ ] [FLATTEN][P0] Create `tools/unified/` directory
- [ ] [FLATTEN][P0] Create `tools/domain/` directory
- [ ] [FLATTEN][P0] Create `tools/deprecated/` directory

#### 3.2 Move Core Infrastructure
- [ ] [FLATTEN][P0] Move `tools_v2/adapters/` → `tools/core/adapters/`
- [ ] [FLATTEN][P0] Move `tools_v2/tool_registry.py` → `tools/core/registry.py`
- [ ] [FLATTEN][P0] Move `tools_v2/toolbelt_core.py` → `tools/core/dispatcher.py`
- [ ] [FLATTEN][P0] Move `tools/cli/` → `tools/cli/` (keep existing)
- [ ] [FLATTEN][P0] Move `tools_v2/core/` → `tools/core/utils/` (if exists)
- [ ] [FLATTEN][P0] Move `tools_v2/utils/` → `tools/core/utils/` (merge)

#### 3.3 Move Category Tools
- [ ] [FLATTEN][P0] Move `tools_v2/categories/*.py` → `tools/categories/`
- [ ] [FLATTEN][P0] Keep existing category files, merge duplicates
- [ ] [FLATTEN][P0] Update imports in category files

#### 3.4 Move Unified Tools
- [ ] [FLATTEN][P0] Move `tools/*/unified_*.py` → `tools/unified/`
- [ ] [FLATTEN][P0] Update imports in unified tools
- [ ] [FLATTEN][P0] Maintain backward compatibility

#### 3.5 Move Domain Tools
- [ ] [FLATTEN][P0] Move `tools/thea/` → `tools/domain/thea/`
- [ ] [FLATTEN][P0] Move `tools/codemods/` → `tools/domain/codemods/`
- [ ] [FLATTEN][P0] Identify other specialized domains
- [ ] [FLATTEN][P0] Move specialized tools to `tools/domain/`

#### 3.6 Move Deprecated Tools
- [ ] [FLATTEN][P0] Move `tools/deprecated/` → `tools/deprecated/` (keep)
- [ ] [FLATTEN][P0] Identify deprecated tools from `tools_v2/`
- [ ] [FLATTEN][P0] Move deprecated tools to `tools/deprecated/`

#### 3.7 Move Tests and Examples
- [ ] [FLATTEN][P0] Move `tools_v2/tests/` → `tools/tests/` (merge)
- [ ] [FLATTEN][P0] Move `tools/examples/` → `tools/examples/` (keep)
- [ ] [FLATTEN][P0] Move `tools/templates/` → `tools/templates/` (keep)

#### 3.8 Clean Up Empty Directories
- [ ] [FLATTEN][P0] Remove empty directories from old structure
- [ ] [FLATTEN][P0] Verify no orphaned files

---

### Phase 4: Import Path Updates (P0)

**Objective**: Update all import statements to reflect new structure.

#### 4.1 Update Internal Imports
- [ ] [IMPORT][P0] Update imports in `tools/categories/*.py`
- [ ] [IMPORT][P0] Update imports in `tools/unified/*.py`
- [ ] [IMPORT][P0] Update imports in `tools/domain/*.py`
- [ ] [IMPORT][P0] Update imports in `tools/core/*.py`
- [ ] [IMPORT][P0] Update imports in `tools/cli/*.py`

#### 4.2 Update External Imports
- [ ] [IMPORT][P0] Update imports in `swarm_mcp/` (if any)
- [ ] [IMPORT][P0] Update imports in `tests/`
- [ ] [IMPORT][P0] Update imports in `examples/`
- [ ] [IMPORT][P0] Update imports in MCP servers

#### 4.3 Update Registry References
- [ ] [IMPORT][P0] Update `tool_registry.lock.json` paths
- [ ] [IMPORT][P0] Update `toolbelt_registry.py` paths
- [ ] [IMPORT][P0] Update registry module paths

---

### Phase 5: Registry Unification (P0)

**Objective**: Merge two registries into a single unified system.

#### 5.1 Design Unified Registry
- [ ] [REGISTRY][P0] Design unified registry API
- [ ] [REGISTRY][P0] Support both adapter and direct import patterns
- [ ] [REGISTRY][P0] Maintain backward compatibility
- [ ] [REGISTRY][P0] Create migration path for old registries

#### 5.2 Merge Registry Data
- [ ] [REGISTRY][P0] Merge `toolbelt_registry.py` entries into unified registry
- [ ] [REGISTRY][P0] Merge `tool_registry.lock.json` entries
- [ ] [REGISTRY][P0] Resolve duplicate tool registrations
- [ ] [REGISTRY][P0] Update tool paths to new structure

#### 5.3 Create Unified Registry Implementation
- [ ] [REGISTRY][P0] Implement `tools/core/registry.py`
- [ ] [REGISTRY][P0] Support dynamic tool discovery
- [ ] [REGISTRY][P0] Support static tool registration
- [ ] [REGISTRY][P0] Maintain JSON lock file for caching

#### 5.4 Update Registry Consumers
- [ ] [REGISTRY][P0] Update CLI dispatcher to use unified registry
- [ ] [REGISTRY][P0] Update MCP servers to use unified registry
- [ ] [REGISTRY][P0] Update tool execution code

---

### Phase 6: Adapter Pattern Migration (P1)

**Objective**: Convert non-adapter tools to adapter pattern where beneficial.

#### 6.1 Identify Migration Candidates
- [ ] [ADAPTER][P1] Identify unified tools that should use adapters
- [ ] [ADAPTER][P1] Identify domain tools that should use adapters
- [ ] [ADAPTER][P1] Prioritize high-value tools for migration

#### 6.2 Create Legacy Adapter
- [ ] [ADAPTER][P1] Create `tools/core/adapters/legacy_adapter.py`
- [ ] [ADAPTER][P1] Wrapper for non-adapter tools
- [ ] [ADAPTER][P1] Enables gradual migration

#### 6.3 Migrate Tools to Adapters
- [ ] [ADAPTER][P1] Convert unified tools to adapters (optional)
- [ ] [ADAPTER][P1] Convert domain tools to adapters (optional)
- [ ] [ADAPTER][P1] Maintain backward compatibility

---

### Phase 7: Testing & Validation (P0)

**Objective**: Ensure flattened structure works correctly.

#### 7.1 Import Testing
- [ ] [TEST][P0] Test all imports in new structure
- [ ] [TEST][P0] Fix broken imports
- [ ] [TEST][P0] Verify no circular dependencies

#### 7.2 Registry Testing
- [ ] [TEST][P0] Test unified registry discovery
- [ ] [TEST][P0] Test tool execution via registry
- [ ] [TEST][P0] Test CLI command dispatch

#### 7.3 Integration Testing
- [ ] [TEST][P0] Test MCP server tool access
- [ ] [TEST][P0] Test CLI tool execution
- [ ] [TEST][P0] Test backward compatibility

#### 7.4 Smoke Testing
- [ ] [TEST][P0] Run all unified tools
- [ ] [TEST][P0] Run sample category tools
- [ ] [TEST][P0] Verify no regressions

---

### Phase 8: Documentation & Cleanup (P1)

**Objective**: Document new structure and clean up old files.

#### 8.1 Update Documentation
- [ ] [DOCS][P1] Update `README.md` with new structure
- [ ] [DOCS][P1] Update `CONTRIBUTING.md` with new organization
- [ ] [DOCS][P1] Create `tools/README.md` with structure guide
- [ ] [DOCS][P1] Document migration from old structure

#### 8.2 Remove Old Structure
- [ ] [CLEANUP][P1] Remove `tools_v2/` directory (after verification)
- [ ] [CLEANUP][P1] Remove old registry files (keep backups)
- [ ] [CLEANUP][P1] Clean up empty directories

#### 8.3 Create Migration Guide
- [ ] [DOCS][P1] Document import path changes
- [ ] [DOCS][P1] Document registry API changes
- [ ] [DOCS][P1] Create migration script for external users

---

## 📋 Detailed File Mapping

### Core Infrastructure

| Source | Target | Notes |
|--------|--------|-------|
| `tools_v2/adapters/base_adapter.py` | `tools/core/adapters/base_adapter.py` | Keep as-is |
| `tools_v2/adapters/error_types.py` | `tools/core/adapters/error_types.py` | Keep as-is |
| `tools_v2/tool_registry.py` | `tools/core/registry.py` | Rename, update paths |
| `tools_v2/tool_registry.lock.json` | `tools/core/registry.lock.json` | Update paths |
| `tools_v2/toolbelt_core.py` | `tools/core/dispatcher.py` | Rename, update paths |
| `tools/toolbelt_registry.py` | `tools/core/registry.py` | Merge into unified registry |

### Categories

| Source | Target | Notes |
|--------|--------|-------|
| `tools_v2/categories/*.py` | `tools/categories/*.py` | Move all, update imports |
| `tools/analysis/unified_analyzer.py` | `tools/unified/unified_analyzer.py` | Move to unified |
| `tools/monitoring/unified_monitor.py` | `tools/unified/unified_monitor.py` | Move to unified |
| `tools/validation/unified_validator.py` | `tools/unified/unified_validator.py` | Move to unified |

### Unified Tools

All `unified_*.py` files from various `tools/*/` directories → `tools/unified/`

### Domain Tools

| Source | Target | Notes |
|--------|--------|-------|
| `tools/thea/*.py` | `tools/domain/thea/*.py` | Move entire directory |
| `tools/codemods/*.py` | `tools/domain/codemods/*.py` | Move entire directory |

---

## ⚠️ Risks & Mitigation

### Risk 1: Import Path Breakage
- **Risk**: High - Many files depend on current import paths
- **Mitigation**: 
  - Comprehensive import path mapping
  - Automated import update script
  - Extensive testing before removal of old structure

### Risk 2: Registry Conflicts
- **Risk**: Medium - Two registries may have conflicting entries
- **Mitigation**:
  - Detailed registry comparison
  - Conflict resolution strategy
  - Backward compatibility layer

### Risk 3: Circular Dependencies
- **Risk**: Medium - Flattening may create circular imports
- **Mitigation**:
  - Dependency graph analysis
  - Careful import organization
  - Testing for circular dependencies

### Risk 4: Lost Functionality
- **Risk**: Low - Tools may be missed during migration
- **Mitigation**:
  - Comprehensive file inventory
  - Automated migration scripts
  - Verification testing

---

## 🎯 Success Criteria

### Phase 1-3 (Flattening)
- [ ] All files moved to unified `tools/` structure
- [ ] No duplicate files
- [ ] All directories created correctly

### Phase 4-5 (Integration)
- [ ] All imports updated and working
- [ ] Unified registry functional
- [ ] No broken tool references

### Phase 6-7 (Migration & Testing)
- [ ] All tools accessible via new structure
- [ ] CLI commands work
- [ ] MCP servers work
- [ ] Tests pass

### Phase 8 (Completion)
- [ ] Documentation updated
- [ ] Old structure removed
- [ ] Migration guide created

---

## 📅 Estimated Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Analysis | 1-2 days | None |
| Phase 2: Structure Design | 1 day | Phase 1 |
| Phase 3: Flattening | 2-3 days | Phase 2 |
| Phase 4: Import Updates | 2-3 days | Phase 3 |
| Phase 5: Registry Unification | 2-3 days | Phase 4 |
| Phase 6: Adapter Migration | 3-5 days | Phase 5 (optional) |
| Phase 7: Testing | 2-3 days | Phase 5 |
| Phase 8: Documentation | 1-2 days | Phase 7 |

**Total Estimated Time**: 14-22 days (2-3 weeks)

---

## 🚀 Quick Start

### Immediate Next Steps

1. **Start Phase 1**: Run dependency analysis
   ```bash
   # Create dependency mapping script
   python scripts/analyze_dependencies.py
   ```

2. **Create Target Structure**: Set up new directory structure
   ```bash
   mkdir -p tools/{core/{adapters,utils},categories,unified,domain/{thea,codemods},deprecated}
   ```

3. **Begin Flattening**: Start with core infrastructure
   ```bash
   # Move adapters first (lowest risk)
   cp -r tools_v2/adapters/* tools/core/adapters/
   ```

---

**Status**: Ready for execution  
**Priority**: P0 (Critical)  
**Owner**: TBD

---

*"The strength of the wolf is the pack."* 🐺


