#!/usr/bin/env python3
"""
Cycle V2 → Spreadsheet Integration
===================================

Connects Cycle V2 cycles to spreadsheet workflow:
- Convert cycle_v2 status.json sections to spreadsheet tasks
- Track cycle completion with validation scores
- Generate actionable tasks from cycle metrics

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-12-07
V2 Compliant: Yes
"""

import argparse
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


def cycle_v2_to_spreadsheet_tasks(
    output_file: Optional[str] = None,
    include_completed: bool = False,
    min_score_threshold: float = 70.0
) -> List[Dict[str, Any]]:
    """
    Convert Cycle V2 cycles from agent status files to spreadsheet tasks.
    
    Args:
        output_file: Output CSV file path (optional)
        include_completed: Include completed cycles
        min_score_threshold: Minimum score to include (default: 70%)
        
    Returns:
        List of task dictionaries
    """
    workspace_dir = project_root / "agent_workspaces"
    tasks = []
    
    if not workspace_dir.exists():
        logger.warning(f"Workspace directory not found: {workspace_dir}")
        return []
    
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
            
            agent_id = status.get("agent_id", agent_dir.name)
            cycle_v2 = status.get("cycle_v2", {})
            
            if not cycle_v2:
                continue
            
            # Check if cycle is active or completed
            current_wip = cycle_v2.get("current_wip", 0)
            doc = cycle_v2.get("documentation", {})
            status_value = doc.get("status_value", "")
            
            # Skip completed if not including
            if status_value == "COMPLETE" and not include_completed:
                continue
            
            # Get validation score
            validation_report = cycle_v2.get("validation_report", {})
            score_percent = validation_report.get("score_percent", 0)
            
            # Skip if score is too low (unless explicitly requested)
            if score_percent > 0 and score_percent < min_score_threshold and not include_completed:
                continue
            
            # Get cycle details
            mission = status.get("current_mission", "Unknown mission")
            micro_plan = cycle_v2.get("micro_plan", [])
            dod = cycle_v2.get("dod", "")
            
            # Determine task type based on cycle status
            if status_value == "COMPLETE":
                task_type = "update_file"  # Completed cycles might need follow-up
            elif current_wip > 0:
                task_type = "open_pr"  # Active cycles need execution
            else:
                task_type = "create_issue"  # Pending cycles need planning
            
            # Create spreadsheet task
            task = {
                "category": "Cycle V2",
                "task_type": task_type,
                "task_payload": f"[Cycle V2] {mission}\n\nDoD: {dod[:100]}...",
                "priority": "HIGH" if current_wip > 0 else "MEDIUM",
                "status": "in_progress" if current_wip > 0 else "pending",
                "run_github": "false",
                "result_url": validation_report.get("result_url", ""),
                "error_msg": "",
                "updated_at": status.get("last_updated", ""),
                "topic": f"cycle_v2_{agent_id}",
                "agent": agent_id,
                "mission": mission,
                "dod": dod[:200],  # Truncate for CSV
                "micro_plan": " | ".join(micro_plan[:3]),
                "validation_score": f"{score_percent:.1f}%",
                "grade": validation_report.get("grade", "N/A"),
                "errors_count": validation_report.get("errors_count", 0),
                "warnings_count": validation_report.get("warnings_count", 0),
                "title": f"[Cycle V2] {agent_id}: {mission[:50]}",
                "body": f"Agent: {agent_id}\nMission: {mission}\n\nDoD:\n{dod}\n\nMicro-Plan:\n" + "\n".join(f"- {item}" for item in micro_plan[:3])
            }
            
            # Add validation details if available
            if validation_report:
                task["validation_evidence"] = f"Score: {score_percent:.1f}% ({validation_report.get('grade', 'N/A')})"
                if validation_report.get("errors"):
                    task["error_msg"] = "; ".join(validation_report["errors"][:3])
            
            tasks.append(task)
        
        except Exception as e:
            logger.warning(f"Failed to process {agent_dir.name}: {e}")
            continue
    
    # Write to CSV if output file specified
    if tasks and output_file:
        import csv
        columns = [
            "category", "task_type", "task_payload", "priority", "status",
            "run_github", "result_url", "error_msg", "updated_at",
            "topic", "agent", "mission", "dod", "micro_plan",
            "validation_score", "grade", "errors_count", "warnings_count",
            "title", "body", "validation_evidence"
        ]
        
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(tasks)
        
        logger.info(f"✅ Generated {len(tasks)} Cycle V2 tasks: {output_file}")
    elif tasks:
        logger.info(f"✅ Generated {len(tasks)} Cycle V2 tasks (in-memory)")
    
    return tasks


def update_cycle_v2_tracker(
    agent_id: str,
    status: str = "completed",
    validation_score: Optional[float] = None,
    artifacts: Optional[List[str]] = None,
    commit_hash: Optional[str] = None,
    pr_url: Optional[str] = None
) -> bool:
    """
    Update Cycle V2 tracker when agent completes cycle.
    
    Args:
        agent_id: Agent ID
        status: Cycle status (completed, in_progress, blocked)
        validation_score: Validation score (0-100)
        artifacts: List of artifact file paths
        commit_hash: Git commit hash
        pr_url: PR URL if applicable
        
    Returns:
        True if updated successfully
    """
    status_file = project_root / "agent_workspaces" / agent_id / "status.json"
    
    if not status_file.exists():
        logger.warning(f"Status file not found: {status_file}")
        return False
    
    try:
        # Load existing status
        with open(status_file, "r", encoding="utf-8") as f:
            status_data = json.load(f)
        
        # Ensure cycle_v2 section exists
        if "cycle_v2" not in status_data:
            status_data["cycle_v2"] = {}
        
        cycle_v2 = status_data["cycle_v2"]
        
        # Update documentation status
        if "documentation" not in cycle_v2:
            cycle_v2["documentation"] = {}
        
        cycle_v2["documentation"]["status_value"] = status.upper()
        cycle_v2["documentation"]["status_json_updated"] = True
        
        # Update validation report if score provided
        if validation_score is not None:
            if "validation_report" not in cycle_v2:
                cycle_v2["validation_report"] = {}
            
            cycle_v2["validation_report"]["score_percent"] = validation_score
            cycle_v2["validation_report"]["updated_at"] = datetime.now().isoformat()
            
            # Calculate grade
            if validation_score >= 90:
                grade = "A"
            elif validation_score >= 80:
                grade = "B"
            elif validation_score >= 70:
                grade = "C"
            elif validation_score >= 60:
                grade = "D"
            else:
                grade = "F"
            
            cycle_v2["validation_report"]["grade"] = grade
        
        # Add artifacts if provided
        if artifacts:
            if "reporting" not in cycle_v2:
                cycle_v2["reporting"] = {}
            
            if "artifacts_changed" not in cycle_v2["reporting"]:
                cycle_v2["reporting"]["artifacts_changed"] = []
            
            cycle_v2["reporting"]["artifacts_changed"].extend(artifacts)
            # Remove duplicates
            cycle_v2["reporting"]["artifacts_changed"] = list(set(cycle_v2["reporting"]["artifacts_changed"]))
        
        # Add commit hash
        if commit_hash:
            if "execution_burst" not in cycle_v2:
                cycle_v2["execution_burst"] = {}
            cycle_v2["execution_burst"]["commit_hash"] = commit_hash
        
        # Add PR URL
        if pr_url:
            if "validation_report" not in cycle_v2:
                cycle_v2["validation_report"] = {}
            cycle_v2["validation_report"]["result_url"] = pr_url
        
        # Update last_updated
        status_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Save updated status
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(status_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Updated Cycle V2 tracker for {agent_id}")

        # Emit telemetry heartbeat (non-blocking)
        try:
            from src.core.activity_emitter import emit_activity_event

            emit_activity_event(
                event_type="TASK_COMPLETED",
                source="cycle_v2_spreadsheet",
                agent_id=agent_id,
                summary=f"Cycle V2 tracker update ({status})",
                artifact={
                    "score": validation_score,
                    "commit": commit_hash,
                    "pr_url": pr_url,
                    "artifacts": artifacts or [],
                },
                meta={"status": status},
            )
        except Exception:
            pass

        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to update Cycle V2 tracker: {e}")
        return False


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Cycle V2 to Spreadsheet Integration"
    )
    parser.add_argument(
        "--to-spreadsheet",
        type=str,
        help="Convert Cycle V2 cycles to spreadsheet tasks"
    )
    parser.add_argument(
        "--include-completed",
        action="store_true",
        help="Include completed cycles"
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=70.0,
        help="Minimum score threshold (default: 70.0)"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update Cycle V2 tracker"
    )
    parser.add_argument(
        "--agent",
        type=str,
        help="Agent ID"
    )
    parser.add_argument(
        "--status",
        type=str,
        choices=["completed", "in_progress", "blocked"],
        help="Cycle status"
    )
    parser.add_argument(
        "--score",
        type=float,
        help="Validation score (0-100)"
    )
    parser.add_argument(
        "--artifact",
        type=str,
        action="append",
        help="Artifact path (can specify multiple)"
    )
    parser.add_argument(
        "--commit",
        type=str,
        help="Commit hash"
    )
    parser.add_argument(
        "--pr-url",
        type=str,
        help="PR URL"
    )
    
    args = parser.parse_args()
    
    if args.update:
        if not args.agent or not args.status:
            logger.error("--agent and --status required for --update")
            sys.exit(1)
        
        success = update_cycle_v2_tracker(
            agent_id=args.agent,
            status=args.status,
            validation_score=args.score,
            artifacts=args.artifact,
            commit_hash=args.commit,
            pr_url=args.pr_url
        )
        
        if success:
            logger.info("✅ Cycle V2 tracker updated")
        else:
            logger.error("❌ Failed to update tracker")
            sys.exit(1)
    
    elif args.to_spreadsheet:
        tasks = cycle_v2_to_spreadsheet_tasks(
            output_file=args.to_spreadsheet,
            include_completed=args.include_completed,
            min_score_threshold=args.min_score
        )
        logger.info(f"✅ Generated {len(tasks)} Cycle V2 tasks in spreadsheet")
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()


