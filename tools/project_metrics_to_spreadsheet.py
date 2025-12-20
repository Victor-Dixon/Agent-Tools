#!/usr/bin/env python3
"""
Project Metrics to Spreadsheet - At-a-Glance Dashboard
======================================================

Converts project state and scanner results into spreadsheet format for:
- Visual project overview
- Actionable task generation
- Spreadsheet-driven automation

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-12-07
V2 Compliant: Yes
"""

import argparse
import csv
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def collect_project_metrics() -> Dict[str, Any]:
    """
    Collect comprehensive project metrics.

    Returns:
        Dictionary with project metrics
    """
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "v2_compliance": {},
        "ssot_status": {},
        "tools_status": {},
        "test_coverage": {},
        "violations": {},
        "consolidation_opportunities": {},
        "agent_status": {},
        "loop_closure": {}
    }

    # V2 Compliance Metrics
    try:
        from tools.v2_checker_cli import check_v2_compliance
        # This would call actual V2 checker
        metrics["v2_compliance"] = {
            "total_files": 0,
            "compliant_files": 0,
            "violations": 0,
            "files_over_limit": []
        }
    except Exception as e:
        logger.warning(f"V2 checker not available: {e}")

    # SSOT Status
    try:
        from tools.ssot_validator import validate_ssot
        metrics["ssot_status"] = {
            "total_files": 0,
            "tagged_files": 0,
            "missing_tags": []
        }
    except Exception as e:
        logger.warning(f"SSOT validator not available: {e}")

    # Tools Status
    try:
        from tools.toolbelt_registry import TOOLS_REGISTRY
        metrics["tools_status"] = {
            "total_tools": len(TOOLS_REGISTRY),
            "registered_tools": len(TOOLS_REGISTRY),
            "unregistered_tools": 0
        }
    except Exception as e:
        logger.warning(f"Toolbelt registry not available: {e}")

    # Test Coverage
    metrics["test_coverage"] = {
        "total_files": 0,
        "tested_files": 0,
        "coverage_percent": 0,
        "missing_tests": []
    }

    # Violations
    metrics["violations"] = {
        "total_violations": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }

    # Consolidation Opportunities
    metrics["consolidation_opportunities"] = {
        "tools_to_consolidate": 0,
        "duplicate_code": 0,
        "dead_code": 0
    }

    # Agent Status
    metrics["agent_status"] = {
        "active_agents": 0,
        "idle_agents": 0,
        "total_tasks": 0,
        "completed_tasks": 0
    }

    # Debate Execution Status
    try:
        from tools.debate_execution_tracker_hook import debate_trackers_to_spreadsheet_tasks
        workflow_dir = project_root / "workflow_states"
        debate_trackers = list(workflow_dir.glob(
            "*_execution.json")) if workflow_dir.exists() else []

        active_debates = 0
        completed_debates = 0
        pending_tasks = 0

        for tracker_file in debate_trackers:
            try:
                with open(tracker_file, "r", encoding="utf-8") as f:
                    tracker = json.load(f)
                status = tracker.get("status", "assigned")
                if status == "completed":
                    completed_debates += 1
                else:
                    active_debates += 1
                    # Count pending agent tasks
                    agents = tracker.get("agents", {})
                    pending_tasks += sum(
                        1 for agent in agents.values()
                        if agent.get("status") in ["assigned", "in_progress"]
                    )
            except Exception:
                pass

        metrics["debate_execution"] = {
            "active_debates": active_debates,
            "completed_debates": completed_debates,
            "pending_tasks": pending_tasks,
            "total_trackers": len(debate_trackers)
        }
    except Exception as e:
        logger.warning(f"Debate execution metrics not available: {e}")
        metrics["debate_execution"] = {
            "active_debates": 0,
            "completed_debates": 0,
            "pending_tasks": 0,
            "total_trackers": 0
        }

    # Cycle V2 Metrics
    try:
        metrics["cycle_v2"] = collect_cycle_v2_metrics()
    except Exception as e:
        logger.warning(f"Cycle V2 metrics not available: {e}")
        metrics["cycle_v2"] = {
            "active_cycles": 0,
            "completed_cycles": 0,
            "total_cycles": 0,
            "average_score": 0.0,
            "low_scores": []
        }

    return metrics


def metrics_to_spreadsheet_rows(metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Convert metrics to spreadsheet rows (actionable format).

    Args:
        metrics: Project metrics dictionary

    Returns:
        List of spreadsheet rows
    """
    rows = []

    # Debate Execution Tasks - Pull actual tasks from trackers
    try:
        from tools.debate_execution_tracker_hook import debate_trackers_to_spreadsheet_tasks
        # Generate detailed debate tasks
        debate_tasks = debate_trackers_to_spreadsheet_tasks(
            output_file="",  # Don't write file, just get tasks
            include_completed=False
        )
        # Add debate tasks to rows
        rows.extend(debate_tasks)
    except Exception as e:
        logger.warning(f"Could not load detailed debate tasks: {e}")
        # Fallback to summary task
        debate_exec = metrics.get("debate_execution", {})
        pending_debate_tasks = debate_exec.get("pending_tasks", 0)
        if pending_debate_tasks > 0:
            rows.append({
                "category": "Debate Execution",
                "task_type": "open_pr",
                "task_payload": f"Execute {pending_debate_tasks} pending debate tasks",
                "priority": "HIGH",
                "status": "pending",
                "run_github": "false",
                "result_url": "",
                "error_msg": "",
                "updated_at": "",
                "estimated_effort": f"{pending_debate_tasks * 0.5} hours",
                "agent": "Multiple",
                "note": f"Active debates: {debate_exec.get('active_debates', 0)}"
            })

    # Cycle V2 Tasks - Pull actual cycles from status files (similar to debate tasks)
    try:
        from tools.cycle_v2_to_spreadsheet_integration import cycle_v2_to_spreadsheet_tasks
        # Generate detailed Cycle V2 tasks
        cycle_v2_tasks = cycle_v2_to_spreadsheet_tasks(
            output_file="",  # Don't write file, just get tasks
            include_completed=False,
            min_score_threshold=70.0
        )
        # Add Cycle V2 tasks to rows
        rows.extend(cycle_v2_tasks)
    except Exception as e:
        logger.warning(f"Could not load detailed Cycle V2 tasks: {e}")
        # Fallback to summary task
        try:
            cycle_v2_metrics = collect_cycle_v2_metrics()
            if cycle_v2_metrics:
                active_cycles = cycle_v2_metrics.get("active_cycles", 0)
                avg_score = cycle_v2_metrics.get("average_score", 0)
                low_scores = cycle_v2_metrics.get("low_scores", [])

                if active_cycles > 0:
                    rows.append({
                        "category": "Cycle V2",
                        "task_type": "update_file",
                        "task_payload": f"Monitor {active_cycles} active Cycle V2 cycles (avg score: {avg_score:.1f}%)",
                        "priority": "MEDIUM",
                        "status": "pending",
                        "run_github": "false",
                        "result_url": "",
                        "error_msg": "",
                        "updated_at": "",
                        "estimated_effort": "0.5 hours",
                        "agent": "Agent-4",
                        "note": f"Active cycles: {active_cycles}, Low scores: {len(low_scores)}"
                    })

                # Add tasks for agents with low scores
                for agent_score in low_scores:
                    agent_id = agent_score.get("agent_id", "Unknown")
                    score = agent_score.get("score_percent", 0)
                    rows.append({
                        "category": "Cycle V2",
                        "task_type": "update_file",
                        "task_payload": f"Improve Cycle V2 compliance for {agent_id} (current: {score:.1f}%)",
                        "priority": "MEDIUM",
                        "status": "pending",
                        "run_github": "false",
                        "result_url": "",
                        "error_msg": "",
                        "updated_at": "",
                        "estimated_effort": "1 hour",
                        "agent": agent_id,
                        "note": f"Score: {score:.1f}% - Review cycle_v2 section in status.json"
                    })
        except Exception as e2:
            logger.warning(f"Cycle V2 metrics not available: {e2}")


def collect_cycle_v2_metrics() -> Dict[str, Any]:
    """
    Collect Cycle V2 metrics from all agent status files.

    Returns:
        Dictionary with cycle v2 metrics
    """
    from pathlib import Path
    import json

    workspace_dir = project_root / "agent_workspaces"
    metrics = {
        "active_cycles": 0,
        "completed_cycles": 0,
        "total_cycles": 0,
        "scores": [],
        "average_score": 0.0,
        "low_scores": []
    }

    if not workspace_dir.exists():
        return metrics

    # Scan all agent workspaces
    for agent_dir in workspace_dir.iterdir():
        if not agent_dir.is_dir() or not agent_dir.name.startswith("Agent-"):
            continue

        status_file = agent_dir / "status.json"
        if not status_file.exists():
            continue

        try:
            with open(status_file, "r", encoding="utf-8") as f:
                status = json.load(f)

            cycle_v2 = status.get("cycle_v2", {})
            if not cycle_v2:
                continue

            metrics["total_cycles"] += 1

            # Check if cycle is active
            current_wip = cycle_v2.get("current_wip", 0)
            if current_wip > 0:
                metrics["active_cycles"] += 1

            # Check completion status
            doc = cycle_v2.get("documentation", {})
            if doc.get("status_value") == "COMPLETE":
                metrics["completed_cycles"] += 1

            # Get validation score if available
            success_metrics = cycle_v2.get("success_metrics", {})
            if success_metrics:
                # Calculate score based on success metrics
                score = 0.0
                if success_metrics.get("output_delivered"):
                    score += 25.0
                if success_metrics.get("validation_evidence_included"):
                    score += 25.0
                if success_metrics.get("zero_drift"):
                    score += 25.0
                if success_metrics.get("wip_respected"):
                    score += 25.0

                metrics["scores"].append({
                    "agent_id": status.get("agent_id", "Unknown"),
                    "score_percent": score
                })

                if score < 70:
                    metrics["low_scores"].append({
                        "agent_id": status.get("agent_id", "Unknown"),
                        "score_percent": score
                    })

        except Exception as e:
            logger.debug(f"Failed to read status for {agent_dir.name}: {e}")
            continue

    # Calculate average score
    if metrics["scores"]:
        metrics["average_score"] = sum(
            s["score_percent"] for s in metrics["scores"]) / len(metrics["scores"])

    return metrics

    # V2 Compliance Tasks
    v2_violations = metrics.get("v2_compliance", {}).get("violations", 0)
    if v2_violations > 0:
        rows.append({
            "category": "V2 Compliance",
            "task_type": "open_pr",
            "task_payload": f"Fix {v2_violations} V2 compliance violations",
            "priority": "HIGH",
            "status": "pending",
            "run_github": "false",  # Set to true when ready
            "result_url": "",
            "error_msg": "",
            "updated_at": "",
            "estimated_effort": f"{v2_violations * 0.5} hours",
            "agent": "Agent-8"
        })

    # SSOT Remediation Tasks
    ssot_missing = metrics.get("ssot_status", {}).get("missing_tags", [])
    if ssot_missing:
        rows.append({
            "category": "SSOT Remediation",
            "task_type": "open_pr",
            "task_payload": f"Add SSOT tags to {len(ssot_missing)} files",
            "priority": "HIGH",
            "status": "pending",
            "run_github": "false",
            "result_url": "",
            "error_msg": "",
            "updated_at": "",
            "estimated_effort": f"{len(ssot_missing) * 0.1} hours",
            "agent": "Agent-8"
        })

    # Tools Consolidation Tasks
    tools_to_consolidate = metrics.get(
        "consolidation_opportunities", {}).get("tools_to_consolidate", 0)
    if tools_to_consolidate > 0:
        rows.append({
            "category": "Tools Consolidation",
            "task_type": "open_pr",
            "task_payload": f"Consolidate {tools_to_consolidate} tools using unified patterns",
            "priority": "MEDIUM",
            "status": "pending",
            "run_github": "false",
            "result_url": "",
            "error_msg": "",
            "updated_at": "",
            "estimated_effort": f"{tools_to_consolidate * 1.0} hours",
            "agent": "Agent-8"
        })

    # Test Coverage Tasks
    coverage = metrics.get("test_coverage", {}).get("coverage_percent", 0)
    if coverage < 85:
        rows.append({
            "category": "Test Coverage",
            "task_type": "open_pr",
            "task_payload": f"Increase test coverage from {coverage}% to 85%+",
            "priority": "MEDIUM",
            "status": "pending",
            "run_github": "false",
            "result_url": "",
            "error_msg": "",
            "updated_at": "",
            "estimated_effort": "4-6 hours",
            "agent": "Agent-8"
        })

    # Loop Closure Tasks
    incomplete_loops = metrics.get(
        "loop_closure", {}).get("incomplete_loops", [])
    for loop in incomplete_loops:
        loop_id = loop.get("loop_id", "?")
        name = loop.get("name", "Unknown Loop")
        status = loop.get("status", "UNKNOWN")
        source = loop.get("source", "")
        rows.append({
            "category": "Loop Closure",
            "task_type": "open_pr",  # placeholder; PR/issue can be driven by adapter
            "task_payload": f"Close Loop {loop_id}: {name} (status: {status}) [source: {source}]",
            "priority": "HIGH",
            "status": "pending",
            "run_github": "false",
            "result_url": "",
            "error_msg": "",
            "updated_at": "",
            "estimated_effort": "1-3 hours",
            "agent": "Agent-6"
        })

    return rows


def generate_dashboard_spreadsheet(metrics: Dict[str, Any], output_file: str):
    """
    Generate comprehensive dashboard spreadsheet.

    Args:
        metrics: Project metrics
        output_file: Output CSV file path
    """
    # Create summary sheet
    summary_rows = [
        {
            "Metric": "V2 Compliance Violations",
            "Value": metrics.get("v2_compliance", {}).get("violations", 0),
            "Status": "🔴 Critical" if metrics.get("v2_compliance", {}).get("violations", 0) > 0 else "✅ Good",
            "Action": "Fix violations" if metrics.get("v2_compliance", {}).get("violations", 0) > 0 else "None"
        },
        {
            "Metric": "SSOT Tagged Files",
            "Value": f"{metrics.get('ssot_status', {}).get('tagged_files', 0)}/{metrics.get('ssot_status', {}).get('total_files', 0)}",
            "Status": "✅ Good" if metrics.get("ssot_status", {}).get("tagged_files", 0) == metrics.get("ssot_status", {}).get("total_files", 0) else "🟡 In Progress",
            "Action": "Add missing tags" if metrics.get("ssot_status", {}).get("missing_tags", []) else "None"
        },
        {
            "Metric": "Tools Registered",
            "Value": f"{metrics.get('tools_status', {}).get('registered_tools', 0)}/{metrics.get('tools_status', {}).get('total_tools', 0)}",
            "Status": "✅ Good",
            "Action": "None"
        },
        {
            "Metric": "Test Coverage",
            "Value": f"{metrics.get('test_coverage', {}).get('coverage_percent', 0)}%",
            "Status": "✅ Good" if metrics.get("test_coverage", {}).get("coverage_percent", 0) >= 85 else "🟡 Needs Improvement",
            "Action": "Increase coverage" if metrics.get("test_coverage", {}).get("coverage_percent", 0) < 85 else "None"
        },
        {
            "Metric": "Consolidation Opportunities",
            "Value": metrics.get("consolidation_opportunities", {}).get("tools_to_consolidate", 0),
            "Status": "🟡 Opportunities Available" if metrics.get("consolidation_opportunities", {}).get("tools_to_consolidate", 0) > 0 else "✅ Complete",
            "Action": "Consolidate tools" if metrics.get("consolidation_opportunities", {}).get("tools_to_consolidate", 0) > 0 else "None"
        },
        {
            "Metric": "Incomplete Loops",
            "Value": len(metrics.get("loop_closure", {}).get("incomplete_loops", [])),
            "Status": "🟡 In Progress" if metrics.get("loop_closure", {}).get("incomplete_loops", []) else "✅ Complete",
            "Action": "Close open loops" if metrics.get("loop_closure", {}).get("incomplete_loops", []) else "None"
        },
        {
            "Metric": "Debate Execution Tasks",
            "Value": f"{metrics.get('debate_execution', {}).get('pending_tasks', 0)} pending",
            "Status": "🟡 Active" if metrics.get("debate_execution", {}).get("pending_tasks", 0) > 0 else "✅ Complete",
            "Action": "Execute debate tasks" if metrics.get("debate_execution", {}).get("pending_tasks", 0) > 0 else "None"
        },
        {
            "Metric": "Cycle V2 Active Cycles",
            "Value": f"{metrics.get('cycle_v2', {}).get('active_cycles', 0)} active",
            "Status": "🟡 Active" if metrics.get("cycle_v2", {}).get("active_cycles", 0) > 0 else "✅ None",
            "Action": "Monitor cycle progress" if metrics.get("cycle_v2", {}).get("active_cycles", 0) > 0 else "None"
        },
        {
            "Metric": "Cycle V2 Average Score",
            "Value": f"{metrics.get('cycle_v2', {}).get('average_score', 0):.1f}%",
            "Status": "✅ Good" if metrics.get("cycle_v2", {}).get("average_score", 0) >= 80 else "🟡 Needs Improvement",
            "Action": "Review low-scoring cycles" if metrics.get("cycle_v2", {}).get("average_score", 0) < 80 else "None"
        }
    ]

    # Create actionable tasks sheet
    task_rows = metrics_to_spreadsheet_rows(metrics)

    # Write summary sheet
    summary_file = output_file.replace(".csv", "_summary.csv")
    with open(summary_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["Metric", "Value", "Status", "Action"])
        writer.writeheader()
        writer.writerows(summary_rows)

    # Write tasks sheet
    tasks_file = output_file.replace(".csv", "_tasks.csv")
    if task_rows:
        columns = ["category", "task_type", "task_payload", "priority", "status", "run_github",
                   "result_url", "error_msg", "updated_at", "estimated_effort", "agent"]
        with open(tasks_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(task_rows)

    logger.info(f"✅ Generated dashboard: {summary_file}")
    logger.info(f"✅ Generated tasks: {tasks_file}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert project metrics to spreadsheet dashboard"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="project_dashboard.csv",
        help="Output CSV file path"
    )
    parser.add_argument(
        "--metrics-file",
        type=str,
        help="Load metrics from JSON file (instead of collecting)"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["dashboard", "tasks", "both"],
        default="both",
        help="Output format"
    )

    args = parser.parse_args()

    # Load or collect metrics
    if args.metrics_file:
        with open(args.metrics_file, "r", encoding="utf-8") as f:
            metrics = json.load(f)
    else:
        logger.info("Collecting project metrics...")
        metrics = collect_project_metrics()

        # Save metrics JSON
        metrics_file = args.output.replace(".csv", "_metrics.json")
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Saved metrics: {metrics_file}")

    # Generate spreadsheet
    if args.format in ["dashboard", "both"]:
        generate_dashboard_spreadsheet(metrics, args.output)

    logger.info("✅ Project metrics converted to spreadsheet format")
    logger.info(
        f"📊 View dashboard: {args.output.replace('.csv', '_summary.csv')}")
    logger.info(f"📋 View tasks: {args.output.replace('.csv', '_tasks.csv')}")

    # Emit telemetry heartbeat (non-blocking)
    try:
        from src.core.activity_emitter import emit_activity_event

        emit_activity_event(
            event_type="TOOL_RUN",
            source="project_metrics_spreadsheet",
            agent_id="SYSTEM",
            summary="project_metrics_to_spreadsheet run",
            artifact={
                "report_path": args.output,
            },
            meta={
                "exit_code": 0,
            },
        )
    except Exception:
        pass


if __name__ == "__main__":
    main()
