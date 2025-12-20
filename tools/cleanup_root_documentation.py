#!/usr/bin/env python3
"""
Cleanup Root Directory Documentation
====================================

Moves outdated documentation files from root to archive directory.

Author: Agent-1
Date: 2025-12-14
"""

import shutil
from pathlib import Path
from datetime import datetime

# Essential files to KEEP in root
ESSENTIAL_FILES = {
    "README.md",
    "CHANGELOG.md",
    "STANDARDS.md",
    "AGENTS.md",
}

# Files to archive (old reports, validations, summaries)
FILES_TO_ARCHIVE = [
    # 2025-12-10 files
    "VALIDATION_2025-12-10.txt",
    "VALIDATION_COMPLETE_2025-12-10.txt",
    "VALIDATION_RESULT_2025-12-10.txt",
    "PYTEST_DEBUGGING_VALIDATION_REPORT_2025-12-10.md",
    "PYTEST_DEBUGGING_DELTA_2025-12-10.md",
    "PYTEST_FIXES_2025-12-10.md",
    "PYTEST_FIXES_COMMIT_2025-12-10.md",
    "PYTEST_FIXES_SUMMARY_2025-12-10.txt",
    "PYTEST_FIXES_VALIDATION_RESULT.txt",
    "FIXES_VERIFIED_2025-12-10.md",
    "COMMIT_INSTRUCTIONS_2025-12-10.md",
    "COMMIT_READY_2025-12-10.txt",
    "FINAL_DELTA_REPORT_2025-12-10.txt",
    "FINAL_SESSION_SUMMARY.md",
    "STALL_RECOVERY_COMPLETE_2025-12-10.md",
    "STALL_RECOVERY_ARTIFACT_2025-12-10.md",
    "WORK_COMPLETE_2025-12-10.txt",
    # 2025-12-11 files
    "AGENT_ACTIVITY_VALIDATION_2025-12-11.md",
    "AGENT7_SESSION_SUMMARY_2025-12-11.md",
    "AGENT8_SSOT_COORDINATION_COMPLETE_SUMMARY_2025-12-11.md",
    "CRITICAL_INFRASTRUCTURE_HEALTH_VALIDATION.md",
    "CUMULATIVE_PROGRESS_REPORT.md",
    "DISK_SPACE_CLEANUP_REPORT.md",
    "DISK_SPACE_VALIDATION_2025-12-11.md",
    "HANDLER_SERVICE_BOUNDARY_VERIFICATION_2025-12-11.md",
    "INFRASTRUCTURE_CRISIS_SUMMARY_2025-12-11.md",
    "INFRASTRUCTURE_HEALTH_VALIDATION_2025-12-11.md",
    "INFRASTRUCTURE_VALIDATION_2025-12-11.md",
    "PRE_PUBLIC_PUSH_AUDIT_2025-12-11.md",
    "PROOF_LEDGER_FIX_ATTEMPT_2025-12-11.md",
    "PROOF_LEDGER_TEST_FIX_2025-12-11.md",
    "PROOF_LEDGER_TEST_STATUS_2025-12-11.md",
    "REPOSITORY_CLEANUP_SSOT_COORDINATION_RESPONSE_2025-12-11.md",
    "REPOSITORY_CLEANUP_SSOT_VALIDATION_2025-12-11.md",
    "REPOSITORY_CLEANUP_SSOT_WORK_SUMMARY_2025-12-11.md",
    "REPOSITORY_STATE_DELTA_REPORT_2025-12-11.md",
    "RESUME_SYSTEM_CRISIS_REPORT.md",
    "RESUME_SYSTEM_FIX_IMPLEMENTATION.md",
    "RESUME_SYSTEM_HARDENING_COMPLETE_2025-12-11.md",
    "RESUME_SYSTEM_HARDENING_FIXES_2025-12-12.md",
    "RESUME_SYSTEM_HARDENING_SUMMARY.md",
    "RESUME_SYSTEM_IMPROVEMENT_ANALYSIS.md",
    "RESUME_SYSTEM_INVESTIGATION_SUMMARY.md",
    "RESUME_SYSTEM_SWARM_DELEGATION.md",
    "SSOT_COMPLIANCE_VALIDATION_2025-12-11.md",
    "SSOT_DOCUMENTATION_MIGRATION_PLAN_2025-12-11.md",
    "SSOT_MIGRATION_DELEGATION_2025-12-11.md",
    "SSOT_MIGRATION_VALIDATION_REPORT_2025-12-11.md",
    "SSOT_PRESERVATION_VALIDATION_RESULT_2025-12-11.md",
    "SSOT_PRESERVATION_VALIDATION_TEST_2025-12-11.md",
    "STALL_DETECTION_ADDITIONAL_IMPROVEMENTS_2025-12-11.md",
    "STALL_DETECTION_COMPREHENSIVE_UPDATE_2025-12-11.md",
    "STALL_DETECTION_IMPLEMENTATION_STATUS_2025-12-11.md",
    "STALL_DETECTION_IMPROVEMENT_ANALYSIS_2025-12-11.md",
    "STALL_DETECTION_VALIDATION_REPORT_2025-12-11.md",
    "SWARM_COORDINATION_PROGRESS_REPORT.md",
    "SWARM_COORDINATION_VALIDATION_2025-12-11.md",
    "TEST_VALIDATION_REPORT_2025-12-11.md",
    "THEME_ASSET_VERIFICATION_REPORT_2025-12-11.md",
    "UNIFIED_TOOLS_WEB_INTEGRATION_STATUS_REPORT_2025-12-11.md",
    # Website audit files
    "WEBSITE_AUDIT_COMPLETE_2025-12-11.md",
    "WEBSITE_AUDIT_COMPREHENSIVE_20251210_191219.md",
    "WEBSITE_AUDIT_COMPREHENSIVE_20251210_191344.md",
    "WEBSITE_AUDIT_COMPREHENSIVE_20251210_202948.md",
    "WEBSITE_AUDIT_COMPREHENSIVE_20251211_045751.md",
    "WEBSITE_AUDIT_COMPREHENSIVE_WITH_PURPOSES_AND_AUTOMATION_2025-12-11.md",
    "WEBSITE_AUDIT_FINAL_2025-12-11.txt",
    "WEBSITE_AUDIT_REPORT_2025-12-10.md",
    "WEBSITE_AUDIT_SUMMARY_2025-12-10.txt",
    "WEBSITE_AUDIT_VALIDATION_2025-12-11.md",
    "WEBSITE_AUDIT_VALIDATION_2025-12-11.txt",
    "WEBSITE_TECHNICAL_AUDIT_2025-12-10.md",
    # Other reports
    "CI_CD_FIXES_COMPLETE.md",
    "CI_CD_FIXES_SUMMARY.md",
    "DISCORD_COMMANDER_REVIEW.md",
    "FIX_QUEUE_PROCESSOR.md",
    "GITHUB_MERMAID_AUTONOMOUS_STATUS.md",
    "GITHUB_MERMAID_FOCUS_PLAN.md",
    "GITHUB_MERMAID_PROGRESS_REPORT.md",
    "INTEGRATION_READINESS_BATCH10.md",
    "PRE_PUBLIC_AUDIT_AGENT8_REPORT.md",
    "PUSH_TO_DREAM_OS_INSTRUCTIONS.md",
    "QUEUE_FIX_SUMMARY.md",
    "SESSION_TRANSITION_COMPLETE.md",
    "SFTP_VALIDATION_FINAL_REPORT.md",
    "STATE_OF_THE_PROJECT_REPORT.md",
    "SWARM_SYSTEM_CATALOG.md",
    "WORDPRESS_DEPLOYMENT_INFRASTRUCTURE_VALIDATION.md",
    "WORDPRESS_INFRASTRUCTURE_DELTA_REPORT.md",
    # Temporary files
    "temp_onboarding_preview.md",
    "DELETION_CANDIDATES_EASY.txt",
    "DELETION_CANDIDATES_MORE.txt",
    # Additional analysis reports
    "duplicate_analysis_Auto_Blogger.md",
    "duplicate_analysis_Dadudekc_Auto_Blogger.md",
    "duplicate_analysis_Dadudekc_trading-leads-bot.md",
    "github_rate_limits_report.md",
    "integration_health_report.md",
    "systems_inventory_report.md",
    "test_coverage_prioritization_report.md",
    "unneeded_functionality_report.md",
    "ULTIMATE_SYSTEM_FAILURE_ANALYSIS.md",
    "REPOSITORY_DESCRIPTIONS.md",
]

def main():
    """Main execution."""
    root = Path(".")
    archive_dir = Path("docs/archive/root_cleanup_2025-12-14")
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    moved_count = 0
    not_found_count = 0
    skipped_count = 0
    
    print("=" * 60)
    print("ROOT DIRECTORY DOCUMENTATION CLEANUP")
    print("=" * 60)
    print()
    
    for filename in FILES_TO_ARCHIVE:
        file_path = root / filename
        
        if not file_path.exists():
            not_found_count += 1
            continue
        
        if filename in ESSENTIAL_FILES:
            skipped_count += 1
            print(f"⚠️  SKIPPED (essential): {filename}")
            continue
        
        try:
            dest_path = archive_dir / filename
            shutil.move(str(file_path), str(dest_path))
            moved_count += 1
            print(f"✅ MOVED: {filename}")
        except Exception as e:
            print(f"❌ ERROR moving {filename}: {e}")
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files moved to archive: {moved_count}")
    print(f"Files not found: {not_found_count}")
    print(f"Files skipped (essential): {skipped_count}")
    print(f"Archive location: {archive_dir}")
    print()
    
    # Count remaining .md files in root
    remaining_md = list(root.glob("*.md"))
    remaining_txt = list(root.glob("*.txt"))
    essential_remaining = [f for f in remaining_md if f.name in ESSENTIAL_FILES]
    
    print("=" * 60)
    print("REMAINING FILES IN ROOT")
    print("=" * 60)
    print(f"Essential .md files: {len(essential_remaining)}")
    print(f"Other .md files: {len(remaining_md) - len(essential_remaining)}")
    print(f"Other .txt files: {len(remaining_txt)}")
    print()
    
    if len(remaining_md) - len(essential_remaining) > 0:
        print("⚠️  Additional .md files still in root:")
        for f in remaining_md:
            if f.name not in ESSENTIAL_FILES:
                print(f"  - {f.name}")
        print()

if __name__ == "__main__":
    main()

