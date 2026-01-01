# 🛠️ Toolbelt Unification & V2 Migration Plan

**Status:** Draft
**Target:** 100% Tool Availability (87+ Tools)
**Current State:** 37 Tools Exposed (Legacy Registry)

## 🎯 Objective
Migrate the active Swarm Toolbelt and MCP Server from the legacy `tools/toolbelt_registry.py` (37 tools) to the comprehensive `tools_v2` architecture (87+ tools). This will expose the full capability of the swarm (OSS management, Brain integration, Advanced Analysis) to agents while maintaining the robustness of recent fixes.

---

## Phase 1: Registry Mapping & Gap Analysis
**Goal:** Ensure every critical tool in the "Unified" (Legacy) list has a corresponding V2 Adapter.

1.  **Audit Comparison**:
    *   Create a mapping matrix between `tools/toolbelt_registry.py` (Legacy) and `tools_v2/tool_registry.lock.json` (V2).
    *   Identify "Orphan" tools: Tools present in Legacy but missing in V2.
    *   Identify "Hidden" tools: Tools present in V2 but missing in Legacy (approx. 50 tools).

2.  **Critical Gap Identification**:
    *   Verify if `monitor` (Unified Monitor) has a V2 equivalent (e.g., `obs.health`).
    *   Verify if `security-scan` has a V2 equivalent.
    *   Verify if `check-sensitive` has a V2 equivalent.

## Phase 2: V2 Adapter Implementation
**Goal:** Wrap legacy tools that are missing from V2 into `IToolAdapter` classes.

For each "Orphan" tool identified in Phase 1:
1.  **Create Adapter**:
    *   Create new file in `tools_v2/categories/` (e.g., `legacy_adapters.py` or specific category).
    *   Implement `IToolAdapter` interface.
    *   Wrap the underlying execution logic (using `subprocess` or direct import).
2.  **Register Tool**:
    *   Update `tools_v2/tool_registry.py` to include the new adapter.
    *   Regenerate `tools_v2/tool_registry.lock.json`.

**Example Adapter Candidates:**
*   `check-sensitive` -> `sec.sensitive_files`
*   `diagnose-auth` -> `github.auth_diagnose`
*   `fix-queue` -> `queue.fix`

## Phase 3: CLI & MCP Entry Point Migration
**Goal:** Switch the "Main Switchboard" to use V2.

1.  **Refactor `tools/toolbelt/__main__.py`**:
    *   Current: Imports `tools.toolbelt_registry`.
    *   Target: Import `tools_v2.toolbelt_core` and `tools_v2.tool_registry`.
    *   Logic:
        *   Initialize `ToolbeltCore`.
        *   Map CLI flags (e.g., `--monitor`) to V2 tool IDs (e.g., `obs.metrics`) if names differ.
        *   Execute via `ToolbeltCore.run()`.

2.  **Refactor `swarm_mcp/servers/tools.py`**:
    *   Update `list_available_tools()` to query `tools_v2.tool_registry`.
    *   Update `execute_toolbelt()` to invoke the unified V2 CLI.
    *   Update `high_value_mappings` to point to V2 tool IDs.

## Phase 4: Verification & Cleanup
**Goal:** Prove 100% operational status.

1.  **Update Verification Script**:
    *   Modify `examples/verify_all_tools.py` to iterate through the *new* V2 registry.
    *   Ensure all 87+ tools return successful help/status codes.
2.  **Deprecate Legacy Registry**:
    *   Mark `tools/toolbelt_registry.py` as deprecated.
    *   Archive legacy runner scripts if fully superseded by V2 adapters.

---

## 📋 Execution Checklist

- [ ] **Step 1:** Run mapping script to identify gaps.
- [ ] **Step 2:** Create `tools_v2/categories/security_extended.py` for missing security tools.
- [ ] **Step 3:** Create `tools_v2/categories/debug_extended.py` for missing debug tools.
- [ ] **Step 4:** Update `tools/toolbelt/__main__.py` to use `tools_v2` as the backend.
- [ ] **Step 5:** Update `swarm_mcp/servers/tools.py` to list V2 tools.
- [ ] **Step 6:** Run full verification suite.

## 🚀 Benefits
*   **Access to ~90 Tools**: Instant access to Swarm Brain, OSS, and Advanced Captain tools.
*   **Unified Architecture**: Single way to run tools (Programmatic + CLI + MCP).
*   **Standardized Output**: V2 tools use structured `ToolResult` objects.
*   **Maintenance**: Only one registry to maintain.
