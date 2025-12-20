#!/usr/bin/env python3
"""
Schedule Dashboard Updates (Daily)
==================================

Schedules project metrics dashboard updates to run daily (e.g., 3:15 AM):
- Generates dashboard_summary.csv
- Generates dashboard_tasks.csv
- Includes Debate + Cycle V2 tasks

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-12-08
V2 Compliant: Yes
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def schedule_with_task_scheduler():
    """
    Schedule dashboard updates using Windows Task Scheduler (Windows).
    
    Creates a scheduled task:
    - Dashboard update: 3:15 AM daily
    """
    script_path = PROJECT_ROOT / "tools" / "project_metrics_to_spreadsheet.py"
    python_exe = sys.executable
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return False
    
    # Create PowerShell script to schedule task
    ps_script = f"""
# Schedule Dashboard Update (3:15 AM daily)
$action = New-ScheduledTaskAction -Execute '{python_exe}' -Argument '"{script_path}" --output dashboard.csv' -WorkingDirectory '{PROJECT_ROOT}'
$trigger = New-ScheduledTaskTrigger -Daily -At 3:15AM
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "ProjectDashboardUpdate" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Generate daily project metrics dashboard (Debate + Cycle V2 tasks)"

Write-Host "✅ Scheduled task created:"
Write-Host "   - ProjectDashboardUpdate (3:15 AM daily)"
"""
    
    ps_file = PROJECT_ROOT / "tools" / "schedule_dashboard.ps1"
    ps_file.write_text(ps_script, encoding="utf-8")
    
    print("\n🔧 To schedule dashboard updates, run (as Administrator):")
    print(f"   powershell -ExecutionPolicy Bypass -File {ps_file}")
    
    print("\nOr manually create scheduled task in Task Scheduler:")
    print("   1. Open Task Scheduler")
    print("   2. Create Basic Task")
    print("   3. Name: ProjectDashboardUpdate")
    print("   4. Trigger: Daily at 3:15 AM")
    print("   5. Action: Start a program")
    print(f"   6. Program: {python_exe}")
    print(f"   7. Arguments: {script_path} --output dashboard.csv")
    print(f"   8. Start in: {PROJECT_ROOT}")
    
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Schedule dashboard updates (daily 3:15 AM)"
    )
    
    args = parser.parse_args()
    
    print("🚀 Setting up daily dashboard updates (3:15 AM)...")
    
    if os.name == "nt":  # Windows
        schedule_with_task_scheduler()
    else:
        print("📋 For Linux/Mac, add to crontab:")
        print("   15 3 * * * cd /path/to/project && python tools/project_metrics_to_spreadsheet.py --output dashboard.csv")
        print("\n   To edit crontab: crontab -e")
    
    print("\n✅ Dashboard updates will generate:")
    print("   - dashboard_summary.csv (project metrics overview)")
    print("   - dashboard_tasks.csv (Debate + Cycle V2 tasks)")
    print("\n📊 Integration flow:")
    print("   Debate → workflow_states/{topic}_execution.json")
    print("   Cycle V2 → agent_workspaces/{agent}/status.json")
    print("   ↓")
    print("   project_metrics_to_spreadsheet.py")
    print("   ↓")
    print("   dashboard_summary.csv + dashboard_tasks.csv")


if __name__ == "__main__":
    main()

