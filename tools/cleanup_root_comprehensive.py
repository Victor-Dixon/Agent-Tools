#!/usr/bin/env python3
"""
Comprehensive Root Directory Cleanup
====================================

Moves all non-essential files from root to appropriate directories.

Author: Agent-1
Date: 2025-12-14
"""

import shutil
from pathlib import Path
from datetime import datetime

# Essential files to KEEP in root
ESSENTIAL_FILES = {
    # Documentation
    "README.md",
    "CHANGELOG.md",
    "STANDARDS.md",
    "AGENTS.md",
    # Config files
    ".gitignore",
    ".env",
    "env.example",
    "requirements.txt",
    "requirements-dev.txt",
    "package.json",
    "package-lock.json",
    "pyproject.toml",
    "jest.config.js",
    "Makefile",
    "importlinter.ini",
    ".eslintrc.cjs",
    ".pre-commit-config.yaml",
    ".pre-commit-config-windows.yaml",
    ".pre-commit-config-optimized.yaml",
    ".coverage",
    ".auditignore",
    # Core Python files
    "__init__.py",
    "conftest.py",
    "config.py",
}

# Files to move to archive (old reports, validations, temp files)
FILES_TO_ARCHIVE = [
    # Temp Python scripts
    "temp_send_4agent_mode_tasks.py",
    "temp_send_downsize_notifications.py",
    "temp_send_loop_closure_tasks.py",
    "temp_unblock_agent1_refactors.py",
    "temp_update_agent4_status_expanded_duties.py",
    # Temp other files
    "temp_functions.php",
    "temp_inventory.json",
    "temp_onboarding_sample.txt",
    "temp_style.css",
    "temp_v2_violations.txt",
    # Validation/test output files
    "PYTEST_DEBUGGING_COMPLETE_SUMMARY.txt",
    "pytest_debugging_validation_2025-12-10.txt",
    "validation_results_2025-12-12.txt",
    "validation_results.xml",
    "validation_run_2025-12-12_15-13.txt",
    "validation_run_2025-12-12_17-44.txt",
    "validation_run_2025-12-12_19-23.txt",
    "validation_run_2025-12-13_01-01.txt",
    "validation_run_2025-12-13_03-02.txt",
    # Report JSON files
    "import_errors_report.json",
    "import_errors_report_v2.json",
    "import_errors_report_updated.json",
    "integration_issues_report.json",
    "integration_issues_report.txt",
    "test_analysis.json",
    "test_coverage_prioritization.json",
    "test_results.json",
    "type_imports_report.json",
    "project_analysis.json",
    "project_dashboard_metrics.json",
    "project_dashboard_summary.csv",
    "dashboard_metrics.json",
    "dashboard_summary.csv",
    # Log files
    "twitch_bot_output.log",
    "twitch_diagnostics.log",
    "webcam_app.log",
    # Utility scripts (move to scripts/)
    "agent_devlog_watcher.py",
    "agent1_response.py",
    "assignment_confirmation.py",
    "check_activation_messages.py",
    "check_queue_status.py",
    "check_recent_activations.py",
    "final_status_check.py",
    "find_agent8_message.py",
    "hard_onboard_agent4.py",
    "onboard_survey_agents.py",
    "pyautogui_training_broadcast.py",
    "respond_to_agent6.py",
    "response_detector.py",
    "simple_agent_onboarding.py",
    "swarm_workspace_broadcast.py",
    "test_template_logging.py",
    "update_repo_descriptions.py",
    # PowerShell cleanup scripts (move to scripts/)
    "cleanup_c_drive.ps1",
    "cleanup_perfectmemory.ps1",
    "cleanup_programs_folder.ps1",
    # Config JSON files (move to config/ or archive)
    "agent_mode_config.json",
    "chatgpt_project_context.json",
    "config.json",
    "coverage_config_ssot.json",
    "coverage.json",
    "cursor_agent_coords.json",
    "deferred_push_queue.json",
    "dependency_cache.json",
    "dream_os_ci_diagnostic.json",
    "github_sandbox_mode.json",
    "manager_files_list.txt",
    "passdown.json",
    "swarm_profile.json",
    "thea_cookies.json",
    "tools_consolidation_tasks.csv",
    "tools_inventory.txt",
    # Broken/weird files
    "itory",
    "olved all linting errors",
    "t status",
    "tatus --short 2>&1 | Select-Object -First 10",
    "rc.services.messaging_cli --bulk --message [BROADCAST] All Agents - Break Acknowledgment Loop",
    "ults",
]

def main():
    """Main execution."""
    root = Path(".")
    archive_dir = Path("docs/archive/root_cleanup_2025-12-14")
    scripts_dir = Path("scripts/root_cleanup")
    logs_dir = Path("logs/root_cleanup")
    
    archive_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    moved_to_archive = 0
    moved_to_scripts = 0
    moved_to_logs = 0
    deleted = 0
    not_found = 0
    
    print("=" * 60)
    print("COMPREHENSIVE ROOT DIRECTORY CLEANUP")
    print("=" * 60)
    print()
    
    # Utility scripts go to scripts/
    scripts = [
        "agent_devlog_watcher.py",
        "agent1_response.py",
        "assignment_confirmation.py",
        "check_activation_messages.py",
        "check_queue_status.py",
        "check_recent_activations.py",
        "final_status_check.py",
        "find_agent8_message.py",
        "hard_onboard_agent4.py",
        "onboard_survey_agents.py",
        "pyautogui_training_broadcast.py",
        "respond_to_agent6.py",
        "response_detector.py",
        "simple_agent_onboarding.py",
        "swarm_workspace_broadcast.py",
        "test_template_logging.py",
        "update_repo_descriptions.py",
        "cleanup_c_drive.ps1",
        "cleanup_perfectmemory.ps1",
        "cleanup_programs_folder.ps1",
    ]
    
    # Log files go to logs/
    log_files = [
        "twitch_bot_output.log",
        "twitch_diagnostics.log",
        "webcam_app.log",
    ]
    
    # Broken files get deleted
    broken_files = [
        "itory",
        "olved all linting errors",
        "t status",
        "tatus --short 2>&1 | Select-Object -First 10",
        "rc.services.messaging_cli --bulk --message [BROADCAST] All Agents - Break Acknowledgment Loop",
        "ults",
    ]
    
    # Process scripts
    for filename in scripts:
        file_path = root / filename
        if file_path.exists():
            try:
                dest_path = scripts_dir / filename
                shutil.move(str(file_path), str(dest_path))
                moved_to_scripts += 1
                print(f"✅ MOVED TO SCRIPTS: {filename}")
            except Exception as e:
                print(f"❌ ERROR moving {filename}: {e}")
    
    # Process log files
    for filename in log_files:
        file_path = root / filename
        if file_path.exists():
            try:
                dest_path = logs_dir / filename
                shutil.move(str(file_path), str(dest_path))
                moved_to_logs += 1
                print(f"✅ MOVED TO LOGS: {filename}")
            except Exception as e:
                print(f"❌ ERROR moving {filename}: {e}")
    
    # Process broken files (delete)
    for filename in broken_files:
        file_path = root / filename
        if file_path.exists():
            try:
                file_path.unlink()
                deleted += 1
                print(f"🗑️  DELETED (broken): {filename}")
            except Exception as e:
                print(f"❌ ERROR deleting {filename}: {e}")
    
    # Process all other files to archive
    for filename in FILES_TO_ARCHIVE:
        if filename in scripts or filename in log_files or filename in broken_files:
            continue
            
        file_path = root / filename
        
        if not file_path.exists():
            not_found += 1
            continue
        
        if filename in ESSENTIAL_FILES:
            continue
        
        try:
            dest_path = archive_dir / filename
            shutil.move(str(file_path), str(dest_path))
            moved_to_archive += 1
            print(f"✅ MOVED TO ARCHIVE: {filename}")
        except Exception as e:
            print(f"❌ ERROR moving {filename}: {e}")
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files moved to scripts/: {moved_to_scripts}")
    print(f"Files moved to logs/: {moved_to_logs}")
    print(f"Files moved to archive: {moved_to_archive}")
    print(f"Broken files deleted: {deleted}")
    print(f"Files not found: {not_found}")
    print()
    
    # Count remaining files
    remaining_files = [f for f in root.iterdir() if f.is_file() and f.name not in ESSENTIAL_FILES]
    
    print("=" * 60)
    print("REMAINING FILES IN ROOT")
    print("=" * 60)
    print(f"Essential files: {len(ESSENTIAL_FILES)}")
    print(f"Other files: {len(remaining_files)}")
    
    if remaining_files:
        print()
        print("⚠️  Additional files still in root:")
        for f in sorted(remaining_files):
            print(f"  - {f.name}")
        print()

if __name__ == "__main__":
    main()

