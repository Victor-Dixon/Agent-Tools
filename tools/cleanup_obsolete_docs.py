#!/usr/bin/env python3
"""
Cleanup Obsolete Documentation
================================

Removes obsolete documentation files based on deletion list.
"""

import os
from pathlib import Path

# Files to delete from OUTDATED_DOCS_DELETION_LIST.md
FILES_TO_DELETE = [
    # Batch execution logs
    "docs/organization/BATCH1_FINAL_STATUS.md",
    "docs/organization/BATCH1_COMPLETION_MILESTONE.md",
    "docs/organization/BATCH1_COMPLETION_VERIFICATION.md",
    "docs/organization/BATCH1_COMPLETE_CLARIFICATION.md",
    "docs/organization/BATCH1_STATUS_SUMMARY.md",
    "docs/organization/BATCH1_VERIFICATION_COMPLETE.md",
    "docs/organization/BATCH1_VERIFICATION_FINAL_REPORT.md",
    "docs/organization/BATCH1_VERIFICATION_SUMMARY.md",
    "docs/organization/BATCH2_COMPLETION_STATUS.md",
    "docs/organization/BATCH2_EXECUTION_ISSUES.md",
    "docs/organization/BATCH2_CRITICAL_BLOCKER.md",
    "docs/organization/BATCH2_CONFLICTS_RE_EVALUATION.md",
    "docs/organization/BATCH2_EXACT_COUNT_CONFIRMATION.md",
    "docs/organization/BATCH2_COMPLETE_STRUCTURE.md",
    "docs/organization/BATCH2_SUBBATCH_VERIFICATION.md",
    "docs/organization/BATCH2_CLEAN_STATE_VERIFICATION.md",
    "docs/organization/BATCH2_READINESS_VERIFICATION.md",
    "docs/organization/BATCH2_FINAL_VERIFICATION_REPORT.md",
    "docs/organization/BATCH2_SSOT_UPDATE_CHECKLIST.md",
    "docs/organization/BATCH2_COMPLETION_CRITERIA.md",
    
    # Phase 1 execution logs
    "docs/organization/PHASE1_BATCH1_EXECUTION_LOG.md",
    "docs/organization/PHASE1_BATCH2_EXECUTION_LOG.md",
    "docs/organization/PHASE1_COMPLETION_MILESTONE.md",
    "docs/organization/PHASE1_FINAL_STATUS.md",
    "docs/organization/PHASE1_MERGE_DETAILS.md",
    "docs/organization/PHASE1_METRICS_DASHBOARD.md",
    "docs/organization/PHASE1_EXECUTION_TRACKING.md",
    "docs/organization/PHASE1_BATCH1_COORDINATION_CHECKLIST.md",
    "docs/organization/PHASE1_BATCH1_MANUAL_EXECUTION_GUIDE.md",
    "docs/organization/PHASE1_BATCH2_PREPARATION.md",
    "docs/organization/PHASE1_DETAILED_APPROVAL_EXPLANATION.md",
    "docs/organization/PHASE1_MULTI_AGENT_COORDINATION_PLAN.md",
    
    # Merge verification
    "docs/organization/MERGE_VERIFICATION_PLAN.md",
    "docs/organization/MERGE_VERIFICATION_RESULTS.md",
    "docs/organization/MERGE1_CONFLICT_RESOLUTION_GUIDE.md",
    "docs/organization/MERGE1_STATUS_VERIFICATION_REPORT.md",
    "docs/organization/MERGE1_COMPLETION_SUMMARY.md",
    "docs/organization/MERGE1_MILESTONE_SUMMARY.md",
    "docs/organization/MERGE1_PROGRESS_UPDATE.md",
    "docs/organization/MERGE_2_REPOSITORY_NOT_FOUND.md",
    "docs/organization/MERGED_REPOS_CI_CD_STATUS.md",
    "docs/organization/MERGED_REPOS_CI_CD_VERIFICATION_GUIDE.md",
    
    # Authentication & troubleshooting (resolved)
    "docs/organization/AUTHENTICATION_BLOCKER_RESOLUTION.md",
    "docs/organization/AUTHENTICATION_DIAGNOSTIC_CHECKLIST.md",
    "docs/organization/GITHUB_AUTHENTICATION_STEPS.md",
    "docs/organization/GITHUB_CLI_AUTHENTICATION_STATUS.md",
    "docs/organization/MERGE_TOOL_TROUBLESHOOTING.md",
    "docs/organization/EXECUTION_BLOCKER_ANALYSIS.md",
    
    # Disk space (resolved)
    "docs/organization/DISK_SPACE_BLOCKER.md",
    "docs/organization/DISK_SPACE_COORDINATION.md",
    "docs/organization/DISK_SPACE_RESOLUTION.md",
    "docs/organization/DISK_SPACE_RESOLUTION_OPTIONS.md",
    "docs/organization/D_TEMP_REPO_CACHE_POLICY.md",
    
    # Old approvals
    "docs/organization/PHASE1_EXECUTION_APPROVAL.md",
    "docs/organization/PHASE1_CONSOLIDATION_APPROVAL.md",
    "docs/organization/PR_CREATION_RESOLUTION.md",
    "docs/organization/GITHUB_MERGE_TOOL_EXPANSION.md",
    "docs/organization/MERGE_EXECUTION_QUICK_START.md",
    "docs/organization/GITHUB_TOOLS_REVIEW.md",
    
    # Old coordination (superseded)
    "docs/organization/REPO_CONSOLIDATION_STATUS.md",
    "docs/organization/REPO_CONSOLIDATION_COORDINATION.md",
    "docs/organization/MASTER_CONSOLIDATION_PLAN.md",
    "docs/organization/GITHUB_REPO_CONSOLIDATION_PLAN.md",
    "docs/organization/PHASE1_AGENT_ASSIGNMENTS.md",
    "docs/organization/PENDING_TASKS_CYCLE_PLANNER.md",
    "docs/organization/COMPREHENSIVE_TASK_BREAKDOWN_2025-11-22.md",
    "docs/organization/COORDINATION_SUMMARY_2025-11-22.md",
    "docs/organization/ROOT_ORGANIZATION_PLAN.md",
    "docs/organization/ROOT_ORGANIZATION_COMPLETE.md",
    "docs/organization/SESSION_TRANSITION_COMPLETE.md",
    "docs/organization/DISCORD_APPROVAL_GUIDE.md",
]

def main():
    """Delete obsolete documentation files."""
    project_root = Path(__file__).parent.parent
    deleted = []
    not_found = []
    
    print("🗑️  Cleaning up obsolete documentation...\n")
    
    for file_path in FILES_TO_DELETE:
        full_path = project_root / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                deleted.append(file_path)
                print(f"✅ Deleted: {file_path}")
            except Exception as e:
                print(f"❌ Error deleting {file_path}: {e}")
        else:
            not_found.append(file_path)
    
    print(f"\n📊 Summary:")
    print(f"   Deleted: {len(deleted)} files")
    print(f"   Not found: {len(not_found)} files")
    
    if not_found:
        print(f"\n⚠️  Files not found (may already be deleted):")
        for f in not_found[:10]:  # Show first 10
            print(f"   - {f}")
        if len(not_found) > 10:
            print(f"   ... and {len(not_found) - 10} more")

if __name__ == "__main__":
    main()



