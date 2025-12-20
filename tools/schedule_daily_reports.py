#!/usr/bin/env python3
"""
Schedule Daily Technical Debt Reports (2x Daily)
=================================================

Schedules technical debt reports to run 2x daily:
- Morning: 9:00 AM
- Afternoon: 3:00 PM

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-12-02
Priority: HIGH
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def schedule_with_task_scheduler():
    """
    Schedule reports using Windows Task Scheduler (Windows).
    
    Creates two scheduled tasks:
    - Morning report: 9:00 AM daily
    - Afternoon report: 3:00 PM daily
    """
    script_path = PROJECT_ROOT / "systems" / "technical_debt" / "daily_report_generator.py"
    python_exe = sys.executable
    
    # Create PowerShell script to schedule tasks
    ps_script = f"""
# Schedule Morning Report (9:00 AM daily)
$action1 = New-ScheduledTaskAction -Execute '{python_exe}' -Argument '-m systems.technical_debt.daily_report_generator --time morning --format both'
$trigger1 = New-ScheduledTaskTrigger -Daily -At 9:00AM
$principal1 = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
$settings1 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "TechnicalDebtReport_Morning" -Action $action1 -Trigger $trigger1 -Principal $principal1 -Settings $settings1 -Description "Generate morning technical debt report"

# Schedule Afternoon Report (3:00 PM daily)
$action2 = New-ScheduledTaskAction -Execute '{python_exe}' -Argument '-m systems.technical_debt.daily_report_generator --time afternoon --format both'
$trigger2 = New-ScheduledTaskTrigger -Daily -At 3:00PM
$principal2 = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
$settings2 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "TechnicalDebtReport_Afternoon" -Action $action2 -Trigger $trigger2 -Principal $principal2 -Settings $settings2 -Description "Generate afternoon technical debt report"

Write-Host "✅ Scheduled tasks created:"
Write-Host "   - TechnicalDebtReport_Morning (9:00 AM daily)"
Write-Host "   - TechnicalDebtReport_Afternoon (3:00 PM daily)"
"""
    
    # Save PowerShell script
    ps_file = PROJECT_ROOT / "tools" / "schedule_reports.ps1"
    with open(ps_file, "w", encoding="utf-8") as f:
        f.write(ps_script)
    
    print(f"📋 PowerShell script created: {ps_file}")
    print("\n🔧 To schedule reports, run (as Administrator):")
    print(f"   powershell -ExecutionPolicy Bypass -File {ps_file}")
    print("\nOr manually create scheduled tasks in Task Scheduler:")
    print("   1. Open Task Scheduler")
    print("   2. Create Basic Task")
    print("   3. Name: TechnicalDebtReport_Morning")
    print("   4. Trigger: Daily at 9:00 AM")
    print("   5. Action: Start a program")
    print(f"   6. Program: {python_exe}")
    print(f"   7. Arguments: -m systems.technical_debt.daily_report_generator --time morning --format both")
    print("   8. Repeat for Afternoon (3:00 PM)")


def create_continuous_runner():
    """
    Create a continuous runner script that checks time and generates reports.
    
    This runs as a background service and generates reports at scheduled times.
    """
    morning_hour = 9
    afternoon_hour = 15
    
    runner_script = f"""#!/usr/bin/env python3
\"\"\"
Continuous Daily Report Runner
Runs in background and generates reports at scheduled times.
\"\"\"

import time
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_SCRIPT = PROJECT_ROOT / "systems" / "technical_debt" / "daily_report_generator.py"
PYTHON_EXE = sys.executable

MORNING_HOUR = {morning_hour}
AFTERNOON_HOUR = {afternoon_hour}

last_morning_report = None
last_afternoon_report = None

print("🔄 Starting continuous daily report runner...")
print(f"   Morning reports: {{MORNING_HOUR}}:00")
print(f"   Afternoon reports: {{AFTERNOON_HOUR}}:00")
print("   (Press Ctrl+C to stop)")

while True:
    now = datetime.now()
    current_date = now.date()
    current_hour = now.hour
    
    # Check for morning report (9:00 AM)
    if current_hour == MORNING_HOUR and last_morning_report != current_date:
        print("\\n📊 Generating morning report...")
        try:
            subprocess.run(
                [PYTHON_EXE, str(REPORT_SCRIPT), "--time", "morning", "--format", "both"],
                cwd=PROJECT_ROOT,
                check=True
            )
            last_morning_report = current_date
            print("✅ Morning report generated")
        except Exception as e:
            print(f"❌ Error generating morning report: {{e}}")
    
    # Check for afternoon report (3:00 PM)
    if current_hour == AFTERNOON_HOUR and last_afternoon_report != current_date:
        print("\\n📊 Generating afternoon report...")
        try:
            subprocess.run(
                [PYTHON_EXE, str(REPORT_SCRIPT), "--time", "afternoon", "--format", "both"],
                cwd=PROJECT_ROOT,
                check=True
            )
            last_afternoon_report = current_date
            print("✅ Afternoon report generated")
        except Exception as e:
            print(f"❌ Error generating afternoon report: {{e}}")
    
    # Sleep for 1 minute
    time.sleep(60)
"""
    
    runner_file = PROJECT_ROOT / "tools" / "run_daily_reports_continuous.py"
    with open(runner_file, "w", encoding="utf-8") as f:
        f.write(runner_script)
    
    print(f"\n✅ Continuous runner script created: {runner_file}")
    print("\n🔧 To run continuously (background):")
    print(f"   python {runner_file}")
    print("\nOr run in background:")
    print(f"   python {runner_file} > daily_reports.log 2>&1 &")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Schedule daily technical debt reports (2x daily)"
    )
    parser.add_argument(
        "--method",
        choices=["task_scheduler", "continuous", "both"],
        default="both",
        help="Scheduling method (default: both)"
    )
    
    args = parser.parse_args()
    
    print("📅 Setting up daily technical debt reports (2x daily)...")
    print("   - Morning: 9:00 AM")
    print("   - Afternoon: 3:00 PM")
    print()
    
    if args.method in ["task_scheduler", "both"]:
        schedule_with_task_scheduler()
        print()
    
    if args.method in ["continuous", "both"]:
        create_continuous_runner()
        print()
    
    print("✅ Scheduling setup complete!")
    print("\n📋 Next Steps:")
    print("   1. Choose scheduling method (Task Scheduler or Continuous)")
    print("   2. Run the setup script for your chosen method")
    print("   3. Reports will generate automatically 2x daily")
    print("   4. Auto-task assigner will pick up new reports")
    print("\n🐝 WE. ARE. SWARM. ⚡🔥")


if __name__ == "__main__":
    main()

