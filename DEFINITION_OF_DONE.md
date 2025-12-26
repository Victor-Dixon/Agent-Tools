# ✅ Definition of Done: Agent Toolbelt Unification

## 1. Tool Integrity & Completeness
- [ ] **Registry Alignment**: The active tool registry (`toolbelt_registry.py` or V2 equivalent) must accurately reflect **all** usable tools in the codebase (~90+).
- [ ] **Zero Orphans**: No high-value scripts (e.g., in `tools/`) exist outside the registry unless explicitly marked deprecated.
- [ ] **V2 Compliance**: All active tools must conform to V2 standards:
    - [ ] Files <400 lines.
    - [ ] No circular dependencies.
    - [ ] Modular architecture (adapters/executors).

## 2. Operational Stability
- [ ] **Verification**: `verify_all_tools.py` must run with **100% pass rate** (exit code 0).
- [ ] **MCP Integration**: The MCP server (`swarm-tools`) must successfully list and execute all registered tools.
- [ ] **Environment**: No tools should fail due to `ImportError` (missing `src` or incorrect paths).
- [ ] **Security**: No sensitive files (secrets, tokens, `.env`) are tracked in git or exposed by tools.

## 3. Usability & Documentation
- [ ] **Unified CLI**: `python -m tools.toolbelt --help` must list all available tools with descriptions.
- [ ] **Consistent Interface**: All tools accept arguments in a predictable format (JSON or standard flags).
- [ ] **Help Text**: Every tool must implement a `--help` flag that provides usage examples.

## 4. Maintenance & Cleanup
- [ ] **Deprecation**: All legacy/broken tools are moved to `deprecated/` or deleted.
- [ ] **Clean Registry**: The "Legacy" registry is either removed or fully synced with V2.
- [ ] **No Dead Code**: Unused "glue code" from the migration is removed.

---

**Success Metric:** An agent connecting via MCP can discover, query help for, and successfully execute any of the ~90 tools without human intervention or "file not found" errors.
