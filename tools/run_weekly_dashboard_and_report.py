#!/usr/bin/env python3
"""
Weekly dashboard + metrics + report runner (with cycle planner hook).

Chain:
- project_metrics_to_spreadsheet.py (dashboard + tasks)
- systems/output_flywheel/metrics_client.py (export unified metrics if available)
- systems/output_flywheel/weekly_report_generator.py (weekly report)
- Optionally writes a cycle planner contract to review the outputs.

Scheduling:
- Use --schedule-weekly to emit a PowerShell script for Windows Task Scheduler.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from systems.output_flywheel.metrics_client import MetricsClient
from systems.output_flywheel.weekly_report_generator import WeeklyReportGenerator


def compute_week_start(week_start_str: Optional[str] = None) -> datetime:
    """Return Monday 00:00 of the requested or current week."""
    if week_start_str:
        dt = datetime.fromisoformat(week_start_str)
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def run_dashboard() -> tuple[bool, str, str]:
    """Run dashboard generation."""
    script = PROJECT_ROOT / "tools" / "project_metrics_to_spreadsheet.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    return result.returncode == 0, result.stdout, result.stderr


def refresh_unified_metrics(client: MetricsClient) -> Optional[Path]:
    """Export unified metrics if exporter is available."""
    try:
        return client.export_fresh_unified_metrics()
    except Exception:
        return None


def generate_weekly_report(week_start: datetime) -> Path:
    """Generate weekly report and return its path."""
    generator = WeeklyReportGenerator()
    generator.generate_weekly_report(week_start=week_start)
    filename = f"weekly_report_{week_start.strftime('%Y-%m-%d')}.md"
    return generator.reports_dir / filename


def update_cycle_planner(
    agent_id: str, week_start: datetime, report_path: Path, dashboard_path: Path
) -> Path:
    """Append a review contract to cycle planner for the agent."""
    planner_dir = (
        PROJECT_ROOT / "agent_workspaces" / "swarm_cycle_planner" / "cycles"
    )
    planner_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().date().isoformat()
    filename = f"{today}_{agent_id.lower()}_pending_tasks.json"
    planner_file = planner_dir / filename

    data: dict[str, object] = {
        "cycle_id": today,
        "agent_id": agent_id,
        "created_date": today,
        "contracts": [],
        "notes": "Auto-generated weekly report review",
    }

    if planner_file.exists():
        try:
            data = json.loads(planner_file.read_text(encoding="utf-8"))
        except Exception:
            pass

    contracts = data.get("contracts") or []
    contract_id = f"WEEKLY-REPORT-{week_start.strftime('%Y%m%d')}"
    already_present = any(
        c.get("contract_id") == contract_id for c in contracts if isinstance(c, dict)
    )
    if not already_present:
        contracts.append(
            {
                "contract_id": contract_id,
                "title": "Review weekly dashboard + report",
                "description": (
                    f"Review weekly report ({report_path}) and dashboard "
                    f"({dashboard_path}). Post Discord summary + update status."
                ),
                "priority": "MEDIUM",
                "points": 100,
                "status": "READY",
                "agent_assigned": agent_id,
            }
        )
    data["contracts"] = contracts

    planner_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return planner_file


def schedule_weekly_task(agent_id: str, time_str: str, day: str) -> None:
    """Emit a PowerShell script to create a weekly scheduled task."""
    if sys.platform != "win32":
        print("📋 On non-Windows, add a weekly cron pointing to this script.")
        return

    script_path = PROJECT_ROOT / "tools" / "run_weekly_dashboard_and_report.py"
    python_exe = sys.executable
    ps_script = f"""
# Schedule Weekly Flywheel Report
$action = New-ScheduledTaskAction -Execute '{python_exe}' -Argument '"{script_path}" --agent {agent_id}' -WorkingDirectory '{PROJECT_ROOT}'
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek {day} -At {time_str}
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "WeeklyFlywheelReport" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Weekly dashboard + metrics + report + cycle planner"

Write-Host "✅ Scheduled task created:"
Write-Host "   - WeeklyFlywheelReport ({day} at {time_str})"
"""
    ps_file = PROJECT_ROOT / "tools" / "schedule_weekly_flywheel.ps1"
    ps_file.write_text(ps_script, encoding="utf-8")
    print("🔧 To create the weekly task (run as Administrator):")
    print(f"   powershell -ExecutionPolicy Bypass -File {ps_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Run dashboard + unified metrics + weekly report, with cycle planner hook"
    )
    parser.add_argument("--agent", default="Agent-4", help="Agent to receive cycle planner contract")
    parser.add_argument("--week-start", help="ISO date for week start (defaults to current Monday)")
    parser.add_argument(
        "--no-cycle-planner",
        action="store_true",
        help="Skip writing cycle planner contract",
    )
    parser.add_argument(
        "--schedule-weekly",
        action="store_true",
        help="Emit a PowerShell script to schedule weekly run (Windows)",
    )
    parser.add_argument(
        "--time",
        default="3:30AM",
        help="Weekly run time for scheduler (Windows format, default 3:30AM Sunday)",
    )
    parser.add_argument(
        "--day",
        default="Sunday",
        help="Day of week for scheduler (Sunday|Monday|...)",
    )

    args = parser.parse_args()

    if args.schedule_weekly:
        schedule_weekly_task(args.agent, args.time, args.day)
        return

    week_start = compute_week_start(args.week_start)
    metrics_client = MetricsClient()

    dash_ok, dash_out, dash_err = run_dashboard()
    unified_path = refresh_unified_metrics(metrics_client)
    report_path = generate_weekly_report(week_start)
    dashboard_summary = PROJECT_ROOT / "dashboard_summary.csv"

    cycle_path = None
    if not args.no_cycle_planner:
        cycle_path = update_cycle_planner(
            agent_id=args.agent,
            week_start=week_start,
            report_path=report_path,
            dashboard_path=dashboard_summary,
        )

    print("✅ Weekly chain completed.")
    print(f"   Dashboard: {'ok' if dash_ok else 'failed'}")
    if dash_err.strip():
        print(f"   Dashboard stderr: {dash_err.strip()}")
    if unified_path:
        print(f"   Unified metrics exported: {unified_path}")
    else:
        print("   Unified metrics: exporter not available or skipped")
    print(f"   Weekly report: {report_path}")
    if cycle_path:
        print(f"   Cycle planner contract: {cycle_path}")


if __name__ == "__main__":
    main()

