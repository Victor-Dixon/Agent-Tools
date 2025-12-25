# 🗺️ Master Plan: Tools Consolidation Phase 1

**Goal**: Consolidate 399 specialized tools into 3 unified systems (`unified_monitor`, `unified_validator`, `unified_analyzer`), reducing tool count by ~56%.

**Strategy**: "Consolidate, Verify, Archive".
We will move functionality into the unified tools, verify they work, and then archive the old tools.

---

## 🏗️ Preparation Phase

- [ ] **Create `unified_validator.py`**: This tool is currently missing. We need to create it to handle verification, SSOT checks, and config validation.
- [ ] **Verify `unified_monitor.py`**: Ensure it can handle the load and logic of the top monitoring candidates.
- [ ] **Verify `unified_analyzer.py`**: Ensure it handles the logic of top analysis candidates.
- [ ] **Create Archival Directory**: Ensure `tools/deprecated/consolidated_phase1` exists.

---

## 🚀 Phase 1: Monitoring Consolidation (108 candidates)

**Target Tool**: `unified_monitor.py`

- [ ] **Batch 1: Status & Health Checks**
    - Consolidate `captain_check_agent_status.py`
    - Consolidate `workspace_health_monitor.py`
    - Consolidate `monitor_service_health` tools
- [ ] **Batch 2: Queue & Infrastructure**
    - Consolidate `discord_bot_infrastructure_check.py`
    - Consolidate `debug_message_queue.py` logic
- [ ] **Batch 3: Recovery Triggers**
    - Consolidate `manually_trigger_status_monitor_resume.py`
    - Consolidate `status_monitor_recovery_trigger.py`

**Action**: Move logic to `unified_monitor.py`, verify `python3 unified_monitor.py --category all` works, then move original scripts to deprecated.

---

## 🛡️ Phase 2: Validation Consolidation (73 candidates)

**Target Tool**: `unified_validator.py`

- [ ] **Batch 1: SSOT & Config**
    - Consolidate `ssot_config_validator.py`
    - Consolidate `validate_trackers.py`
- [ ] **Batch 2: Code & Imports**
    - Consolidate `validate_imports.py`
    - Consolidate `check_active_theme_and_deploy_css.py` (validation parts)
- [ ] **Batch 3: System Verification**
    - Consolidate `verify_file_usage_enhanced.py`
    - Consolidate `check_system_readiness.py`

**Action**: Implement checks in `unified_validator.py`, verify, archive.

---

## 🧠 Phase 3: Analysis Consolidation (218 candidates)

**Target Tool**: `unified_analyzer.py`

- [ ] **Batch 1: Reporting & Metrics**
    - Consolidate `tech_debt_ci_summary.py`
    - Consolidate `generate_weekly_progression_report.py`
- [ ] **Batch 2: Codebase Scanning**
    - Consolidate `projectscanner_modular_reports.py`
    - Consolidate `analyze_project_structure.py` logic
- [ ] **Batch 3: Specialized Audits**
    - Consolidate `audit_wordpress_blogs.py`
    - Consolidate `analyze_documentation_sprawl.py`

**Action**: Implement analyzers in `unified_analyzer.py`, verify, archive.

---

## 🧹 Phase 4: Cleanup & Finalization

- [ ] **Update Toolbelt**: Ensure `toolbelt.py` points to the unified tools.
- [ ] **Documentation**: Update `README.md` to reference the unified tools.
- [ ] **Final Archive**: Move all 399 tools to `tools/deprecated/consolidated_phase1`.
- [ ] **Verify Tool Count**: Run `count_tools.py` (or `ls | wc -l`) to confirm reduction.

---

## 📝 Execution Log

*   [ ] Plan Created
*   [ ] `unified_validator.py` Created
*   [ ] Phase 1 Started
*   [ ] Phase 1 Complete
*   [ ] Phase 2 Started
*   [ ] Phase 2 Complete
*   [ ] Phase 3 Started
*   [ ] Phase 3 Complete
*   [ ] Cleanup Complete
