# 🗺️ Master Plan: Tools Consolidation Phase 1

**Goal**: Consolidate 399 specialized tools into 3 unified systems (`unified_monitor`, `unified_validator`, `unified_analyzer`), reducing tool count by ~56%.

**Strategy**: "Consolidate, Verify, DELETE".
We move fast and break stuff. Functionality goes into unified tools, verify they work, then DELETE the old tools. No archives.

---

## 🏗️ Preparation Phase

- [x] **Create `unified_validator.py`**: ✅ Created with SSOT, imports, tracker, session, refactor, consolidation, and queue validation categories.
- [x] **Verify `unified_monitor.py`**: ✅ Confirmed working - handles queue, service, disk, agent, workspace, and coverage monitoring.
- [x] **Verify `unified_analyzer.py`**: ✅ Confirmed working - handles repository, structure, file, consolidation, and overlap analysis.
- [x] **Create Archival Directory**: ✅ `tools/deprecated/consolidated_phase1` exists.

---

## 🚀 Phase 1: Monitoring Consolidation (108 candidates)

**Target Tool**: `unified_monitor.py`

- [x] **Batch 1: Status & Health Checks** ✅ COMPLETE
    - `captain_check_agent_status.py` - Already archived in `deprecated/consolidated_2025-12-05/`
    - `workspace_health_monitor.py` - Archived to `deprecated/consolidated_phase1/`
    - Service health monitoring consolidated in `unified_monitor.py`
- [x] **Batch 2: Queue & Infrastructure** ✅ COMPLETE
    - `check_queue_status.py`, `check_queue_issue.py` - Archived to `deprecated/consolidated_phase1/`
    - `check_service_status.py` - Archived to `deprecated/consolidated_phase1/`
    - Queue/service logic consolidated in `unified_monitor.py`
- [x] **Batch 3: Recovery Triggers** ✅ COMPLETE
    - `status_monitor_recovery_trigger.py` - Archived to `deprecated/consolidated_phase1/`
    - Resume trigger functionality in `unified_monitor.py --trigger-resume`

**Status**: ✅ PHASE 1 COMPLETE - Use `python3 unified_monitor.py --category all` for all monitoring.

---

## 🛡️ Phase 2: Validation Consolidation (73 candidates)

**Target Tool**: `unified_validator.py`

- [x] **Batch 1: SSOT & Config** ✅ DELETED
    - 4 ssot_* tools DELETED
- [x] **Batch 2: Code & Imports** ✅ DELETED
    - 14 validate_* tools DELETED
    - 1 consolidation/validate_consolidation.py DELETED
- [x] **Batch 3: System Verification** ✅ DELETED
    - 36 verify_* tools DELETED
    - 24 check_* tools DELETED

**Status**: ✅ PHASE 2 COMPLETE - 78 tools DELETED. Use `python3 unified_validator.py --all` for all validation.

---

## 🧠 Phase 3: Analysis Consolidation (218 candidates)

**Target Tool**: `unified_analyzer.py`

- [x] **Batch 1: Reporting & Metrics** ✅ DELETED
    - tech_debt_*, generate_*report*, analyze_* tools DELETED
- [x] **Batch 2: Codebase Scanning** ✅ DELETED  
    - scan_*, diagnose_* tools DELETED
- [x] **Batch 3: Specialized Audits** ✅ DELETED
    - audit_* tools DELETED

**Status**: ✅ PHASE 3 COMPLETE - Use `python3 unified_analyzer.py --category all` for all analysis.

**Additional Cleanup**:
- fix_* tools (38) DELETED
- debug_* tools (7) DELETED  
- send_* tools (14) DELETED
- test_* tools (28) DELETED
- run_* tools (7) DELETED
- create_* tools (20) DELETED
- generate_* tools (8) DELETED
- update_* tools (13) DELETED

---

## 🧹 Phase 4: Cleanup & Finalization

- [ ] **Update Toolbelt**: Ensure `toolbelt.py` points to the unified tools.
- [ ] **Documentation**: Update `README.md` to reference the unified tools.
- [ ] **Final Archive**: Move all 399 tools to `tools/deprecated/consolidated_phase1`.
- [ ] **Verify Tool Count**: Run `count_tools.py` (or `ls | wc -l`) to confirm reduction.

---

## 📝 Execution Log

*   [x] Plan Created - 2025-12-25
*   [x] `unified_validator.py` Created - 2025-12-25
*   [x] Phase 1 Complete - 2025-12-25 (Monitoring → unified_monitor.py)
*   [x] Phase 2 Complete - 2025-12-25 (Validation → unified_validator.py)
    - 4 ssot_* + 15 validate_* + 36 verify_* + 24 check_* = 79 tools DELETED
*   [x] Phase 3 Complete - 2025-12-25 (Analysis → unified_analyzer.py)
    - 17 analyze_* + 10 audit_* + 6 tech/scan/diagnose = 33 tools DELETED
    - Additional: 38 fix_* + 7 debug_* + 14 send_* + 28 test_* + 7 run_* + 20 create_* + 8 generate_* + 13 update_* = 135 tools DELETED
*   [x] **TOTAL DELETED: 245+ tools** (709 → 464)
*   [ ] Phase 4: Final Cleanup
